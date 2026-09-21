# 第08轮候选11图独立视觉复核

**建议采用7个诊断机位，保留旧B一位，另3位各最多一次有界再修。没有改生产配置。** 新图诊断标签为3个READABLE、4个LIMITED、4个FRAMING_FAIL，摄影质量通过数为0。采用的7位包括4个明确保留限制的LIMITED视角。

实际逐张打开11张新PNG及对应11张07旧PNG，均为640×360原尺寸，另打开旧L3 Bath B确认与新A互补。渲染记录11个唯一镜头、11次PASS、参数逐项等于候选JSON；这些PASS只说明文件渲染成功。

**实际几何仍是冻结07**（SHA256 `bf50530009e4a93315915815473188c91d891272ef2d8e9e0169b704bd2e2f16`），目录名iteration08-cameras代表下一轮相机候选，并非完整08场景验收。Cycles CPU、16 samples、AgX；新旧对比未靠提高曝光，11个曝光沿用原值。完整08的支持/身体射线和实图均为NOT_RUN。

## 采用与保留

- 采用诊断：Plunge B、Alcove B、Bath A、L3 Stair A。Bath A虽与洗手盆B互补，仍是小室有限WC视角。
- 带LIMITED采用：Guest Boiler B、Closet G A、Closet G B。保留近裁和上下文不足记录。
- 暂留旧值：Servant B。新图没有实质覆盖增益，旧FRAMING_FAIL不撤销。
- 最多一次有界再修：Servant A、Coat B、Closet M B。当前新值不建议合入；旧值只是临时记录，不代表通过。

## 每图结论

| 镜头 | 新图标签 / 建议 | 相对07及限制 |
|---|---|---|
| [CAM_GUEST_L1_BOILER_B](D:/zx/test/project/renders/previews/iteration08-cameras/CAM_GUEST_L1_BOILER_B.png) | LIMITED_COMPOSITION / ADOPT_LIMITED_DIAGNOSTIC | 旧图为几乎占满画幅的锅炉平箱正面；新图能读取烟管、锅炉、右侧压力罐及左侧入口之间的关系。 锅炉下部占画面主体，烟管顶端及压力罐右侧仍出框；属于设备关系近景，不能作为完整锅炉房摄影。 |
| [CAM_MAIN_B_PLUNGE_B](D:/zx/test/project/renders/previews/iteration08-cameras/CAM_MAIN_B_PLUNGE_B.png) | READABLE_DIAGNOSTIC / ADOPT_DIAGNOSTIC | 旧图只读到狭长水面与近墙；新图读到池身、池梯、石墙包围及远侧出口关系。 水面仍深暗，右侧近梯占较大面积；池水真实感、远处结构和通行另验。 |
| [CAM_MAIN_L1_COAT_B](D:/zx/test/project/renders/previews/iteration08-cameras/CAM_MAIN_L1_COAT_B.png) | FRAMING_FAIL / BOUNDED_RETRY | 目标由旧图楼梯/石墙改成储物柜，语义方向有改善。 巨大暗柜板几乎填满画面，门把手/内部分格不可读，储物空间深度及开口关系不足。不能由目标命中率判通过。 |
| [CAM_MAIN_L1_SERVANT_A](D:/zx/test/project/renders/previews/iteration08-cameras/CAM_MAIN_L1_SERVANT_A.png) | FRAMING_FAIL / BOUNDED_RETRY | 新图上移取景，显示更多沙发靠背和墙面。 沙发左侧及底部仍裁切，原图较完整的桌面在新图被底边裁去，书柜关系反而丢失；未获得实质房间覆盖改善。 |
| [CAM_MAIN_L1_SERVANT_B](D:/zx/test/project/renders/previews/iteration08-cameras/CAM_MAIN_L1_SERVANT_B.png) | FRAMING_FAIL / KEEP_OLD_PROVISIONAL | 新图显示较完整靠背上沿及少量上方窗口。 仍是紧贴沙发和书柜的局部；桌面比旧图更残缺，方向变化不足以解决原FRAMING_FAIL。 |
| [CAM_MAIN_L2_CLOSET_G_A](D:/zx/test/project/renders/previews/iteration08-cameras/CAM_MAIN_L2_CLOSET_G_A.png) | LIMITED_COMPOSITION / ADOPT_LIMITED_DIAGNOSTIC | 旧图被侧柜/窄通道阻挡；新图能读到柜门、上沿把手及右侧窗/外门的相邻关系。 柜顶、柜底出框，下部被床头遮住；开门后的内收纳没有展示，室外偏亮。 |
| [CAM_MAIN_L2_CLOSET_G_B](D:/zx/test/project/renders/previews/iteration08-cameras/CAM_MAIN_L2_CLOSET_G_B.png) | LIMITED_COMPOSITION / ADOPT_LIMITED_DIAGNOSTIC | 旧图主要为外窗及阳台；新图朝实际柜门，并在左缘看到相邻浴室与开口。 木柜板仍占大部分画幅，上下出框、把手不可读，左侧浴室只是窄片。与A相较是有限的反向邻接关系。 |
| [CAM_MAIN_L2_CLOSET_M_B](D:/zx/test/project/renders/previews/iteration08-cameras/CAM_MAIN_L2_CLOSET_M_B.png) | FRAMING_FAIL / BOUNDED_RETRY | 旧图为近石墙及透亮石缝；新图朝向真实柜体。 床头横板遮住柜下部，柜顶和两侧出框，缺少把手及开口轮廓；整体仍是难以辨别空间的木板近景。旧石缝未出镜不代表已修。 |
| [CAM_MAIN_L3_ALCOVE_B](D:/zx/test/project/renders/previews/iteration08-cameras/CAM_MAIN_L3_ALCOVE_B.png) | READABLE_DIAGNOSTIC / ADOPT_DIAGNOSTIC | 旧图朝木隔墙及外窗；新图清楚展示床垫、枕头、床头柜与侧窗关系。 床脚/底架仍裁切，白床品局部偏亮且材质简单；这是床龛用途诊断，不是完整卧室摄影。 |
| [CAM_MAIN_L3_BATH_A](D:/zx/test/project/renders/previews/iteration08-cameras/CAM_MAIN_L3_BATH_A.png) | LIMITED_COMPOSITION / ADOPT_DIAGNOSTIC | 旧图被洗手盆镜背挡住；新图马桶座圈、便器和靠墙位置清楚，与已实看的旧B洗手盆视角互补。 水箱顶部略出框、相机下俯，不能看到完整小浴室；墙地边缘和装配形状另验。 |
| [CAM_MAIN_L3_STAIR_A](D:/zx/test/project/renders/previews/iteration08-cameras/CAM_MAIN_L3_STAIR_A.png) | READABLE_DIAGNOSTIC / ADOPT_DIAGNOSTIC | 旧图与L2 Stair A几乎共眼位；新图以较明显侧角展示梯段和下层蓝石平台、玻璃门窗关系，减少重复。 栏墙/门框仍在右前景，下方深色开口不能凭本图判定修复或通行。 |

