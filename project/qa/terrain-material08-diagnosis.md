# 完整08森林地表材质诊断

状态：READ_ONLY_DIAGNOSIS_COMPLETE；整体环境VISUAL_FAIL。根任务已将bank08路径几何修复、surface_tint=False合入完整08，本报告不修改该状态或场景。

来源为`scene/Fallingwater_iteration08.blend`，SHA256 `c5cd501e4c8ae0205ecb2437cd2d06d0c92bcc9a87e7d93d3986aeef976070d7`。CPU4新进程只读检查，源文件哈希始终不变。证据：`terrain-material08-probe.py/json/log`及`terrain-material08-image-stats.py/json`。

## 实际查看记录

- `renders/previews/iteration08-focus/CAM_HERO.png`：近西坡仍是连续浅色土体，细草纹清晰于近部但没有相应叶层/根石轮廓，稀疏灌丛难以打断大面。
- 同目录`CAM_MAIN_L1_LOGGIA_B.png`：道路埋土已消除；坡脚接触正确不等于整个前后坡真实。图左侧坡面能看见细草纹，主体仍是连续光滑黄灰绿色面。
- 同目录`CAM_MAIN_L1_LIVING_A.png`：窗外多数地面是中远距离浅灰绿色，室内亮度提高使外部更淡；不能把画面全部归给近30m岸边。
- `assets/textures/forrest_ground_01_diff_2k.jpg`及`disp_2k.jpg`：确有绿色草/苔藓、土、细枝、少量碎叶，非厚阔叶落叶层。实际图像不是纯灰色或缺失占位图。
- `data/photo_refs/main_sw_87.jpg`：瀑布西侧是岩面及较密常绿灌丛、根部暗部，不支持全幅光滑裸草坡。
- `data/photo_refs/main_east_88.jpg`：林地背景、枝干/灌丛和暗色地表分层可见；不能从该视角测定Loggia前坡高程或得到其真实反照率。

87/88是不同相机与光照的历史照片，不能直接采其RGB当作当前合成基线的土壤测色。`research/interiors.md`第6节支持砂岩、林下灌丛、枯枝/叶/苔藓的分层；物种和每个点的高程仍不由这些照片确定。

## 保存场景中的事实

terrain唯一材质槽为`FW_Continuous_Forest_Floor`，216,572个三角面全部slot0、全部smooth，108,945顶点，无modifier。对象世界矩阵单位、scale=(1,1,1)。08标记明确`surface_tint:false`，没有bank07b/08染色权重属性。

有效节点链：

```text
Texture Coordinate.002.Object → Vector Math.001(SCALE=0.5)
   ├→ PH_Diffuse(sRGB) → MULTIPLY(.85,.92,.80) → Principled.Base Color
   ├→ PH_Rough(Non-Color) → Map Range(0..1 → .7..1) → Principled.Roughness
   └→ PH_Displacement(Non-Color) → Bump.001 → Principled.Normal
Principled → active Material Output.Surface
```

三张2048²外部图均存在，MD5与已有官方文件记录一致；有效链没有mute，指向活动输出。Object没有额外坐标对象，BOX投射、blend=.22、Linear、REPEAT。实际为XYZ各2m一周期，未按整个2080m地形拉伸，也没有对象scale将纹理缩成厘米。**2m是现有作者设定，不把它升级为扫描厂商实测覆盖范围。**

`site.py::_terrain`原先的暗色噪声ramp现在在输出不可达路径上；`asset_materials.apply`替换了Base Color和Normal输入。不能拿那个暗色ramp值解释保存材质，也不能因它存在就声称保留了宏观土色变化。

Bump Strength=.5，Distance=.045m，height接线有效，Material Output.Displacement未接，terrain无真实位移。输入height并不平：灰度5/95百分位约.192/.529。它能扰动法线，却不能制造树根、石块、落叶边缘或改变坡轮廓。只读probe没有执行Cycles着色器数值求值，因此结论是“路径有效且设置非零”，不是虚构一张法线AOV。

Rough贴图本身.867…1、均值.9365；再映射后输出约.96…1、均值.981。几乎全极哑光，但没有错接金属、透明、涂层或自发光：这些权重为0。不是湿塑料/镜面反射把地面涂白。

## 为什么仍像浅灰光滑坡

优先级1是地景与素材类型：原图主要是细草、苔藓、细枝，缺少清晰宽叶边缘和腐殖物团块；同一种2m图覆盖所有地形，草丝微观频率与光滑坡体之间缺少能在当前机位读到的中尺度结构。单一材质替换可以隔离表面类型问题，但不会修好原宏观坡形、树冠和遮蔽。

像素射线和相邻射线计算得到的实际世界足迹如下；它不是Cycles精确mipmap级别。

| 机位与像素 | 实际命中 | 距离 | 一个像素地表足迹 |
|---|---|---:|---:|
| HERO (100,415)/(220,470) | 西坡terrain首命中 | 29.4/32.1m | 32.5…40.9mm |
| Loggia B (110,210)/(320,260)/(380,170) | terrain首命中 | 11.0…12.5m | 12.9…24.4mm |
| Living A (540,200) | terrain首命中，世界(60.53,-8.34,1.01) | 60.2m | 80.8/473.5mm |

HERO一像素已覆盖多条毫米级草丝；Loggia较近能读草纹，但仍无厘米级实体轮廓。Living A中心的浅色地面不是bank08范围；另两个采样地面在124/143m，但被玻璃/树干首命中，已在原始JSON明确标注，不当作无遮挡地面测色。

优先级2是曝光和环境遮蔽。根实际渲染记录HERO/Loggia +.8EV，Living A +2.4EV，分别相对0EV约1.74倍/5.28倍，Living较前两者高1.6档。世界强度.36，太阳2.5，林冠稀疏让大片坡面直接受光；AgX压缩与远处纹理平均化可使颜色更淡。**没有仅凭图像给曝光错误分配百分比，也不建议为地面盲调全屋曝光。**

原diffuse编码均值RGB约(.568,.529,.366)，独立sRGB转线性并乘当前色后均值约(.251,.231,.098)，确非灰色。抽样渲染patch显示HERO/Loggia亮度约.654… .697、平均通道差.065… .088；Living约.796、通道差.037。四patch全通道>.95的比例均为0，因此这里“发白”是低色差/高亮观感，不是证实硬剪白。PNG是AgX显示输出，不能与线性反照率相除反推照明。

## 单一最小候选提案

仅复制这一件terrain材质，在独立08场景中替换为实际查看过、许可和扫描尺度可追溯的阔叶枯叶/腐殖土扫描。先选一个素材，不并行堆多个tint/随机色/石叶方案。保留几何、物体总数、terrain topology、路径/核心/水、相机/曝光/灯光。宽度用素材实际声明范围；若未声明，只能记C作者尺度并清楚解释，不能把旧2m直接称为扫描真值。

保留三通道的正确色彩空间和明确微表面单位；不加灰色染色，不增加散叶总数、不增加地面sheet，不以降低分辨率或提高bump替代真实细节。原始扫描图与保存08图是不同证据，候选须由根同frame48、同960×540与三机位曝光渲染，保留旧图作对照；在看图前仍NOT_ACCEPTED。

根任务随后已授权并完成一个CC0新素材及上述独立材质候选，结果见`terrain-material08-handoff.md`。当前诊断本身没有更改生产、几何、缓存、旧贴图或源场景。
