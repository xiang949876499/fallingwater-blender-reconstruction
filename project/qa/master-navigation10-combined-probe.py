import bpy,sys,json,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import master_navigation10 as nav
SRC=R/'scene/Fallingwater_integration_candidate10a.blend'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()=='dc7594d60b68effaf10b85dd1804827fc9cb16dd786656daa4da16c761b33518'
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
ms=importlib.util.spec_from_file_location('tour_master10_combined_probe',R/'scripts/tour.py');tour=importlib.util.module_from_spec(ms);ms.loader.exec_module(tour)
work=R/'qa/master-navigation10-combined-workspace';work.mkdir(exist_ok=True);tour.ROOT=work
spec=nav.apply(tour,s,rooms,work);p=tour.master_navigation10_probe;byid={r['id']:r for r in rooms}
results={'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'scene':str(SRC),'paths':{},'cameras':{},'storage':{},'step_support':[],'objects':{}}
for name,path in spec['paths'].items():
 pts=nav.eyes(path['feet']);rows=[{'edge':i,'failure':p.segment(a,b,True)} for i,(a,b) in enumerate(zip(pts,pts[1:]))]
 results['paths'][name]={'pieces':rows,'result':tour.hinted_connection(byid[path['from']],byid[path['to']],p,{},[])}
 print(name,json.dumps(rows),flush=True)
for name,c in spec['cameras'].items():results['cameras'][name]={'proposal':c,'failure':p.point(c['eye'],True)}
candidates={rid:tour.room_candidates(byid[rid],p,True) for rid in (nav.MASTER,nav.BATH,nav.CLOSET)}
results['storage']=tour.storage_inspection(s,byid[nav.MASTER],byid[nav.CLOSET],p,candidates)
for name in [o.name for o in s.objects if o.name.startswith('MAIN_L2_master_south')]:
 ob=s.objects[name];eo=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=eo.to_mesh();v=[eo.matrix_world@a.co for a in me.vertices];eo.to_mesh_clear()
 results['objects'][name]={'min':[min(a[i] for a in v) for i in range(3)],'max':[max(a[i] for a in v) for i in range(3)],'opening_use':ob.get('opening_use'),'clear_width_m':ob.get('clear_width_m')}
for y in [7.17,7.11,7.05,6.94,6.90,6.88,6.85,6.82,6.80,6.76,6.65,6.59,6.53]:
 for x in [2.53,2.62,2.71]:
  hit=p.ray((x,y,3.10),(0,0,-1),.50)
  results['step_support'].append({'xy':[x,y],'hit':hit})
(R/'qa/master-navigation10-combined-probe.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print('STORAGE',json.dumps(results['storage']),flush=True)
print('DONE',flush=True)
