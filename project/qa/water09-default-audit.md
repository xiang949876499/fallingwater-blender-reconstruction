# water09：本机默认液体设置审计与最小对照计划

**后续真实床对照：**[唯一24帧实际报告](water09-realbed24-control-review.md)已确认默认主物理组合在相同真实床/完整初池上可保持静水；这是组合可行性结果，非单因归因，视觉状态未提升。

**后续执行：**根已批准并完成唯一factory12对照，实际CPU4，0.789秒烘焙、10.09MB缓存，最小默认案例短段静水稳定性通过；首帧名义体积偏差仍为−11.62%。见[实际控制报告](water09-default-audit-control-review.md)。下文保留审计阶段的未执行提案，不代表复杂岩床已经通过。

2026-09-21。**审计完成；没有模拟、渲染、保存新场景、修改失败缓存或生产模型。** 新建对象只存在于独立`--factory-startup`后台进程内。读取的是本机Blender5.2.1 LTS，build `9e2066aef7ef`，不是凭文档猜默认值。

**未找到漏开自适应时间步、粒子半径异常或外部力权重继承。** 相比真实factory默认，static24主动开启了fraction碰撞及障碍内删除，调整了FLIP比例和时间步范围；另有已确认的secondary开关配置错误。这些是需要隔离的差异，当前还不能指定其中一项为31.98cm下降的根因。

## 可复现审计范围

审计脚本完全不导入项目建模helper。先创建2m单位缩放立方DOMAIN，切为LIQUID；再创建下半部GEOMETRY液体。仅另建一个域外临时立方碰撞体用于读取默认effector RNA，读取后移除；最终factory内只有domain和liquid两个对象。**没有运行流体求解或保存此场景。** 随后只读打开旧static24，比较150项domain属性、28项flow属性、全部effector/力权重、重力/单位及对象变换。全值、描述和差异见[审计JSON](water09-default-audit.json)，实际执行见[日志](water09-default-audit.log)。

旧场景 `Fallingwater_water08_static_head24.blend` 的前后SHA均为 `c108949a959351a2f0219a1f457b235b34903d9efb50dade5ab533a525d7ef2e`。原RNA上的只读`domain_resolution/cell_size/start_point`在未载入运行时求解器时返回0，报告保留该事实，**不把它当实际零分辨率或错误域尺寸**。domain基准网格仍是2.4×2×1.01m；带缓存对象的显示dimensions不参与域尺寸判断。

## 逐项关键对比

| 参数 | factory实际默认液体域 | static24实际保存值 | 判断 |
|---|---|---|---|
| `use_adaptive_timesteps` | True | True | 相同；不是遗漏启用 |
| CFL | 2 | 2 | 相同；实际逐子步执行仍无日志 |
| 最少/最多时间步 | 1 / 4 | 2 / 12 | 主动增加，未证明是错误 |
| `simulation_method` | FLIP | FLIP | 相同 |
| FLIP比例 | .97 | .94 | 主动增加PIC成分，不能仅凭差异定罪 |
| `use_fractions` | False | True | **碰撞表示发生变化，优先隔离** |
| fraction距离/阈值 | .5 / .05 | .5 / .05 | 参数同默认，只有启用状态不同 |
| `delete_in_obstacle` | False | True | **主动启用删除；有复杂碰撞时值得隔离**，未证实实际删除量 |
| 主液体`particle_radius` | 1 | 1 | 相同；不是mesh半径 |
| 粒子sampling | 2 | 2 | 相同 |
| 粒子min/max | 8 / 16 | 8 / 16 | 相同；窄带重采样不能按总点数当质量 |
| 随机率/窄带宽 | .1 / 3 | .1 / 3 | 相同 |
| system maximum | 0 | 0 | 相同，无额外全局粒子数量上限 |
| 六面碰撞 | 全True | 仅顶False，其余True | 静水顶面远高于液面；无证据证明该差异造成大量流失 |
| `use_flip_particles` | True | True | 主粒子系统均存在 |
| foam/spray/bubble | 全False | 全True | **已确认意外启用**；不是干净无secondary对照 |
| tracer / guiding | False / False | False / False | 相同，无引导场继承 |
| `use_mesh` | True | True | 本机实际默认，不假设为False |
| mesh倍率/半径 | 2 / 2 | 1 / 1.25 | 仅表示参数差异；无法解释原始FLIP包络同步下沉 |
| mesh生成器/平滑 | IMPROVED / 1、1 | 同左 | 相同 |
| 粘性、扩散、表面张力 | False、False、0 | 同左 | 没有隐藏高粘性或张力 |
| 时间倍率、FPS、重力 | 1、24、−9.81 | 同左 | 单位比例均1；use_gravity均True |
| force field权重 | factory默认 | 全部相同 | 未发现外部力权重继承 |

