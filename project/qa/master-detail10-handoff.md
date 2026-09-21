# 主卧源校正10：独立候选交接

**几何候选最终为10f；主卧布局局部改善已由root及本审查者实际看图确认，完整照片级仍不通过。** 本轮不再扩展模型。生产主屋、家具、浴室、路线、相机、灯光和原场景均未改；只新增独立helper、候选及本组QA。`neat-freak`收尾限于本组交接，中央STATUS与生产整合由root维护。

| 产物 | 冻结值 |
|---|---|
| [Fallingwater_master_detail_candidate10f.blend](D:/zx/test/project/scene/Fallingwater_master_detail_candidate10f.blend) | 44,371,522 B；SHA256 `f7ff5b0ab1317b0d375b884b651497bbc26e573cceebe5a9d15139a9c8e9ba5c` |
| [master_detail10.py](D:/zx/test/project/scripts/master_detail10.py) | SHA256 `751fa855c78add9e98b055a8a9bfd993640fc28c60cf8225fd351ffc7422572c`；未hook生产 |
| 基底 interface10c | SHA256 `f85d813129fab175257f00be12c8d1116505b62d2ca1f9f8a6ffae57926e4a2a`；已接受的Loggia实体/门阈闭缝保留 |

实际对象改动46、移除124、新增111；具体名单在[build-check](D:/zx/test/project/qa/master-detail10-build-check.json)。其余对象指纹、保存相机/灯光/设置均不变，保存后已重开核对。八项生产源码/数据hash不变。未运行渲染或保存checked路线。

## 源与实现

