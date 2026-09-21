"""Reopen the saved candidate and verify that shading flags/normals persisted."""
import bpy,json,hashlib
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'scene/Fallingwater_geology_candidate07c.blend'
source_sha=hashlib.sha256(path.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(path))
records=[]
for name in ('SITE_Core_Continuous_Fractured_Sandstone','SITE_Cascade_Shoulder_Continuous_0','SITE_Cascade_Shoulder_Continuous_1'):
    ob=bpy.data.objects[name];ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
    records.append({'object':name,'smooth_faces':sum(p.use_smooth for p in m.polygons),
                    'flat_faces':sum(not p.use_smooth for p in m.polygons),
                    'sharp_edges':sum(e.use_edge_sharp for e in m.edges),
                    'material_index_counts':dict(Counter(p.material_index for p in m.polygons)),
                    'normal_max_length_error':max(abs(n.vector.length-1) for n in m.corner_normals),
                    'normal_max_deviation_from_face':max((m.corner_normals[j].vector-p.normal).length for p in m.polygons for j in p.loop_indices)})
    ev.to_mesh_clear()
assert all(r['sharp_edges']>0 and r['smooth_faces']>0 and r['flat_faces']>0 for r in records)
assert all(r['normal_max_length_error']<.0001 for r in records)
report={'status':'PASS_SAVED_SHADING_FLAGS_AND_NORMALS','candidate_sha256':source_sha,'objects':records,'render_performed':False}
(ROOT/'qa/core-geology07c-saved-normals.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
assert hashlib.sha256(path.read_bytes()).hexdigest()==source_sha
print(json.dumps(report,indent=2),flush=True)
