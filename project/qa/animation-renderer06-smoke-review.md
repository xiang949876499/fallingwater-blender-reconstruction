# 第六轮序列渲染流程验证

独立EEVEE预览源 SHA256 `e317241899808995f049e8d3343eac96c591cbecfddaa980949d6babb51ccce6`。源文件未修改。

实际渲染固定地下浴室B机位第1、2帧，384×216、8samples。两个Blender进程均退出码0；第一次生成两张PNG，第二次独立复开后核对源/工具/设置签名、分辨率、曝光与图片SHA，复用2帧，新增渲染0帧。进度见 `animation-renderer06-smoke/animation-progress.json`。

实际第2帧已打开。保存的FastGI=false、raytracing=true、单浴室灯丝排除设置均被序列工具保留，未被重新配置覆盖。物理Cycles切换恢复此排除的独立新进程检查见 `eevee-iteration06-reopen-check.json`。

这里只验证渲染、恢复设置和断点续渲链路。固定机位、两帧0.083秒、低分辨率不代表运动连续性、成片、最终水流或实时帧率。源预览总体视觉仍未通过。

首进程退出时出现 `Unable to delete file` 清理提示，退出码0且两PNG尺寸/SHA正确；日志原样保留，未把提示删除。后续独立复开与复用成功。
