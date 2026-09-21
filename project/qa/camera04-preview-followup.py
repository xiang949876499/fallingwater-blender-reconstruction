import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];folder=ROOT/'renders/previews/camera04-review'
notes={
'CAM_MAIN_B_BATH_A':('LIMITED_COMPOSITION','洁具已进入画面；马桶底部仍被裁切，洗手盆右侧裁切。照明比原图清楚，曝光待校准。'),
'CAM_MAIN_B_BATH_B':('READABLE_WITH_GEOMETRY_ISSUE','洗手盆、门口和地材可辨。实际图暴露门口两条黑色带状区域，已交主楼几何负责人；05已按其报告补共面地坪，仍需同机位复渲确认。'),
'CAM_MAIN_L1_SERVANT_A':('FRAMING_FAIL','相机位于沙发背面方向，宽背板占据中央，不能把家具射线命中当作有用正面构图。下一版限制到已知沙发局部坐标正面。'),
'CAM_MAIN_L1_STAIR_A':('READABLE_DIAGNOSTIC','连续真实踏步可辨，陡俯视适合梯面检查。不是最终美观或连续路径通过。'),
'CAM_MAIN_L1_STAIR_B':('LIMITED_COMPLEMENT','同样是陡俯视，和A方向接近。下一版寻找低处反看梯段的安全机位。'),
'CAM_GUEST_OVERVIEW':('LIMITED_COMPOSITION','巨型近树干问题已消除，整个客楼/连廊布局可辨；中部枝叶仍遮低翼和部分泳池，不能称无遮挡。'),
'CAM_GUEST_POOL':('READABLE_DIAGNOSTIC','泳池主体、池沿、临池翼与高围墙完整可辨，近树位于边缘，可保留该构图；05泳池阶与门口改变后需重看。')}
benchmark=json.loads((folder/'render-benchmark.json').read_text())
records=[]
for r in benchmark['runs']:
    name=r['camera'];status,note=notes[name];p=folder/(name+'.png')
    records.append({'camera':name,'image':str(p.resolve()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'actually_viewed_at_full_960x540':True,
                    'camera_settings':r['camera_settings'],'diagnostic_status':status,'notes':note,'final_visual_acceptance':'NOT_ACCEPTED'})
out={'scene_sha256':benchmark['scene_sha256'],'resolution':benchmark['resolution'],'samples':benchmark['max_samples'],
     'scope':'All seven actual unretouched preview images opened. These results supersede geometric framing guesses for the exact rendered candidates only.', 'images':records}
(ROOT/'qa/camera04-preview-followup.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'actual_images_reviewed':len(records)}))
