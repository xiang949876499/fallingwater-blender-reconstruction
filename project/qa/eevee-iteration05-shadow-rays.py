"""Inspect exact ray intersections from visible sources to dark/bright image samples."""
import hashlib,json,math
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'scene/Fallingwater_preview_iteration05.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
eval_mesh_cache={}

def ray(origin,direction,distance):
    hit,point,normal,face,obj,matrix=s.ray_cast(deps,origin,direction,distance=distance)
    if not hit:return None
    if obj.name not in eval_mesh_cache:
        evaluated=obj.evaluated_get(deps)
        eval_mesh_cache[obj.name]=(evaluated,evaluated.to_mesh())
    mesh=eval_mesh_cache[obj.name][1]
    index=mesh.polygons[face].material_index if mesh and face<len(mesh.polygons) else None
    material=mesh.materials[index].name if index is not None and index<len(mesh.materials) and mesh.materials[index] else None
    return {'object':obj.name,'point':list(point),'normal':list(normal),'face':face,
            'front_face':normal.dot(direction)<0,'distance':(point-origin).length,'material':material}

def hits_segment(origin,target,max_hits=20):
    direction=(target-origin).normalized();length=(target-origin).length;cursor=origin.copy();hits=[]
    for i in range(max_hits):
        remain=length-(cursor-origin).dot(direction)
        if remain<.0005:break
        result=ray(cursor,direction,remain+.0002)
        if result is None:break
        hits.append({**result,'source_distance':(Vector(result['point'])-origin).length})
        cursor=Vector(result['point'])+direction*.0005
    return hits

def camera_hit(camera,pixel):
    inverse=camera.calc_matrix_camera(deps,x=960,y=540).inverted()
    ndc=Vector((2*pixel[0]/960-1,1-2*pixel[1]/540,-1,1))
    p=inverse@ndc;d=(camera.matrix_world.to_3x3()@Vector((p.x/p.w,p.y/p.w,p.z/p.w))).normalized()
    return ray(camera.matrix_world.translation,d,200)

lights=[]
for obj in s.objects:
    if obj.type=='LIGHT' and not obj.hide_render:
        props={}
        for p in obj.data.bl_rna.properties:
            if any(k in p.identifier for k in ('shadow','clip','radius','size','energy','shape')):
                try:props[p.identifier]={'value':str(getattr(obj.data,p.identifier)),'description':p.description}
                except Exception:pass
        lights.append({'name':obj.name,'type':obj.data.type,'location':list(obj.matrix_world.translation),
                       'visible_source':obj.get('visible_source'),'properties':props})
report={'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'lights':lights,'views':[]}
for camera_name,pixels in [('CAM_MAIN_B_BATH_B',{'dark_center':(505,325),'left_bright':(170,300),'right_bright':(850,300)}),
                           ('CAM_MAIN_L1_LIVING_B',{'dark_center':(820,260),'fireplace_dark':(395,195),'top_bright':(480,95)})]:
    camera=s.objects[camera_name];view={'camera':camera_name,'samples':[]}
    sources=[o for o in s.objects if o.type=='LIGHT' and not o.hide_render and ('MAIN_B_BATH' in o.name)] if 'BATH' in camera_name else [o for o in s.objects if o.type=='LIGHT' and not o.hide_render and o.data.type=='SUN']
    for label,pixel in pixels.items():
        target=camera_hit(camera,pixel);entry={'label':label,'pixel':pixel,'camera_hit':target,'source_rays':[]}
        if target:
            endpoint=Vector(target['point'])
            for source in sources:
                if source.data.type=='SUN':
                    incoming=source.matrix_world.to_quaternion()@Vector((0,0,-1))
                    origin=endpoint-incoming*80
                else:origin=source.matrix_world.translation.copy()
                entry['source_rays'].append({'source':source.name,'source_origin':list(origin),
                    'endpoint':list(endpoint),'hits':hits_segment(origin,endpoint)})
        view['samples'].append(entry)
    report['views'].append(view)
emit=[]
for obj in s.objects:
    if obj.type!='MESH' or obj.hide_render:continue
    for mat in obj.data.materials:
        if not mat or not mat.use_nodes:continue
        node=mat.node_tree.nodes.get('Principled BSDF')
        if node and node.inputs['Emission Strength'].default_value>0 and ('MAIN_L1_LIVING' in obj.name or 'CEILING' in obj.name.upper()):
            emit.append({'object':obj.name,'material':mat.name,'emission':node.inputs['Emission Strength'].default_value,'center':list(obj.matrix_world.translation)})
report['living_emissive_meshes']=emit
for sample in report['views'][1]['samples']:
    endpoint=Vector(sample['camera_hit']['point'])
    sample['emission_surface_rays']=[]
    candidates=sorted(emit,key=lambda e:(Vector(e['center'])-endpoint).length)[:4]
    for emitter in candidates:
        obj=bpy.data.objects[emitter['object']]
        bounds=[obj.matrix_world@Vector(p) for p in obj.bound_box]
        origin=Vector(emitter['center']);origin.z=min(p.z for p in bounds)-.0005
        sample['emission_surface_rays'].append({'emitter':emitter['object'],'origin':list(origin),
            'target':list(endpoint),'hits':hits_segment(origin,endpoint)})
light=next(o for o in s.objects if o.type=='LIGHT' and 'MAIN_B_BATH' in o.name)
filament=next(o for o in s.objects if 'MAIN_B_BATH' in o.name and o.name.endswith('_visible_emissive_filament'))
temp=bpy.data.collections.new('FW_DIAG_LINK_API');temp.objects.link(filament)
api={'light_linking_properties':[(p.identifier,p.type,p.description) for p in light.light_linking.bl_rna.properties],
     'collection_properties':[p.identifier for p in temp.bl_rna.properties]}
if hasattr(temp,'collection_objects'):
    member=temp.collection_objects[0]
    api['member_properties']=[p.identifier for p in member.bl_rna.properties]
    if hasattr(member,'light_linking'):
        api['member_light_linking']=[{'identifier':p.identifier,'type':p.type,
            'enum':[e.identifier for e in p.enum_items] if p.type=='ENUM' else []}
            for p in member.light_linking.bl_rna.properties]
report['shadow_linking_api']=api
bpy.data.collections.remove(temp)
(ROOT/'qa/eevee-iteration05-shadow-rays.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'lights':[(x['name'],x['type']) for x in lights],'views':report['views'],'living_emission_count':len(emit)},indent=2))
for evaluated,mesh in eval_mesh_cache.values():evaluated.to_mesh_clear()
