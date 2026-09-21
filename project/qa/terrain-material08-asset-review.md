# 一个阔叶落叶扫描候选

本轮只选择 **[Leaves Forest Ground](https://polyhaven.com/a/leaves_forest_ground)**，由Dimitrios Savva摄影、Dario Barresi处理。原图已实际查看，适合一次表面材质对照；不是Fallingwater现场扫描，具体叶种与秋季匹配保持C/U。

官方资产页标注CC0；[官方许可页](https://polyhaven.com/license)明确允许商业使用及资产随项目或单独再分发。许可判断针对下载的三张原始资产贴图，不扩展到网页文字、标志或官方预览渲染。根任务统一更新assets manifest，本代理未修改其清单或生产材质。

## 真实尺度与高度

[官方info API](https://api.polyhaven.com/info/leaves_forest_ground)给出约1260×1260；[官方API schema](https://github.com/Poly-Haven/Public-API/blob/master/swagger.yml)定义texture.dimensions单位为毫米。故候选使用 **1.26×1.26m**，Object缩放约**0.79365076/m**。官方网页的1.3m和2K约16.3px/cm是舍入后的交叉证据。

高度PNG含16位数据，0..1值不能直接当成米。未找到此资产的实测Z幅度；候选Bump Distance=.020m、Strength=.5为明确C作者设置，仅扰动法线，不驱动位移或改变碰撞几何。不会为了更显眼而把叶宽放大到任意2m/4m。

## 实际原图判读

- diffuse：连续重叠的浅褐卷叶、碎裂宽叶边缘、黄橙色完整叶、深色腐殖土与细枝，绿色成分有限。与原forrest_ground_01主要细草/苔藓/泥土的形态明确不同。
- rough：存在对应叶片与土区的粗糙度差别，候选直接使用源图，不再压缩到旧材质约.96…1的狭窄范围。
- height：本机直接view工具不支持原I;16 PNG；已实际打开从**未改变的原标量矩阵**绘制的`terrain-material08-height-analysis.png`，带1.26m平面坐标与0..1数值标尺。能看到叠叶与卷边起伏，图中的米仅表示平面覆盖尺度，不表示高度幅度。

新图并非单一灰色；但浅色枯叶、黄橙色点和周期性铺贴能否在当前曝光下显得自然，必须看候选三图。没有采用灰色tint、替换参考照片作为纹理、增加散叶或改变林冠。

## 下载与再分发记录

三文件共**12,976,072 bytes**，均由[官方files API](https://api.polyhaven.com/files/leaves_forest_ground)给出的dl.polyhaven.org链接下载，字节数/MD5逐项一致，本地另算SHA256。完整URL、时间和元数据保存在`terrain-material08-asset-download.json`；官方响应保存于同前缀info/files JSON。

| 文件 | SHA256 |
|---|---|
| assets/textures/leaves_forest_ground_diff_2k.jpg | bda0ffc30570af7c067a3d6922cb1c7f31ada4fcece24b8f2cc4c5dde742e22c |
| assets/textures/leaves_forest_ground_rough_2k.jpg | a08b1aaba9ca87924abfbe65a1c6be03c6cc7fcfcf140dc784ccf35205c307f0 |
| assets/textures/leaves_forest_ground_disp_2k.png | 38294b4ce4c1f6c99611876cb972f7973ecf65ae5be0ed406a11b705699411bd |

没有付费购买、修改旧素材或发布远端资源。查看状态单独写入`terrain-material08-asset-view.json`，不把下载状态当作外观通过。
