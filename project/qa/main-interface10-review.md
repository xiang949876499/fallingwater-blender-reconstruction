# 10轮主屋接口候选交接

**三类确认接口已修，几何回归及独立复开通过；实际视觉仍待原机位复渲。主卧门口配准与Loggia踏步下横石芯仍未解决，不能称房间通过。**

候选 [Fallingwater_main_interface_candidate10c.blend](D:/zx/test/project/scene/Fallingwater_main_interface_candidate10c.blend)，44,361,115字节，SHA-256 `f85d813129fab175257f00be12c8d1116505b62d2ca1f9f8a6ffae57926e4a2a`。源为完整09 `489b05e403aa9d02c3568a8e3813a24235ee5b7e782df4d1f149b3ff6673e331`。仅新增独立 [main_interface10.py](D:/zx/test/project/scripts/main_interface10.py)，SHA `d4edfd0f879be1e49e6bf3868c7aba25f76bf43bb55fae53b1ac6cb40f43b900`，没有hook生产。原main_house仍 `d80558f5780773f8f3b2e8324dea32da616500958c83a70d7637a9e3fc180caf`。

| 接口 | 确认的缺陷与物理修复 |
|---|---|
| Loggia左柱脚 | 原(240,445)/(293,429)穿到地下石墩。主04原始TIFF的连续L石芯外脸约x535，旧实体止x531.866。把旧corner_core与east_1并为一闭合L体，仅向东延0.16682m至C描图x535.05；既有西内脸、原北端及y409南端保留，Z0.1..2.58不变。旧两体联合平面约2.097375→2.804275m²，净增约0.706900m²。删除的是已被统一L体包含的east_1物体，建筑体积没有删空。原leg的7mm分块边倒角不再保留。 |
| 东面石饰 | 原108块east_relief正向石饰随底材向东0.16682m，保留每块原网格、材料、旋转、Y/Z及相对嵌入/突出深度。内侧石饰不动。避免新石芯吞没原课程层次。 |
| Loggia远入口墙脚 | 原(536,340)/(552,350)直达地形。主04为连续入口石铺地。entry_loggia门槛板/面层向北贴Coat墙内面，5mm搭接进入墙体；东接现Loggia边。面积1.814337→1.959196m²；板顶0.1、面层顶0.122不变。 |
| Master左脚 | 原(170,465)/(140,472)穿到下方Hall板侧面。Closet_M板/面层向西接现石芯东面x332、向北接现木墙内面，保留5mm墙内搭接；东/南分别接现门槛和Master。用x367..368、y<307凹口避开既有hall_master门槛。面积0.322762→0.699675m²；面层顶2.8668不变。 |

这不是把整条源图墙轮廓都验收为A：西内脸和纵向端点继承09，整体L体内脸的源配准仍可能有偏差。本轮有证据改变的是东外脸及其地面接口。源身份明确，C描图仍约一JPEG像素不确定度；数字小数不是实测精度。

已实际打开 [main-interface10-main04-candidate-source.png](D:/zx/test/project/qa/main-interface10-main04-candidate-source.png)（主04原始TIFF局部，红石芯/绿铺地/蓝旧边）和 [main-interface10-main05-candidate-source.png](D:/zx/test/project/qa/main-interface10-main05-candidate-source.png)（主05，绿色新地板、蓝色旧板、门位置问题单独标记）。所有图片仅为源图或原09图的诊断标注，绝非10c渲染。最初两张09实际图、25点第一命中、多边形及包含命中点的三角面记录在 [main-interface10-probe.json](D:/zx/test/project/qa/main-interface10-probe.json)。

| 复验 | 实际结果 |
|---|---|
| 范围 | 5实体/地面网格修改，108同面石饰刚性平移，1冗余墙物体移除；无新增物体 |
| 非目标场景指纹 | 全部不变，包括其他建筑、家具、相机、灯光、材质槽、可见性 |
| 保存设置 | 原活动相机、帧、分辨率、引擎、曝光、采样和线程设置一致 |
| 唯一正确面层 | 10,727个原/新轮廓采样，0共面或缺面失败 |
| 既有机位/候选09路线身体点 | 8,040点，0新增0.18m近碰；不是全60连接/7,584帧再验收 |
| 邻近主楼踏步 | 90点支承和≥1.95m头部净空均通过 |
| 24门槛路径 | 744点，无新增地面支承丢失 |
| 所有113目标网格 | 闭合边各用2次，体积方向为正 |
| 独立新进程源码重建→10c复开 | 全对象指纹完全一致，目标世界顶点误差0m；未再次保存 |
| 石饰依附 | 108块原形/材料/旋转一致，相对底材偏移误差<2µm；108个正面中心射线均首先命中自身 |

25原像素中12点有预期实体变化：5点改命中统一石芯、4点改命中新门槛面层、3点改命中Closet面层。其中Loggia(335,416)原来虽有一层地板，其源身份落在应为石芯的范围内，最终改为石芯，不能继续当成必须保留地面命中的控制。既有正向地面(494,275)/(499,293)、主卧原明口四点、踏步下三点均保留原命中。

主卧明口不能直接封：原射线在现master门平面y303穿x375..388，后方命中地形或外螺旋梯。主05所画入口约x352..366，与当前367..390有配准偏移迹象；本轮不移动/关闭门、不修改路线来掩盖。Loggia踏步下原点位于主04南Coat/西横石芯边附近，尚不能证明为真实地下开口；其实体高度和连接身份未完成，原失败证据继续保留。

失败与方法修正均保留：第一候选10的44个Closet/门槛共面点见 `main-interface10-first-fail-*`，10b保留为漏做石饰跟随的中间候选；最终10c才同时满足地面与石饰依附检查。原固定像素(150,300)在墙外移后落到课程间石芯，不能要求它仍命中旧石块；错误的“同像素必须仍是course”断言脚本/日志保留，改用每块实际正面中心射线验证108块都未被底材吞没。

早期候选检查的 `surface_translations.after_translation` 在依赖图更新前读取，因此字段滞后；最终helper已将读数放到更新后。权威新进程 [main-interface10-final-reopen.json](D:/zx/test/project/qa/main-interface10-final-reopen.json) 给出实际保存位置和源码重建一致性；没有为了元数据修改重保存候选。完整回归见 [main-interface10-candidate-check.json](D:/zx/test/project/qa/main-interface10-candidate-check.json)。

整合者复渲目标为原 **CAM_MAIN_L1_LOGGIA_A / CAM_MAIN_L2_MASTER_A，frame48**。本轮无渲染、无GPU、无生产源码/CSV/路线或原09文件改动。阶段整理仅收束本轮QA、源标注和未解决问题，不改总STATUS或发布状态。
