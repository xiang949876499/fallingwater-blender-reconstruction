"""Fresh saved readback of scoped entry03 repair; preserve entry02 failures."""
import bpy,hashlib,json,struct,time,ast,math,array,collections
from pathlib import Path
R=Path(__file__).resolve().parents[1];Q=R/'qa';TERRAIN='SITE_Continuous_BearRun_Terrain'
OUT=Q/'checkpoint10-entry03-saved-compare.json';assert not OUT.exists()
repair=json.loads((Q/'checkpoint10-entry03-scoped-reinstall02.json').read_text(encoding='utf-8'))
assert repair['pass']
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(repair['output'])==repair['output_sha256']
tree=ast.parse((Q/'master-ceiling11-build-check.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'prop_state','materials'}],type_ignores=[]),'<read-only material utility>','exec'))
tree=ast.parse((Q/'checkpoint10-entry02-independent.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<exact saved object audit>','exec'))
a=json.loads((Q/'checkpoint10-entry02-independent-state-0.json').read_text(encoding='utf-8'))
b02=json.loads((Q/'checkpoint10-entry02-independent-state-1.json').read_text(encoding='utf-8'))
b,_=state(Path(repair['output']),'03');b=json.loads(json.dumps(b))
changed=sorted(n for n in a['objects'] if a['objects'][n]!=b['objects'].get(n))
changed02=sorted(n for n in b02['objects'] if b02['objects'][n]!=b['objects'].get(n))
cameras=sorted(n for n in a['cameras'] if a['cameras'][n]!=b['cameras'].get(n))
room_diffs={n:sorted(k for k in set(a['rooms'][n])|set(b['rooms'][n]) if a['rooms'][n].get(k)!=b['rooms'][n].get(k)) for n in a['rooms'] if a['rooms'][n]!=b['rooms'].get(n)}
terrain02=json.loads((Q/'terrain10-rebuild02-independent.json').read_text(encoding='utf-8'))
terrain_transitive=terrain02['pass'] and b['objects'][TERRAIN]==b02['objects'][TERRAIN] and b['terrain']==b02['terrain']
previous=json.loads((Q/'checkpoint10-entry02-independent-animation-probe.json').read_text(encoding='utf-8'))
refs={str(r['frame']):r['source'] for r in previous['differing_actual_evaluated_matrices']}
refs.update({str(f):v['source'] for f,v in previous['boundaries'].items()})
s=bpy.context.scene;initial=s.frame_current;rows=[]
for f,source in sorted(refs.items(),key=lambda p:int(p[0])):
    s.frame_set(int(f));m=s.objects['CAM_TOUR_SUPPLEMENTAL'].evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world
    actual=[list(r) for r in m]
    rows.append({'frame':int(f),'actual_matrix':actual,'source_matrix':source['matrix_world'],'exactly_equal':actual==source['matrix_world']})
s.frame_set(initial)
four=['CAM_MAIN_L2_BATH_M_A','CAM_MAIN_L2_BATH_M_B','CAM_MAIN_L2_MASTER_A','CAM_MAIN_L2_MASTER_B']
record={'status':'PENDING','candidate':repair['output'],'candidate_sha256':sha(repair['output']),'source_sha256':a['sha256'],'rebuilt02_sha256':b02['sha256'],
        'object_counts':[len(a['objects']),len(b['objects'])],'object_name_sets_exactly_equal':set(a['objects'])==set(b['objects']),
        'indexed_object_hash_changes_from_source':changed,'indexed_object_hash_changes_from02':changed02,
        'terrain_exact_reindex_transitive_proof':terrain_transitive,'terrain_proof_basis':'Source10 versus02 direct exact multiset proof retained; repaired terrain indexed geometry hash/matrix/topology/material state is exactly equal to02. No tolerance.',
        'all131_camera_state_and_animation_exact':not cameras,'camera_changes':cameras,'camera_key_counts':[a['camera_key_count'],b['camera_key_count']],
        'four_quaternion_cameras':{n:{'exact_equal':a['cameras'][n]==b['cameras'][n],'mode':b['cameras'][n]['rotation_mode']} for n in four},
        'all_object_aux_state_exactly_equal':a['object_aux']==b['object_aux'],'all_materials_exactly_equal':a['materials']==b['materials'],
        'room_metadata_diff_fields':room_diffs,'room_geometry_and_navigation_fields_exact':all(set(v)<= {'model_status','surface_identity_note'} for v in room_diffs.values()),
        'actual_affected_and_boundary_matrices':rows,'actual_frames_checked':len(rows),'matrix_difference_count':sum(not r['exactly_equal'] for r in rows),
        'candidate_unchanged':sha(repair['output'])==repair['output_sha256'],'rendered':False,'saved':False,'full_navigation_rerun':False,
        'limits':'Geometric and animation reproducibility only; source height/visual/GUI/movie acceptance is not established. Source and rebuilt room status annotations intentionally differ and are explicitly listed.'}
passed=record['object_name_sets_exactly_equal'] and set(changed)<={TERRAIN} and not changed02 and terrain_transitive and not cameras and record['all_object_aux_state_exactly_equal'] and record['all_materials_exactly_equal'] and record['room_geometry_and_navigation_fields_exact'] and record['matrix_difference_count']==0 and record['candidate_unchanged']
record['pass']=passed;record['status']='PASS_EXACT_GEOMETRY_CAMERAS_AND_ANIMATION' if passed else 'FAIL_EXACT_REPRODUCTION'
OUT.write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in record.items() if k not in ('actual_affected_and_boundary_matrices','room_metadata_diff_fields')},indent=2),flush=True)
assert passed
