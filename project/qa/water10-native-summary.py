"""Summarize unfiltered native rows; no Blender operations or cache writes."""
import json,csv
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent
rows=[json.loads(p.read_text(encoding='utf8')) for p in sorted(P.glob('water10-native-frame[0-9][0-9][0-9][0-9].json'))]
assert [r['frame'] for r in rows]==list(range(1,49))
audit=json.loads((P/'water10-native-audit.json').read_text(encoding='utf8'));targets=json.loads((P/'water10-native-head-targets.json').read_text(encoding='utf8'))
heads=np.array([np.load(P/r['heads_npz'])['head_columns'] for r in rows]);initial=np.load(P/rows[0]['heads_npz'])['initial_geometry_head_columns'];groups=np.array(targets['groups'])
V=np.array([r['mesh_volume_m3'] for r in rows]);tt=np.array([r['scene_time_from_frame1_s'] for r in rows]);timeint=lambda q:float(np.trapezoid(q,x=tt))
q=np.array([r['source_planes']['-5.64']['full_plane_down_positive']['net_out_m3_s'] for r in rows]);source_velocity=np.array([r['source_cell_median_velocity_world_m_s'] for r in rows]);target_velocity=np.array(rows[0]['source_C_design_velocity_world_m_s'])
out={'status':'NATIVE48_RAW_DIAGNOSTIC_COMPLETE_INITIALIZATION_AND_HEAD_NOT_STABLE_NO_JOIN_PASS',
     'frames':48,'source_plane_native_Q_median_f5_48_m3_s':float(np.median(q[4:])),
     'source_plane_native_Q_f5_48_p05_p95_m3_s':np.quantile(q[4:],[.05,.95]).tolist(),
     'source_Q_relative_author_design_error':float(np.median(q[4:])/audit['summary']['source_C_Q_design_m3_s']-1),
     'source_velocity_actual_median_f5_48_m_s':np.median(source_velocity[4:],axis=0).tolist(),
     'source_velocity_vs_encoded_vector_relative_error_median':float(np.median(np.linalg.norm(source_velocity[4:]-target_velocity,axis=1)/np.linalg.norm(target_velocity))),
     'source_native_to_previous_upstream_C_capacity_ratio':float(np.median(q[4:])/.3245931),
     'source_required_upstream_mean_velocity_if_area_01797263_m2':float(np.median(q[4:])/.17972631549835205),
     'source_plane_sensitivity':{},'boundaries':{},'heads':{},
     'frame1_mesh_volume_m3':float(V[0]),'frame48_mesh_volume_m3':float(V[-1]),'volume_change_m3':float(V[-1]-V[0]),'volume_relative_change_f1_f48':float(V[-1]/V[0]-1),
     'frame1_initial_geometry_relative_volume_error':float(V[0]/audit['summary']['initial_authored_volume_m3']-1),
     'all48_meshes_closed_manifold':audit['summary']['all_observed_meshes_closed'],'mass_balance_sensitivities':audit['summary']['mass_balance_sensitivities'],
     'normal_threshold_not_relaxed':.3,'upstream_join':'NOT_ASSEMBLED','native_visual':'NOT_RENDERED',
     'old_water09_flow_FAIL':'RETAINED_NOT_RECLASSIFIED','no_detrend_no_lowpass':True}
for z in ['-5.62','-5.64','-5.68']:
    qq=np.array([r['source_planes'][z]['full_plane_down_positive']['net_out_m3_s'] for r in rows]);area=np.array([r['source_planes'][z]['full_plane_down_positive']['wet_area_m2'] for r in rows]);outside=np.array([r['source_planes'][z]['outside_jet_window_net_down_m3_s'] for r in rows])
    jet=np.array([r['source_planes'][z]['jet_X03_15_Yminus27_minus165']['net_out_m3_s'] for r in rows])
    out['source_plane_sensitivity'][z]={'Q_median_f5_48_m3_s':float(np.median(qq[4:])),'native_wet_area_median_f5_48_m2':float(np.median(area[4:])),
        'Q_integral_f1_f48_m3':timeint(qq),'outside_fixed_jet_window_Q_abs_max_m3_s':float(abs(outside).max()),
        'fixed_jet_window_Q_median_f5_48_m3_s':float(np.median(jet[4:])),
        'fixed_jet_window_Q_p05_p95_f5_48_m3_s':np.quantile(jet[4:],[.05,.95]).tolist(),
        'fixed_jet_window_Q_integral_m3':timeint(jet),
        'fixed_jet_window_is_not_particle_provenance':True}
