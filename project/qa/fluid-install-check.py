"""Independent fresh-process test of fluid_water.install's cached domain."""
import bpy
import json
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'scripts'))
import fluid_water
run=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'run02'
if bpy.data.filepath:
    raise RuntimeError('This check requires --factory-startup')
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj,do_unlink=True)
loaded=fluid_water.install(bpy.context.scene,root/f'scene/Fallingwater_fluid_{run}.blend')
domain=next(o for o in loaded.objects if o.name.startswith('WATER_Mantaflow'))
report={'scope':'fresh-process append of only fluid collection, using existing original cache location; not relocated final-package portability',
        'domain':domain.name,'frames':[]}
last=domain.modifiers.get('Mantaflow local Bear Run cascade').domain_settings.cache_frame_end
for frame in (1,last//2,last):
    bpy.context.scene.frame_set(frame)
    ev=domain.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=ev.to_mesh()
    report['frames'].append({'frame':frame,'vertices':len(mesh.vertices),'polygons':len(mesh.polygons),
                             'particle_counts':[{ 'type':p.settings.type,'count':len(p.particles)} for p in ev.particle_systems]})
    ev.to_mesh_clear()
    assert report['frames'][-1]['vertices']>8,'Cached liquid was not loaded'
report['status']='PASS_CACHED_COLLECTION_APPEND'
(root/f'qa/fluid-install-{run}.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report),flush=True)
