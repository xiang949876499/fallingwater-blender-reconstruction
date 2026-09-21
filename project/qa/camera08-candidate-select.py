"""Bounded manual regions, true support/body checks, and semantic frame diagnostics."""
import sys,json,hashlib,math,collections,random,copy,argparse
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import camera_review as cr
scene_path=ROOT/'scene/Fallingwater_iteration07.blend'
assert hashlib.sha256(scene_path.read_bytes()).hexdigest()=='bf50530009e4a93315915815473188c91d891272ef2d8e9e0169b704bd2e2f16'
bpy.ops.wm.open_mainfile(filepath=str(scene_path));scene=bpy.context.scene
scene.render.threads_mode='FIXED';scene.render.threads=4
cfg=json.loads((ROOT/'qa/camera07e-settings-frozen.json').read_text(encoding='utf-8'))
assert hashlib.sha256((ROOT/'data/camera-settings-reviewed.json').read_bytes()).hexdigest()=='4def78dcbae91f3292562f41796adec71c4680b64e04301f051fdc1833ce8666'
parser=argparse.ArgumentParser()
parser.add_argument('--plan',default=str(ROOT/'qa/camera08-candidate-plan.json'))
parser.add_argument('--append',action='store_true')
parser.add_argument('--report',default=str(ROOT/'qa/camera08-candidate-search-report.json'))
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
plan=json.loads(Path(args.plan).read_text(encoding='utf-8'))
rm={r['id']:r for r in json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())}
geo=cr.Geometry(scene)
offsets=[(0,0),(.06,0),(-.06,0),(0,.06),(0,-.06)]
selected=json.loads((ROOT/'qa/camera08-candidate-settings.json').read_text(encoding='utf-8')) if args.append else {};results=[]
def projection(eye,target,lens,shift):
    f=(Vector(target)-eye).normalized();right=f.cross(Vector((0,0,1))).normalized();up=right.cross(f).normalized()
    def uv(q):
        d=Vector(q)-eye;depth=d.dot(f)
        if depth<=.01:return None
        return [.5+d.dot(right)*lens/(36*depth),.5+d.dot(up)*lens/(20.25*depth)-shift*36/20.25]
    return f,right,up,uv
def semantic(eye,values,room,subjects):
    f,right,up,uv=projection(eye,values['target'],values['lens'],values['shift_y'])
    rng=random.Random(812);hits=collections.Counter();types=collections.Counter();near=0;grid=[]
    for ix in range(21):
      for iy in range(13):
        u=(ix+.2+.6*rng.random())/21;v=(iy+.2+.6*rng.random())/13
        direction=f+right*((u-.5)*36/values['lens'])+up*(((v-.5)*20.25+values['shift_y']*36)/values['lens'])
        h=geo.ray(eye,direction,40)
        if h:
            hits[h['object']]+=1;near+=h['distance']<.65
            o=geo.objects[h['object']]
            if o.get('room_id')==room['id']:types[o.get('asset_type','ROOM_STRUCTURE')]+=1
            if subjects==['POOL'] and any(s in h['object'].lower() for s in ('pool','plunge')):types['POOL']+=1
            if subjects==['STAIR'] and 'MAIN_stair2_' in h['object']:types['STAIR']+=1
        grid.append({'uv':[round(u,5),round(v,5)],'hit':h})
    framed=[]
    for o in geo.objects.values():
        if o.get('room_id')==room['id'] and o.get('asset_type') in subjects:
            bb=[o.matrix_world@Vector(q) for q in o.bound_box]
            center=sum(bb,Vector())/8;pos=uv(center)
            if pos and .03<pos[0]<.97 and .03<pos[1]<.97:
                d=center-eye;h=geo.ray(eye,d,d.length+.06)
                if h and geo.objects[h['object']].get('asset_id')==o.get('asset_id'):
                    framed.append({'object':o.name,'asset_type':o.get('asset_type'),'uv':pos})
    frac={s:types[s]/273 for s in subjects};dominant=hits.most_common(1)[0][1]/273 if hits else 0
    # This only rejects obviously absent or overwhelmingly near subjects. It
    # cannot establish photograph readability; every chosen view needs render.
    required=min(frac.values()) if frac else 0
    gate=all(v>=.015 for v in frac.values()) and sum(frac.values())>=.07 and near/273<.28 and dominant<.85
    score=sum(min(v,.4) for v in frac.values())+min(required,.15)*1.8-near/273*1.2-max(0,dominant-.48)*.8
    return {'semantic_geometry_gate':gate,'score':score,'subject_fractions':frac,'near_under065_fraction':near/273,'dominant_fraction':dominant,'dominant_hits':hits.most_common(8),'visible_subject_part_points':framed,'grid':grid}
