"""Record actual contact-sheet inspection, separate from geometry or final acceptance."""
import json,hashlib,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
# Status: R readable diagnostic framing; L limited; F framing failure; D illumination failure.
pairs={
'MAIN_B_BATH':('F|门口及软木墙为主，洁具投影落在画面下方或侧外','F|空软木墙为主，马桶主体未入画'),
'MAIN_B_BOILER':('L|近墙和炉体各占一侧，设备明显裁切','R|锅炉、烟管、压力容器可辨；曝光偏亮待校准'),
'MAIN_B_FOUNDATION_1':('R|基础石墙和地面关系可辨，阴影较重','R|基础墙、顶板和溪流关系可辨'),
'MAIN_B_FOUNDATION_2':('R|基础墙及溪流界面可辨','F|主要对着近处土坡，未清楚展示该检查区的结构'),
'MAIN_B_FOUNDATION_3':('R|基础墙和邻接梯级可辨，阴影较重','F|近处土坡占据主要开口，结构信息不足'),
'MAIN_B_PLUNGE':('L|俯视池沿及局部水体，池整体仍有裁切','D|水面及池壁近黑，不能据此验收池内细节'),
'MAIN_B_STAIR':('L|梯级左侧与酒窖门口可辨，但飞行方向展示不完整','F|主要是地坪边、孔洞和近坡，梯段主体未入画'),
'MAIN_B_WINE':('R|酒架及邻接门口可辨，亮度偏高待校准','L|酒架端板遮住大块画面，架体仍可辨'),
'MAIN_L1_COAT':('L|只能看到关闭柜门局部，柜体上/下均裁切','F|镜头看向邻接楼梯，未展示衣帽储藏'),
'MAIN_L1_ENTRY':('R|入口转折、书架和起居空间联系可辨','L|入口邻接梯级可辨，近墙占比过大'),
'MAIN_L1_HATCH':('F|只见露台、树和架梁，水梯开口未入画','R|从真实梯级仰看阶梯、栏杆与玻璃开口，关系可辨'),
'MAIN_L1_KITCHEN':('R|AGA、南窗和工作区可辨；局部明暗待校准','R|橱柜、台面和餐桌可辨，局部阴影偏重'),
'MAIN_L1_LIVING':('R|天花灯框、窗、起居地面与水梯口关系可辨','R|壁炉、圆形水壶、座椅与窗可辨'),
'MAIN_L1_LOGGIA':('L|墙、顶板与局部通道可辨，观察范围局促','F|主要看土坡与溪流，柱廊本体未清楚展示'),
'MAIN_L1_SERVANT':('F|近土坡/背景占主要画面，沙发仅露边','F|近墙和土坡占主要画面，起居家具未清楚展示'),
'MAIN_L1_SERVICE_STAIR':('F|镜头看上方冰箱与天空，梯段未入画','F|主要看台面、地坪和近土坡，梯段未入画'),
'MAIN_L1_STAIR':('F|实际支撑是该层下方地形，画面为外弧梯底和土坡','R|真实主梯连续踏步可辨，俯视检查用途明确'),
'MAIN_L1_TERRACE_E':('R|露台与红色窗框关系可辨','R|露台地坪、矮墙和树林关系可辨'),
'MAIN_L1_TERRACE_W':('R|露台与主楼窗、石墙关系可辨','R|露台矮墙及溪流关系可辨'),
'MAIN_L2_BATH_G':('F|镜头主要看邻接空间，未展示浴室洁具','D|洁具可见极少，浴室主体近黑'),
'MAIN_L2_BATH_M':('F|主要看邻接卧室与门，浴室主体未入画','D|墙及马桶仅有轮廓，不能检查细部'),
'MAIN_L2_BATH_N':('F|主要看邻接更衣室，浴室主体未入画','D|盆、马桶、浴缸有轮廓，但光照不足'),
'MAIN_L2_CLOSET_G':('L|柜门与把手局部可见，不能检查完整储藏空间','F|主要看邻接卧室与外窗，柜内/柜体未展示'),
'MAIN_L2_CLOSET_M':('L|柜门局部与邻接灯具可辨，整体信息不足','F|近石墙为主，储藏空间未展示'),
'MAIN_L2_DRESSING':('R|柜体、窗和平台关系可辨，部分阴影偏重','R|书架、椅子、桌面可辨，近景略裁切'),
'MAIN_L2_GUEST':('R|床、柜与床头灯可辨；床尾有裁切','R|窗、桌与露台关系可辨'),
'MAIN_L2_HALL':('R|走廊、梯段与浴室门口关系可辨','R|走廊地面及外窗可辨'),
'MAIN_L2_MASTER':('R|床、床头柜与灯可辨','R|窗、桌及床沿可辨；近灯略裁切'),
'MAIN_L2_STAIR':('L|上层梯口/楼板洞口可辨，梯段未充分展示','F|只有画面左缘少量梯级，主要是近墙'),
'MAIN_L2_TERRACE_E':('R|露台内侧与室内家具关系可辨','R|矮墙、顶板及外部关系可辨'),
'MAIN_L2_TERRACE_N':('R|北露台、外窗及邻接梯段可辨','R|北露台与真实外弧梯关系可辨；土坡也如实入画'),
'MAIN_L2_TERRACE_S':('R|露台与南侧立面可辨','R|露台地坪和矮墙可辨'),
'MAIN_L2_TERRACE_W':('R|实际露台铺面与墙、门窗可辨','R|矮墙、铺面和树林可辨'),
'MAIN_L3_ALCOVE':('L|楼梯口、柜体和部分床可辨，卧榻主体展示不足','F|柜板占大半画面，卧榻主体未展示'),
'MAIN_L3_BATH':('D|镜子与窗有轮廓，洁具及墙细节过暗','D|近黑墙面及局部水箱，不能检查浴室'),
'MAIN_L3_GALLERY':('R|长窗、卧榻和狭长通道关系可辨','L|玻璃开口及柜边可辨，近景裁切较多'),
'MAIN_L3_LINK':('L|平台、屋顶与连接起点可辨，路线不完整','L|平台、梯口和远处客楼可辨，连廊连续性未完整展示'),
'MAIN_L3_STAIR':('F|主要是邻接卧榻和楼板洞口，梯段未展示','L|近处木踏步可辨，但整体飞行方向未充分展示'),
'MAIN_L3_STUDY':('L|沙发、书架与窗可辨，室内阴影很重','L|椅子、书架与桌可辨，室内阴影很重'),
'MAIN_L3_TERRACE':('R|主楼长窗与露台地坪可辨','R|露台矮墙、地坪和树林可辨'),
'GUEST_B1_BATH':('F|镜头看向洗衣桌与近软木板，浴室洁具未展示','F|几乎全是软木墙，浴室洁具未入画'),
'GUEST_B1_LAUNDRY':('R|工作台、叠巾、洗手盆及洗衣机可辨，曝光偏亮待校准','R|洗衣机及出入口可辨，门板占较大前景'),
'GUEST_B1_STAIR':('F|离踏步太近，局部几级横板占满画面','F|主要是梯底/近踏步，无法检查完整梯段'),
'GUEST_L1_BATH':('D|近黑，无法检查浴室','D|近黑，无法检查浴室'),
'GUEST_L1_BOILER':('D|仅门口侧光可见，设备主体近黑','D|设备及墙面近黑'),
'GUEST_L1_CAR_COURT':('L|阴影内立面与窗可辨，但车庭地面和范围不足','R|车庭地坪、侧立面与树林边界可辨'),
'GUEST_L1_CHAUFFEUR_LOUNGE':('D|近墙与座椅轮廓很暗，空间不可读','L|窗、柜与椅子局部可辨，室内仍暗'),
'GUEST_L1_GALLERY':('R|走廊、门口和起居室联系可辨','F|石墙占据大半画面，通道检查信息不足'),
'GUEST_L1_GUEST_ROOM':('R|床、窗、椅子和矮柜可辨，床尾裁切','R|床、床头墙与柜可辨，床尾裁切'),
'GUEST_L1_LOUNGE':('R|书架、茶几、长椅与窗关系可辨','L|近隔栅遮住大半前景，沙发和窗仍可辨'),
'GUEST_L1_POOL':('R|池沿、水面及入水小阶可辨；材料真实性未验收','R|水面与反向池沿可辨；材料真实性未验收'),
'GUEST_L1_STAIR_HALL':('F|主要是外部弧形连廊，标称楼梯厅未充分展示','R|楼梯口与真实梯段可辨'),
'GUEST_L1_TERRACE':('R|露台与弧形连廊关系可辨','R|沿客楼立面、泳池及廊架的露台方向可辨'),
'GUEST_L1_THEATER':('D|桌椅、窗仅有暗部轮廓，检查照明不足','D|座椅与墙面明显过暗，细节不可读'),
'GUEST_L2_BATH':('L|洗手盆/镜子和门可辨，下缘裁切','F|只拍到水箱顶，马桶主体在画面下方'),
'GUEST_L2_BEDROOM_MIDDLE':('R|床、柜、桌椅和门关系可辨','R|床与外窗关系可辨，床沿裁切'),
'GUEST_L2_BEDROOM_NORTH':('R|床、柜和桌椅可辨','R|床与外窗关系可辨，床沿裁切'),
'GUEST_L2_BEDROOM_SOUTH':('R|柜、桌椅、床与窗关系可辨','R|床及两面窗可辨'),
'GUEST_L2_HALL':('L|两侧门口与走廊墙可辨，空墙占比偏大','R|窄廊、墙材及门口关系可辨'),
'GUEST_L2_TERRACE':('R|真实高围墙及门口可辨；不为取景降低已校准墙高','R|真实高石围墙、铺面及阴影可辨；不等于开阔观景露台')
}
index=json.loads((ROOT/'qa/camera04-contact-sheets/index.json').read_text())
source={Path(im['image']).stem:dict(im,contact_sheet=p['sheet']) for p in index for im in p['images']}
frozen=json.loads((ROOT/'qa/camera04-settings-frozen.json').read_text())
rows=[]
labels={'R':'READABLE_DIAGNOSTIC','L':'LIMITED_COMPOSITION','F':'FRAMING_FAIL','D':'ILLUMINATION_FAIL'}
for name in frozen:
    rid=frozen[name]['room_id'];suffix=name[-1]
    code,note=pairs[rid][0 if suffix=='A' else 1].split('|',1)
    rows.append({'camera':name,'room_id':rid,'actually_viewed':True,'review_method':'Actual contact sheet opened; unretouched 426x240 thumbnails from 640x360 rendered PNGs.',
                 'diagnostic_status':labels[code],'notes':note,'final_visual_acceptance':'NOT_ACCEPTED',**source[name]})
