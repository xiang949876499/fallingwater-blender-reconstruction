# 完整第08轮120机位独立检查

**120/120保存相机参数匹配；120/120实际网格点位安全检查通过。Blender5.2.1 LTS、CPU4进程退出码0。** 本检查没有渲染，没有改生产配置、相机或场景。

实际源 [Fallingwater_iteration08.blend](D:/zx/test/project/scene/Fallingwater_iteration08.blend) SHA256 `c5cd501e4c8ae0205ecb2437cd2d06d0c92bcc9a87e7d93d3986aeef976070d7`。冻结 [camera08-settings-frozen.json](D:/zx/test/project/qa/camera08-settings-frozen.json) SHA256 `f011c9462431e12137a49d3829a85586da0804a5a934086e03d7143c7d5dc1d0`，与已采用7位后的生产文件同字节；检查前后场景和生产文件哈希均未变。

## 先读取保存值，再比较与检查

从磁盘重新打开完整08后，先读取每个真实相机的世界位置、完整四元数旋转（含滚转）、焦距、shift_x、shift_y和fw_exposure，随后与冻结JSON比较。没有先应用配置，也没有保存场景。全部120位逐字段误差低于0.0001；最大shift_y误差为1.669×10⁻⁸，其余记录的最大误差为0。

点位射线使用刚读出的实际世界位置和方向；方向目标沿相机自身−Z恢复。冻结配置里的地面高度只作为参考，用来检出实际支持面变化。独立写出的saved-geometry-input是检查输入，不是生产相机设置，也没有回写场景。

[实际保存值与期望值逐项记录](D:/zx/test/project/qa/camera08-saved-settings-check.json)；[真实几何120行报告](D:/zx/test/project/qa/camera08-verification.json)；[运行摘要与哈希](D:/zx/test/project/qa/camera08-validation-summary.json)；[完整日志](D:/zx/test/project/qa/camera08-verification.log)。

## 当前几何与支持面

新评估索引为9,631对象、976,540顶点、1,042,424多边形。3,840条总射线中，1,920条检查四脚支持点、身体柱、六方向眼点及中心地面；其余1,920条是旧式未应用shift的取景诊断射线，不能证明构图通过。身体检查高度1.75m、五条轴向竖射线覆盖0.15m半径，属于离散点位检查，不是连续碰撞体或导航路径验收。

中心支持面相对冻结地面高度容差4cm；四脚点允许19cm高度差并排除家具、水和陡斜支持。18个房间多边形外的相邻/门外/平台检查位重新计算后标识全部匹配；它们仍不是18个房间内部浏览通过。

相对旧07报告，有9个中心支持记录变化：7个来自本轮已接受的实际机位移动；另2个为原机位的地面变化，具体如下。

| 原机位 | 08实际支持变化 | 结果与限制 |
|---|---|---|
| CAM_MAIN_L2_BATH_G_A | 原门槛饰面变为MAIN_L2_BATH_G_finish，高度仍2.86700m | 中心和身体检查通过；这个单点不能证明整条墙脚/门槛无缝 |
| CAM_GUEST_L1_POOL_A | 同一GUEST_L1_MAIN_FLOOR上，07实测8.40137m，08实测8.40020m | 相对冻结support_z 8.40430m低4.1mm，在4cm容差内；眼高相对实际面约1.6041m，不改配置 |

此外，Main Coat B的冻结支持名称仍是旧门槛饰面、实测为MAIN_L1_COAT_finish；Guest Boiler A旧名GUEST_L1_HALL_NORTH、实测GUEST_L1_CAR_COURT。两项名称差异已存在于07，08仍为同高；不把旧差异误记为新结构退化。

| 新采用机位 | 08实际中心支持面 | z（米） |
|---|---|---:|
| CAM_MAIN_B_PLUNGE_B | MAIN_loggia_pool_stair_00 | -2.32647 |
| CAM_MAIN_L2_CLOSET_G_A | MAIN_L2_GUEST_finish | 2.86700 |
| CAM_MAIN_L2_CLOSET_G_B | MAIN_L2_GUEST_finish | 2.86700 |
| CAM_MAIN_L3_BATH_A | MAIN_L3_BATH_finish | 5.28635 |
| CAM_MAIN_L3_ALCOVE_B | MAIN_L3_GALLERY_finish | 5.28635 |
| CAM_MAIN_L3_STAIR_A | MAIN_L3_GALLERY_finish | 5.28635 |
| CAM_GUEST_L1_BOILER_B | GUEST_L1_BOILER_FLOOR | 8.40020 |

## 视觉与范围边界

本轮只是完整08上的新几何与保存参数复验，没有打开新的完整08渲染图。此前接受的7张构图图像来自冻结07：Plunge B、Alcove B、Stair A为R；Bath A、Boiler B、Closet G A/B为L。它们的历史标签和图像哈希保留，不能因08点位通过而升级为08视觉通过。

房间几何索引排除植被；HERO等展示相机不在这120位范围内。未完成的Servant A/B、Coat B、Closet M B构图FAIL，以及其他旧图的材质、照明、墙脚与石缝问题仍需新图检查。摄影质量、连续导航和全120新视觉均不由本报告验收。

历史证据：[07逐房120图](D:/zx/test/project/qa/camera07-room-review.md)；[7位采用的图像与限制](D:/zx/test/project/qa/camera08-accepted-review.md)。
