# 07e 相机冻结交接

生产配置已更新为 [camera07e-settings-frozen.json](camera07e-settings-frozen.json)，与 `data/camera-settings-reviewed.json` 同字节，SHA256 `4def78dcbae91f3292562f41796adec71c4680b64e04301f051fdc1833ce8666`。完整120位在家具候选07e中重新复验，**120/120 GEOMETRY_ONLY_PASS**。Lounge A 座席侧实图为 **STAGED_COMPOSITION_ACCEPTED**；最终画质及完整第07轮仍未验收。

## 采用的构图与曝光

基于06完整冻结候选，仅替换 Lounge A 为已渲染的座席侧视点：眼点 `[8.85,37.45,10.0002]`，目标 `[4.9,38.15,10.0002]`，28mm，shift_y −0.08，EV3.6。它保持A11照片中的南侧窗/座席在左、书架在右、远处壁炉的空间关系；这是C级构图依据，不声称八点照片标定通过。

root 与相机代理均实际打开座席侧和入口前场两张 EV3.6 图。座席侧能看见壁炉开口与炉台、书架边缘、窗侧沙发、玻璃门和桌边；炉膛仍暗，桌子局部裁切，材质及照明还有待处理。入口前场图右侧书架明显挡住炉口，标为 **FRAMING_FAIL_NOT_ADOPTED**，原图保留。

| 参数 | 最终值 | 依据与边界 |
|---|---|---|
| Guest Lounge A | EV3.6 | 座席侧07e实图阶段构图接受；新07天空亮度下仍需曝光复查 |
| Guest Lounge B | EV3.0 | 保留06修正位置，作为已可读的互补房间视角；root要求的曝光保留值，非新07照明通过 |
| Main Living A | EV2.4 | root及相机代理已看天空强度0.36的独立照明候选EV2.4图，阶段曝光接受 |

其他镜头曝光不变。Main Living B EV2.4、Main B Bath A/B EV1.6及浴室A人工下移画幅都保留。保留 Main Loggia A、Main Plunge A 的真实上层干平台支撑修正；Plunge A是相邻平台下视检查，不能称为水池内部站位。独立展示相机不在这120位JSON内。

三张实际查看图的SHA256均记录在 [冻结清单](camera07e-final-manifest.json)。座席侧采用图为 `8d98dc75b04dffa5ae9015288f515a8dc63613c49be3af10b5132f310b687eac`，拒绝入口图为 `7275642b463d780208be1a651c85ed50da4a4f2e410166629aa3f7be41e6d809`，Main Living A EV2.4为 `563a8ba65cd78af57f8eaec49346b5e0aa5707b7ace943c48ec16c83b79d0195`。

## 全部120位复验

源 `scene/Fallingwater_furniture_candidate07e.blend`，SHA256 `d6084c1ebca7e1328f1a008b673d86e55c738da4b5ee8a52c5b7e5ce86b8eadd`。这是独立家具候选，不是完整整合07。Blender5.2.1 LTS、CPU4、`--python-exit-code 1`，实际退出码0；没有启动渲染或修改场景。

[复验报告](camera07e-final-verification.json) 与 [运行日志](camera07e-final-verification.log) 绑定源场景及冻结配置哈希。实际评估索引包含9,683对象、956,568顶点及1,024,245多边形；3,840射线检查脚下支撑、身体1.75m/轴向半径0.15m、四脚点及六方向眼点。120位全部几何通过，15个外侧检查点的polygon标识均与存储配置一致。

实际中心支持面名称与旧参数有两项差异，高度差均为0；未改它们的位置或抹去差异：

| 机位 | 存储支持面 | 07e实际支持面 | 高度 |
|---|---|---|---|
| Main Coat B | MAIN_floor_threshold_entry_coat_finish | MAIN_L1_COAT_finish | 0.1222m |
| Guest Boiler A | GUEST_L1_HALL_NORTH | GUEST_L1_CAR_COURT | 8.4002m |

检查索引不含植被；旧15条构图射线不应用shift，不可替代实际图像。全120几何通过不等于全120视觉、曝光、逐房覆盖或导航通过。

## 使用与保留

下一次完整第07轮构建应读取本冻结文件或同字节生产配置。已有场景必须显式应用JSON；本检查只核对给定参数在07e内安全，没有重写07e保存相机。新的完整07场景应重新做全部120位几何复验，并依实图检查曝光与构图，不能继承本候选的通过。

旧05-v2、06初验失败、06候选、柜后A/细部失败及未采用的入口候选均保留。相机索引和本交接已同步，未改root状态页、建筑、家具、天空或60边导航图。
