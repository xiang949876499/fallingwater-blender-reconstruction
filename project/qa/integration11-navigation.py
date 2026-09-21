"""Adapt only the saved south-terrace keys on the combined physical11 scene."""
from pathlib import Path
import bpy, hashlib, json, shutil, sys, time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
SOURCE=ROOT/'scene/Fallingwater_integration_candidate11a.blend'
SHA='2abe3f45e87d9e08971b9825da859b185b3259d50723bf3ccb1fcf1128dafaeb'
OUT=ROOT/'scene/Fallingwater_navigation_candidate11a.blend'
WORK=ROOT/'qa/integration11-navigation-workspace'
REF=ROOT/'qa/integration10-navigation-workspace/data/tour-route.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert bpy.app.background and sha(SOURCE)==SHA and not OUT.exists() and not WORK.exists()
started=time.monotonic()
for f in ('data','qa','scripts','scene'):(WORK/f).mkdir(parents=True,exist_ok=True)
for f in ('config.json','data/main_house.json','data/guest_house.json','adjacency.csv'):
    shutil.copy2(ROOT/f,WORK/f)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene
scene.render.threads_mode='FIXED';scene.render.threads=4
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
import guest_circulation10_routes as guest,master_navigation10 as master,master_navigation11 as nav
tour,rooms,gs=guest.prepare(WORK,scene,rooms)
ms=master.apply(tour,scene,rooms,WORK)
spec=nav.apply(tour,scene,rooms,WORK,reference_route=REF)
route=json.loads(REF.read_text(encoding='utf8'))
keys=nav.patch_saved_terrace_keys(scene,route,spec)
nav.embed_metadata(scene,rooms,spec)
(WORK/'data/tour-route.json').write_text(json.dumps(route,ensure_ascii=False,indent=2),encoding='utf8')
for name,value in [('FW_GUEST_CIRCULATION10_ROUTES.json',gs),('FW_MASTER_NAVIGATION10.json',ms)]:
    txt=bpy.data.texts.get(name) or bpy.data.texts.new(name);txt.clear();txt.write(json.dumps(value,indent=2))
scene.frame_set(48)
scene['navigation_revision11']='Combined local Master/terrace strict path pass; complete graph/saved-frame reopen still pending'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
result={'status':'COMBINED_LOCAL_NAV_PASS_FULL_REGRESSION_PENDING','source_sha256':SHA,'output':str(OUT),
        'sha256':sha(OUT),'bytes':OUT.stat().st_size,'keys':keys,'outward':spec['outward_step_status'],
        'inward':spec['inward_step_status'],'terrace_path_failure':spec['terrace_path_failure'],
        'seconds':time.monotonic()-started,'source_unchanged':sha(SOURCE)==SHA}
(ROOT/'qa/integration11-navigation.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result),flush=True)
