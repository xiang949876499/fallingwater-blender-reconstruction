"""Assemble authorized seven-view adoption into an independent full config."""
from pathlib import Path
from copy import deepcopy
import hashlib
import json

P = Path(__file__).resolve().parents[1]
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

prod_path = P / 'data/camera-settings-reviewed.json'
candidate_path = P / 'qa/camera08-candidate-settings.json'
ledger_path = P / 'qa/camera08-candidate-visual-ledger.json'
assert sha(prod_path) == '4def78dcbae91f3292562f41796adec71c4680b64e04301f051fdc1833ce8666'
prod = json.loads(prod_path.read_text(encoding='utf-8'))
candidate = json.loads(candidate_path.read_text(encoding='utf-8'))
ledger = json.loads(ledger_path.read_text(encoding='utf-8'))
accepted = {r['camera']: r for r in ledger['rows'] if r['recommended_disposition'].startswith('ADOPT_')}
assert set(accepted) == {
    'CAM_MAIN_B_PLUNGE_B', 'CAM_MAIN_L3_ALCOVE_B', 'CAM_MAIN_L3_BATH_A',
    'CAM_MAIN_L3_STAIR_A', 'CAM_GUEST_L1_BOILER_B',
    'CAM_MAIN_L2_CLOSET_G_A', 'CAM_MAIN_L2_CLOSET_G_B',
}
result = deepcopy(prod)
for name, r in accepted.items():
    val = deepcopy(candidate[name])
    val['render_reviewed'] = True
    val['composition_status'] = 'STAGED_DIAGNOSTIC_ACCEPTED'
    val['diagnostic_label'] = r['diagnostic_label']
    val['final_quality_accepted'] = False
    val['visual_evidence'] = {
        'scene': ledger['actual_geometry_scene'],
        'scene_sha256': ledger['scene_sha256'],
        'image': r['image'], 'image_sha256': r['image_sha256'],
        'actual_review': r['actual_review'],
        'limitations': r['limitations'],
        'scope': 'Accepted diagnostic composition on frozen07; full08 geometry and actual images still require validation; not final photography.',
    }
    val['evidence'] = val['evidence'].replace('Geometry diagnostics only; actual image review pending.', 'Actual image reviewed; staged diagnostic acceptance only.')
    result[name] = val
assert len(result) == len(prod) == 120
unchanged = [n for n in prod if n not in accepted]
assert len(unchanged) == 113 and all(result[n] == prod[n] for n in unchanged)
assert all(result[n][k] == candidate[n][k] for n in accepted for k in ('location', 'target', 'lens', 'shift_x', 'shift_y', 'exposure'))
path = P / 'qa/camera08-accepted-settings.json'
path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
readback = json.loads(path.read_text(encoding='utf-8'))
assert readback == result
manifest = {
    'full_config': path.resolve().as_posix(), 'sha256': sha(path), 'count': 120,
    'production_path': prod_path.resolve().as_posix(), 'production_sha256_unchanged': sha(prod_path),
    'source_candidate_sha256': sha(candidate_path), 'source_visual_ledger_sha256': sha(ledger_path),
    'accepted_count': 7, 'preserved_original07_count': 113,
    'accepted': [{k: r[k] for k in ('camera', 'diagnostic_label', 'image', 'image_sha256', 'limitations')} for r in accepted.values()],
    'held_original07': ['CAM_MAIN_L1_SERVANT_A', 'CAM_MAIN_L1_SERVANT_B', 'CAM_MAIN_L1_COAT_B', 'CAM_MAIN_L2_CLOSET_M_B'],
    'geometry_validation_scene_sha256': ledger['scene_sha256'],
    'full08_geometry': 'NOT_RUN', 'full08_visual': 'NOT_RUN',
    'final_photo_quality': 'NOT_ACCEPTED', 'production_mutated': False,
}
(P / 'qa/camera08-accepted-settings-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
md = [
    '# 第08轮采用的7个诊断视角', '',
    '**独立完整120相机配置已生成：采用7个新视角，另外113个保留07原值。生产data文件未改。**', '',
    f'[完整配置]({path.resolve().as_posix()}) SHA256：`{manifest["sha256"]}`。', '',
    '本子集实际7张图全部逐张打开并与07旧图比较：3个R（可读诊断）、4个L（有限构图）。L没有因被采用而升级为R。所有采用仅用于诊断，摄影质量均未通过。', '',
    '| 相机 | 分类 | 采用依据与保留限制 | 图像SHA256 |', '|---|---|---|---|',
]
for r in accepted.values():
    label = 'R — READABLE_DIAGNOSTIC' if r['diagnostic_label'] == 'READABLE_DIAGNOSTIC' else 'L — LIMITED_COMPOSITION'
    md.append(f"| [{r['camera']}]({r['image']}) | {label} | {r['comparison']} {r['limitations']} | `{r['image_sha256']}` |")
md += [
    '', '## 本轮保持原值的4位', '',
    'Servant A/B、Coat B、Closet M B均保留07原配置，其原构图FAIL不撤销。Servant B的新图只增加上沿墙面/窗口，没有取得足够覆盖增益，本轮不再搜索。', '',
    '## 仅记录下一步的三项有界建议', '',
]
for r in ledger['rows']:
    if r['recommended_disposition'] == 'BOUNDED_RETRY':
        md.append(f"- **{r['camera']}**：{r['bounded_next_step']}")
md += [
    '', '本轮不继续试渲，没有为这三项生成新姿态。', '',
    '## 来源与重新验证要求', '',
    f'实际样图源为冻结07场景，SHA256 `{ledger["scene_sha256"]}`，不是尚待整合的完整08。全部7位的眼点、target、28mm焦距、shift与曝光，均精确取自已渲染的候选配置；11候选在07真实支撑/身体射线上通过，不表示新08也已通过。', '',
    f'原生产配置SHA256 `{manifest["production_sha256_unchanged"]}`；候选源SHA256 `{manifest["source_candidate_sha256"]}`。读回确认完整120个名字、7个被授权替换、113项对象内容完全不变。新增视觉证据绑定实际图像哈希，final_quality_accepted保持false。', '',
    '完整08合入后必须重新检查120位实际支持面、身体净空及保存相机参数，并看受结构变化影响的图。旧图的已证实墙脚/石缝不能因为新机位不再拍到就自动结案。', '',
    f'[完整11图独立复核]({(P / "qa/camera08-candidate-visual-review.md").resolve().as_posix()})；[120文件及7图清单]({(P / "qa/camera08-accepted-settings-manifest.json").resolve().as_posix()})。', '',
]
(P / 'qa/camera08-accepted-review.md').write_text('\n'.join(md), encoding='utf-8')
print(json.dumps({'count': 120, 'accepted': 7, 'unchanged': 113, 'sha256': manifest['sha256'], 'production_mutated': False}, ensure_ascii=False))
