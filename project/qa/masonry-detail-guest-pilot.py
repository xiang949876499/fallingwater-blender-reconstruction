"""Guest05-only masonry validation and one CPU near-view. No shared outputs."""
import bpy,bmesh,sys,json,hashlib,time,itertools
from pathlib import Path
from types import SimpleNamespace
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from fwlib import collection
from materials import build_materials
import guest_house,masonry_detail,lighting,asset_materials

def signature(obj):
    h=hashlib.sha256()
    for value in ([list(r) for r in obj.matrix_world],obj.hide_render,[tuple(v.co) for v in obj.data.vertices],[tuple(f.vertices) for f in obj.data.polygons],[m.name if m else None for m in obj.data.materials]):h.update(str(value).encode())
    return h.hexdigest()

bpy.ops.wm.read_factory_settings(use_empty=True)
ctx=SimpleNamespace(root=ROOT,mats=build_materials(),collection=collection,config=json.loads((ROOT/'config.json').read_text(encoding='utf8')))
rooms=guest_house.build(ctx)
bpy.context.view_layer.update()
before={o.name:signature(o) for o in bpy.context.scene.objects if o.type=='MESH'}
report=masonry_detail.build(ctx,rooms,include_main=False,include_guest=True)
bpy.context.view_layer.update()
report['sources']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ('scripts/guest_house.py','scripts/guest_architectural_detail.py','data/guest_house.json','scripts/masonry_detail.py','data/masonry-detail.json')}
report['unchanged_substrates']={'count':len(before),'changed':[name for name,sha in before.items() if signature(bpy.data.objects[name])!=sha]}
assert not report['unchanged_substrates']['changed']
obj=bpy.data.objects['FW_MASONRY_GUEST_LOUNGE']
bm=bmesh.new();bm.from_mesh(obj.data)
report['mesh']={'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume_m3':bm.calc_volume(signed=True),'vertices':len(obj.data.vertices),'polygons':len(obj.data.polygons),'modifiers':len(obj.modifiers)}
tree=BVHTree.FromBMesh(bm);bm.free()
assert report['mesh']['nonmanifold_edges']==0 and report['mesh']['signed_volume_m3']>0
config=json.loads((ROOT/'data/masonry-detail.json').read_text())
exclusion=config['guest']['strict_firebox_exclusion']
bounds=[]
for i,stone in enumerate(report['meshes'][0]['stones']):
    va,vb=stone['vertices'];points=[obj.matrix_world@obj.data.vertices[j].co for j in range(va,vb)]
    bounds.append(([min(p[k] for p in points) for k in range(3)],[max(p[k] for p in points) for k in range(3)]))
