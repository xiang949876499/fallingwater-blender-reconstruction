"""Phase10 C circulation design: numerical only, no production or Blender."""
from pathlib import Path
import json,hashlib,math
R=Path(__file__).resolve().parents[1];Q=R/'qa'
SX,SY=.05256,.05272
B1,SOUTH,L1,L2=-2.36,-1.18,0.,2.352675
HEAD,RADIUS=1.95,.18
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
owned_inputs=[R/'scripts/guest_house.py',R/'data/guest_house.json',R/'scripts/tour.py']
before={str(p.relative_to(R)):sha(p) for p in owned_inputs}
data=json.loads((R/'data/guest_house.json').read_text(encoding='utf-8'))
levels=json.loads((Q/'guest-level-context09-review.json').read_text(encoding='utf-8'))

def enumerate_pair(lengths,low,mid,high,common_riser=False):
 out=[]
 for nl in range(2,25):
  for nr in range(2,25):
   rl=(mid-low)/nl;rr=(high-mid)/nr
   gl=lengths[0]/(nl-1);gr=lengths[1]/(nr-1)
   if all(.13<=v<=.19 for v in (rl,rr)) and all(.25<=v<=.40 for v in (gl,gr)):
    if common_riser and abs(rl-rr)>1e-9:continue
    out.append(dict(left_n=nl,right_n=nr,left_riser=rl,right_riser=rr,left_going=gl,right_going=gr))
 return out

lower_lengths=[(404.5-368)*SY,(400.8-350)*SY]
lower_all=enumerate_pair(lower_lengths,B1,SOUTH,L1)
lower_uniform=enumerate_pair(lower_lengths,B1,SOUTH,L1,True)
assert [(q['left_n'],q['right_n']) for q in lower_uniform]==[(8,8)]
upper_mid=8*(L2/13)
upper=enumerate_pair([(405.5-369)*SY,(405.5-382)*SY],L1,upper_mid,L2,True)
assert [(q['left_n'],q['right_n']) for q in upper]==[(8,5)]
front=[]
for nw in range(2,8):
 for ne in range(2,8):
  r=(L1-SOUTH)/(nw+ne);gw=(336-324)*SX/(nw-1);ge=(448-428)*SX/(ne-1)
  if .13<=r<=.19 and .25<=gw<=.40 and .25<=ge<=.40:
   front.append(dict(west_n=nw,east_n=ne,riser=r,west_going=gw,east_going=ge,middle_z=SOUTH+nw*r))
selected_front=next(p for p in front if p['west_n']==3 and p['east_n']==4)
MID_FRONT=selected_front['middle_z']

def flight(fid,axis,start,end,other,width,z0,z1,n,sheet,source_evidence):
 return dict(id=fid,axis=axis,start=start,end=end,other=other,width_m=width,
             source_sheet=sheet,source_start_px=[start,other] if axis=='X' else [other,start],
             source_end_px=[end,other] if axis=='X' else [other,end],z0=z0,z1=z1,
             risers=n,goings=n-1,riser_m=(z1-z0)/n,
             going_m=abs(end-start)*(SX if axis=='X' else SY)/(n-1),
             evidence='C selected level/hidden extent/count',source_evidence=source_evidence)
flights=[
 flight('F1_B1_LEFT_SOUTH','Y',368,404.5,294.45,.700,B1,SOUTH,8,'guest01 main plan plus basement inset',
        'Main-plan left projection includes UP/DOWN and break. Eight risers cannot fit the four visible basement edges; hidden/overlap extent is an explicit C hypothesis. Center fits the existing measured basement wall gap, with no door relocation.'),
 flight('F2_LOWER_RIGHT_NORTH','Y',400.8,350,316.35,15.9*SX,SOUTH,L1,8,'guest01 main plan',
        'Right UP arrow north and long run outline; identifying north end as L1=0 remains C.'),
 flight('F3_UPPER_LEFT_SOUTH','Y',369,405.5,296.75,15.5*SX,L1,upper_mid,8,'guest02',
        'UP south;369 northern frame/cap is not confirmed to be a vacant strip at this elevation. Hypothesis retains high cap and lower passage.'),
 flight('F4_UPPER_RIGHT_NORTH','Y',405.5,382,316.35,15.9*SX,upper_mid,L2,5,'guest02',
        'UP north; upper end meets paved upper hall, B correspondence. Four visible bands do not establish total count without this C interpretation.'),
 flight('W1_FRONT_WEST','X',324,336,461,22*SY,SOUTH,MID_FRONT,3,'guest01 front walkway',
        'Three drawn crossway edges/two bands; DOWN west. Candidate rises east and keeps the original useful lane450..472.'),
 flight('W2_FRONT_EAST','X',428,448,461,22*SY,MID_FRONT,L1,4,'guest01 front walkway',
        'Four drawn crossway edges/three bands; DOWN west. Candidate rises east to unchanged east terrace0.'),
]