## 有界再修建议

- **CAM_MAIN_L1_COAT_B**：最多一次入口侧后退的候选检查，以柜体轮廓和真实开口为目标；不提高曝光掩饰缺失细节。若固定柜确为无细节块，转交家具记录，不继续搜相机。
- **CAM_MAIN_L1_SERVANT_A**：最多一次南侧实际入口/可站立边缘的后退候选，争取座席、桌、柜三者关系；保留另一机位的独立方向，不复制A/B。
- **CAM_MAIN_L2_CLOSET_M_B**：最多一次沿真实卧室床侧过道的后退/侧向候选，目标是柜体至少两条外轮廓和开口；不移动床/柜或站在床上。无安全可读位置则保留F并记录固定布置限制。

这三项只是下一步建议，未生成新姿态、未运行新的搜索、未发起渲染。若后退区域被真实家具或墙体占据，应记录限制，而不是隐藏固定家具或无限微调。Servant B暂时不追加搜索，以避免两个相机又变成重复画面。

## 结构问题与验收边界

本轮候选移动不会修复地板/墙脚、衣柜石缝和门槛黑条。新Closet M B不再朝石墙，所以旧图透亮石缝的已知问题仍保持；Servant B的新图仍可见细亮墙脚线。完整08正在另行修补，必须按新场景重新验证，不能把本轮视角改变当作结构修复证据。

曝光可辨不等于材质/照明真实。尤其Coat B的深暗面板需要把相机限制和柜体缺细节分开；单纯加曝光无法生成柜门结构。Plunge B能读池身，但池水质感没有通过。

生产120相机SHA256仍为 `4def78dcbae91f3292562f41796adec71c4680b64e04301f051fdc1833ce8666`。候选11项SHA256仍为 `214ae74cd82054bfb8c92a173fdbde0cc6a3ebbfd5ac9b1b42343338703b6c30`。支持检查是冻结07上的11/11 GEOMETRY_ONLY_PASS，不能升级为完整08或全120新视觉PASS。

## 图像哈希

| 新图 | SHA256 |
|---|---|
| CAM_GUEST_L1_BOILER_B | `840eca0369d643d430d26c05b5b5968f9db75dce1858cd014b4b6297b308a327` |
| CAM_MAIN_B_PLUNGE_B | `ade1f619f35cecaf2a845d777947f6eb9a433bb78a59d67e72165a6028e2a7ba` |
| CAM_MAIN_L1_COAT_B | `e3959618936f6c30695a62057d044f98ab5f3f49529f67516f5ea101fe4719f6` |
| CAM_MAIN_L1_SERVANT_A | `b43d612a0f9c879da206deec524a6b42579cd89a85dbb43209f1475ec6b0c671` |
| CAM_MAIN_L1_SERVANT_B | `15bfd9b6b6e1342a53a06910873bfc09114509809b54ee9c4762fa63113f79aa` |
| CAM_MAIN_L2_CLOSET_G_A | `4b5770715850c9a5f8d7ae87b76ddac92b4706cc1318636a484e3f17a60d0359` |
| CAM_MAIN_L2_CLOSET_G_B | `90eb735c06b070947d30be795005dfc0a422f51c79a2b90d772847ba98559eda` |
| CAM_MAIN_L2_CLOSET_M_B | `b91de8fe73afc2ce33bc614b80667b046461d77ca40bf46e124b23d7744eff88` |
| CAM_MAIN_L3_ALCOVE_B | `22584df401f8d5cebfc1068a1d5304f794f117857eca659ba030e1aa46e9b8db` |
| CAM_MAIN_L3_BATH_A | `57838b056dda8c2b1c0afeed7763906bc7810af00ce936c7a25ee29b723422ca` |
| CAM_MAIN_L3_STAIR_A | `63648861e781e816753c0f51b780508cbce5f374e57cb627d162aabd67347959` |

[完整逐图记录及新旧图哈希](D:/zx/test/project/qa/camera08-candidate-visual-ledger.json)。读回与参数源见 [候选读回记录](D:/zx/test/project/qa/camera08-candidate-readback.json)。旧120图问题清单保持在 [07视觉报告](D:/zx/test/project/qa/camera07-room-review.md)。
