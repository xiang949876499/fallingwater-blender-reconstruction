"""Freeze final diagnostic metadata and a reproducible unexecuted render recipe."""
import bpy,json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import hybrid_motion as hm
import hybrid_water as h
report=json.loads(hm.REPORT.read_text(encoding='utf-8'));check_path=ROOT/'qa/water-hybrid07-motion-check.json';check=json.loads(check_path.read_text(encoding='utf-8'))
bpy.ops.wm.open_mainfile(filepath=str(hm.OUTPUT));scene=bpy.context.scene
scene['hybrid_water_status']='DIAGNOSTIC_FAIL_NORMALS_AND_RAW_POOL_HEAD_NOT_PRODUCTION'
scene['hybrid_water_report']='qa/water-hybrid07-motion-review.md'
scene['hybrid_water_no_long_cache_authorization']=True
water=scene.objects['WATER_Hybrid07a_Continuous_River_Branch_Pool']
water['animation_status']='37newkeys;36frames checked;1–11triangle normal reversals remain; closed joins stable but geometric/visual acceptance FAIL'
scene.frame_set(24);scene.camera=scene.objects['CAM_WATER_FOOT']
bpy.ops.wm.save_as_mainfile(filepath=str(hm.OUTPUT));sha=hashlib.sha256(hm.OUTPUT.read_bytes()).hexdigest()
check['pre_metadata_stamp_sha256']=check['sha256'];check['sha256']=sha;check['metadata_stamp_only']=True;h.write(check_path,check)
report['status']='DIAGNOSTIC_FAIL_NORMALS_AND_RAW_POOL_HEAD_NOT_PRODUCTION';report['output_sha256']=sha
report['physical_boundary_limitation']='qa/water-hybrid07-impact36-boundary.json';report['motion_visual_review']='NOT_RUN_ROOT_SCHEDULED'
h.write(hm.REPORT,report)
camera=scene.camera
recipe={'status':'NOT_RUN_DIAGNOSTIC_ONLY_ROOT_SCHEDULES','source_scene':str(hm.OUTPUT),'source_sha256':sha,
 'camera':'CAM_WATER_FOOT','camera_matrix_world':[list(row) for row in camera.matrix_world],
 'camera_lens_mm':camera.data.lens,'camera_sensor_width_mm':camera.data.sensor_width,
 'camera_clip_m':[camera.data.clip_start,camera.data.clip_end],
 'frame_start':1,'frame_end':36,'frame_step':1,'fps':24,'duration_seconds':1.5,
 'resolution':[480,270],'resolution_percentage':100,'engine':'CYCLES','device':'CPU','threads':8,
 'samples':12,'denoising':True,'use_persistent_data':True,'motion_blur':False,'exposure':.8,'view_transform':scene.view_settings.view_transform,
 'sequence_format':'PNG_RGBA_8bit','output_directory':'project/renders/previews/hybrid07-motion36-foot',
 'optional_static_views':[{'camera':'CAM_WATER_FOOT','frame':24,'resolution':[960,540],'samples':32},
                          {'camera':'CAM_HERO','frame':24,'resolution':[960,540],'samples':32}],
 'review_focus':['Full impact foot and entry into original pool','Mappedfoam follows the same displayed surface','Clear0.55mm droplets, nowhiteconfetti',
 'Remaining thin-face normal reversals or pinching','Visible effects of drift removal and filtered/clamped wave field'],
 'budget_note':'Measure first frame then stable frame; prior1280x72064sample84–94s is not a reliable36frame total; do not start final-quality or ten-second output',
 'production_status':'FAIL; preview is diagnostic, not acceptance or permission to install'}
h.write(ROOT/'qa/water-hybrid07-preview-spec.json',recipe)
fluid_path=ROOT/'data/fluid.json';fluid=json.loads(fluid_path.read_text(encoding='utf-8'))
fluid['latest_bounded_trials']['hybrid07_impact36']={'frames':36,'bake_seconds':963.3298037999994,'cache_bytes':1054473339,
 'report':'qa/water-hybrid07-motion-review.md','cache_range':[1,36],'source_core':'frozen07c_matches_root07',
 'physical_acceptance':'FAIL_POOL_HEAD_AND_DOMAIN_BOTTOM_LIMITATION','motion_geometry':'FAIL_THIN_TRIANGLE_NORMAL_REVERSALS',
 'installation_accepted':False,'second_bake_executed':False,'ten_second_acceptance':'NOT_RUN'}
fluid['acceptance']['hybrid07_36frame_cache']='PASS_FILES_AND_NEW_PROCESS_CRC_REOPEN'
fluid['acceptance']['hybrid07_continuous_body_motion']='FAIL_NORMAL_REVERSALS_1_TO_11_PER_FRAME_FIXED_JOINS_AND_ROCK_CONTACT_PASS'
h.write(fluid_path,fluid)
print('HYBRID_FINAL_DIAGNOSTIC',sha,flush=True)
