"""Summarize existing read-only probe; does not import Blender or create assets."""
import json
from pathlib import Path

QA = Path(__file__).resolve().parent
p = json.loads((QA / 'terrain-material08-shrub-probe.json').read_text(encoding='utf8'))
byname = {r['leaf_object']: r for r in p['near_instances']}
groups = {
    'west': ['0062', '0558', '0679', '0895', '1191', '1590', '1990', '1998'],
    'bridge': ['0055', '1071', '1334', '2150', '0110', '1338', '1342', '1043'],
}
chosen = []
for group, ids in groups.items():
    for ident in ids:
        r = byname[f'TREE_Understory_{ident}_Leaves']
        assert r['asset'] in (2, 3) and r['design_envelope']['preliminary_envelope_clear']
        assert all(abs(a-r['scale'][0]) < 1e-6 for a in r['scale'])
        chosen.append({
            'bank': group,
            **{k: r[k] for k in ('leaf_object', 'branch_object', 'asset', 'root', 'scale',
                                  'bounds_world_xyz_pairs', 'dimensions_world', 'ground_anchor_gap_m')},
            'camera_evidence': {c: {k: v[k] for k in ('direct_samples', 'through_glass_samples',
                                                     'projected_bound_px_xy_pairs')}
                                for c, v in r['cameras'].items()},
            'preliminary_envelope': r['design_envelope'],
            'proposed_world_height_max_m': 1.2 * r['scale'][0],
            'proposed_world_crown_radius_max_m': .55 * r['scale'][0],
        })
camera_quant = {}
for cam, s in p['camera_summary'].items():
    rows = [byname[n] for n in s['direct_instances']]
    camera_quant[cam] = {
        **{k: v for k, v in s.items() if k != 'direct_instances'},
        'direct_instance_world_dimensions_min_max_xyz_m': [
            [min(r['dimensions_world'][i] for r in rows), max(r['dimensions_world'][i] for r in rows)]
            for i in range(3)],
        'selected_direct_instances': sum(r['camera_evidence'].get(cam, {}).get('direct_samples', 0) > 0 for r in chosen),
        'selected_through_glass_instances': sum(r['camera_evidence'].get(cam, {}).get('through_glass_samples', 0) > 0 for r in chosen),
    }
out = {
    'status': 'DESIGN_ONLY_PENDING_ROOT_AUTHORIZATION_NO_PROTOTYPE',
    'source_blend': 'scene/Fallingwater_iteration08.blend',
    'source_sha256': p['source_sha256'], 'frame': 48,
    'failed_material_candidate_used': False,
    'scope': 'Replace data on exactly 16 existing leaf/branch object pairs; retain matrices and roots. Do not mutate old meshes shared by 600 users each.',
    'selection_evidence_grade': 'C: existing authored roots, not surveyed rhododendron positions; exact species/cultivar U',
    'total_understory_instances_before_and_after': 2400,
    'selected_plant_count': len(chosen), 'maximum_authorized_design_limit': 20,
    'camera_quantification': camera_quant,
    'prototype_local_geometry_limits': {'height_m': 1.2, 'radial_extent_m': .55,
        'asset2': {'basal_stems': 5, 'terminal_shoots': 20, 'leaves': 240},
        'asset3': {'basal_stems': 6, 'terminal_shoots': 24, 'leaves': 288},
        'leaf_length_m': [.13, .17], 'leaf_width_m': [.035, .05],
        'leaf_mesh_triangles': 12, 'total_triangles_per_plant_limit': 5500,
        'material_change': False, 'flowers': False},
    'selection': chosen,
    'collision_validation': 'PRELIMINARY_AABB_ONLY; future real geometry must pass actual terrain/route/hard-object tests. Not a built-candidate PASS.',
    'scene_saved': False, 'rendered': False, 'prototype_built': False,
}
(QA / 'terrain-material08-shrub-design.json').write_text(json.dumps(out, indent=2), encoding='utf8')

