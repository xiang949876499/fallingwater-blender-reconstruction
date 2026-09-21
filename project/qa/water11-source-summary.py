"""Summarize completed read-only source audits; no Blender/cache writes."""
import json
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent
result={'status':'PAIRED_SOURCE_RAW_AUDIT_COMPLETE_COARSE_REPRODUCED_FINE_IMPROVED_BUT_FLOW_SCREEN_FAIL',
 'arms':{},'frames_per_arm':12,'source_scene_or_cache_changed':False,'renders':0,'additional_bakes':0,
 'old_water09_FAIL_retained':True,'natural_pool_boundary_and_initialization_test':'NOT_RUN',
 'waterfall_join_visual_and_10second_status':'NOT_PASSED'}
for arm in ['S24','S48']:
 a=json.loads((P/f'water11-source-{arm}-audit.json').read_text(encoding='utf8'));b=json.loads((P/f'water11-source-{arm}-bake.json').read_text(encoding='utf8'))
 rows=a['frames'];assert len(rows)==12 and rows[0]['frame']==1
 v=np.array([r['source_interior_median_velocity_m_s'] for r in rows]);encoded=np.array([-1.5031434297561646,-1.0052733421325684,-6.694818496704102])
 out={'actual_grid':a['actual_grid'],'actual_cell_m':a['actual_cell_m'],'source_cells':rows[0]['source_interior_geometric_cells'],
  'expected_grid_match':a['expected_grid_match'],'expected_cell_match':a['expected_cell_match'],'lattice_origin_error_m':a['lattice_phase_expected_error_m'],
  'mesh_world_mapping_error_m':a['raw_mesh_world_mapping']['max_error_m'],'time_units':a['actual_time_units'],
  'supervisor_seconds':a['supervisor']['elapsed_seconds'],'solve_seconds':b['bake_seconds'],'cache_bytes':b['cache_bytes'],
  'cache_files':b['cache_files'],'mesh_frames':b['mesh_frames'],'baked_scene_sha256':b['baked_scene_sha256'],
  'source_velocity_f1_m_s':v[0].tolist(),'source_velocity_median_f5_12_m_s':np.median(v[4:],axis=0).tolist(),
  'source_velocity_relative_error_median_f5_12':float(np.median(np.linalg.norm(v[4:]-encoded,axis=1)/np.linalg.norm(encoded))),
  'source_vertical_change_f1_m_s':float(v[0,2]-encoded[2]),'gravity_over_one24fps_step_m_s':-9.81/24,
  'author_geometry_volume_m3':a['author_source_volume_m3'],'f1_mesh_volume_m3':rows[0]['mesh']['volume_m3'],
  'f1_phi_volume_proxy_m3':rows[0]['phi_volume_center_proxy_m3'],
  'f1_mesh_relative_author_volume_error':rows[0]['mesh']['volume_m3']/a['author_source_volume_m3']-1,
  'f1_phi_relative_author_volume_error':rows[0]['phi_volume_center_proxy_m3']/a['author_source_volume_m3']-1,
  'f1_is_not_true_t0':True,'all12_meshes_closed':all(r['mesh']['boundary_edges']==0 and r['mesh']['nonmanifold_edges']==0 for r in rows),
  'native_mesh_sections_bad_degree_total':sum(s['native_mesh_section']['bad_degree_vertices'] for r in rows for s in r['planes'].values()),
  'native_cache_hashes_unchanged':a['native_cache_hashes_unchanged'],'old_cache_hash_changes':a['old_cache_hash_changes'],
  'planes':{},'summary':a['summary']}
 for z in ['-5.35','-5.58','-5.64','-5.68']:
  pp=[r['planes'][z] for r in rows];q=np.array([p['fixed_jet_window']['Q_net_down_m3_s'] for p in pp]);ar=np.array([p['fixed_jet_window']['phi_wet_area_m2'] for p in pp]);ma=np.array([p['native_mesh_section']['area_m2'] for p in pp],float)
  out['planes'][z]={'source_stationary_geometry_area_m2':pp[0]['author_stationary_source_horizontal_area_m2'],
   'f1_phi_area_m2':float(ar[0]),'f1_native_mesh_area_m2':float(ma[0]),'f1_mesh_section_status':pp[0]['native_mesh_section']['status'],
   'f1_Q_m3_s':float(q[0]),'f5_12_Q_median_m3_s':float(np.median(q[4:])),
   'f5_12_Q_minmax_m3_s':[float(q[4:].min()),float(q[4:].max())],
   'f5_12_phi_area_median_m2':float(np.median(ar[4:])),'f5_12_native_mesh_area_median_m2':float(np.nanmedian(ma[4:])),
   'f5_12_wet_mean_down_velocity_median_m_s':float(np.median([p['fixed_jet_window']['wet_area_mean_down_velocity_m_s'] for p in pp[4:]])),
   'Q_all12_m3_s':q.tolist(),'phi_area_all12_m2':ar.tolist(),'native_mesh_area_all12_m2':ma.tolist()}
 medians=[out['planes'][z]['f5_12_Q_median_m3_s'] for z in ['-5.58','-5.64','-5.68']]
 out['downstream_plane_relative_spread']=(max(medians)-min(medians))/np.mean(medians)
 result['arms'][arm]=out
