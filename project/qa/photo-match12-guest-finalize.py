"""Reconcile bounded12 photo QA and handoff; no optimization or shared-doc edits."""
import json,hashlib,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
fit=json.loads((ROOT/'qa/photo-match12-guest-fit.json').read_text(encoding='utf-8'))
ray=json.loads((ROOT/'qa/photo-match12-guest-rays.json').read_text(encoding='utf-8'))
lock=json.loads((ROOT/'qa/photo-match12-guest-observation-lock.json').read_text(encoding='utf-8'))
data=json.loads(Path(lock['file']).read_text(encoding='utf-8'))
assert hashlib.sha256(Path(lock['file']).read_bytes()).hexdigest()==lock['sha256']
assert hashlib.sha256(Path(fit['scene']).read_bytes()).hexdigest()==fit['scene_sha256']
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
# The window markers are the frozen modeled coordinates, explicitly not a claim
# that the red circles are the drawing's real frame marks.
for name,title in [
 ('source-plan-roof','QA |2010 guest02 native crop | red = actual12a underside vertices R01/R02/R03/O0N/O0S'),
 ('source-plan-window-stairs','QA |2010 guest01 native crop | red =12a modeled locations, NOT verified drawing window-post marks')]:
    path=ROOT/('qa/photo-match12-guest-'+name+'.png');im=Image.open(path).convert('RGB')
    # Idempotent finalizer: retain crop file rather than stack repeated headers.
    if im.height not in (438,636):continue
    canvas=Image.new('RGB',(im.width,im.height+34),'white');canvas.paste(im,(0,34));d=ImageDraw.Draw(canvas);d.text((8,6),title,font=font,fill='black');canvas.save(path)
rows=[]
for p,r in zip(fit['points'],ray['rows']):
    ob=r['blocking_before_target_25mm']
    if ob.get('object')=='GUEST_LAYERED_SANDSTONE_COURSES':verdict='REJECT_AS_VISIBLE_EXACT_LANDMARK: foreground stone obscures target'
    elif ob.get('object','').endswith('_head'):verdict='UNVERIFIED: head overlaps nominal post endpoint; actual visible contour must be identified'
    else:verdict='UNVERIFIED: source topology supports identity; actual base/evaluated vertex visible, independent review pending'
    rows.append({'id':p['id'],'role':p['role'],'pixel':p['pixel'],'world_m':p['world_m'],'object':p['object'],
       'locator':{'vertex_index':p.get('vertex_index'),'edge_vertices':p.get('actual_edge_vertices'),'adjacent_base_faces':p['adjacent_base_faces']},
       'residual_px':p['residual_px'],'residual_pct_diagonal':p['residual_pct_diagonal'],
       'blocking_object':ob.get('object'),'target_to_first_hit_m':r['model_projection_first_hit'].get('distance_to_landmark_m'),
       'review_status':verdict,'source_confidence':p['confidence']})
cam=fit['camera'];pitch=math.degrees(math.asin(cam['forward_world'][2]));foot=ray['support_probes'][0]
review={'schema':'fallingwater.photo_match12.guest_review.v1','test':'GEO-07','result':'NOT_RUN_ACCEPTANCE / DIAGNOSTIC_INTERPRETATION_FAIL',
 'why':'Only one fixed15point candidate fit. At least8 independently reliable visible structural landmarks were NOT achieved: exact windowbase endpoints are obscured or composite joints, and the roof identities await independent review. Good median does not override these failures.',
 'scene_sha256':fit['scene_sha256'],'points_sha256':lock['sha256'],'fitted_camera_immutable_file':'photo-match12-guest-fit.json',
 'geometry_changed':False,'production_camera_created':False,'renders_run':0,
 'photo_date':'Jack E. Boucher, February and March1985, caption page1; individualA10day not specified',
 'plan_date':'2010 HABS measured drawing set. No proof of intervening changes supplied; date gap is uncertainty, not an excuse for mismatch.',
 'point_reviews':rows,'statistics':fit['statistics'],'fit_rank':3,
 'camera_support':{'support_object':foot['object'],'support_z':foot['position_m'][2],'eye_z':cam['eye_m'][2],
    'eye_above_support_m':foot['eye_height_above_first_support_m'],'normal_standing_pose':'FAIL',
    'historical_low_camera_pose':'UNKNOWN;0.46m low tripod/crouching is possible but not supported by caption',
    'upward_pitch_degrees':pitch,'fixed_principal_point_assumption':'UNVERIFIED. Near-vertical source frame posts disagree with fitted near-post26.44px upper/lower lateral difference. Architectural camera shift/crop origin might matter but not fitted this round.'},
 'continuous_edge_review':[
   'Roof first elbow and first aperture topology corresponds to sourceguest02; fitting R01/R02 cannot independently validate them.',
   'R02-R03 south beam is noticeably too slanted/right in projection: near modeled(599.115,458.796),far(627.438,559.933); source endpoints(601,469),(596,540). Farholdout37.225px. This tests one camera/identity/model combination, not a direct correction vector for architecture.',
   'All10aperture lower boundary loops show a coherent projected drift; sky openings were not replaced by straightglass planes. Exact far hole corner identities not silently reassigned.',
   'Nearwindow projected endpoints separate horizontally26.44px whereas locked source endpoints nearly align vertically. Modelposts/scan principalpoint/inferredcamera remain a coupled unresolved issue.',
   'Orange W1/W2 actual tread edges do not follow the photographed side-wall/nosing profile. W2 photographed far stair group has several rough bands; current4risers and heights remainC. No individualroughline was invented as a precise point.',
   'Nativeguest01 overlay shows current equal7bay modeled locators do not land on the drawing window-post symbols. Association of photographed closest post to the plan return/firstpost must be reviewed before a new point set.'
 ],
 'next_bounded_review':'Independent reviewer should check observed image + native roof/window crop + exact15locators, focusing on R03east termination, W0near corner identity and composite sill/head contours. Do not change points because of residual. New camera optics protocol or source-constrained facade correction requires a separately frozen round.',
 'negative_evidence_retained':['data/photo-match-points-iteration05.json','qa/photo-match-iteration05-review.md','qa/photo-match-results-iteration05-guest10-diagnostic.json'],
 'qa_cleanup':'neat-freak applied within assignedphoto-match12-guest docs only; no rootSTATUS/AGENTS or shared acceptance ledgers modified.'}
