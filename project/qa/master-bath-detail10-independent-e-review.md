# 主浴室10e局部接受与保护确认

**结论：PASS_LOCAL_INTEGRATION_ACCEPTED。确认的22mm窗角竖缝已关闭；白帘局部材质改善可接受。允许整合这两项局部修复，房间整体照片级/全屋导航验收仍未通过。** 10d的失败证据保留于 [10d独立报告](D:/zx/test/project/qa/master-bath-detail10-independent-d-review.md)，其中MB10-D01可依据本轮证据关闭。

最终候选：[Fallingwater_master_bath_candidate10e.blend](D:/zx/test/project/scene/Fallingwater_master_bath_candidate10e.blend)，44,689,923字节，SHA-256 `180c16e5d1cc2e77e4377560c00aa7a49560545924c3c42b9af6060461e8baee`。读取的helper SHA `6d13723236de78c790a23f50a608d390d4744ec8e9a94a640bab412ec4b0e60e` 与root生成记录一致。独立检查只读取10d/10e保存场景，不执行helper；Blender 5.2.1 LTS新后台CPU4、无渲染、无保存，候选SHA前后不变。

| 检查 | 实际结果 |
|---|---|
| 原25条穿缝射线 | 25/25命中 `MASTER_BATH10_south_window_glass_0`，不再穿出 |
| 原10条控制射线 | 5命中真实共享 `south_window_mullion_0`，5命中调整后的首块玻璃；旧控制位置由立框变为玻璃符合本次窗格重算，不能错误要求对象名完全相同 |
| 实际角框 | 西窗末端重复框 `southwest_return_mullion_1` 仅此1个对象移除；南窗角框实际保留并与西窗共角，没有以删空实体假称闭合 |
| 角部相关实网格 | 区域筛选内13个窗构件均无开边、无非流形、体积为正；不把区域筛选数量称全场景实体总数 |
| 10d→10e对象差异 | 原23,424→现23,423；23,408个对象的几何/矩阵/材料槽/显示等保护签名不变；14个南窗构件重算，1个帘对象仅材料槽变化，1个重复角框移除；0新增对象、0越界变化 |
| 帘几何 | 网格签名完全不变，未移动/删帘改善通路 |
| 既有材质保护 | 10d已有56个材质的节点/链接/默认输入/色带均不变，包括全局 `FW_linen`；只新增 `FW_MasterBath_WhiteCurtain10` |
| 实际白帘材质 | 新本房材质使用反射与约0.38 Translucent混合；实际Principled发光强度0，无发光节点；没有将照片贴到帘面 |

射线使用与10d相同的X4.999/5.003/5.008/5.013/5.017 × Z3.75/4.0/4.4/4.8/4.95，以及两侧X4.988/5.028控制，从Y6.95沿−Y穿过窗平面；玻璃也计真实遮挡实体。35条全部保留命中对象、材料、世界位置及法线。仅看小样难以发现的旧空缝此次有实际实体证据关闭。

根据明确差异保护，墙、地面、淋浴35mm地台/倒角、门扇与把手、柜、WC、盆、灯具、镜体及其位置均与10d一致。因此本轮不重复已通过的241个平地路线站、54个分足承重接触、1458个摆动脚底点和162个踏台身体姿态；沿用10d相应局部证据，保留180mm身体半径、1950mm头高、4mm承重高度误差和法线Z≥0.9。整合后的新场景仍须重新做全连接/影片/机位测试，不能将局部继承当成整合结果。

## 两张同机位图的实际复核

已打开 [SOUTH](D:/zx/test/project/renders/previews/master-bath10e/CAM_MB10_SOUTH.png) 和 [ENTRY东北补位](D:/zx/test/project/renders/previews/master-bath10e/CAM_MB10_ENTRY.png)。白帘在SOUTH的冷蓝偏色明显减轻，褶面层次可读，ENTRY仍呈淡暖白；没有出现发光白板或丢材质。WC/柜/淋浴/盆与真实镜像的布局未见新的可见变化，南窗分格的轻微重排与角框修复一致。当前两图未完整展示角窗全部转折，几何闭合结论来自相同射线复验，不伪称图片展示了未入镜部分。

保留的视觉界限：帘褶仍高度规则，软木拼块/使用层次不够，柜木纹偏显著，ENTRY近帘遮挡仍大，窗外树叶仍有薄与糊的观感。照明改善不等于与2001原照片精确匹配；窗分格/镜侧边/灯位及材质反射参数仍是C解释。这次局部接受不能把整体“材料与微细节、自然环境、摄影可信度”提升到≥4或宣称4K成品。

两图均frame48、960×540、48samples、AgX、exposure0.8，root渲染设置不由本审查修改。SOUTH SHA `8b0731b5e6bb7b119ef7aa2344b8e51a11b7d7e9234100cca83c6b6e0a6050e0`；ENTRY SHA `af64956c441caf51451b89ffcff05bde9842819fae5a69b1133d93fd0ec47b04`。

证据：[独立检查脚本](D:/zx/test/project/qa/master-bath-detail10-independent-e-audit.py)、[全部35射线与差异保护](D:/zx/test/project/qa/master-bath-detail10-independent-e-audit.json)、[运行日志](D:/zx/test/project/qa/master-bath-detail10-independent-e-audit.log)。保护签名包含实际原网格、世界变换、曲线点/设置、材料槽、显隐/集合及相机/灯光基础值；这是明确属性集合的独立比对，不冒称两个.blend二进制相同或所有Blender内部属性的穷尽比较。

neat-freak范围内交接已在本报告收束：10b/10d报告保持历史状态，10e是这两项局部修复的新入口；未改生产模块、总STATUS、源报告、AGENTS或全局记忆。本轮也没有新建/改写生产路线或重复运行分足检查。