def overlap(a,b):return [min(a[1][k],b[1][k])-max(a[0][k],b[0][k]) for k in range(3)]
opening=(exclusion['min'],exclusion['max'])
inside=[i for i,b in enumerate(bounds) if min(overlap(b,opening))>.000001]
pairs=[(i,j) for i,j in itertools.combinations(range(len(bounds)),2) if min(overlap(bounds[i],bounds[j]))>.000001]
report['overlap']={'stone_count':len(bounds),'tested_pairs':len(bounds)*(len(bounds)-1)//2,'overlap_pairs':pairs,'stones_intersecting_strict_firebox_box':inside}
if inside or pairs:
    (ROOT/'qa/masonry-detail-guest-rejected-overlap.json').write_text(json.dumps(report,indent=2))
    print('MASONRY_OVERLAP_REJECTED',report['overlap'],flush=True)
assert not inside and not pairs
rays=[]
lo,hi=exclusion['min'],exclusion['max']
for i in range(11):
    for j in range(11):
        z=lo[2]+.004+(hi[2]-lo[2]-.008)*j/10
        x=lo[0]+.004+(hi[0]-lo[0]-.008)*i/10
        y=lo[1]+.004+(hi[1]-lo[1]-.008)*i/10
        # These are strict free-volume probes. Separate retained diagnostics
        # document the 40 mm exterior approach at the adjacent north-wall edge.
        for label,a,b in [('south',(x,lo[1]+.002,z),(x,hi[1]-.002,z)),('east',(hi[0]-.002,y,z),(lo[0]+.002,y,z))]:
            av,bv=Vector(a),Vector(b);d=bv-av;hit=tree.ray_cast(av,d.normalized(),d.length)
            rays.append({'face':label,'start':a,'end':b,'new_masonry_hit':list(hit[0]) if hit[0] is not None else None})
report['opening_rays']={'scope':'Strict cavity interior, endpoints 2 mm inside bounds. Exterior approach fringe is separately retained in masonry-detail-guest-rejected-rays.json.','total':len(rays),'blocked':sum(r['new_masonry_hit'] is not None for r in rays),'records':rays}
if report['opening_rays']['blocked']:
    (ROOT/'qa/masonry-detail-guest-rejected-rays.json').write_text(json.dumps(report,indent=2))
    print('MASONRY_RAY_REJECTED',[r for r in rays if r['new_masonry_hit'] is not None],flush=True)
assert report['opening_rays']['blocked']==0
s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4
source=ROOT/'qa/masonry-detail-guest-geometry.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(source))

# Reuse the frozen author's independent structural dimension measurements.
# It queries named actual evaluated faces and retains the original tolerance.
dimension_script=(ROOT/'qa/guest-dimensions-measured-extract.py').read_text(encoding='utf8')
dimension_script=dimension_script.replace("root/'scene/Fallingwater_working.blend'","root/'qa/masonry-detail-guest-geometry.blend'").replace('guest-dimensions-measured-projection.json','masonry-detail-guest-projection.json').replace('guest-dimensions-measured.json','masonry-detail-guest-dimensions.json').replace('saved iteration03','fresh guest05 with masonry finish')
exec(compile(dimension_script,'masonry-guest-dimension-regression','exec'),{})

# Run the author's door/stair/pool/firebox probes against this SAME live scene;
# omit its factory reset and rebuild, which would otherwise remove the finish.
geometry_script=(ROOT/'qa/guest-iteration05-check.py').read_text(encoding='utf8')
geometry_script=geometry_script[geometry_script.index("data=json.loads((root/'data/guest_house.json')"):]
geometry_script=geometry_script.replace('guest-iteration05-geometry.json','masonry-detail-guest-regression.json')
namespace={'bpy':bpy,'sys':sys,'json':json,'math':__import__('math'),'hashlib':hashlib,'Vector':Vector,'root':ROOT,'ctx':ctx,'source':source}
exec(compile(geometry_script,'masonry-guest-cavity-and-door-regression','exec'),namespace)
report['regression_counts']=namespace['report']['counts']
assert report['regression_counts']['door_pass']==7 and report['regression_counts']['fireplace_pass']==4
report['status']='GEOMETRY_PASS_VISUAL_PENDING'
(ROOT/'qa/masonry-detail-guest-pilot.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')

# Guest-only daylight diagnostic. No furniture edits or invented fill lights.
asset_materials.apply(ROOT)
lighting.apply(s,'DAYLIGHT')
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=32
s.cycles.use_denoising=True;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.025
s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA'
s.view_settings.view_transform='AgX';s.view_settings.exposure=2.8
camdata=bpy.data.cameras.new('FW_MASONRY_GUEST_DETAIL');cam=bpy.data.objects.new('FW_MASONRY_GUEST_DETAIL',camdata);collection('80_CAMERAS').objects.link(cam)
cam.location=(5.65,37.87,9.78);target=Vector((4.10,40.10,9.45));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camdata.lens=37;camdata.clip_start=.02;s.camera=cam
cam['purpose']='Guest-only material/geometry close-view, not an accepted room-tour camera'
s.render.filepath=str(ROOT/'qa/masonry-detail-guest.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'qa/masonry-detail-guest-pilot.blend'))
t=time.perf_counter();bpy.ops.render.render(write_still=True)
render={'file':s.render.filepath,'seconds':time.perf_counter()-t,'width':960,'height':540,'samples':32,'threads':4,'device':'CPU','exposure':s.view_settings.exposure,'scene_sha256':hashlib.sha256((ROOT/'qa/masonry-detail-guest-pilot.blend').read_bytes()).hexdigest(),'viewed':False}
(ROOT/'qa/masonry-detail-guest-render.json').write_text(json.dumps(render,indent=2))
print('MASONRY_GUEST_PILOT_COMPLETE',flush=True)
