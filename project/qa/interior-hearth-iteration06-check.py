"""Local replacement only, real mesh regressions, no rendering."""
import bpy, json, sys, hashlib, bmesh
from pathlib import Path
from types import SimpleNamespace
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
VARIANT='06b' if '--variant06b' in sys.argv else '06'
sys.path.insert(0,str(ROOT/'scripts'))
import furnishings, tour, fwlib
scene=bpy.context.scene
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
room=next(r for r in rooms if r['id']=='MAIN_L1_LIVING')
root=next(o for o in scene.objects if o.type=='EMPTY' and o.get('asset_type')=='emergent_hearth_bedrock')
children=list(root.children)
archival={'source_scene':bpy.data.filepath,'root':root.name,'children':[
    {'name':o.name,'type':o.type,'world_matrix':[list(row) for row in o.matrix_world],
     'vertices':[list(v.co) for v in o.data.vertices] if o.type=='MESH' else None,
     'faces':[list(p.vertices) for p in o.data.polygons] if o.type=='MESH' else None}
    for o in children]}
(ROOT/'qa/interior-hearth-iteration05-geometry.json').write_text(json.dumps(archival,indent=2),encoding='utf-8')
before_identity={o.name:(o.type,len(o.data.vertices) if o.type=='MESH' else None,
    tuple(round(v,7) for row in o.matrix_world for v in row)) for o in scene.objects if o not in children and o!=root}
fixture_count=len([o for o in scene.objects if o.type=='LIGHT' and 'service' in o.name.lower()])
paths=[]
route=json.loads((ROOT/'qa/tour-path-route-iteration05-final.json').read_text(encoding='utf-8'))
for s in route['main_segments']+route['supplemental_segments']:
    if 'MAIN_L1_LIVING' in s['room_ids']:
        paths.append({'label':s['id'],'points':s['points'],'walk':s['mode'].startswith('NORMAL')})
adj=json.loads((ROOT/'qa/tour-path-all-adjacency-iteration05-final.json').read_text(encoding='utf-8'))
for edge in adj['edges']:
    if 'MAIN_L1_LIVING' not in (edge['from'],edge['to']):continue
    if edge.get('points'):paths.append({'label':edge['id'],'points':edge['points'],'walk':True})
    if edge.get('inspection_motion'):paths.append({'label':edge['id']+'_inspection','points':edge['inspection_motion'],'walk':True})
probe=tour.Probe(scene,((-2,12),(0,17),(-.5,3.5)))
for p in paths:p['before']=probe.path(p['points'],p['walk'])
del probe
for obj in children:bpy.data.objects.remove(obj,do_unlink=True)
ctx=SimpleNamespace(root=ROOT,mats={m.name[3:]:m for m in bpy.data.materials if m.name.startswith('FW_')},collection=fwlib.collection)
r=furnishings.Room(ctx,room)
a=furnishings.Asset.__new__(furnishings.Asset)
a.owner=r;a.ctx=ctx;a.root=root;a.kind='emergent_hearth_bedrock';a.w=2.23;a.d=2.89
a.ref='HABS PA-5346 main04/main11 and PA-5346-48';a.evidence='C';a.objects=[];a.name=root.name
furnishings.hearth_rock(a)
bpy.context.view_layer.update()
probe=tour.Probe(scene,((-2,12),(0,17),(-.5,3.5)))
for p in paths:p['after']=probe.path(p['points'],p['walk'])
camera=bpy.data.objects['CAM_MAIN_L1_LIVING_B']
camera_check=probe.point(camera.matrix_world.translation,True)
meshes=[]
for obj in root.children:
    if obj.type!='MESH':continue
    bm=bmesh.new();bm.from_mesh(obj.data)
    verts=[obj.matrix_world@v.co for v in obj.data.vertices]
    meshes.append({'name':obj.name,'vertex_count':len(verts),'faces':len(obj.data.polygons),
        'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),
        'world_bounds':[[min(p[k] for p in verts),max(p[k] for p in verts)] for k in range(3)]})
    bm.free()
