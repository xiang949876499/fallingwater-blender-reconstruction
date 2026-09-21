import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
P=Path('D:/zx/test/project');S=P/'scene/Fallingwater_iteration06.blend'
EXPECTED='172b76340d1224a2b98f415b21042d19ad7fba4d849543d7156beb17e5fcf055'
assert hashlib.sha256(S.read_bytes()).hexdigest()==EXPECTED
bpy.ops.wm.open_mainfile(filepath=str(S));dg=bpy.context.evaluated_depsgraph_get();scene=bpy.context.scene
def world(p,z):return ((p[0]-327)*.0524,(540-p[1])*.0531,z)
def source(v):return [v[0]/.0524+327,540-v[1]/.0531]
def ray(a,b):
 a,b=Vector(a),Vector(b);v=b-a
 ok,p,n,i,o,m=scene.ray_cast(dg,a,v.normalized(),distance=v.length)
 return {'object':o.name,'point_m':list(p),'source_px':source(p),'normal':list(n)} if ok else None
selected={}
for o in scene.objects:
 if o.type!='MESH' or not (o.name in ['MAIN_B_pool_wall_0','MAIN_B_pool_wall_1','MAIN_B_pool_wall_2','MAIN_loggia_stair_lower_landing','MAIN_B_plunge_water','MAIN_B_pool_deck_north','MAIN_B_pool_deck_east','MAIN_B_pool_deck_south','MAIN_B_pool_deck_west'] or o.name.startswith('MAIN_pool_eastterrace_stair')):continue
 ev=o.evaluated_get(dg);m=ev.to_mesh()
 try:
  vs=[ev.matrix_world@v.co for v in m.vertices]
  lo=[min(v[a] for v in vs) for a in range(3)];hi=[max(v[a] for v in vs) for a in range(3)]
  selected[o.name]={'min_m':lo,'max_m':hi,'min_source_px':source(lo),'max_source_px':source(hi)}
 finally:ev.to_mesh_clear()
cross=[]
for px in [627,640,674,685,690,695]:
 for z in [-2.2,-2.0,-1.9]:
  cross.append({'source_x':px,'z':z,'hit':ray(world((px,371),z),world((px,384),z))})
floor=[]
for p in [(690,362),(690,375),(690,382),(674,382),(640,382),(600,382),(550,382),(540,382),(540,423),(680,401),(694,410),(675,424)]:
 floor.append({'source_px':p,'hit':ray(world(p,-2.28),world(p,-3.7))})
route=[]
for z in [-2.15,-1.95,-1.55,-.6]:
 route.append({'z':z,'hit':ray((19.126,8.345,z),(11.1612,8.345,z))})
out={'scene':str(S),'scene_sha256':EXPECTED,'scene_mutated':False,'rendered':False,'selected_evaluated_bounds':selected,'landing_to_north_band_wall_sections':cross,'floor_points':floor,'north_band_westward_rays':route,'limits':'Read-only probe of frozen06. Geometric diagnosis only, not source authorization to remove a full wall or claim a dry route.'}
(P/'qa/main-pool-iteration06-mesh.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({'wall':selected['MAIN_B_pool_wall_0'],'lower_landing':selected['MAIN_loggia_stair_lower_landing'],'sample_690':[r for r in cross if r['source_x']==690],'westward':route,'floor':floor},indent=2))
assert hashlib.sha256(S.read_bytes()).hexdigest()==EXPECTED
