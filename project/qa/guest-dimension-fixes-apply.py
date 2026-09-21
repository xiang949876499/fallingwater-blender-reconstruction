from pathlib import Path
import json,hashlib,copy
p=Path('D:/zx/test/project');q=p/'qa';dp=p/'data/guest_house.json';sp=p/'scripts/guest_house.py'
for a in [dp,sp]:(q/('guest-dimension-fixes-before-'+a.name)).write_bytes(a.read_bytes())
d=json.loads(dp.read_text(encoding='utf-8'));sx,sy=d['registration']['meters_per_pixel'];walls={w['id']:w for w in d['walls']};rooms={r['id']:r for r in d['rooms']};slabs={r['id']:r for r in d['slabs']};roofs={r['id']:r for r in d['roofs']}
changes=[]
def note(ids,description,coordinates):changes.append({'anchors':ids,'change':description,'coordinates_normalized_px':coordinates})
# Shared guest bathroom partition and southern facade: preserve east doorway X and north spine.
xpart=632-(4.8006+.09+.11)/sx
yfront=350+(4.2926+.21+.095)/sy
dx=xpart-532;dy=yfront-432
for wid in ['GUEST_L1_BATH_WC_NORTH','GUEST_L1_BATH_EAST','GUEST_L1_BATH_SOUTH','GUEST_L1_BED_FRONT']:
 for k in ['a','b']:
  if walls[wid][k][0]==532:walls[wid][k][0]=xpart
for wid in ['GUEST_L1_BATH_EAST','GUEST_L1_BATH_SOUTH','GUEST_L1_BED_FRONT','GUEST_L1_BED_EAST']:
 for k in ['a','b']:
  if walls[wid][k][1]==432:walls[wid][k][1]=yfront
walls['GUEST_L1_BATH_WEST']['b'][1]=yfront
# Keep the existing east-door physical endpoints and width while extending the southern tail.
ew=walls['GUEST_L1_BED_EAST']
for op in ew['openings']:op['span']=[v*78/(yfront-354) for v in op['span']]
rooms['GUEST_L1_GUEST_ROOM']['polygon']=[[xpart+2.1,354.1],[629.8,354.1],[629.8,yfront-2],[xpart+2.1,yfront-2]]
rooms['GUEST_L1_GUEST_ROOM']['center']=[(xpart+632)/2,(354+yfront)/2]
rooms['GUEST_L1_GUEST_ROOM']['entry']=[xpart+1,374]
for f in rooms['GUEST_L1_GUEST_ROOM']['furniture']:
 if f['type']=='cabinet':f['center'][1]+=dy
rooms['GUEST_L1_BATH']['polygon']=[[479,399],[502,399],[502,385],[xpart-2,385],[xpart-2,yfront-2],[479,yfront-2]]
rooms['GUEST_L1_BATH']['center']=[514,416]
rooms['GUEST_L1_GALLERY']['polygon']=[[441,357],[xpart+2,357],[xpart+2,381],[506,381],[506,394],[442,394]]
tr=rooms['GUEST_L1_TERRACE']
for v in tr['polygon']:
 if v[1]==433:v[1]=yfront+2.1
tr['notes']+=' Guest/bath south facade moved to clear printed room dimensions; terrace census follows south exterior face plus trace margin, pool exclusion retained.'
note(['GUEST_GUEST_ROOM_LENGTH','GUEST_GUEST_ROOM_DEPTH'],'Move shared bath partition east and connected guest/bath south facade south; preserve north spine, east doorway endpoints and pool. Coordinate bath cork finish, guest/gallery/terrace polygons and south cabinet.',{'bath_east_x':xpart,'south_y':yfront})
# Boiler dimensions: expand to the north/east; keep west access and southern wall datum.
bn=348-(1.397+.30)/sy;be=326+(2.4892+.11+.15)/sx
for w in [walls['GUEST_L1_BOILER_'+s] for s in ['NORTH','EAST','SOUTH','WEST']]:
 for k in ['a','b']:
  if w[k][1]==320:w[k][1]=bn
  if w[k][0]==377:w[k][0]=be
