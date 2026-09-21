# 逐空间相机检查 — 2026-09-20

状态：**120 个相机位置通过几何复查；整体视觉仍未验收。** 本项没有修改墙、家具、灯光或 working.blend。

已实际查看 iteration03 的 10 张联系表、共 120 张原机位图，以及 camera-correction01 的 10 张修正图。联系表包括基础、楼梯、露台和泳池等检查空间，不能称为 60 个居住房间。

## 实际看到的问题

| 对象 | 图像与实际网格证据 | 处理 |
|---|---|---|
| MAIN_L1_KITCHEN A | 黑图；眼点穿吊柜底座，前向物体仅 0.214m | 换到真实厨房地坪，两个修正图已看到灶具、工作台、橱柜和窗；仍不是最终材质验收 |
| MAIN_L1_COAT A/B | A 穿衣柜搁板；B 离墙 0.071m。首轮安全机位仍明显俯斜 | 冻结版 A 从门口水平看入，B 从内侧水平反看入口；第二次图待检查 |
| MAIN_B_BOILER A | 身体穿压力罐；B 无身体碰撞但图像仍黑 | 换安全机位；首轮修正两图仍黑，已通知灯具制作方 |
| MAIN_B_BATH | 原 A/B 无身体或眼点碰撞；安全机位重渲仍近黑 | 需要可见实用灯具；不能靠换机位宣称解决 |
| MAIN_B_PLUNGE | 原 A 撞台阶，B 在水体内 | A 保留桥上总览；冻结版 B 站南侧实际池边地坪 z=-2.4998m，眼点 z=-0.8998m，待重渲 |
| GUEST_L1_THEATER A | 眼点在幕布后，幕布仅距 0.0527m | 重新选实际地坪机位，待图像检查 |
| GUEST_L1_BOILER B | 眼点落入石材墙面，最近表面距 0.00158m | 重新选安全机位，需重新看照明 |
| 楼梯、衣帽柜、浴室 | 多个原机位在台阶、床/柜/浴缸/洗手台内，或只看到近处门板、墙面 | 实际梯级取高程；柜体门口加反向；室内镜头俯仰限制在 6° 内，衣柜保持水平 |

原位置诊断有 53 个身体/脚下检查问题、13 个眼点附近表面问题，二者有重叠。它们是相机布点缺陷，不等于相同数量的建筑模型缺陷。

## 灯具复核清单

优先补足可见灯具或复核已建灯具发光：MAIN_B_BATH、MAIN_B_BOILER、GUEST_B1_BATH、GUEST_L2_BATH、GUEST_L2_HALL、GUEST_B1_LAUNDRY。其中主楼地下浴室和锅炉间已在安全新机位重渲确认仍黑；后三组原双机位几何安全但近黑，洗衣房 B 安全而很暗。

下一批待新机位确认：GUEST_L1_BATH、GUEST_L1_BOILER、MAIN_L2_BATH_G、MAIN_L2_BATH_M、MAIN_L2_BATH_N、MAIN_L3_BATH。不能把原机位穿家具造成的黑图全部归因于缺灯。灯具位置、造型和功率若无可核实资料，应记录为 C；不采用隐形补光。

## 几何检查边界

- 对 iteration03 实际求值后的 9,231 个物体、646,357 顶点、646,414 多边形建索引；包含墙、玻璃、家具、地形和水体，**排除植被**。场景改变后需重新检查。
- 选择阶段实际发出 1,811,305 条射线。60 个空间均取得两个相隔至少 0.45m 的位置；11 个机位在本空间多边形外，从邻接门口或池边观察，配置逐项标记。
- 每个位置核实真实支撑面、中心及四周 13cm 脚下支撑、1.75m 身体高度/15cm 半径的轴向检测柱、眼点六方向 16cm 清空。楼梯允许真实相邻级差；不会要求整个楼梯空间是平地。
- 不能站在水体、家具、屋顶、廊架或栏杆上。MAIN_water_stair 名称里的 water 不等于液体；真实台阶可作支撑。
- 构图使用 15 条视域射线辅助，正常镜头 28–32mm。普通室内俯仰不超过 6°；衣柜水平；泳池与楼梯保留俯视检查需要。
- 冻结 JSON 另经 3,840 次射线独立复查：120/120 **GEOMETRY_ONLY_PASS**，0 个位置失败。这不代表全身连续路径、GUI 导航、植被碰撞、亮度、光照真实性或视觉验收通过。
- 所有曝光仍是诊断建议，所有配置的 `render_reviewed` 保持 false。新图需要实际打开检查。

## 接入与重验

权威配置：[camera-settings-reviewed.json](../data/camera-settings-reviewed.json)。构建完所有几何及 120 个相机之后调用 `camera_review.integrate(scene, rooms)`，只设置相机位置、朝向、镜头与曝光；不会移动几何或保存场景。

渲染器可直接传 `--camera-settings project/data/camera-settings-reviewed.json`。新增或改动墙体、家具、池边和楼梯后，使用 `camera_review.py --scene <新场景> --verify-settings project/data/camera-settings-reviewed.json` 复查；不能沿用 iteration03 的 PASS。相机重新搜索使用同一脚本，不传 `--verify-settings`；`--rooms` 支持逗号分隔局部重算，保留其余配置。

证据：[位置选择明细](camera-review-geometry.json)、[冻结配置复查](camera-review-verification.json)、[完整运行日志](camera-review-final-run.log)、[复查运行日志](camera-review-verification-run.log)。早期 run/nonflat/stairs/framing 日志保留失败过程，仅 `final` 与 `verification` 对应冻结版。

等待下一轮实际查看：CAM_MAIN_L1_COAT_A/B、CAM_MAIN_B_PLUNGE_B、CAM_MAIN_L1_HATCH_A/B；之后需要完整 120 张新机位图和实际灯具的照明复核。
