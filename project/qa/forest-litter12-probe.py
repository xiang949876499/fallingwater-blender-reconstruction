"""Read actual visible terrain footprints and the isolated fern asset."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
P=R/'scene/Fallingwater_forest_floor_candidate11a.blend'
assert hashlib.sha256(P.read_bytes()).hexdigest()=='5bc4e480237bfa202b205370aea647e4501797ec46e8e335b5106f4ca9fc1d27'
bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene
terrain=s.objects['SITE_Continuous_BearRun_Terrain'];tree=BVHTree.FromObject(terrain,bpy.context.evaluated_depsgraph_get())
settings=json.loads((R/'qa/forest-floor11-camera-settings.json').read_text())
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
groups={'CAM_HERO':[(.22,.25),(.35,.26),(.5,.27),(.65,.3),(.8,.32),(.9,.26),(.6,.14),(.75,.16)],
        'CAM_MAIN_L1_LOGGIA_B':[(.08,.30),(.2,.27),(.35,.34),(.42,.47),(.24,.61),(.10,.6),(.48,.53),(.40,.23)],
        'CAM_WATER_DETAIL':[(.06,.4),(.18,.40),(.30,.52),(.15,.7),(.85,.35),(.94,.6)]}
report=[]
for name,pixels in groups.items():
    cam=s.objects[name];cfg=settings[name]
    if 'location'in cfg:
        cam.location=cfg['location'];cam.rotation_euler=(Vector(cfg['target'])-cam.location).to_track_quat('-Z','Y').to_euler()
        cam.data.lens=cfg['lens'];cam.data.shift_x=cfg['shift_x'];cam.data.shift_y=cfg['shift_y']
    bpy.context.view_layer.update();frame=cam.data.view_frame(scene=s)
    xmin,xmax=min(p.x for p in frame),max(p.x for p in frame);ymin,ymax=min(p.y for p in frame),max(p.y for p in frame)
    for u,v in pixels:
        d=(cam.matrix_world.to_3x3()@Vector((xmin+u*(xmax-xmin),ymax-v*(ymax-ymin),frame[0].z))).normalized()
        hit,n,idx,dist=tree.ray_cast(cam.matrix_world.translation,d,400)
        report.append({'camera':name,'image_uv_top':[u,v],'hit':list(hit)if hit else None,
                       'normal':list(n)if n else None,'distance_m':dist})
out={'status':'READ_ONLY_TERRAIN_FOOTPRINTS','source_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),
     'samples':report,'limits':'Terrain-only rays may pass behind intervening vegetation/architecture; manual viewed-image regions constrain selection.',
     'rendered':False,'saved':False}
(R/'qa/forest-litter12-probe.json').write_text(json.dumps(out,indent=2))
print('LITTER12_FOOTPRINTS',json.dumps(report),flush=True)