# Preserve west-door exact old endpoints; prevent moving its access with longer north tail.
bo=walls['GUEST_L1_BOILER_WEST']['openings'][0];bo['span']=[(320+28*v-bn)/(348-bn) for v in bo['span']]
rooms['GUEST_L1_BOILER']['polygon']=[[328.2,bn+3],[be-3,bn+3],[be-3,345.1],[328.2,345.1]]
rooms['GUEST_L1_BOILER']['center']=[(326+be)/2,(bn+348)/2];rooms['GUEST_L1_BOILER']['entry']=[328.2,334.7]
slabs['GUEST_L1_BOILER_FLOOR']['polygon']=[[326,bn],[be,bn],[be,348],[326,348]]
roofs['GUEST_BOILER_ROOF']['polygon']=[[323.8,bn-2.9],[be+3,bn-2.9],[be+3,346],[323.8,346]]
note(['GUEST_BOILER_DIM_1','GUEST_BOILER_DIM_2'],'Northern/eastern structural faces follow printed 4ft7in x8ft2in clear room label; floor/roof/census follow revised walls and existing west-door endpoints remain fixed.',{'north_y':bn,'east_x':be})
# Basement: retain east stair/entry and south edge; correct the two partitions and outer envelope coherently.
ben=420-(3.5306+.14+.13)/sy
bex=285-(2.9464+.11+.065)/sx
bwx=bex-(1.5494+.13+.018)/sx
bny=420-(2.032+.065+.13+.018)/sy
# Independent source chain:18ft9 7/8in between west inner face and east outer face.
overall=(18*12+9.875)*.0254
outerwest=285+.11/sx-overall/sx-.135/sx
for wid in ['GUEST_B1_BASE_WEST','GUEST_B1_BASE_NORTH_SPLAY','GUEST_B1_BASE_NORTH','GUEST_B1_BASE_EAST','GUEST_B1_BASE_SOUTH']:
 w=walls[wid]
 for k in ['a','b']:
  if w[k][0]==196:w[k][0]=outerwest
  if w[k][1]==351:w[k][1]=ben
# Preserve basement entry actual endpoints.
bdoor=walls['GUEST_B1_BASE_EAST']['openings'][0];bdoor['span']=[(351+69*v-ben)/(420-ben) for v in bdoor['span']]
for wid in ['GUEST_B1_BASE_BATH_NORTH','GUEST_B1_BASE_BATH_EAST','GUEST_B1_BASE_BATH_WEST']:
 w=walls[wid]
 for k in ['a','b']:
  if w[k][0]==201:w[k][0]=bwx
  if w[k][0]==230:w[k][0]=bex
  if w[k][1]==377:w[k][1]=bny
  if w[k][1]==418:w[k][1]=420
