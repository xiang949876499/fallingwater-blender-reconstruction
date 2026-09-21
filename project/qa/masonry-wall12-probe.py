"""Read-only actual frozen two-wall inspection; no save or render."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'qa'))
import shrub08_auditlib as audit
SOURCE=R/'scene/Fallingwater_navigation_candidate10a.blend'
SHA='1e7b17d9c2396513f005724e50788bf834097eedb401b91a7f1030825e2c4ed9'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SOURCE)==SHA
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene
def rec(o):
    vs=[o.matrix_world@v.co for v in o.data.vertices]
    return {'name':o.name,'bounds':audit.bounds(o),'vertices':len(vs),'polygons':len(o.data.polygons),
            'coordinates':[list(v) for v in vs],'materials':[m.name if m else None for m in o.data.materials],
            'modifiers':[m.type for m in o.modifiers],'hash':audit.physical_hash(o),'custom':dict(o.items())}
prefixes=('MAIN_L2_dressing','MAIN_L3_study_core','MAIN_L3_study_west')
rows=[rec(o) for o in s.objects if o.type=='MESH' and o.name.startswith(prefixes)]
targets=['MAIN_L2_dressing_shell_north_0','MAIN_L3_study_core_0']
bvh,owners=audit.world_bvh([s.objects[n] for n in targets],True)
rays=[]
for z in (5.9,6.5,7.2):
    p=Vector((-5.,(540-267)*.0531,z));hit,normal,index,distance=bvh.ray_cast(p,Vector((1,0,0)),3)
    rays.append({'point':list(p),'direction':[1,0,0],'hit':owners[index] if index is not None else None,'location':list(hit) if hit else None})
report={'source':str(SOURCE),'sha256':SHA,'frame':s.frame_current,'objects':rows,'study_window_centerline_core_probes':rays,
        'cameras':{n:{'eye':list(s.objects[n].matrix_world.translation),'matrix':[list(v) for v in s.objects[n].matrix_world],'lens':s.objects[n].data.lens} for n in ('CAM_HERO','CAM_MAIN_L2_TERRACE_W_A')},
        'source_unchanged':sha(SOURCE)==SHA,'saved':False,'rendered':False}
(R/'qa/masonry-wall12-probe.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps({'targets':[{k:v for k,v in r.items() if k not in ('coordinates','custom')} for r in rows if r['name']in targets],'study_window_probes':rays,'source_unchanged':report['source_unchanged']},indent=2))
