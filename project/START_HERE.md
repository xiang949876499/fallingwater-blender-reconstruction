# 打开与探索流水别墅

当前文件是制作中的检查点，完整影片、照片级效果和交互验收尚未完成。实际完成情况见 [STATUS.md](STATUS.md)。以下操作依据场景内实现与 Blender 手册整理，仍需在本机解锁后的 Blender 窗口逐项实测。

工作文件现为第10版，完整60项空间连接及7,584个影片帧的几何采样已在保存后复验，120个检查机位重新检查。仍没有完整影片或全部逐房照片；旧09版保留可回退。当前数据以模型内嵌记录和[第10版冻结记录](qa/integration10-freeze.json)为准。

## 打开场景

在 Blender 5.2.1 LTS 中选择 **File → Open**，打开 [Fallingwater_working.blend](scene/Fallingwater_working.blend)。先使用总览视角查看主屋、溪流和后方客房。

## 自由查看

- 按住鼠标中键拖动：环绕；滚轮：拉近或拉远；Shift＋中键：平移。
- 在三维窗口的 **View → Navigation → Fly Navigation** 中开始自由飞行。鼠标转向，W/A/S/D 改变移动方向，滚轮调节移动，左键结束，Esc 返回进入前的位置。
- **Walk Navigation** 适合从人眼高度穿过门口和走廊。自由检查模式没有完整的游戏碰撞，正常游览请沿实际门洞和楼梯移动。
- 从命名相机看景后，可按小键盘 0 返回自由视图继续探索；这样不会改变保存的对照机位。

## 一键切换房间

工程内附有可选的中文面板，只需在当前 Blender 会话运行一次：

1. 打开 **Text Editor**，从文本列表选择 `FW_NAVIGATION.py`。
2. 点击 **Run Script**，然后返回三维窗口。
3. 按 **N** 展开侧栏，选择 **Fallingwater**。
4. 从“视点”选择房间，点“前往视点”；下方有“返回入口”“主屋总览”“客房总览”。

这个面板只在当前 Blender 会话生效，不修改全局设置。所有空间都有 A/B 检查机位；空间清单还包括泳池、露台、楼梯和基础检查区。

## 显示质量与输出

面板提供“快速”“光照”和“Cycles”三档。需要快速改变位置时用“快速”；稳定观察光影时再切换高质量模式。各模式的本机实时帧率仍待实测。

- [逐房诊断图](renders/rooms/)：包括原机位与修正机位，尚未全部视觉验收。
- [联系表](renders/room-contact-sheets/)：一次查看多个房间。
- [材质试渲染](qa/floor-material-preview.png)：客厅不规则石板地面。
- [水流试验报告](qa/fluid-review.md)：独立短段模拟与当前限制。
- [保存后路线复验](qa/integration10-navigation-reopen.json)：第10版完整7,584帧几何检查，不能代替实际操作录像。

最终 12 张 4K 静帧、完整游览影片及可移植交付包尚未交付。短段模拟工程只允许播放报告注明的缓存帧范围，不能当作完整漫游影片。

操作参考：[Blender Fly/Walk Navigation](https://docs.blender.org/manual/en/4.3/editors/3dview/navigate/walk_fly.html)、[Text Editor](https://docs.blender.org/manual/en/4.4/editors/text_editor.html)。当前版本界面的最终确认以本机实操记录为准。
