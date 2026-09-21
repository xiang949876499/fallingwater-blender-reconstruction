"""Main house digitization of HABS PA-5346 sheets 3–6.
Plan boundaries are manually traced from the public 1024 px reference JPEGs.
Dimensional labels have A evidence; traced vertices / unspecified construction
thicknesses are C, not a measured laser scan. Coordinates are in metres.
"""
import math
import json
from pathlib import Path
SX, SY = .0524, .0531
ORIGIN = (327, 540)
LEVELS = {'B':-2.15,'L1':.10,'L2':2.8448,'L3':5.26415}

def xy(p): return ((p[0]-ORIGIN[0])*SX,(ORIGIN[1]-p[1])*SY)
def xyz(p,z): return (*xy(p),z)
def rect(a,b,c,d): return [(a,b),(c,b),(c,d),(a,d)]
ARC_END_ANGLE = math.radians(-65)
ARC_END_INNER = (473+17*math.cos(ARC_END_ANGLE),125+17*math.sin(ARC_END_ANGLE))
ARC_END_OUTER = (473+50*math.cos(ARC_END_ANGLE),125+50*math.sin(ARC_END_ANGLE))
NORTH_UPPER_LANDING = [(431,84),(460,84),(477,87),ARC_END_OUTER,ARC_END_INNER,(460,110),(431,110)]

# ID, source label, level, source polygon (pixel), center, entry, kind.
ROOM_SPECS = [
('MAIN_B_WINE','Wine Cellar','B',[(252,244),(285,244),(285,283),(321,283),(321,309),(253,309)],(277,292),(264,245),'storage'),
('MAIN_B_BATH','Bath','B',rect(291,247,319,282),(305,264),(290,270),'bathroom'),
('MAIN_B_BOILER','Boiler Room','B',rect(334,280,382,324),(357,303),(334,298),'mechanical'),
('MAIN_B_STAIR','Basement Stair','B',[(203,201),(277,201),(277,248),(252,248),(252,228),(203,228)],(249,217),(264,245),'stair'),
('MAIN_B_FOUNDATION_1','Foundation Bay 1','B',[(319,344),(379,337),(379,432),(319,435)],(349,391),(347,435),'foundation'),
('MAIN_B_FOUNDATION_2','Foundation Bay 2','B',rect(395,286,452,446),(423,376),(423,445),'foundation'),
('MAIN_B_FOUNDATION_3','Foundation Bay 3','B',[(466,286),(514,286),(514,325),(524,325),(524,446),(466,446)],(490,375),(490,445),'foundation'),
('MAIN_B_PLUNGE','Plunge Pool','B',[(533,379),(628,379),(628,352),(695,352),(695,357),(706,357),(706,431),(533,431)],(601,401),(691,370),'pool'),
('MAIN_L1_LIVING','Living Room','L1',[(327,259),(383.984732824,259),(383.984732824,277),(448,277),(448,327),(469,340),(528,340),(528,450),(456,450),(456,537),(328,537),(328,461),(314,461),(314,380),(331,380),(331,338),(327,338)],(407,406),(475,340),'living'),
('MAIN_L1_KITCHEN','Kitchen','L1',[(260,230),(320,230),(320,270),(328,270),(328,288),(320,288),(320,321),(307,321),(307,331),(272.5,331),(272.5,319.4),(260,319.4)],(292,281),(324,278.5),'kitchen'),
('MAIN_L1_SERVANT','Servant Sitting Room','L1',[(183.5,228),(193,226),(202,227),(205.5,214.7),(244.5,214.7),(244.5,229.4),(238,229.4),(238,269),(183.5,269)],(210,251),(235,225),'sitting'),
('MAIN_L1_SERVICE_STAIR','Service Stair','L1',[(207,202),(278,202),(278,230),(241,230),(241,219),(207,219)],(256,212),(261,230),'stair'),
('MAIN_L1_ENTRY','Entry','L1',rect(464,301,510,333),(487,318),(507,316),'entry'),
('MAIN_L1_COAT','Coat','L1',rect(495,282,522,300),(509,291),(495,297),'closet'),
('MAIN_L1_STAIR','Main Stair','L1',rect(410,282,473,304),(441,293),(460,310),'stair'),
('MAIN_L1_LOGGIA','Loggia','L1',[(535,307),(565,308),(597,342),(705,342),(705,355),(535,355)],(562,333),(603,350),'loggia'),
('MAIN_L1_TERRACE_W','West Terrace','L1',rect(239,456,324,538),(282,497),(324,488),'terrace'),
('MAIN_L1_TERRACE_E','East Terrace','L1',[(552,379),(597,379),(597,539),(459,539),(459,501),(531,501),(531,457),(459,457),(459,452),(533,452),(533,428),(552,428)],(564,472),(531,431),'terrace'),
('MAIN_L1_HATCH','Living Room Water Stair','L1',rect(459,462,528,498),(490,480),(459,480),'water_stair'),
('MAIN_L2_DRESSING','Dressing Room','L2',[(254,236),(321,236),(321,270),(330,270),(330,300),(309,300),(309,322),(254,322)],(283,282),(321,280),'dressing'),
('MAIN_L2_MASTER','Master Bedroom','L2',[(330,312),(368,312),(368,305),(415,305),(415,405),(323,405),(323,384),(330,384)],(369,359),(380,306),'bedroom'),
('MAIN_L2_BATH_N','Bath (north)','L2',rect(333,238,391,267),(360,253),(336,266),'bathroom'),
('MAIN_L2_BATH_G','Bath (guest)','L2',rect(426,307,461,338),(444,322),(462,324),'bathroom'),
('MAIN_L2_BATH_M','Bath (master)','L2',rect(425,354,461,409),(443,382),(425,377),'bathroom'),
('MAIN_L2_HALL','Hall','L2',[(331,272),(395,272),(395,253),(431,253),(431,255),(536,255),(536,328),(484,328),(484,344),(468,344),(468,301),(480,301),(480,282),(410,282),(410,301),(331,301)],(496,278),(479,278),'hall'),
('MAIN_L2_GUEST','Guest Bedroom','L2',rect(469,342,534,410),(500,382),(471,343),'bedroom'),
('MAIN_L2_TERRACE_W','Dressing Room Terrace','L2',[(75,205),(241,205),(241,299),(75,299)],(157,253),(242,272),'terrace'),
('MAIN_L2_TERRACE_S','Master Bedroom Terrace','L2',rect(322,415,461,577),(390,497),(354,413),'terrace'),
('MAIN_L2_TERRACE_E','Guest Bedroom Terrace','L2',[(545,349),(698,349),(698,412),(545,412)],(616,379),(537,382),'terrace'),
('MAIN_L2_TERRACE_N','North Stair Terrace','L2',[(433,126),(469,126),(469,142),(474,142),(474,176),(471,176),(471,248),(433,248)],(451,214),(449,249),'terrace'),
('MAIN_L2_STAIR','Main Stair L2','L2',rect(397,255,435,274),(415,265),(439,270),'stair'),
('MAIN_L2_CLOSET_M','Master Bedroom Wardrobe','L2',rect(337,308,366,323),(351,315),(351,325),'closet'),
('MAIN_L2_CLOSET_G','Guest Bedroom Wardrobe','L2',rect(486,325,534,339),(510,333),(510,341),'closet'),
('MAIN_L3_STUDY','Study','L3',[(253,237),(310,237),(310,267),(319,267),(319,322),(253,322)],(284,278),(318,291),'study'),
('MAIN_L3_BATH','Bath','L3',rect(336,239,362,278),(349,258),(357,277),'bathroom'),
('MAIN_L3_GALLERY','Gallery','L3',[(332,278),(365,278),(365,291),(434,291),(434,304),(331,304)],(393,292),(331,291),'gallery'),
('MAIN_L3_ALCOVE','Sleeping Alcove','L3',rect(435,259,468,302),(451,280),(435,294),'sleeping_alcove'),
('MAIN_L3_TERRACE','Third Floor Terrace','L3',[(334,308),(430,308),(430,352),(463,352),(463,309),(491,309),(491,286),(526,286),(526,379),(334,379)],(386,344),(386,306),'terrace'),
('MAIN_L3_LINK','North Upper Walk and Spiral Landing','L3',NORTH_UPPER_LANDING,(455,98),(431,98),'loggia'),
('MAIN_L3_STAIR','Gallery Stair L3','L3',rect(367,271,432,291),(398,280),(433,292),'stair'),
]

