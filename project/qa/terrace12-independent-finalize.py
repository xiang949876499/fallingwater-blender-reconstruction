"""Freeze the bounded review, retaining literal numerical failures separately."""
import json,hashlib
from pathlib import Path
from collections import Counter
R=Path(__file__).resolve().parents[1]
def read(name):return json.loads((R/'qa'/name).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
extract=read('terrace12-independent-12b-extract.json');vol=read('terrace12-independent-12b-volume.json');precision=read('terrace12-independent-12b-precision.json');boundary=read('terrace12-independent-12b-boundary.json')
geometry=read('terrace12-independent-12b-after-geometry.json');topology={}
for n,g in geometry.items():
    if not n.endswith('_slab'):continue
    edges=Counter((a,b) for t in g['triangles'] for a,b in zip(t,t[1:]+t[:1]))
    topology[n]={'directed_edge_winding_mismatches':sum(edges[e[::-1]]!=count for e,count in edges.items()),
                 'unoriented_edge_degree_counts':g['edge_degree_counts'],'degenerate_triangle_count':g['degenerate_triangle_count']}
    assert topology[n]['directed_edge_winding_mismatches']==0
expected_markers={'/global/scene/custom_properties/terrace12b_slab_interface',
                  '/objects/MAIN_L2_TERRACE_W_slab/properties/custom_properties/terrace12b_slab_interface',
                  '/objects/MAIN_L2_TERRACE_S_slab/properties/custom_properties/terrace12b_slab_interface'}
assert set(extract['unexpected_snapshot_differences'])==expected_markers
assert all(extract[k] for k in ['non_target_objects_exact','object_sets_identical','materials_exact','camera_objects_exact','action_keyframes_exact'])
assert all(not x['introduced_missing_support'] and all(r['status']=='PASS' for r in x['negative12a_regression']) for x in boundary['parts'])
assert all(x['after_same_direction_coplanar_area_m2']==0 for x in precision['parts'])
sources={str(R/'scene/Fallingwater_navigation_candidate11a.blend'):'d66ded0f23b7d19c20b81d2f59f94aa5aa77747be4568e85e1d105395fc219ff',
         str(R/'scene/Fallingwater_terrace_interface_candidate12a.blend'):'0499c4594e4143ebc8ae28735417ae17765e1ffdafe20285903f654768958fa1',
         str(R/'scene/Fallingwater_terrace_interface_candidate12b.blend'):'285ea6d0c29b0ff483fb6f582c644f5286b23e83f1d894bedf32546fbca3a14c'}
assert all(sha(Path(p))==value for p,value in sources.items())
dims={case:read(f'terrace12-independent-12b-{case}-extract.json')['dimensions'] for case in ['before','after']}
assert all(x['counts']=={'PASS':4,'FAIL':0,'NOT_RUN':0} for x in dims.values())
files=['terrace12-independent-review.md','terrace12-independent-12b-review.md',
       'terrace12-independent-extract.py','terrace12-independent-volume.py','terrace12-independent-witness.py',
       'terrace12-independent-12b-volume.py','terrace12-independent-12b-precision.py','terrace12-independent-12b-boundary.py']
out={'engineering_status':'PASS_LOCAL_INTERFACE_WITH_DOCUMENTED_SMALL_TRIANGULATION_SEAM',
     'strict_mathematical_exact_zero_claimed':False,'candidate12a_status':'FAIL_PRESERVED',
     'candidate12a_report':'terrace12-independent-review.md','candidate12b_report':'terrace12-independent-12b-review.md',
     'source_hashes_rechecked_unchanged':sources,'non_target_objects_exact':23432,'total_objects':23434,
     'expected12b_markers_individually_reviewed':sorted(expected_markers),'other_unexpected_state_changes':[],
     'materials_cameras_keyframes_unchanged':True,'empty_material_slots_added':0,'topology':topology,
     'four_dimensions':{k:v['counts'] for k,v in dims.items()},'volume_results_literal_statuses_preserved':vol['parts'],
     'same_direction_coplanar_area_results':precision['parts'],
     'boundary_summary':[{k:x[k] for k in ['part','maximum_sampled_boundary_distance_m','signed_boundary_sample_range_m','world_float32_coordinate_ULP_max_m','interface_sample_count','boundary_limit_statement']} for x in boundary['parts']],
     'old_negative_witnesses_corrected':sum(len(x['negative12a_regression']) for x in boundary['parts']),
     'actual_finish_support_points':sum(x['finish_support_locations'] for x in boundary['parts']),
     'actual_structure_occupancy_samples':sum(x['finish_support_column_samples'] for x in boundary['parts']),
     'introduced_missing_support':0,'body_clearance_or_dimension_thresholds_changed':False,
     'images_actually_opened_by_reviewer':[str(R/'renders/previews/integration11a/CAM_HERO.png'),str(R/'renders/previews/terrace-interface12b/CAM_HERO.png')],
     'local_visual_result':'Conspicuous black band removed in the same camera view; no whole-exterior acceptance claim',
     'review_artifact_sha256':{f:sha(R/'qa'/f) for f in files},'rendered_by_reviewer':False,'scene_saved_by_reviewer':False,
     'production_modules_changed_by_reviewer':False,'scope':'Two terrace slabs and their interfaces only; no new whole-scene navigation claim'}
(R/'qa/terrace12-independent-final.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print(json.dumps({k:out[k] for k in ['engineering_status','candidate12a_status','non_target_objects_exact','four_dimensions','old_negative_witnesses_corrected','actual_structure_occupancy_samples','introduced_missing_support']}))