Flow仅一项差异：factory `use_initial_velocity=False`，static24=True，但两者`velocity_coord=(0,0,0)`、normal=0、random=0、velocity_factor=1，所以没有已证实的非零初速度。二者均LIQUID/GEOMETRY/MESH、surface_distance=0、subframes=0、非平面；volume_density=0也是本机默认，不能仅看这个数就认定液体没有体积初始化。对象没有动画、父变换或shape keys；单位缩放与矩阵均在JSON中。

两个actual effector均COLLISION/use_effector=True/非平面/velocity_factor1/subframes0，与factory默认一致；唯一标量差异是surface_distance 0→.001。这是以格为尺度的极小表面扩张，不是把碰撞体加厚1mm的世界长度。复杂地形和核心岩体本身仍是factory不存在的主要条件差异，几何正确闭合并不能证明求解器中的SDF/压力边界正确。

其他变化是res32→96、帧数250→24、REPLAY→ALL、缓存目录和分组集合等制作/输出配置。`has_cache_baked_guide/noise`等状态位在ALL完成后也为True，**不能据此说guiding/noise物理被启用**；实际`use_guide=False`。未发现第三个液体源、Outflow或额外effector。审计未尝试从缺失的压力/phi缓存中杜撰求解结论。

## secondary幂等预检实际通过

在无保存的factory进程中，执行“当前值不等于目标才赋值”的设置器，对三类secondary总计18步测试：重复False、False→True、重复True、True→False、再重复False。每一步都读取实际布尔值和粒子系统类型并断言。最终三项均False，只有FLIP系统，未创建任何流体缓存。

这已实际验证避免先前“对False重复赋False反而创建系统”的回调副作用；未来准备时仍要保存、重新打开并再次验证，不把代码中的赋值语句当验收。控制是否能保持水头尚未因这个设置器而验证。

## 唯一建议的最小对照：factory立方静水12帧

**只是一项待root选择的建议，本轮未执行。** 目的只判断纯默认物理的简单容器能否保持静水，先把复杂岩床和作者碰撞调参一起移出问题；它不是逐一归因的多因素试验，也不能取代自然河流验收。

- 独立factory启动，无项目helper、旧场景或旧缓存。DOMAIN为X/Y/Z均[−1,1]的2m闭合立方体、单位缩放；GEOMETRY液体为X/Y[−1,1]、Z[−1,0]的完整下半立方体，名义4m³。初始液面Z=0，底/侧达到域边缘，由默认边界处理不可流体格；不要留一圈干区域后再把初始铺展误判为失水。
- 保持真实默认物理：六面封闭、FLIP .97、fraction关闭、障碍内删除关闭、adaptive=True、CFL2、步数1–4、主粒子半径1、sampling2、min/max8/16、band3、无初速度、无effector、无secondary。重力−9.81，单位1，24fps。用已测幂等设置器确认secondary关闭，最终必须只有FLIP系统。
- 物理分辨率保持**默认32**，32³=32,768格、cell=.0625m、水深约16格；mesh保留默认倍率2/半径2。**1–12帧，共.5秒**，CPU8。只检验31.98cm量级的大幅静水坍塌，不能证明厘米薄片、湍流或5–10秒视觉。
- 仅输出配置改为ALL/1–12及新的项目内缓存目录；建议打开`cache_resumable`保留额外重启状态，完成后实际列出可读取的grid，不能预先保证pressure/obstacle一定被导出。若追求完全默认输出可仍使用False，但会重现诊断数据不足；此选择是缓存可观测性，不是新物理调参。
- **开算前**保存独立文件、复开，逐项断言上述实际参数、唯一GEOMETRY源、零非零初速度/effector、源体积4m³、闭合方向、六面边界和secondary系统；任何不符直接停止并报告，不边烘焙边修。
- 原始每帧报告mesh体积、水头、FLIP点数及粒子表面包络，禁止去漂移/映射滤波。至少实际保留f1/f6/f12原始数据。记录f1相对名义4m³的偏差；动态对照以f1为参照，f2–12体积漂移≤3%、中位液面漂移≤1格(.0625m)、95%高度漂移≤2格(.125m)，另报相对Z=0的误差。该粗网格控制门槛不同于最终水面门槛，不能用它追认旧static24为通过。
- 成本依据static24实测89.163秒/.355GB。按格数×帧数线性缩放仅约4.64秒，但新默认mesh倍率2会增加表面生成成本、启动与I/O固定成本也不能忽略；建议预算 **15–60秒、90秒停止上限、约10–60MB**。这是待实测估算，未承诺必达；绝不自动扩到24/36或长缓存。

若纯factory容器也出现明显粒子下沉，优先审查本机求解器/粒子栅格耦合与实际导出状态；不要继续在岩床调水头。若保持稳定，只能证明简单默认案例有效，接下来才有资格单项引入fraction/删除策略或真实床面去定位差异；这些后续试验均未获本提案授权，不在本轮执行。

收尾：只新增`qa/water09-default-audit*`。已有water08失败结论、155点厚度反例与生产guard保持不变。运行日志中的扩展索引写入受限及未启用粒子枚举警告保留；审计进程退出0，没有修改全局Blender设置。
