# Water11：S48 原缓存清除事故与隔离恢复方案

2026-09-21。**R075 已暂停。fluid_water 的准备脚本错误地先修改沿用旧缓存路径的液体参数，导致 S48 原有36个缓存文件、7,748,027字节丢失。** 没有启动 R075 烘焙，也没有擅自重算 S48。责任在本次准备动作，不能归为原模拟失败。当前不可声称旧缓存保持不变。

## 实际发生与证据

1. 准备前已为720个旧文件、4,455,960,343字节计算逐文件 SHA256，清单为 [准备前清单](water11-source-r075-preserved-cache-manifest.json)。
2. 脚本打开原 S48 prepared 场景，读取/验证成功；此时域的 `cache_directory` 仍指向 `caches/fluid_water11/source_S48`。
3. 错误顺序是 `d.particle_radius=.75` 后才创建新目录并设置 `d.cache_directory`。Blender 随后保存了独立 R075 场景，但最终旧缓存清单断言失败，进程退出1。实际日志保留在 [失败日志](water11-source-r075-prepare.log)。
4. 后续纯文件审计发现恰好 S48 的12个 config、12个 VDB 和12个 mesh 文件缺失；其空 guiding 目录尚在。没有执行显式删除命令。**“物理 RNA 更新使旧路径缓存失效并清除”是由动作顺序与结果支持的最可能原因，尚未独立追踪到具体 Blender 回调。** 不为查回调再触及旧场景参数。
5. 在整个 project 中查找与缺失文件相同大小的文件并逐项比较 SHA256，未找到原始字节副本。未把其它帧或其它分辨率缓存当作替代品。没有对用户磁盘进行删除恢复、全盘扫描或系统设置修改。

[事故 JSON](water11-source-cache-incident.json) 保存缺失36文件的原哈希、当前残存全部684文件的哈希、源场景及水体审计文件哈希、核验时间与副本搜索结果。只读审计脚本为 [incident-audit.py](water11-source-cache-incident-audit.py)。

| 独立核对的缓存范围 | 当前文件数 | 当前字节数 | 相对准备前哈希 |
|---|---:|---:|---|
| water08/static_head24 | 96 | 355,096,749 | 全部相同 |
| water09/real_bed_default24 | 72 | 192,553,687 | 全部相同 |
| hybrid07/impact36 | 144 | 1,054,473,339 | 全部相同 |
| water09/impact36 | 144 | 392,190,824 | 全部相同 |
| water10/natural48 | 192 | 2,451,203,294 | 全部相同 |
| water11/source_S24 | 36 | 2,694,423 | 全部相同 |
| water11/source_S48 | **0 / 原36** | **0 / 原7,748,027** | 原文件缺失，不能复核 |

S48 prepared 场景仍为 `ff28f3447ab60792b60044ac249d77b2f35ac5f6dc54888a9c8083af48b3fef3`；prepared 与 baked 场景、原监控/模拟日志、每帧审计 JSON、完整12帧审计与原始缓存哈希仍保留。已保存但未复开的 R075 场景 SHA256 为 `7b50ed8c513026dc736bbeb6c42b8118f7c5cb2a04484724eab1bada6fd395ed`，它是**事故后的未就绪候选**，不是可启动交付。

原 S48 的已观测 Q=0.4675332738m³/s、原诊断失败与细格比较仍是事故前真实审计历史，不能更名为未测，也不能借事故重写结论；现在其底层原缓存无法重读。报告区分历史测量记录与当前可复现数据可用性。

## 已实施的止损

- 没有继续 Blender/RNA 写入、复开、烘焙或渲染。准备脚本的 prepare/reopen 入口都已在任何操作前硬拒绝。
- 通用监控的 `S48_R075` 分支已硬拒绝，避免误用之前交接命令。S24/S48 已运行日志也仍阻止重复旧臂执行。
- 原准备前清单未覆盖；原日志、失败场景和缺失证据未删除。没有把当前684文件清单替换成“所有旧文件均保持”的新基线。
- 当前模型和生产场景未写入。根决定后续恢复路径；本报告没有授权或启动恢复。

## 推荐恢复：新 factory 场景，仅引入静态网格，不打开旧流体场景修改

单纯复制旧 .blend 到新工作目录**不够**：绝对缓存 RNA 仍可指向原目录。单纯交换两个 setter 顺序也不作为隔离保证。

建议下一项准备使用全新 `project/qa/water11-isolated-recovery/` 工作目录、新场景和 `project/caches/fluid_water11/source_S48_reproduction01/` 缓存。原 S48 路径保持空缺历史状态，永不作为新输出目录。流程如下，当前仅方案：

1. 用新的 factory 后台进程启动。**不调用 `open_mainfile` 打开任何带原流体域的 .blend，不 append 原 Objects/Collections/Scenes，不复制原 FLUID modifier。**
2. 在 `bpy.data.libraries.load` 中只读取原 S48 的三个指定 **Mesh datablock**：`WATER11_Exact_Frozen_Inflow` 以及 prepare.json 中两个 collider 名称。加载 Mesh 不引入对象、modifier 或域缓存 RNA。源顶点也可直接使用原 prepare.json 中已保存数组。原构建 helper `mesh()` 用世界顶点创建 identity 对象，因此三个原网格在 identity 下的 world-geometry SHA 必须逐项等于 prepare.json；不相等就停，不能猜变换。
3. 创建全新对象、全新 FLUID 设置。新 domain 建立后立刻指向全新空缓存；在所有物理参数 setter 前断言场景只有这个新域、其缓存规范化路径位于隔离目录，任何旧缓存路径均未进入 RNA。所有 flow/effector 也新建，不继承旧modifier。
4. 主参数逐项设回原 S48 的冻结值（`particle_radius=1.0`），原物理、几何、域原点、帧率、时步、线程、源速度和 mesh radius 全部原样。恢复试验不能同时加入 R075 改动。幂等关闭 secondary。
5. 保存到新 recovery scene，退出；新进程只打开这个已隔离场景、读取检查全部实际参数/几何哈希和所有 cache/output 路径，再退出。此时复开不修改物理设置。分别核对完整残存684文件及原场景/审计证据哈希不变。
6. 根审核后唯一 CPU4、48res、12帧、90秒硬停止，独立日志。原 S48 实际 solve 5.3037秒、监控34.7092秒、7.75MB，可作为预算依据，不能保证新运行字节完全确定。读取哈希成本包含在总预算；新缓存512MiB也中止。
7. 完成后将新输出逐文件名、大小、SHA256与事故前 S48 清单比较。若所有36文件全部同字节，只能说新目录中获得了**与原清单一致的重算副本**，事故与原文件被清除的事实保留。任何文件不同则标记 **REPRODUCTION_NOT_BYTE_RESTORATION**，保留两个清单及旧审计，逐帧重新测量而非覆盖旧审计。
8. 数据压缩头/时戳等可能造成文件 SHA 不同；即使另做解码数组比较相同，也仅能报告内容比较，不称原文件恢复。原输出路径不回填，原FAIL不被新结果追认PASS。

后续状态：根已批准并完成此 factory 隔离准备及新进程只读复开，见 [reproduction-ready](water11-source-reproduction-ready.md)。尚未烘焙，不代表原缓存恢复。若根有真正备份，优先只读逐文件比原清单并复制到独立 restored 目录；本项目内搜索未找到。R075 在恢复/基线处置明确前继续暂停。
