# 第四轮静态场景迁移检查

2026-09-20。**静态场景的12张贴图已打包，迁移后独立复开与重渲通过。** 此结果不包含尚未整合的流水缓存、最终影片或从脚本重建整个项目。

源文件为 `scene/Fallingwater_iteration04.blend`，SHA-256 `247d20f7863e4f7e9c18587d4c032bd663857a420bcfb828d271195665841ac2`。打包检查点在 `delivery/iteration04-checkpoint/Fallingwater.blend`，可编辑且保留原始材质。

检查副本移至 `qa/portability/iteration04-relocated-v2/Fallingwater.blend`。逐张读取 packed bytes，与原纹理 SHA-256 比较，12/12一致；随后仅在检查副本中将全部外部图像路径改到不存在的目录，保存退出。新的 Blender 进程仍能打开并用嵌入贴图渲染，原项目与源纹理没有改名或删除。

HERO采用原机位、同帧1、AgX、EV+0.8、Cycles24上限、960×540、同种子42。原图8线程，迁移重渲4线程，图像不要求逐字节相同。实际通道平均差0.00831/255，P95为0，最大10/255；2.24%的像素至少一通道有变化。两张图均实际打开查看，建筑、森林、石材和水面外观一致，没有粉色缺图或材质丢失。

首次检查脚本试图在迁移目录解析旧相对纹理路径以比较源文件，因该路径已失效而失败；日志 `portability-iteration04-preparation.log` 和首次副本保留。第二次明确从原资产目录核对嵌入字节，再执行不存在路径测试；不是修改失败证据冒充成功。

机器证据：`package-iteration04.json`、`portability-iteration04-preparation.json`、`portability-iteration04-image-comparison.json`、`portability-iteration04-render.log`。流水真实缓存、近树库等脚本重建依赖和最终交付包仍需单独整理与迁移验证。
