import bpy,bmesh,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scene/Fallingwater_bridge10_endfix.blend'));bpy.context.scene.frame_set(1)
o=bpy.data.objects['WATER_BearRun_Continuous_Upstream_Downstream'];ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();bm=bmesh.new();bm.from_mesh(m)
bad=[v for v in bm.verts if not v.is_manifold];r={'vertices':len(bm.verts),'bad_vertices':len(bad),'isolated_vertices':sum(not v.link_faces for v in bad),'bad_used_vertices':sum(bool(v.link_faces) for v in bad),'bad_edges':sum(not e.is_manifold for e in bm.edges),'bad_used_positions':[(tuple(v.co),len(v.link_faces),len(v.link_edges)) for v in bad if v.link_faces][:40]}
print(json.dumps(r),flush=True);(R/'qa/bridge10-watertrim-input-topology.json').write_text(json.dumps(r,indent=2),encoding='utf8')