# Keep bathroom door width from old41px segment; its center follows new partition.
bdoor=walls['GUEST_B1_BASE_BATH_EAST']['openings'][0];bdoor['span']=[(377+41*v-bny)/(420-bny) for v in bdoor['span']]
bath=rooms['GUEST_B1_BATH'];bath['polygon']=[[bwx+1.43,bny+1.43],[bex-1.43,bny+1.43],[bex-1.43,417.34],[bwx+1.43,417.34]];bath['center']=[(bwx+bex)/2,(bny+420)/2];bath['entry']=[bex-1.5,387.66]
lau=rooms['GUEST_B1_LAUNDRY'];lau['polygon']=[[220,ben+2.7],[282.8,ben+2.7],[282.8,417.4],[bex+1.3,417.4],[bex+1.3,bny-1.3],[bwx+1.3,bny-1.3],[bwx+1.3,364.5]];lau['center']=[255.6,390];lau['entry']=[282.8,365]
# Reclip one-sided cork lining to the moved bathroom span, leaving laundry concrete face clear.
south=walls['GUEST_B1_BASE_SOUTH'];south['interior_finish']['span']=[(bwx-outerwest)/(285-outerwest),(bex-outerwest)/(285-outerwest)]
slabs['GUEST_B1_FLOOR']['polygon']=[[outerwest,364],[219,ben],[285,ben],[285,420],[outerwest,420]]
# The corrected basement extends below grade west/north of L1. Only that difference gets a ceiling extension.
d['slabs'].append({'id':'GUEST_B1_CEILING_EXTENSION','level':'L1','thickness':.24,'polygon':[[outerwest,364],[219,ben],[285,ben],[285,350],[207,350],[193,364],[193,420],[outerwest,420]],'notes':'Below-grade basement extension follows printed room dimensions and18ft9 7/8in overall width; top remains guest L1datum, no room above this extension.'})
for rid in ['GUEST_B1_BATH','GUEST_B1_LAUNDRY']:rooms[rid]['notes']+=' Corrected finished-face dimensions and adjacent envelope from sheet1 labels; east stairs and entrance retained. See qa/guest-dimension-fixes.json.'
note(['GUEST_LAUNDRY_LENGTH','GUEST_LAUNDRY_DEPTH','GUEST_BASE_BATH_LENGTH','GUEST_BASE_BATH_WIDTH'],'Retain east stair and south datum; shift north envelope, shared bath partition and west bath wall; basement outer west face constrained by separately read18ft9 7/8in source chain. Revised slab, extension ceiling, room polygons, cork spans and opening fractions.',{'north_y':ben,'bath_east_x':bex,'bath_west_x':bwx,'bath_north_y':bny,'outer_west_x':outerwest,'overall_west_inner_to_east_outer_m':overall})
# Coping: clear inner shell stays exactly unchanged; exterior horizontal chain controls uniform ring width.
d['pool']['coping_width_m']=(9.617075-d['pool']['size_m'][0])/2
d['pool']['coping_reference']='HABS PA-5346-A sheet1 exterior31ft6 5/8in chain; source round-corner ring; same offset onall sides C.'
s=sp.read_text(encoding='utf-8');s=s.replace("pooltop=gz+.70485;waterz=pooltop-.14;basin=gz-.91;inner=rounded(w,dep,radius);outer=rounded(w+.29,dep+.29,radius+.145)","coping_width=pool.get('coping_width_m',.145)\n    pooltop=gz+.70485;waterz=pooltop-.14;basin=gz-.91;inner=rounded(w,dep,radius);outer=rounded(w+2*coping_width,dep+2*coping_width,radius+coping_width)")
sp.write_text(s,encoding='utf-8')
note(['GUEST_POOL_OUTER_WIDTH'],'Keep clear shell, water and steps; widen only outside shell/coping ring to exterior31ft6 5/8in witness dimension.',{'coping_width_m':d['pool']['coping_width_m']})
for w in d['walls']:
 if w['id'].startswith('GUEST_L2_UPPER_TERRACE_'):
  w['height']=4.511675-d['levels']['L2']['offset'];w['reference']='HABS sheet4 west TOP OF STONE WALL14ft9 5/8in relative MAIN LEVEL0; floor SECOND LEVEL7ft8 5/8in';w['evidence']='A datum; B/C matching pointed upperterrace enclosure acrossplan/elevation'
note(['GUEST_TOP_STONE'],'Raise allfour pointed upperterrace enclosure walls to printed topdatum; floor remains2.352675m. Eye-level view through north/pointed terrace is correctly enclosed rather than low-parapet open.',{'wall_height_above_L2_m':4.511675-d['levels']['L2']['offset'],'top_above_L1_m':4.511675})
d['dimension_fix_revision']='iteration04 guest corrections; sourceverified; actual mesh QA pending'
dp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
report={'status':'PENDING_ACTUAL_MESH_QA','baseline':'qa/guest-dimensions-measured.json','changes':changes,'limitations':['Clear-face interpretation from printed roomlabels is explicit; source tracing isnot survey-grade.','Basement overall chain18ft9 7/8in read separately fromoriginal; footprint belowgrade expanded west to keep eaststair fixed.','Pool uniformcoping width inferred fromsource ring rather than separatelydimensioned transversecoping.','No working.blend overwritten; integrationscene and furnishing/terrainregression stillrequired.']}
(q/'guest-dimension-fixes.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(changes,ensure_ascii=False,indent=2))
