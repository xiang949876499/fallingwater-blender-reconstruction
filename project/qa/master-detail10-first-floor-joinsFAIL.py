"""Read-only all changed finished-floor joins, preserving every old failure."""
import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import main_house as mh
SRC=R/'scene/Fallingwater_master_detail_candidate10e.blend';bpy.ops.wm.open_mainfile(filepath=str(SRC))
s=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
build=json.loads((R/'qa/master-detail10-build-check.json').read_text(encoding='utf-8'));trees={}
for o in s.objects:
 if o.type!='MESH' or not o.name.startswith('MAIN_') or not o.name.endswith('_finish'):continue
 e=o.evaluated_get(deps);m=e.to_mesh();trees[o.name]=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[tuple(f.vertices) for f in m.polygons]);e.to_mesh_clear()
def inside(p,poly):
 r=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:r=not r
 return r
rows=[]
for g in build['manifest']['geometry']:
 if not g['name'].endswith('_finish') or g['name']=='MAIN_L2_MASTER_finish':continue
 poly=[mh.xy(q) for q in g['source_polygon']];z=g['z'][1]
 for ix in range(45):
  for iy in range(45):
   q=[min(v[k] for v in poly)+(max(v[k] for v in poly)-min(v[k] for v in poly))*((ix if k==0 else iy)+(.371 if k==0 else .413))/45 for k in (0,1)]
   if not inside(q,poly):continue
   hits=[]
   for n,t in trees.items():
    p,no,f,d=t.ray_cast(Vector((*q,z+.03)),Vector((0,0,-1)),.06)
    if p is not None and abs(p.z-z)<1e-4:hits.append(n)
   rows.append({'owner':g['name'],'xy':q,'layers':hits,'pass':len(hits)==1})
report={'candidate':str(SRC),'sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'status':'PASS_CHANGED_FLOOR_JOINS' if all(q['pass'] for q in rows) else 'FAIL_CHANGED_FLOOR_JOINS','samples':len(rows),'failures':sum(not q['pass'] for q in rows),'rows':rows}
(R/'qa/master-detail10-floor-joins-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({k:report[k] for k in ('status','samples','failures')},indent=2))
