"""Only translate the source-confirmed screen; preserve the tube-fix candidate."""
import bpy,json,sys,hashlib
from pathlib import Path
from types import SimpleNamespace
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import furnishings,tour
scene=bpy.context.scene;rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string());byid={r['id']:r for r in rooms}
room=byid['GUEST_L1_LOUNGE']
screen=next(o for o in scene.objects if o.type=='EMPTY' and o.get('room_id')==room['id'] and o.get('asset_type')=='walnut_vertical_screen')
chair=next(o for o in scene.objects if o.type=='EMPTY' and o.get('room_id')==room['id'] and o.get('asset_type')=='walnut_armchair')
adjust_chair='--chair-clearance' in sys.argv
version=sys.argv[sys.argv.index('--variant')+1] if '--variant' in sys.argv else ('07c' if adjust_chair else '07b')
assert version in ('07b','07c','07d','07e')
def state(o):return (o.data.as_pointer() if o.data else None,tuple(v for row in o.matrix_world for v in row))
screen_members={screen.name,*[o.name for o in screen.children]}
moving=set(screen_members)
if adjust_chair:moving.update({chair.name,*[o.name for o in chair.children]})
others={o.name:state(o) for o in scene.objects if o.name not in moving}
probe=tour.Probe(scene,((2,23),(34,43),(8,12)))
route=json.loads((ROOT/'qa/tour-path-route-iteration06-final.json').read_text(encoding='utf-8'))
shots=[s for s in route['main_segments']+route['supplemental_segments'] if room['id'] in s['room_ids']]
old_path=[probe.path(s['points'],s['mode'].startswith('NORMAL')) for s in shots]
old_location=list(screen.location)
old_chair=list(chair.location)
ctx=SimpleNamespace(root=ROOT,config={})
screen.location=furnishings.guest_lounge_screen_center(ctx,room['z'])
screen['source_screen_line_px']=json.dumps([[440,394],[440,430]])
screen['placement_evidence']='C: source-confirmed screen location, manually read approximately ±2px and active registration'
screen['placement_revision']='07 translated whole screen/cabinet to source southeast entry location; dimensions unchanged'
if adjust_chair:
    chair.location.x=screen.location.x-.98
    if version=='07d':chair.location.y=screen.location.y+1.06
    if version=='07e':chair.location.y=screen.location.y+.91
    chair['placement_evidence']='C: west/north translation to clear fixed source screen/cabinet and original lounge route; orientation and form unchanged'
bpy.context.view_layer.update();del probe
probe=tour.Probe(scene,((2,23),(34,43),(8,12)))
new_path=[probe.path(s['points'],s['mode'].startswith('NORMAL')) for s in shots]
cameras={n:probe.point(bpy.data.objects[n].matrix_world.translation,True) for n in ('CAM_GUEST_L1_LOUNGE_A','CAM_GUEST_L1_LOUNGE_B')}
selected=[byid[rid] for rid in ('GUEST_L1_LOUNGE','GUEST_L1_GALLERY','GUEST_L1_TERRACE')]
candidates={r['id']:tour.room_candidates(r,probe,True) for r in selected}
doors=[tour.hinted_connection(room,byid[rid],probe,candidates,tour.threshold_hints()) for rid in ('GUEST_L1_GALLERY','GUEST_L1_TERRACE')]
def box_world(o):
    pp=[o.matrix_world@Vector(p) for p in o.bound_box]
    return [[min(p[k] for p in pp),max(p[k] for p in pp)] for k in range(3)]
cab=next(o for o in screen.children if 'screen_low_drawercase' in o.name)
cab_bounds=box_world(cab);overlaps=[]
for o in scene.objects:
    if o.get('room_id')!=room['id'] or o.name in screen_members or o.type!='MESH' or not o.name.startswith('FW_FURN_'):continue
    bb=box_world(o);depth=[min(cab_bounds[k][1],bb[k][1])-max(cab_bounds[k][0],bb[k][0]) for k in range(3)]
    if min(depth)>.003:overlaps.append({'object':o.name,'axis_overlap_m':depth,'object_bounds':bb})
chair_members={chair.name,*[o.name for o in chair.children]}
chair_overlaps=[]
for own in chair.children:
    if own.type!='MESH':continue
    own_bounds=box_world(own)
    for o in scene.objects:
        if o.get('room_id')!=room['id'] or o.name in chair_members or o.type!='MESH' or not o.name.startswith('FW_FURN_'):continue
        bb=box_world(o);depth=[min(own_bounds[k][1],bb[k][1])-max(own_bounds[k][0],bb[k][0]) for k in range(3)]
        if min(depth)>.003:chair_overlaps.append({'chair_part':own.name,'object':o.name,'axis_overlap_m':depth,'object_bounds':bb})
same=others=={o.name:state(o) for o in scene.objects if o.name not in moving}
gap_path=[[screen.location.x-.46,chair.location.y-.65,room['z']+1.6],
          [screen.location.x-.46,chair.location.y+.65,room['z']+1.6]]
gap_failure=probe.path(gap_path,True) if adjust_chair else None
result={'source_scene':bpy.data.filepath,'source_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
    'source_reference':'HABS PA-5346-A-11 photograph and guest01 x440/y394..430 slat line; actual source images inspected',
    'old_location':old_location,'new_location':list(screen.location),'rotation_unchanged':[0,0,0],
    'chair_adjusted':adjust_chair,'old_chair_location':old_chair,'new_chair_location':list(chair.location),
    'chair_cabinet_body_gap_path':gap_path if adjust_chair else None,'chair_cabinet_body_gap_failure':gap_failure,
    'cabinet_bounds':cab_bounds,'all_other_objects_unchanged':same,'cabinet_furniture_overlaps':overlaps,'chair_furniture_overlaps':chair_overlaps,
    'old_film_path_checks':old_path,'new_film_path_checks':new_path,'unchanged_camera_body_checks':cameras,
    'door_connections':doors,'status':'PASS_TRANSLATION_GEOMETRY_NOT_VISUAL_ACCEPTANCE' if same and not overlaps and not chair_overlaps and gap_failure is None and all(x is None for x in new_path) and not any(cameras.values()) and all(d['status']=='PASS_MESH_AND_GROUND' for d in doors) else 'REQUIRES_REVIEW',
    'limits':'No scene architecture, fixture light, camera transform, screen dimensions or tube geometry changed. Film-path failures are retained for the next tour rebuild.'}
candidate=ROOT/f'scene/Fallingwater_furniture_candidate{version}.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(candidate),compress=True)
result['candidate']=str(candidate);result['candidate_sha256']=hashlib.sha256(candidate.read_bytes()).hexdigest()
(ROOT/f'qa/guest-screen-placement{version if adjust_chair else "07"}-check.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('SCREEN_PLACEMENT',json.dumps(result),flush=True)
