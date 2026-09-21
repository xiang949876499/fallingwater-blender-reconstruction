# 客厅中央矩形灯屏 — 2026-09-20

本部件已完成独立建模和局部几何检查，可以并入下一版场景。整屋写实程度、最终灯光及漫游仍由总验收决定。

## 证据与保留条件

- 实际查看 [HABS PA-5346-48](https://www.loc.gov/pictures/item/pa1690.photos.134187p/) 的 1985 年原片，以及摄影者 Eritak 于 2011-06-22 拍摄的[原始灯屏照片](https://commons.wikimedia.org/wiki/File:Fallingwater_interior.JPG)。两图均可见外圈分格灯屏、中央实心平板与外围凹槽照明，支持 circa 2010 保育合成基线中的构件形式（B）。
- 实际查看馆方 [Fireside](https://fallingwater.org/fallingwater-fireside/) 壁炉原图、[High School Residency](https://fallingwater.org/fallingwater-institute/high-school-residency-studio-1/) 学生照片；它们裁掉此区域，不能作为灯屏的当代确认。From Home 页面只读取文字和链接，没有从该页确认天花。
- 主屋 main04、main05 图实际查看，仅用于房间轴线、上层楼板关系；未发现带尺寸的天花反射平面。灯框尺寸、细框厚度、分格数量和灯光强度均为 C，不能当作现场测量。
- Commons 照片自身是 CC BY-SA 3.0；本轮仅在线查看，未下载、未做纹理、未随模型重分发。灯具技术类型、隐藏线路和精确历史设计归属不作断言。

## 实施范围

只改变 `MAIN_L1_LIVING_ceiling` 的 18 mm 饰面层，在世界 X 0.70–6.10、Y 4.60–10.40 m 的范围形成灯屏开口。5.4 × 5.8 m 外框和 3.7 × 4.0 m 中央板按照片比例与中央轴线估计；位置不确定度 ±0.5 m，尺寸不确定度 ±0.6 m。

外框、分格透光片、偏移细轨、可见小齿边、凹槽灯片和中央实心面共 206 个物件。只使用实际构件的发光表面，没有添加房间隐藏补光灯。灯片强度是渲染参数，不是实测瓦数或流明。

槽口内另有不透明封板，避免上层门洞投影处漏光；原上层楼板、层高和房间记录均不改变。保留在已有夹层内的浅槽约 65 mm，并不把照片无法量出的深度当真值。

## 已执行检查

| 项目 | 结果 | 证据 |
|---|---|---|
| 改造前向上实际场景射线 | 25 处；原饰面底/顶 2.500 / 2.518 m；有楼板处板底 2.6248 m | architectural-detail-preconstruction.json |
| 二层结构保持 | 所有 MAIN_L2_*_slab 的顶点、面拓扑及对象变换 SHA256 前后相同 | architectural-detail.json 的 structural_slab_hashes_unchanged |
| 部件高度范围 | 2.475000–2.603000 m；与最下层上部楼板间距 21.8 mm | 同一数据文件的实际网格包围盒 |
| 槽口闭合、净空 | 195 组实际地坪向下射线与天花向上射线全部通过；最小采样净高 2.369 m；全构件最低框底相对名义地坪保守下限 2.353 m | architectural-detail-clearance.json |
| 槽口外原天花连续性 | 四边槽口外 12 处射线均命中原 `MAIN_L1_LIVING_ceiling`、Z 2.500 m；原周围天花保留 | 同上 |
| CPU 小样 | 4 线程、Cycles 32 samples、900×600 两张；60.58 秒与54.37 秒 | architectural-detail-render.json |
| 视觉检查 | 两张 PNG 均实际打开查看；中央板、外圈分格、双轨与灯槽清楚可辨，开槽没有变成天窗 | architectural-detail-context.png / architectural-detail-upward.png |

局部外形通过。灯片在上下文图中偏亮，原场景天花偏深；应随总场景曝光继续校准，不能把此处的灯光参数标为最终摄影匹配。上述净空检查只覆盖天花闭合和高度，不代表家具碰撞或全屋漫游验收。

## 整合接口

在主屋、客房构建后、家具构建前调用 `architectural_detail.build(ctx, rooms)`。需要 `ctx.mats['ceiling']` 及 `MAIN_L1_LIVING_ceiling`，返回生成的对象列表。

模块拒绝重复安装，且在原饰面高度或上方净空不符时停止。若主屋饰面高度改变，应先重新检查，不能禁用保护检查强行挖槽。模块写入 `project/data/architectural-detail.json`，并把同一证据嵌入场景文本 `FW_ARCHITECTURAL_DETAIL.json`。

独立检查点：`project/qa/architectural-detail-checked.blend`。没有覆盖 `Fallingwater_working.blend`。该检查点基于整合前工作文件，最终交付须以 root 的下一次全场景重建为准。

收尾已按 neat-freak 在本任务所有权范围内同步实现、证据与检查文档。项目总目录、状态和构建入口由 root 统一更新，避免并行覆盖。