lines = [
    '# 08近岸灌木：只读量化与16株局部资产设计', '',
    '**DESIGN_ONLY / NO_BUILD / NO_RENDER / NOT_IN_PRODUCTION。** 本文等待整合者审阅后才进入独立局部模型候选。当前没有新增或替换任何植物，没有保存新场景。', '',
    '完整08为唯一拟用基线：`scene/Fallingwater_iteration08.blend`，SHA256 `' + p['source_sha256'] + '`。不叠加已判VISUAL_FAIL的落叶地面材质候选。该材质候选三图已由整合者与本代理实际打开并归档于`terrain-material08-visual-review.md`；HERO/Loggia呈均匀碎石贴面，Living远景几乎未改善。', '',
    '## 保存模型中的实际问题', '',
    '2400株understory中，asset0/1是各600株蕨类，asset2/3是各600株普通灌木，因此本诊断对象是1200株普通灌木。两类普通灌木各有13个独立双环直管分量、91个独立叶片分量；每片7顶点/6三角，枝干208三角，总754三角/株。`site.py::_plant_asset`也确认13根没有侧枝的直茎，每茎7叶，叶序从茎长20%排到83%，末梢留空17%。这种统一从根部放射、细茎尖端露出的结构解释了图上的尖锥轮廓。', '',
    '| 实际共享资产 | 本地宽X×宽Y×高（m） | 叶长范围（cm） | 叶宽范围（cm） | 单面叶面积（m²） |',
    '|---|---|---|---|---|',
]
for a in p['asset_meshes']:
    lines.append(f"| mesh{a['index']} | " + '×'.join(f'{v:.3f}' for v in a['local_dimensions']) +
                 f" | {a['leaf_length_m']['min']*100:.1f}–{a['leaf_length_m']['max']*100:.1f} | " +
                 f"{a['actual_outline_width_m']['min']*100:.1f}–{a['actual_outline_width_m']['max']*100:.1f} | {a['one_sided_leaf_mesh_area_m2']:.3f} |")
lines += ['',
    '现有叶长已经落在合理宽叶杜鹃参考量级；不能把失败简单归因于“小叶”，更不能只把每片叶放大。实际需要改变木质分枝、末梢叶群和不规则冠缘。实例旋转和缩放后的世界AABB大于某些本地宽度，以下数值来自保存对象而非脚本设定。', '',
    '## 三机位可见性与实际尺度', '',
    '以(5,5)为参考的35m近区共有433株mesh2/3。CPU4新进程在frame48、960×540对19个实际叶面三角中心/株抽样射线，共5610条；自己的叶或枝第一次被击中才记直接可见。玻璃最多跳过4层，只是透窗可见性的近似，不模拟折射。AABB相交不等于可见；下表是抽样确认的实例下界，不是精确像素覆盖率或可见叶片总数。', '',
    '| 相机 | AABB入画 | 直接可见实例 | 经玻璃抽样实例 | 直接实例实际X/Y/Z跨度范围（m） | 本提案直接/经玻璃实例 |',
    '|---|---:|---:|---:|---|---:|',
]
for cam, s in camera_quant.items():
    ranges = '; '.join(f'{a:.3f}–{b:.3f}' for a, b in s['direct_instance_world_dimensions_min_max_xyz_m'])
    lines.append(f"| {cam} | {s['bbox_intersects_frame_near35m']} | {s['sample_confirmed_direct_instances']} | {s['sample_confirmed_through_glass_instances']} | {ranges} | {s['selected_direct_instances']}/{s['selected_through_glass_instances']} |")
