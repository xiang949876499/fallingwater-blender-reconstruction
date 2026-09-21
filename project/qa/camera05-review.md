# Iteration05 相机冻结与复验

**120/120 GEOMETRY_ONLY_PASS；05 新构图视觉验收仍待实际渲染。** 04 的 120 张已看图记录继续保留，不能替代 05 新构图或新几何的验收。

冻结场景为 `scene/Fallingwater_iteration05.blend`，SHA256 `6bcfee7841c22e8e2b636352cfca79ae94968afb4235fc20cdc57e250ae046ff`。当前冻结相机参数为 [camera05-settings-frozen-v2.json](camera05-settings-frozen-v2.json)，SHA256 `34e4bc6b9ca8555ba57832b830c575658955da7fc9c947b9c5721dfede31bd9e`；`data/camera-settings-reviewed.json` 与此同字节。场景文件本身未重存；渲染必须显式加载该 JSON，下一次构建由 `camera_review.integrate` 接入。

先前的 `camera05-settings-frozen.json` 原样保留。v2 只将 Main B Bath A 的 `shift_y` 从 -0.44966 降到 -0.55 并补充证据说明，眼点、目标和其余 119 位不变；这修复了 05 自动重算覆盖此前人工镜头位移的问题。原 04/05 同机位图截掉部分马桶底，较低画幅仍需新图验证。

## 变更与验收范围

原 04 冻结点位在 05 上为 115 通过、5 失败，记录在 [原配置复验](camera05-original-verification.json)。Wine A 眼点距新墙约 61mm；LINK A/B 的旧支撑已不是实际上层地面；Guest Lounge B 的脚部碰新炉台；Guest Pool A 身体柱碰新砂岩石层。只修改机位，没有移动、隐藏或改变建筑、家具、树木。

最终与 04 冻结参数相比，22 个检查空间的 41 位改变了位置、朝向或镜头位移。其余点位保留，包括已实际可读的 Main Hatch B、Guest Stair Hall B 与 Guest Pool B。20 个空间的语义构图使用实际洁具、家具或指定梯段见证点；LINK 两位单独校验新平台与外弧梯，Pool A 仅作局部干地坪修正。

| 关键修正 | 证据和限制 |
|---|---|
| Main / Guest 小浴室 | 水平镜头配负 `shift_y` 纳入低处洁具；选择互补目标。不能仅因目标射线可见便称完整洁具构图通过。 |
| Main Servant | 限制眼点位于真实长椅正面，避免 04 小样中椅背占满中心。新图仍待查看。 |
| 楼梯 | 以标称梯段实际踏步作目标；拒绝用场地下层地形作楼梯支撑。主梯和客地下梯采用不同高程的安全相邻平台，不能解释为两个点均在房间内部。 |
| Guest Lounge | A 的射线覆盖新壁炉及长凳、书架、桌、格栅，B 离开新增炉台碰撞点；新图仍待查看。 |
| Main L3 LINK | A `[5.82688,23.99058,6.88635]` 与 B `[8.34415,23.9956,6.88635]` 均在新上层平台多边形内，支撑为 `MAIN_L3_LINK_finish`。A 覆盖外弧梯 8 个踏步见证点，B 中心射线到真实连接梯 `GUEST_CONNECTOR_step_001`。未把旧南侧雨篷当楼板。 |
| Guest Pool A | 从旧点向西移 0.15m，支撑为干燥 `GUEST_L1_MAIN_FLOOR`，原目标与 B 保留。新点在地坪边缘轻微倒角上，中心支撑比选点存值低 2.93mm，身体、四脚和眼点均通过。 |

语义搜索证据：[20 空间构图记录](camera05-composition-supplement-geometry.json)、[最后三个机位](camera05-residual-geometry.json)。A/B 机位有不同位置不等于画面覆盖互补，仍需实图确认。

## 独立复验

最终 v2 冻结副本在独立 Blender 后台 CPU4 进程检查，实际求值网格为 9,696 对象、949,419 顶点、1,015,619 面，3,840 条复验射线。120 机位全部支撑与 1.75m 身高、15cm 半径轴向身体柱、四周脚部和六方向眼点测试通过。报告：[camera05-frozen-v2-verification.json](camera05-frozen-v2-verification.json)；运行日志：[camera05-frozen-v2-verification.log](camera05-frozen-v2-verification.log)。

该房间几何索引排除植被，不能证明外景树枝无遮挡。旧 15 条构图射线未包含镜头位移，只作近表面诊断；新的有位移构图使用另列的实际目标投影见证点，最终仍需看真实图片。

有 **15 个点在当前标称空间多边形外**。浴室/衣帽间门外、泳池干岸、连接地坪和相邻楼梯平台均可能是检查位，但并未因此接受为房间内部占用或连续通行。逐点位置、实际支撑、说明和未验收状态见 [冻结清单](camera05-freeze-manifest.json)。Guest Room A 位于修订后的多边形西界外 16.406mm，修正了旧的 `outside_room_polygon=False` 标记，眼点没有改变。Main Coat B 的支撑对象名从门槛变为衣帽间铺面，高程相同。

## 真实图像与曝光证据

整合者实际查看的 05 焦点图、20 格曝光联系表和局部地坪修复结论见 [iteration05-focus-review.md](iteration05-focus-review.md)。本配置采用 Main B Bath A/B +1.6、Main Living B +2.4、Guest Lounge A +2.8；新 Lounge A 朝向已改变，因此 +2.8 仅沿用诊断曝光。其余曝光仍为诊断值，封闭浴室的新灯具尚需全套图确认。

展示相机独立于这 120 位：`qa/camera04-showcase-near-settings.json` 中 Guest Pool +0.8 已有 05 实图可读证据；Guest Overview 在 04 实图中仍有枝叶遮挡下部翼楼，维持 LIMITED，不算无遮挡总览通过。

04 完整实际看图台账为 57 张诊断构图可读、22 张有限可读、28 张构图失败、13 张照明失败，见 [camera04-visual-ledger.md](camera04-visual-ledger.md)。本轮未生成新 120 张图，没有关闭所有衣柜、地下影音室及其他照明/构图问题，更未宣布照片级、4K、导航或最终交付通过。