def rect(name,x0,x1,y0,y1,z,th=.21,classification='C inferred finished plane'):
 return dict(name=name,rect_px=[x0,x1,y0,y1],z=z,thickness=th,classification=classification)
def treads(f):
 out=[]
 for j in range(f['risers']-1):
  a=f['start']+(f['end']-f['start'])*j/(f['risers']-1)
  b=f['start']+(f['end']-f['start'])*(j+1)/(f['risers']-1)
  c=f['other'];half=f['width_m']/(2*(SY if f['axis']=='X' else SX))
  box=(min(a,b),max(a,b),c-half,c+half) if f['axis']=='X' else (c-half,c+half,min(a,b),max(a,b))
  out.append(rect(f"{f['id']}_{j+1:02d}",*box,f['z0']+(j+1)*f['riser_m'],.13))
 return out
flight_rects={f['id']:treads(f) for f in flights}
surfaces=[
 rect('P_B1_NORTH',284,304,358,368,B1,.18,'C existing provisional B1 datum and unchanged northern door/threshold approach; trimmed only at first riser368'),
 rect('P_SOUTH_LOW',284,326,405.5,472,SOUTH,.21,'C finish interpretation of source south terminal grade in[-1.20,-1.11]'),
 rect('P_LOWER_LEFT_STUB',287.79,301.11,404.5,405.5,SOUTH),
 rect('P_LOWER_RIGHT_STUB',308.4,324.3,400.8,405.5,SOUTH),
 rect('P_L1_NORTH',284,326,319,350,L1,.21,'Existing north foyer/doors stay at current datum; right stair end boundary meets350'),
 rect('P_L1_LEFT_APPROACH',284,304.5,350,369,L1,.21,'C source paved north-left approach, keeps existing chauffeur door access and stays above B1 entry'),
 rect('P_UPPER_RETURN',289,324.3,405.5,419.6,upper_mid,.21,'A footprint; C intermediate finished level; replaces wrong full L2 south plate'),
 rect('P_L2_NORTH',286,326,267,369,L2,.21,'A printed storey rise; C correct opening boundary'),
 rect('P_L2_RIGHT_APPROACH',308.4,324.3,369,382,L2,.21,'B source right top meets upper hall, no additional step symbol'),
 rect('P_FRONT_MIDDLE',336,428,444,472,MID_FRONT,.21,'C elevation between two observed stair groups; below Lounge glazing, not Lounge FFL'),
 rect('P_FRONT_EAST',448,697,439.31,472,L1,.21,'Existing east terrace/guest-room approach remains0'),
]
sd={s['name']:s for s in surfaces}
def clearance(walk,ceilings):
 rows=[]
 for w in walk:
  x0,x1,y0,y1=w['rect_px'];cx=(x0+x1)/2
  for c in ceilings:
   a,b,d,e=c['rect_px'];dx=max(a-cx,0,cx-b)*SX
   if dx>RADIUS:continue
   reach=math.sqrt(RADIUS**2-dx**2)/SY
   lo,hi=max(y0,d-reach),min(y1,e+reach)
   if hi<=lo:continue
   h=c['z']-c['thickness']-w['z']
   rows.append(dict(walk=w['name'],overhead=c['name'],headroom_m=h,margin_m=h-HEAD,witness_px=[cx,(lo+hi)/2]))
 rows.sort(key=lambda r:r['headroom_m'])
 return dict(minimum=rows[0] if rows else None,pairs=rows,failures=[r for r in rows if r['headroom_m']<HEAD])
