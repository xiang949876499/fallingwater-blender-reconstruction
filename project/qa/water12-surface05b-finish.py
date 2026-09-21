"""Separate zero-volume touching shoreline fans; preserve every triangle position."""
import sys,json,hashlib,time
from pathlib import Path
import bpy,bmesh,numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import water_surface12 as g
import hybrid_water as h
source=ROOT/'scene/Fallingwater_water12_surface05.blend';output=ROOT/'scene/Fallingwater_water12_surface05b.blend'
assert not output.exists();bpy.ops.wm.open_mainfile(filepath=str(source))
assert not any(m.type=='FLUID' for ob in bpy.data.objects for m in ob.modifiers)
o=bpy.data.objects['WATER12_Continuous_Upper_9Branches_Pool_OuterRiver']
def triangle_digest(mesh):
    v=np.array([tuple(q.co) for q in mesh.vertices],dtype=np.float32);f=np.array([tuple(p.vertices) for p in mesh.polygons]);return hashlib.sha256(v[f].tobytes()).hexdigest()
before_digest=triangle_digest(o.data);before=h.topology(o)
bm=bmesh.new();bm.from_mesh(o.data);bad=[e for e in bm.edges if not e.is_manifold]
locations=[{'edge':[list(e.verts[0].co),list(e.verts[1].co)],'linked_faces':len(e.link_faces)} for e in bad]
assert len(bad)==19 and all(len(e.link_faces)==4 for e in bad)
bmesh.ops.split_edges(bm,edges=bad)
assert not any(not e.is_manifold for e in bm.edges)
bm.to_mesh(o.data);bm.free();after_digest=triangle_digest(o.data);assert before_digest==after_digest
names=json.loads(o['water12_tag_names']);tags=[names[q.value] for q in o.data.attributes['water12_part'].data]
check=g.audit_mesh(o,tags);assert check['topology']['nonmanifold_edges']==0 and check['topology']['boundary_edges']==0
assert check['degenerate_triangles']==0 and check['confirmed_segment_triangle_crossings']==0
o['evidence']='C static render candidate. Shared interfaces, pure geometry only. Bottom caps are optical closure, not CFD bed boundaries.'
o['production_ready']=False
bpy.ops.wm.save_as_mainfile(filepath=str(output))
r={'status':'CLOSED_STATIC_RENDER_CANDIDATE_VISUAL_UNVERIFIED','source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
   'output':str(output),'output_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'before':before,'geometry_audit':check,
   'touching_edges_separated':locations,'vertices_duplicated':check['topology']['vertices']-before['vertices'],
   'all_triangle_positions_and_winding_exactly_unchanged':True,'triangle_coordinate_sha256':before_digest,
   'physical_contact_report':'qa/water12-surface05-final-audit.json','contact_reuse_reason':'Every triangle coordinate and winding is bitwise unchanged; all centroid tests and geometric vertex positions are preserved.',
   'old_failure_reports_retained':['qa/water12-surface01.json','qa/water12-surface02.json','qa/water12-surface03.json','qa/water12-surface04.json','qa/water12-surface05.json'],
   'no_water_head_change':True,'no_rock_change':True,'no_cache_access':True,'no_bake':True,'no_render':True,'production_install':False,
   'geometry_volume_not_physical_water_quantity':True,'lower_dimensional_contact_not_volume_overlap':True,
   'limitations':['A near shoreline may end up to one sample cell short because partially wet triangles were conservatively omitted.',
       'Optical bottom caps are C closures and are not exact fluid-bed interfaces; free-surface and shore contact are reported separately.',
       'The remote upstream extension interface and final motion remain unverified.']}
(ROOT/'qa/water12-surface05b.json').write_text(json.dumps(r,indent=2),encoding='utf8')
print('W12_05B_READY',r['output_sha256'],check['topology'],flush=True)
