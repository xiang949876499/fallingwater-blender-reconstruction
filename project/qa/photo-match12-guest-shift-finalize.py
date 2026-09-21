"""Freeze second camera diagnosis, retaining first round unchanged."""
import json,hashlib,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
file=ROOT/'qa/photo-match12-guest-shift-fit.json'
new=json.loads(file.read_text(encoding='utf-8'));old=json.loads((ROOT/'qa/photo-match12-guest-fit.json').read_text(encoding='utf-8'))
vertical=json.loads((ROOT/'qa/photo-match12-guest-shift-verticals.json').read_text(encoding='utf-8'))
rays=json.loads((ROOT/'qa/photo-match12-guest-shift-rays.json').read_text(encoding='utf-8'))
# Correct two metadata labels only, without rerunning any optimizer or changing
# any camera number, point, projection or residual.
for a,b in [('fit_ids','fit_count'),('holdout_ids','holdout_count')]:
    if a in new['fit']:new['fit'][b]=new['fit'].pop(a)
file.write_text(json.dumps(new,indent=2),encoding='utf-8')
datafile=ROOT/'data/photo-match-points12-guest-exterior.json'
assert hashlib.sha256(datafile.read_bytes()).hexdigest()==new['locked_points_sha256']==old['locked_points_sha256']
assert hashlib.sha256(Path(new['scene']).read_bytes()).hexdigest()==new['scene_sha256']==old['scene_sha256']
oldR=np.array(old['camera']['world_to_opencv']);vp=np.array([371,512])+old['camera']['focal_px']*oldR[:2,2]/oldR[2,2]
verticals=[]
for measured,current in zip(vertical['traces'],new['independent_vertical_line_checks']):
    pts=np.array(measured['points_xy']);center=pts.mean(axis=0);slope=(center[0]-vp[0])/(center[1]-vp[1]);b=float(np.mean(pts[:,0]-slope*pts[:,1]));delta=(pts[:,0]-slope*pts[:,1]-b)/math.sqrt(1+slope*slope)
    verticals.append(dict(current,first_camera_predicted_angle_degrees=math.degrees(math.atan(slope)),
        first_camera_direction_rms_px=float(np.sqrt(np.mean(delta**2))),
        role_note='Independent of15photo/modelpoints; these sixsource traces were used to choose fixedroll, so not out-of-samplecameraorientationvalidation.'))
review={'schema':'fallingwater.photo_match12.guest_second_camera_review.v1','status':'UNVERIFIED; GEO07 ACCEPTANCE NOT_RUN',
 'physical_scene_unchanged':True,'scene_sha256':new['scene_sha256'],'same_point_file_sha256':new['locked_points_sha256'],
 'camera_trials_total':2,'more_trials':False,'first_report_preserved':'photo-match12-guest-review.md',
 'second_camera':new['camera'],'statistics':new['statistics'],'vertical_trace_comparison':verticals,
 'vertical_traces':{'count':6,'total_retained_rows':sum(p['rows_retained'] for p in vertical['traces']),
     'median_roll_deg':vertical['roll_fixed_degrees'],'maximum_single_trace_deviation_px':max(p['max_deviation_px'] for p in vertical['traces']),
     'uncertainty':'Gradient traces can switch between a post bright/darkedge. V5 has5.815pxmax deviation; retained, no cherry-picking. Medianroll C constraint, pitch0 C near-horizontal hypothesis.'},
 'support':rays['support_probes'],'support_status':'Normal standingcameraFAIL; no actualphotographerposeknown. No terrain or model adjusted.',
 'same_point_qualification_failures_retained':['W0H and allS nominal points hidden by closerstonecourses','OtherH targets composite post/headjoints','7equalmodeldivisionsdo notindependentlyregister2010printedposts','R03source terminalidentity independentlyunverified'],
 'interpretation':'Allowingcywhileholdingpitch/rollfromphoto decreaseswindowmedian/verticaltilt but worsensindependentR03from37.225to44.428px and doesnotproduce standingpose. It cannot resolveGEO07; residualcannotbeconvertedintoarchitecturecorrection.',
 'source_date':'1985February/March photo;2010drawings; no assumedchronologicalequivalence or assertedrenovation',
 'images_actually_opened':['photo-match12-guest-shift-vertical-source-crop.png','photo-match12-guest-shift-verticals-observed.png','photo-match12-guest-shift-points-overlay.png','photo-match12-guest-shift-continuous-edges.png'],
 'stopped':'No morecameraoptimization; nextstep is independently reviewpoint identity/model facade/source registration, not parametersearch.',
 'metadata_correction':'shift-fit fit_ids/holdout_ids integercount labels corrected tofit_count/holdout_count without modifying numericfit.'}
(ROOT/'qa/photo-match12-guest-shift-review.json').write_text(json.dumps(review,indent=2),encoding='utf-8')
lines=['|竖线|原片角度°|自身线性RMS px|旧镜头方向RMS px|新镜头方向RMS px|','|---|---:|---:|---:|---:|']
for r in verticals:lines.append('|%s|%.6f|%.4f|%.4f|%.4f|'%(r['id'],r['measured_angle_degrees'],r['rms_about_own_line_px'],r['first_camera_direction_rms_px'],r['camera_parallel_direction_rms_px']))
hold=['|保留点|旧镜头误差px|替代镜头误差px|替代误差/对角线|','|---|---:|---:|---:|']
for a,b in zip(old['points'],new['points']):
    assert a['id']==b['id'] and a['pixel']==b['pixel'] and a['role']==b['role'] and a['world_m']==b['world_m']
    if a['role']=='holdout':hold.append('|%s|%.6f|%.6f|%.4f%%|'%(a['id'],a['residual_px'],b['residual_px'],b['residual_pct_diagonal']))