# True floor continuity across the existing door/wall thickness; no exterior outline is enlarged.
# name, room_id, rectangle in plan pixels, level, finish, short across-door probe path.
THRESHOLDS = [
 ('stair_wine','MAIN_B_WINE',(252,238,276,251),'B','stone_floor',[(264,239),(264,250)]),
 ('study_gallery','MAIN_L3_GALLERY',(318,278,333,303),'L3','cork',[(316,291),(337,291)]),
 ('hall_master','MAIN_L2_MASTER',(367,300,391,307),'L2','cork',[(378,298),(378,310)]),
 ('kitchen_living','MAIN_L1_KITCHEN',(319,269.7,333,287.3),'L1','kitchen_rubber',[(317,278.5),(334,278.5)]),
 # Join the two real floor edges without overlapping their coplanar finishes.
 # Continue under the existing double partition/jambs; aperture remains y255..275.
 ('wine_bath','MAIN_B_BATH',(285,244,291,283),'B','cork',[(281,265),(296,265)]),
 ('hall_dressing','MAIN_L2_DRESSING',(325,271,334,300),'L2','cork',[(323,285),(337,285)]),
 ('dressing_bath','MAIN_L2_BATH_N',(333,266,354,274),'L2','cork',[(343,279),(343,262)]),
 ('master_bath','MAIN_L2_BATH_M',(414,365,427,384),'L2','cork',[(410,375),(430,375)]),
 ('guest_bath','MAIN_L2_BATH_G',(460,313,470,333),'L2','cork',[(456,323),(474,323)]),
 ('dressing_terrace','MAIN_L2_DRESSING',(240,281,255,296),'L2','stone_floor',[(236,289),(259,289)]),
 ('master_terrace','MAIN_L2_MASTER',(368,404,386,417),'L2','stone_floor',[(377,401),(377,420)]),
 ('guest_terrace','MAIN_L2_GUEST',(533,370,548,386),'L2','stone_floor',[(530,378),(551,378)]),
 ('living_west_n','MAIN_L1_LIVING',(323,479,330,500),'L1','stone_floor',[(320,489),(334,489)]),
 ('living_west_s','MAIN_L1_LIVING',(323,516,330,535),'L1','stone_floor',[(320,526),(334,526)]),
 ('living_east','MAIN_L1_LIVING',(527,431,535,449),'L1','stone_floor',[(524,440),(538,440)]),
 ('living_southeast','MAIN_L1_LIVING',(455,517,462,536),'L1','stone_floor',[(452,527),(465,527)]),
 ('living_hatch','MAIN_L1_HATCH',(454,463,461,497),'L1','stone_floor',[(451,480),(461,480)]),
 ('entry_loggia','MAIN_L1_ENTRY',(509,306,537,332),'L1','stone_floor',[(506,318),(540,318)]),
 ('entry_coat','MAIN_L1_COAT',(492,296,512,303),'L1','stone_floor',[(505,292),(505,307)]),
 ('service_top','MAIN_L1_SERVICE_STAIR',(261,204,278,233),'L1','stone_floor',[(270,226),(270,236)]),
 ('servant_entry','MAIN_L1_SERVANT',(229,222.5,268,233.5),'L1','stone_floor',[(231,225),(231,236)]),
 ('gallery_bath','MAIN_L3_BATH',(338,275,363,283),'L3','cork',[(350,272),(350,285)]),
 ('gallery_alcove','MAIN_L3_GALLERY',(432,291,438,304),'L3','cork',[(429,297),(442,297)]),
 ('gallery_terrace','MAIN_L3_GALLERY',(375,302,392,311),'L3','stone_floor',[(383,300),(383,314)]),
]

MEASUREMENTS = [
('MAIN_CHAIN_TOTAL','04','120 ft 4.25 in',120*.3048+4.25*.0254,'x',227,927,.10),
('MAIN_CHAIN_01','04','9 ft 7.25 in',9*.3048+7.25*.0254,'x',227,284,.10),
('MAIN_CHAIN_02','04','7 ft 8.5 in',7*.3048+8.5*.0254,'x',284,328,.07),
('MAIN_CHAIN_03','04','11 ft',11*.3048,'x',328.3714301871854,392.4184810269751,.010),
('MAIN_CHAIN_04','04','24 ft 6 in',24*.3048+6*.0254,'x',393,535,.09),
('MAIN_CHAIN_05','04','11 ft 8 in',11*.3048+8*.0254,'x',535,602,.08),
('MAIN_CHAIN_06','04','17 ft 9 in',17*.3048+9*.0254,'x',602,705,.08),
('MAIN_CHAIN_07','04','13 ft 9 in',13*.3048+9*.0254,'x',705,786,.09),
('MAIN_CHAIN_08','04','22 ft 5.5 in',22*.3048+5.5*.0254,'x',786,916,.09),
('MAIN_CHAIN_09','04','1 ft 11 in',.3048+11*.0254,'x',916,927,.07),
('MAIN_VERTICAL_TOTAL','04','54 ft 9.75 in',54*.3048+9.75*.0254,'y',229,544,.10),
('MAIN_LIVING_NOMINAL_LENGTH','04','48 ft',48*.3048,'nominal',None,None,.15),
('MAIN_LIVING_NOMINAL_WIDTH','04','33 ft 8 in',33*.3048+8*.0254,'nominal',None,None,.15),
('MAIN_KITCHEN_NOMINAL_LENGTH','04','15 ft 9 in',15*.3048+9*.0254,'nominal',None,None,.1),
('MAIN_KITCHEN_NOMINAL_WIDTH','04','12 ft',12*.3048,'nominal',None,None,.1),
('MAIN_SERVANT_NOMINAL_LENGTH','04','11 ft 5 in',11*.3048+5*.0254,'nominal',None,None,.1),
('MAIN_SERVANT_NOMINAL_WIDTH','04','9 ft 4 in',9*.3048+4*.0254,'nominal',None,None,.1),
('MAIN_LEVEL_2','10','9 ft 4 in',9*.3048+4*.0254,'z',0,2.8448,.025),
('MAIN_LEVEL_3','10','17 ft 3.25 in',17*.3048+3.25*.0254,'z',0,5.26415,.025),
('MAIN_ROOF_EAST','10','24 ft 7.375 in',24*.3048+7.375*.0254,'z',0,7.502525,.035),
('MAIN_ROOF_WEST','10','24 ft 11.75 in',24*.3048+11.75*.0254,'z',0,7.61365,.035),
]