for name in ['Xminus','Yminus','Xplus']:
    methods={}
    for method in ['inner_phi_constant','inner_phi_linear_extrapolated','inner_Fluid_flag_binary','post_delete_phi_blend_BIASED']:
        qq=np.array([r['outflow_removal_interfaces'][name]['methods'][method]['net_out_m3_s'] for r in rows]);methods[method]={'integral_m3':timeint(qq),'f1_f24_f48_Q_m3_s':[float(qq[i]) for i in [0,23,47]],'minmax_Q_m3_s':[float(qq.min()),float(qq.max())]}
    out['boundaries'][name]={'interface_coordinate_m':rows[0]['outflow_removal_interfaces'][name]['actual_removal_interface_world_m'],'MAC_index':rows[0]['outflow_removal_interfaces'][name]['MAC_index'],'methods':methods}
for group in sorted(set(groups)):
    mask=groups==group;info={}
    for label,col in [('first_ray_hit',0),('highest_upward',2),('upward_below_source_plane',3)]:
        a=heads[:,mask,col];common=np.isfinite(a[0])&np.isfinite(a[-1]);delta=a[-1,common]-a[0,common]
        info[label]={'points':int(mask.sum()),'valid_f1_f24_f48':[int(np.isfinite(a[i]).sum()) for i in [0,23,47]],
            'valid_count_all48_minmax':[int(np.isfinite(a).sum(axis=1).min()),int(np.isfinite(a).sum(axis=1).max())],
            'paired_f1_f48_count':int(common.sum()),'paired_change_median_m':float(np.median(delta)) if len(delta) else None,
            'paired_change_p05_p95_m':np.quantile(delta,[.05,.95]).tolist() if len(delta) else None,
            'max_abs_delta_from_f1_any_frame_m':float(np.nanmax(abs(a-a[0]))),
            'absolute_head_median_f1_f24_f48_m':[float(np.nanmedian(a[i])) if np.isfinite(a[i]).any() else None for i in [0,23,47]]}
    info['first_hit_minmax_normal_z_f1_f24_f48']=[[float(np.nanmin(heads[i,mask,1])),float(np.nanmax(heads[i,mask,1]))] for i in [0,23,47]]
    out['heads'][group]=info
P.joinpath('water10-native-summary.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
with P.joinpath('water10-native-timeseries.csv').open('w',newline='',encoding='utf-8-sig') as stream:
    fields=['frame','seconds_from_f1','mesh_volume_m3','retained_CV_below_source_m3','source_measured_down_Q_m3_s','Xminus_outflow_proxy_m3_s','Yminus_outflow_proxy_m3_s','Xplus_outflow_proxy_m3_s','HERO_below_plane_median_z','WATER_DETAIL_below_plane_median_z','author_patch_below_plane_median_z']
    writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
    for r in rows:
        writer.writerow(dict(zip(fields,[r['frame'],r['scene_time_from_frame1_s'],r['mesh_volume_m3'],r['mesh_volume_inside_removal_interfaces_below_source_m3'],r['source_planes']['-5.64']['full_plane_down_positive']['net_out_m3_s'],*[r['outflow_removal_interfaces'][n]['methods']['inner_phi_constant']['net_out_m3_s'] for n in ['Xminus','Yminus','Xplus']],*[r['groups'][n]['head_median_m'] for n in ['CAM_HERO','CAM_WATER_DETAIL','AUTHORED_INITIAL_STEEP_REGION']]])))
print(json.dumps(out,ensure_ascii=False,indent=2))
