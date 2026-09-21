# Water11 S48：隔离重现已准备，根安排唯一运行

**后续实际状态：根已完成唯一12帧重算，新只读审计也完成。24文件SHA相同/12个VDB不同SHA，全部历史逐帧量测精确相等；正确状态为重现，不是原文件恢复。见 [reproduction-review](water11-source-reproduction-review.md)。以下是准备阶段记录，不能重跑历史命令。**

2026-09-21，**`REPRODUCTION_FRESH_REOPEN_PASS_NO_BAKE`**。准备与新进程只读复开退出0，未模拟、未渲染。目标是在独立路径重现S48以重新获得可检查数据；原36文件已丢失的 [事故](water11-source-cache-incident.md) 没有被消除，R075继续暂停。

新场景 [Fallingwater_water11_source_S48_reproduction01.blend](../scene/Fallingwater_water11_source_S48_reproduction01.blend) SHA256：

`a97e8f0db32cb22ae87f10b71d1cb56131f84e477d6a0283281f60ac0de84fe2`

[准备/复开证据](water11-source-reproduction-prepare.json) 实测：

- factory新场景仅加载3个原静态Mesh datablock，旧Objects/Collections/Scenes/FLUID modifier均未载入。源和两个实际邻岩在identity变换下的世界几何哈希与原S48逐项一致。
- 所有原S48主物理参数零差异：48res、12帧、24fps、CPU4；primary radius仍1.0，mesh radius仍1.25。实际只有FLIP主粒子，secondary全部关闭，原source速度/形状/域原点不变。并非R075对照。
- 新domain建立后的首个设置赋值就是独立空cache路径；所有随后物理参数赋值前/后均验证唯一域只指向新路径。没有打开原旧流体场景修改RNA。
- 684个残存缓存准备前/后、复开前/后逐文件哈希全部一致；旧36缺失路径仍缺失。准备场景哈希复开前后不变，新缓存0文件。
- 首次加载试验因 Blender library API 将赋给 `data_to.meshes` 的可变list转成Mesh对象，导致名字集合断言失败；失败发生在新FLUID创建之前，没有保存场景或缓存。改为保留immutable名字tuple后通过。原 [prepare.log](water11-source-reproduction-prepare.log) 保留，成功为 [prepare2.log](water11-source-reproduction-prepare2.log) 与 [reopen.log](water11-source-reproduction-reopen.log)。默认液体枚举过渡警告和无关默认材质相对路径警告也保留，实际最终RNA/UNI复开检查通过。

由根执行一次，**本准备过程没有执行**：

```powershell
& 'D:\zx\test\project\qa\water11-source-reproduction-start.ps1' -ApprovedByRoot
```

监督器使用独立 `project/qa/water11-isolated-recovery/` 工作目录，保存到 `project/caches/fluid_water11/source_S48_reproduction01/`，只监控自己创建的PID，CPU4、90秒总硬停、512MiB缓存上限。非空新缓存、已有日志/报告均拒绝重跑；超时保留partial，不重试、不延长。90秒包括加载、684文件守卫、求解与最终检查；原S48监控34.7092秒/solve5.3037秒仅供参考。

烘焙完成后独立保存 `_baked.blend`，不覆盖prepared。runner会将36个输出文件逐项与事故前缺失清单的原SHA比较；任何差异写 `REPRODUCTION_NOT_BYTE_RESTORATION`，全部相同时写“重算副本与原36哈希一致”。旧路径始终不回填，不把新结果写成原始文件恢复。

监督器完成或超时保留完整帧之后，另做只读全帧审计：

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --threads 4 --python-exit-code 7 --python 'D:\zx\test\project\qa\water11-source-audit.py' -- S48_reproduction01
```

此审计保留首帧、全部12帧原始phi/MAC/mesh/速度单位；输出新前缀，旧S48审计和失败不覆盖。原比较Q=0.4675332738m³/s等是待重现的真实历史数据，不能以相近终点替代全帧和文件身份比较。Python语法和监督器PowerShell解析均通过；尚无此新臂实际求解/流量结论。

下一完整水体独立设计在 [water12-complete-plan.md](water12-complete-plan.md) 与 [JSON](water12-complete-plan.json)。这份恢复准备不授权R075或大型水体运行。根的STATUS和生产场景未修改；本阶段使用 neat-freak 收尾方式更新了水体ready/历史数据可用性和事故交接，未扩写全局规则或回退其他代理文件。