ADJACENCY = [
 ('MAIN_B_STAIR','MAIN_B_WINE','open_passage'),('MAIN_B_WINE','MAIN_B_BATH','door'),('MAIN_B_WINE','MAIN_B_BOILER','door'),
 ('MAIN_B_STAIR','MAIN_L1_SERVICE_STAIR','stairs'),('MAIN_L1_SERVICE_STAIR','MAIN_L1_KITCHEN','open_passage'),('MAIN_L1_SERVICE_STAIR','MAIN_L1_SERVANT','door'),
 ('MAIN_L1_KITCHEN','MAIN_L1_LIVING','door'),('MAIN_L1_LOGGIA','MAIN_L1_ENTRY','door'),('MAIN_L1_ENTRY','MAIN_L1_COAT','door'),('MAIN_L1_ENTRY','MAIN_L1_LIVING','open_passage'),
 ('MAIN_L1_ENTRY','MAIN_L1_STAIR','stairs'),('MAIN_L1_STAIR','MAIN_L2_HALL','stairs'),('MAIN_L1_LIVING','MAIN_L1_TERRACE_W','glazed_door'),('MAIN_L1_LIVING','MAIN_L1_TERRACE_E','glazed_door'),
 ('MAIN_L1_LIVING','MAIN_L1_HATCH','hatch_stairs'),('MAIN_L1_LOGGIA','MAIN_B_PLUNGE','exterior_steps'),
 ('MAIN_L2_HALL','MAIN_L2_DRESSING','door'),('MAIN_L2_DRESSING','MAIN_L2_BATH_N','door'),('MAIN_L2_DRESSING','MAIN_L2_TERRACE_W','glazed_door'),
 ('MAIN_L2_HALL','MAIN_L2_MASTER','door'),('MAIN_L2_MASTER','MAIN_L2_BATH_M','door'),('MAIN_L2_MASTER','MAIN_L2_CLOSET_M','cabinet'),('MAIN_L2_MASTER','MAIN_L2_TERRACE_S','glazed_door'),
 ('MAIN_L2_HALL','MAIN_L2_GUEST','door'),('MAIN_L2_HALL','MAIN_L2_BATH_G','door'),('MAIN_L2_GUEST','MAIN_L2_CLOSET_G','cabinet'),('MAIN_L2_GUEST','MAIN_L2_TERRACE_E','glazed_door'),
 ('MAIN_L2_HALL','MAIN_L2_TERRACE_N','door'),('MAIN_L2_TERRACE_N','MAIN_L3_LINK','curved_exterior_stair'),('MAIN_L2_HALL','MAIN_L2_STAIR','open_passage'),
 ('MAIN_L2_STAIR','MAIN_L3_STAIR','stairs'),('MAIN_L3_STAIR','MAIN_L3_GALLERY','open_passage'),('MAIN_L3_GALLERY','MAIN_L3_STUDY','door'),('MAIN_L3_GALLERY','MAIN_L3_BATH','door'),
 ('MAIN_L3_GALLERY','MAIN_L3_ALCOVE','open_alcove'),('MAIN_L3_GALLERY','MAIN_L3_TERRACE','glazed_door'),
 ('MAIN_B_FOUNDATION_1','EXTERIOR_UNDERCROFT','open_bay'),('MAIN_B_FOUNDATION_2','EXTERIOR_UNDERCROFT','open_bay'),('MAIN_B_FOUNDATION_3','EXTERIOR_UNDERCROFT','open_bay')
]

def room_records():
 out=[]
 for rid,label,lev,p,c,e,kind in ROOM_SPECS:
  z=LEVELS[lev]
  if kind=='terrace' and lev=='L1': z=0.
  if kind=='foundation': z=-2.8467
  if kind=='pool': z=-2.50 # access landing in the current model, not a surveyed basin level
  out.append(dict(id=rid,label=label,building='MAIN',level=lev,z=z,height={'B':2.15,'L1':2.40,'L2':2.17,'L3':2.04}[lev],polygon=[list(xy(v)) for v in p],center=list(xyz(c,z)),entry=list(xyz(e,z)),kind=kind,reference='HABS PA-5346 sheet '+{'B':'03','L1':'04','L2':'05','L3':'06'}[lev],evidence='C',notes='Room name and topology from HABS; manually traced boundaries, pixel tolerance 1–3 pixels; construction thickness/door heights approximated. Baths remain separate as drawn.',source_polygon=p,furniture=[]))
  if rid=='MAIN_L3_LINK':
   out[-1]['notes']='Only the true north upper walk/spiral landing is walkable atL3. The long southward projection in sheet06 is NOT an upper floor; the stepped canopy is separately tagged non-walkable roof. Access climbs south-low to north-high on the exterior curve.'
   out[-1]['route_level_range_m']=[2.8448,5.26415]
  if rid=='MAIN_B_WINE':out[-1]['notes']='Access follows the internal north stair leg. Sheet03 west boundary is rock/retaining wall, not an outside doorway.'
  if rid=='MAIN_B_PLUNGE':
   out[-1].update(notes='Inspection envelope includes wet basin, northeast stair recess and perimeter stonework. It is NOT a continuous dry walkable polygon. Main04 original shows the northern wall stop nearx628. Loggia stair gives pool-edge observation access; a dry ring route to East Terrace is source-unsupported. Model access level-2.50m and water-2.70m remainC.',walkable_polygon=False,access_scope='pool_observation_only; no dry through-route',water_surface_model_z=-2.70,observation_entry_world=list(xyz((691,370),-2.50)))
 return out

