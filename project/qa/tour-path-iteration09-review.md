# 完整09连接与全部整数帧独立复验

**总状态：FAIL_FULL_CONNECTION_GRAPH_NO_CHECKED_SCENE_SAVED。** 全部7,584整数帧通过，但60条连接中仍有2条失败；没有保存checked09，也没有将候选导览标为可交付。

冻结输入为 `scene/Fallingwater_iteration09.blend`，44,414,422字节，SHA-256 `489b05e403aa9d02c3568a8e3813a24235ee5b7e782df4d1f149b3ff6673e331`。先完成 [camera09-review.md](D:/zx/test/project/qa/camera09-review.md) 的120个实际保存机位读取和比对，再运行本轮隔离导览检查。Blender5.2.1 LTS后台CPU4、无渲染/GUI，审计过程退出0表示执行完成，不能覆盖下列连接失败。

| 检查范围 | 实际结果 |
|---|---|
| 保存机位参数 | 120/120匹配冻结设置 |
| 保存机位几何 | 120/120 GEOMETRY_ONLY_PASS，3,840射线 |
| 完整连接图 | 58 PASS / 2 FAIL / 0 NOT_RUN |
| 正常行走连接 | 50 PASS |
| 仅观察连接 | 8 PASS；不声称可步行 |
| 主片整数帧 | 10段，2,880帧通过 |
| 补充片段整数帧 | 49段，4,704帧通过 |
| 总整数帧 | 7,584通过，0几何失败 |
| 检查空间覆盖 | 60/60；不是60个卧室 |
| 主片选用门连接 | 7项通过；不替代60图 |

`ADJ_041`（客房车庭→一层楼梯厅）再次得到 `FAIL_NO_VALIDATED_BODY_PATH`。0.24米网格有界转弯搜索访问388点、测试549点，未找到通过体柱/相机净空的路径。实际碰撞示例包括 `GUEST_LAYERED_SANDSTONE_COURSES`（眼点1.07422,41.05479,10；前方0.05875米即命中石饰）及 `GUEST_LAUNDRY_DESCENT_outer_retaining_wall`。失败具体证据保留，不能因预期失败而跳过，也不能把有限搜索失败解释为建筑绝对不存在通路。

`ADJ_054`（客房一层楼梯厅→二层厅）再次得到 `FAIL_STAIR_ROOM_ATTACHMENT`。真实命名踏步中心线的上端接入通过，下端接入未验证；下端搜索访问156点、测试235点。眼点2.09861,40.25407,10.03361处体柱命中洗衣下降外挡墙，另在2.89542,38.24989,10.04801等点发现预期地面8.44801下未获得有效支撑。完整踏步、接入例及搜索结果保留在 [tour-path-all-adjacency-iteration09-attempt01.json](D:/zx/test/project/qa/tour-path-all-adjacency-iteration09-attempt01.json)。

整数帧检查读取新建候选动画的实际依赖图相机世界矩阵，并与同时间参数的预期折线路径比较，逐段检查相机位置和前一整数帧扫掠；步行段还检身体和地面。跨段剪切没有假造连续扫掠，因此全部帧PASS与两条未验证连接可同时成立。总计1,305,469次探测射线，其中整数帧网格射线150,694次。已撤回、缺乏源支持的Loggia→东露台直接连接没有重新伪装成有效边。

隔离与保存控制：先直接读取09保存机位，再把本次主屋/客房数据、配置与邻接CSV逐字节复制至专属 `tour-path-iteration09-attempt01-workspace`。只将未改动导览模块的内存输出根切换到该目录，在09实际网格中创建候选动画并检查；不调用场景保存。规范化副本明确记录 `accepted_for_delivery=false`、`checked_scene_saved=false`、`checked_blend=null`。原始模块输出也保留供追溯，不能当交付授权。

检查结束时，源场景SHA不变、120个原保存机位变化数为0；12个受保护生产文件全部逐字节不变（主屋/客房数据、配置、邻接CSV、生产路线、机位设置及6个相关源码）。生产 `data/tour-route.json` 没有被覆盖；09候选路线只是测试证据。没有创建任何checked09场景。

主要证据：[tour-path-iteration09-attempt01-result.json](D:/zx/test/project/qa/tour-path-iteration09-attempt01-result.json)、[tour-path-camera-coverage-iteration09-attempt01.json](D:/zx/test/project/qa/tour-path-camera-coverage-iteration09-attempt01.json)、[tour-path-check-iteration09-attempt01.json](D:/zx/test/project/qa/tour-path-check-iteration09-attempt01.json)、[tour-path-input-freeze-check-iteration09.json](D:/zx/test/project/qa/tour-path-input-freeze-check-iteration09.json)。本轮重现了08遗留的同两条失败，没有新增连接失败；这不代表真实照片匹配、120张图外观、最终影片或交互导航已通过。最新尺寸44行与09场景的精确关联和生成数据分类另见 [camera09-dimension-freeze-crosscheck.md](D:/zx/test/project/qa/camera09-dimension-freeze-crosscheck.md)。
