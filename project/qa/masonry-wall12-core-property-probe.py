import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'scripts'),str(R/'qa')]
import masonry_wall12 as h
import shrub08_auditlib as a
bpy.ops.wm.open_mainfile(filepath=str(R/'scene/Fallingwater_navigation_candidate10a.blend'))
o=bpy.context.scene.objects[h.TARGETS[1]]
def snap():return json.loads(json.dumps({'props':a.props(o),'slots':[(s.link,s.material.name if s.material else None) for s in o.material_slots],
                                      'mods':[(m.name,m.type,a.props(m)) for m in o.modifiers]}))
before=snap();h.cut_study_window(bpy.context.scene);after=snap()
out={k:{n:[v,after[k].get(n)] for n,v in before[k].items() if after[k].get(n)!=v} if isinstance(before[k],dict) else [before[k],after[k]] for k in before if before[k]!=after[k]}
(R/'qa/masonry-wall12-core-property-probe.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out,indent=2))