coarse=result['arms']['S24']['summary']['Q_f5plus_median_m3_s'];fine=result['arms']['S48']['summary']['Q_f5plus_median_m3_s'];q=.2994137004643072
result['comparison']={'water10_fixed_window_median_Q_m3_s':.621348976408266,'coarse_to_water10_ratio':coarse/.621348976408266,
 'coarse_Q_over_design':coarse/q,'fine_Q_over_design':fine/q,'fine_Q_vs_coarse_relative_change':fine/coarse-1,
 'reduction_of_absolute_design_error_fraction':1-abs(fine-q)/abs(coarse-q),
 'coarse_reproduction_prespecified20percent_gate':abs(coarse/.621348976408266-1)<=.2,
 'fine_prespecified10percent_Q_gate':abs(fine/q-1)<=.1,
 'source_native_Q_is_phi_MAC_flux_not_proved_particle_mass':True,
 'inference':'Pool and its false X+ outlet are not necessary for near-twofold coarse phi/MAC flux. Finer grid reduces but does not remove bias; spatial refinement also changes adaptive substeps.'}
result['next_minimal_change_proposal_only']={'base':'S48 frozen geometry/velocity/grid/secondary/12frames',
 'one_RNA_change':{'particle_radius':[1.0,.75]},'mesh_particle_radius_unchanged':1.25,
 'reason':'Native simulation phi/Q is inflated, not merely a mesh silhouette. Official script passes primary radius to unionParticleLevelset and adjustNumber, separate from meshing radius.',
 'not_isolated_mechanism':'The single RNA affects particle-to-levelset reconstruction and resampling; result would not isolate those internals.',
 'frames':12,'threads':4,'proposed_hard_limit_s':90,'solve_cost_estimate_s':[3,12],'monitored_total_estimate_s':[25,45],
 'authorization':'NOT_AUTHORIZED_NOT_PREPARED_NOT_BAKED','no_geometry_or_Q_renormalization':True,
 'same_Q_screen_relative_error_max':.10,'failure_action':'Preserve unchanged threshold and stop; no automatic radius sweep or natural-pool migration'}
result['primary_sources']=['https://raw.githubusercontent.com/blender/blender/blender-v5.2-release/intern/mantaflow/intern/strings/liquid_script.h','https://raw.githubusercontent.com/blender/blender/blender-v5.2-release/extern/mantaflow/preprocessed/plugin/flip.cpp']
(P/'water11-source-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k!='arms'},ensure_ascii=False,indent=2))
for arm,out in result['arms'].items():print(arm,json.dumps({k:v for k,v in out.items() if k not in ['planes']},ensure_ascii=False,indent=2));print('planes',json.dumps(out['planes'],indent=2))
