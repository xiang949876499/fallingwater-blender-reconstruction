# 完整09保存机位独立检查

**120个实际保存机位均匹配冻结设置，随后几何检查120/120通过。此结果不等同120张渲染图的构图、照明或真实感通过。**

输入 [Fallingwater_iteration09.blend](D:/zx/test/project/scene/Fallingwater_iteration09.blend)，SHA-256 `489b05e403aa9d02c3568a8e3813a24235ee5b7e782df4d1f149b3ff6673e331`。从 `integration09-freeze.json` 的已保存状态读取实际检查点和哈希；相机设置SHA `f011c9462431e12137a49d3829a85586da0804a5a934086e03d7143c7d5dc1d0`，另存09冻结副本。

首先直接读取Blender保存对象的世界位置、完整四元数（包括滚转）、焦距、shift_x/shift_y及fw_exposure，再与设置比较。检查前没有调用integrate、重设机位或保存场景。全部120项均为 `SAVED_SETTINGS_MATCH`；最大位置、旋转、焦距、shift_x和曝光差为0，shift_y最大差为 `1.66893×10⁻⁸`，低于逐字段0.0001容差。

随后用实际保存位置与方向构造几何检查输入，保留原地面标高作为变化参照。3,840次射线在9,632个几何对象、1,013,224顶点、1,079,070多边形的索引上完成，120项均为 `GEOMETRY_ONLY_PASS`。18个机位在对应统计房间多边形之外，全部与冻结的“邻室/门口/外部检查机位”标记一致；不能称为18个房间内视点。

| 证据 | 文件 |
|---|---|
| 实际保存pose逐项对比 | [camera09-saved-settings-check.json](D:/zx/test/project/qa/camera09-saved-settings-check.json) |
| 来自实际保存pose的输入 | [camera09-saved-geometry-input.json](D:/zx/test/project/qa/camera09-saved-geometry-input.json) |
| 逐机位几何结果 | [camera09-verification.json](D:/zx/test/project/qa/camera09-verification.json) |
| 哈希与计数汇总 | [camera09-validation-summary.json](D:/zx/test/project/qa/camera09-validation-summary.json) |

本轮Blender5.2.1后台CPU4执行，无渲染、无GUI、无源码/配置修改、无场景保存。结束后场景与生产相机设置SHA均相同。

方法的边界保留：几何索引排除植被，原15条构图诊断射线不计算镜头shift，因而只是旧诊断信息，不能替代带shift的实际图像检查。此报告也不代替完整导览、60条连接、材质外观或照片配准验收。导览结果另记 [09完整连接及整数帧检查](D:/zx/test/project/qa/tour-path-iteration09-review.md)。
