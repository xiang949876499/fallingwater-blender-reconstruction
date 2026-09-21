# 客房第06轮：池沿真缺口与低屋顶挑板

两项有界修正已完成并通过客房独立几何复验。输入冻结为 `scene/Fallingwater_iteration05.blend`，SHA-256 `6bcfee7841c22e8e2b636352cfca79ae94968afb4235fc20cdc57e250ae046ff`；没有覆盖它或 working。新独立模块 `guest-iteration06-module.blend` 的 SHA-256 为 `7d44d8e2310bcd749aad7949a9f1a447d5aa129c10866a92cd4f746a5802e92b`。

## 池阶入口

05水面缺口已正确，干阶上方仍有旧圆角 `GUEST_POOL_coping_16` 和相邻池壳穿过，造成身体撞到沿口。06按 guest01 的真实入口切除了阶梯横向范围内、客房地坪以上的池壳与沿口；保留地坪以下的壳和其余连续外圈。没有隐藏整座泳池、改掉池沿高度或只过滤碰撞对象。

修后沿入口前0.15m至末端平台后0.30m连续采样37点，步长不超过5cm。每点验证半径0.18m的5个脚下点、5条竖向身体射线和6条横向身体射线，共592条，全部通过。脚下以真实踏步高程为准，允许相邻级0.1762m高差；身体采样从足面上0.24m开始，既不把合法低踏级误判为墙，也能检测原0.53m沿口障碍。

负向控制直接从05冻结文件追加同一个旧 `GUEST_POOL_coping_16`，其真实网格使12个路径样本失败。失败逐点保存在 `guest-iteration06-pool-roof.json`，随后仅在验证进程内移除旧物件；测试没有改写生产源场景。

## 原图确认屋檐与退后女儿墙是两条轮廓

实际查看 guest01、guest02 的原始 TIFF、guest03立面、guest04剖面和 A10原照片。guest02 南侧约 y431–435 的粗双线是退后的女儿墙；外侧白色挑板延伸到 lounge 区 **y488.7**，在 **x488** 转折至 pergola 区 **y477.2**，东界 **x681**。原图的8个短矩形和2个长矩形是这块挑板的开孔。旧模型用了接近室内轮廓的整块板，并用8根孤立条近似外侧格栅，遗漏了宽挑板及其连续边框。

06将板外轮廓和女儿墙轮廓分开。挑板与其薄表面层都真正扣除10孔，移除旧孤立格栅条；维持原板底高程+2.16m、板厚0.19m和图纸标注女儿墙顶+3.29565m。南窗外面约Y36.0266，外檐约Y33.5836，外伸现约 **2.44m**。这些坐标来自原图轮廓，未按 A10 的232.50px残差或 R01点拟合；R01纵向站位仍为 U。

原图 tracing 约1px误差、北边凹凸节点及连接区背面仍为 C/B 级解释，不是新增的A级尺寸标注。外檐宽度修正会影响客房照明，需整合者重新渲染实际镜头再校准曝光。

实际查看的源图和模型叠合：

- `guest-iteration06-grid-guest-01.png`、`guest-iteration06-grid-guest-02.png`：独立原图裁切及分析网格。
- `guest-iteration06-roof-south-source.png`、`roof-west-source.png`、`roof-east-source.png`：外檐、折角和两种真实开孔的高分辨率原图。
- `guest-iteration06-roof-overlay.png`：红线为**实际 evaluated mesh**板底边/孔边，蓝线为女儿墙；叠在原始guest02同坐标裁切上。已实际打开检查。

叠合检查曾发现北侧女儿墙局部超出旧直线板边，实际支撑测试出现3个失败。按同一原图北侧折线补齐板边，并保留约0.4px的实体支撑余量；复测81个墙底采样均命中板。首次失败保留为 `guest-iteration06-parapet-first-fail.json` 和同名 `.blend`，没有删除证据。

## 回归结果

Blender5.2.1 LTS，新后台进程、CPU4，无渲染/GPU。

| 检查 | 结果 |
|---|---|
| 同组22项实际网格尺寸 | 17 PASS / 0 FAIL / 5 NOT_RUN；GEO-02容差未放宽 |
| 上楼梯47点 | 47 PASS，最小2.120m；旧坏板负向12 FAIL |
| 地下梯42点 | 42 PASS，最小2.180m |
| 原7门及两新门脚下 | 7门/18脚下点 PASS |
| 第05轮池阶12脚下点 | 12 PASS |
| 第06轮连续池阶37点 | 37 PASS；旧精确coping16负向12 FAIL |
| 壁炉真实空腔 | 4 PASS；未改变第05轮火口 |
| 10个真实屋顶孔 | 30射线 PASS；同时穿过板与薄表面层 |
| 连续挑板底 | 6处 PASS |
| 女儿墙实际板支撑 | 81/81 PASS |

复算入口：`guest-iteration06-check.py`、`guest-iteration06-pool-roof-check.py`；详细证据分别为 `guest-iteration06-dimensions.json`、`upper-clearance.json`、`geometry.json`、`pool-roof.json`。原图叠合实际边记录为 `guest-iteration06-roof-edges.json`。每次进程日志均保留；Blender全局扩展缓存权限提示未通过修改权限消除。

## 冻结交接

仅修改 `scripts/guest_house.py` 和 `data/guest_house.json`；`guest_architectural_detail.py` 保持05已通过状态。变更前模块/数据副本在 `qa/guest-iteration06-before-*`。05成功工作未重做，邻接语义、客房基准、门位、火口、楼梯与曲廊端点均保持。

整合者须在新全场景重验 ADJ051 的所有障碍、屋顶与主客廊道接头，以及扩大遮阳后的客房实图。此次不做照片对应残差的成功声明、也不声称完整导航/120机位/影片已完成。按 neat-freak 在本轮负责的证据文档中同步真实状态；README、STATUS和全项目结论留给整合者统一更新。
