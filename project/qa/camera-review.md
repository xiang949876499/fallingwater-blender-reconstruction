# 逐空间相机检查

生产 `data/camera-settings-reviewed.json` 已采用 [07e 冻结配置](camera07e-settings-frozen.json)，SHA256 `4def78dcbae91f3292562f41796adec71c4680b64e04301f051fdc1833ce8666`。**完整第07轮现已独立完成120/120实际支撑与净空复验、120/120保存参数匹配**，见 [完整07检查](camera07-review.md)。六张重点新图及选定曝光梯度已实际查看：Lounge A/B构图可读，Study桌下亮条消失，Bath仍是裁切有限视图，HERO水体失败；建议保持现有曝光。只有5个房间镜头属于120位集，不能称完整新视觉验收。历史来源见 [07e交接](camera07e-final-review.md)。

**新的完整视觉验收尚未进行。** 15 个门外、相邻平台及池边等外侧检查点在07e复算后标识一致，不能自动解释为房间内部浏览通过。Lounge A 的新图证明空间关系可读，仍有暗炉膛、局部裁切及材质照明质量待处理。几何安全、阶段构图接受与最终质量是不同状态。

下一次构建使用与07e冻结副本同字节的生产 JSON。原05-v2浴室人工下移画幅、已选曝光及06非平地修正均保留。场景新增或修改几何后必须重新复验；已有场景需要显式载入 JSON 才会应用新机位、镜头位移和曝光。原 [05 配置](camera05-settings-frozen-v2.json)、[05 说明](camera05-review.md) 与 [06 候选及失败证据](camera06-review.md) 保持可追溯。

`scripts/camera_review.py --scene <新场景> --verify-settings <配置> --report <独立报告>` 只复查点位，不改模型。`--rooms` 支持局部重新搜索；泳池、楼梯等已经人工调整的特殊点不得无依据批量重置。构建接入函数为 `camera_review.integrate(scene, rooms)`，支持 JSON `shift_x/shift_y`。几何报告的旧 15 条构图射线不含镜头位移，不能替代实际图像。

04 的 120 张已全部实际查看，结果为 57 张诊断构图可读、22 张有限可读、28 张构图失败、13 张照明失败，见 [逐图台账](camera04-visual-ledger.md) 与 [04 复验说明](camera04-review.md)。03 记录保留在 [camera-review-iteration03.md](camera-review-iteration03.md)。旧图及几何通过都不能计为新版视觉通过。
