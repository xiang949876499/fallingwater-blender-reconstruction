# 第08轮采用的7个诊断视角

后续完整08的120位几何与保存参数已独立重新检查，见 [完整08报告](camera08-review.md)。以下保留采用决策当时的冻结07图像来源与视觉限制，不将历史实图改称08实图。

**独立完整120相机配置已生成：采用7个新视角，另外113个保留07原值。生产data文件未改。**

[完整配置](D:/zx/test/project/qa/camera08-accepted-settings.json) SHA256：`f011c9462431e12137a49d3829a85586da0804a5a934086e03d7143c7d5dc1d0`。

本子集实际7张图全部逐张打开并与07旧图比较：3个R（可读诊断）、4个L（有限构图）。L没有因被采用而升级为R。所有采用仅用于诊断，摄影质量均未通过。

| 相机 | 分类 | 采用依据与保留限制 | 图像SHA256 |
|---|---|---|---|
| [CAM_GUEST_L1_BOILER_B](D:/zx/test/project/renders/previews/iteration08-cameras/CAM_GUEST_L1_BOILER_B.png) | L — LIMITED_COMPOSITION | 旧图为几乎占满画幅的锅炉平箱正面；新图能读取烟管、锅炉、右侧压力罐及左侧入口之间的关系。 锅炉下部占画面主体，烟管顶端及压力罐右侧仍出框；属于设备关系近景，不能作为完整锅炉房摄影。 | `840eca0369d643d430d26c05b5b5968f9db75dce1858cd014b4b6297b308a327` |
| [CAM_MAIN_B_PLUNGE_B](D:/zx/test/project/renders/previews/iteration08-cameras/CAM_MAIN_B_PLUNGE_B.png) | R — READABLE_DIAGNOSTIC | 旧图只读到狭长水面与近墙；新图读到池身、池梯、石墙包围及远侧出口关系。 水面仍深暗，右侧近梯占较大面积；池水真实感、远处结构和通行另验。 | `ade1f619f35cecaf2a845d777947f6eb9a433bb78a59d67e72165a6028e2a7ba` |
| [CAM_MAIN_L2_CLOSET_G_A](D:/zx/test/project/renders/previews/iteration08-cameras/CAM_MAIN_L2_CLOSET_G_A.png) | L — LIMITED_COMPOSITION | 旧图被侧柜/窄通道阻挡；新图能读到柜门、上沿把手及右侧窗/外门的相邻关系。 柜顶、柜底出框，下部被床头遮住；开门后的内收纳没有展示，室外偏亮。 | `4b5770715850c9a5f8d7ae87b76ddac92b4706cc1318636a484e3f17a60d0359` |
| [CAM_MAIN_L2_CLOSET_G_B](D:/zx/test/project/renders/previews/iteration08-cameras/CAM_MAIN_L2_CLOSET_G_B.png) | L — LIMITED_COMPOSITION | 旧图主要为外窗及阳台；新图朝实际柜门，并在左缘看到相邻浴室与开口。 木柜板仍占大部分画幅，上下出框、把手不可读，左侧浴室只是窄片。与A相较是有限的反向邻接关系。 | `90eb735c06b070947d30be795005dfc0a422f51c79a2b90d772847ba98559eda` |
| [CAM_MAIN_L3_ALCOVE_B](D:/zx/test/project/renders/previews/iteration08-cameras/CAM_MAIN_L3_ALCOVE_B.png) | R — READABLE_DIAGNOSTIC | 旧图朝木隔墙及外窗；新图清楚展示床垫、枕头、床头柜与侧窗关系。 床脚/底架仍裁切，白床品局部偏亮且材质简单；这是床龛用途诊断，不是完整卧室摄影。 | `22584df401f8d5cebfc1068a1d5304f794f117857eca659ba030e1aa46e9b8db` |
| [CAM_MAIN_L3_BATH_A](D:/zx/test/project/renders/previews/iteration08-cameras/CAM_MAIN_L3_BATH_A.png) | L — LIMITED_COMPOSITION | 旧图被洗手盆镜背挡住；新图马桶座圈、便器和靠墙位置清楚，与已实看的旧B洗手盆视角互补。 水箱顶部略出框、相机下俯，不能看到完整小浴室；墙地边缘和装配形状另验。 | `57838b056dda8c2b1c0afeed7763906bc7810af00ce936c7a25ee29b723422ca` |
| [CAM_MAIN_L3_STAIR_A](D:/zx/test/project/renders/previews/iteration08-cameras/CAM_MAIN_L3_STAIR_A.png) | R — READABLE_DIAGNOSTIC | 旧图与L2 Stair A几乎共眼位；新图以较明显侧角展示梯段和下层蓝石平台、玻璃门窗关系，减少重复。 栏墙/门框仍在右前景，下方深色开口不能凭本图判定修复或通行。 | `63648861e781e816753c0f51b780508cbce5f374e57cb627d162aabd67347959` |

## 本轮保持原值的4位

Servant A/B、Coat B、Closet M B均保留07原配置，其原构图FAIL不撤销。Servant B的新图只增加上沿墙面/窗口，没有取得足够覆盖增益，本轮不再搜索。

## 仅记录下一步的三项有界建议

- **CAM_MAIN_L1_COAT_B**：最多一次入口侧后退的候选检查，以柜体轮廓和真实开口为目标；不提高曝光掩饰缺失细节。若固定柜确为无细节块，转交家具记录，不继续搜相机。
- **CAM_MAIN_L1_SERVANT_A**：最多一次南侧实际入口/可站立边缘的后退候选，争取座席、桌、柜三者关系；保留另一机位的独立方向，不复制A/B。
- **CAM_MAIN_L2_CLOSET_M_B**：最多一次沿真实卧室床侧过道的后退/侧向候选，目标是柜体至少两条外轮廓和开口；不移动床/柜或站在床上。无安全可读位置则保留F并记录固定布置限制。

本轮不继续试渲，没有为这三项生成新姿态。

## 来源与重新验证要求

实际样图源为冻结07场景，SHA256 `bf50530009e4a93315915815473188c91d891272ef2d8e9e0169b704bd2e2f16`，不是尚待整合的完整08。全部7位的眼点、target、28mm焦距、shift与曝光，均精确取自已渲染的候选配置；11候选在07真实支撑/身体射线上通过，不表示新08也已通过。

原生产配置SHA256 `4def78dcbae91f3292562f41796adec71c4680b64e04301f051fdc1833ce8666`；候选源SHA256 `214ae74cd82054bfb8c92a173fdbde0cc6a3ebbfd5ac9b1b42343338703b6c30`。读回确认完整120个名字、7个被授权替换、113项对象内容完全不变。新增视觉证据绑定实际图像哈希，final_quality_accepted保持false。

完整08合入后必须重新检查120位实际支持面、身体净空及保存相机参数，并看受结构变化影响的图。旧图的已证实墙脚/石缝不能因为新机位不再拍到就自动结案。

[完整11图独立复核](D:/zx/test/project/qa/camera08-candidate-visual-review.md)；[120文件及7图清单](D:/zx/test/project/qa/camera08-accepted-settings-manifest.json)。
