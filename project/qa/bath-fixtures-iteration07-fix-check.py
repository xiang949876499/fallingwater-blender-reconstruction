"""Install only identified bath-tube fixes into an independent06-derived candidate."""
import bpy,json,sys,hashlib,runpy
from pathlib import Path
from types import SimpleNamespace
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import furnishings,fwlib,tour
scene=bpy.context.scene
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string());byid={r['id']:r for r in rooms}
def wanted(o):
    return o.type=='CURVE' and 'BATH' in o.get('room_id','') and o.get('asset_type') in ('washbasin','water_closet','towel_rail','bath_tub') and any(o.name.endswith('_'+s) for s in ('basin_spout','inlet','rail','spout','shower_riser'))
targets=[o for o in scene.objects if wanted(o)]
def signature(o):
    return {'name':o.name,'radius':o.data.bevel_depth,'matrix':[list(row) for row in o.matrix_world],
        'knots':[list(p.co) for s in o.data.splines for p in s.bezier_points]}
before={o.name:signature(o) for o in targets}
other_state={o.name:(o.as_pointer(),o.data.as_pointer() if o.data else None,tuple(v for row in o.matrix_world for v in row)) for o in scene.objects if not wanted(o)}
def localprobe():
    r=byid['MAIN_B_BATH'];xs=[p[0] for p in r['polygon']];ys=[p[1] for p in r['polygon']]
    return tour.Probe(scene,((min(xs)-.5,max(xs)+.5),(min(ys)-.5,max(ys)+.5),(r['z']-.3,r['z']+r['height']+.3)))
route=json.loads((ROOT/'qa/tour-path-route-iteration06-final.json').read_text(encoding='utf-8'))
segments=[s for s in route['main_segments']+route['supplemental_segments'] if 'MAIN_B_BATH' in s['room_ids']]
probe=localprobe();path_before=[probe.path(s['points'],s['mode'].startswith('NORMAL')) for s in segments];del probe
ctx=SimpleNamespace(root=ROOT,mats={m.name[3:]:m for m in bpy.data.materials if m.name.startswith('FW_')},collection=fwlib.collection)
for obj in targets:
    snapshot=before[obj.name];parent=obj.parent;kind=obj.get('asset_type');rid=obj['room_id'];ref=obj.get('reference');evidence=obj.get('evidence')
    label=obj.name[len(parent.name)+1:]
    owner=furnishings.Room(ctx,byid[rid]);owner.coll=obj.users_collection[0]
    asset=furnishings.Asset.__new__(furnishings.Asset)
    asset.owner=owner;asset.ctx=ctx;asset.root=parent;asset.kind=kind;asset.ref=ref;asset.evidence=evidence
    asset.objects=[];asset.name=parent.name
    bpy.data.objects.remove(obj,do_unlink=True)
    asset.tube(label,snapshot['knots'],snapshot['radius'],'metal')
bpy.context.view_layer.update()
checks=[]
for name,old in before.items():
    obj=bpy.data.objects[name];spline=obj.data.splines[0];knots=spline.bezier_points
    limits=[[min(p[k] for p in old['knots']),max(p[k] for p in old['knots'])] for k in range(3)]
    excess=max(max(0,limits[k][0]-p[k],p[k]-limits[k][1]) for knot in knots for p in (knot.co,knot.handle_left,knot.handle_right) for k in range(3))
    dots=[]
    for p in knots[1:-1]:
        left=p.co-p.handle_left;right=p.handle_right-p.co
        if min(left.length,right.length)>1.e-7:dots.append(left.normalized().dot(right.normalized()))
    endpoints=(Vector(old['knots'][0])-knots[0].co).length<1.e-6 and (Vector(old['knots'][-1])-knots[-1].co).length<1.e-6
    same_transform=old['matrix']==[list(row) for row in obj.matrix_world]
    checks.append({'object':name,'endpoints_unchanged':endpoints,'transform_unchanged':same_transform,
        'radius_unchanged':obj.data.bevel_depth==old['radius'],'handle_hull_excess_outside_authored_bbox_m':excess,
        'minimum_join_tangent_dot':min(dots) if dots else 1.,
        'pass':endpoints and same_transform and obj.data.bevel_depth==old['radius'] and excess<1.e-6 and all(d>.9999 for d in dots)})
other_after={o.name:(o.as_pointer(),o.data.as_pointer() if o.data else None,tuple(v for row in o.matrix_world for v in row)) for o in scene.objects if o.name not in before}
probe=localprobe();path_after=[probe.path(s['points'],s['mode'].startswith('NORMAL')) for s in segments]
camera_results={n:probe.point(bpy.data.objects[n].matrix_world.translation,True) for n in ('CAM_MAIN_B_BATH_A','CAM_MAIN_B_BATH_B')}
candidate=ROOT/'scene/Fallingwater_bath_fixtures_candidate07.blend'
result={'status':'PASS_BOUNDED_TUBE_FIX_NOT_VISUAL_ACCEPTANCE' if all(c['pass'] for c in checks) and other_state==other_after and all(a is None or b is not None for a,b in zip(path_after,path_before)) and not any(camera_results.values()) else 'FAIL',
    'source_scene':bpy.data.filepath,'source_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
    'changed_curve_count':len(checks),'checks':checks,'all_non_target_objects_datablocks_and_matrices_unchanged':other_state==other_after,
    'main_bath_path_before':path_before,'main_bath_path_after':path_after,'main_bath_camera_body_checks':camera_results,
    'scope':'Only bath fitting curves. No sanitaryware meshes, fixture positions, lights, camera transforms, hearth or architecture changed.',
    'visual_status':'NOT_RUN pending integrator same-camera render; no final appearance claim'}
bpy.ops.wm.save_as_mainfile(filepath=str(candidate),compress=True)
result['candidate_file']=str(candidate);result['candidate_sha256']=hashlib.sha256(candidate.read_bytes()).hexdigest()
sys.argv.extend(['--output-json',str(ROOT/'qa/bath-fixtures-iteration07-probe-after.json')])
runpy.run_path(str(ROOT/'qa/bath-fixtures-iteration06-probe.py'),run_name='__main__')
preview=ROOT/'scene/Fallingwater_preview_iteration06.blend'
if preview.exists():
    bpy.ops.wm.open_mainfile(filepath=str(preview))
    result['smoke_preview_geometry_matches_before']={n:signature(bpy.data.objects[n])==s for n,s in before.items()}
    result['smoke_preview_sha256']=hashlib.sha256(preview.read_bytes()).hexdigest()
(ROOT/'qa/bath-fixtures-iteration07-fix-check.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('BATH_FIX_RESULT',json.dumps({k:v for k,v in result.items() if k not in ('checks','smoke_preview_geometry_matches_before')}),flush=True)
assert result['status']=='PASS_BOUNDED_TUBE_FIX_NOT_VISUAL_ACCEPTANCE'
