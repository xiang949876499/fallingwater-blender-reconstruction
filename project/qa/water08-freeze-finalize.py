"""Reconcile the bounded diagnostic findings into the owned handoff report."""
import json,hashlib,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'qa/water08-freeze-review.json'
r=json.loads(p.read_text(encoding='utf-8'))
d=json.loads((ROOT/'qa/water08-freeze-detail-probe.json').read_text(encoding='utf-8'))
frames=r['frames'];detail=d['frames'];adj=set(np.load(ROOT/'qa/water08-freeze-sampling.npz')['freeze_adjacent_triangles'].tolist())
worse=[e for f in frames for e in f['face_collision']['worsened_examples']]
assert all(len(f['face_collision']['worsened_examples'])==f['face_collision']['worsened_inherited_inside_samples'] for f in frames)
shortest=detail[10]['five_shortest_inward_chords'][0]
comparison=d['source_frame_crosschecks'][1]
original=comparison['source_vertical_thickness_m'];frozen=comparison['frozen_vertical_thickness_m']
dihedral=math.degrees(math.acos(max(-1,min(1,float(np.dot(shortest['source_normal'],shortest['hit_normal']))))))
r['status']='NORMALS_FIXED_LOCAL_THICKNESS_REGRESSION_NOT_ADOPTED'
r['review_conclusion']='Specified 155-point freeze removes reversed triangles at all 36 integer frames, but retaining motion on the opposite bottom skin reduces a measured 75.7666 mm source-frame water layer to 31.0755 mm. Keep diagnostic only; no installation.'
r['detailed_probe_report']='qa/water08-freeze-detail-probe.json'
r['actual_36frame_summary']['sampled_face_interior_no_new_inside_pass']=all(f['face_collision']['new_inside_samples']==0 for f in frames)
r['actual_36frame_summary']['no_worsening_of_inherited_Basis_contacts']=not worse
r['actual_36frame_summary']['worsened_inherited_contact_samples_touching_freeze_patch']=sum(e['triangle'] in adj for e in worse)
r['actual_36frame_summary']['inherited_contact_maximum_increase_m']=max(e['detail']['frame_m']-e['detail']['basis_m'] for e in worse)
r['actual_36frame_summary']['sampled_pond_top_bottom_order_pass']=all(f['sign_only_ordered_pair_missing']==0 for f in detail)
r['actual_36frame_summary']['strict_nz_02_filter_exceptions_max']=max(f['strict_nz_02_missing'] for f in detail)
r['actual_36frame_summary']['strict_filter_exceptions_interpretation']='All have a positive ordered pond entry/exit pair under sign-only classification; they are steep-surface exceptions, not missing or inverted water layers.'
r['actual_36frame_summary']['sampled_local_thickness_pass']=False
r['actual_36frame_summary']['sampled_local_thickness_pass_reason']='Thickness and shape preservation not accepted: measured 58.9852% reduction against actual source frame36 plus very sharp top-surface fold. No sampled top/bottom inversion demonstrated.'
r['thickness_interpretation']={
    'probe_xy_m':comparison['same_vertical_xy_m'],'frame':36,'source_actual_frame_thickness_m':original,
    'frozen_actual_frame_thickness_m':frozen,'reduction_m':original-frozen,'reduction_fraction':1-frozen/original,
    'source_surface_z_m':comparison['source_vertical_hits'][0]['z'],
    'frozen_surface_z_m':detail[35]['sign_only_minimum_vertical_pair']['pair'][0]['z'],
    'bottom_same_z_m':comparison['source_vertical_hits'][-1]['z'],
    'cause':'The three top triangle13172 vertices are among155 frozen; bottom triangle413679 vertices remain animated. Thus top/bottom separation no longer tracks coherently.',
    'shortest_inward_chord':shortest,'short_chord_top_surface_normal_angle_deg':dihedral,
    'short_chord_is_not_pool_depth':True,
    'short_chord_interpretation':'Both start and hit normals point upward; frame11 ray exits through an adjacent top-surface triangle sharing an edge. This is a narrow top-surface wedge/fold, not a measured0.441mm full pond layer. Existing source also has local fold/ray-orientation defects; do not attribute all of this defect to freezing.',
    'sign_only_ordered_pair_tests':len(detail)*r['thickness_method']['baseline_regular_top_bottom_pairs'],
    'sign_only_pair_failures':sum(f['sign_only_ordered_pair_missing'] for f in detail)}
