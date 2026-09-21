# 客房独立网格尺寸核验 — iteration03 修复前

**结果：7 PASS / 10 FAIL / 5 NOT_RUN。** 这是已保存场景的真实网格测量，不能作为项目验收通过。此次仅新增证据，未覆盖 working.blend。

场景：`D:\zx\test\project\scene\Fallingwater_working.blend`；修改时间 `2026-09-20T14:01:06.443038`；SHA-256 `2f4f904a0364cf2792036ad59b7a112280cd64a15405945a13e975615a561bf4`。Blender 5.2.1 后台只读、4 线程，无渲染。

测量使用 evaluated mesh 的世界坐标顶点、实际表面射线与几何极值。参考 JSON 的 `model_value_m` 没有作为测量结果使用。泳池边沿集合只包含数字编号 coping 环，已排除同前缀的上行楼梯扶手。

容差严格采用 QA GEO-02：`max(0.020 m, 0.005 × 参考尺寸)`。原图读数不确定性另列，不扩大通过门槛。A 表示原图标注，C 表示净面/构件归属解释；二者与是否实际测量分开。

| 锚点 | 原图 | 参考 m | 实测 m | 差值 mm | 容差 mm | 结果 |
|---|---|---:|---:|---:|---:|---|
| GUEST_THEATER_LENGTH | 27 ft 9 in | 8.458200 | — | — | 42.3 | NOT_RUN |
| GUEST_THEATER_DEPTH | 19 ft 5 in | 5.918200 | — | — | 29.6 | NOT_RUN |
| GUEST_POOL_LENGTH | 30 ft 1 in | 9.169400 | 9.169399 | -0.001 | 45.8 | PASS |
| GUEST_POOL_WIDTH | 13 ft 0 in | 3.962400 | 3.962402 | +0.002 | 20.0 | PASS |
| GUEST_BOILER_DIM_1 | 4 ft 7 in | 1.397000 | 1.176155 | -220.845 | 20.0 | FAIL |
| GUEST_BOILER_DIM_2 | 8 ft 2 in | 2.489200 | 2.420560 | -68.640 | 20.0 | FAIL |
| GUEST_GUEST_ROOM_LENGTH | 15 ft 9 in | 4.800600 | 5.055999 | +255.399 | 24.0 | FAIL |
| GUEST_GUEST_ROOM_DEPTH | 14 ft 1 in | 4.292600 | 4.018040 | -274.560 | 21.5 | FAIL |
| GUEST_LAUNDRY_LENGTH | 11 ft 7 in | 3.530600 | 3.367680 | -162.920 | 20.0 | FAIL |
| GUEST_LAUNDRY_DEPTH | 9 ft 8 in | 2.946400 | 2.715800 | -230.600 | 20.0 | FAIL |
| GUEST_BASE_BATH_LENGTH | 6 ft 8 in | 2.032000 | 2.053959 | +21.959 | 20.0 | FAIL |
| GUEST_BASE_BATH_WIDTH | 5 ft 1 in | 1.549400 | 1.376240 | -173.160 | 20.0 | FAIL |
| GUEST_SERVICE_Y_CHAIN | 50 ft 10.25 in | 15.500350 | — | — | 77.5 | NOT_RUN |
| GUEST_POOL_OUTER_WIDTH | 31 ft 6.625 in | 9.617075 | 9.459400 | -157.675 | 48.1 | FAIL |
| GUEST_THEATER_NORTH_RISE | 14 ft 5.625 in | 4.410075 | — | — | 22.1 | NOT_RUN |
| GUEST_THEATER_EAST_SEGMENT | 12 ft 8.75 in | 3.879850 | — | — | 20.0 | NOT_RUN |
| GUEST_SECOND_LEVEL | 7 ft 8.625 in | 2.352675 | 2.352675 | +0.000 | 20.0 | PASS |
| GUEST_TOP_STONE | 14 ft 9.625 in | 4.511675 | 3.392675 | -1119.000 | 22.6 | FAIL |
| GUEST_PARAPET | 10 ft 9.75 in | 3.295650 | 3.295650 | +0.001 | 20.0 | PASS |
| GUEST_CHIMNEY | 17 ft 2.75 in | 5.251450 | 5.251450 | +0.001 | 26.3 | PASS |
| GUEST_LOW_STONE | 6 ft 11.75 in | 2.127250 | 2.127251 | +0.001 | 20.0 | PASS |
| GUEST_POOL_TOP | 2 ft 3.75 in | 0.704850 | 0.704850 | +0.000 | 20.0 | PASS |

## 高优先级复核与修正建议

