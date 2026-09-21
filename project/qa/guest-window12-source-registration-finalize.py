"""Singlefacade source/evaluatedgeometry handoff, preserving all prior failures."""
from pathlib import Path
import json,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'qa/guest-window12-source-registration-probe.json').read_text(encoding='utf-8'))
src=data['source_records'];posts=data['model_posts'];objs=data['objects']
assert hashlib.sha256(Path(data['scene']).read_bytes()).hexdigest()==data['scene_sha256']
source_points=src['points'];sy=source_points[0]['world_plan_xy_m'][1]
span_source=source_points[-1]['world_plan_xy_m'][0]-source_points[0]['world_plan_xy_m'][0]
span_old=posts[-1]['center_world_m'][0]-posts[0]['center_world_m'][0]
sections=[r for p in posts[1:7] for r in p['crosssections'] if r['z']<8.68 and r['stone_first_hit']]
depth=[r['frame_outerY_minus_stone_frontY_m'] for r in sections]
skindepth=[35.95560073852539-r['stone_first_hit']['position_m'][1] for r in sections if r['stone_first_hit']['object'].startswith('GUEST_LAYERED')]
obnames=list(objs)
targets=[n for n in obnames if n.startswith('GUEST_L1_LOUNGE_FRONT_')]
whitelist={'primary_front_glazing_and_backing':targets,
 'west_terminal_interface_only':['GUEST_L1_WEST_LOUNGE_pier_end','GUEST_C10_WEST_LOUNGE_WINDOW_mullion_3','GUEST_C10_WEST_LOUNGE_WINDOW_glass_2','GUEST_C10_WEST_LOUNGE_WINDOW_SILL','GUEST_C10_WEST_LOUNGE_WINDOW_sill','GUEST_C10_WEST_LOUNGE_WINDOW_head'],
 'conditional_tiny_support_extensions':['GUEST_C10_FRONT_LOUNGE_EXPOSED_PLINTH','GUEST_C10_WEST_LOUNGE_EXPOSED_PLINTH'],
 'batched_skin_scope':'Only connectedstonecourse components that belong to correspondingfrontcaps/baseor westendstub; never entire batchedGUEST_LAYERED_SANDSTONE_COURSES mesh recreation.',
 'protected':'Roof/openings/easttrueentry/gueststairs/bridge/Theaterbays/servicewing/furniture/lighting/cameras/routes/materialnodes and allothercoursevertices.'}
clear=[
 {'id':'GWIN01','finding':'2010source shows7intermediatepostsymbols plus2returns=8intervals; evaluatedmodelhas8same38mmgenericmullions and7glassmeshes.',
  'evidence':'B/A source topology, C tracing/profiles; actualmesh count verified','repair_qualification':'SOURCE_CLEAR_COUNT_AND_TOPOLOGY_ERROR'},
 {'id':'GWIN02','finding':'Currentpane/postaxis normalizes toY442.000; actualdrawnfrontaxisY444.35±0.25. Registrationdifference0.123892m north/inboard.',
  'evidence':'B traced sourceaxis; exactworld transform fixed','repair_qualification':'SOURCE_CLEAR_AXIS_MISREGISTRATION; actualsillfinishallocationstillC'},
 {'id':'GWIN03','finding':'Currentgeneric frontopening has0.237571mwide fullheightstoneendpieces. WestA10is glazed90degcorner, guest01also hasglazedreturn; modelwestendstubstops oldwestwindow0.472896m before sourcedsouthcorner.',
  'evidence':'B photo+plan topology; sourceZ/detailC','repair_qualification':'SOURCE_CLEAR_WRONG_WEST_SOLID_CORNER'},
 {'id':'GWIN04','finding':'FrozenoldA10W0..W7 labels were paired withgeneric0..7indices. PhotoW7 iscandidatelastprincipalP4; modelindex7 isendjambaxis, notsourceP4.',
  'evidence':'B alternatingphoto/plansequence, U exactcrossdatefinegeometry','repair_qualification':'CLEAR_CORRESPONDENCE_INDEX_MISMATCH; do notsimplytranslateeachindexedposttowarditsoldphotoassignment'}]
