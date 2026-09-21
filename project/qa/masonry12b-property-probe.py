import bpy,json,sys
from pathlib import Path
from types import SimpleNamespace
R=Path(__file__).resolve().parents[1];Q=R/'qa';sys.path[:0]=[str(R/'scripts'),str(Q)]
import masonry_tower12b as entry
import shrub08_auditlib as audit
bpy.ops.wm.open_mainfile(filepath=str(R/'scene/Fallingwater_masonry_tower_candidate12a.blend'))
bpy.context.scene.frame_set(48)
before={n:audit.props(bpy.context.scene.objects[n]) for n in entry.MODIFIED}
entry.build(SimpleNamespace(root=R))
diff={n:{k:[v,audit.props(bpy.context.scene.objects[n])[k]] for k,v in before[n].items() if v!=audit.props(bpy.context.scene.objects[n])[k]} for n in entry.MODIFIED}
(Q/'masonry12b-property-probe.json').write_text(json.dumps(diff,indent=2),encoding='utf-8');print(json.dumps(diff,indent=2))
