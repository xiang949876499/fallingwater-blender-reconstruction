"""Measure cached water coverage at fixed world coordinates, without rendering."""
import sys,json,time,hashlib
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import water_integration as wi
run=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'run05'
source=ROOT/'scene/Fallingwater_iteration04.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='247d20f7863e4f7e9c18587d4c032bd663857a420bcfb828d271195665841ac2'
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scene'/f'Fallingwater_fluid_{run}.blend'))
scene=bpy.context.scene
domain=scene.objects['WATER_Mantaflow_Local_Cascade']
with bpy.data.libraries.load(str(source),link=False) as (src,dst):dst.objects=[wi.SURFACE]
surface=dst.objects[0];scene.collection.objects.link(surface)
wi.repair_surface_normals(scene)
rocks=[wi._bvh(o) for o in scene.objects if o.get('fluid_collision')]
lip=Vector((2.4,-2.83,0));down=Vector((-.882352948,-.470588356,0));across=Vector((.470588356,-.882352948,0))
ss=[-4+i*.25 for i in range(45)];cc=[-4.5+i*.25 for i in range(37)]
points=[lip+down*s+across*c for s in ss for c in cc]
def hit(tree,p):
    q=tree.ray_cast(Vector((p.x,p.y,0)),Vector((0,0,-1)),10)
    return [round(q[0].z,5),round(q[1].z,4)] if q[0] is not None else None
rockz=[]
for p in points:
    values=[h[0] for tree in rocks if (h:=hit(tree,p)) is not None]
    rockz.append(max(values) if values else None)
report={'run':run,'along':ss,'cross':cc,'points_order':'along-major, cross-minor','lip':list(lip),'down':list(down),'across':list(across),'rock_top':rockz,'frames':[]}
path=ROOT/'qa'/f'water-dynamic-sample-{run}.json'
started=time.perf_counter()
for frame in range(24,min(48,scene.frame_end)+1):
    scene.frame_set(frame);tree=wi._bvh(domain);river=wi._bvh(surface)
    waters=[hit(tree,p) for p in points];rivers=[hit(river,p) for p in points]
    report['frames'].append({'frame':frame,'water':waters,'river':rivers})
    path.write_text(json.dumps(report),encoding='utf-8')
    print('WATER_FRAME',frame,'hits',sum(h is not None for h in waters),'seconds',round(time.perf_counter()-started,2),flush=True)
report['seconds']=time.perf_counter()-started
path.write_text(json.dumps(report),encoding='utf-8')