counts=dict(collections.Counter(r['diagnostic_status'] for r in rows))
out={'scene':'scene/Fallingwater_iteration04.blend','scene_sha256':'247d20f7863e4f7e9c18587d4c032bd663857a420bcfb828d271195665841ac2',
     'settings_sha256':hashlib.sha256((ROOT/'qa/camera04-settings-frozen.json').read_bytes()).hexdigest(),'actual_images_reviewed':len(rows),
     'scope':'All 120 source renders inspected through ten stable contact sheets. R means the named inspection space is readable in this diagnostic image only; it is not photoreal, exposure, 4K, material, route, or final acceptance. Geometry PASS is separate.',
     'counts':counts,'cameras':rows}
(ROOT/'qa/camera04-visual-ledger.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# Iteration04 逐张视觉检查','',f'已实际打开 10 张固定联系表，查看全部 {len(rows)} 张 640×360 原机位图的未修饰缩略图。计数：'+', '.join(f'{k}={v}' for k,v in counts.items())+'。',
'','可读仅指本张诊断图能辨认标称检查空间；**所有图的最终视觉验收均未通过**。没有用“无黑图”或几何 PASS 代替视觉检查。PNG 哈希、尺寸、联系表路径及逐张结论见同名 JSON。','',
'| 机位 | 诊断结论 | 实际看到的内容/问题 |','|---|---|---|']
for r in sorted(rows,key=lambda r:(r['camera'].startswith('CAM_GUEST'),r['camera'])):lines.append(f"| {r['camera']} | {r['diagnostic_status']} | {r['notes']} |")
(ROOT/'qa/camera04-visual-ledger.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps(counts))
