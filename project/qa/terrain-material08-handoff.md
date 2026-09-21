# 08森林地表：诊断与单一材质候选交付

**当前状态：物理不变检查PASS / 新进程贴图依赖与接线PASS / VISUAL_FAIL / NOT_ADOPTED / NOT_IN_PRODUCTION。** 根任务及本代理已实际打开三张候选图，详见`terrain-material08-visual-review.md`。后文的渲染交接描述保留原实验条件，不代表仍未渲染。

候选：`scene/Fallingwater_terrain_material_candidate08.blend`，SHA256 **`7c4949d3d0a0dc4c9cfeb6c906b33842ef39fbe84bb5ce1030761a86ad1dbdae`**。

来源：完整08 `scene/Fallingwater_iteration08.blend`，SHA256 `c5cd501e4c8ae0205ecb2437cd2d06d0c92bcc9a87e7d93d3986aeef976070d7`，文件保持不变；已包含bank08 geometry、surface_tint=False及其他代理的08建筑工作。

## 诊断结论

实际查看了原三机位图、原草地diffuse/height及87/88照片。保存材质没有丢图、错颜色空间或对象尺度错误：2m Object/BOX映射和三贴图连接有效。原素材以细草、苔藓、土为主，近景草丝多数只有亚像素宽；场地缺少叶/根/岩的中尺度轮廓与林冠遮蔽。只靠Bump不会改变平滑坡体。Living A中央坡面实测在60m外，并非近30m修复范围；其+2.4EV比HERO/Loggia高1.6档，加重浅淡观感，但抽样不是硬剪白。

完整证据与边界见`terrain-material08-diagnosis.md`，原始保存场景probe与像素统计均在同前缀JSON。不能将“材质连线正确”称为环境外观通过。

## 原图与单一候选

选择[Poly Haven Leaves Forest Ground](https://polyhaven.com/a/leaves_forest_ground)，[官方许可](https://polyhaven.com/license)为可再分发CC0。只下载一个素材的2K diffuse/rough/16位height，共12,976,072 bytes；官方字节数/MD5和本地SHA256均核验。来源、作者、下载URL与文件清单见`terrain-material08-asset-download.json`，根任务据此统一补assets manifest。

新diffuse已直接实际打开：连续浅褐卷碎阔叶、黄橙整叶、深色腐殖土与细枝；旧forrest_ground_01为绿色细草/苔藓主导，两者形态明显不同。原height的I;16格式不被view工具支持，已实际看过未改变原矩阵的科学标量图`terrain-material08-height-analysis.png`。查看证据、C/U限制见`terrain-material08-asset-view.json`及`terrain-material08-asset-review.md`。

只复制terrain材质为`FW_LeafLitter_Scan08_Candidate`并替换slot0：

- 真实扫描平面范围约**1.26×1.26m**，API毫米单位与官网1.3m/16.3px每厘米互证。实际映射Scale=.793650746；BOX blend=.22保持原值。
- diffuse使用源色，MULTIPLY=(1,1,1)，没有新增灰色tint或去色。
- rough直接驱动Roughness，保留源粗糙度范围，绕过旧.7…1压缩。
- height使用原16位PNG、Non-Color，Bump Distance=.020m/Strength=.5。该幅度为**C作者近似**，不是扫描Z实测，Material Output.Displacement仍未接。
- 三图使用`//../assets/textures/leaves_forest_ground_*`相对路径。没有覆盖旧素材、复制网页图片当纹理、增加leaf/tree/rock或ground sheet。

## 验证和渲染交接

CPU4候选检查比较完整08 **23,384对象**：全部几何/拓扑/逐面smooth/矩阵/可见性不变，相机属性及灯光/曝光/保存帧不变，原有材质节点与图像数据设置未改；唯一对象属性差异是terrain材质槽。保存后重新打开的完整快照一致。见`terrain-material08-candidate-check.json`。

另一个CPU4新进程验证三张新图均可从相对路径加载，均2048²，颜色空间分别sRGB/Non-Color/Non-Color，sha一致，Base/Rough/Normal连接与1.26m实际映射正确。见`terrain-material08-candidate-readback.json`。首次readback把尚未请求像素的lazy-loaded图错误判为缺数据；已改成请求尺寸加载后再查，错误日志保留为attempt01，未修改候选文件。初构建的两个内置图像枚举警告也保留在日志，新三图依赖读回全部正常。

以下为已执行的同位对比设置，对照`renders/previews/iteration08-focus`；三图结果已判VISUAL_FAIL，不再安排该候选的重复渲染：

| 相机 | 对照曝光 | 目的 |
|---|---:|---|
| CAM_HERO | +.8EV | 近西坡是否读成叶土地表，是否产生明显平铺或黄橙噪点 |
| CAM_MAIN_L1_LOGGIA_B | +.8EV | 原路缘几何是否保持，卷叶细节是否自然，坡面是否仍像贴纸 |
| CAM_MAIN_L1_LIVING_A | +2.4EV | 60m以外林地能否改善，是否仍浅灰，避免把远地平均色当近景细节 |

根已按960×540/原相机与曝光完成CPU渲染并实际打开，本代理也已逐图复核：HERO/Loggia仍为均匀碎石状贴面，Living远景几乎未改善，故未采用。没有调曝光替代材质对比，本代理没有渲染/GPU或执行生产整合。此候选只验证了表面素材类型；不能替代后续宏观地形、树冠与环境整体验收。
