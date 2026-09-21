import bpy,sys,json,hashlib,copy,importlib.util
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import master_navigation10 as nav
import master_bath_detail10 as bath
import master_detail10 as master
SRC=R/'scene/Fallingwater_master_detail_candidate10g.blend'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()=='34dbbb2b6639718a11d876f9ef44d2de251513a701c4c04ba4611a763bda7631'
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene
bath.apply();master.refresh_master_floor(True);bpy.context.view_layer.update()
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
ms=importlib.util.spec_from_file_location('tour_master10_local',R/'scripts/tour.py');tour=importlib.util.module_from_spec(ms);ms.loader.exec_module(tour)
work=R/'qa/master-navigation10-workspace';work.mkdir(exist_ok=True);tour.ROOT=work
spec=nav.apply(tour,s,rooms,work);p=tour.master_navigation10_probe
byid={r['id']:r for r in rooms};results={'source':str(SRC),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'in_memory_bath_apply':True,'master_refresh_true':True,'mesh':p.mesh_counts,'paths':{},'old_cameras':{},'proposed_cameras':{},'room_shots':{},'saved':False}
for name,c in spec['cameras'].items():
 ob=s.objects[name];eye=ob.matrix_world.translation
 results['old_cameras'][name]={'eye':list(eye),'failure':p.point(eye,True)}
 results['proposed_cameras'][name]={'eye':c['eye'],'failure':p.point(c['eye'],True)}
for name,path in spec['paths'].items():
 points=nav.eyes(path['feet']);rows=[]
 for i,(a,b) in enumerate(zip(points,points[1:])):
  rows.append({'edge':i,'from':a,'to':b,'failure':p.segment(a,b,True)})
 result=tour.hinted_connection(byid[path['from']],byid[path['to']],p,{},[])
 results['paths'][name]={'rows':rows,'adapter_result':result}
 print(name,json.dumps({'failures':[r for r in rows if r['failure']]}),flush=True)
candidates={rid:tour.room_candidates(byid[rid],p,True) for rid in (nav.MASTER,nav.BATH,nav.CLOSET)}
for rid in candidates:
 shot,issue=tour.room_shot(byid[rid],p,candidates)
 results['room_shots'][rid]={'candidates':[list(x) for x in candidates[rid]],'shot':shot,'issue':issue}
results['storage']=tour.storage_inspection(s,byid[nav.MASTER],byid[nav.CLOSET],p,candidates)
results['source_helpers_sha256']={n:hashlib.sha256((R/'scripts'/n).read_bytes()).hexdigest() for n in ('master_detail10.py','master_bath_detail10.py','master_navigation10.py')}
(R/'qa/master-navigation10-diagnostic.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print('CAMERAS',json.dumps(results['proposed_cameras']),flush=True)
print('SHOTS',json.dumps(results['room_shots']),flush=True)
print('STORAGE',json.dumps(results['storage']),flush=True)
