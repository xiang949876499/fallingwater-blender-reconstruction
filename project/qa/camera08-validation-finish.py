"""Bind completed Blender exit0 outputs and document actual08 support changes."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
Q = ROOT / 'qa'
def read(name):
    return json.loads((Q / name).read_text(encoding='utf-8'))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def link(name):
    return (Q / name).resolve().as_posix()

summary = read('camera08-validation-summary.json')
saved = read('camera08-saved-settings-check.json')
geometry = read('camera08-verification.json')
old = {r['camera']: r for r in read('camera07-verification.json')['cameras']}
frozen = read('camera08-settings-frozen.json')
accepted = read('camera08-accepted-settings-manifest.json')
assert summary['geometry_status'] == 'GEOMETRY_ONLY_PASS'
assert summary['saved_settings_status'] == 'SAVED_SETTINGS_MATCH'
assert len(geometry['cameras']) == len(saved['cameras']) == 120
assert {r['camera'] for r in geometry['cameras']} == set(frozen)
assert summary['scene_unchanged'] and summary['active_settings_unchanged']
changes = []
for r in geometry['cameras']:
    earlier = old[r['camera']]
    if r['actual_center_support'] != earlier['actual_center_support']:
        changes.append({
            'camera': r['camera'], 'old07_actual_center': earlier['actual_center_support'],
            'new08_actual_center': r['actual_center_support'],
            'camera_adopted_new_pose': r['camera'] in {v['camera'] for v in accepted['accepted']},
        })
name_changes = [r for r in geometry['cameras'] if r['support_object_changed']]
height_changes = [r for r in geometry['cameras'] if abs(r['support_delta_z_m'] or 0) > .00001]
summary.update({
    'process_exit_code': 0,
    'max_saved_field_errors': {k: max(r['errors'][k] for r in saved['cameras']) for k in saved['cameras'][0]['errors']},
    'safety_support_body_eye_rays': 1920,
    'legacy_unshifted_view_diagnostic_rays': 1920,
    'actual_center_changes_since07': changes,
    'stored_support_name_differences': [{k: r[k] for k in ('camera', 'stored_support', 'actual_center_support', 'support_delta_z_m')} for r in name_changes],
    'stored_support_height_differences': [{k: r[k] for k in ('camera', 'stored_support', 'actual_center_support', 'support_delta_z_m')} for r in height_changes],
    'reports': {name: sha(Q / name) for name in (
        'camera08-verification.json', 'camera08-saved-settings-check.json',
        'camera08-verification.log', 'camera08-saved-geometry-input.json',
        'camera08-settings-frozen.json', 'camera08-verify.py',
    )},
})
(Q / 'camera08-validation-summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

md = [
    '# 完整第08轮120机位独立检查', '',
    '**120/120保存相机参数匹配；120/120实际网格点位安全检查通过。Blender5.2.1 LTS、CPU4进程退出码0。** 本检查没有渲染，没有改生产配置、相机或场景。', '',
    f'实际源 [Fallingwater_iteration08.blend]({(ROOT / "scene/Fallingwater_iteration08.blend").resolve().as_posix()}) SHA256 `{summary["scene_sha256"]}`。冻结 [camera08-settings-frozen.json]({link("camera08-settings-frozen.json")}) SHA256 `{summary["settings_sha256"]}`，与已采用7位后的生产文件同字节；检查前后场景和生产文件哈希均未变。', '',
    '## 先读取保存值，再比较与检查', '',
    '从磁盘重新打开完整08后，先读取每个真实相机的世界位置、完整四元数旋转（含滚转）、焦距、shift_x、shift_y和fw_exposure，随后与冻结JSON比较。没有先应用配置，也没有保存场景。全部120位逐字段误差低于0.0001；最大shift_y误差为1.669×10⁻⁸，其余记录的最大误差为0。', '',
    '点位射线使用刚读出的实际世界位置和方向；方向目标沿相机自身−Z恢复。冻结配置里的地面高度只作为参考，用来检出实际支持面变化。独立写出的saved-geometry-input是检查输入，不是生产相机设置，也没有回写场景。', '',
    f'[实际保存值与期望值逐项记录]({link("camera08-saved-settings-check.json")})；[真实几何120行报告]({link("camera08-verification.json")})；[运行摘要与哈希]({link("camera08-validation-summary.json")})；[完整日志]({link("camera08-verification.log")})。', '',
    '## 当前几何与支持面', '',
    '新评估索引为9,631对象、976,540顶点、1,042,424多边形。3,840条总射线中，1,920条检查四脚支持点、身体柱、六方向眼点及中心地面；其余1,920条是旧式未应用shift的取景诊断射线，不能证明构图通过。身体检查高度1.75m、五条轴向竖射线覆盖0.15m半径，属于离散点位检查，不是连续碰撞体或导航路径验收。', '',
    '中心支持面相对冻结地面高度容差4cm；四脚点允许19cm高度差并排除家具、水和陡斜支持。18个房间多边形外的相邻/门外/平台检查位重新计算后标识全部匹配；它们仍不是18个房间内部浏览通过。', '',
    '相对旧07报告，有9个中心支持记录变化：7个来自本轮已接受的实际机位移动；另2个为原机位的地面变化，具体如下。', '',
    '| 原机位 | 08实际支持变化 | 结果与限制 |', '|---|---|---|',
    '| CAM_MAIN_L2_BATH_G_A | 原门槛饰面变为MAIN_L2_BATH_G_finish，高度仍2.86700m | 中心和身体检查通过；这个单点不能证明整条墙脚/门槛无缝 |',
    '| CAM_GUEST_L1_POOL_A | 同一GUEST_L1_MAIN_FLOOR上，07实测8.40137m，08实测8.40020m | 相对冻结support_z 8.40430m低4.1mm，在4cm容差内；眼高相对实际面约1.6041m，不改配置 |', '',
    '此外，Main Coat B的冻结支持名称仍是旧门槛饰面、实测为MAIN_L1_COAT_finish；Guest Boiler A旧名GUEST_L1_HALL_NORTH、实测GUEST_L1_CAR_COURT。两项名称差异已存在于07，08仍为同高；不把旧差异误记为新结构退化。', '',
    '| 新采用机位 | 08实际中心支持面 | z（米） |', '|---|---|---:|',
]
for r in geometry['cameras']:
    if r['camera'] in {v['camera'] for v in accepted['accepted']}:
        center = r['actual_center_support']
        md.append(f"| {r['camera']} | {center['object']} | {center['location'][2]:.5f} |")
md += [
    '', '## 视觉与范围边界', '',
    '本轮只是完整08上的新几何与保存参数复验，没有打开新的完整08渲染图。此前接受的7张构图图像来自冻结07：Plunge B、Alcove B、Stair A为R；Bath A、Boiler B、Closet G A/B为L。它们的历史标签和图像哈希保留，不能因08点位通过而升级为08视觉通过。', '',
    '房间几何索引排除植被；HERO等展示相机不在这120位范围内。未完成的Servant A/B、Coat B、Closet M B构图FAIL，以及其他旧图的材质、照明、墙脚与石缝问题仍需新图检查。摄影质量、连续导航和全120新视觉均不由本报告验收。', '',
    f'历史证据：[07逐房120图]({link("camera07-room-review.md")})；[7位采用的图像与限制]({link("camera08-accepted-review.md")})。', '',
]
(Q / 'camera08-review.md').write_text('\n'.join(md), encoding='utf-8')
print(json.dumps({'status': summary['geometry_status'], 'saved': summary['saved_settings_status'], 'center_changes_vs07': len(changes), 'stored_support_name_differences': len(name_changes), 'height_differences': len(height_changes)}, ensure_ascii=False))
