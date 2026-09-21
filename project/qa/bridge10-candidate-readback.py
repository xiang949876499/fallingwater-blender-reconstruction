"""Fresh-process candidate reopen, fingerprint and bridge mesh quality."""
import bpy,sys,json,hashlib,time
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'qa'));sys.path.insert(0,str(ROOT/'scripts'))
import shrub08_auditlib as audit
import bridge_detail10 as detail
Q=ROOT/'qa';SOURCE=ROOT/'scene/Fallingwater_bridge_candidate10_meshclean.blend'
check=json.loads((Q/'bridge10-candidate-check.json').read_text())
sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest();assert sha==check['candidate_sha256']
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene
frame=scene.frame_current
expected=json.loads((Q/'bridge10-candidate-fingerprint.json').read_text())
before=audit.snapshot()
assert {n:audit.digest(v) for n,v in before['objects'].items()}==expected['objects']
assert audit.digest(before['global'])==expected['global']
assert before['meshes']==expected['meshes']
scene.frame_set(48);bpy.context.view_layer.update()
assert {n:audit.physical_hash(scene.objects[n]) for n in check['protected_physics']}==check['protected_physics']
assert {n:audit.physical_hash(scene.objects[n]) for n in detail.NEW_NAMES}==check['new_physical_hashes']
quality=[]
deps=bpy.context.evaluated_depsgraph_get()
for name in detail.NEW_NAMES:
    obj=scene.objects[name];ev=obj.evaluated_get(deps);mesh=ev.to_mesh();mesh.calc_loop_triangles()
    counts=Counter(tuple(sorted((a,b))) for p in mesh.polygons for a,b in zip(list(p.vertices),list(p.vertices)[1:]+list(p.vertices)[:1]))
    tiny=[i for i,p in enumerate(mesh.polygons) if p.area<1e-10]
    tiny_tri=sum((mesh.vertices[t.vertices[1]].co-mesh.vertices[t.vertices[0]].co).cross(
        mesh.vertices[t.vertices[2]].co-mesh.vertices[t.vertices[0]].co).length<2e-10 for t in mesh.loop_triangles)
    normals=Counter(tuple(round(float(v),3) for v in p.normal) for p in mesh.polygons)
    quality.append({'name':name,'vertices':len(mesh.vertices),'polygons':len(mesh.polygons),'triangles':len(mesh.loop_triangles),
                    'open_or_nonmanifold_edges':sum(c!=2 for c in counts.values()),'zero_area_polygons':len(tiny),'zero_area_triangles':tiny_tri,
                    'top_normal_frequencies':normals.most_common(8),'bounds_xyz_pairs':audit.bounds(obj),
                    'material_slots':[m.name if m else None for m in mesh.materials],
                    'finite_vertices':all(all(abs(v)<1e8 for v in p.co) for p in mesh.vertices)})
    ev.to_mesh_clear()
report={'status':'PASS_FRESH_REOPEN_FINGERPRINTS','candidate_sha256':sha,'frame_saved':frame,'physical_frame':48,
        'object_count':len(before['objects']),'full_snapshot_matches':True,'protected_physics_count':len(check['protected_physics']),
        'new_mesh_quality':quality,'rendered':False,'saved_again':False,
        'physical_candidate_issues':check.get('issues'),'visual_acceptance':'NOT_RUN'}
if any(r['open_or_nonmanifold_edges'] or r['zero_area_polygons'] or r['zero_area_triangles'] or not r['finite_vertices'] for r in quality):
    report['mesh_quality_status']='ISSUES_REVIEW_REQUIRED'
else:report['mesh_quality_status']='PASS_CLOSED_FINITE_NONDEGENERATE'
(Q/'bridge10-candidate-readback.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('BRIDGE10_READBACK',json.dumps(report),flush=True)
