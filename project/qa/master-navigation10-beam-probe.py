"""Actual10f ceiling failure; read-only, CPU4, no navigation claims."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import main_house as mh
SRC=R/'scene/Fallingwater_master_detail_candidate10f.blend'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()=='f7ff5b0ab1317b0d375b884b651497bbc26e573cceebe5a9d15139a9c8e9ba5c'
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene;dep=bpy.context.evaluated_depsgraph_get();rows=[]
def ray(origin,direction,length):
 h,p,n,f,o,m=s.ray_cast(dep,Vector(origin),Vector(direction),distance=length)
 return {'object':o.name,'point':list(p),'normal':list(n),'face':f} if h else None
for py in (351,354.2,357,359.4,362):
 for px in (339,344,350,359,367,371):
  xy=mh.xy((px,py));g=ray((*xy,2.8668+.06),(0,0,-1),.15)
  ground=g['point'][2] if g else None
  roof=ray((*xy,2.8668+.09),(0,0,1),2.5)
  head=roof['point'][2]-2.8668 if roof else None
  rows.append({'source_xy':[px,py],'ground':g,'ground_delta':None if ground is None else ground-2.8668,'up':roof,'clear_height_m':head,'ground4mm':ground is not None and abs(ground-2.8668)<=.004,'headroom195':head is not None and head>=1.95})
o=s.objects['MASTER_DETAIL10_west_connected_soffit'];v=[o.matrix_world@q.co for q in o.data.vertices]
report={'source':str(SRC),'sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'object':o.name,'actual_bounds':[[min(p[k] for p in v),max(p[k] for p in v)] for k in range(3)],'rows':rows,'failures':[r for r in rows if r['ground4mm'] and not r['headroom195']],'status':'FAIL_PHYSICAL_HEADROOM_C_SOFFIT_NOT_A_ROUTE_PROBLEM','no_scene_save':True,'physical_helper_not_edited':True}
(R/'qa/master-navigation10-beam-probe.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({'bounds':report['actual_bounds'],'failures':len(report['failures']),'first_failure':report['failures'][0]},indent=2))
