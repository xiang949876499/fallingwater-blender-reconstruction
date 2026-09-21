# 陶瓷10：整合者同机位复核

状态：**REJECT_VISUAL；不并入生产。**

实际打开候选 `renders/previews/ceramic10/CAM_MAIN_L3_BATH_A.png` 与冻结09 `renders/previews/iteration09-focus/CAM_MAIN_L3_BATH_A.png`。两图960×540、Cycles CPU8、48samples、frame48。候选SHA256 `2cc9f029cb8fba653ef8f93ac7ba3ab1d5ed9d9323249e6391cc157623cd5157`。

候选外轮廓较圆，但盆内被大块封闭底面盖住，排水盆腔形态退步。闭合边数为零不能替代正确形体；这里新增闭底虽通过拓扑检查，却不符合预期可见结构。保留候选与失败证据，不在生产调用 `furnishing_ceramic10.py`。

当前只有L3一套通用坐便器被尝试。Master浴室新照片明确显示无外置水箱的冲洗阀式器具，与该通用水箱式模型不同；支承/排污脚具体构造待高清图核实，不能径称悬挂式。需要按相应房间来源单独重建，而非全局套用该候选。
