# Iteration06 相机检查

源场景 `scene/Fallingwater_iteration06.blend`，SHA256 `172b76340d1224a2b98f415b21042d19ad7fba4d849543d7156beb17e5fcf055`。初始参数为 05-v2，SHA256 `34e4bc6b9ca8555ba57832b830c575658955da7fc9c947b9c5721dfede31bd9e`。本轮没有修改模型几何或启动渲染。

**06阶段结论：修正候选 120/120 点位几何通过；实际新图未整体验收。** 当时 root 要求生产参数保持 05-v2，等待独立原图/屏风柜体布置结论，没有把候选复制进 `data/camera-settings-reviewed.json`。随后07e已采用新的座席侧A及其余修正，当前状态见 [07e冻结交接](camera07e-final-review.md)。本报告保留的06初验2个失败不能与后续候选通过混淆。

## 初验与真实图像

同一套 120 位在 05 和 06 分别建立真实求值网格、身体/脚部/眼点射线与含镜头位移的取景探针。05 新采样只是差异基线，没有继承其通过结论。06 网格含 9,683 对象、952,728 顶点、1,020,405 面；排除植被。06 初验 118 通过、2 失败，共 11,999 条含语义和构图的射线。

| 原机位 | 失败证据 | 候选修正 |
|---|---|---|
| Main B Plunge A | 原桥北道路已经移走，存储地坪附近无支撑 | 改从真正的上层 Loggia 干地坪观察原泳池目标；这不是泳池内部站位 |
| Main L1 Loggia A | 眼点中心仍落真实 finish，但一只脚在新地形移走后失去支撑 | 从东端狭窄区域移到实际干平台，保留原目标 |

初验记录：[camera06-full-check.json](camera06-full-check.json)。原现场参数集成无遗漏：[camera06-embedded-settings-check.json](camera06-embedded-settings-check.json) 中 120 个保存相机的位置、方向、焦距和 `shift_y` 均与 v2 相符。

相机代理实际打开了 root 输出的 06 Lounge A/B 960×540 图。A 近左侧石柱/窗边占前景，桌、屏风与书架可辨，完整炉口缺失；B 的近处木屏栏条占据大部画幅，炉口仍缺失。两张均为 **FRAMING_FAIL**，记录原 PNG 哈希的 [台账](camera06-lounge-visual-findings.json) 保留。

旧 `GUEST_FIREPLACE` 见证点把外侧石体也计入，5 个可见点不能证明炉膛可见。此次采用实际 hood/hearth 的东、南炉口矩形、完整投影面积和 7×7 口前遮挡采样；不再拿石体见证点作为炉膛证据。规则网格可能遗漏细栏条，所有比例均为采样证据，绝不替代实图。

## 新构图候选

[四位候选](camera06-repair-candidates.json) 与 [完整 120 合并参数](camera06-repair-merged.json) 包含两处支撑修正及 Lounge A/B；[候选证据](camera06-repair-geometry.json) 记录每条炉口采样和真实命中物体。

- Lounge A：`[7.90167,39.97148,10.0002]`，目标 `[4.4562,39.91788,10.0002]`。完整 hood/hearth 的投影能进入画幅；炉口面积为画幅 5.08%，但只有 38/49 口前采样清空，其余命中现存屏风底柜与末端栏条。**明确 LIMITED；完整无遮挡炉口要求仍未通过。**
- Lounge B：`[5.46639,37.30034,10.0002]`，目标 `[9.73679,38.03706,10.0002]`。换到屏风东南侧观察窗、长凳、桌和书架；实际画面仍待查看，采样未命中不能解释为绝对无遮挡。
- 第三个独立炉膛细部：`[5.32,39.96,10.0002]`，目标 `[4.4562,39.91788,9.04]`。完整东侧炉口投影占画幅 27.29%，49/49 口前采样清空，43/49 延长射线落到真实炉床或内衬，另 6 条命中周边石层/客楼主层地坪。它是细部候选，不能替代两张房间视图。

第三细部使用 [camera06-firebox-detail-settings.json](camera06-firebox-detail-settings.json)，临时复用相机名 `CAM_GUEST_L1_LOUNGE_A`。渲染须放独立输出目录，不能覆盖房间 A 或计为另一间房。没有移动或隐藏屏风、石柱及建筑来制造无遮挡结果。

## 复渲队列

[camera06-rerender-queue.md](camera06-rerender-queue.md) 与 [完整 JSON](camera06-rerender-queue.json) 明确列出 80 个房间机位需要复渲：旧 41 个待看图新构图、28 位实测画幅首命中变化、34 位客楼深檐/真开孔照明复核及位置失败，集合有重叠。另 20 位只命中其他部分变化的同一网格对象，局部射线没有变化，列为上下文复查，不夸称实质画幅变化。

展示相机 Guest Pool、Guest Overview、Hero、Upstream 独立于这 120 位，需要全场景及植被实图复核。未触发稀疏差异的其余机位也不等于视觉通过。

当前是候选与局部 QA 阶段。全部新图、最终照片级、完整空间覆盖与连续导航均未由本检查接受。生产参数的更新及最后几何状态以随后冻结清单为准；原 05-v2 与 06 首次失败报告保持不变。

## 候选复验与实际五图结论

四位变更合并后，在独立 CPU4 后台进程对完整 120 位重新执行 3,840 条点位射线，全部 **GEOMETRY_ONLY_PASS**。报告 [camera06-final-candidate-verification.json](camera06-final-candidate-verification.json)。不可变候选 [camera06-settings-candidate-frozen.json](camera06-settings-candidate-frozen.json) 的 SHA256 为 `8ca887363c8b6a7d3ccadc613576726c9acb261c83691499e95742fbae5bbba6`；[交接清单](camera06-candidate-manifest.json) 明确区分候选与未更新的生产参数。

相机代理实际打开了 root 新渲染的 4 张修正图及 1 张独立细部图，逐图哈希与结论在 [camera06-repair-visual-ledger.json](camera06-repair-visual-ledger.json)：

- **Lounge B：READABLE_DIAGNOSTIC。** 书架、椅子、窗下长凳和东侧空间可辨，旧近屏栏条遮挡消失。root 接受为一个房间视点，照明与家具质量另列 P1，最终视觉质量未接受。
- **Lounge A：FRAMING_AND_ILLUMINATION_FAIL。** 左侧大柜背面与右侧近石面形成局促通道，只留下中间暗凹洞；不能把全 hood 包围盒进入画幅当成完整房间摄影。
- **独立炉膛细部：FRAMING_AND_ILLUMINATION_FAIL。** 49/49 几何开口采样清空，实际图仍为屏风后黑方洞和局促下视构图。真实射线证据没有证明曝光与视觉可读性。
- **Loggia A：LIMITED_CIRCULATION_VIEW。** 支撑安全，但取景为近石面之间的通道/后部楼梯，存在明显深色横向地坪带。未证明完整 Loggia 构图，也未仅凭图片认定这些带是孔洞。
- **Plunge A：LIMITED_STAIR_POOL_EDGE。** 下视真实踏步清楚，水体仅占狭窄区域，不能视为完整泳池视图。

06阶段按 root 指令停止继续盲搜机位并保持生产 JSON。屏风/柜体是否偏离历史原图由独立复核负责；本报告只提供实际遮挡位置与图片，不凭候选失败自行移动家具或宣称来源错误。