lines += ['',
    '直接与经玻璃集合可能重叠，不能相加当独立总数。即使一株仅一叶可见，它仍有91叶；因此不把104×91等数字称为“可见叶数”。完整每株世界bounds、原根位、相机投影包围框和逐样本首击对象保存在`terrain-material08-shrub-probe.json`。当前提案改善HERO及Loggia近岸形态；不能承诺修复Living约60m处的裸灰地面。', '',
    '## 现场与植物形态证据', '',
    '已实际查看的`data/photo_refs/main_sw_87.jpg`、`main_east_88.jpg`支持近岸层状裸岩、暗部枝干和稠密宽叶灌丛的组合，不支持把整坡变成草皮或均匀颗粒贴纸。照片无法可靠给出每株品种、年龄、叶片数或本模型具体根位，且没有把像素直接换算成新灌木的实测尺寸。', '',
    '- **本地存在证据。** 研究S12原链接为Fallingwater Tours；现可直接核对的[官方游客信息](https://fallingwater.org/visit/visitor-information/)说明本地杜鹃约六月下旬至七月中旬开白到浅粉色花。它支持本地rhododendron类别，不能确定每株为R. maximum或某栽培品种。',
    '- **生境与形态。** [美国林务局FEIS对R. maximum的综述](https://research.fs.usda.gov/feis/species-reviews/rhomax)描述河岸及邻坡的多干、弯曲枝条与密集灌丛，耐荫生长可较疏曲，叶集中在新生末梢并保留多个年生叶群；叶长8–35cm、宽2–8cm。这里把它作为候选结构参考，不作现场种鉴定。',
    '- **叶序。** [NC State Extension](https://plants.ces.ncsu.edu/plants/rhododendron-maximum/)记录宽叶常绿、多干、互生单叶、革质和全缘，常见叶长4–8英寸。因此应造“末梢密集互生/螺旋排列，视觉近似轮生”，不能造在同一节点上严格等角同高的真轮生轮盘。',
    '- **当地管理机构交叉核对。** [Western Pennsylvania Conservancy](https://waterlandlife.org/mountain-laurel-and-rhododendron-what-are-the-differences/)指出Bear Run保护区有山月桂及rhododendron，后者的长椭圆深色叶及湿凉河岸生境与本方案一致。照片中的每丛仍可能不是同一物种，精确品种为U。', '',
    '## 单一局部候选设计（所有精确数值为C）', '',
    '仅替换下表16株已有对象对，西岸8株用于HERO、桥岸8株用于Loggia并兼顾HERO。选择来自57株保守包络初筛中的高可见样本，以两个已实际失败区域验证形态；不改变原根位或变成规则排布。精确位置是现有作者散布的C级坐标，不是照片测得的杜鹃位置。', '',
    '- 两个新共享网格变体分别服务选中旧asset2/3：5或6根低位木质主干，每根经两级侧枝形成4个末梢，共20或24末梢。主干由连续弯曲截面构成，分叉不共面、末梢高度不齐；不使用13根同源直射线，不用球体/锥体树冠。主干局部直径2.5–4cm，末级小枝3–6mm，均为C设计限值。',
    '- 每末梢两段短年生叶群，各6片不严格共节点的互生叶，总240或288片/株；叶群间保持可读木枝。每叶11顶点/12三角，有中脉、轻弯和完整轮廓，叶柄接到实际小枝，不能是浮空卡片。局部叶长13–17cm、宽3.5–5cm，非加大旧叶。',
    '- 局部冠层径向范围≤0.55m、最高1.20m，保留原对象变换。所选缩放使实际株高上限约' + f"{min(r['proposed_world_height_max_m'] for r in chosen):.3f}–{max(r['proposed_world_height_max_m'] for r in chosen):.3f}" + 'm，冠半径上限约' + f"{min(r['proposed_world_crown_radius_max_m'] for r in chosen):.3f}–{max(r['proposed_world_crown_radius_max_m'] for r in chosen):.3f}" + 'm。这是低株局部试验尺度，不冒充成熟杜鹃灌丛的实测完整高度；若这种低株尺度本身不足，三图应明确失败而非偷偷扩大。',
    '- 每株≤5500三角，16株上限88000三角；只增加选中植物的分枝与叶群细节，不增加植物数、地面散叶数或全场灌丛密度。不造花；先保留现有叶/枝材质及光照，隔离形态变量。',
    '- 只把选中32个Leaves/Branches对象的data指向新网格；不能就地编辑仍被其他各600株共享的旧mesh2/3。保留对象名、matrix、root及全2400株实例计数，其他1184株普通灌木和1200株蕨类不改。', '',
    '| 区域/已有编号 | 原asset | 固定根位XYZ（m） | 缩放 | HERO/Loggia直接命中样本 | 最近实际路径边界（m） |',
    '|---|---:|---|---:|---:|---:|',
]
for r in chosen:
    h = r['camera_evidence'].get('CAM_HERO', {}).get('direct_samples', 0)
    l = r['camera_evidence'].get('CAM_MAIN_L1_LOGGIA_B', {}).get('direct_samples', 0)
    lines.append(f"| {r['bank']}/{r['leaf_object'].split('_')[2]} | {r['asset']} | " +
                 ', '.join(f'{v:.3f}' for v in r['root']) + f" | {r['scale'][0]:.3f} | {h}/{l} | " +
                 f"{r['preliminary_envelope']['nearest_actual_path_boundary'][0][1]:.3f} |")
