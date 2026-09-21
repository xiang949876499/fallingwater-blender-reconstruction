"""Root-owned documentation reconciliation; no production model changes."""
from pathlib import Path
import csv
import json
import hashlib

root = Path(__file__).resolve().parents[1]
qa = root / 'qa'
expected = '489b05e403aa9d02c3568a8e3813a24235ee5b7e782df4d1f149b3ff6673e331'
assert hashlib.sha256((root / 'scene/Fallingwater_iteration09.blend').read_bytes()).hexdigest() == expected
tour = json.loads((qa / 'tour-path-iteration09-attempt01-result.json').read_text(encoding='utf-8'))
assert tour['source_sha256'] == expected and tour['counts'] == {'PASS':58,'FAIL':2,'NOT_RUN':0}
assert tour['frame_count'] == 7584 and tour['integer_frame_failure_count'] == 0
for name in ('STATUS.md', 'qa/issues.csv'):
    p = root / name
    backup = qa / ('before-reconcile09-' + p.name)
    if not backup.exists():
        backup.write_bytes(p.read_bytes())

(root / 'STATUS.md').write_text('''# 实施状态

更新：2026-09-21。**进行中，未达到最终交付门槛。**

## 当前检查点

[工作模型](scene/Fallingwater_working.blend)与[冻结第09版](scene/Fallingwater_iteration09.blend)字节相同：44,414,422字节，SHA256 `489b05e403aa9d02c3568a8e3813a24235ee5b7e782df4d1f149b3ff6673e331`。新后台完整构建130.433秒、退出0；60个空间记录、23,385对象、9,566网格、1,394,192独立网格顶点。空间含露台、楼梯、设备与基础检查区，不等于60间居住房间。之前检查点及失败证据保留。

09合入主屋09/09b地板、天花与石柱转角修复，以及8张床的10只柔软枕头。此前局部候选图已实看；完整09又渲染并实际打开5张960×540、48样本图，修复保留，但Loggia、Master部分墙脚缝、通用家具与摄影质量仍需改进。见[整合决策](qa/iteration09-integration-decisions.md)、[完整09焦点图](qa/iteration09-focus-review.md)。新楼梯、灌木、水流与预览灯光试验尚未安装进这个冻结版本。

## 实际验收

| 项目 | 当前证据与限制 |
|---|---|
| 环境与保存 | 本机Blender5.2.1 LTS；CPU/Cycles和EEVEE可用。HIP全场景曾崩溃，保留日志，当前诊断用CPU |
| 构建与来源 | 23个冻结输入不变；main_house.json由build重新导出，独立进程生成字节与新输出完全一致。第一次误将生成文件当不可变输入的失败记录保留 |
| 尺寸 | 最新44行全部关联09场景SHA；23数值匹配，其中15标准通过、8来源/端点精度受限；21待测留空。悬挑与开口缺项，场地仅泳池部分覆盖，GEO-02仍INCOMPLETE。外梯2′5″锚点3站最大误差18.50mm，小于20mm |
| 逐房双图 | 第07版120张全部独立实看：81可读、29有限、10构图失败，16另有界面异常。08替换7个机位；09重点5图已实看。尚未有完整最终逐房摄影通过 |
| 保存机位 | 完整09独立读回120/120位置、旋转、镜头、shift和曝光匹配；120/120几何通过、3,840射线。配置SHA f011c9462431e12137a49d3829a85586da0804a5a934086e03d7143c7d5dc1d0；几何不等于视觉通过 |
| 真实路线 | 完整09重新计算58连接PASS/2FAIL，含50步行与8检查连接；ADJ041/054仍被墙/平台接入阻断。7,584整数帧全PASS不能抵销连接失败；未保存checked09。07的通过检查点保留 |
| 照片匹配 | 六个可靠匹配视点未完成。此前88视点外露带竖高与整体残差的局部改进不等于GEO-07通过 |
| 流水 | 09真实床静水24帧动态体积稳定、头高中位漂移1.43微米；36帧冲击实际流量比原C目标高70.44%，仍FAIL。根已实际看1/18/36帧，人工矩形池边不能合入自然溪流。更大真实岸域正在设计，没有最终5–10秒成品 |
| 岸坡与植被 | 08真实路边坡几何已保留；灰色染色与扫描落叶材质均因实图失败未采用。16株宽叶弯枝候选三图与三张基线实看后仅接受局部形体；完整09独立应用复验中，冻结09未变。光滑裸坡和均匀疏植仍FAIL |
| 4K与影片 | 仅旧场景4K耗时基准及短诊断片；12张最终4K、2–4分钟1080p主片和剩余空间补充片尚未输出 |
| 实时预览 | 弱非相机环境光＋单窗AREA试验改善室内颜色，但硬天花分界与颗粒仍PARTIAL；局部Cycles恢复复开通过，未全场采用 |
| GUI与帧率 | Windows先前锁屏，尚无用户解锁确认，未继续操作。实际自由漫游与4组60秒帧时间验收未运行 |
| 迁移 | 04静态纹理移动目录/失效外路径/独立复开与重渲通过；最终模型、脚本与流水缓存整体包未验收 |

## 正在修正

- 客房完整图纸显示南走道有两组向西下行台阶，服务梯南端可见地线约低于MAIN基准1.15m，现有整片平地及单跑楼梯方向不成立。已选明确C方案：南到达面−1.18m、下8+8级、上8+5级、南走道3+4级；北门与印刷层高不变。实际独立候选制作中，尚非几何或导航PASS。[源图](qa/guest-level-context09-review.md)、[数值设计](qa/guest-circulation10-design.md)。
- 主屋Loggia及Master剩余明暗条带按原图与真实面逐点定位；真实门洞/楼梯不可用填墙掩盖。
- 新取得并实际打开Columbia桥上全景片与Dan Hyde2005作者照片，支持主桥连续涂饰混凝土护墙与两岸石墙收口；旧连续石砌护栏须修。照片仅作参考，不进入公开模型素材包。
- 流水扩大到真实池岸与下游边界后先做有预算的小样；旧70.44%流量偏差与全部失败缓存保留。

## 证据入口

- [打开与操作](START_HERE.md)、[构建日志](qa/build-iteration09.log)、[冻结记录](qa/integration09-freeze.json)。
- [09完整机位与路线](qa/tour-path-iteration09-review.md)、[09保存机位](qa/camera09-validation-summary.json)。
- [最新尺寸实测](qa/dimensions-build-20260920-165955.json)、[独立尺寸/生成来源复查](qa/camera09-dimension-freeze-crosscheck.md)。
- [09真实床静水](qa/water09-realbed24-control-review.md)、[冲击物理与流量](qa/water09-impact36-review.md)、[3帧实际图像](qa/water09-root-visual.md)。
- [灌木三图对照](qa/shrub08-root-visual.md)、[软枕](qa/softgoods09-root-visual.md)、[结构09b](qa/structure09b-root-visual.md)。
- [07逐房120张](qa/camera07-room-review.md)、[08整合历史](qa/iteration08-integration-decisions.md)、[04迁移证据](qa/portability-iteration04-review.md)。
- [缺陷清单](qa/issues.csv)、[参考库](reference_manifest.csv)、[素材许可](assets/LICENSES.md)。

## GitHub发布

用户已授权完成后创建公开GitHub仓库并上传模型与制作文件，无需再次询问。仍须先完成最终质量、导航、尺寸/照片匹配、实时性能、4K/影片与整体迁移验收。已只读确认连接器账号xiang949876499；本机CLI旧凭据失效，未改凭据。默认仓库名fallingwater-blender-reconstruction。尚未创建仓库或上传，计划与分包清单见[publication-plan](delivery/publication-plan.md)。
''', encoding='utf-8')

