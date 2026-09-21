"""Read-only architectural landmark extraction from frozen12a; never saves scene."""
import bpy,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCENE=ROOT/'scene/Fallingwater_guest_bays_candidate12a.blend'
EXPECTED='ebe6748261e9716ea9f9bd07e9137da1955798a7b3356bedc0d6a14d06638548'
assert hashlib.sha256(SCENE.read_bytes()).hexdigest()==EXPECTED
bpy.ops.wm.open_mainfile(filepath=str(SCENE))
bpy.context.scene.render.threads_mode='FIXED';bpy.context.scene.render.threads=4
dg=bpy.context.evaluated_depsgraph_get()
prefixes=('GUEST_L1_LOUNGE_FRONT','GUEST_LOW_ARM_ROOF','GUEST_C10_W1_FRONT','GUEST_C10_W2_FRONT','GUEST_C10_P_FRONT','GUEST_C10_MAIN_FLOOR_EAST','GUEST_C10_FRONT_LOUNGE','GUEST_L1_TERRACE','GUEST_L1_BED_FRONT','GUEST_C10_SOUTHEAST_ENTRY','GUEST_L1_LOUNGE_EAST_PIER','GUEST_L1_WEST_LOUNGE','GUEST_C10_P_SOUTH_LOW')
obs={}
for ob in bpy.context.scene.objects:
    if ob.type!='MESH' or not ob.name.startswith(prefixes):continue
    world=[list(ob.matrix_world@v.co) for v in ob.data.vertices]
    ev=ob.evaluated_get(dg);mesh=ev.to_mesh()
    obs[ob.name]={'world_vertices':world,'edges':[list(e.vertices) for e in ob.data.edges],
      'faces':[list(p.vertices) for p in ob.data.polygons],
      'evaluated_world_vertices':[list(ob.matrix_world@v.co) for v in mesh.vertices],
      'evaluated_faces':[list(p.vertices) for p in mesh.polygons],
      'materials':[m.name if m else None for m in ob.data.materials],
      'properties':{k:str(ob[k]) for k in ob.keys()},
      'modifiers':[{'name':m.name,'type':m.type} for m in ob.modifiers]}
    ev.to_mesh_clear()
out={'scene':str(SCENE),'scene_sha256':EXPECTED,'read_only':True,'objects':obs}
(ROOT/'qa/photo-match12-guest-mesh.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({'objects':len(obs),'names':list(obs)},indent=2))
assert hashlib.sha256(SCENE.read_bytes()).hexdigest()==EXPECTED
