"""Summarize bounded evidence and produce renderer settings after exact readback."""
from collections import Counter
from pathlib import Path
import hashlib
import json

qa = Path(__file__).resolve().parent
root = qa.parent
read = lambda name: json.loads((qa / name).read_text(encoding='utf-8'))
plan = read('forest-undergrowth13-plan.json')
build = read('forest-undergrowth13-build.json')
selected = {r['leaf_object'] for r in plan['selection']}
checks = [r for r in plan['physical_checks'] if r['leaf_object'] in selected]
assert len(checks) == 189 and all(not r['failures'] for r in checks)
counts = Counter(r['asset'] for r in plan['selection'])
metrics = {
    'selected_roots': len(checks), 'target_objects': len(build['changed_objects']),
    'asset_instance_counts': dict(counts),
    'root_gap_minmax_m': [min(r['root_anchor_gap_m'] for r in checks), max(r['root_anchor_gap_m'] for r in checks)],
    'leaf_terrain_gap_min_m': min(r['leaf_terrain_gap_min_m'] for r in checks),
    'branch_above_basal_gap_min_m': min(r['branch_above_basal_min_m'] for r in checks),
    'basal_branch_gap_minmax_m': [min(r['branch_basal_gap_minmax_m'][0] for r in checks), max(r['branch_basal_gap_minmax_m'][1] for r in checks)],
    'leaf_petiole_contact_upper_bound_max_m': max(r['leaf_petiole_contact_upper_bound_m'] for r in checks),
    'path_boundary_minus_crown_radius_min_m': min(r['nearest_path_boundary'][1] - r['crown_radius_m'] for r in checks),
    'actual_leaf_terrain_triangle_hits': sum(r['terrain_intersections']['leaf'] for r in checks),
    'actual_nonbasal_branch_terrain_triangle_hits': sum(r['terrain_intersections']['branch_nonbasal'] for r in checks),
    'leaf_count_before': len(checks) * 91,
    'leaf_count_after': counts[2] * 236 + counts[3] * 286,
    'instance_triangles_after': build['instance_triangles_after'],
    'net_instance_triangles_added': build['net_instance_triangles_added'],
    'saved_camera_count': len(build['saved_camera_clearance']),
    'saved_camera_minimum_clearance': min(build['saved_camera_clearance'], key=lambda r: r['nearest_new_mesh_m']),
    'movie_position_count': sum(r['samples'] for r in build['movie_positions']),
    'movie_minimum_clearance_m': min(r['minimum_clearance_m'] for r in build['movie_positions']),
    'route_ray_count': build['current_route_regression']['ray_count'],
    'route_new_obstacles': build['current_route_regression']['new_obstacles'],
    'route_candidate_hits': build['current_route_regression']['candidate_target_hits'],
    'physics_protected_count': len(build['protected_physics']),
    'non_target_objects_unchanged': build['non_target_objects_unchanged'],
}
print(json.dumps(metrics, indent=2))
settings = {
    'CAM_HERO': {'exposure': 0.8},
    'CAM_MAIN_OVERVIEW': plan['overview_external_comparison_settings'],
    'CAM_MAIN_L1_LOGGIA_B': {'exposure': 0.8},
}
(qa / 'forest-undergrowth13-camera-settings.json').write_text(json.dumps(settings, indent=2), encoding='utf-8')
readback_path = qa / 'forest-undergrowth13-readback.json'
if not readback_path.exists():
    print('READBACK_PENDING; final audit not written')
else:
    readback = read('forest-undergrowth13-readback.json')
    assert readback['status'] == 'PASS_FRESH_PROCESS_EXACT_REOPEN'
    out = {
        'status': 'PASS_BOUNDED_PHYSICAL_CANDIDATE_VISUAL_NOT_RUN',
        'source': build['source'], 'source_sha256': build['source_sha256'],
        'candidate': build['candidate'], 'candidate_sha256': build['candidate_sha256'],
        'helper': 'scripts/forest_undergrowth13.py', 'helper_sha256': build['helper_sha256'],
        'plan': 'qa/forest-undergrowth13-plan.json', 'plan_sha256': build['plan_sha256'],
        'metrics': metrics, 'fresh_process_readback': readback,
        'viewed_source_images': plan['source_images'],
        'zone_counts': plan['selected_zone_counts'], 'rejected_roots': plan['rejected_root_count'],
        'soft_edge_retained_old': len(plan['soft_edge_kept_old']),
        'accepted16_unchanged': True, 'root_matrix_and_labels_unchanged': True,
        'native_meshes_reused': 4, 'new_meshes': 0, 'new_materials': 0, 'new_objects': 0,
        'terrain_material_unchanged': build['source_terrain_material'],
        'source_scene_unchanged': readback['source_unchanged'],
        'scene_frame': 48, 'rendered': False, 'visual_status': 'NOT_RUN',
        'production_status': 'NOT_INTEGRATED',
        'limits': [
            'C authored root locations, photographic zone interpretation and shrub morphology; exact species/cultivar U.',
            '717 coarse camera protection rays are not a pixel-exact visibility proof; root must inspect all three images.',
            'Route helper scope text retains a legacy frozen08 label; actual inputs are frozen11 route and current d66 movie FCurves.',
            'Existing terrain, sky, water, architecture, tree trunks and accepted canopy are unchanged; whole-environment acceptance remains open.',
        ],
    }
    assert hashlib.sha256(Path(build['candidate']).read_bytes()).hexdigest() == build['candidate_sha256']
    (qa / 'forest-undergrowth13-final-audit.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
    print('FINAL_AUDIT_WRITTEN')