lines += ['',
    '## 碰撞边界、冻结范围与未来验证', '',
    '当前只是半径0.85m、高度1.8m、根上0.10m起的保守冠层AABB预检：16株均不与可见MAIN/GUEST、核心、连续肩岩、桥和旧水对象AABB相交，距实际路径网格开放边界>1.0m、距全部相机XY>1.35m。这个包络比拟造冠层大；但它没有证明未来模型每个分叉或所有路线都通过，且根部以下/0.10m范围不在冠层预检内。', '',
    '授权后独立候选必须完成以下实际几何检查，未完成项当前均NOT_RUN：', '',
    '1. 根部用保存terrain实际BVH核对，维持现有约−12mm入土锚定。所有基部截面和细枝需检查坡面穿插；若坡面导致叶群埋入，缩减该株叶群或剔除该替换，不移动根位、不改变terrain或扩大保护圈。根部合理入土不当作悬空通过。',
    '2. 对真实新分枝/叶网格检测道路/桥走面、建筑墙/玻璃/门洞、MAIN水边楼梯、main_plunge_and_stair排除体、核心/肩岩及原水的实际三角碰撞。路径保留≥0.15m净空，相机保留≥0.50m身体/视点净空；此外复跑原完整导航路线的身体与头部检测。失败时减少替换名单，不靠移动保护物。',
    '3. 全部非目标对象的几何、世界矩阵、可见性、材质、相机、光照、曝光、帧和水缓存引用逐项与完整08冻结快照相同；旧共享网格hash不变，选中32对象仅data变化，所有根位精确不变，2400总实例不变。核心/肩岩/水的物理三角hash必须完全一致。',
    '4. 新进程读回独立候选，检查真实分枝连通、叶柄接触、叶片数量/尺寸、≤5500三角限制及无材质副作用，然后由整合者在原frame48/960×540同3相机渲染；本代理不渲染。HERO和Loggia检验冠缘/分枝/密集末梢是否可读，Living主要防止新遮挡并诚实记录远景问题未修。', '',
    '三个既有材质负样本、原08及所有检查日志保留不动。本设计不改变生产配置，也不把预检通过或将来成功保存模型当成视觉验收。', '',
    '## 证据文件', '',
    '- `terrain-material08-visual-review.md`：三张失败材质候选的实际图像评价。',
    '- `terrain-material08-shrub-probe.py/.json/.log`：CPU4只读探测，433株bounds、叶计数、5610个样本和57株预筛。',
    '- `terrain-material08-shrub-design.json`：16株精确根位、原bounds、投影矩形、缩放、预检包络与设计硬限。',
    '- `terrain-material08-shrub-design-report.py`：只从已保存探测数据生成本报告，不创建资产/场景。',
]
(QA / 'terrain-material08-shrub-design.md').write_text('\n'.join(lines) + '\n', encoding='utf8')
print(json.dumps({'selected': len(chosen), 'camera_quant': camera_quant,
                  'height_max_range_m': [min(r['proposed_world_height_max_m'] for r in chosen), max(r['proposed_world_height_max_m'] for r in chosen)],
                  'root_gap_range_m': [min(r['ground_anchor_gap_m'] for r in chosen), max(r['ground_anchor_gap_m'] for r in chosen)],
                  'files': ['terrain-material08-shrub-design.md', 'terrain-material08-shrub-design.json']}, indent=2))