1. 上层尖角服务露台的石墙顶实测 3.392675 m，原图标高 4.511675 m，低 1.119 m。西立面叠合可直接辨认高度差，须修正关联围墙而非修改标注。
2. 客房净尺寸 +255 / −275 mm；锅炉房 −221 / −69 mm；洗衣房 −163 / −231 mm；地下浴室宽 −173 mm。修正前须逐项确认净面定义，连同相邻墙、门、房间多边形一并协调。
3. 泳池内壳两净尺寸通过，外沿宽短 158 mm，应先确认外侧界线后只调整外环。地下浴室长度 +22 mm 属边界偏差，不能忽略扫描不确定性。

## 原图与实际网格叠合

红线为已保存场景的 evaluated mesh 真正边线，灰色为 HABS 原图，蓝色为实测线段或标高差。两图均为透视遮挡未消除的正交投影，未逐物体拟合。全量构件名和投影线存在配套 JSON，可复算。

![首层叠合](D:/zx/test/project/qa/guest-dimensions-measured-plan-overlay.png)

平面：原图统一 1024×790 坐标，`px=325+(X−3.4)/0.05256`，`py=422−(Y−37.1)/0.05272`。含首层楼板/墙/窗、泳池、两组服务梯；不含二层与地下室围护、屋面、家具、装饰砌石。图上约 1 px 追踪不确定性等于 53 mm。

![西立面叠合](D:/zx/test/project/qa/guest-dimensions-measured-west-overlay.png)

西立面水平尺度独立采用原图 66′2⅜″=20.177125m、见证端点 px221.5→606.0；垂直采用 SECOND LEVEL 7′8⅝″=2.352675m、py243→199。映射 `px=577−(Y−37.1)/0.052476268`，`py=243−(Z−8.3999996)/0.053469886`。服务东南角定位 ±2px，尺寸见证端点 ±1px；没有用石墙顶目标单独拟合。包含西侧服务外墙、上层露台、选定楼板屋面和连接雨棚，完整列表见 JSON。

两张叠合均已实际打开检查。连接雨棚仍存在源图立面形状偏差，此次尺寸锚点审计未判其通过。

## 逐项对象与端点证据

### GUEST_THEATER_LENGTH — NOT_RUN

来源：HABS PA-5346-A sheet 1 original TIFF；标注 27 ft 9 in；读数不确定性 ±0.0254 m。

NOT_RUN: Nominal27′9×19′5 is printed inside a skew, recessed theater. Neither dimension is drawn with explicit endpoints; true door recess and nonparallel walls make world-axis extent an invalid substitute.

A printed source; U exact source-to-mesh endpoints.

### GUEST_THEATER_DEPTH — NOT_RUN

来源：HABS PA-5346-A sheet 1 original TIFF；标注 19 ft 5 in；读数不确定性 ±0.0254 m。

NOT_RUN: Same nonrectangular theater endpoint ambiguity; no independent source principal-axis endpoint correspondence has been established.

A printed source; U exact source-to-mesh endpoints.

### GUEST_POOL_LENGTH — PASS

来源：HABS PA-5346-A sheet 1 original TIFF；标注 30 ft 1 in；读数不确定性 ±0.0254 m。

Opposed ray intersections with evaluated pool shell inner faces at guest datum; finite water mesh deliberately not used as the clear-basin size.

A printed pool dimensions; unambiguous inner shell face intersections.

- 端点 1：`GUEST_POOL_shell_17`，世界坐标 `[23.2031403, 34.9648399, 8.3999996]` m。
- 端点 2：`GUEST_POOL_shell_35`，世界坐标 `[32.3725395, 34.9648399, 8.3999996]` m。

### GUEST_POOL_WIDTH — PASS

来源：HABS PA-5346-A sheet 1 original TIFF；标注 13 ft 0 in；读数不确定性 ±0.0254 m。

Opposed ray intersections with evaluated pool shell inner faces at guest datum; finite water mesh deliberately not used as the clear-basin size.

A printed pool dimensions; unambiguous inner shell face intersections.

- 端点 1：`GUEST_POOL_shell_26`，世界坐标 `[27.7878399, 32.9836388, 8.3999996]` m。
- 端点 2：`GUEST_POOL_shell_08`，世界坐标 `[27.7878399, 36.9460411, 8.3999996]` m。

### GUEST_BOILER_DIM_1 — FAIL

来源：HABS PA-5346-A sheet 1 original TIFF；标注 4 ft 7 in；读数不确定性 ±0.0254 m。

