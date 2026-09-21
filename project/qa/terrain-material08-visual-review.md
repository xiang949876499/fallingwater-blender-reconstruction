# 材质候选08：三机位实际阅图

**VISUAL_FAIL / NOT_ADOPTED。** 根任务和本代理均已实际打开`renders/previews/terrain-material08`的HERO、Loggia B、Living A。素材类型比原草地合理，但本候选不足以通过环境外观验收，禁止仅因纹理许可/物理不变检查PASS就合入。

渲染来源`Fallingwater_terrain_material_candidate08.blend` SHA256 `7c4949d3d0a0dc4c9cfeb6c906b33842ef39fbe84bb5ce1030761a86ad1dbdae`；基准完整08为`c5cd501e…070d7`。根渲染frame48、960×540、32samples，曝光HERO/Loggia+.8EV、Living+2.4EV，与原08相同。benchmark的PASS仅指渲染完成。

| 图像 | 实际观察 | 判定 |
|---|---|---|
| CAM_HERO.png | 西坡由浅灰绿变为均匀密集的浅褐/白/橙颗粒，远看接近碎石贴面；实体仍是同一大块光滑坡，灌木仍细茎小锥。 | FAIL，表面资产类型改善未解决层次与轮廓。 |
| CAM_MAIN_L1_LOGGIA_B.png | 路缘结构保持正确，前坡表面像被连续颗粒贴纸覆盖；没有来源照片中的层状露岩和饱满宽叶灌丛遮挡。 | FAIL，未采用，不能靠再调灰色tint或强bump追赶。 |
| CAM_MAIN_L1_LIVING_A.png | 窗外60m以外地面仍几乎同样浅灰，换图没有实质改善远景林地分层。 | FAIL，近岸20株方案也不能宣称能修复该远景。 |

保留模型、三图、benchmark和全部负证据。CC0素材本身不判为错误；失败的是它在当前光照、尺度、地形与植被结构中的整场景用法。

下一步经根任务授权只做近岸普通灌木mesh2/3的只读量化与≤20株替换设计，不改生产、不渲染、不调整核心/水/建筑/相机。设计应优先改变真实分枝和末梢宽叶群的形态，不无依据增加全场灌木总量。