[HABS main05](https://www.loc.gov/pictures/item/pa1690.sheet.00005a/)原TIFF提供门、柜、炉膛和玻璃边界的身份；转换到项目1024参考坐标的边缘追踪仍为C约0.5–1px。[Columbia MCAH Master Bedroom全景](https://projects.mcah.columbia.edu/ha/panos/Fallingwater/Master-Bedroom/)提供家具朝向与可见形体B证据。该全景署名Maurice Luker，版权2001 Columbia University；源图及其衍生图保持`REFERENCE_ONLY_EXCLUDE_PUBLIC_PACKAGE`。

已实际打开[源布局叠图](D:/zx/test/project/qa/master-detail10-source-layout-annotation.png)、[炉边图纸网格](D:/zx/test/project/qa/master-detail10-hearth-plan-grid.png)、[2880炉面](D:/zx/test/project/qa/master-detail10-face3-2880.jpg)。未拟合精确摄影相机，GEO-07仍NOT_RUN。

| 部分 | 实施范围及证据边界 |
|---|---|
| 主卧北门 | 从旧x367..390改至图纸真口x352..366、y303；右侧铰接，门扇向主卧南侧打开。相邻墙、门框、门楣、原hall_master阈一起重建；完成面净宽0.7016m，9条竖向射线净高约1.958m。尺寸Z仍C。 |
| 北柜/旧柜 | 经root明确授权移除挡真门的`FW_FURN_MAIN_L2_CLOSET_M_coat_storage_00`整套。新北柜x367.5..415.5、y306..315.5，平门、大连续顶板，宽2.5152m、深0.50445m；尺度C。 |
| 床及床边 | 主卧床中心source(395.6,347.2)，转−90°使床头靠东；原1.55×2.02m床尺寸与已接受枕/床罩保留，低床头降低。该尺寸仍C，叠图不把床框当精确图纸匹配。南北开放架分别位于source y372.6/326.2；南架至约y380.7，给真浴室口y390.5..405留空间。旧通用抽屉柜/锥罩灯被替换。 |
| 木纹 | 只复制北柜专用`FW_MasterSource10_horizontal_veneer`。三PH通道共享同一米制柜根坐标、1/1.8比例、绕Y90°旋转，四门不会各自重置纹理。所有既有材质节点指纹不变。横纹方向是C艺术解释，非历史柜体扫描。 |
| 桌椅 | 主卧桌移到图纸/全景西南窗边，中心source(335,397)；椅位(341,383.3)。仅主卧专属资产移动。 |
| 地面 | Master与hall_master改石板材质，Closet原石材保留。物理地面依据墙/玻璃实际面扩展，与语义房间多边形分离；不改data房间记录。Master物理面积23.319630→25.702864m²；合并新浴室后应为25.828573m²。 |
| 西炉 | 炉口source x316..333、y333..349有真实东向凹腔、实心背/边/底/楣与错层悬挑。原东侧石饰移除重做，西侧石饰及楼梯侧北背衬保留。主石芯南端按图延至y384与现窗边相接。悬挑的XY源可辨、Z高度为C；非照片级碎石细部。 |
| 顶部 | 新西芯相接梁的source y354..359.6、Z4.79..5.005为有限C解释。梁身份可见但精确平面位置未测；必须保留该不确定度。 |
| 接口限制 | 未动`MAIN_L2_master_east_n/s`、`master_bath`阈或BATH_M物体。这些由root浴室helper负责。 |

## 几何复验及保留失败

所有结果均关联最终10f，不把未跑项目写成PASS。

- 151个目标网格为闭合双流形、正体积；保存前后所有非目标对象指纹相同。
- Master主地板8,717点、另3个改动完成面6,075点，共14,792点均只有一个完成面，无重复或缺失。[地板接缝复验](D:/zx/test/project/qa/master-detail10-floor-joins-check.json)
- 15个炉腔测试均穿过开放炉口命中后退背衬，未用黑平面遮住实心墙。
- 14项柜/灯柱/书本接触、6项实际落地检查通过；各独立家具资产之间三角交叉0。[接触复验](D:/zx/test/project/qa/master-detail10-contact-check.json)
- 家具与建筑仍有4项明确记录的交叉：同一连续柜顶板进入北墙、东段、门楣与框头约20.7mm，作为内嵌支撑接触C保留。不能将该项写成“全部几何零交叉”。
- 9条门高射线均约1.958m；全部原材质不变，专用材质三通道和共享坐标验证通过。[材质/门高/刷新](D:/zx/test/project/qa/master-detail10-material-door-check.json)
- 源入口沿床西侧至浴室前的修订旁路119点通过；终点仍在旧浴室墙西侧，尚未证明真正穿过浴室新门。
- **原MASTER动画路径29个目标近体碰撞保留FAIL。** 原保存`CAM_MAIN_L2_MASTER_A`身体落在现正确西南桌处；原B落进正确北柜，均保持原位且身体检查FAIL。
- 首个旁路177点中8FAIL保留：1点旧浴室东墙、6点南玻璃低槛、1点打开窗扇边。不把后续119点的局部PASS冒充这些原路线通过。
- 全120机位、60连接、7,584整数帧路线均未重验；完整导航仍NOT_RUN。

早期书本7.5mm悬浮、旧master_terrace阈y415..417共面，以及首次空材质槽读取错误均留在`first-*FAIL`/`attempt01-*`文件。最终阈为y410.52919..415：北接Master，南在实际TERRACE_S的y415边界结束，未改露台或玻璃。

## 实际图像审查

root使用本候选建议的两处正常室内位置，以24mm、EV0.9渲染了10e；本审查者已实际打开两图。它们虽然沿用了`CAM_MAIN_L2_MASTER_A/B`文件名，**其pose来自[master-detail10-root-cameras.json](D:/zx/test/project/qa/master-detail10-root-cameras.json)，并非保存场景的旧A/B**。

| 输出 | 实际观察 |
|---|---|
| [10e A](D:/zx/test/project/renders/previews/master-detail10e/CAM_MAIN_L2_MASTER_A.png) | 床头在东、门在北柜左侧、北柜横向连续木纹可辨，布局方向改善。整体明显偏暗，床罩颜色/纹样与源金黄织物不同；床侧过平整，柜上细条纹与源粗大木纹带仍有差距。C尺度与未知梁位置未获照片配准通过。 |
| [10e B](D:/zx/test/project/renders/previews/master-detail10e/CAM_MAIN_L2_MASTER_B.png) | 实际炉腔、水平悬挑与低阶均可辨，已具备原模型缺失的结构身份。但前面过于整齐，大石面和石缝节奏与源差异明显；暗部不足以观察整个炉内。地面虽改石材，色调/板形仍非源图精确匹配。 |

root接受**局部布局改善**；完整照片级仍FAIL。10f仅再收掉露台阈旧重复尾段，家具/炉/材料实现保持10e版本。10f尚未实际渲染，root将做曝光1.4/1.9/2.4分档。本轮不再为暗图扩大几何或陌生资产范围。

## 整合顺序与复渲位置

建议在已含interface10c修正的完整场景中顺序执行：

1. `master_detail10.apply(bath_source10=False)`。
2. root浴室helper调整真门/旧阈，并以此时Master地板最东实际X作为新阈起点。
3. `master_detail10.refresh_master_floor(bath_source10=True)`，只重建Master slab/finish，补回旧阈notch0.12570894m²。
4. 再做合并场景门口/地板/路线复验。新Master完成面东边实际X约4.735799789m，source x417.3778626；浴室阈与此边共享，不另叠一条面。

也可先`apply(True)`再运行浴室helper，使其读取最终东边；不应先让浴室阈取旧4.6112，再扩Master而忘记同步阈。

两建议位置均已检查0.18m身体净空，**只写JSON，没有在交付blend新建或移动相机**：

| 查看对象 | Eye world | Target world | 镜头 |
|---|---|---|---|
| 北柜/床 | (1.6768,8.4429,4.4668) | (3.4584,10.9917,3.8868) | 24mm，36mm sensor |
| 西壁炉 | (2.7772,8.2305,4.4668) | (-0.1048,10.4076,3.8868) | 24mm，36mm sensor |

局部相机与路径提案见contact-check JSON。照明、共性材质和生产路线整合由root继续；本文件不授予这些项目已经通过的状态。