# Test underlying actual architecture with the authored rock itself excluded.
verts=[];faces=[];owners=[]
for obj in scene.objects:
    if obj.type!='MESH' or obj.hide_render or obj.parent==root:continue
    bb=[obj.matrix_world@Vector(p) for p in obj.bound_box]
    if any(max(p[k] for p in bb)<low or min(p[k] for p in bb)>high for k,(low,high) in enumerate(((-1,3),(8,12),(-.3,.5)))):continue
    offset=len(verts);verts.extend(obj.matrix_world@v.co for v in obj.data.vertices)
    faces.extend(tuple(offset+i for i in f.vertices) for f in obj.data.polygons)
    owners.extend([obj.name]*len(obj.data.polygons))
support=BVHTree.FromPolygons(verts,faces,epsilon=.001)
contacts=[]
for obj in root.children:
    if obj.type!='MESH' or 'native_lobe' not in obj.name:continue
    seen=set()
    for v in obj.data.vertices:
        p=obj.matrix_world@v.co
        if abs(p.z-(room['z']-.024))>.00001:continue
        key=(round(p.x,3),round(p.y,3))
        if key in seen:continue
        seen.add(key)
        loc,n,index,d=support.ray_cast(Vector((p.x,p.y,room['z']+.08)),Vector((0,0,-1)),.30)
        hit_name=owners[index] if index is not None else None
        masonry_seat=hit_name=='FW_MASONRY_MAIN_HEARTH' and loc is not None and p.z<=loc.z<=room['z']+.12
        floor_seat=loc is not None and p.z<=loc.z<=room['z']+.04
        contacts.append({'rock':obj.name,'point':list(p),'floor_hit':hit_name,
            'floor_z':loc.z if loc is not None else None,
            'support_kind':'existing hearth masonry edge' if masonry_seat else 'finished floor',
            'base_embedded':floor_seat or masonry_seat})
after_identity={o.name:(o.type,len(o.data.vertices) if o.type=='MESH' else None,
    tuple(round(v,7) for row in o.matrix_world for v in row)) for o in scene.objects if o.parent!=root and o!=root}
unchanged=before_identity==after_identity
clearance=[]
# Actual aperture remains open over the new rock, below the unchanged lintel.
for y in (9.15,9.5,9.9,10.3,10.7):
    for z in (.60,.90,1.20):
        hit=probe.ray((.45,y,z),(-1,0,0),.48)
        clearance.append({'point':[.45,y,z],'hit':hit,'new_rock_obstruction':bool(hit and 'native_lobe' in hit['object'])})
fail_paths=[p['label'] for p in paths if p['after'] and not p['before']]
result={'status':'PASS_LOCAL_GEOMETRY_NOT_VISUAL_ACCEPTANCE' if unchanged and not fail_paths and not camera_check and all(c['base_embedded'] for c in contacts) and not any(c['new_rock_obstruction'] for c in clearance) and all(m['non_manifold_edges']==0 for m in meshes) else 'FAIL_LOCAL_GEOMETRY',
    'source_scene':bpy.data.filepath,'source_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
    'all_other_object_transforms_and_mesh_counts_unchanged':unchanged,'practical_fixture_config_count':len(furnishings.PRACTICAL_FIXTURES),
    'new_path_failures':fail_paths,'paths':paths,'living_B_camera_body_failure':camera_check,
    'meshes':meshes,'ground_contacts':contacts,'aperture_checks':clearance,
    'visual_status':'NOT_RUN: root will render unchanged Living_B camera; 05 tour evidence remains frozen'}
(ROOT/f'qa/interior-hearth-iteration{VARIANT}-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/f'scene/Fallingwater_hearth_candidate{VARIANT}.blend'),compress=True)
print('HEARTH_RESULT',json.dumps({k:v for k,v in result.items() if k not in ('paths','ground_contacts','aperture_checks','meshes')}),flush=True)
