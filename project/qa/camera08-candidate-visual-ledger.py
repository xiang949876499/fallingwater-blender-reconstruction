"""Record manual individual-image review. No scene/config changes or rendering."""
from pathlib import Path
import collections
import datetime
import hashlib
import json

P = Path(__file__).resolve().parents[1]
NEW = P / 'renders/previews/iteration08-cameras'
OLD = P / 'renders/room-contact-sheets/iteration07/views'
SHA_SCENE = 'bf50530009e4a93315915815473188c91d891272ef2d8e9e0169b704bd2e2f16'
SHA_CONFIG = '4def78dcbae91f3292562f41796adec71c4680b64e04301f051fdc1833ce8666'
SHA_CANDIDATE = '214ae74cd82054bfb8c92a173fdbde0cc6a3ebbfd5ac9b1b42343338703b6c30'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def link(path):
    return path.resolve().as_posix()

# Human observations after opening each new and old 640x360 PNG at original size.
# Tuple: camera, label, disposition, improvement, limitations, followup.
OBS = [
    ('CAM_GUEST_L1_BOILER_B', 'LIMITED_COMPOSITION', 'ADOPT_LIMITED_DIAGNOSTIC',
     '旧图为几乎占满画幅的锅炉平箱正面；新图能读取烟管、锅炉、右侧压力罐及左侧入口之间的关系。',
     '锅炉下部占画面主体，烟管顶端及压力罐右侧仍出框；属于设备关系近景，不能作为完整锅炉房摄影。',
     '采用时保留LIMITED，不继续仅为扩大设备像素占比搜索。'),
    ('CAM_MAIN_B_PLUNGE_B', 'READABLE_DIAGNOSTIC', 'ADOPT_DIAGNOSTIC',
     '旧图只读到狭长水面与近墙；新图读到池身、池梯、石墙包围及远侧出口关系。',
     '水面仍深暗，右侧近梯占较大面积；池水真实感、远处结构和通行另验。',
     '采用；上层Loggia俯视A保持，完整08实际几何再验。'),
    ('CAM_MAIN_L1_COAT_B', 'FRAMING_FAIL', 'BOUNDED_RETRY',
     '目标由旧图楼梯/石墙改成储物柜，语义方向有改善。',
     '巨大暗柜板几乎填满画面，门把手/内部分格不可读，储物空间深度及开口关系不足。不能由目标命中率判通过。',
     '最多一次入口侧后退的候选检查，以柜体轮廓和真实开口为目标；不提高曝光掩饰缺失细节。若固定柜确为无细节块，转交家具记录，不继续搜相机。'),
    ('CAM_MAIN_L1_SERVANT_A', 'FRAMING_FAIL', 'BOUNDED_RETRY',
     '新图上移取景，显示更多沙发靠背和墙面。',
     '沙发左侧及底部仍裁切，原图较完整的桌面在新图被底边裁去，书柜关系反而丢失；未获得实质房间覆盖改善。',
     '最多一次南侧实际入口/可站立边缘的后退候选，争取座席、桌、柜三者关系；保留另一机位的独立方向，不复制A/B。'),
    ('CAM_MAIN_L1_SERVANT_B', 'FRAMING_FAIL', 'KEEP_OLD_PROVISIONAL',
     '新图显示较完整靠背上沿及少量上方窗口。',
     '仍是紧贴沙发和书柜的局部；桌面比旧图更残缺，方向变化不足以解决原FRAMING_FAIL。',
     '保留旧B作临时诊断值，原F不撤销；等待一次A修正后再判断覆盖，不为B再开独立微调搜索。'),
    ('CAM_MAIN_L2_CLOSET_G_A', 'LIMITED_COMPOSITION', 'ADOPT_LIMITED_DIAGNOSTIC',
     '旧图被侧柜/窄通道阻挡；新图能读到柜门、上沿把手及右侧窗/外门的相邻关系。',
     '柜顶、柜底出框，下部被床头遮住；开门后的内收纳没有展示，室外偏亮。',
     '可作为储物柜外部诊断采用，保留LIMITED，不等于完整储物空间通过。'),
    ('CAM_MAIN_L2_CLOSET_G_B', 'LIMITED_COMPOSITION', 'ADOPT_LIMITED_DIAGNOSTIC',
     '旧图主要为外窗及阳台；新图朝实际柜门，并在左缘看到相邻浴室与开口。',
     '木柜板仍占大部分画幅，上下出框、把手不可读，左侧浴室只是窄片。与A相较是有限的反向邻接关系。',
     '可作为外部储物关系诊断采用，保留LIMITED；不能算第二张全室照片。'),
    ('CAM_MAIN_L2_CLOSET_M_B', 'FRAMING_FAIL', 'BOUNDED_RETRY',
     '旧图为近石墙及透亮石缝；新图朝向真实柜体。',
     '床头横板遮住柜下部，柜顶和两侧出框，缺少把手及开口轮廓；整体仍是难以辨别空间的木板近景。旧石缝未出镜不代表已修。',
     '最多一次沿真实卧室床侧过道的后退/侧向候选，目标是柜体至少两条外轮廓和开口；不移动床/柜或站在床上。无安全可读位置则保留F并记录固定布置限制。'),
    ('CAM_MAIN_L3_ALCOVE_B', 'READABLE_DIAGNOSTIC', 'ADOPT_DIAGNOSTIC',
     '旧图朝木隔墙及外窗；新图清楚展示床垫、枕头、床头柜与侧窗关系。',
     '床脚/底架仍裁切，白床品局部偏亮且材质简单；这是床龛用途诊断，不是完整卧室摄影。',
     '采用；原A保留作为另一方向检查，不因可见床即撤销结构或材质问题。'),
    ('CAM_MAIN_L3_BATH_A', 'LIMITED_COMPOSITION', 'ADOPT_DIAGNOSTIC',
     '旧图被洗手盆镜背挡住；新图马桶座圈、便器和靠墙位置清楚，与已实看的旧B洗手盆视角互补。',
     '水箱顶部略出框、相机下俯，不能看到完整小浴室；墙地边缘和装配形状另验。',
     '采用为明确互补的WC诊断视角，标签仍LIMITED；原B不变。'),
    ('CAM_MAIN_L3_STAIR_A', 'READABLE_DIAGNOSTIC', 'ADOPT_DIAGNOSTIC',
     '旧图与L2 Stair A几乎共眼位；新图以较明显侧角展示梯段和下层蓝石平台、玻璃门窗关系，减少重复。',
     '栏墙/门框仍在右前景，下方深色开口不能凭本图判定修复或通行。',
     '采用上层独立诊断机位；保留L3 B，完整08再验真实楼梯支持和导航。'),
]

