"""Read-only volume RNA, nominal lattice and local geometric visibility evidence."""
import hashlib,itertools,json,math
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'scene/Fallingwater_preview_iteration06.blend'
EXPECTED='e317241899808995f049e8d3343eac96c591cbecfddaa980949d6babb51ccce6'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())

def inside(point,poly):
    x,y=point[:2];hit=False
    for i,p in enumerate(poly):
        q=poly[i-1]
        if (p[1]>y)!=(q[1]>y) and x<(q[0]-p[0])*(y-p[1])/(q[1]-p[1])+p[0]:hit=not hit
    return hit

def ray(origin,direction,distance):
    hit,p,n,face,obj,matrix=s.ray_cast(deps,origin,direction,distance=distance)
    return {'object':obj.name,'point':list(p),'normal':list(n),'face':face,
        'distance':(p-origin).length,'front_face':n.dot(direction)<0} if hit else None

def camera_ray(camera,pixel):
    inv=camera.calc_matrix_camera(deps,x=960,y=540).inverted()
    v=inv@Vector((pixel[0]*2/960-1,1-pixel[1]*2/540,-1,1))
    d=(camera.matrix_world.to_3x3()@Vector((v.x/v.w,v.y/v.w,v.z/v.w))).normalized()
    return ray(camera.matrix_world.translation,d,100)

names=['clip_start','influence_distance','visibility_buffer_bias','visibility_bleed_bias','visibility_blur',
    'visibility_collection','invert_visibility_collection','intensity','resolution_x','resolution_y','resolution_z',
    'capture_distance','normal_bias','view_bias','facing_bias','bake_samples','surface_bias','escape_bias',
    'surfel_density','validity_threshold','dilation_threshold','dilation_radius','capture_world','capture_indirect',
    'capture_emission','clamp_direct','clamp_indirect']
report={'source_sha256':EXPECTED,'production_saved':False,'rendered':False,'probes':[],'room_checks':[]}
probe_points={}
for obj in sorted((o for o in s.objects if o.type=='LIGHT_PROBE' and o.data.type=='VOLUME'),key=lambda o:o.name):
    props={}
    for name in names:
        if not hasattr(obj.data,name):continue
        p=obj.data.bl_rna.properties[name];value=getattr(obj.data,name)
        props[name]={'value':value.name if hasattr(value,'name') else value,'description':p.description,
            'min':getattr(p,'hard_min',None),'max':getattr(p,'hard_max',None)}
    resolution=[obj.data.resolution_x,obj.data.resolution_y,obj.data.resolution_z]
    corners=[obj.matrix_world@Vector(x) for x in itertools.product((-1,1),repeat=3)]
    bounds=[[min(p[i] for p in corners) for i in range(3)],[max(p[i] for p in corners) for i in range(3)]]
    # Runtime padded-grid transform, unshifted original cell centers. Real baked
    # virtual offsets/validity are not exposed by the installed RNA interface.
    centers=[]
    for index in itertools.product(*(range(n) for n in resolution)):
        local=Vector([-1+2*(index[i]+1)/(resolution[i]+1) for i in range(3)])
        centers.append({'index':list(index),'world':list(obj.matrix_world@local)})
    probe_points[obj.name]=centers
    report['probes'].append({'name':obj.name,'bounds':bounds,'matrix_world':[list(r) for r in obj.matrix_world],
        'resolution':resolution,'properties':props,'rna_identifiers':[p.identifier for p in obj.data.bl_rna.properties],
        'nominal_unshifted_sample_formula':'object_to_world * (-1 + 2*(index+1)/(resolution+1)); derived from 5.2.1 padded-grid transform',
        'nominal_unshifted_world_centers':centers,
        'actual_baked_validity_or_virtual_offsets_read':False})
axes=[Vector(v) for v in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]]
for room_id,probe_name in [('MAIN_L3_STUDY','FW_PROBE_MAIN_L3'),('GUEST_L2_BEDROOM_NORTH','FW_PROBE_GUEST_L2')]:
    room=next(r for r in rooms if r['id']==room_id)
    checks=[]
    for point in probe_points[probe_name]:
        p=Vector(point['world'])
        if not inside(p,room['polygon']) or not room['z']<p.z<room['z']+room['height']:continue
        hits=[ray(p,d,5) for d in axes]
        checks.append({**point,'axis_hits':hits,'backface_first_hits':sum(h is not None and not h['front_face'] for h in hits),
            'nearer_than_10cm_hits':sum(h is not None and h['distance']<.1 for h in hits)})
    report['room_checks'].append({'room':room_id,'probe':probe_name,'polygon':room['polygon'],'floor_z':room['z'],
        'height':room['height'],'nominal_samples_inside_room_polygon':checks,
        'suspect_note':'First backface hits suggest inside/reversed/open geometry; these are not baked validity values.'})
camera=s.objects['CAM_MAIN_L3_STUDY_B'];samples=[]
for label,pixel in [('dark_wall',(720,275)),('upper_wall',(720,125)),('lower_bright_gap',(710,454))]:
    hit=camera_ray(camera,pixel);entry={'label':label,'pixel':pixel,'camera_hit':hit}
    if hit:
        target=Vector(hit['point'])+Vector(hit['normal'])*.003
        nearest=sorted(probe_points['FW_PROBE_MAIN_L3'],key=lambda p:(Vector(p['world'])-target).length)[:8]
        entry['nearest_eight_nominal_samples']=[]
        for sample in nearest:
            origin=Vector(sample['world']);direction=(target-origin).normalized();distance=(target-origin).length
            entry['nearest_eight_nominal_samples'].append({**sample,'distance_to_target':distance,
                'first_segment_hit':ray(origin,direction,max(0,distance-.001))})
    samples.append(entry)
report['study_pixels']=samples
report['cache_exposure_limit']='Installed RNA exposes probe controls, not baked per-cell SH/validity/virtual-offset arrays. Do not claim bad cached normals from these settings alone.'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED
(ROOT/'qa/eevee-iteration06-volume-inspect.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'probe_count':len(report['probes']),'room_sample_counts':[(r['room'],len(r['nominal_samples_inside_room_polygon']),sum(bool(p['backface_first_hits']) for p in r['nominal_samples_inside_room_polygon'])) for r in report['room_checks']],
    'study_pixels':samples},indent=2),flush=True)