p = qa / 'issues.csv'
with p.open(encoding='utf-8-sig', newline='') as handle:
    reader = csv.DictReader(handle)
    fields = reader.fieldnames
    rows = list(reader)
updates = {
 'FW-001': ('iteration09','FAIL','Fresh09 graph:58 PASS and2 FAIL (ADJ041/054);7584 film-frame passes do not repair missing true connections. Guest multi-flight/source-level candidate10 in progress.','project/qa/tour-path-iteration09-review.md'),
 'FW-002': ('iteration09','INCOMPLETE','Full09 saved120 poses and geometry PASS;5 integrated focus images actually viewed. Existing07 full-room visual deficits and final complementary photography remain.','project/qa/iteration09-focus-review.md'),
 'FW-003': ('water09-impact36','FAIL','True-bed09 static control stable. Impact36 actual flow .173354596m3/s exceeds former authored .101709741 by70.44%; raw1/18/36 images show artificial closed pool boundaries. No candidate installed.','project/qa/water09-root-visual.md'),
 'FW-009': ('iteration09','PASS','Latest44 measured-ledger rows all match frozen09 SHA;23 numeric matches and21 unmeasured blanks. Independent read-only16-assertion data/freeze review agrees. Overall source/category gate remains separate.','project/qa/camera09-dimension-freeze-crosscheck.md'),
 'FW-013': ('iteration09','NOT_RUN','Fresh09 all7584 integer frames pass, graph58/60 only; no checked09 saved. Final2-4minute1080p film and room supplements NOT_RUN.','project/qa/tour-path-iteration09-review.md'),
 'FW-015': ('iteration09','INCOMPLETE','44 current09 rows:23 numeric agreements;15 nominal-standard passes,8 source/endpoint limits,21 unmeasured. Cantilever/opening categories missing; site pool-only.','project/qa/dimensions-build-20260920-165955.json'),
 'FW-016': ('iteration09;shrub08-candidate','INCOMPLETE','Corev3 frozen; bank08 geometry integrated. Scanned ground failed;16-shrub three-camera comparison accepts local morphology only, not integrated into09. Smooth pale banks and sparse regular vegetation still FAIL.','project/qa/shrub08-root-visual.md'),
 'FW-020': ('iteration09','INCOMPLETE','Source retaining wall and2ft5in finished-face width preserved in09; navigation still fails. Complete-sheet evidence requires circulation-level/stair redesign, independent candidate10 pending.','project/qa/guest-circulation10-design.md'),
 'FW-021': ('iteration09','INCOMPLETE','09/09b interface repairs integrated and5 actual focus images reviewed. Remaining Loggia/Master strips undergoing actual-face diagnosis; bright staircase seen through real Master opening is not automatically a missing wall.','project/qa/iteration09-focus-review.md'),
}
for row in rows:
    if row['issue_id'] in updates:
        version, result, description, evidence = updates[row['issue_id']]
        row.update(scene_version=version,result=result,description=description,evidence_path=evidence)