Opposed world axis1 rays to actual named structural/finish faces from drawing pixel(353, 333),Z8.75000. Opening-free section selected; decorative coursing and furnishings excluded. Nominal room dimension axis follows plan aspect and adjacent dimension chain.

A printed label; C endpoint interpretation from plan/elevation; actual evaluated mesh.

- 端点 1：`GUEST_L1_BOILER_SOUTH_pier_end`，世界坐标 `[4.8716798, 41.1512833, 8.75]` m。
- 端点 2：`GUEST_L1_BOILER_NORTH_pier_end`，世界坐标 `[4.8716798, 42.3274384, 8.75]` m。

### GUEST_BOILER_DIM_2 — FAIL

来源：HABS PA-5346-A sheet 1 original TIFF；标注 8 ft 2 in；读数不确定性 ±0.0254 m。

Opposed world axis0 rays to actual named structural/finish faces from drawing pixel(353, 343),Z8.75000. Opening-free section selected; decorative coursing and furnishings excluded. Nominal room dimension axis follows plan aspect and adjacent dimension chain.

A printed label; C endpoint interpretation from plan/elevation; actual evaluated mesh.

- 端点 1：`GUEST_L1_BOILER_WEST_pier_end`，世界坐标 `[3.5625598, 41.2648811, 8.75]` m。
- 端点 2：`GUEST_L1_BOILER_EAST_pier_end`，世界坐标 `[5.98312, 41.2648811, 8.75]` m。

### GUEST_GUEST_ROOM_LENGTH — FAIL

来源：HABS PA-5346-A sheet 1 original TIFF；标注 15 ft 9 in；读数不确定性 ±0.0254 m。

Opposed world axis0 rays to actual named structural/finish faces from drawing pixel(580, 425),Z8.75000. Opening-free section selected; decorative coursing and furnishings excluded. Nominal room dimension axis follows plan aspect and adjacent dimension chain.

A printed label; C endpoint interpretation from plan/elevation; actual evaluated mesh.

- 端点 1：`GUEST_L1_BATH_EAST_pier_end`，世界坐标 `[14.3699198, 36.9418411, 8.75]` m。
- 端点 2：`GUEST_L1_BED_EAST_sill_1`，世界坐标 `[19.4259186, 36.9418411, 8.75]` m。

### GUEST_GUEST_ROOM_DEPTH — FAIL

来源：HABS PA-5346-A sheet 1 original TIFF；标注 14 ft 1 in；读数不确定性 ±0.0254 m。

Opposed world axis1 rays to actual named structural/finish faces from drawing pixel(580, 400),Z8.75000. Opening-free section selected; decorative coursing and furnishings excluded. Nominal room dimension axis follows plan aspect and adjacent dimension chain.

A printed label; C endpoint interpretation from plan/elevation; actual evaluated mesh.

- 端点 1：`GUEST_L1_BED_FRONT_sill_0`，世界坐标 `[16.8027992, 36.6678009, 8.75]` m。
- 端点 2：`GUEST_L1_NORTH_STONE_SPINE_pier_end`，世界坐标 `[16.8027992, 40.6858406, 8.75]` m。

### GUEST_LAUNDRY_LENGTH — FAIL

来源：HABS PA-5346-A sheet 1 original TIFF；标注 11 ft 7 in；读数不确定性 ±0.0254 m。

Opposed world axis1 rays to actual named structural/finish faces from drawing pixel(258, 393),Z6.54000. Opening-free section selected; decorative coursing and furnishings excluded. Nominal room dimension axis follows plan aspect and adjacent dimension chain.

A printed label; C endpoint interpretation from plan/elevation; actual evaluated mesh.

- 端点 1：`GUEST_B1_BASE_SOUTH_sill_0`，世界坐标 `[-0.12152, 37.3354416, 6.54]` m。
- 端点 2：`GUEST_B1_BASE_NORTH_pier_end`，世界坐标 `[-0.12152, 40.7031212, 6.54]` m。

### GUEST_LAUNDRY_DEPTH — FAIL

来源：HABS PA-5346-A sheet 1 original TIFF；标注 9 ft 8 in；读数不确定性 ±0.0254 m。

Opposed world axis0 rays to actual named structural/finish faces from drawing pixel(255, 406),Z6.54000. Opening-free section selected; decorative coursing and furnishings excluded. Nominal room dimension axis follows plan aspect and adjacent dimension chain.

A printed label; C endpoint interpretation from plan/elevation; actual evaluated mesh.

