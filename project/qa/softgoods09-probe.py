"""Read the one Alcove pillow and its bed support from frozen structure09."""
import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];p=R/'scene/Fallingwater_structure_candidate09.blend'
assert hashlib.sha256(p.read_bytes()).hexdigest()=='4fa1fc1f56795a2da88c97bacc9bd3b2a0730d3d085076173425b00addd744a0'
bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();records=[]
for ob in s.objects:
 if ob.type!='MESH' or 'MAIN_L3_ALCOVE' not in ob.name or not any(k in ob.name for k in ('pillow','woven_bedcover','mattress','walnut_platform')):continue
 e=ob.evaluated_get(dg);m=e.to_mesh();local=[list(v.co) for v in m.vertices];world=[list(e.matrix_world@v.co) for v in m.vertices]
 records.append({'name':ob.name,'parent':ob.parent.name if ob.parent else None,'matrix_world':[list(r) for r in ob.matrix_world],'matrix_local':[list(r) for r in ob.matrix_local],'local_evaluated_bounds':[[min(v[k] for v in local),max(v[k] for v in local)] for k in range(3)],'world_evaluated_bounds':[[min(v[k] for v in world),max(v[k] for v in world)] for k in range(3)],'materials':[m.name if m else None for m in ob.data.materials],'modifiers':[{'name':m.name,'type':m.type,'width':getattr(m,'width',None)} for m in ob.modifiers],'vertices':len(local),'polygons':len(m.polygons)})
 e.to_mesh_clear()
out={'source':str(p),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bed_parameters_source':'scripts/furnishings.py bed(): pillow .89x.46x.14 at z.576; bedcover top .5255; source pose preserved','records':records}
(R/'qa/softgoods09-probe.json').write_text(json.dumps(out,indent=2));print(json.dumps(records,indent=2))