def export_data(path=None):
 dims=[]
 for rid,sheet,raw,meter,axis,a,b,unc in MEASUREMENTS:
  actual=abs(b-a)*(SX if axis=='x' else SY) if axis in ('x','y') else (b if axis=='z' else None)
  dims.append(dict(id=rid,source=f'HABS PA-5346 sheet {sheet}',raw=raw,meters=meter,axis=axis,pixels=[a,b] if axis in ('x','y') else None,method='read dimension label' if axis in ('z','nominal') else 'dimension label plus traced extension endpoints',label_evidence='A',geometry_evidence='C',uncertainty_m=unc,model_m=actual,delta_m=None if actual is None else actual-meter))
 result=dict(building='MAIN',transform={'source':'research/references/architecture/main-04-sheet.jpg','source_resolution':[1024,789],'origin_px':ORIGIN,'meters_per_pixel_x':SX,'meters_per_pixel_y':SY,'formula':'X=(px-327)*0.0524, Y=(540-py)*0.0531','z_datum':'Main level terrace 0 ft 0 in; L1 room finish +0.10 m inferred','north':'Plan north arrow points approximately northeast on page; +Y is drawing up, not geographic north; bearing not surveyed'},rooms=room_records(),dimensions=dims,levels=LEVELS,thresholds=[{'id':n,'room_id':rid,'source_rect':list(rr),'z':LEVELS[lev],'finish':mat,'probe_px':probe,'evidence':'C infill at actual door/wall thickness; plan outlines retained'} for n,rid,rr,lev,mat,probe in THRESHOLDS],adjacency=[{'from':a,'to':b,'type':t,'evidence':'C','status':'modeled; traversal not yet visually accepted'} for a,b,t in ADJACENCY],cameras=[{'id':'MAIN_LIVING_DETAIL','eye':[4.5,3.9,1.6],'target':[.1,10.4,1.0]},{'id':'MAIN_HATCH','eye':[5.7,3.0,1.5],'target':[9.4,3.0,-1.3]},{'id':'MAIN_STUDY','eye':[-2,12.8,6.7],'target':[-2.7,15.5,6.1]}],gaps=['Construction thicknesses, stair tread count and precise stairwell registration, exact glazing operability, several door heights, cellar level and furniture provenance are approximations, not surveyed.','Nominal room dimensions do not describe rectangular net floor polygons.','Plan north rotation is not numerically calibrated.','Guest relationship calibrated independently against site sheet.','Exterior upper connector is reached via L2 north terrace and exterior curved stair; no unsupported direct door cut through the sleeping-alcove north wall.'])
 result['dimension_interpretations']={'MAIN_LIVING_NOMINAL_WIDTH':'33 ft 8 in is an un-arrowed room-name annotation, not the maximum stepped floor bounding width. Candidate furniture/net-face spans remain unproven; no scaling applied.','MAIN_KITCHEN_NOMINAL_LENGTH':'15 ft 9 in label retained verbatim. South floor edge corrected from source y318 to y321 by wall/window trace; label endpoint semantics remain unresolved.','MAIN_SERVANT_NOMINAL_LENGTH':'11 ft 5 in label has no dimension arrows or axis assignment; former X-bounding comparison was not a proven correspondence. North rock-edge bay restored from source geometry.','MAIN_SERVANT_NOMINAL_WIDTH':'9 ft 4 in label has no dimension arrows. Former y230..269 floor omitted the northern bay; corrected floor extends to y214.7 without closing the descending stair strip.'}
 result['verified_opening_locations']=[{'id':'MAIN_L1_kitchen_door','source':'HABS PA-5346 sheet04 original TIFF','plan_px':[[324,270],[324,287]],'world_xyz':[xyz((324,270),.1),xyz((324,287),.1)],'height_m':2.05,'width_m':17*SY,'wall_thickness_m':.3668,'plan_evidence':'C endpoints traced from directly viewed original; about1px uncertainty','height_evidence':'C unmeasured construction approximation','superseded_plan_px':[[324,294],[324,315]],'old_opening_status':'closed with continuous masonry'}]
 for t in result['thresholds']:
  if t['id']=='guest_bath':t.update({'from':'MAIN_L2_HALL','to':'MAIN_L2_BATH_G','evidence':'Sheet05 bath east opening joins the north hall branch, not Guest Bedroom directly.'})
  if t['id']=='stair_wine':t.update({'from':'MAIN_B_STAIR','to':'MAIN_B_WINE','evidence':'Sheet03 internal north stair leg; no west opening into rock.'})
 result['exterior_connector_handoff']={'main_px':[431,98],'world_xyz':xyz((431,98),5.26415),'reference':'Sheet06 north upper walk, cross-check site point549,297','evidence':'C plan registration; elevation inherited fromL3 datum','replaces_invalid_canopy_point':xyz((451,120),5.26415),'next_guest_point':[2.62,23.58,5.83]}
 for edge in result['adjacency']:
  if edge['from']=='MAIN_L1_LOGGIA' and edge['to']=='MAIN_B_PLUNGE':
   edge.update(access_scope='pool observation via actual descending stairs; no dry cross-pool traversal',source_status='SOURCE_SUPPORTED_FOR_POOL_ACCESS_ONLY')
 result['retracted_adjacency']=[{'from':'MAIN_L1_LOGGIA','to':'MAIN_L1_TERRACE_E','previous_type':'exterior_steps','status':'SOURCE_UNSUPPORTED_AS_DRY_WALKEDGE','previous_case':'iteration06 ADJ017 remains a historical FAIL','reason':'The inferred path joined two stairs across pool/perimeter stonework. Main03/04 do not establish a continuous dry deck at the stair-foot level; current broad deck strips cannot serve as source evidence. East Terrace remains accessible through Living glazed doors.','source_crops':['qa/main-pool-iteration06-plan04.png','qa/main-pool-iteration06-plan04-grid.png','qa/main-pool-iteration06-plan03.png']}]
 result['pool_boundary_review']={'source':'Main04 original TIFF and main03 savedJPEG, actually viewed','north_wall_retained_px':[[533,376],[628,376]],'removed_false_continuation_px':[[628,376],[700,376]],'east_stone_band_px':[695,706],'south_stone_band_py':[419,428],'trace_uncertainty_m':.12,'dry_coping_route_status':'U height/use; not an accepted dry through-route','geometry_change':'Only north wall length shortened. Existing east/south walls, deck, basin, water and stairs unchanged.'}
 if path: Path(path).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 return result

