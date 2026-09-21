# 第08b轮：六类有限结构异常

**已完成局部几何修正并保存、复开验证。六个原机位仍需实际渲染验收；本轮没有改变相机来避开缺陷，也没有调整家具或照明。**

候选：[Fallingwater_structure_candidate08b.blend](D:/zx/test/project/scene/Fallingwater_structure_candidate08b.blend)，SHA-256 `77ecfeaa879a49432d727844c299ea618b021ec08015149717bf88f0559ec3cb`。

对应稳定源码 `scripts/main_house.py` SHA-256：`1cebf586ca6913d451a9d01bad7f0d64acb1331d8a96f68091ba7e41075a3ef6`。修改前源码为 `structure08b-main-house-before.py`。输入是已保存的08地板/石芯候选，SHA-256 `c78cab9c1d1d3341c72ac926da1abe931902f4c0381e49e956c6c814c930ddc7`，该文件保留未覆盖。冻结07和已验收的07导览场景、路线JSON同样没有修改。

## 原图、精确像素与原因

已实际打开07的Servant_B、Loggia_A、Terrace_N_B、Closet_G_A、L2_GUEST_A、L2_MASTER_A，以及 `camera07-room-anomaly-pixels.json` 所列位置。独立射线记录在 [structure08b-probe.json](D:/zx/test/project/qa/structure08b-probe.json)。这些被检查的黑色表面都属于建筑网格，没有先碰到家具，故没有向家具模块提交无依据的修改。

| 区域 | 证据 | 有界修正 |
|---|---|---|
| Servant_B西墙脚绿带 | 三点首先穿到地形；统计地板西边比现有墙内侧向东约73mm | 地板延至墙内侧并搭接5mm，保留北部凹凸轮廓 |
| Loggia_A黑带 | (300,280)、(315,278)、(233,290)均有Loggia及entry_loggia门槛同高面层 | 门槛仅保留Entry与Loggia之间的连接，北端斜边也共享边界 |
| Terrace_N_B首阶黑带 | 三点同时有Terrace_N及arc_lower_landing面层 | 移除完全重复的下平台板/面层，原露台板及全部弧梯保持不变 |
| Closet_G_A顶角黑斑 | 三点为Guest天花与guest_corridor_ceiling重复 | 走廊天花在Guest边界处退至共享边 |
| L2_GUEST_A柜顶缝 | 两点是上述重叠；(138,46)越过天花边缝，碰到Z5.03415的已有上层板底 | 调整衣柜天花，使其与走廊、Guest天花相接，填闭已有楼板下的局部天花缝 |
| L2_MASTER_A柜顶黑条 | 三点有Master及Closet_M同高天花 | Closet_M只保留Master天花尚未覆盖的北段 |

20个地面/天花采样包括18个异常点及2个正向参照；修正后每点均只命中一个正确楼层表面。

## 保留的真实窄开口

Servant_B的(294,25)、(294,44)与墙脚漏板不同。主04石墩和北侧岩沿之间存在薄线表示的窄窗/开口，见 [源图与地板边界](D:/zx/test/project/qa/structure08b-servant-overlay.png)。它不是给石墙补一个实心短连接的依据。两条控制射线在候选中仍穿到原地形位置；未加墙、关窗或改岩沿。具体窗构造与描图精度继续是C级，不据本轮检查声明整个开口已达照片级。

本轮只改Servant板及面层西侧边界。新西边X−7.5978m，比原墙内侧X−7.5928m搭接5mm；北端接回原(183.5,228)，没有向楼梯、岩外空区扩展。

## 其余共享边界

主04/05裁切和下列叠图全部已实际打开：

- [Entry—Loggia连接](D:/zx/test/project/qa/structure08b-loggia-overlay.png)：原门槛矩形内裁去已被房间覆盖的部分，保留原北端斜角，不扩大原门槛范围。
- [弧梯下平台](D:/zx/test/project/qa/structure08b-landing-overlay.png)：原重复矩形px468..474、py142..176完全落在现有Terrace_N板/面层内。删除的是第二份相同水平面，不是删除承托平台或改动首阶。
- [衣柜及走廊天花](D:/zx/test/project/qa/structure08b-ceiling-overlay.png)：Closet_M只保留px337..366、py308..312；其余位置由现有Master天花提供。Closet_G改为px484..534、py328..342，接到既有走廊及Guest天花。走廊西侧px468..469的原窄条保持，未用大矩形封楼梯或室外开口。

Guest_A的局部天花缝上方原本已存在实体楼板，射线直接测得其板底Z5.03415；本轮增加的是相同Z5.0的室内天花接缝，不是关闭一个通天采光口。周边原走廊天花外轮廓没有扩张。

所有地面/天花标高不变。新增 `physical_ceiling_source_polygon` 与世界坐标字段保留统计房间轮廓的原含义；门槛增加多边形构造边界以处理斜角。原门、窗、楼梯、家具与灯具均不动。

## 保存与回归

[完整检查JSON](D:/zx/test/project/qa/structure08b-candidate-check.json)记录旧顶点、新源轮廓及所有采样。7个对象改网格，2个重复平台对象删除；其他对象几何、变换、材质指纹一致。保存复开后，源码构造函数重建世界顶点误差0m。

| 检查 | 结果 |
|---|---|
| 20个地面/天花像素 | 唯一正确表面 |
| Servant窄开口控制2点 | 保持原外部命中 |
| 修改天花范围789个采样 | 每点只存在一层Z5.0天花 |
| 原重复平台范围455点 | 保留的Terrace_N面层完整承托，Z2.8668 |
| Servant墙脚及Loggia连接508点 | 正确连续地面，无缺失 |
| 受影响原路线地面89点 | 无支承缺失或高度跳跃 |
| 全部相机及主/补路线8,088身体中心 | 未引入0.18m范围内碰撞 |

在新后台Blender5.2.1、固定4线程完成，没有渲染或使用GPU。旧异常图、异常像素记录和探针JSON均保留。局部身体检查只验证本轮改动，不替代新版完整导览及视觉验收。

本阶段按已读取的 neat-freak 流程同步了交接报告与前一阶段的后续入口。根规则、总STATUS和发布状态由整合任务统一维护，未把阶段流水账写入规则文件。


后续记录：新图发现的剩余问题见 [08b只读复核](D:/zx/test/project/qa/structure08b-remaining-review.md)，其后有界修正见 [第09轮交接](D:/zx/test/project/qa/structure09-review.md)。本报告原采样通过不覆盖后续新像素，不能据此认定整个凉廊或主卧已通过。