candidate_path = P / 'qa/camera08-candidate-settings.json'
production_path = P / 'data/camera-settings-reviewed.json'
benchmark_path = NEW / 'render-benchmark.json'
assert sha(candidate_path) == SHA_CANDIDATE
assert sha(production_path) == SHA_CONFIG
benchmark = json.loads(benchmark_path.read_text(encoding='utf-8'))
settings = json.loads(candidate_path.read_text(encoding='utf-8'))
readback = json.loads((P / 'qa/camera08-candidate-readback.json').read_text(encoding='utf-8'))
assert benchmark['status'] == 'PASS' and benchmark['scene_sha256'] == SHA_SCENE
assert benchmark['resolution'] == [640, 360] and benchmark['max_samples'] == 16
assert readback['scene_sha256'] == SHA_SCENE and readback['settings_sha256'] == SHA_CANDIDATE
runs = {r['camera']: r for r in benchmark['runs']}
assert len(runs) == len(benchmark['runs']) == len(OBS) == len(settings) == 11
assert set(runs) == set(settings) == {o[0] for o in OBS}
rows = []
for camera, label, disposition, improvement, limitations, followup in OBS:
    run = runs[camera]
    assert run['status'] == 'PASS'
    assert run['camera_settings'] == settings[camera], camera
    new_path = NEW / f'{camera}.png'
    old_path = OLD / f'{camera}.png'
    rows.append(dict(
        camera=camera, image=link(new_path), image_sha256=sha(new_path),
        old07_image=link(old_path), old07_image_sha256=sha(old_path),
        actual_review='INDIVIDUAL_ORIGINAL_SIZE_NEW_AND_OLD_IMAGE_OPENED',
        diagnostic_label=label, recommended_disposition=disposition,
        comparison=improvement, limitations=limitations, bounded_next_step=followup,
        exposure=run['exposure'], rendered_settings_match_candidate=True,
        geometry_scope='11-candidate readback on frozen07 only; full08 NOT_RUN',
        photography_pass=False, final_quality_accepted=False,
    ))

ledger = dict(
    reviewed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    scope='Manual diagnostic composition review of 11 new candidate PNGs plus their 11 original07 counterparts. A further old Bath B PNG was opened for complementarity. No production camera or geometry mutation. No rendering.',
    actual_geometry_scene='scene/Fallingwater_iteration07.blend', scene_sha256=SHA_SCENE,
    render_directory_is_candidate_label_not_scene_revision=True,
    candidate_settings_sha256=SHA_CANDIDATE, production_settings_sha256_unchanged=SHA_CONFIG,
    benchmark_sha256=sha(benchmark_path), benchmark_status=benchmark['status'],
    unique_new_images=11, individually_opened_new_images=11,
    individually_opened_comparison_images=11, extra_complementary_old_image='CAM_MAIN_L3_BATH_B',
    old_bath_b_sha256=sha(OLD / 'CAM_MAIN_L3_BATH_B.png'),
    resolution=benchmark['resolution'], samples=benchmark['max_samples'],
    diagnostics=dict(collections.Counter(r['diagnostic_label'] for r in rows)),
    dispositions=dict(collections.Counter(r['recommended_disposition'] for r in rows)),
    decisions_are_recommendations_only=True, production_mutated=False,
    full08_geometry='NOT_RUN', full08_visual='NOT_RUN', final_photo_quality='NOT_ACCEPTED',
    rows=rows,
)
out = P / 'qa/camera08-candidate-visual-ledger.json'
out.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

