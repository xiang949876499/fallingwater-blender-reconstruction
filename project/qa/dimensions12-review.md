# 第12轮保存模型尺寸汇总

**同一冻结12a内现有21个独立印刷名义尺寸通过原数值门槛；GEO-02仍INCOMPLETE。** 合并提案共50行：29项数值PASS，其中21项可计入独立印刷名义断言，8项仍为SOURCE_PRECISION_LIMIT；另21项NOT_RUN。数量达标不能代替悬挑类别及未解决的来源/端点问题。

输入：[Fallingwater_integration_candidate12a.blend](D:/zx/test/project/scene/Fallingwater_integration_candidate12a.blend)，SHA256 `50e0a8fc0bab10fdec0e0b9d26c4ef4a4c71fa56aea6401e75197787c8c0e75a`。新后台Blender5.2.1 LTS、CPU4，实际打开该保存文件，进程exit0；没有应用建模helper、保存场景或渲染。

整合产物为[50行CSV提案](D:/zx/test/project/qa/dimensions12-integration12a-merge-proposal.csv)及[完整合并JSON](D:/zx/test/project/qa/dimensions12-integration12a-merged.json)。CSV保留中央列名，并追加独立计数、实际范围、最大采样误差及来源报告列；`model_m`对多站项只是中位数展示，是否通过由全部站点及最大误差决定。中央`dimensions.csv`未写入，根可按稳定`component_id`审阅后合并。

| 新鲜测量组 | 行数 | 数值PASS | 可计独立名义PASS | 精度/端点受限 | NOT_RUN |
|---|---:|---:|---:|---:|---:|
| 原dimension_audit实际44项 | 44 | 23 | 15 | 8 | 21 |
| 原supplement12四项 | 4 | 4 | 4 | 0 | 0 |
| 北整樘完成面与塔连续帽顶 | 2 | 2 | 2 | 0 | 0 |
| 去重后总计 | **50** | **29** | **21** | **8** | **21** |

原44项完整结果保留在[central44.json](D:/zx/test/project/qa/dimensions12-integration12a-central44.json)。调用原`audit_dimensions(..., write_csv=False)`，未改变其名义数据、测量选择或15项既有资格规则。8个客房房间标签的面/轴解释和来源精度仍受限，未因几何数值吻合而纳入21项。21个未测项没有继承旧版本PASS。

本次4项补充与2项新增在源标注、端面和稳定ID上核对中央44项，没有同一印刷标记的中央别名；所以没有中央ID需要替换。旧QA中的`MAIN10_*`、`SOURCE08_*`和`GUEST10_*`身份原样沿用，不能把09/10/11/12不同候选的同一断言再次相加。三露台各9站、桥9站、北整樘2556站与塔东西完成面复核，各仍只算相应的一项。

| 稳定来源ID | 印刷名义m | 12a实际m | 最大绝对差mm | 结果及实际端点 |
|---|---:|---:|---:|---|
| MAIN10_L2_WEST_TERRACE_X | 8.820150 | 8.820149899 | 0.000578 | PASS；西露台护墙西外面→更衣西石墙西面，两面均向西，非内净距/悬挑 |
| MAIN10_L2_WEST_TERRACE_Y | 5.343525 | 5.343525887 | 0.000887 | PASS；西露台北外面→南外面 |
| MAIN10_L2_SOUTH_TERRACE_X | 7.753350 | 7.753350735 | 0.001688 | PASS；南露台西外面→东外面 |
| SOURCE08_MAIN_BRIDGE_SOUTH_STONE_GAP | 4.038600 | 4.038599014 | 0.000986 | PASS；南侧两石端向内竖直端面；不是混凝土护栏、全桥最大宽或桥面净宽 |
| GUEST10_THEATER_NORTH_BAY | 2.486025 | **2.469984114..2.502110541** | **16.085541** | PASS；整樘两实际完成石面，全2556站均满足20mm；中位数2.485694051仅展示 |
| MAIN_TOWER_CONTINUOUS_COPING_RELATIVE_MAIN_TERRACE | 9.994900 | **9.994900063** | 0.000063 | PASS；实际连续帽顶→实际首层西露台完成面；东露台完成面一致 |

四锚点来自原[dimension_supplement12.py](D:/zx/test/project/scripts/dimension_supplement12.py)的`measure(scene)`，逐站命中、法向、三角形/多边形号与源引线资格存于[four.json](D:/zx/test/project/qa/dimensions12-integration12a-four.json)。前三项印刷为28′11¼″、17′6⅜″、25′5¼″，桥为13′3″；均为A标称数字。这里的微小余差反映按名义值建模后的浮点网格，不是历史建筑测绘达到微米精度。

