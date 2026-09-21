import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
import camera_review as cr
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scene/Fallingwater_iteration04.blend'))
scene=bpy.context.scene
settings=json.loads((ROOT/'qa/camera04-settings-frozen.json').read_text())
cr.integrate(scene,settings_path=ROOT/'qa/camera04-settings-frozen.json')
bpy.context.view_layer.update()
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
out=[]
for r in rooms:
    if r['id'] not in ('MAIN_B_BATH','MAIN_L1_SERVANT','MAIN_L1_SERVICE_STAIR','MAIN_L1_STAIR'):continue
    assets=[]
    for obj in scene.objects:
        if obj.type!='EMPTY' or obj.get('room_id')!=r['id'] or not obj.get('asset_type'):continue
        points=[child.matrix_world@Vector(q) for child in obj.children if child.type=='MESH' for q in child.bound_box]
        views={}
        for suffix in ('A','B'):
            cam=scene.objects['CAM_'+r['id']+'_'+suffix]
            projected=[world_to_camera_view(scene,cam,q) for q in points]
            if projected:views[suffix]={'xmin':min(p.x for p in projected),'xmax':max(p.x for p in projected),'ymin':min(p.y for p in projected),'ymax':max(p.y for p in projected),'mindepth':min(p.z for p in projected)}
        assets.append({'name':obj.name,'type':obj.get('asset_type'),'location':cr.plain(obj.matrix_world.translation),'views':views})
    out.append({'room':r,'assets':assets,'cameras':{s:settings['CAM_'+r['id']+'_'+s] for s in ('A','B')}})
cr.write_json(ROOT/'qa/camera04-frame-diagnostics.json',out)
print(json.dumps(out,ensure_ascii=True))
