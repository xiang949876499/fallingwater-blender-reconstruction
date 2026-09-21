"""Read-only saved-scene shader, physical mapping and visible-terrain probe."""
import bpy, json, hashlib, math
from pathlib import Path
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'scene/Fallingwater_iteration08.blend'
SHA='c5cd501e4c8ae0205ecb2437cd2d06d0c92bcc9a87e7d93d3986aeef976070d7'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene;scene.frame_set(48)
scene.render.resolution_x=960;scene.render.resolution_y=540;scene.render.resolution_percentage=100
obj=scene.objects['SITE_Continuous_BearRun_Terrain'];mat=obj.data.materials[0]
def value(v):
    if isinstance(v,(str,int,float,bool)) or v is None:return v
    try:return list(v)
    except:return str(v)
def node_record(n):
    r={'name':n.name,'type':n.bl_idname,'label':n.label,'mute':n.mute,
       'inputs':[{'name':s.name,'identifier':s.identifier,'linked':s.is_linked,
                  'value':value(s.default_value) if hasattr(s,'default_value') else None} for s in n.inputs]}
    for name in ('operation','blend_type','projection','projection_blend','interpolation','extension','space','invert','is_active_output'):
        if hasattr(n,name):r[name]=value(getattr(n,name))
    if hasattr(n,'object'):r['coordinate_object']=n.object.name if n.object else None
    if hasattr(n,'image') and n.image:
        im=n.image;path=Path(bpy.path.abspath(im.filepath))
        r['image']={'name':im.name,'filepath':str(path),'size':list(im.size),'colorspace':im.colorspace_settings.name,
                    'is_float':im.is_float,'has_data':im.has_data,'packed':bool(im.packed_file),
                    'exists':path.exists(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None}
    return r
links=[{'from':[l.from_node.name,l.from_socket.name],'to':[l.to_node.name,l.to_socket.name],'valid':l.is_valid} for l in mat.node_tree.links]
active=[n for n in mat.node_tree.nodes if n.bl_idname=='ShaderNodeOutputMaterial' and n.is_active_output]
reachable=set()
def trace(n):
    if n.name in reachable:return
    reachable.add(n.name)
    for socket in n.inputs:
        for link in socket.links:trace(link.from_node)
for output in active:trace(output)
allnodes=[node_record(n) for n in mat.node_tree.nodes]
image_nodes=[n for n in mat.node_tree.nodes if n.bl_idname=='ShaderNodeTexImage']
scale_nodes=[n for n in mat.node_tree.nodes if n.bl_idname=='ShaderNodeVectorMath' and n.operation=='SCALE']
assert len(scale_nodes)==1
scale=float(scale_nodes[0].inputs['Scale'].default_value)
world_to_object=obj.matrix_world.inverted()
bvh=BVHTree.FromObject(obj,bpy.context.evaluated_depsgraph_get())
bench=json.loads((ROOT/'renders/previews/iteration08-focus/render-benchmark.json').read_text(encoding='utf8'))
exposure={r['camera']:r['exposure'] for r in bench['runs']}
samples=[]
for camera_name,pixels in {
    'CAM_HERO':[(100,415),(220,470)],
    'CAM_MAIN_L1_LOGGIA_B':[(110,210),(320,260),(380,170)],
    'CAM_MAIN_L1_LIVING_A':[(440,170),(540,200),(770,190)]}.items():
    cam=scene.objects[camera_name];frame=cam.data.view_frame(scene=scene)
    x0,x1=min(v.x for v in frame),max(v.x for v in frame);y0,y1=min(v.y for v in frame),max(v.y for v in frame);z=frame[0].z
    origin=cam.matrix_world.translation
    def shoot(px,py):
        local=Vector((x0+(x1-x0)*(px+.5)/960,y0+(y1-y0)*(1-(py+.5)/540),z))
        direction=(cam.matrix_world.to_3x3()@local).normalized()
        hit,n,index,d=bvh.ray_cast(origin,direction,1500)
        return hit,n,index,d,direction
    for px,py in pixels:
        hit,n,index,d,direction=shoot(px,py)
        if hit is None:
            samples.append({'camera':camera_name,'pixel':[px,py],'terrain_hit':None});continue
        first=scene.ray_cast(bpy.context.evaluated_depsgraph_get(),origin,direction,distance=d+.1)
        deriv=[]
        for dx,dy in [(1,0),(0,1)]:
            q,_,_,_,_=shoot(px+dx,py+dy)
            if q is None:continue
            diff=world_to_object.to_3x3()@(q-hit)
            deriv.append({'pixel_axis':[dx,dy],'world_m_per_pixel':(q-hit).length,
                          'object_delta':list(diff),'cycles_per_pixel_xyz':list(diff*scale),
                          'projected_texels_per_pixel_XY':Vector((diff.x,diff.y)).length*scale*2048,
                          'projected_texels_per_pixel_XZ':Vector((diff.x,diff.z)).length*scale*2048,
                          'projected_texels_per_pixel_YZ':Vector((diff.y,diff.z)).length*scale*2048})
        samples.append({'camera':camera_name,'pixel':[px,py],'terrain_hit':list(hit),'normal':list(n),
                        'face_material_index':obj.data.polygons[index].material_index,
                        'distance_m':d,'first_scene_hit':first[4].name if first[0] else None,
                        'scale_derivatives':deriv,'render_exposure_stops':exposure[camera_name],
                        'texture_xyz':list((world_to_object@hit)*scale)})
lights=[]
for o in scene.objects:
    if o.type=='LIGHT' and (o.data.type=='SUN' or o.name.startswith('FW_')):
        lights.append({'object':o.name,'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'hide_render':o.hide_render})
out={'status':'READ_ONLY_SAVED_SHADER_AND_MAPPING_PROBE','source':str(SOURCE),'source_sha256':SHA,
     'frame':48,'render_benchmark_sha256':hashlib.sha256((ROOT/'renders/previews/iteration08-focus/render-benchmark.json').read_bytes()).hexdigest(),
     'terrain':{'object':obj.name,'matrix_world':[list(r) for r in obj.matrix_world],
                'scale':list(obj.scale),'dimensions':list(obj.dimensions),
                'vertices':len(obj.data.vertices),'faces':len(obj.data.polygons),
                'smooth_faces':sum(p.use_smooth for p in obj.data.polygons),
                'modifiers':[{'name':m.name,'type':m.type,'show_render':m.show_render} for m in obj.modifiers],
                'material_slots':[m.name if m else None for m in obj.data.materials],
                'face_material_counts':dict(Counter(p.material_index for p in obj.data.polygons)),
                'attributes':[a.name for a in obj.data.attributes],'bridge08_marker':obj.get('fw_bridge08_applied')},
     'material':{'name':mat.name,'use_nodes':mat.use_nodes,'properties':{k:value(v) for k,v in mat.items()},
                 'users':mat.users,'nodes':allnodes,'links':links,'output_reachable_nodes':sorted(reachable),
                 'displacement_method':getattr(mat,'displacement_method',None)},
     'mapping':{'saved_scale':scale,'local_metres_per_tile':1/scale,
                'world_metres_per_tile_axes':[1/scale*(obj.matrix_world.to_3x3()@Vector(v)).length for v in [(1,0,0),(0,1,0),(0,0,1)]],
                'all_image_nodes_reachable':all(n.name in reachable for n in image_nodes)},
     'scene_view':{'view_transform':scene.view_settings.view_transform,'look':scene.view_settings.look,
                   'saved_exposure':scene.view_settings.exposure,'render_camera_exposures':{k:exposure[k] for k in ('CAM_HERO','CAM_MAIN_L1_LOGGIA_B','CAM_MAIN_L1_LIVING_A')},
                   'world_nodes':[node_record(n) for n in scene.world.node_tree.nodes],
                   'world_links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in scene.world.node_tree.links],
                   'lights':lights},'visible_samples':samples,
     'rendered':False,'scene_saved':False,
     'limits':'Graph reachability and nonzero bump settings prove the path is active, not numerical Cycles shading evaluation. Pixel derivatives are geometric footprints, not exact mip levels; first-hit objects flag intervening glass/foliage.'}
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
(ROOT/'qa/terrain-material08-probe.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print('TERRAIN_MATERIAL08',json.dumps({'material':mat.name,'slots':out['terrain']['material_slots'],'mapping':out['mapping'],'active_nodes':sorted(reachable),'file_unchanged':True}),flush=True)
