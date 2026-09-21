# 核心砂岩候选07c：局部破裂与表面尺度

当前阶段状态更新：根任务实际查看07c HERO/WATER_DETAIL后，将其接受为**下一次水原型的冻结碰撞基线**。主要床层和局部破裂较06/07/07b改善，但表面仍偏均匀、偏棕且反光/平滑感未解决；**最终摄影真实度与场地验收仍未通过**。已将 `data/site.json` 的 `core_bedrock_revision` 设置为 `discontinuous_beds_v3`，并注明阶段接受。下方“未启用”的表述为创建时历史状态。

新后台从空场景按真实 `_terrain→_geology` 顺序与相同seed/RNG生成，三个世界几何hash与07c完全一致，详见 `qa/core-geology07c-fresh-module-reproduction.json`。当前配置SHA256为 `2b4d5c712e7358dacc11458749d7dabc45bee98f43ec660fa9be4f36aa070c3d`。接下来的近岸 `bank_detail.py` 为独立候选，不允许修改该核心几何。

本轮实际打开了 `renders/previews/iteration07b-geology-candidate/CAM_HERO.png` 和 `CAM_WATER_DETAIL.png`。07b恢复了水平床层，但仍表现为大面积光滑带状墙、整洁的三角形台肩，不符合参考砂岩表面。**07b仍为 VISUAL_FAIL，不启用到全场配置。**

## 先核实的基线、材质与法线

`qa/geology-baseline-material-inspect07c.json` 是新 Blender 后台只读检查结果，进程退出0。旧无水基线 `Fallingwater_geology_baseline06_no_water.blend` 与较新 `Fallingwater_geology_baseline06b_frame48_no_water.blend` 在明确设置 frame48 后：23,436对象的网格/面索引/材质索引/平滑标记/形态键、变换、可见性、集合、相机投影与灯光均一致；材质节点列表、已记录的 socket 默认值/连接、BOX投影和打包贴图字节也一致。**可以直接复用已渲的旧基线，无须再渲两张重复基线。** 文件二进制hash不同不代表图像目标不同。

实际07b材质检查并非“猜测缺贴图”：

| 对象 | 实际槽与使用面数 | 朝向跌水方向的主要侧面 |
|---|---|---|
| Core | FW_wet_rock：591；FW_rock：418 | 547面湿岩，313面干岩 |
| Shoulder0 | 全部169面 FW_wet_rock | 57面朝向主要跌水方向 |
| Shoulder1 | 全部127面 FW_wet_rock | 36面朝向主要跌水方向 |

求值网格的主要前侧法线点积为正，范围约0.35…1.00，没有前墙整体反向的证据。图像中的宽亮岩面不能归咎于漏材质：PH_Diffuse/PH_Rough/PH_Displacement 实际存在，Object BOX纹理的色彩、roughness以及 Bump.001 正常连入 Principled BSDF。原湿岩的乘色、roughness和0.022m Bump保持不变；本候选没有调亮暗、替换材质或改变纹理尺度。

## 07c的有界几何改变

07b的[参考标注图](core-geology-07b-reference-annotations.png)和四个主要岩体层级继续保留。新增的裂隙具体位置/深度仍属C级作者近似，只借鉴87照片可见的局部剥落、裂缝终止于床层、粗糙岩面等类型，并非照片测量坐标。

- 以明确的 **8个局部多边形剥落区、5条有起止点的短裂缝**打断大平面。每处剥落范围和深度不同，凹进约6–12cm；不是把同一截面按整幅岩墙重复。
- 保留07b的主要层厚和退台，给表面添加约6–35cm波长、厘米级振幅的真实几何起伏；主要床层边缘只做局部碎口，仍可读出宽床层。
- 原始顶盖和底盖完整保留。内部网格加密后，用过渡多边形接回未细分、未移动的原边界；没有为了提高细节而改变上游床面或水力边界。
- 侧墙细化使用平滑面和38°几何锐边；上/下盖保留平面法线。其作用仅限小尺度表面的法线连续性，不改变大形体，避免整个肩部只有数个干净的三角面。
- 地形、植物、建筑、交通、材质、相机和灯光均不改；新碰撞网格仍使旧水缓存失效，不启动新模拟。

实现为 `site.py::refine_core_bedrock_v3`，配置启用键为 `discontinuous_beds_v3`，**当前data/site.json没有启用**。它从原冻结iteration06生成，不从工作场景反复侵蚀。配置中记录的每个剥落多边形与实际偏移统计会进入候选检查JSON，方便辨认哪里发生了几何改动。

本轮只准备一份无水候选，重用已证等价的旧frame48基线。候选在根任务统一渲染前仍为 **VISUAL_NOT_RUN**；不能以网格更密或封闭性通过断言真实感通过。

## 已完成的实际网格检查

Blender后台检查完成、退出0（启用 `--python-exit-code 1`）。候选为 `scene/Fallingwater_geology_candidate07c.blend`，SHA256 `24a2ca01d276cde137ff3e041ecbf5bdc028289f5b83e8be20167cb4a0c561f3`；对应 `qa/core-geology-candidate07c-check.json`、`.log`、`.py`。

| 对象 | 顶点 / 面 | 非流形边 / 边界边 | 体积 m³ |
|---|---:|---:|---:|
| Core | 11877 / 11730 | 0 / 0 | +309.7434 |
| Continuous shoulder0 | 6937 / 6805 | 0 / 0 | +8.8264 |
| Continuous shoulder1 | 5095 / 4996 | 0 / 0 | +13.9308 |

比对23,436对象，非目标对象签名变化0；核心上下各53顶点、两肩顶盖完全保持一致。实际参与局部细节的23,443顶点中，8,058顶点法向偏移超过1cm；最大法向偏移16.109cm出现在局部剥落/短裂缝叠加处，最大竖向偏移3.168cm。核心最高点仍−3.05500007m，水力顶盖没有上抬。

新core mesh SHA256为 `b85195ea1a7d71e51d2f36657211cfc31803436d280dd52de3e761cdcb551337`，不同于07b，旧水缓存仍不可复用。当前 `scripts/site.py` SHA256为 `2efde333707891a0a75237657b14057259ec2ae00e51c9df0ccc7db52858e1a6`，旧脚本备份为 `qa/site-after-core07b-before07c.py`；site.json SHA256仍 `edcf3b3f6375eb6eaf7fa676e36389ed0ce416857e0646120a9b52fe90b40a66`，未启用候选。

另从已保存候选重新打开验证法线，`qa/core-geology07c-saved-normals.json` 为 `PASS_SAVED_SHADING_FLAGS_AND_NORMALS`：核心1626条锐边、两肩796/688条锐边均实际保留；核心11728面、两肩6792/4986面为平滑面；顶底盖保持平面法线。求值角法线最大单位长度误差低于1.4×10⁻⁷，且与面法线有非零偏差，证明平滑/锐边并非只写在说明中。实际core材质分配为7318湿岩面/4412干岩面，两肩全部使用原湿岩。重新打开未保存、未渲染，候选文件hash不变。