北整樘本次重新打开[原图北樘裁图](D:/zx/test/project/qa/guest-bays11-source-north.png)及[端点身份图](D:/zx/test/project/qa/guest-bays11-source-endpoints-final.png)，8′1⅞″的上下引线对应北墙内石面与pier2北长石面；不是27′9″/19′5″剧场整房跨度，也不是某一门扇通行净宽。新的只读选择器对**完整evaluated石皮批次**加两个真实石背衬做相反方向射线，未使用建模helper返回的course块号或其名义控制面。5112次命中中，4680次为实际石皮、432次为露出的背衬（北侧168、pier2侧264）；无漏射，所有面朝向入口射线。每次实际命中世界坐标、法向及三角形顶点都在[extra.json](D:/zx/test/project/qa/dimensions12-integration12a-extra.json)，避免把隐藏core净距或平均值代替完成面检验。采样覆盖仍是声明的有限面站，未宣称连续全域最小值证明。

塔高复核采用已独立确认的HABS主10 **MAIN TOWER32′9½″ / MAIN LEVEL TERRACE0′0″**；本次再次打开[原生标注与接线](D:/zx/test/project/qa/master-ceiling12-source-west-tower-labelled.png)。连续帽顶实际水平向上面Z=10.016900062561，西/东完成面均为0.021999999881，相减9.994900062680。突出帽顶的两个旧flue另测并明确排除，未借用最高物件替换源端点。结构面替代对照仍写入JSON：相对首层板顶0m为10.016900062561，和选定完成面结果相差22mm。中央MAIN_LEVEL_3/ROOF仍用结构面惯例；本轮没有暗改中央约定，也没有把主卧未解决的局部顶高算成通过。

证据等级保持分开：**A为清楚印刷值；源图形到模型面、XY配准、22mm完成层选择、石皮起伏/背衬分配均为C；绝对测绘精度、未标注构造和部分历史形体为U。** 塔连续帽顶相对标高通过，不等于旧帽板/烟口的形状数量已合源或照片级通过；相关12b保留问题与主卧SOURCE HEIGHT OPEN均不受本尺寸汇总影响。

| 类别 | 本12a独立名义测量覆盖 | 仍缺什么 |
|---|---|---|
| 主屋/客房 | 主屋来源含桥10项；客房来源11项 | 分类与下列功能类重叠，不能累加再计数 |
| 标高 | 11项相对标高 | 绝对测绘精度、主客楼共享高程和22mm惯例统一仍未解决 |
| 开口 | 1项客房北整樘 | 不代表单门净宽、主屋全部门窗尺寸；中整樘旧问题未复测/未通过 |
| 联系空间 | 1项laundry stair2′5″ | 复用中央72完成面站仍只1项，不是两楼共享基准 |
| 场地 | 1项南桥石端距；另有泳池局部尺寸 | 挡墙、溪流、地形及绝对配准没有因此通过 |
| **悬挑** | **本12a未测** | 已有独立C图形断言，但09的GRAPHICAL_MISMATCH与承托界面问题尚未在12a复核解决；没有可计印刷悬挑PASS |

旧`MAIN10_GRAPHICAL_L2_SOUTH_CANTILEVER`、service端点身份受限及`GUEST10_THEATER_MIDDLE_BAY`有限AB/非平行面问题在合并JSON的独立历史段保留，全部明确不是本场景新鲜实测。未把西露台总体投影、房间总跨度、桥别名、同一个标高的多个角或C图形比例凑入21项。**本轮仅完成尺寸汇总，不能据21个名义PASS宣称GEO-02整体通过。**

入口为[dimension_supplement12_integration.py](D:/zx/test/project/scripts/dimension_supplement12_integration.py)，SHA256 `a30224856ef9f77e45645818ae9c736f3c6ae1321bed5d2bf47afc54da20b799`。`measure(bpy.context.scene)`只返回上述2项；CLI另运行中央44项与原4项并写新前缀。它不导入任何建模helper。复现可参考[结构化参数启动文件](D:/zx/test/project/qa/dimensions12-run.py)，重跑必须选新输出前缀，保留既有报告。成功日志：[attempt02.log](D:/zx/test/project/qa/dimensions12-integration12a-attempt02.log)；第一次直接CMD引号启动在Blender前失败，见[attempt01记录](D:/zx/test/project/qa/dimensions12-launch-attempt01.json)。日志里的既有颜色空间/CUEW警告保留，本轮没有渲染或申请GPU。

前后全场景快照完全一致，包含所有对象矩阵/属性/mesh、相机、材质/图像/世界、灯光、动作关键帧、设置和嵌入文本。保存源SHA及中央CSV、原audit/supplement和四个输入数据文件的前后SHA一致，详见合并JSON。中央CSV仍为 `3b3c72b9fc27ad8daaed16df485e915f6fb9df365df089b91449c6c3ec645ffd`。按neat-freak作限定收尾：本组CSV/JSON、稳定ID、查看记录及失败记录已对应；根文档、AGENTS、其他helper和全部场景文件未修改。
