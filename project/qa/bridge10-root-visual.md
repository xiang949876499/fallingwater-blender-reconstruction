# Bridge10：整合者实际图像复核

状态：**ACCEPT_LOCAL_FORM_AND_ENDFACE_FIX；整体环境与照片级未通过。**

实际打开初版meshclean与endfix的南入口/住宅侧两机位，共4张960×540、Cycles48sample、CPU8、frame48图。两次使用同一个 `bridge10-render-cameras.json`，并对照此前实际打开的Columbia两张原面与Hyde桥梁照片。

初版 `renders/previews/bridge10/` 的四石墙端出现明显黑条；exact_end零凸出贴面与完整core端面共面，几何闭合检查没有捕获此可见问题，状态VISUAL_FAIL并保留。新 `renders/previews/bridge10-endfix/` 两图黑条消失，保留完整石材端面和13ft3in实面间距，主栏墙连续且有照片支持的浅赭混凝土身份。没有改机位、升曝光或隐藏实体来掩盖黑条。

接受的独立候选为 `scene/Fallingwater_bridge10_endfix.blend`，SHA256 `2a7630b8024c37bd768e563236807f8049469172c7e44b03379a450f91637063`。此接受只针对连续栏墙、实体石桥头及端面黑条修正；路面仍显过于规整，森林稀疏、岸坡单调与程序河水问题清楚可见，不能给整体写实质量PASS。

两个南桥头内残存旧连续水面仍需真实裁切；正常水岸接触与穿入固体内的水已分开测量。后续裁水候选应以这份端面修正版为基底；未完成裁水与新场景复验前，不把此文当完整水体验收。