works_upper=flight_rects['F3_UPPER_LEFT_SOUTH']+flight_rects['F4_UPPER_RIGHT_NORTH']+[sd['P_UPPER_RETURN']]
ceil_l2=[sd['P_L2_NORTH'],sd['P_L2_RIGHT_APPROACH']]
headroom={
 'B1_door_and_left_flight':clearance([sd['P_B1_NORTH']]+flight_rects['F1_B1_LEFT_SOUTH'],works_upper+ceil_l2+[sd['P_L1_NORTH'],sd['P_L1_LEFT_APPROACH']]),
 'lower_right_and_low_south':clearance(flight_rects['F2_LOWER_RIGHT_NORTH']+[sd[n] for n in ['P_SOUTH_LOW','P_LOWER_LEFT_STUB','P_LOWER_RIGHT_STUB']],works_upper+ceil_l2),
 'upper_left_and_north_approach':clearance(flight_rects['F3_UPPER_LEFT_SOUTH']+[sd['P_L1_LEFT_APPROACH']],ceil_l2),
}
assert all(not h['failures'] for h in headroom.values())

# The parent specifically requires the actual current-to-new identity changes,
# not leaving old plates hidden in the hypothetical opening.
old_face_actions=[
 dict(object='GUEST_L1_HALL_SOUTH',old_z=0,action='replace flat plate by P_SOUTH_LOW and separate lower stubs; remove all0m faces within the stair/return footprint',reason='Source south line and two walkway DOWN groups refute a universal south0 plane'),
 dict(object='GUEST_L2_STAIR_TOP_LANDING',old_z=L2,action='remove full404..422 high plate; install only P_UPPER_RETURN at1.4478 on405.5..419.6',reason='Would otherwise leave only.694875m over new upper return'),
 dict(object='GUEST_L2_STAIR_PASSAGE',old_z=L2,action='retain only north portion through369; open remaining left shaft369..405.5',reason='Wrong full west strip covers new upper left flight'),
 dict(object='GUEST_L2_CORRIDOR_FLOOR',old_z=L2,action='extend exact right upper landing351..382, with separate left opening at369; share edges and avoid duplicated finish',reason='Source upper right run terminates at382'),
 dict(object='GUEST_L1_HALL_NORTH',old_z=0,action='keep doors and north slab; right stair attachment at350 plus separate left paved approach to369',reason='Fixes endpoint interface without moving northern chauffeur/boiler doors'),
 dict(object='GUEST_L1_TERRACE slab/finish',old_z=0,action='split into western stairW1, middle lower plane, eastern stairW2 and retained eastern0 plane; preserve source southern/outer wall limits',reason='Two DOWN arrows west explicitly require steps'),
 dict(object='Guest bridge/canopy approach',old_z='C varying to8.4world',action='walk endpoint to7.22world; monotone rescale existing C walking heights from fixed main start; retain XY and canopy envelope, extend existing supports if necessary',reason='Must actually meet the lower service arrival; cannot keep a1.18m drop at endpoint'),
]

# Explicit connected candidate travel skeleton, not an executed mesh route.
nodes={
 'B1_DOOR':[285,365.835,B1],
 'B1_NORTH_LANDING':[294.45,365.835,B1],
 'SOUTH_RETURN':[305,412.3,SOUTH],
 'NORTH_RIGHT_L1':[316.35,348,L1],
 'NORTH_CROSSOVER_L1':[306,342.5,L1],
 'NORTH_LEFT_L1':[296.75,365,L1],
 'UPPER_RETURN':[305,412.3,upper_mid],
 'UPPER_HALL':[316.35,378,L2],
 'UPPER_CROSSOVER':[306,364,L2],
 'SOUTH_ARRIVAL':[305,423,SOUTH],
 'FRONT_WEST':[320,461,SOUTH],
 'FRONT_MIDDLE':[382,461,MID_FRONT],
 'FRONT_EAST':[460,461,L1],
 'GUEST_EAST_DOOR':[635,389,L1],
}
paths=[
 dict(id='B1_TO_NORTH',sequence=['B1_DOOR','B1_NORTH_LANDING','F1_B1_LEFT_SOUTH','SOUTH_RETURN','F2_LOWER_RIGHT_NORTH','NORTH_RIGHT_L1'],kind='walking C candidate'),
 dict(id='NORTH_TO_UPPER',sequence=['NORTH_RIGHT_L1','NORTH_CROSSOVER_L1','NORTH_LEFT_L1','F3_UPPER_LEFT_SOUTH','UPPER_RETURN','F4_UPPER_RIGHT_NORTH','UPPER_HALL','UPPER_CROSSOVER'],kind='walking C candidate',note='Cross around the actual northern divider caps; do not draw a straight segment through the central stone divider.'),
 dict(id='MAIN_TO_EAST_GUEST',sequence=['SOUTH_ARRIVAL','FRONT_WEST','W1_FRONT_WEST','FRONT_MIDDLE','W2_FRONT_EAST','FRONT_EAST','GUEST_EAST_DOOR'],kind='walking C candidate'),
 dict(id='LOUNGE_ACCESS',sequence=['GUEST_EAST_DOOR','GUEST_ROOM','GALLERY','LOUNGE'],kind='existing internally connected rooms; actual future mesh path required',note='Uses verified guest east door and existing room connections, rather than inventing a stair at the questionable west Lounge glazing.'),
]
old_points=data['connector']['points'];z0=old_points[0][2];zold=old_points[-1][2];znew=8.4+SOUTH
factor=(znew-z0)/(zold-z0)
connector=[list(p[:2])+[z0+(p[2]-z0)*factor] for p in old_points]
assert all(b[2]>=a[2] for a,b in zip(connector,connector[1:]))

