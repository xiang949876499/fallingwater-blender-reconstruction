# 第八轮尺寸来源核读

这是来源核读报告，未改变模型、中央尺寸审计或 dimensions.csv。三个开口/场地原 TIFF 候选已核读，另完成一个主05露台投影候选的高分核读；全部网格实值均为 NOT_RUN。数值来自明确印刷字值；附图坐标仅用于定位，不能用像素换算赋予这些名义目标以测绘精度。

| 候选 | 清楚转录 | 名义米值 | 端点语义与待验对象 |
|---|---:|---:|---|
| 客房西北整樘门窗开口 | 8′1⅞″ | 2.486025 | 北斜石墙与相邻北石墩的相向 reveal，包含整樘窗门框；不是单门扇净通行宽。|
| 客房西侧中整樘窗开口 | 7′1⅛″ | 2.162175 | 中间两石墩相向 reveal，沿本樘斜线量取。原生字形确认分子为1，不是7。|
| 主屋桥南端石墙口 | 13′3″ | 4.038600 | 底部尺寸链两条延长线对应桥南岸两侧石墙的相向端面。不是桥板外包宽、细边栏净距，也不是没有箭头的 BRIDGE 14′3″房间式标签。|

开口来源：[HABS PA-5346-A sheet 1](https://www.loc.gov/pictures/item/pa2187.sheet.00001a/)。桥端来源：[HABS PA-5346 sheet 4](https://www.loc.gov/pictures/item/pa1690.sheet.00004a/)。实际使用的是已保存并重新计算 SHA256 的官方原始 TIFF；网页本轮未重新取得，不能称网页访问核验通过。

## 实际已看证据

- dimension-sources08-guest01bays.png：两樘原始线条、尺寸线、框与门扇关系。
- dimension-sources08-g01_north_glyph.png、dimension-sources08-g01_middle_glyph.png：原生分数字形。
- dimension-sources08-main04bridge.png：桥与南岸端面、完整底部尺寸链。
- dimension-sources08-main04top.png、dimension-sources08-guest02roof.png：用于排除把总体链跨度误称悬挑。
- dimension-sources08-main05west.png：现有低分 JPEG 西露台候选定位；不能从该放大图可靠抄读分数。

原始 TIFF 的 hash、未旋转原像素裁切框、旋转、展示裁切与输出路径记录在 dimension-sources08-crops.json。各候选对象选择建议与限制在 dimension-sources08-review.json。

## 现模型对应的限制

客房源码把三段门窗开口放在一条直的 THEATER_WEST 墙上，图纸是逐石墩错位的斜向 bay。不能将 opening.span 的百分比或一个门扇宽当作这两个有标注的整樘开口。应先识别实际相向石墩 reveal，沿该樘斜向轴射线，记录 evaluated mesh 面及世界交点，然后计算两点的平面距离。

桥的当前构建为矩形桥板、连续石边栏和四个矩形桥台，尚未证明有图纸南岸石墙相向端面的同一几何。候选对象名仅帮助定位，不能据名称赋予端点一致性；如果对应构件不存在，则保留 NOT_RUN。桥板配置 bbox 的宽度不是真实网格测量。

这三项有明确名义字值与图上端点，可供下一次实际测量；本报告不给 GEO-02 PASS，也不调整 max(20mm,0.5%L) 门槛。未量化的抄读误差和绝对测绘精度仍为 null / UNKNOWN，不填0。

## 西露台高分复核结论

2026-09-21 完成定点原 TIFF 下载与文件格式核验：[LOC 官方 00005a.tif](https://tile.loc.gov/storage-services/master/pnp/habshaer/pa/pa1600/pa1690/sheet/00005a.tif)，30,143,777 字节，SHA256 `b8ecfc0128d9f5452e768032afd766976eb1e1b39cf85924a256e45baf50c891`。原图、完整局部、见证线和原生字形均已保存并实际打开。既有 floor08 裁切代码输入为1024px JPEG，此次没有把先前模糊放大图当作字值证据。

原生字形明确为 **28′11¼″ = 8.82015m**。双端见证线对应西露台自由板/栏板外侧边与更衣室西侧石墙外面。图内另写 TERRACE **28′3″×16′2″**，那是没有箭头的房间式标签，不能用来替换该尺寸链。这是明确的平面投影候选；实际应量被见证的外侧边，不以可能内缩的完成面边界代替。

**仍不能把此值当作已核验的悬挑长度。** 主04同区域在更衣室西侧更远处还存在 Servants’ Sitting Room 石墩/墙体，处于二层露台投影范围内。上层更衣室外墙不能自动当作下层整块露台最近支承面。也不能简单减去主04邻近10′11″尺寸来拼出精确悬挑，因跨层共同端面和受力支承身份尚未验证。

主04顶链11′8″、客房02屋面顶链38′7¼″也都没有建立“真实支承面—自由板边”关系，因此悬挑类别保持缺项。此次有界研究在三个明确开口/场地候选与这一额外平面投影的核读后结束，没有启动其他下载或扩大搜索。

主05证据：dimension-sources08-main05-west-native.png、dimension-sources08-main05-west-dimension.png、dimension-sources08-main05-west-glyph.png、dimension-sources08-main05-west-wall.png；下层支承语义对照：dimension-sources08-main04-support-context.png、dimension-sources08-main04-kitchen-bearing.png。完整元数据仍在相邻JSON。

按 neat-freak 技能对所属报告与裁切清单作了收束：下载等待状态已替换为已完成核读，实际看图标记与文件一致；没有修改共享 STATUS、AGENTS、生产模块、中央审计或全局设置。图库索引中未实际打开的最后一张 guest04 独立页不作为本次查验依据。
