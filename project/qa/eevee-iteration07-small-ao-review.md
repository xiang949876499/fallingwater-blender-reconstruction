# 零VOLUME、小半径AO预览试验

**FAIL / NOT_ADOPTED。** 从已冻结零VOLUME候选 `a38639236bae8a08061bfc6f38218d24fe346ad476cdebdded1065f74266e3f3` 派生，保留全部原灯、阴影和薄玻璃，只在候选启用0.6m范围的AMBIENT_OCCLUSION_ONLY；无新GI烘焙、无补光、未改生产helper。

本机RNA实际确认相关枚举及参数。该试验是一个预览配置组合：quality0.5、16步、4射线、thickness0.08m，曝光另导出0/0.8/1.6/2.4；不是单变量因果检查。Study B，frame48，960×540，32samples，43.774秒，退出码0。退出时日志另有“Unable to delete file”，输出图、报告和独立候选存在；保留原日志，不将该行抹去。

整合者实际打开EV0.8与EV2.4图。没有旧缓存的大块黑lobes，但书架内、桌下、墙顶转角仍缺乏可信遮蔽，木材与室内整体平白。降曝光改善亮度，不能恢复缺失的空间光照关系，故不采用。体积强度0、真正无体积与局部AO是三个不同试验，不能混写结果。

图像、候选及完整参数见 `qa/eevee-iteration07-small-ao/`。Cycles物理源保持不变。