unknown=[
 {'id':'GWU01','finding':'1985photo and2010plan show compatiblecorner/alternatingpostorder, but preciseX/Yproportions acrossdates are not independentlysurveyed; noassertedrenovation.'},
 {'id':'GWU02','finding':'Lowerpointobscuration alone is notamodelfault: stonecaps maynaturallyprojectand lowviews concealpostfeet. Modelactual setback measured71..108mm; historicalsetbacknotdimensioned.'},
 {'id':'GWU03','finding':'Sourceplan exteriorline aroundY450 is a separate loweroutline/band; do notassignit towindowaxis orforceallroughstonefrontfacestoit withoutsectionidentity.'},
 {'id':'GWU04','finding':'ExactA10E_RETURNpixel is not registered; source9thplanstation doesnotprove a9thfreestandingcolumn visibleinA10.'},
 {'id':'GWU05','finding':'Principal/secondary tubeprofiles, sourcewindowhead/sillheightandoperablecasementhorizontalbars remainB/C; no newprintedheight orclearbaywidthanchors.'}]
proposal={'name':'One source-registered southfrontwindowassembly correction',
 'status':'READ_ONLY_PROPOSAL_NO_CANDIDATE_OR_HELPER_CREATED',
 'geometry_basis':'Keepglobalregistration/scale and existingwindowverticaldatum; trace2010frontglazingaxisandbothreturns; use sevenrealintermediatepoststations insteadofuniformdivision.',
 'axis_world_Y':sy,'boundary_world_X':[source_points[0]['world_plan_xy_m'][0],source_points[-1]['world_plan_xy_m'][0]],
 'source_axis_uncertainty_m':[.25*.05256,.25*.05272],
 'vertical_bounds_preserved_C':[8.68,10.50],
 'components':'Rebuild onlyfrontglazing/frameassemblyinto8intervals withJ_W,P1,M1,P2,M2,P3,M3,P4,J_E roles; replaceabove-sillgenericweststonecapand oldwestendstubwithclosedglassreturn; close eastjambtotracedwallreturn.',
 'bottom_support_rule':'Re-seat everypost/frameonclosedphysicalbacking/sillinsideexistingtracedband. Afteroutboard123.892mmshift, currenthiddencorealone wouldnotcarrythewholeframefootprint; this requireslocalbacking/sillreturnconstructionC, not deletingroughstone to expose a chosenphoto point.',
 'stone_rule':'Retainnaturalcourseshapesunless they belong tosourcecontradictedfullheightendcaps. Neverflattensills/entirestonebatch toforcevisibility.',
 'dimensions_rule':'Return-stationaxis span5.839416m versus currentendpointaxis span5.464138m are raster-deriveddiagnostics, notprintedclearwidthanchors. Preserveknownsourceanchors,wholehouseoutline androof; do notrescalebuildingorusephotoresiduals.',
 'scope':whitelist,
 'required_future_checks':['Closedpane/frame/sill/endjoints','Framefootprint actualsupportandadjacentnorth/southfloorfaces','All non-targetobject/material/camera/routefingerprints','Existingserviceandtrueeastentrypassagesremainunchanged','Same-sourceA10identityreviewbeforeanynewphotofit; previousfitfailuresretained']}