- 端点 1：`GUEST_B1_BASE_BATH_EAST_pier_end`，世界坐标 `[-1.5281999, 37.9435196, 6.54]` m。
- 端点 2：`GUEST_B1_BASE_EAST_pier_end`，世界坐标 `[1.1876, 37.9435196, 6.54]` m。

### GUEST_BASE_BATH_LENGTH — FAIL

来源：HABS PA-5346-A sheet 1 original TIFF；标注 6 ft 8 in；读数不确定性 ±0.0254 m。

Opposed world axis1 rays to actual named structural/finish faces from drawing pixel(216, 400),Z6.54000. Opening-free section selected; decorative coursing and furnishings excluded. Nominal room dimension axis follows plan aspect and adjacent dimension chain.

A printed label; C endpoint interpretation from plan/elevation; actual evaluated mesh.

- 端点 1：`GUEST_B1_BASE_SOUTH_pier_0_cork_lining`，世界坐标 `[-2.3290401, 37.3444405, 6.54]` m。
- 端点 2：`GUEST_B1_BASE_BATH_NORTH_pier_end_cork_lining`，世界坐标 `[-2.3290401, 39.3983994, 6.54]` m。

### GUEST_BASE_BATH_WIDTH — FAIL

来源：HABS PA-5346-A sheet 1 original TIFF；标注 5 ft 1 in；读数不确定性 ±0.0254 m。

Opposed world axis0 rays to actual named structural/finish faces from drawing pixel(216, 404),Z6.54000. Opening-free section selected; decorative coursing and furnishings excluded. Nominal room dimension axis follows plan aspect and adjacent dimension chain.

A printed label; C endpoint interpretation from plan/elevation; actual evaluated mesh.

- 端点 1：`GUEST_B1_BASE_BATH_WEST_pier_end_cork_lining`，世界坐标 `[-3.0434401, 38.0489616, 6.54]` m。
- 端点 2：`GUEST_B1_BASE_BATH_EAST_pier_end_cork_lining`，世界坐标 `[-1.6672001, 38.0489616, 6.54]` m。

### GUEST_SERVICE_Y_CHAIN — NOT_RUN

来源：HABS PA-5346-A sheet 1 original TIFF；标注 50 ft 10.25 in；读数不确定性 ±0.0127 m。

NOT_RUN: Printed50′10¼ vertical witness line starts at an angled service-wall projection. Mapping that witness to a specific inner/outer finished vertex is unresolved.

A printed source; U exact source-to-mesh endpoints.

### GUEST_POOL_OUTER_WIDTH — FAIL

来源：HABS PA-5346-A sheet 1 original TIFF；标注 31 ft 6.625 in；读数不确定性 ±0.0127 m。

WorldX extrema of actual evaluated outer coping ring; compared with the separate printed pool exterior horizontal chain.

A source pool exterior chain; actual mesh extrema.

- 端点 1：`GUEST_POOL_coping_16`，世界坐标 `[23.0581398, 36.3960419, 9.0348501]` m。
- 端点 2：`GUEST_POOL_coping_00`，世界坐标 `[32.51754, 36.3960419, 9.0348501]` m。

### GUEST_THEATER_NORTH_RISE — NOT_RUN

来源：HABS PA-5346-A sheet 1 original TIFF；标注 14 ft 5.625 in；读数不确定性 ±0.0127 m。

NOT_RUN: Printed14′5⅝ north angled-wall projected rise lacks established inner/outer vertex identity in the current traced mesh. Do not substitute whole object boundingbox.

A printed source; U exact source-to-mesh endpoints.

### GUEST_THEATER_EAST_SEGMENT — NOT_RUN

来源：HABS PA-5346-A sheet 1 original TIFF；标注 12 ft 8.75 in；读数不确定性 ±0.0127 m。

NOT_RUN: Printed12′8¾ is a partial east-wall interval terminating at a projection line; no named mesh vertex fixes that witness endpoint, so whole east-wall length is not equivalent.

A printed source; U exact source-to-mesh endpoints.

### GUEST_SECOND_LEVEL — PASS

来源：HABS PA-5346-A sheet4 original TIFF；标注 7 ft 8.625 in；读数不确定性 ±0.0063 m。

Difference between actual mesh topZ and actual guest L1 slab topZ. TOP_STONE uses pointed service terrace enclosing stone walls visible at west elevation left; roof finish/other chimneys are not substituted.

A elevation label; C wall identity mapping for TOP_STONE, A direct object mapping for other levels.

- 端点 1：`GUEST_L1_MAIN_FLOOR`，世界坐标 `[3.4525599, 34.3058395, 8.3999996]` m。
- 端点 2：`GUEST_L2_BEDROOM_FLOOR`，世界坐标 `[-3.4853599, 37.0999985, 10.7526751]` m。

