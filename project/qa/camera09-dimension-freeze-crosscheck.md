# 09尺寸记录与生成数据来源独立复查

**记录关联与生成数据分类自洽；尺寸总体验收仍为 INCOMPLETE。** 本次只读核对记录、源码调用顺序和当前文件哈希，没有重新建模、测量、导出或修改中央CSV。

最新记录 [dimensions-build-20260920-165955.json](D:/zx/test/project/qa/dimensions-build-20260920-165955.json) 写的是构建保存时路径 `scene/Fallingwater_working.blend`。其顶层和全部44行的场景SHA均为 `489b05e403aa9d02c3568a8e3813a24235ee5b7e782df4d1f149b3ff6673e331`，与实际读取的冻结 `Fallingwater_iteration09.blend` 及当前 working 文件完全相同；冻结文件44,414,422字节。因此该尺寸记录精确关联完整09，文件名中的build时间不是迭代号。

| 逐行重新计数 | PASS | SOURCE_PRECISION_LIMIT | NOT_RUN | 总数 |
|---|---:|---:|---:|---:|
| 数值比较 | 23 | — | 21 | 44 |
| GEO-02标准分类 | 15 | 8 | 21 | 44 |

23个独立测量项满足至少20项的数量门槛，但不替代类别覆盖。悬挑长度、门窗净尺寸仍缺测；场地只覆盖泳池部分。8项来源精度受限分别为锅炉房两尺寸、客房长/深、洗衣房长/深、基础层浴室长/宽，不能并入15项标准PASS。房间标签对应面和轴的解释仍标C；类别之间重叠，不能相加制造更多锚点。

主屋数据来源复查结论：`main_house.build()` 在返回房间前调用 `export_data(ctx.root/'data'/'main_house.json')`，而 `export_data()` 从源码常量及房间函数构造对象，不读取旧主屋JSON。`build_scene` 随后才读取新数据生成清单，保存 working 场景，再运行尺寸审计。于是冻结 `inputs` 中 `85c0ce86bc27dfc2f0f9d91f1e2fe2068348f70bfd1db5349e76d7e2562b97bf` 是上一版输出快照，而非本次主屋构建的不可变输入。

冻结记录已明确保留该历史快照，并以 `generated_outputs` 单列本次输出 `be830b3d37b53726bb4919f4732b9439792bc82af2f418480199d4cd2ec4e3ac`。该值同时匹配当前文件、尺寸审计数据哈希、已执行独立源码导出记录的UTF-8/Windows-CRLF字节哈希；JSON差异列表为空。嵌入冻结记录的生成数据证据与独立报告完全相同。其余23个冻结输入（含主屋源码）本次逐个复算均未变。

分类修正是自洽的，但读取该冻结文件的下游应使用 `generated_outputs` 判断当前主屋数据，不能把 `inputs` 的旧快照误作当前值。初次把所有路径都当不可变输入、及只用LF比较产生的失败日志继续保留。本复查审核该既有复现证据，没有再次执行导出。

机器可读逐项检查、44行分组ID及23输入哈希见 [camera09-dimension-freeze-crosscheck.json](D:/zx/test/project/qa/camera09-dimension-freeze-crosscheck.json)。导览与保存机位结论分别见 [tour-path-iteration09-review.md](D:/zx/test/project/qa/tour-path-iteration09-review.md)、[camera09-review.md](D:/zx/test/project/qa/camera09-review.md)。没有改动中央 `dimensions.csv`、任何生产源码或冻结场景。