def build(ctx):
 from fwlib import box,poly_prism,segment,stairs,window,beam,cylinder,tag
 mats=ctx.mats
 # Conserved kitchen replacement: 9-inch Cherokee-red rubber tiles, not stone.
 rubber=mats['red'].copy();rubber.name='MAIN_Kitchen_9inch_Cherokee_Rubber';mats['kitchen_rubber']=rubber
 ns,ls=rubber.node_tree.nodes,rubber.node_tree.links
 bs=next(n for n in ns if n.type=='BSDF_PRINCIPLED');bs.inputs['Roughness'].default_value=.64
 tc=ns.new('ShaderNodeTexCoord');brick=ns.new('ShaderNodeTexBrick')
 brick.offset=0.;brick.offset_frequency=1
 brick.inputs['Scale'].default_value=1/.2286;brick.inputs['Brick Width'].default_value=1.;brick.inputs['Row Height'].default_value=1.
 brick.inputs['Mortar Size'].default_value=.0065;brick.inputs['Mortar Smooth'].default_value=.003
 brick.inputs['Color1'].default_value=(.24,.044,.024,1);brick.inputs['Color2'].default_value=(.265,.052,.028,1);brick.inputs['Mortar'].default_value=(.065,.020,.013,1)
 ls.new(tc.outputs['Object'],brick.inputs['Vector']);ls.new(brick.outputs['Color'],bs.inputs['Base Color'])
 bump=ns.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.0015
 ls.new(brick.outputs['Fac'],bump.inputs['Height']);ls.new(bump.outputs[0],bs.inputs['Normal'])
 rubber['tile_size_m']=.2286;rubber['reference']='research/interiors.md kitchen conservation record; physical grid 9 inches'
 structure=ctx.collection('MAIN_Architecture')
 openings=ctx.collection('MAIN_Steel_Windows')
 masonry=ctx.collection('MAIN_Stone_Courses')
 details=ctx.collection('MAIN_Fixed_Details')
 records=room_records()
 def mark(o,rid=None,role='architecture'):
  tag(o,room_id=rid,reference='HABS PA-5346 plan trace',evidence='C',role=role)
  items=o if isinstance(o,list) else [o]
  for ob in items: ob['component_type']=role
  return o
 def prism(name,p,z0,z1,mat='ochre',coll=None,rid=None):
  return mark(poly_prism(name,[xy(a) for a in p],z0,z1,mats[mat],coll or structure),rid)
 def wall(name,a,b,z0,z1,t=.24,mat='stone',rid=None):
  return mark(segment(name,xy(a),xy(b),z0,z1,t,mats[mat],structure),rid,'wall')
 def win(name,a,b,z0,z1,n=4,door=False,rid=None):
  out=window(name,xy(a),xy(b),z0,z1,ctx,openings,divisions=n,open_panel=door)
  if door:
   av,bv=xy(a),xy(b);dx,dy=bv[0]-av[0],bv[1]-av[1];ln=math.hypot(dx,dy);k=n//2
   hx,hy=av[0]+dx*k/n,av[1]+dy*k/n
   # Narrow Cherokee-red leaf swung 78 degrees clear of its measured opening.
   theta=math.atan2(dy,dx)+math.radians(78); leaf=ln/n-.042
   ep=(hx+math.cos(theta)*leaf,hy+math.sin(theta)*leaf)
   out+=window(name+'_open_casement',(hx,hy),ep,z0+.015,z1-.015,ctx,openings,divisions=1,open_panel=False)
   for hz in (z0+.20,z1-.20): out.append(cylinder(name+'_hinge',(hx,hy,hz),.022,.105,mats['red'],openings,12))
   pp=(hx+math.cos(theta)*leaf*.82,hy+math.sin(theta)*leaf*.82)
   out.append(beam(name+'_latch',(pp[0],pp[1],z0+1.03),(pp[0],pp[1],z0+1.16),.012,mats['metal'],openings))
  if door:
   nominal_clear=math.dist(xy(a),xy(b))/n-.038
   opening_use='operable_casement' if name in ('MAIN_L2_dressing_west','MAIN_L3_study_west','MAIN_L2_hall_north') else 'terrace_door'
   for ob in out: ob['opening_use']=opening_use;ob['clear_width_m']=nominal_clear
  if name.startswith(('MAIN_L1_living_','MAIN_L1_west_terrace_door','MAIN_L1_east_terrace_access','MAIN_L1_southeast_door')):
   # Close the real head band between steel frame and L1 ceiling / upper slab.
   wall(name+'_concrete_head',a,b,z1+.018,2.646,.20,'ochre',rid)
  return mark(out,rid,'window')
 def chain(name,p,z0,z1,t=.23,mat='stone',closed=False):
  pp=p+[p[0]] if closed else p
  for i,(a,b) in enumerate(zip(pp,pp[1:])): wall(f'{name}_{i}',a,b,z0,z1,t,mat)
 def floor(name,p,z,th=.25,mat='ochre',rid=None):
  ob=prism(name,p,z-th,z,mat,rid=rid)
  return ob
 def portal(name,a,b,z,h=2.0,top=2.40,t=.20):
  # Genuine open center; upper lintel only. Door leaf is swung clear along side.
  wall(name+'_lintel',a,b,z+h,z+top,t,'wood')
  aa,bb=xy(a),xy(b); length=math.dist(aa,bb)
  ang=math.atan2(bb[1]-aa[1],bb[0]-aa[0])+math.pi/2
  ob=box(name+'_open_door',(aa[0]+math.cos(ang)*length*.43,aa[1]+math.sin(ang)*length*.43,z+h/2),(length*.86,.045,h),mats['wood'],details,.007);ob.rotation_euler.z=ang;mark(ob,None,'open_door')
 def stone_courses(name,a,b,z0,z1,t=.45):
  # Layered sandstone courses form real relief on both wall faces.
  av,bv=xy(a),xy(b); dx=bv[0]-av[0];dy=bv[1]-av[1]; length=math.hypot(dx,dy)
  if length<.1:return
  ux,uy=dx/length,dy/length; nx,ny=-uy,ux; z=z0;row=0
  while z<z1-.04:
   height=min(.095+.065*((row*7)%5)/4,z1-z)
   pos=-.36*(row%2);j=0
   while pos<length:
    start=max(0,pos); end=min(length,pos+.58+.23*((row+j*3)%4)/3)
    if end>start+.04:
     for side in (-1,1):
      dep=.03+.025*((row*3+j)%4)/3; mid=(start+end)/2
      ob=box(f'{name}_course{row:02}_{j:02}_{side}',(av[0]+ux*mid+nx*side*(t/2+.008),av[1]+uy*mid+ny*side*(t/2+.008),z+height/2),(end-start-.012,dep,height-.013),mats['stone'],masonry,.009);ob.rotation_euler.z=math.atan2(dy,dx)
    pos=end+.015;j+=1
   z+=height+.016;row+=1
 # All occupied floor surfaces; terrace/roof construction separately below.
 for r in records:
  if r['kind'] in ('foundation','pool','stair','water_stair'): continue
  p=r['source_polygon']; z=r['z'];floor(r['id']+'_slab',p,z,.22,rid=r['id'])
  surface='cork' if r['level'] in ('L2','L3') and r['kind'] in ('bedroom','dressing','study','gallery','sleeping_alcove') else 'stone_floor'
  if r['kind']=='kitchen':surface='kitchen_rubber'
  if r['kind']=='bathroom':surface='cork'
  prism(r['id']+'_finish',p,z,z+.022,surface,rid=r['id'])
 # Basement: occupied chambers, open foundation bays, stairs and plunge pool.
 # Sheet03 access is the internal north stair leg, not a west door into rock.
 chain('MAIN_B_cellar',[(251,244),(251,310),(319,310),(319,307)],-2.15,-.12,.26,'stone')
 wall('MAIN_B_cellar_north_east',(284,244),(284,255),-2.15,-.12,.26,'stone')
 chain('MAIN_B_cellar_bath_south',[(284,275),(284,285),(319,285),(319,288)],-2.15,-.12,.26,'stone')
 wall('MAIN_B_cellar_bath_lintel',(284,255),(284,275),-.25,-.12,.26,'stone')
 chain('MAIN_B_boiler',[(333,286),(333,280),(383,280),(383,325),(333,325),(333,307)],-2.15,-.12,.26,'stone')
 portal('MAIN_B_wine_boiler_passage',(320,288),(320,306),-2.15,1.92,2.03)
 # Carve cellar/boiler connection by intentionally discontinuous partition.
 wall('MAIN_B_connection_south',(319,309),(334,309),-2.15,-.12,.22)
 floor('MAIN_B_connection_floor',rect(318,285,336,310),-2.15,.20,'stone_floor')
 chain('MAIN_B_bath',[(289,246),(321,246),(321,282),(300,282)],-2.15,-.12,.17,'ceiling')
 wall('MAIN_B_bath_west_top',(289,246),(289,255),-2.15,-.12,.17,'ceiling')
 wall('MAIN_B_bath_west_bottom',(289,275),(289,282),-2.15,-.12,.17,'ceiling')
 for i,(a,b) in enumerate([((311,349),(311,444)),((387,284),(387,449)),((458,284),(458,449)),((529,338),(529,449))]):
  wall(f'MAIN_B_foundation_pier_{i}',a,b,-3.18,-.20,.58,rid=f'MAIN_B_FOUNDATION_{min(i+1,3)}')
  stone_courses(f'MAIN_B_pier_{i}',a,b,-3.18,-.2,.58)
 floor('MAIN_B_lower_platform',rect(476,460,561,501),-2.8467,.20)
 for pn,pp in [('west',rect(534,375,543,432)),('east',rect(688,375,700,432)),('north',rect(543,375,688,387)),('south',rect(543,418,688,432))]:
  floor('MAIN_B_pool_deck_'+pn,pp,-2.50,.28,'stone',rid='MAIN_B_PLUNGE')
 for pn,pp in [('west',rect(540,384,543,421)),('east',rect(688,384,691,421)),('north',rect(543,384,688,387)),('south',rect(543,418,688,421))]:
  prism('MAIN_B_pool_side_'+pn,pp,-3.18,-2.5,'stone',rid='MAIN_B_PLUNGE')
 prism('MAIN_B_plunge_basin',rect(541,385,690,420),-3.18,-2.80,'dark')
 prism('MAIN_B_plunge_water',rect(543,387,688,418),-2.73,-2.70,'water',rid='MAIN_B_PLUNGE')
 # Main04 original/main03: north wall ends at the stair recess nearx628.
 # Preserve east/south walls; the former x628..700 continuation falsely sealed the pool recess.
 wall('MAIN_B_pool_wall_0',(533,376),(628,376),-2.5,-1.97,.28,'stone')
 wall('MAIN_B_pool_wall_1',(700,376),(700,431),-2.5,-1.97,.28,'stone')
 wall('MAIN_B_pool_wall_2',(700,431),(533,431),-2.5,-1.97,.28,'stone')
 # Main L1 core walls: stepped north spine follows the plan, fireplace void retained.
 chain('MAIN_L1_north_spine',[(282,225),(324,225),(324,255),(387.984732824,255),(387.984732824,273),(505,273)],.1,2.55,.45)
 chain('MAIN_L1_kitchen_west',[(249,231),(249,321),(265,321)],.1,2.55,.48)
 # Original sheet04 TIFF: door gap y270..287 in the approximately7px stone wall.
 # The former y294..315 opening was a mis-trace and is now continuous masonry.
 wall('MAIN_L1_kitchen_east_north',(324,257),(324,270),.1,2.55,.3668)
 wall('MAIN_L1_kitchen_east_south',(324,287),(324,324),.1,2.55,.3668)
 portal('MAIN_L1_kitchen_door',(324,270),(324,287),.1,2.05,2.45,t=.3668)
 chain('MAIN_L1_servant_wall',[(180,230),(180,269),(240,269),(240,230)],.1,2.45,.22,'ceiling')
 # Former lower rectangle omitted the clearly drawn north bay against natural rock.
 chain('MAIN_L1_servant_rock_edge',[(183.5,228),(193,226),(202,227),(205.5,214.7)],.1,2.45,.16,'stone')
 win('MAIN_L1_servant_south',(186,271),(235,271),.55,2.17,4,rid='MAIN_L1_SERVANT')
 # Sheet04 shows the stepped south window bay, while HABS photo56 shows glazing
 # to the floor and repeated horizontal steel bars, not a1m-high opaque sill.
 # Heights/bar elevations are photograph-based C; the3-segment plan is traced.
 for nm,a,b,divisions,bars in [('inner',(260,319.4),(272.5,319.4),1,(.55,2.04)),('return',(272.5,319.4),(272.5,331),1,(.55,2.04)),('front',(272.5,331),(307,331),2,(.43,.77,1.11,1.45,1.79,2.13))]:
  frames=win('MAIN_L1_kitchen_south_'+nm,a,b,.12,2.40,divisions,rid='MAIN_L1_KITCHEN')
  for ob in frames:
   ob['reference']='HABS PA-5346 sheet04 south-bay plan and photograph56; vertical subdivisions C'
   if '_transom_' in ob.name: ob.location.z=bars[0]
  for j,h in enumerate(bars[1:]):
   mark(wall('MAIN_L1_kitchen_south_'+nm+f'_horizontal_{j}',a,b,h-.013,h+.013,.048,'red','MAIN_L1_KITCHEN'),'MAIN_L1_KITCHEN','window')
  wall('MAIN_L1_kitchen_south_'+nm+'_head_band',a,b,2.419,2.52,.16,'ochre','MAIN_L1_KITCHEN')
 # Stone hearth is open toward the living room. Furnishings adds fire and projecting hearth rock.
 wall('MAIN_L1_hearth_back',(313,329),(313,378),.1,2.56,.70)
 wall('MAIN_L1_hearth_jamb_n',(313,330),(331,330),.1,2.56,.34)
 wall('MAIN_L1_hearth_jamb_s',(313,376),(331,376),.1,2.56,.34)
 wall('MAIN_L1_hearth_lintel',(327,334),(327,373),1.43,2.56,.53)
 stone_courses('MAIN_L1_hearth_relief',(313,329),(313,378),.1,2.56,.70)
 chain('MAIN_L1_entry_west',[(454,304),(454,332),(470,332)],.1,2.5,.36)
 chain('MAIN_L1_entry_east',[(508,334),(527,334),(527,409),(516,409)],.1,2.58,.51)
 wall('MAIN_L1_east_pier',(516,376),(516,408),.1,2.56,.70)
 stone_courses('MAIN_L1_east_relief',(527,338),(527,409),.1,2.56,.51)
 chain('MAIN_L1_coat',[(495,279),(529,279),(529,301),(510,301)],.1,2.5,.25)
 wall('MAIN_L1_entry_southshort',(491,333),(508,333),.1,2.5,.28)
 chain('MAIN_L1_loggia_north',[(542,302),(598,302),(598,308)],0,2.58,.40)
 floor('MAIN_L1_entry_threshold',rect(465,331,511,342),.10,.18,'stone_floor')
 # Three visible glass fronts, true terrace access, corner steel and low fixed stone seats.
 win('MAIN_L1_living_south',(332,536),(451,536),.15,2.40,9,rid='MAIN_L1_LIVING')
 win('MAIN_L1_living_west',(314,382),(314,449),.35,2.40,5,rid='MAIN_L1_LIVING')
 win('MAIN_L1_west_terrace_door_n',(326,460),(326,499),.12,2.4,2,True,'MAIN_L1_LIVING')
 win('MAIN_L1_west_terrace_door_s',(326,500),(326,534),.12,2.4,2,True,'MAIN_L1_LIVING')
 win('MAIN_L1_living_east',(458,449),(525,449),.28,2.40,5,rid='MAIN_L1_LIVING')
 win('MAIN_L1_east_terrace_access',(529,417),(529,448),.13,2.40,2,True,'MAIN_L1_LIVING')
 win('MAIN_L1_southeast_door',(456,502),(456,535),.10,2.4,2,True,'MAIN_L1_LIVING')
 for i,(a,b) in enumerate([((310,454),(324,454)),((450,454),(465,454)),((321,535),(332,535))]):wall(f'MAIN_L1_south_stone_pier_{i}',a,b,.1,2.49,.48)
 # Cantilever slab edge and parapets, not floating cosmetic ribbons.
 chain('MAIN_L1_west_parapet',[(236,450),(236,543),(322,543)],-.24,.43,.22,'ochre')
 # Main09 east elevation:0/9ft4in datums give visible bandZ−.49..+1.08.
 # Includes the downward structural band, not1.57m of railing above the floor.
 # JPEG graphical reading isC±.055m; plan footprint and terrace datum unchanged.
 chain('MAIN_L1_east_parapet',[(458,543),(600,543),(600,383)],-.49,1.08,.24,'ochre')
 chain('MAIN_L1_south_fascia',[(236,543),(600,543)],-.29,-.015,.18,'ochre')
 # Loggia stair and plunge-pool access retain their physical lower landing.
 floor('MAIN_loggia_stair_upper_landing',rect(534,345,576,377),.10,.22,'stone_floor')
 floor('MAIN_loggia_stair_lower_landing',rect(677,352,706,384),-2.50,.23,'stone_floor')
 mark(stairs('MAIN_loggia_pool_stair',xyz((690,362),-2.50),xyz((575,362),.10),1.04,2.60,mats['stone'],details),'MAIN_B_PLUNGE','stairs')
 wall('MAIN_loggia_stair_retaining',(569,346),(704,346),-.20,.60,.28,'stone')
 floor('MAIN_pool_eastterrace_top_landing',rect(532,366,553,380),0,.20,'stone_floor')
 mark(stairs('MAIN_pool_eastterrace_stair',xyz((540,423),-2.50),xyz((540,380),0),.93,2.50,mats['stone'],details),'MAIN_L1_TERRACE_E','stairs')
 # Water stair: open floor hatch, lowered stair treads and rolled steel handrails.
 start=xyz((527,480),-2.8467);end=xyz((459,480),.10)
 mark(stairs('MAIN_water_stair',start,end,1.53,2.9467,mats['stone'],details),'MAIN_L1_HATCH','stairs')
 for yy in (464,495):
  beam('MAIN_water_handrail',xyz((461,yy),.94),xyz((530,yy),-1.90),.024,mats['red'],details)
  for xx in (463,491,525):
   frac=(xx-459)/(528-459);bottom=.1-2.9467*frac
   beam('MAIN_water_post',xyz((xx,yy),bottom),xyz((xx,yy),bottom+.9),.018,mats['red'],details)
 # Rolled upright glass hatch frame shown open vertically, retaining open walking void.
 win('MAIN_hatch_open_leaf',(460,461),(528,461),.10,2.02,5,False,'MAIN_L1_HATCH')
 for j in range(17):
  a=math.pi/2-math.pi*j/16;b=math.pi/2-math.pi*(j+1)/16
  pa=(528+16*math.cos(a),480+18*math.sin(a));pb=(528+16*math.cos(b),480+18*math.sin(b))
  wall('MAIN_hatch_curved_rim',pa,pb,.05,.19,.07,'red')
 # Stair run follows the first-floor UP arrow; upper landing remains outside its open well.
 floor('MAIN_stair1_landing',rect(397,280,411,302),2.8448,.14,'stone_floor',rid='MAIN_L2_STAIR')
 mark(stairs('MAIN_stair1',xyz((473,292),.1),xyz((410,292),2.8448),1.0,2.7448,mats['stone_floor'],details),'MAIN_L1_STAIR','stairs')
 # Place the descending flight in the actual northern y200..213 strip. Its old
 # centered-on213 geometry incorrectly occupied the servant-room north bay.
 service_steps=stairs('MAIN_service_stair',xyz((207,206.5),-2.15),xyz((264,206.5),.1),.68,2.25,mats['stone'],details)
 mark(service_steps[:7],'MAIN_B_STAIR','stairs');mark(service_steps[7:],'MAIN_L1_SERVICE_STAIR','stairs')
 # L2 perimeter, stone core and partitions with deliberate open doors.
 chain('MAIN_L2_dressing_shell_north',[(246,253),(246,227),(270,227)],2.8448,5.06,.46)
 wall('MAIN_L2_dressing_shell_middle',(246,270),(246,282),2.8448,5.06,.46)
 wall('MAIN_L2_dressing_shell_south',(246,308),(246,322),2.8448,5.06,.46)
 wall('MAIN_L2_dressing_window_sill',(246,253),(246,270),2.8448,3.25,.46)
 wall('MAIN_L2_dressing_window_header',(246,253),(246,270),4.99,5.06,.46)
 wall('MAIN_L2_dressing_door_sill',(246,282),(246,308),2.8448,2.88,.46)
 wall('MAIN_L2_dressing_door_header',(246,282),(246,308),4.99,5.06,.46)
 wall('MAIN_L2_dressing_north',(282,228),(328,228),2.8448,5.06,.38)
 wall('MAIN_L2_dressing_east',(326,231),(326,268),2.8448,5.06,.35)
 wall('MAIN_L2_dressing_south',(252,322),(274,322),2.8448,5.06,.36)
 wall('MAIN_L2_master_hearth',(316,325),(316,381),2.8448,5.21,.62)
 stone_courses('MAIN_L2_core',(316,305),(316,381),2.8448,5.22,.62)
 chain('MAIN_L2_bath_n_shell',[(334,232),(394,232),(394,269),(353,269)],2.8448,5.05,.20,'ceiling')
 wall('MAIN_L2_bath_n_left',(331,233),(331,254),2.8448,5.05,.17,'ceiling')
 win('MAIN_L2_dressing_north_window',(256,227),(270,227),3.6,4.9,2)
 win('MAIN_L2_bath_n_window',(343,232),(381,232),4.25,4.96,4)
 win('MAIN_L2_dressing_west',(247,253),(247,270),3.25,4.99,2,True)
 win('MAIN_L2_dressing_terrace',(246,308),(246,282),2.88,4.99,2,True)
 # Master bedroom room shell and ensuite, guest ensuite and open hall.
 wall('MAIN_L2_master_north',(332,303),(367,303),2.8448,5.04,.22,'wood')
 wall('MAIN_L2_master_north_east',(390,303),(418,303),2.8448,5.04,.22,'wood')
 portal('MAIN_L2_master_entry',(367,303),(390,303),2.8448,1.98,2.19)
 wall('MAIN_L2_master_east_n',(419,306),(419,355),2.8448,5.05,.18,'ceiling')
 wall('MAIN_L2_master_east_s',(419,385),(419,410),2.8448,5.05,.18,'ceiling')
 for nm,top,btm in [('guest',303,342),('master',349,413)]:
  wall('MAIN_L2_bath_'+nm+'_north',(422,top),(465,top),2.8448,5.05,.16,'ceiling')
  wall('MAIN_L2_bath_'+nm+'_south',(422,btm),(465,btm),2.8448,5.05,.16,'ceiling')
  wall('MAIN_L2_bath_'+nm+'_lefttop',(422,top),(422,top+15),2.8448,5.05,.16,'ceiling')
  if nm=='master':
   wall('MAIN_L2_bath_master_right',(465,top),(465,btm),2.8448,5.05,.16,'ceiling')
   wall('MAIN_L2_bath_master_leftbottom',(422,389),(422,btm),2.8448,5.05,.16,'ceiling')
  else: wall('MAIN_L2_bath_guest_left',(422,top),(422,btm),2.8448,5.05,.16,'ceiling')
 wall('MAIN_L2_bath_guest_righttop',(466,303),(466,312),2.8448,5.05,.16,'ceiling')
 wall('MAIN_L2_bath_guest_rightbottom',(466,333),(466,342),2.8448,5.05,.16,'ceiling')
 wall('MAIN_L2_guest_north',(486,330),(539,330),2.8448,5.05,.21,'wood')
 wall('MAIN_L2_guest_west',(466,346),(466,412),2.8448,5.05,.22,'ceiling')
 win('MAIN_L2_master_south',(322,411),(416,411),2.90,5.03,6,True,'MAIN_L2_MASTER')
 win('MAIN_L2_master_west',(317,384),(317,409),2.90,5.03,2)
 win('MAIN_L2_guest_south',(470,413),(537,413),2.89,5.02,5,False,'MAIN_L2_GUEST')
 win('MAIN_L2_guest_east',(539,344),(539,412),2.89,5.02,5,True,'MAIN_L2_GUEST')
 win('MAIN_L2_hall_north',(480,250),(536,250),3.12,5.04,5,True)
 floor('MAIN_L2_north_door_threshold',rect(433,246,473,257),2.8448,.21,'stone_floor')
 win('MAIN_L2_north_terrace_door',(434,250),(470,250),2.88,5.03,2,True,'MAIN_L2_HALL')
 wall('MAIN_L2_hall_northeast',(539,249),(539,296),2.8448,5.06,.3)
 wall('MAIN_L2_hall_east',(539,296),(578,296),2.8448,5.06,.36)
 # L2 terraces provide the recognizable unequal cantilevers; rounded horizontal lips.
 chain('MAIN_L2_west_parapet',[(72,204),(72,302),(242,302)],2.58,3.59,.22,'ochre')
 chain('MAIN_L2_west_north',[(73,201),(181,201)],2.58,3.32,.22,'ochre')
 chain('MAIN_L2_south_parapet',[(318,415),(318,581),(463,581),(463,418)],2.58,3.59,.24,'ochre')
 chain('MAIN_L2_east_parapet',[(544,415),(704,415),(704,347),(549,347)],2.58,3.53,.24,'ochre')
 for nm,p in [('west',[(72,302),(242,302)]),('south',[(318,581),(464,581)]),('east',[(543,415),(704,415)])]:
  chain('MAIN_L2_'+nm+'_rounded_lip',p,3.54,3.63,.26,'ochre')
 # Open pergola to right of south terrace, with slots open to sky and water stair.
 for j in range(8):
  yy=421+j*21
  wall(f'MAIN_L2_pergola_{j}',(470,yy),(535,yy),2.62,2.845,.25,'ochre')
 wall('MAIN_L2_pergola_edge',(536,420),(536,581),2.61,2.845,.24,'ochre')
 # North outdoor stairs and landing, left open for the guest-house connector.
 floor('MAIN_L2_north_terrace',rect(431,121,473,254),2.8448,.25)
 chain('MAIN_L2_north_terrace_wall',[(430,250),(430,116),(465,116)],2.58,3.65,.26,'ochre')
 # Sheet05 shows the low entry on the SOUTH side of the curve. The old
 # north-low direction incorrectly required a platform through the stair void.
 # Sheet06's long below-plan/canopy projection is not an upper walkable floor.
 cx,cy=473,125
 for i in range(16):
  a=math.pi/2+i*(ARC_END_ANGLE-math.pi/2)/16;b=a+(ARC_END_ANGLE-math.pi/2)/16
  pts=[(cx+rr*math.cos(ang),cy+rr*math.sin(ang)) for rr,ang in [(17,a),(50,a),(50,b),(17,b)]]
  z=2.8448+(i+1)*(5.26415-2.8448)/16
  mark(prism(f'MAIN_north_spiral_{i:02}',pts,z-.22,z,'stone_floor',details),'MAIN_L3_LINK','stairs')
  canopy=[(cx+rr*math.cos(ang),cy+rr*math.sin(ang)) for rr,ang in [(14,a),(66,a),(66,b),(14,b)]]
  ob=prism(f'MAIN_stepped_canopy_roof_{i:02}',canopy,z+2.36,z+2.50,'ochre',details)
  mark(ob,None,'canopy');ob['walkable']=False;ob['reference']='HABS sheet06 stepped canopy footprint; height follows tread atC2.36m clearance'
 # The actual lower toe connects to the east side of the L2 north terrace.
 floor('MAIN_L2_arc_lower_landing',rect(468,142,474,176),2.8448,.22,'stone_floor',rid='MAIN_L2_TERRACE_N')
 prism('MAIN_L2_arc_lower_landing_finish',rect(468,142,474,176),2.8448,2.8668,'stone_floor',rid='MAIN_L2_TERRACE_N')
 # Third floor: unequal roof bands, small study, gallery and open sleeping alcove.
 floor('MAIN_L2_elongated_roof',[(269,379),(308,379),(308,321),(330,321),(330,306),(537,306),(537,344),(711,344),(711,359),(731,359),(731,427),(269,427)],5.26415,.23)
 chain('MAIN_L3_study_core',[(247,323),(247,227),(325,227),(325,268)],5.26415,7.60,.42)
 wall('MAIN_L3_study_east_south',(325,305),(325,331),5.26415,7.60,.48)
 wall('MAIN_L3_study_south',(255,326),(279,326),5.26415,7.60,.37)
 win('MAIN_L3_study_west',(246,259),(246,276),5.7,7.46,2,True,'MAIN_L3_STUDY')
 win('MAIN_L3_study_south',(279,328),(311,328),5.32,7.49,3,False,'MAIN_L3_STUDY')
 portal('MAIN_L3_study_gallery',(325,277),(325,303),5.26415,2.03,2.32)
 chain('MAIN_L3_bath',[(334,235),(391,235),(391,252),(363,252),(363,277)],5.26415,7.48,.18,'ceiling')
 wall('MAIN_L3_bath_west',(333,236),(333,276),5.26415,7.48,.2,'ceiling')
 wall('MAIN_L3_gallery_north',(366,255),(432,255),5.26415,7.48,.22,'wood')
 wall('MAIN_L3_alcove_north',(432,253),(472,253),5.26415,7.48,.24,'wood')
 wall('MAIN_L3_alcove_east',(472,255),(472,280),5.26415,7.48,.24,'wood')
 win('MAIN_L3_gallery_south',(334,306),(432,306),5.30,7.42,7,True,'MAIN_L3_GALLERY')
 win('MAIN_L3_alcove_south',(435,306),(468,306),5.29,7.46,3,False,'MAIN_L3_ALCOVE')
 win('MAIN_L3_alcove_east',(472,282),(472,304),5.28,7.43,2)
 chain('MAIN_L3_terrace_parapet',[(335,382),(529,382),(529,284),(491,284)],5.03,6.05,.23,'ochre')
 floor('MAIN_L3_study_roof',rect(241,224,331,335),7.61365,.20)
 floor('MAIN_L3_gallery_roof',[(331,230),(395,230),(395,250),(476,250),(476,278),(508,278),(508,287),(332,287)],7.502525,.18)
 chain('MAIN_L3_roof_fascia',[(241,335),(331,335),(331,308),(476,308)],7.44,7.64,.21,'ochre')
 # Central fireplace/chimney piers retain independent stone mass and offset cap.
 wall('MAIN_stone_tower_west',(316,326),(316,382),5.25,9.46,.73)
 stone_courses('MAIN_tower_course',(316,326),(316,382),5.25,9.46,.73)
 wall('MAIN_stone_tower_north',(315,326),(330,326),5.25,9.46,.74)
 prism('MAIN_chimney_cap',rect(306,320,335,384),9.44,9.56,'stone')
 for xx in (315,326):prism('MAIN_chimney_flue',rect(xx-2,333,xx+2,347),9.57,9.60,'dark')
 # Stair to third gallery follows the narrow internal stair run.
 floor('MAIN_stair2_landing',rect(354,270,368,293),5.26415,.16,'wood',rid='MAIN_L3_STAIR')
 mark(stairs('MAIN_stair2',xyz((432,279.7),2.8448),xyz((367,279.7),5.26415),.82,2.41935,mats['wood'],details),'MAIN_L3_STAIR','stairs')
 # Exposed ceilings on actual enclosed room plans; no ceilings on terraces/gallery link.
 for r in records:
  if r['kind'] in ('terrace','loggia','foundation','pool','stair','water_stair') or r['level']=='B':continue
  zz=r['z']+r['height']
  if r['level']=='L2': zz=5.00
  if r['level']=='L3': zz=7.30415
  if r['id']=='MAIN_L3_STUDY': zz=7.38415
  cp=r['source_polygon']
  if r['id']=='MAIN_L1_LIVING':
   # The T-shaped outline in sheet04 is a dining table, not a floor or ceiling void.
   # Follow the stepped masonry perimeter and keep only the actual stair opening.
   cp=[(327,259),(383.984732824,259),(383.984732824,277),(405,277),(405,306),(448,306)]+cp[4:]
  if r['id']=='MAIN_L2_HALL':
   cp=[(435,253),(536,253),(536,301),(480,301),(480,282),(435,282)]
   prism(r['id']+'_ceiling_west',rect(331,291,410,301),zz,zz+.018,'ceiling',rid=r['id'])
  prism(r['id']+'_ceiling',cp,zz,zz+.018,'ceiling',rid=r['id'])
 # Minimal built-in architecture only: chimney shelving, entry stone sill and handrail.
 for r in records:
  if r['kind'] in ('bedroom','dressing','study','gallery','sleeping_alcove'):
   # Retain floor texture within actual polygon; movable furnishings supplied independently.
   pass
 # Fill actual doorway wall-thickness pockets rather than leaving holes between room polygons.
 for tn,rid,rr,lev,mat,probe in THRESHOLDS:
  zz=LEVELS[lev];ob=floor('MAIN_floor_threshold_'+tn,rect(*rr),zz,.18,mat,rid=rid);ob['component_type']='floor';ob['threshold_id']=tn
  ob=prism('MAIN_floor_threshold_'+tn+'_finish',rect(*rr),zz,zz+.022,mat,rid=rid);ob['component_type']='floor';ob['threshold_id']=tn
 floor('MAIN_B_STAIR_base_floor',ROOM_SPECS[3][3],-2.15,.18,'stone_floor',rid='MAIN_B_STAIR')
 prism('MAIN_L2_guest_corridor_ceiling',[(468,301),(536,301),(536,328),(484,328),(484,344),(468,344)],5.0,5.018,'ceiling',rid='MAIN_L2_HALL')
 # Cork finishes are documented for main-house bathroom floors/walls; exact basement attribution remains C.
 for ob in structure.objects:
  if ob.type=='MESH' and 'bath' in ob.name.lower() and ob.get('component_type')=='wall':
   ob.data.materials.clear();ob.data.materials.append(mats['cork'])
 # Sheet elevations show softened concrete band edges; restrict broad bevels to these bands.
 for ob in structure.objects:
  if ob.type=='MESH' and any(k in ob.name for k in ('parapet','rounded_lip','_roof','roof_fascia')):
   mod=next((m for m in ob.modifiers if m.type=='BEVEL'),None) or ob.modifiers.new('Concrete edge radius','BEVEL')
   mod.width=.055;mod.segments=4;mod.limit_method='ANGLE'
 export_data(ctx.root/'data'/'main_house.json')
 return records

if __name__=='__main__':
 export_data(Path(__file__).resolve().parents[1]/'data'/'main_house.json')
