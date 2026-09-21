# Water11 两臂 source-only：已准备，根启动

**当前事故状态（2026-09-21，后于下述审计）：R075准备动作清除了S48原36文件缓存，现暂停。S24及此前684个文件独立哈希相同，S48场景/逐帧审计/原哈希仍在，但原缓存不能重读。见 [事故与隔离恢复方案](water11-source-cache-incident.md)。不要执行本页历史烘焙命令或R075入口。**

2026-09-21，**后续实际状态：根已完成两臂唯一烘焙，各12帧、退出0；全帧只读审计完成，见 [source-review](water11-source-review.md)。粗格复现约2.03倍通量、细格仍高56.15%，未通过流量匹配。不得重跑下面的历史启动命令。** P池体对照尚未准备，没有渲染或生产改动。

以下是准备阶段冻结记录，原状态 `PREPARED_TWO_ARMS_REOPEN_PASS_NO_BAKE` 及缓存当时0文件不代表当前未执行。根实际监控耗时27.8365/34.7092秒，缓存2,694,423/7,748,027字节。场景哈希指未被覆盖的prepared版本。

| 臂 | 场景 | SHA256 | 预计网格/厚度 |
|---|---|---|---|
| S24 | [Fallingwater_water11_source_S24.blend](../scene/Fallingwater_water11_source_S24.blend) | `c2b37ca465e4518295eafe9c0acfdd3b928dc91a751da8435946f34718c5a428` | 24×24×19，源厚3.07格 |
| S48 | [Fallingwater_water11_source_S48.blend](../scene/Fallingwater_water11_source_S48.blend) | `ff28f3447ab60792b60044ac249d77b2f35ac5f6dc54888a9c8083af48b3fef3` | 48×48×38，源厚6.13格 |

两臂源世界几何哈希均为 `3a3c4fc41cfbde3fd165ebdca6afb9d8efbf56d3092537a3e15b4c0431a31131`，与 water10 完全相同；速度不变。完整连续地形和 v3 核心岩作为实际邻岩保留，其他44碰撞体完全在局部域0.30m邻圈之外。源与保留岩体三角相交0，源采样净空最小0.937331m；源末端环重力位移采样最小净空0.373359m、内部采样0。岩床没有挪动、裁掉或添加假墙。

实际域顶点已校验，共同世界包围盒约 X[−0.24999985,1.55000019]、Y[−3.0625,−1.26249981]、Z[−6.13749981,−4.71249962]。原点由 water10 实际网格起点加整数粗格构造。**未运行求解器时 RNA domain_resolution 为[0,0,0]，表中格数仍是预期，不冒充原生缓存已观测网格。** 烘焙后审计会读实际 config/VDB 格数、格距和相位，差异必须保留报告。

两次新进程复开均通过，实际仅有FLIP主粒子，foam/spray/bubble/tracer全关；无初始水池。逐项参数、碰撞哈希及复开依据在 [prepare.json](water11-source-prepare.json)。新建域初始读取 particle format 的枚举警告以及 Blender 扩展缓存目录写入被拒日志保留；实际赋值及两次复开均为UNI，准备场景正常保存，未修改全局扩展设置。

根按臂执行，下列每条只启动指定的单臂；不在本代理准备过程中执行：

```powershell
& 'D:\zx\test\project\qa\water11-source-start.ps1' -Arm S24 -ApprovedByRoot
& 'D:\zx\test\project\qa\water11-source-start.ps1' -Arm S48 -ApprovedByRoot
```

[监控入口](water11-source-start.ps1) 的90秒包括子进程加载、哈希/复开预检与烘焙，精确监控自己创建的PID；缓存超过512MiB也中止。旧日志、已存在缓存或缺少审批开关会在启动前拒绝。超时只保留partial，不重试、不延长、不渲染。完整旧缓存648文件、4,445,517,893字节已在准备前后全哈希核对不变；每臂启动再核对该清单，读哈希成本算在90秒预算内，实际模拟可用时间相应减少。保存baked独立文件，不覆盖prepared场景。

烘焙完成或监控中止之后，运行独立只读审计（不计入90秒模拟预算）：

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --threads 4 --python-exit-code 7 --python 'D:\zx\test\project\qa\water11-source-audit.py' -- S24
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --threads 4 --python-exit-code 7 --python 'D:\zx\test\project\qa\water11-source-audit.py' -- S48
```

审计从 **frame1** 到全部12帧，读作者水平截面、phi湿面积、原生网格截面、MAC速度与Q，并独立核对源内速度。平面为源内 z−5.35 与源下−5.58/−5.64/−5.68；原始时基/单位由该臂 config T 差计算，不用作者Q校正结果。源有限几何在下方截面面积为0，不能把过流面积除以0；下游比较输送通量。保留体积、粒子包络/计数、首帧偏差及原生网格映射误差。**frame1 是已推进的首帧，不是真正t0。** 若volume-only、首帧网格未写或只有partial，报告明确NOT_AVAILABLE，不用末帧代替首帧，也不假定0体积。

审计脚本通过已知闭盒的截面面积/体积与匀速湿面积通量解析自检；Python编译与PowerShell解析通过。后续真实12帧审计已完成，并修复坐标四舍五入造成的截面连接误判，原结果保留，详见 [source-review](water11-source-review.md)。完整实验解释见 [water11-design](water11-design.md)；脚本自检与空气域结果都不构成最终连接或视觉通过。