r['contact_interpretation']={
    'points_per_frame':r['geometry']['all_active_related_triangles']*4,
    'point_frame_tests':r['geometry']['all_active_related_triangles']*4*36,
    'basis_inside_samples':77,'basis_near_contact_samples':154,
    'new_inside_samples_all_frames':sum(f['face_collision']['new_inside_samples'] for f in frames),
    'new_near_contact_samples_all_frames':sum(f['face_collision']['new_near_samples'] for f in frames),
    'old_contact_worsening_max_count_per_frame':max(f['face_collision']['worsened_inherited_inside_samples'] for f in frames),
    'old_contact_worsening_all_outside_frozen_patch':all(e['triangle'] not in adj for e in worse),
    'interpretation':'No new sampled rock interior/contact caused by the freeze. Up to5 original upstream samples deepen≤0.104mm versus Basis; every such face has no frozen vertex and all its source-key coordinates were preserved. These are retained pre-existing motion defects, not new freeze collisions.',
    'limits':'Nearest distance and three-ray parity at four barycentric samples per actual triangle. Continuous edges/interiors between samples remain unproven; this is not a global collision-free claim.'}
r['area_clarification']={
    'frozen155_all_adjacent_triangles':410,'frozen155_all_adjacent_area_m2':r['geometry']['freeze_adjacent_basis_area_m2'],
    'prior_diagnosis_0_023646085_m2_meant':'Immediate faces touching the original33 bad-triangle vertices, before expansion to155; not every face touching the final155-point frozen patch.'}
r['preservation_evidence']={
    'source_final_sha256':hashlib.sha256(Path(r['source']).read_bytes()).hexdigest(),
    'candidate_final_sha256':hashlib.sha256(Path(r['candidate']).read_bytes()).hexdigest(),
    'detail_probe_hash_assertions':{'source':d['source_hash_unchanged'],'candidate':d['candidate_hash_unchanged']},
    'scope':'One candidate only; no render, bake, production install, global settings, or existing source/helper edits.'}
assert r['preservation_evidence']['source_final_sha256']==r['source_sha256']
assert r['preservation_evidence']['candidate_final_sha256']==r['candidate_sha256']
r['logs']=['qa/water08-freeze-build.log','qa/water08-freeze-check.log','qa/water08-freeze-detail-probe.log',
           'qa/water08-freeze-check-triangulation-aborted.log','qa/water08-freeze-triangulation-probe.log']