md='''# Guest A10：第二且最后镜头假设交接

**GEO-07仍NOT_RUN/UNVERIFIED，没有得到照片配准通过。** 原固定主点7参数失败报告和全部冻结文件不变。本次只按根授权增加一个有来源约束的替代解释：光轴水平、竖线测量固定roll，横主点371保持，只允许垂直主点cy变化；优化yaw、XYZ、f、cy共6参数。没有第3次镜头尝试，没有换点或改几何。

模型 `scene/Fallingwater_guest_bays_candidate12a.blend` SHA `'''+new['scene_sha256']+'''`；同一 `data/photo-match-points12-guest-exterior.json` SHA `'''+new['locked_points_sha256']+'''`。原8fit/7holdout角色、每个像素、实际对象/定位/世界坐标、742×1024分辨率完全相同。原照片年份仍1985年2–3月，2010图纸不等于2010照片。

## 来源竖线与旋转约束

先实际打开窗柱中段放大原片，再在6条预选连续窗柱边ROI中逐行找水平Sobel梯度峰，保留全部884行，使用局部抛物线亚像素峰和普通线性回归；没有用模型投影选择ROI，没有删离群行。测量JSON SHA `'''+new['vertical_measurement_sha256']+'''` 先于本次拟合锁定，并实际打开 `photo-match12-guest-shift-verticals-observed.png`。

取6条线斜率中位对应roll=0.404234978°，pitch固定0°。这是近水平建筑摄影的C假设；相机/后背移轴、扫描偏心等原因均为U，不能断言使用了某种摄影装置。V5梯度会跳到邻边，最大线性偏差5.815px，完整保留；因此不把这个roll当作高精度摄影标定。竖线独立于15个3D对应点，但同组线用于确定roll，所以方向残差不是另外保留的一组相机验收点。

'''+ '\n'.join(lines)+'''

## 两个假设比较

|参数/结果|第一固定主点镜头|第二源约束镜头|
|---|---:|---:|
|自由参数|7|6|
|pitch|11.517908°|0°固定|
|roll|自由拟合|0.404235°固定|
|cx|371固定|371固定|
|cy|512固定|683.826895|
|cy相对原中心|0|+171.826895px，图高16.779970%|
|36mm长边等效焦距|28.470759mm|27.698814mm|
|8fit中位误差|11.807083px|7.555054px|
|7holdout中位误差|9.647160px|7.552000px|
|最差holdout R03|37.224644px|44.428183px|
|镜头到实际脚下地形|0.459400m|0.321908m|

第二镜头眼位(0.734424231,33.275106108,7.518351750)m，yaw20.929575°，f787.877380px；主点cy未触0..1024边界。参数和完整矩阵在 `photo-match12-guest-shift-fit.json`。保留点从未参与目标函数；所有15点仍在相机前。

'''+ '\n'.join(hold)+'''

真实保存场景射线首先命中 `SITE_Continuous_BearRun_Terrain` 面129261，脚下Z7.196443081m。0.18m周边5点分别仅离镜头0.302–0.411m；没有楼梯踏面可将该镜头解释成正常站立。低相机摄影并非不可能，但档案未提供姿势依据。没有为了提高站立高度改变模型或相机约束。

## 实际叠图的结论

`photo-match12-guest-shift-points-overlay.png` 与 `photo-match12-guest-shift-continuous-edges.png` 均已实际打开。近窗柱的投影方向改进，说明旧固定扫描中心主点会影响局部配准。但连续檐梁和天窗仍向右下漂，独立远檐R03误差增加到44.428px（3.5133%对角线），没有解决非共面结构。台阶投影与源石墙/踏步接口仍不吻合。

两假设共有的资格问题继续成立：W0H及所有窗下端首先被前侧石皮遮挡；其余窗头名义点是head与post复合接缝；2010图纸窗柱符号与当前7等分C模型并未一一登记；R03身份还需要独立审核。镜头变化不撤销这些事实，也不能把更低总中位称为通过。

下一步交独立源身份审查：近窗W0到底属于西转角还是第一柱、真正可见head/sill交线、远檐R03的终止身份。没有足够依据根据投影偏移直接修改屋檐尺寸；也不继续放开更多相机参数。

交接主文件：`photo-match12-guest-shift-review.json`（两方案与全部竖线比较）、`photo-match12-guest-shift-fit.json`（同15点完整残差）、`photo-match12-guest-shift-rays.json`（实际面/支撑/遮挡）、`photo-match12-guest-shift-freeze.json`（哈希）。旧 `photo-match12-guest-review.md/json` 和其manifest保持原样。neat-freak按限定QA范围完成交接核对；没有修改生产模型、相机、数据旧件、root状态或其他模块。
'''
(ROOT/'qa/photo-match12-guest-shift-handoff.md').write_text(md,encoding='utf-8')
files=sorted((ROOT/'qa').glob('photo-match12-guest-shift-*'))
manifest={'scene_sha256':new['scene_sha256'],'points_sha256':new['locked_points_sha256'],'status':review['status'],
 'camera_trials_total':2,'no_more_trials':True,'first_hypothesis_sha256':hashlib.sha256((ROOT/'qa/photo-match12-guest-fit.json').read_bytes()).hexdigest(),
 'first_report_sha256':hashlib.sha256((ROOT/'qa/photo-match12-guest-review.md').read_bytes()).hexdigest(),
 'files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files if p.is_file() and p.name!='photo-match12-guest-shift-freeze.json']}
(ROOT/'qa/photo-match12-guest-shift-freeze.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'status':review['status'],'files':len(manifest['files']),'scene_unchanged':True,'point_roles_and_numbers_unchanged':True,'vertical_rows':review['vertical_traces']['total_retained_rows']},indent=2))
