# Master源全景10：房间匹配差异

**新全景不支持当前模型的主卧门位和床向；地面材质及壁炉形体也有明确差异。只读审核完成，没有修改生产或候选10c。GEO-07精确照片配准仍为NOT_RUN。**

来源为 [Columbia MCAH Master Bedroom官方全景](https://projects.mcah.columbia.edu/ha/panos/Fallingwater/Master-Bedroom/)。原XML描述Interior Master Bedroom，署名Media Center for Art History / Photo by Maurice Luker，版权2001 Columbia University；文件名也标2001。该年代记录作为本轮源基准，不能自动冒充其他年代完全相同的陈设。四张800px水平原面均实际打开，另按XML明确input地址读取并打开face0、face2的2880原面。仅在本地作参考，保持REFERENCE_ONLY_EXCLUDE_PUBLIC_PACKAGE。

[四面关系图](D:/zx/test/project/qa/master-source10-four-face-layout.png)已实际打开。face0为入口/柜体一侧，face1为床头侧，face2看露台玻璃，face3看石壁炉及桌面。对照main05可称图纸北/东/南/西侧；这不是地理方位测量，也不是已拟合全景相机角度。

| 部分 | 全景可见事实 | 真实保存09模型 | 判断 |
|---|---|---|---|
| 入口门 | face0：石芯右侧、大柜左侧；main05门口约x352..366 | 门/门楣为x367..390、y303；北木墙覆盖x332..367 | 现门偏入柜体对应范围，源身份不符；应连同相邻墙、门槛、门扇重新配准 |
| 床朝向 | face1床头靠图纸东墙，南玻璃在右；柜体位于相邻北面 | 床头在source x340.723..373.357、y323.614..324.838，床轴南北、头朝北 | 主卧专属陈设位置与方向不同，不能靠换镜头解决 |
| 主卧地面 | 四面连续可见大块不规则石板 | MASTER_finish及hall_master_finish为FW_cork | 两处材质与该全景不符；Closet_M_finish已经是FW_stone_floor，不能算作同一材质错误 |
| 柜与床边陈设 | 大型平整通高北柜在门右侧；低床头，床旁开放书架、细木灯柱 | 当前视图将床放在北侧柜/门附近，使用通用抽屉柜及锥形灯罩 | 房间布局和轮廓需按专属源重做；不把未测尺寸写成精确值 |
| 西壁炉 | face3：深炉膛、悬挑横石板、错层壁龛、不同高度石返回 | MAIN_L2_master_hearth为8顶点/6面实心矩形，加表层石课程 | 关键结构特征缺失，不能用矩形框角替代真实壁炉角做拟合 |
| 顶部梁/吊顶台阶 | face1/3有明显深台阶，接到西侧石芯 | Master_A画面大体平顶；对应实体未逐一配对 | 源特征已确认，模型中是否全缺仍需专门追踪，未冒充已核定缺失 |

模型事实来自独立后台CPU4读取完整09保存文件，见 [master-source10-model-audit.json](D:/zx/test/project/qa/master-source10-model-audit.json)。它没有重设相机、改材料、保存场景或渲染。10c只修接口，保持原Master材质、门位、床向，因此这些差异也不会因10c闭缝自动消失。

为下一轮保留**9个可见结构特征候选**：入口左门框上下交点2个、南玻璃两个立框上下交点4个、西石壁炉的阶形/悬挑端点3个。逐点身份、800原面像素、约4px选点不确定度及阻塞原因见 [master-source10-review.json](D:/zx/test/project/qa/master-source10-review.json)。标注已实际打开：[face0](D:/zx/test/project/qa/master-source10-face0-landmarks.png)、[face2](D:/zx/test/project/qa/master-source10-face2-landmarks.png)、[face3](D:/zx/test/project/qa/master-source10-face3-landmarks.png)。MS10_09在开图后被剔除：原选点只是无法唯一定位的石板边中点。

**可验证的当前模型3D对应点为0，拟合点0，留出点0。** 门位已经矛盾、壁炉角缺失，南玻璃立框还未取得确定编号；这9个点不能充作已经完成的8点非共线配准。四个窗框点共面，全景面序也未被校准为世界方位。XML的默认浏览fov80不是原面摄影内参，tileScale1.00347亦须按正确的cube投影解释。

下一步应先纠正门/壁炉的源身份，再从连续玻璃分格和跨面建筑角冻结至少6拟合+2独立留出点，并使用正确全景投影检验。低残差不能把错误对象对应升级为通过。此轮已经提供明确可执行的布局差异，没有为凑8点而给错误世界坐标。
