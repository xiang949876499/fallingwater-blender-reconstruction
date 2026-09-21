# 第五轮中央尺寸账本

第五轮冻结全场景重新测量完成。43 项源标注中，22 项已有明确的实际网格测量方法，全部数值吻合；其中 **12 项同时满足记录的读图精度要求，10 项为 SOURCE_PRECISION_LIMIT**。其余 21 项为 NOT_RUN，中央 CSV 的模型实值和差值留空。**GEO-02 整体验收仍为 INCOMPLETE。**

场景：`scene/Fallingwater_iteration05.blend`，SHA-256 `6bcfee7841c22e8e2b636352cfca79ae94968afb4235fc20cdc57e250ae046ff`。本次使用 Blender 5.2.1、CPU 4 线程，只读已保存网格，没有建模、改场景、保存场景或渲染。

## 账本纠正

旧 `dimensions.csv` 把源图坐标推导的 `MAIN_CHAIN_03.model_m=3.3560654640m` 写成模型实测。现在从两个已确认石墙外面的 evaluated mesh 顶点独立得到 **3.3527998999m**，对 11ft /3.3528m 的差为 −0.0000001001m。

- 当前账本：`../dimensions.csv`。
- 旧账本原字节备份：`dimensions-iteration05-previous.csv`。SHA 存于报告，不被重复审计覆盖。
- 全部对象选择器、实际顶点/面索引、射线起终点、原图标注、差值、读取误差、结果：`dimensions-iteration05.json`。
- 错误场景哈希、缺失对象选择器、NOT_RUN 空值、旧伪实值未被复用等 8 项回归：`dimensions-iteration05-verification.json`，全部通过。

测量来自本次加载的完整冻结场景，不复制主屋/客房独立模块报告中的旧数值。旧报告只用于追溯端点解释及无法测量的原因。源数据中的 `model_m`、`model_value_m` 从不作为测量输入；图纸坐标仅定位客房内部射线起点，实测距离取实际面交点。

## 数量与类别

| 类别 | 实测覆盖 | 尚缺内容 |
|---|---|---|
| 主屋 | 5：一个石墙水平跨距、四个相对标高 | 其他链式尺寸与无端点名义房间尺寸 |
| 客房 | 17：八个房间净面跨距、三个泳池平面尺寸、六个相对标高 | 五个剧场/服务翼端点不明尺寸 |
| 标高 | 10，分别依主屋和客房各自的实际楼板基准 | 没有共享主客楼绝对标高验证 |
| 悬挑 | 0 | 支承面到自由板边的有标注投影长度 |
| 开口 | 0 | 有源标注对应的门窗净宽或净高；通行检查不能替代 |
| 连接 | 0 | 有源标注对应的楼梯、连廊跨度/高差/交接尺寸 |
| 场地 | 仅泳池局部 4 项（含池壁顶标高） | 桥、挡墙、地形、建筑之间配准尺寸 |

类别互相重叠，不能把类别数量相加；同一锚点多次复测也不是新锚点。泳池内/外跨距有不同标注和不同端点，但构造及标定相关。主屋全链总长如将来可测，也不能作为各分段之外新增的独立约束。

主屋实测 ID：`MAIN_CHAIN_03`、`MAIN_LEVEL_2`、`MAIN_LEVEL_3`、`MAIN_ROOF_EAST`、`MAIN_ROOF_WEST`。客房 17 项的完整 ID、类别和端点均列于 JSON 的 `measurements` 与 `category_coverage`，没有把泳池长度当作建筑门窗开口尺寸。

## 精度与解释

数值阈值始终为 **max(0.020m,0.005×原图长度)**。`numeric_result=PASS` 只表示实际网格与标注数字之差在此阈值内；若读图误差大于阈值，`standard_result=SOURCE_PRECISION_LIMIT`，不能称符合该标准的精度。

受此限制的 10 项为 `MAIN_LEVEL_2`、`GUEST_POOL_WIDTH`、`GUEST_BOILER_DIM_1/2`、`GUEST_GUEST_ROOM_LENGTH/DEPTH`、`GUEST_LAUNDRY_LENGTH/DEPTH`、`GUEST_BASE_BATH_LENGTH/WIDTH`。主屋读取误差 25mm，客房这些项 25.4mm；对应阈值为 20–24.003mm。没有放宽标准。

客房八个房间的轴向和饰面边界仍沿用已声明的 C 级解释，网格实测不能反证其原图端点语义已达到测绘精度。客房标高全部相对其自身主层；其世界 Z=8.4m 仍是缺乏共同测量基准的 C 级估计。`GUEST_POOL_OUTER_WIDTH` 沿世界 X 的池体长向测量，不能只看 ID 名称认成短向宽度。

## 整合接口

新接口位于 `../scripts/dimension_audit.py`。整合者可以在生成普通清单并保存目标 `.blend` **之后**调用：

```python
from dimension_audit import audit_dimensions
report = audit_dimensions(
    root,
    scene_path=bpy.data.filepath,
    prefix='dimensions-iteration05',
)
```

函数要求当前加载文件就是已保存目标且没有未保存修改；可提供 `expected_sha256` 锁定检查点。它不加载或修改场景，只读取 evaluated meshes 并更新 CSV/QA 报告；命令行入口会先加载指定文件。应最后运行，避免 `save_manifests` 再次用源图推导值覆盖中央账本。后续版本使用不同 `prefix` 保存独立负向证据。

本次没有修改 `build_scene.py`、主客屋源码或共享库。整合者仍需加入上述调用，否则未来重建可能复发。当前阶段按 neat-freak 对齐本次账本、报告和接口说明，项目全局状态继续由整合者维护。