(ROOT/'qa/photo-match12-guest-review.json').write_text(json.dumps(review,indent=2),encoding='utf-8')
table=['|点|用途|照片像素|实际对象/定位|误差px|实体可见性复核|','|---|---|---|---|---:|---|']
for p in rows:
    loc=p['locator'];where='v'+str(loc['vertex_index']) if loc['vertex_index'] is not None else 'edge'+str(loc['edge_vertices'])+'中点'
    name=p['object'].replace('GUEST_L1_LOUNGE_FRONT_steel_window_0_','…window_0_')
    vis='前侧石皮遮挡' if p['blocking_object']=='GUEST_LAYERED_SANDSTONE_COURSES' else ('先命中同组head接缝' if p['blocking_object'] else '原顶点可见；源身份待独审')
    table.append('|%s|%s|%s|%s %s|%.3f|%s|'%(p['id'],p['role'],tuple(p['pixel']),name,where,p['residual_px'],vis))
md='''# Guest exterior A10：12a 固定对应点诊断

**GEO-07 验收仍 NOT_RUN；本次镜头/对应解释未通过。** 已完成一个可复核的15点候选（8拟合、7完全保留），世界秩3；没有得到8个独立验证且实际可见的可靠结构点。不存在相机保存、渲染、建筑改动或残差驱动换点。

场景为 `scene/Fallingwater_guest_bays_candidate12a.blend`，SHA `'''+fit['scene_sha256']+'''`。源图 `data/photo_refs/guest_exterior_10.jpg`，HABS PA-5346-A-10，742×1024；图注PDF第一页明确摄影师 Jack E. Boucher、1985年2月和3月，A10具体日未注。不是2010照片；2010 guest01/02/04仅提供跨年代结构拓扑控制。没有证据表明这段时间屋顶发生改变，不能用日期差自动解释不一致。

源图及 guest01南铺地、guest02挑檐外轮廓/矩形开孔、guest03南立面、guest04完整剖面均已实际打开。固定点文件 `data/photo-match-points12-guest-exterior.json` 的 SHA 为 `'''+lock['sha256']+'''`，先写后实际打开 `photo-match12-guest-observed.png`，之后仅执行一次拟合。新原生图纸裁片也已实际打开。图纸裁片红色窗点表示**当前模型的坐标**，不表示印刷窗柱圆点已经匹配。

## 身份与冻结点

窗点是原片西至东连续柱的上下端候选，模型取实际外边中点；点表逐一列出对象、边的两顶点、相邻面、世界米坐标和置信。7等分窗格及高度为C，不是历史独立尺寸。屋顶R01/R02分别对应guest02外挑檐南侧两转角，R03对应狭长檐梁东端；O0N/O0S为首个真实矩形天窗西边的两下角。屋顶5点均有真实存储顶点，其投影位置射线能命中相同的已求值实体边界。

'''+ '\n'.join(table)+'''

各点的完整未缩写对象名、相邻面索引、源置信、第一命中面/法向和遮挡距离在 `photo-match12-guest-review.json`、`photo-match12-guest-rays.json`。窗下端均先被前侧石皮挡住，距离目标约0.135–0.326m；W0H也被石皮遮住约0.168m。其余窗头先命中同组head，相距约26–41mm，是复合接缝问题，不能把隐藏基网格角称为照片可见点。8个拟合位置虽能计算，并未完成“8个可靠实际可见对应”的资格。

近/远台阶按图纸锁定W1/W2组，保留实际连续踏步边投影；未把粗石层理逐条当作踏步，也未凭图像虚构单级顶点。当前阶数/绝对高度仍C，不能用于精准拟合掩盖窗面问题。

## 唯一相机与数值的实际限制

相机优化仅旋转3、眼位3、焦距1，主点固定(371,512)，正方像素，无畸变、裁切、图像变形或剔除离群点。眼位(1.079343,33.615675,7.705283)m；焦距809.834928px，**36mm长边等效28.470759mm**。若用36mm横边定义则39.291182mm；二者不能在竖幅中混写。15点都在镜头前，图像凸包18.38%，拟合世界秩3。

|分组|中位误差|最大误差|
|---|---:|---:|
|8拟合点|11.807px|19.169px|
|7保留点|9.647px|37.225px|
|全部|10.377px|37.225px|

原片对角线1%为12.646px。虽然总中位低于1%，远檐R03保留点为2.944%，不能汇总成通过。R01本轮是训练点，05是未验证保留点；**不能把旧232.50px与新15.90px直接称为独立精度改善**。

实际射线向下首先命中真实 `SITE_Continuous_BearRun_Terrain`，顶Z7.245883m，镜头仅高0.459400m；0.18m周边5点高度范围0.440–0.491m，不能当正常站立导航机位。低机位摄影并非物理不可能，但档案未证明使用低三脚架/蹲姿。

拟合向上倾斜约'''+f'{pitch:.3f}'+'''°，W0投影上下端横移26.44px，而原片柱近竖直。固定扫描中心主点这一摄影假设未由档案确认；真实建筑摄影移轴或扫描偏心可能影响，但这一轮没有增加自由主点或再次拟合。屋顶误差因此只说明当前**源身份/模型/镜头组合**不一致，不能据它扭曲图纸建筑。

## 实际打开的连续边证据

`photo-match12-guest-continuous-edges.png` 是标明QA的原片加真实网格投影线；红屋顶、青窗、橙台阶。它不是渲染成果。R02–R03模型线从(599.115,458.796)到(627.438,559.933)，照片对应(601,469)到(596,540)，长边方向和端部位置都不合。10个实际屋顶洞下边界形成一致漂移，不能只报告首孔局部误差。近窗柱倾斜、窗台位置及W1/W2踏步与石墙接头也不吻合。没有为了重叠好看隐藏线段或改变模型。

下一有界步骤是独立审查：首先核R03是否确属长梁终端、近窗柱W0属于西回角还是第一窗柱，并区分照片可见head/sill复合轮廓和模型隐蔽边。原生guest01红点与实际窗柱符号偏离已经明确，源约束的窗面复核应先于任何新的相机点集。若后续采用不同摄影主点协议，也须新轮冻结，不回填本轮点表。

## 交接和保留

- `photo-match12-guest-observed.png`：先验锁点图。
- `photo-match12-guest-source-plan-roof.png`、`photo-match12-guest-source-plan-window-stairs.png`：原生图纸对应身份和C模型位置。
- `photo-match12-guest-points-overlay.png`、`photo-match12-guest-continuous-edges.png`：已实际打开的唯一镜头QA叠图。
- `photo-match12-guest-fit.json`：固定镜头及全部残差；`photo-match12-guest-rays.json`：真实场景面/支撑/遮挡。
- `photo-match12-guest-review.json`：逐点资格与验收未完成原因；`photo-match12-guest-manifest.json`：所有本轮文件哈希。

05点表、报告、失败投影与12a原场景均保留。依neat-freak收尾核对本任务交接文件；根STATUS/AGENTS/中央验收表与其他模块未改。没有提交或推送。
'''
(ROOT/'qa/photo-match12-guest-review.md').write_text(md,encoding='utf-8')
files=sorted((ROOT/'qa').glob('photo-match12-guest-*'))+[Path(lock['file'])]
manifest={'scene_sha256':fit['scene_sha256'],'original_scene_unchanged':True,'point_file_unchanged':True,
 'status':'UNVERIFIED_DIAGNOSTIC; GEO07 acceptance NOT_RUN','images_actually_opened_before_review':[
 'guest_exterior_10.jpg','photo-match12-guest-source-roof-stairs-crop.png','photo-match12-guest-observed.png',
 'photo-match12-guest-source-plan-roof.png','photo-match12-guest-source-plan-window-stairs.png',
 'photo-match12-guest-points-overlay.png','photo-match12-guest-continuous-edges.png'],
 'files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files if p.is_file() and p.name!='photo-match12-guest-manifest.json']}
(ROOT/'qa/photo-match12-guest-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'files':len(manifest['files']),'pitch':pitch,'review':review['result'],'scene_unchanged':True},indent=2))
