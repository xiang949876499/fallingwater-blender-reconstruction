"""Read-only 960x540 rendered-pixel to saved-terrain/mask diagnosis."""
import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import near_terrain_detail as near
baseline=ROOT/'scene/Fallingwater_geology_candidate07c.blend'
candidate=ROOT/'scene/Fallingwater_near_terrain_candidate07b_contacts.blend'
assert hashlib.sha256(candidate.read_bytes()).hexdigest()=='fd07ec36e53258df3e577b39ac8949096651c5fb739900535f71f562cd77eebe'
bpy.ops.wm.open_mainfile(filepath=str(baseline));bpy.context.scene.frame_set(48)
oldobj=bpy.data.objects['SITE_Continuous_BearRun_Terrain']
oldbvh=BVHTree.FromObject(oldobj,bpy.context.evaluated_depsgraph_get())
bpy.ops.wm.open_mainfile(filepath=str(candidate));scene=bpy.context.scene;scene.frame_set(48)
scene.render.resolution_x=960;scene.render.resolution_y=540;scene.render.resolution_percentage=100
cam=scene.objects['CAM_MAIN_L1_LOGGIA_B'];frame=cam.data.view_frame(scene=scene)
x0,x1=min(v.x for v in frame),max(v.x for v in frame);y0,y1=min(v.y for v in frame),max(v.y for v in frame);z=frame[0].z
ctx=SimpleNamespace(root=ROOT,config=json.loads((ROOT/'config.json').read_text(encoding='utf8')))
surf=near.Terrain(ctx,json.loads(json.dumps(near.DEFAULTS)))
obj=surf.obj;attrs=obj.data.attributes['bank07b_litter_weight']
delta_map={p['index']:p['delta_m'] for p in json.loads((ROOT/'qa/near-terrain07b-candidate-check.json').read_text())['result']['deformation']['vertices']}

def constraints(x,y,geometry=False):
    q=[('radius30',30-math.hypot(x-5,y-5))]
    q.extend(('building:'+b['name'],near.box_outside(x,y,b['bbox'])) for b in surf.cfg['building_exclusions'])
    q.append(('bridge',near.box_outside(x,y,surf.cfg['bridge']['bbox'])-.4))
    for o in surf.rocks:
        if geometry:q.append(('existing_rock:'+o.name,near.box_outside(x,y,near.bounds(o))-.2))
        if o.name.startswith(('SITE_Core_','SITE_Cascade_Shoulder_Continuous')):q.append(('core:'+o.name,near.box_outside(x,y,near.bounds(o))-.35))
    for route in surf.cfg['paths']:
        q.append(('path:'+route['name'],min(near.segment_distance(x,y,a,b)[0] for a,b in zip(route['points'],route['points'][1:]))-route['width']*.5-.75))
    for i,(a,b) in enumerate(zip(surf.cfg['river_path'],surf.cfg['river_path'][1:])):
        d,t=near.segment_distance(x,y,a,b);q.append(('river_segment:'+str(i),d-(a[3]+(b[3]-a[3])*t)*.5-.75))
    if geometry:q.extend(('camera:'+name,math.hypot(x-cx,y-cy)-2) for name,cx,cy in surf.cameras)
    return [{'name':name,'clearance_m':v} for name,v in sorted(q,key=lambda item:item[1])[:8]]

records=[]
for label,(px,py) in [('A_crest',(357,136)),('B_mid',(400,200)),('C_foot',(400,280)),('D_left',(310,220)),('E_right',(460,240))]:
    local=Vector((x0+(x1-x0)*(px+.5)/960,y0+(y1-y0)*(1-(py+.5)/540),z))
    direction=(cam.matrix_world.to_3x3()@local).normalized();origin=cam.matrix_world.translation
    p,n,index,d=surf.bvh.ray_cast(origin,direction,500)
    assert p is not None,label
    first=[];start=origin.copy()
    for j in range(8):
        ok,hit,normal,face,hitobj,matrix=scene.ray_cast(bpy.context.evaluated_depsgraph_get(),start,direction,distance=d+1)
        if not ok:break
        first.append({'object':hitobj.name,'point':list(hit),'hide_render':hitobj.hide_render})
        if not hitobj.hide_render:break
        start=hit+direction*.001
    old,_,_,_=oldbvh.ray_cast(Vector((p.x,p.y,60)),Vector((0,0,-1)),130)
    oldray,_,_,_=oldbvh.ray_cast(origin,direction,500)
    poly=obj.data.polygons[index];vv=[obj.matrix_world@obj.data.vertices[i].co for i in poly.vertices]
    a,b,c=vv;den=(b.y-c.y)*(a.x-c.x)+(c.x-b.x)*(a.y-c.y)
    u=((b.y-c.y)*(p.x-c.x)+(c.x-b.x)*(p.y-c.y))/den
    v=((c.y-a.y)*(p.x-c.x)+(a.x-c.x)*(p.y-c.y))/den
    bary=[u,v,1-u-v]
    weights=[attrs.data[i].value for i in poly.vertices]
    projected=world_to_camera_view(scene,cam,p)
    entry={'label':label,'pixel_top_left':[px,py],'world':list(p),'normal':list(n),'distance_from_camera_m':d,
           'first_scene_hit_chain':first,'baseline_z_same_xy':old.z,'actual_delta_same_xy_m':p.z-old.z,
           'baseline_same_pixel_world':list(oldray) if oldray else None,
           'reproject_pixel':[projected.x*960-.5,(1-projected.y)*540-.5],
           'triangle':index,'triangle_vertex_indices':list(poly.vertices),'triangle_vertices':[list(v) for v in vv],
           'triangle_vertex_material_weights':weights,'interpolated_material_weight':sum(a*b for a,b in zip(bary,weights)),
           'triangle_vertex_z_deltas_m':[delta_map.get(i,0) for i in poly.vertices],
           'shading_clearances':constraints(p.x,p.y),'geometry_clearances':constraints(p.x,p.y,True),
           'formula_point_material_weight':surf.weight(p.x,p.y),
           'zone_inside_distances':{name:-near.box_outside(p.x,p.y,bb) for name,bb in near.DEFAULTS['zones'].items()},
           'proposed_delta_current_field':surf.proposed_delta(p.x,p.y)}
    records.append(entry)
out={'status':'READ_ONLY_PIXEL_TO_SAVED_MESH_DIAGNOSIS','render_path':'renders/previews/iteration07b-near-terrain/CAM_MAIN_L1_LOGGIA_B.png',
     'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'frame':48,'resolution':[960,540],
     'camera':cam.name,'camera_position':list(cam.matrix_world.translation),'camera_shift':[cam.data.shift_x,cam.data.shift_y],'records':records,
     'limits':'Pixel centers are ray-projected through the actual saved camera and independently reprojected. Scene first-hit record flags any intervening object. Terrain masks are analyzed from current helper without invoking build. No scene save/render.'}
(ROOT/'qa/bank07c-diagnosis-pixel-rays.json').write_text(json.dumps(out,indent=2),encoding='utf8')
for r in records:print(json.dumps({k:r[k] for k in ('label','pixel_top_left','world','actual_delta_same_xy_m','interpolated_material_weight','geometry_clearances','shading_clearances','zone_inside_distances')}),flush=True)
