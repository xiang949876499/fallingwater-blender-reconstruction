"""Read-only frozen masonry inspection. No source modules, edits or saves."""
import bpy, json, hashlib, statistics
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
P=R/'scene/Fallingwater_main_terrace_candidate11a.blend'
EXPECTED='e856456005d3a4493e70122644d52192dd49c2d2ffc046248b1247484beb4750'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(P)==EXPECTED
bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;s.frame_set(48)
deps=bpy.context.evaluated_depsgraph_get()
def bounds(vs):return [[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)]
def obj(o):
    v=[o.matrix_world@v.co for v in o.data.vertices]
    e=o.evaluated_get(deps);m=e.to_mesh();m.calc_loop_triangles()
    ev=[e.matrix_world@v.co for v in m.vertices]
    rec={'name':o.name,'bounds':bounds(v),'evaluated_bounds':bounds(ev),'scale':list(o.scale),'matrix':[list(r) for r in o.matrix_world],
         'local_bounds':bounds([v.co for v in o.data.vertices]),'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),'evaluated_triangles':len(m.loop_triangles),
         'flat_polygons':sum(not p.use_smooth for p in m.polygons),'smooth_polygons':sum(p.use_smooth for p in m.polygons),
         'materials':[x.name if x else None for x in o.data.materials],'modifiers':[{k:getattr(q,k,None) for k in ('name','type','width','segments')} for q in o.modifiers]}
    rec['world_geometry_sha256']=hashlib.sha256(json.dumps({'v':[[round(c,8) for c in w] for w in ev],'p':[list(p.vertices) for p in m.polygons]},sort_keys=True).encode()).hexdigest()
    e.to_mesh_clear();return rec
targets=[o for o in s.objects if o.type=='MESH' and o.name.startswith(('MAIN_stone_tower_','MAIN_tower_course','MAIN_chimney_cap','MAIN_chimney_flue'))]
rows=[obj(o) for o in sorted(targets,key=lambda o:o.name)]
mat=bpy.data.materials['FW_stone'];p=mat.node_tree.nodes.get('Principled BSDF')
nodes=[]
for n in mat.node_tree.nodes:
    d={'name':n.name,'type':n.bl_idname}
    for k in ('operation','projection','projection_blend','blend_type','invert'):
        if hasattr(n,k):d[k]=getattr(n,k)
    if hasattr(n,'image') and n.image:d['image']={'name':n.image.name,'filepath':n.image.filepath,'colorspace':n.image.colorspace_settings.name}
    for k in ('Scale','Strength','Distance','To Min','To Max'):
        if k in n.inputs:d[k]=n.inputs[k].default_value
    if n.type=='MIX_RGB':d['tint']=list(n.inputs[2].default_value)
    nodes.append(d)
links=[{'from':l.from_node.name+'.'+l.from_socket.name,'to':l.to_node.name+'.'+l.to_socket.name} for l in mat.node_tree.links]
def ray(cname,px,py):
    c=s.objects[cname];proj=c.calc_matrix_camera(deps,x=960,y=540,scale_x=1,scale_y=1)
    q=proj.inverted()@Vector((px/960*2-1,1-py/540*2,-1,1));v=Vector((q.x/q.w,q.y/q.w,q.z/q.w))
    origin=c.matrix_world.translation;direction=(c.matrix_world.to_3x3()@v).normalized()
    hit,loc,norm,idx,o,mx=s.ray_cast(deps,origin,direction)
    return {'camera':cname,'pixel':[px,py],'hit':hit,'object':o.name if o else None,'location':list(loc),'normal':list(norm),'polygon':idx}
rays=[ray('CAM_MAIN_L2_TERRACE_W_A',*xy) for xy in [(405,185),(940,55),(943,185),(352,47)]]+[ray('CAM_MAIN_L2_TERRACE_S_A',*xy) for xy in [(69,25),(31,36),(47,161)]]
stoneusers=[o.name for o in s.objects if o.type=='MESH' and any(m==mat for m in o.data.materials)]
courses=[x for x in rows if x['name'].startswith('MAIN_tower_course')]
output={'source':str(P),'sha256':EXPECTED,'frame':48,'target_objects':rows,'target_count':len(rows),'course_count':len(courses),
        'course_rows':len(set(x['name'].split('_course')[-1].split('_')[0] for x in courses)),
        'course_unique_z_heights':sorted(set(round(x['bounds'][2][1]-x['bounds'][2][0],6) for x in courses)),
        'target_evaluated_triangles':sum(x['evaluated_triangles'] for x in rows),
        'FW_stone':{'users_count':len(stoneusers),'users':stoneusers,'nodes':nodes,'links':links,'properties':dict(mat.items())},'terrace_pixel_rays':rays,
        'dependencies':{str(q.relative_to(R)):sha(q) for q in [R/'scripts/main_house.py',R/'scripts/masonry_detail.py',R/'scripts/materials.py',R/'scripts/asset_materials.py',R/'scripts/fwlib.py',R/'data/masonry-detail.json']},
        'source_unchanged_after_probe':sha(P)==EXPECTED,'saved':False,'rendered':False}
(R/'qa/masonry12-source-probe.json').write_text(json.dumps(output,indent=2),encoding='utf-8')
print(json.dumps({k:output[k] for k in ('target_count','course_count','course_rows','course_unique_z_heights','target_evaluated_triangles','terrace_pixel_rays','source_unchanged_after_probe')},indent=2))