r['diagnostic_checker_correction']='The first checker stopped at frame3 after assuming fixed render-triangle diagonals. Its log/json are retained. Corrected checker uses actual per-frame triangles and immutable Basis coordinates of those same vertices, preserving the1e-9 threshold; 36frames completed.'
p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
md=f'''# Water08：155 点冻结候选复核

2026-09-20。结论：**法线修复通过，局部厚度明显改变，不采纳为最终水体修复**。已只生成一个诊断副本，元数据 `DIAGNOSTIC_GEOMETRY_ONLY`；没有渲染、烘焙、安装生产或修改旧场景。水头与玻璃带／白泡沫圆片问题仍未解决。

候选：[Fallingwater_water_hybrid08_freeze155.blend](../scene/Fallingwater_water_hybrid08_freeze155.blend)，134,901,051 bytes。SHA256：`{r['candidate_sha256']}`。
源：`Fallingwater_water_hybrid07_motion36.blend`，SHA256：`{r['source_sha256']}`；制作及两次只读检查后均一致。

## 改动与边界

- 原样使用 `water08-normal-freeze-arrays.npz` 的155个 `ring_vertices`，未重选点、删面、改阈值或扩张候选变体。
- 仅将36个 `C_flow_and_real_impact_001…036` 键中这些点设回 Basis。原网格、Basis、其余点、fall/pond属性、材质、动画及缓存引用保留。另有诊断元数据。
- 155／6620活动点，占2.3414%；最多取消44.7888mm原位移。207943个外部固定点保持原样。
- 冻结点世界范围：X 0.405324～0.901242、Y −2.468675～−2.008302、Z −5.793751～−5.723366m。
- 局部 s 1.054957～1.412762、c −1.634225～−1.048230m。全部410个邻接三角的Basis面积0.0824923m²。前次0.0236461m²只统计最初33个坏面顶点的直接邻面。

## 实际逐帧验证

Blender5.2.1 LTS，新后台进程，CPU4。主检查72.47秒，另做只读射线解释和原源同帧对比；所有检查进程正常退出。

| 检查 | 实际结果 |
| --- | --- |
| 36帧真实求值反向三角 | 全部0；Basis叉积长度>1e−9且两叉积点积<0，阈值未变 |
| 155冻结点／207943外部点移动 | 全部0m |
| 原多边形拓扑 | 214563点、224758面，逐帧保持 |
| 边界／非流形边 | 全部0 |
| 渲染三角切分 | 429122三角；部分帧的2～4个局部三角对角线改变，按每帧真实切分检查，未将其误报为拓扑修改 |
| 新增岩内／近接触采样 | 全部0／0 |
| 上、下表面符号配对 | 3226位置×36帧，共116136次；有序配对缺失0 |

首次检查因“每帧渲染三角索引不变”的假设在第3帧停止，失败日志与JSON保留。修正的是检查方法，候选没有再次保存。

## 厚度与陡折面：不能用法线0推导通过

对每个向上落点面质心加独立31×31冻结区域网格做竖向射线；3232候选位置中3226在Basis可找到池层配对，6个无可靠基准的位置排除。水束可能另有上方交点，因此取池层范围的连续入／出交点。另对401个有效冻结邻面发出内法线射线。没有用正体积替代厚度。

**明确的厚度回归**：第36帧，XY=(0.4389154, −2.10505571)m。原场景同帧水层厚75.7666mm，冻结候选31.0755mm，减少44.6911mm（{(1-frozen/original)*100:.4f}%）。原顶部Z −5.732058m，被冻结为−5.776749m；底部Z −5.807825m未变。顶部三角13172的3点全被冻结，底部三角413679仍随原动画运动。此处上、下顺序尚为正，但配对表皮失去同步。

**短弦须正确解释**：第11帧，三角428746质心(0.922703, −2.225582, −5.779128)m，内向射线0.440780mm后从邻面428751退出。两面法线Z均为正，夹角约{dihedral:.2f}°；这是上表面尖折边的短弦，不能称整个水池只有0.441mm厚。对应Basis同起始面内向射线为70.4527mm。原motion同一区域也存在折面／射线出口朝向异常，不能把所有局部缺陷归因于冻结。

原严格法线Z>0.2／<−0.2的水层配对每帧最多30个例外；补查完整交点后，全都能按正、负符号配对，属于陡面，未证实上下面倒置。窄尖折边、约59%局部水层减薄及固定补丁视觉仍不具备采纳依据。

## 岩石接触范围与既有反例

检查全部13484个活动相关真实三角，每面质心及3边中点，共53936位置／帧（1941696点帧）。与活动区域相交的实际岩石为 `SITE_Core_Continuous_Fractured_Sandstone`，使用其渲染三角BVH、最近距离和3方向奇偶射线；0.5mm内单列接触，未把这些点直接当作安全外部点。

Basis已经有77个岩内样本和154个近接触样本。36帧没有新增岩内或近接触样本；最多5个原有上游样本较Basis加深，最大0.103951mm，全部不接冻结155点，且它们的原shape-key坐标经哈希确认保留。这些是原motion已有的动画接触问题。例：三角210884边中点已有约42.07mm穿入，不能因“新增0”而宣称全体水体无穿岩。

四点采样不能证明两个样本之间的全部三角内部／边都不与岩石相交。未执行全局自交证明、连续子帧检查或超过1.5秒的动画检查。

## 交付与后续边界

- 结构化主报告：[water08-freeze-review.json](water08-freeze-review.json)。射线明细与原场景同帧对照：[water08-freeze-detail-probe.json](water08-freeze-detail-probe.json)。
- 过程与失败证据：`water08-freeze-build.log`、`water08-freeze-check.log`、`water08-freeze-detail-probe.log`、`water08-freeze-check-triangulation-aborted.log/json`。
- 选择和采样表：`water08-freeze-sampling.npz`、`water08-freeze-thickness-sampling.npz`。所有辅助检查仅在qa内新增，旧hybrid脚本不变。
- 未继续制作变体。父任务需先决定如何保持顶／底表皮同步及改善冻结边缘，再决定任何后续执行；本候选保留作诊断，不安装生产。

收尾已按neat-freak范围核对报告与实际产物，未改父任务负责的STATUS、AGENTS或全局设置。
'''
(ROOT/'qa/water08-freeze-review.md').write_text(md,encoding='utf-8')
print(json.dumps({'status':r['status'],'candidate_sha256':r['candidate_sha256'],'reduction_fraction':1-frozen/original,'top_fold_normal_angle_deg':dihedral},ensure_ascii=False))