for name,spec in plan.items():
    old=cfg[name];room=rm[old['room_id']];tested=[];safe=[]
    for nominal_index,xy in enumerate(spec['points']):
        found=None
        for dx,dy in offsets:
            point=(xy[0]+dx,xy[1]+dy)
            support,problem=geo.support(point,room,spec.get('support_offset',.32))
            if problem:tested.append({'xy':point,'issue':problem});continue
            eye=Vector((*point,support['location'][2]+1.6));problem=geo.clearance(eye,support['location'][2])
            if problem:tested.append({'xy':point,'issue':problem});continue
            if name.endswith('_B'):
                other=selected.get(name[:-1]+'A',cfg.get(name[:-1]+'A'))
                if other:
                    angle=(Vector(spec['target'])-eye).normalized().angle((Vector(other['target'])-Vector(other['location'])).normalized())
                    if math.dist(eye,other['location'])<.7 and angle<.6:tested.append({'xy':point,'issue':'INSUFFICIENT_COMPLEMENT_TO_A'});continue
            if name=='CAM_MAIN_L3_STAIR_A':
                if any(math.dist(eye,cfg[k]['location'])<.65 for k in ('CAM_MAIN_L2_STAIR_A','CAM_MAIN_L3_STAIR_B')):tested.append({'xy':point,'issue':'DUPLICATE_STAIR_REGION'});continue
            values=copy.deepcopy(old)
            values.update(location=cr.plain(eye),target=spec['target'],lens=spec['lens'],shift_x=0,shift_y=spec['shift_y'],support_z=support['location'][2],support_object=support['object'],outside_room_polygon=not cr.inside(eye,room['polygon']),render_reviewed=False,
                evidence='08 candidate on frozen07 actual geometry: '+spec['reason']+' Geometry diagnostics only; actual image review pending.',composition_status='CANDIDATE_RENDER_PENDING',final_quality_accepted=False)
            for stale in ('composition_review','exposure_review'):values.pop(stale,None)
            quality=semantic(eye,values,room,spec['subjects'])
            found={'nominal_index':nominal_index,'values':values,'support':support,'semantic':quality}
            tested.append({'xy':point,'issue':None,'nominal_index':nominal_index,'semantic_geometry_gate':quality['semantic_geometry_gate']})
            safe.append(found);break
    good=[c for c in safe if c['semantic']['semantic_geometry_gate']]
    best=max(good,key=lambda c:c['semantic']['score']) if good else None
    if best:selected[name]=best['values']
    results.append({'camera':name,'status':'GEOMETRY_SAFE_SEMANTIC_CANDIDATE_RENDER_PENDING' if best else 'NO_BOUNDED_SEMANTIC_CANDIDATE','plan':spec,'attempts':tested,'safe_nominal_candidates':safe,'selected_nominal':best['nominal_index'] if best else None})
    cr.write_json(ROOT/'qa/camera08-candidate-settings.json',selected)
    cr.write_json(Path(args.report),{'scene':str(scene_path),'scene_sha256':hashlib.sha256(scene_path.read_bytes()).hexdigest(),'geometry':geo.counts,'scope':'Bounded plan: maximum4 nominal regions x5 local offsets of6cm per view. Support/body and shifted273-ray grid diagnostics only; no model changes or renders. Do not treat this as visual acceptance.','cameras':results,'rays_cast':geo.calls})
    print('CAMERA08_CANDIDATE '+json.dumps({'camera':name,'safe_regions':len(safe),'passing_semantic_regions':len(good),'selected':None if not best else {k:best['values'][k] for k in ('location','target','lens','shift_y')},'subject_fractions':None if not best else best['semantic']['subject_fractions']}),flush=True)
print('CAMERA08_DONE '+json.dumps({'selected':len(selected),'expected':11,'missing':sorted(set(plan)-set(selected))}),flush=True)
readback=json.loads((ROOT/'qa/camera08-candidate-settings.json').read_text(encoding='utf-8'))
checks=[]
for name,c in readback.items():
    issue=geo.clearance(c['location'],c['support_z'])
    h=geo.ray((c['location'][0],c['location'][1],c['support_z']+.16),(0,0,-1),.3)
    if not h or abs(h['location'][2]-c['support_z'])>.04:issue={'reason':'STORED_GROUND_CHANGED','hit':h}
    checks.append({'camera':name,'status':'FAIL' if issue else 'GEOMETRY_ONLY_PASS','issue':issue,'actual_support':h,'stored_support':{'object':c['support_object'],'z':c['support_z']},'location':c['location'],'target':c['target'],'lens':c['lens'],'shift_y':c['shift_y'],'outside_room_polygon':c['outside_room_polygon']})
cr.write_json(ROOT/'qa/camera08-candidate-readback.json',{'scene_sha256':hashlib.sha256(scene_path.read_bytes()).hexdigest(),'settings_sha256':hashlib.sha256((ROOT/'qa/camera08-candidate-settings.json').read_bytes()).hexdigest(),'scope':'Re-read emittedcandidateJSON and independently re-run actual support/body/eye tests using this07 mesh index. These candidate camera transforms are not saved in07; this does not claim savedscene matches or newvisual acceptance.','camera_count':len(checks),'status':'FAIL' if any(c['issue'] for c in checks) else 'GEOMETRY_ONLY_PASS','cameras':checks})
