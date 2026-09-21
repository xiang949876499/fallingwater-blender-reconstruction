import bpy,sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'scene/Fallingwater_integration_candidate10a.blend'
assert hashlib.sha256(p.read_bytes()).hexdigest()=='dc7594d60b68effaf10b85dd1804827fc9cb16dd786656daa4da16c761b33518'
bpy.ops.wm.open_mainfile(filepath=str(p));deps=bpy.context.evaluated_depsgraph_get();rows=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH':continue
    vv=[o.matrix_world@v.co for v in o.data.vertices]
    if not vv:continue
    bb=[[min(v[i] for v in vv),max(v[i] for v in vv)] for i in range(3)]
    selected=o.name.startswith(('MAIN_L2_west','MAIN_L2_south','MAIN_L2_TERRACE_W','MAIN_L2_TERRACE_S','MAIN_L2_dressing'))
    near=(bb[2][1]>2.60 and bb[2][0]<3.7 and ((bb[0][1]>-13.6 and bb[0][0]<-4.35 and bb[1][1]>12.4 and bb[1][0]<18.25) or (bb[0][1]>-.7 and bb[0][0]<7.4 and bb[1][1]>-2.5 and bb[1][0]<6.8)))
    if not selected and not near:continue
    mods=[]
    for m in o.modifiers:
        mods.append({k:getattr(m,k,None) for k in ('name','type','width','segments','limit_method')})
    e=o.evaluated_get(deps);me=e.to_mesh()
    try:ev=[e.matrix_world@v.co for v in me.vertices];ebb=[[min(v[i] for v in ev),max(v[i] for v in ev)] for i in range(3)] if ev else None
    finally:e.to_mesh_clear()
    rows.append(dict(name=o.name,selected=selected,locator_bounds=bb,evaluated_bounds=ebb,materials=[m.name if m else None for m in o.data.materials],modifiers=mods,vertices=len(vv),faces=len(o.data.polygons),role=o.get('role'),component=o.get('component_type')))
cams=[{'name':o.name,'location':list(o.matrix_world.translation)} for o in bpy.context.scene.objects if o.type=='CAMERA' and ('TERRACE' in o.name or 'EXTERIOR' in o.name)]
(R/'qa/main-terrace11-before-probe.json').write_text(json.dumps(dict(scene=str(p),objects=rows,cameras=cams),indent=2),encoding='utf-8')
print(json.dumps({'targets':[r for r in rows if r['selected']],'nearby_others':[r['name'] for r in rows if not r['selected']],'cameras':cams},indent=2))