### GUEST_TOP_STONE — FAIL

来源：HABS PA-5346-A sheet4 original TIFF；标注 14 ft 9.625 in；读数不确定性 ±0.0063 m。

Difference between actual mesh topZ and actual guest L1 slab topZ. TOP_STONE uses pointed service terrace enclosing stone walls visible at west elevation left; roof finish/other chimneys are not substituted.

A elevation label; C wall identity mapping for TOP_STONE, A direct object mapping for other levels.

- 端点 1：`GUEST_L1_MAIN_FLOOR`，世界坐标 `[3.4525599, 34.3058395, 8.3999996]` m。
- 端点 2：`GUEST_L2_UPPER_TERRACE_DIAGONAL_pier_end`，世界坐标 `[-3.4569476, 52.6337547, 11.792675]` m。

### GUEST_PARAPET — PASS

来源：HABS PA-5346-A sheet4 original TIFF；标注 10 ft 9.75 in；读数不确定性 ±0.0063 m。

Difference between actual mesh topZ and actual guest L1 slab topZ. TOP_STONE uses pointed service terrace enclosing stone walls visible at west elevation left; roof finish/other chimneys are not substituted.

A elevation label; C wall identity mapping for TOP_STONE, A direct object mapping for other levels.

- 端点 1：`GUEST_L1_MAIN_FLOOR`，世界坐标 `[3.4525599, 34.3058395, 8.3999996]` m。
- 端点 2：`GUEST_LOW_ARM_ROOF_parapet_0`，世界坐标 `[3.4595604, 41.0487213, 11.6956501]` m。

### GUEST_CHIMNEY — PASS

来源：HABS PA-5346-A sheet4 original TIFF；标注 17 ft 2.75 in；读数不确定性 ±0.0063 m。

Difference between actual mesh topZ and actual guest L1 slab topZ. TOP_STONE uses pointed service terrace enclosing stone walls visible at west elevation left; roof finish/other chimneys are not substituted.

A elevation label; C wall identity mapping for TOP_STONE, A direct object mapping for other levels.

- 端点 1：`GUEST_L1_MAIN_FLOOR`，世界坐标 `[3.4525599, 34.3058395, 8.3999996]` m。
- 端点 2：`GUEST_STONE_CHIMNEY_pier_end`，世界坐标 `[1.07216, 40.9415588, 13.6514502]` m。

### GUEST_LOW_STONE — PASS

来源：HABS PA-5346-A sheet4 original TIFF；标注 6 ft 11.75 in；读数不确定性 ±0.0063 m。

Difference between actual mesh topZ and actual guest L1 slab topZ. TOP_STONE uses pointed service terrace enclosing stone walls visible at west elevation left; roof finish/other chimneys are not substituted.

A elevation label; C wall identity mapping for TOP_STONE, A direct object mapping for other levels.

- 端点 1：`GUEST_L1_MAIN_FLOOR`，世界坐标 `[3.4525599, 34.3058395, 8.3999996]` m。
- 端点 2：`GUEST_L1_NORTH_STONE_SPINE_pier_end`，世界坐标 `[6.1926804, 40.6928406, 10.5272503]` m。

### GUEST_POOL_TOP — PASS

来源：HABS PA-5346-A sheet4 original TIFF；标注 2 ft 3.75 in；读数不确定性 ±0.0063 m。

Difference between actual mesh topZ and actual guest L1 slab topZ. TOP_STONE uses pointed service terrace enclosing stone walls visible at west elevation left; roof finish/other chimneys are not substituted.

A elevation label; C wall identity mapping for TOP_STONE, A direct object mapping for other levels.

- 端点 1：`GUEST_L1_MAIN_FLOOR`，世界坐标 `[3.4525599, 34.3058395, 8.3999996]` m。
- 端点 2：`GUEST_POOL_coping_00`，世界坐标 `[32.51754, 36.3960419, 9.1048498]` m。

## 限制

5 个 NOT_RUN 均未找到可靠的原图见证点到当前网格端点的对应：剧场两个斜向名义尺寸、服务翼总 Y 尺寸、剧场北侧斜墙投影升高及东侧局部段。不能用整体包围盒代替这些尺寸。

绝对客房标高 8.4 m 仍是跨楼注册 C 级估计（7.4–9.4 m），本报告的局部标高通过不证明绝对位置准确。内部净面不含装饰石块突出，遇到实际软木墙衬则包含墙衬。后续修复与重测须另写 `guest-dimension-fixes*`，保留此修复前证据。
