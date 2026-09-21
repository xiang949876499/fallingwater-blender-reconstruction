# 16株灌木生产入口与完整09复验

**局部形体已由整合者采用；整体地景仍FAIL。** 本代理实际打开候选三图及08基线三图，独立判断见`shrub09-integration-visual-review.md`。Loggia宽叶与侧枝改善明确，HERO改善有限，Living未见新遮挡；裸坡、均匀疏植和伞状冠层仍未解决。本次没有重新设计形体或渲染新图。

## 入口与接线

```python
import understory_detail
shrub_report = understory_detail.build(ctx, {'enabled': True})
```

入口：`scripts/understory_detail.py`，SHA256 `4c2e469ecac66f5b6b9f437d670e6957a49701d4550c7aa7af6b001764c95c28`。

调用顺序：site植被创建和最终terrain/root seating（包括bank08几何修复）完成之后，导航检查与最终保存之前。此入口不拟合新的地形、不重设根位，随后仍需对整合场景运行实际接触和当前路线回归。

默认`enabled=False`，返回`NOT_RUN_DISABLED`。只接受`enabled`，没有自动调树位或改材质选项。**对象修改白名单仅`object.data`，不更改任何标签。** 旧自定义`plant_asset`仍是源标签，实际几何以`object.data.name`为准；需要改标签时，另行扩展明确白名单，不在此次入口内默改。

每次启用先核对全场understory数量2400、批准32对象存在、原assigned data名称及签名、完整world matrix（最大容差1μm）、无意外modifier/shape key。所有对象先通过才生成资产并统一替换。任何原网格或根位不符即整批拒绝；部分上次应用也拒绝。全部已应用且签名相同则返回`SKIPPED_ALREADY_APPLIED`，不重复创建或再次移动。

生产运行不读取QA文件：批准名单、原/新网格签名与修剪集合已内嵌入口；可读副本是`qa/shrub09-integration-manifest.json`，由实际获采用的08候选文件提取。生成器`understory_detail08.py`完全未改，SHA256仍为`ecda4c99d9f36608241e78be34e1ba3e81208ea3bede5a6a0060a111bcf05bc2`，入口校验其SHA防止静默生成其他版本。

## 精确复用已采用资产

新网格的位置、边、面、smooth、材质索引、UV和材质名称签名与实际渲染的08候选相同。asset2保留236叶/3832三角，asset3为286叶/4632三角；修剪集合仍为asset2的154/160/170/182与asset3的100/103。没有新增变体、叶片、植物或地表材料。

精确16株原位、32对象、10个asset2实例与6个asset3实例不变。原先600用户的两类旧共享网格没有就地编辑，其余1184株普通灌木、1200株蕨类及全部成熟树保持当前09状态。

## 完整09独立验证

来源`scene/Fallingwater_iteration09.blend` SHA256 `489b05e403aa9d02c3568a8e3813a24235ee5b7e782df4d1f149b3ff6673e331`，使用匹配该SHA的`tour-path-route-iteration09-attempt01.json`冻结副本。没有读取其他代理正在改写的建筑或路线输入；排除数据hash也核对完整09内嵌输入记录。

独立产物`scene/Fallingwater_shrub_integration09.blend`，SHA256 `3de043c500dc6735bcdefe8f4a5362d2afa65387a38b9f24768a2862fff5fa80`。源保存帧73保留，物理与路线比较明确使用frame48。

| 检查 | 结果 |
|---|---|
| 已采用资产精确重建 | 两个新共享枝/叶网格的四个签名均相同 |
| 默认禁用、错误根位、错误data | 禁用无操作；错误输入整批拒绝，无新网格或部分替换 |
| 重复调用 | SKIPPED_ALREADY_APPLIED，无再次生成 |
| 完整09对象比对 | 23,385对象，仅批准32个对象的data与派生尺寸改变；matrix/根位/标签保持原值 |
| 其余数据 | 原共享网格、材质/图像、全部非目标几何、动画、相机、灯光、曝光和内嵌配置指纹不变 |
| 地面 | 仍是FW_Continuous_Forest_Floor，不采用失败落叶材质 |
| 16株实际地形接触 | 叶面最低离地18.095mm，叶/非基部枝与terrain三角相交0；根锚约−12mm保持 |
| 路径/相机 | 保守路径XY净空≥0.538m；相机XY净空≥2.929m；建筑、桥、核心、水及水边楼梯排除检查通过 |
| 当前09路线 | 11,554条相机/身体/头部射线，修改对象在基线与候选命中均0 |
| 核心/肩岩/旧水 | 63个frame48评估世界三角hash前后相等 |

新进程复开结果记录在`shrub09-integration-readback.json`；完整快照摘要、同一四个新资产签名、实际接触、63个冻结物理体和当前09路线均重新检查。路线回归不代表新的全楼房间连通性或GUI自由行走验收。

## 证据与限制

- `shrub09-integration-check.json/.log`：完整09应用、输入拒绝/重复调用、非目标比对与实际接触/路线结果。
- `shrub09-integration-fingerprint.json`：完整快照摘要及每对象摘要；无需再写两份100MB对象明细。
- `shrub09-integration-readback.json/.log`：独立CPU4新进程复开结果。
- `shrub09-integration-route.json`：本次精确对应完整09的路线冻结副本。
- `shrub09-integration-check-attempt01.json/.log`：首次负面测试使用matrix回写来恢复位置，引入浮点分解变化，指纹检测正确拒绝且没有保存场景。已改为恢复原始location值；入口与采用资产没有因此改变。

源码、QA和独立候选已就绪；`build_scene.py`、`config.json`、`site.py`、工作blend及其他代理文件均未改动，由整合者接线。新09候选没有渲染。当前采用的是16株局部形体，物种/品种与精确植株位置仍为U/C，不是环境最终验收。
