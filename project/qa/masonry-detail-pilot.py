import bpy,bmesh,sys,json,hashlib,time
from pathlib import Path
from types import SimpleNamespace
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from fwlib import collection
import masonry_detail

def signature(o):
    h=hashlib.sha256()
    h.update(str([list(r) for r in o.matrix_world]).encode())
    h.update(str(o.hide_render).encode())
    if o.type=='MESH':
        h.update(str([(tuple(v.co)) for v in o.data.vertices]).encode())
        h.update(str([tuple(p.vertices) for p in o.data.polygons]).encode())
        h.update(str([m.name if m else None for m in o.data.materials]).encode())
    return h.hexdigest()

source=ROOT/'scene/Fallingwater_iteration04.blend'
bpy.ops.wm.open_mainfile(filepath=str(source))
config=json.loads((ROOT/'data/masonry-detail.json').read_text())
assert hashlib.sha256(source.read_bytes()).hexdigest()==config['source_sha256']
existing={o.name:signature(o) for o in bpy.data.objects if o.type=='MESH' and (o.name.startswith('MAIN_L1_hearth') or o.name.startswith('GUEST_L1_') or o.name=='GUEST_LAYERED_SANDSTONE_COURSES')}
report=masonry_detail.build(SimpleNamespace(root=ROOT,mats={'stone':bpy.data.materials['FW_stone']},collection=collection),[],include_guest=False)
report['source_sha256']=config['source_sha256']
report['unchanged_substrate_check']={'objects_checked':len(existing),'changed':[name for name,sha in existing.items() if signature(bpy.data.objects[name])!=sha]}
assert not report['unchanged_substrate_check']['changed']
trees=[]
mesh_checks=[]
for item in report['meshes']:
    obj=bpy.data.objects[item['object']]
    bm=bmesh.new();bm.from_mesh(obj.data)
    nonmanifold=sum(not e.is_manifold for e in bm.edges)
    volume=bm.calc_volume(signed=True)
    trees.append((obj.name,BVHTree.FromBMesh(bm)))
    mesh_checks.append({'object':obj.name,'nonmanifold_edges':nonmanifold,'signed_volume_m3':volume,'modifiers':len(obj.modifiers),'unit_scale':list(obj.scale)})
    bm.free()
    assert nonmanifold==0 and volume>0
report['mesh_checks']=mesh_checks

probes=[]
def probe(label,start,end):
    a,b=Vector(start),Vector(end);d=b-a
    hits=[]
    for name,tree in trees:
        hit=tree.ray_cast(a,d.normalized(),d.length)
        if hit[0] is not None:hits.append({'object':name,'point':list(hit[0]),'distance':hit[3]})
    probes.append({'label':label,'start':start,'end':end,'hits':hits})

# Actual new geometry must leave the previously open fireplace face clear.
for iy in range(11):
    for iz in range(9):
        y=8.899+iy*(10.915-8.899)/10
        z=.16+iz*(1.418-.16)/8
        probe('main_firebox',(.9,y,z),(-.30,y,z))
# Both lounge doors, including near edge samples, must retain the original void.
for y0,y1,x0,x1,label in [(36.412,37.434,3.40,4.10,'guest_west_door'),(37.16,38.16,9.3,10.0,'guest_east_door')]:
    for iy in range(11):
        for iz in range(9):
            y=y0+iy*(y1-y0)/10;z=8.46+iz*(10.46-8.46)/8
            probe(label,(x0,y,z),(x1,y,z))
report['opening_rays']={'rays':len(probes),'blocked':sum(bool(p['hits']) for p in probes),'records':probes}
assert report['opening_rays']['blocked']==0
report['status']='GEOMETRY_CHECKS_PASS_VISUAL_PENDING'
(ROOT/'qa/masonry-detail-pilot.json').write_text(json.dumps(report,indent=2),encoding='utf8')

s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=32
s.cycles.use_denoising=True;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.025
s.render.threads_mode='FIXED';s.render.threads=4
s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100
s.render.use_persistent_data=True;s.frame_set(48)
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA'
guest=bpy.data.cameras.new('FW_MASONRY_GUEST_DETAIL');cam=bpy.data.objects.new('FW_MASONRY_GUEST_DETAIL',guest);collection('80_CAMERAS').objects.link(cam)
cam.location=(5.60,37.40,9.94);target=Vector((3.84,39.05,9.68));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();guest.lens=29;guest.clip_start=.02;cam['fw_exposure']=3.0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'qa/masonry-detail-pilot.blend'))
renders=[]
for camera_name,out in [('CAM_MAIN_L1_LIVING_B','main')]:
    s.camera=bpy.data.objects[camera_name]
    s.view_settings.exposure=float(s.camera.get('fw_exposure',3.0))
    s.render.filepath=str(ROOT/f'qa/masonry-detail-{out}.png')
    t=time.perf_counter();bpy.ops.render.render(write_still=True)
    renders.append({'camera':camera_name,'file':s.render.filepath,'seconds':time.perf_counter()-t,'exposure':s.view_settings.exposure,'width':960,'height':540,'samples':32,'threads':4,'device':'CPU'})
    (ROOT/'qa/masonry-detail-render.json').write_text(json.dumps(renders,indent=2))
print('MASONRY_PILOT_COMPLETE',flush=True)