# Projection station and old assumptions which are expressly NOT accepted.
observed_step_deltas=[(b-a)/levels['calibrations'][0]['raw_px_per_m'] for a,b in zip(levels['right_visible_stair_edges']['raw_y_centers'],levels['right_visible_stair_edges']['raw_y_centers'][1:])]
source_residuals=dict(selected_south_z=SOUTH,source_grade_envelope=levels['south_grade_candidate']['read_envelope_m'],source_line_center_z=levels['south_grade_candidate']['right_center_z_m'],selected_minus_line_center_m=SOUTH-levels['south_grade_candidate']['right_center_z_m'],lower_riser_m=.1475,observed_visible_vertical_spacing_m=observed_step_deltas,observed_spacing_minus_selected_riser_m=[d-.1475 for d in observed_step_deltas],interpretation='Source edge intervals near.154-.159m are not directly reproduced by.1475. First visible edge lies above0; these projected line identities remain C/U. Keep this residual, do not claim8+8 source-confirmed.',basement_lowest_line_z=levels['basement_lowest_line']['relative_z_m'],provisional_B1_minus_lowest_line_m=B1-levels['basement_lowest_line']['relative_z_m'],basement_note='Lowest heavy line is not a proven FFL. Retain existing B1 C datum by parent constraint, not by pretending the source supports-2.36.')
result=dict(schema='fallingwater.guest_circulation10.numeric_design.v1',status='SELECTED_C_DESIGN_NUMERICALLY_FEASIBLE_WITH_EXPLICIT_FACADE_AND_CAP_GATES',scope='20-minute bounded design; no Blender scene, render or production editing',source_review='qa/guest-level-context09-review.json',source_review_sha256=sha(Q/'guest-level-context09-review.json'),thresholds=dict(riser_m=[.13,.19],going_m=[.25,.40],headroom_m=HEAD,body_radius_m=RADIUS,legal_claim=False),datums=dict(B1=B1,B1_evidence='C unchanged',south=SOUTH,south_evidence='C selected finish within source grade interval, not proven plane identity',L1=L1,L2=L2,printed_main_second_preserved=True),selection_reason='Lower8+8 uniquely shares a uniform riser at the selected midlevel within measured full-projection lengths. Front3+4 matches two/three visible bands, preserves east terrace0 and adds no extra unmarked group. Upper8+5 keeps prior C option and tight northern cap condition.',flights=flights,enumeration=dict(lower_all=lower_all,lower_same_riser=lower_uniform,upper=upper,front=front,selected_front=selected_front),surfaces=surfaces,headroom=headroom,minimum_headroom=min(h['minimum']['headroom_m'] for h in headroom.values()),north_cap_maximum_combined_slab_and_downward_finish_m=L2-(L2/13)-HEAD,old_face_actions=old_face_actions,nodes=nodes,paths=paths,connector_C=dict(original_world_points=old_points,proposed_world_points=connector,walk_height_rescale=factor,main_endpoint_fixed=True,guest_datum_not_shifted=True,roof_action='No automatic roof relocation. Existing canopy underside is above lowered walking profile; real posts/terrain interfaces require candidate checks.',mesh_clearance_status='NOT_RUN_NUMERICAL_ONLY'),source_residuals=source_residuals,west_lounge_opening=dict(existing_model='GUEST_L1_WEST_LOUNGE opening span.68..94; no leaf, modeled as door at0',source_location='guest01 western facade below masonry pier, approximatelyx329..335/y423..440',observed='Native crop shows continuous corner-glazing-like outline; this review does not establish a hinged/access door.',candidate_access_decision='Do not use as a walking edge in this candidate. Enter Lounge via the existing east guest-room/Gallery connections. Do not lower Lounge FFL or add an unmarked1.18m entrance stair.',source_gate='Confirm glazing-versus-door before production adjacency or opening changes. If a real door is confirmed, the candidate lacks its source-supported approach and must be revised.',physical_requirement='No unguarded door over1.18m drop may be accepted. Existing modeled hole cannot silently remain a certified door.'),body_width_screen=dict(B1_existing_minimum_measured_finish_clearance_m=.720369,selected_lower_tread_width_m=.7,required_diameter_m=.36,upper_left_width_m=15.5*SX,upper_right_width_m=15.9*SX,return_depth_m=14.1*SY,front_useful_lane_m=22*SY,turn_center_y=412.3,maximum_divider_south_tip_y_for_radius_clearance=412.3-RADIUS/SY,divider_note='Source rounded tip must be inside this limit; do not shorten actual masonry to fit.'),unresolved_but_bounded=['North cap/frame369..372.6 must allow the first upper tread below: nominal headroom1.9617 leaves11.7mm reserve.','B1 projected partial stair lines and south-elevation step intervals do not prove selected8+8; retain documented residual.','West Lounge glazed/opening identity is a required facade gate, not a hidden failed navigation edge.','Main connector lowering and terrain/support/roof interfaces require actual full candidate mesh regression.','No current production slabs may remain hidden across new stair voids; remove/split exact face identities listed.','Neither all southern stone planes nor all room FFLS are reassigned; northern chauffeur/boiler/room doors stay at present levels.'],verification=dict(method='Exact piecewise constant tread/landing rectangle-disk overlap; integer enumeration; no actual mesh tests',status='NUMERICAL_SCREEN_ONLY',production_hashes_unchanged={str(p.relative_to(R)):sha(p) for p in owned_inputs},source_numeric_design_script_sha256=sha(Path(__file__))))
assert before==result['verification']['production_hashes_unchanged']
assert levels['south_grade_candidate']['read_envelope_m'][0]<=SOUTH<=levels['south_grade_candidate']['read_envelope_m'][1]
retaining_inner_px=325+(2.1627-3.4)/SX
result['fixed_retaining_wall_context']=dict(existing_world_inner_x=2.1627,source_equivalent_inner_x=retaining_inner_px,current_C_top_relative_m=.8,retained_XY_and_printed_width=True,upper_left_center_x=296.75,upper_left_body_east_extent_px=296.75+RADIUS/SX,centerline_body_to_wall_margin_m=(retaining_inner_px-296.75)*SX-RADIUS,nominal_upper_left_clear_width_below_wall_top_m=(retaining_inner_px-289)*SX,note='Existing B1 retaining wall projects inside the nominal upper-left full-width tread outline below its C top. Walkable intersection still exceeds.36m; preserve the real wall and trim/merge tread construction at its face, not move the wall for a path. This is an actual-candidate mesh join gate, not a claim the full raster width remains clear.')
result['retained_negative_controls']=dict(B1_visible_edges_if_forced8_risers_going_m=(673.1-655.8)*SY/7,B1_entire_inset_enclosure_if_forced8_risers_going_m=(676-648)*SY/7,upper_visible_nominal_if8_risers_going_m=(405.5-372.6)*SY/7,note='All three nominal going values fail.25. Selected longer lower run comes from explicit full first-floor projection hypothesis; selected upper run includes the unresolved northern cap band. No hidden tolerance upgrades.',lower_return_under_old_L1_south_headroom_m=0-.22-SOUTH,upper_return_under_old_L2_south_headroom_m=L2-.21-upper_mid,L1_south_walk_under_new_upper_return_headroom_m=upper_mid-.21,old_west_strip_above_second_upper_left_tread_headroom_m=L2-.19-2*L2/13)
(Q/'guest-circulation10-design.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(dict(status=result['status'],lower=lower_uniform,front=selected_front,headroom_minima={k:v['minimum'] for k,v in headroom.items()},connector_endpoint=connector[-1],source_residuals=source_residuals),indent=2))