if not any(row['issue_id']=='FW-022' for row in rows):
    rows.append(dict(zip(fields, ['FW-022','P1','GEO-01;GEO-05','iteration09','Guest south circulation and west Lounge glazing','OPEN','FAIL','Complete source sheets contradict flat south terrace and old single stair runs; Lounge west corner is drawn glazing, current model door identity incorrect. SelectedC circulation10 requires actual mesh, source opening and full-route validation.','project/qa/guest-circulation10-design.md','Source-bound six flights, north doors, real east room access and lowered connector with unchanged thresholds; full adjacency and film-frame rerun'])))
with p.open('w', encoding='utf-8', newline='') as handle:
    writer=csv.DictWriter(handle,fieldnames=fields)
    writer.writeheader(); writer.writerows(rows)

p = qa / 'iteration09-integration-decisions.md'
text = p.read_text(encoding='utf-8')
text = text.replace('Full09 connection and7,584-frame checks are running in a separate process. The known08 guest-approach failures are not presumed repaired by unrelated main-house changes.', 'Full09 independent checks finished:58/60 connections PASS,2 FAIL (ADJ041/054), and7,584/7,584 integer frames PASS. No checked09 scene was saved. All production files remain unchanged. See `tour-path-iteration09-review.md`. Five integrated focus images have since been rendered and actually opened; see `iteration09-focus-review.md`.')
text = text.replace('A16-plant branch/leaf shape candidate preserves root positions, counts and original materials, and is awaiting root image review.', 'A16-plant branch/leaf shape candidate preserves root positions, counts and original materials. Root and worker actually opened three candidate and three baseline images and accept local morphology only; the full environment still fails. See `shrub08-root-visual.md`.')
p.write_text(text,encoding='utf-8')
print(json.dumps({'status':'DOCUMENTS_RECONCILED','issues':len(rows),'scene_sha256':expected}))