out={'schema':'fallingwater.guest_window12.source_registration.v1','scene_sha256':data['scene_sha256'],
 'source':src,'actual_model_columns':posts,'clear_findings':clear,'unresolved_findings':unknown,'single_minimal_proposal':proposal,
 'summary_dimensions':{'actual_mullion_section_m':[.038,.038],'post_Z':[8.680000305,10.5],
  'actual_axis_Y':posts[0]['center_world_m'][1],'source_axis_Y':sy,'axis_northward_error_m':posts[0]['center_world_m'][1]-sy,
  'old_endpoint_axis_span_m':span_old,'source_return_axis_span_m':span_source,
  'source_num_glazing_intervals':8,'model_num_glass_meshes':7,
  'core_front_Y':35.9556007385,'mullion_outer_Y':36.026599884,
  'visible_stone_to_mullion_outer_depth_m':[min(depth),max(depth)],'sampled_course_projection_beyond_core_m':[min(skindepth),max(skindepth)]},
 'scope':'Read-only oneLounge southfacade. No newcamera fit/projection/render. Frozen12a unchanged. Sharedproduction/helper/data nevermodified.',
 'prior_photo_point_files':'All15oldlockedpositions andbothcameraresults remain unchanged; thisnewregistration doesnotretroactivelyreplacepoints.',
 'cleanup':'neat-freak review limited toownedQA handoff/manifest; parentSTATUS/AGENTS untouched.'}