md = [
    '# 第08轮候选11图独立视觉复核', '',
    '**建议采用7个诊断机位，保留旧B一位，另3位各最多一次有界再修。没有改生产配置。** 新图诊断标签为3个READABLE、4个LIMITED、4个FRAMING_FAIL，摄影质量通过数为0。采用的7位包括4个明确保留限制的LIMITED视角。', '',
    '实际逐张打开11张新PNG及对应11张07旧PNG，均为640×360原尺寸，另打开旧L3 Bath B确认与新A互补。渲染记录11个唯一镜头、11次PASS、参数逐项等于候选JSON；这些PASS只说明文件渲染成功。', '',
    f'**实际几何仍是冻结07**（SHA256 `{SHA_SCENE}`），目录名iteration08-cameras代表下一轮相机候选，并非完整08场景验收。Cycles CPU、16 samples、AgX；新旧对比未靠提高曝光，11个曝光沿用原值。完整08的支持/身体射线和实图均为NOT_RUN。', '',
    '## 采用与保留', '',
    '- 采用诊断：Plunge B、Alcove B、Bath A、L3 Stair A。Bath A虽与洗手盆B互补，仍是小室有限WC视角。',
    '- 带LIMITED采用：Guest Boiler B、Closet G A、Closet G B。保留近裁和上下文不足记录。',
    '- 暂留旧值：Servant B。新图没有实质覆盖增益，旧FRAMING_FAIL不撤销。',
    '- 最多一次有界再修：Servant A、Coat B、Closet M B。当前新值不建议合入；旧值只是临时记录，不代表通过。', '',
    '## 每图结论', '',
    '| 镜头 | 新图标签 / 建议 | 相对07及限制 |',
    '|---|---|---|',
]
for r in rows:
    md.append(f"| [{r['camera']}]({r['image']}) | {r['diagnostic_label']} / {r['recommended_disposition']} | {r['comparison']} {r['limitations']} |")
md += ['', '## 有界再修建议', '']
for r in rows:
    if r['recommended_disposition'] == 'BOUNDED_RETRY':
        md.append(f"- **{r['camera']}**：{r['bounded_next_step']}")
md += [
    '', '这三项只是下一步建议，未生成新姿态、未运行新的搜索、未发起渲染。若后退区域被真实家具或墙体占据，应记录限制，而不是隐藏固定家具或无限微调。Servant B暂时不追加搜索，以避免两个相机又变成重复画面。', '',
    '## 结构问题与验收边界', '',
    '本轮候选移动不会修复地板/墙脚、衣柜石缝和门槛黑条。新Closet M B不再朝石墙，所以旧图透亮石缝的已知问题仍保持；Servant B的新图仍可见细亮墙脚线。完整08正在另行修补，必须按新场景重新验证，不能把本轮视角改变当作结构修复证据。', '',
    '曝光可辨不等于材质/照明真实。尤其Coat B的深暗面板需要把相机限制和柜体缺细节分开；单纯加曝光无法生成柜门结构。Plunge B能读池身，但池水质感没有通过。', '',
    f'生产120相机SHA256仍为 `{SHA_CONFIG}`。候选11项SHA256仍为 `{SHA_CANDIDATE}`。支持检查是冻结07上的11/11 GEOMETRY_ONLY_PASS，不能升级为完整08或全120新视觉PASS。', '',
    '## 图像哈希', '',
    '| 新图 | SHA256 |', '|---|---|',
]
for r in rows:
    md.append(f"| {r['camera']} | `{r['image_sha256']}` |")
md += ['', f'[完整逐图记录及新旧图哈希]({link(out)})。读回与参数源见 [候选读回记录]({link(P / "qa/camera08-candidate-readback.json")})。旧120图问题清单保持在 [07视觉报告]({link(P / "qa/camera07-room-review.md")})。', '']
(P / 'qa/camera08-candidate-visual-review.md').write_text('\n'.join(md), encoding='utf-8')
print(json.dumps({'diagnostics': ledger['diagnostics'], 'dispositions': ledger['dispositions'], 'production_unchanged': True, 'ledger': str(out)}, ensure_ascii=False))