(ROOT/'qa/guest-window12-source-registration-review.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
# Compare drawingaxis stations and savedmodelstations directly inworldplan, not aphoto camera.
fig,(ax,bx)=plt.subplots(2,1,figsize=(13,6),gridspec_kw={'height_ratios':[1.4,1]},constrained_layout=True)
sx=[p['world_plan_xy_m'][0] for p in source_points];mx=[p['center_world_m'][0] for p in posts]
ax.plot(sx,[sy]*9,'o-',color='#b31c27',label='2010 traced source axis /actualsymbols')
ax.plot(mx,[posts[0]['center_world_m'][1]]*8,'s-',color='#087dbe',label='12a evaluated genericmullion centers')
for p in source_points:ax.annotate(p['source_id'],p['world_plan_xy_m'],xytext=(0,-20),textcoords='offset points',ha='center',color='#b31c27')
for i,p in enumerate(posts):ax.annotate(str(i),(p['center_world_m'][0],p['center_world_m'][1]),xytext=(0,9),textcoords='offset points',ha='center',color='#087dbe')
ax.set(xlabel='World X (m)',ylabel='World Y (m)',title='One facade only: source stations vs actual saved12a | no photo fit',ylim=(sy-.10,sy+.24));ax.legend(loc='upper left');ax.grid(alpha=.2)
ax.text(6.5,sy+.058,'0.123892m inboardaxis shift; source8intervals /model7intervals',ha='center',fontsize=10)
p=posts[3];bb=p['evaluated_bounds'];core=objs['GUEST_L1_LOUNGE_FRONT_sill_0']['evaluated_bounds'];sill=objs['GUEST_L1_LOUNGE_FRONT_steel_window_0_sill']['evaluated_bounds']
for b,color,label in [(core,'#a68a64','savedstonecore'),(bb,'#266a99','savedpost'),(sill,'#9b302e','savedsillframe')]:
    bx.add_patch(Rectangle((b[1][0],b[2][0]),b[1][1]-b[1][0],b[2][1]-b[2][0],facecolor=color,alpha=.55,label=label))
q=[r for r in p['crosssections'] if r['stone_first_hit'] and r['z']<8.68]
bx.scatter([r['stone_first_hit']['position_m'][1] for r in q],[r['z'] for r in q],color='black',zorder=4,label='actualhorizontalray hits (notinterpolatedskin)')
bx.axvline(sy,color='#b31c27',ls='--',label='sourceaxis only; notstonefrontsurface')
bx.set(xlabel='World Y (south/exterior left)',ylabel='World Z (m)',title='Evaluated physical section at modelcolumn3 | lowercorner obscuration is not alone a defect',xlim=(35.89,36.16),ylim=(8.45,8.82));bx.grid(alpha=.2);bx.legend(fontsize=8,loc='upper left')
fig.savefig(ROOT/'qa/guest-window12-source-registration-model-section.png',dpi=160);plt.close(fig)
rows=['|照片列候选|图纸身份|归一化XY|原始像素XY|世界XY m|','|---|---|---|---|---|']
for p in source_points:
    rows.append('|%s|%s %s|%s|(%0.2f,%0.2f)|(%0.6f,%0.6f)|'%(p['photo_column_candidate'],p['source_id'],p['plan_identity'],tuple(p['normalized_plan_xy']),*p['original_plan_pixel_xy'],*p['world_plan_xy_m']))
modelrows=['|模型mullion索引|当前归一化X|当前世界X m|说明|','|---|---:|---:|---|']
for p in posts:modelrows.append('|%d|%.6f|%.6f|%s|'%(p['index'],p['center_plan_normalized'][0],p['center_world_m'][0],'端jamb的同型构造；不等于照片柱同索引' if p['index'] in (0,7) else '无主柱/次梃区分的等分位置'))
md='''# Guest Lounge 南窗：逐列源登记与最小修正建议

**可确认当前南窗的分格、轴线和西转角构造未按已采用的2010图纸登记。** 八个照片竖线不能继续机械配给八个模型同名编号；这也是两次镜头诊断仍未通过的重要资格问题。本轮只读，没有新拟合、模型修改或渲染。

冻结12a SHA `'''+data['scene_sha256']+'''`，实际已求值网格与射线见 `guest-window12-source-registration-probe.json`。所有原15点及两次相机失败文件保持不变。

## 先分清“八列”的身份

guest01原生TIFF与带格网细部、A10西玻璃转角/东末端放大及逐列标注图均实际打开。图纸是 **4个大主柱P +3个小次竖梃M =7个中间站**。连同西90°玻璃转角J_W，构成A10可见8列的有据候选；东端另有贴墙返角J_E，是第9个边界站，不是第9根自由柱。两返角间共有8段玻璃。源图西角确为折返玻璃而非全高石墩；照片圆柱/细梃交替，也与P/M顺序吻合。

当前模型却是8根完全同型38×38mm竖框、7块等分玻璃；端头0、7本来承担generic jamb角色。尤其照片W7是末根主柱P4候选，模型7却靠东终止，不能按序号当同一身份。

## 原像素、归一化和世界登记

guest01为17673×13632px；归一化横宽1024，原像素比例17.2587890625，归一化高度789.858428。无旋转。世界转换沿当前项目固定值：`X=3.4+(u-325)*0.05256`，`Y=37.1+(422-v)*0.05272`。下表读取图纸柱心/折返点，约±0.25归一化像素（XY约±13.14/13.18mm）；这是B/C描图，**不是新增A级打印尺寸**。

'''+ '\n'.join(rows)+'''

照片为1985年2–3月，图纸为2010年。拓扑顺序的相容性是B级证据，不证明每个1985实物尺寸与2010完全一致；没有任何翻修日期结论。E_RETURN在A10中的精确像素边界仍U，未虚构新照片点。

模型当前每根中心Y=36.045600891m，归一化v≈442.000；源窗轴v≈444.35、Y=35.921708m，模型退后/北移约 **123.893mm**。图纸各主柱和次梃不在当前均分柱位；对象、已求值边界和实际玻璃洞段均逐一保存在probe/readout。

'''+ '\n'.join(modelrows)+'''

当前端柱轴间5.464138m；源两返角轴间5.839416m。这是轴站跨度，不是玻璃净宽或印刷开口尺寸。不能用源跨度去整体缩放房屋，也不能把旧W0..W7与源表强行一一平移：旧索引分配本身就不正确。

## 石皮、窗脚与转角的实际几何

南窗基底：core外面Y35.955601m，厚约0.180m；竖框外面Y36.026600m，玻璃外面Y36.041599m。内侧6柱截面实测石皮突出core约'''+f'{min(skindepth)*1000:.1f}–{max(skindepth)*1000:.1f}'+'''mm，当前石面到竖框外面约'''+f'{min(depth)*1000:.1f}–{max(depth)*1000:.1f}'+'''mm。低机位看到的下端被石台挡住是实际前后关系，**遮挡本身不证明石皮错误**；不能把石头削平来让旧点可见。

更明确的矛盾是西转角：`GUEST_L1_LOUNGE_FRONT_pier_0` 全高8.4–10.56m，X3.715360–3.952931m；旁边 `GUEST_L1_WEST_LOUNGE_pier_end` 也是全高石段，Y36.151039–36.394608m。旧西窗停在Y36.394608，而图纸南角是35.921708，相隔约0.472900m。A10同一转角是上下横框相接的折返玻璃，两端generic全高石堵和缺失玻璃返角不能由“历史不同”自动解释。全高石挡住W0H与单纯低窗脚被凸石遮挡，是不同问题。

图纸约v450的外侧粗轮廓与v444.35窗轴也不同；它可能属于下方石基/铺地投影边，不应没有剖面身份就把整批石面拉到它上面。新来源精度不足以确定粗石每块、柱截面、窗头窗台高度、逐扇横框与开扇细节；这些仍B/C/U。

## 单一最小修正建议

建议下一候选只把 **这面南窗作为一个源登记的连续构造单元重建**：以J_W–P1–M1–P2–M2–P3–M3–P4–J_E九个轴站形成8段玻璃，沿源Y35.921708排列；保持现Z8.68–10.50的C高度和全局注册/尺度。将错误generic西全高端堵及其最末短西墙段改为源确证的玻璃转角，东端接真实贴墙返角，保留主体墙/屋顶/房间轮廓和已测独立尺寸。

这一项需同时做好窗脚与端部闭合。窗轴向外移后，旧隐藏core不能自动承担整个新框脚，必须在原图已有带状范围内配置局部背衬/窗台连接；厚度分配注明C施工解释。保留自然石层理，只有属于源矛盾全高端堵的局部石饰才随该实体调整；不隐去整批石皮，不靠开孔暴露旧配准点。

目标白名单在review.json：主要 `GUEST_L1_LOUNGE_FRONT_*`；西角仅 `GUEST_L1_WEST_LOUNGE_pier_end` 和既有 `GUEST_C10_WEST_LOUNGE_WINDOW` 最末接口；必要时两块EXPOSED_PLINTH仅做小范围支撑闭合。主屋/服务梯、东南真门、客楼11/12bay、桥、屋顶开孔、家具灯光及全部路线/相机不在范围内。框脚实体接触、端部闭合、邻接地板/门净空、非目标指纹应独立复验；该建议本轮未建模实施。

已实际打开 `guest-window12-source-registration-model-section.png` 的世界平面/实体截面图；它不使用任何照片拟合相机。详细数据：sources.json、probe.json、readout.json、review.json。直接cmd引号启动Blender失败日志probe.log保留，后由直接Python子进程启动CPU4成功probe-run.log；没有改用户打开的场景。neat-freak按拥有的QA范围整理交接与freeze，不改rootSTATUS/AGENTS/旧数据。
'''
(ROOT/'qa/guest-window12-source-registration-review.md').write_text(md,encoding='utf-8')
files=sorted((ROOT/'qa').glob('guest-window12-source-registration-*'))
freeze={'scene_sha256':data['scene_sha256'],'scene_unchanged':True,'no_new_camera_fit':True,'renders':0,'model_edits':0,
 'files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files if p.is_file() and p.name!='guest-window12-source-registration-freeze.json']}
(ROOT/'qa/guest-window12-source-registration-freeze.json').write_text(json.dumps(freeze,indent=2),encoding='utf-8')
print(json.dumps({'sourceY':sy,'old_span_m':span_old,'source_span_m':span_source,'setback_m':[min(depth),max(depth)],'skin_projection_m':[min(skindepth),max(skindepth)],'files':len(freeze['files'])},indent=2))
