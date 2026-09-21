"""Read-only 06 camera support and semantic witnesses, with a comparable 05 baseline."""
import argparse,sys,json,math,hashlib,collections,array
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import bpy
from mathutils import Vector
import camera_review as cr

p=argparse.ArgumentParser();p.add_argument('--scene',required=True);p.add_argument('--prefix',required=True)
p.add_argument('--settings',default=str(ROOT/'qa/camera05-settings-frozen-v2.json'))
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
bpy.ops.wm.open_mainfile(filepath=str(Path(a.scene).resolve()))
scene=bpy.context.scene;cfg=json.loads(Path(a.settings).read_text(encoding='utf-8'))
rooms=json.loads(bpy.data.texts['FW_ROOMS.json'].as_string());rm={r['id']:r for r in rooms}
assert set(cfg)=={'CAM_'+r['id']+'_'+s for r in rooms for s in ('A','B')}
geo=cr.Geometry(scene);deps=bpy.context.evaluated_depsgraph_get()
report={'scene':bpy.data.filepath,'scene_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
        'settings':str(Path(a.settings).resolve()),'settings_sha256':hashlib.sha256(Path(a.settings).read_bytes()).hexdigest(),
        'geometry':geo.counts,'scope':'Actual evaluated mesh including furniture, terrain, water and glass, excluding vegetation. 1.75m body, axial radius0.15m, four foot and six eye rays. Semantic witnesses are sparse evidence, never actual image, lighting or continuous navigation acceptance.',
        'cameras':[],'object_fingerprints':{}}
def bbox(obj):return [obj.matrix_world@Vector(q) for q in obj.bound_box]

# Fingerprints include actual evaluated shape, world transform and assigned
# material names. This is geometry change detection, not shader/lighting QA.
for name,obj in geo.objects.items():
    e=obj.evaluated_get(deps);m=e.to_mesh()
    if not m:continue
    co=array.array('f',[0])*(len(m.vertices)*3);m.vertices.foreach_get('co',co)
    loops=array.array('i',[0])*len(m.loops);m.loops.foreach_get('vertex_index',loops)
    counts=array.array('i',[0])*len(m.polygons);m.polygons.foreach_get('loop_total',counts)
    h=hashlib.sha256();h.update(co.tobytes());h.update(loops.tobytes());h.update(counts.tobytes())
    h.update(str([[round(x,7) for x in row] for row in e.matrix_world]).encode())
    h.update('|'.join(mat.name if mat else '' for mat in m.materials).encode())
    bb=[e.matrix_world@Vector(q) for q in e.bound_box]
    report['object_fingerprints'][name]={'sha256':h.hexdigest(),'room_id':obj.get('room_id'),
        'bounds':[min(v[i] for v in bb) for i in range(3)]+[max(v[i] for v in bb) for i in range(3)]}
    e.to_mesh_clear()
stair_prefix={'MAIN_L1_STAIR':'MAIN_stair1_','MAIN_L2_STAIR':'MAIN_stair2_','MAIN_L3_STAIR':'MAIN_stair2_',
              'MAIN_L1_SERVICE_STAIR':'MAIN_service_stair_','MAIN_B_STAIR':'MAIN_service_stair_',
              'MAIN_L1_HATCH':'MAIN_water_stair_','GUEST_B1_STAIR':'GUEST_LAUNDRY_DESCENT_tread_',
              'GUEST_L1_STAIR_HALL':'GUEST_SERVICE_ASCENT_tread_','MAIN_L3_LINK':'MAIN_north_spiral_'}
all_witness={}
for rid,room in rm.items():
    groups=collections.defaultdict(list)
    if rid in stair_prefix:
        for name,obj in geo.objects.items():
            if not name.startswith(stair_prefix[rid]) or any(s in name.lower() for s in ('rail','baluster','soffit')):continue
            bb=bbox(obj);q=sum(bb,Vector())/8;q.z=max(v.z for v in bb)+.025
            groups[name].append(q)
    else:
        for name,obj in geo.objects.items():
            group=None
            if rid=='GUEST_L1_LOUNGE' and name.startswith('GUEST_FIREPLACE'):group='GUEST_FIREPLACE'
            elif rid=='MAIN_L1_LIVING' and any(s in name for s in ('Hearth','hearth','fireplace','Fireplace')):group='MAIN_HEARTH_ARCHITECTURE'
            elif obj.get('room_id')==rid and obj.get('component_type')=='furniture' and 'lamp' not in obj.get('asset_type',''):group=obj.get('asset_id',name)
            if group:groups[group].append(sum(bbox(obj),Vector())/8)
    witness=[]
    for group,points in groups.items():
        ordered=sorted(points,key=lambda q:q.z)
        samples=ordered if len(ordered)<=7 else [ordered[round(i*(len(ordered)-1)/6)] for i in range(7)]
        witness.extend((q,group) for q in samples)
    all_witness[rid]=witness

for name,c in cfg.items():
    room=rm[c['room_id']];eye=Vector(c['location']);ground=c['support_z']
    issue=geo.clearance(eye,ground)
    center=geo.ray((eye.x,eye.y,ground+.16),(0,0,-1),.3)
    if not center or abs(center['location'][2]-ground)>.04:issue={'reason':'STORED_GROUND_CHANGED','hit':center}
    if not 28<=c['lens']<=40:issue={'reason':'LENS_OUTSIDE_APPROVED_RANGE'}
    forward=(Vector(c['target'])-eye).normalized();right=forward.cross(Vector((0,0,1))).normalized();up=right.cross(forward).normalized()
    visible=collections.Counter();framed=collections.Counter();hidden=collections.Counter();events=[]
    for q,owner in all_witness[room['id']]:
        delta=q-eye;depth=delta.dot(forward)
        if depth<=.05:continue
        ux=.5+delta.dot(right)*c['lens']/(36*depth)-c.get('shift_x',0)
        vy=.5+delta.dot(up)*c['lens']/(20.25*depth)-c.get('shift_y',0)*36/20.25
        if not(.07<ux<.93 and .06<vy<.94):continue
        framed[owner]+=1;hit=geo.ray(eye,delta,delta.length+.12)
        hitobj=geo.objects[hit['object']] if hit else None
        ok=bool(hit and (hit['object']==owner or hitobj.get('asset_id')==owner or owner=='GUEST_FIREPLACE' and hit['object'].startswith(owner) or owner=='MAIN_HEARTH_ARCHITECTURE' and any(s in hit['object'] for s in ('Hearth','hearth','fireplace','Fireplace'))))
        if ok:visible[owner]+=1
        elif hit:hidden[hit['object']]+=1
        events.append({'owner':owner,'point':cr.plain(q),'uv':[round(ux,5),round(vy,5)],'visible':ok,'first_hit':hit})
    grid=[]
    for ix in range(11):
        for iy in range(7):
            ux=(ix+.5)/11;vy=(iy+.5)/7
            direction=forward+right*((ux-.5+c.get('shift_x',0))*36/c['lens'])+up*(((vy-.5)*20.25+c.get('shift_y',0)*36)/c['lens'])
            grid.append({'uv':[round(ux,5),round(vy,5)],'hit':geo.ray(eye,direction,60)})
    outside=not cr.inside(eye,room['polygon'])
    report['cameras'].append({'camera':name,'room_id':room['id'],'geometry_status':'FAIL' if issue else 'GEOMETRY_ONLY_PASS','issue':issue,
        'outside_current_room_polygon':outside,'stored_outside_flag_matches':outside==c.get('outside_room_polygon',False),
        'stored_support':{'object':c.get('support_object'),'z':ground},'actual_center_support':center,
        'support_delta_z_m':round(center['location'][2]-ground,6) if center else None,
        'semantic_witness_status':'HAS_VISIBLE_TARGETS_RENDER_PENDING' if visible else ('NO_VISIBLE_TARGETS' if all_witness[room['id']] else 'NO_DEFINED_FURNITURE_OR_STAIR_WITNESSES'),
        'visible_witnesses':dict(visible),'framed_witnesses':dict(framed),'occluding_objects':dict(hidden),'witness_events':events,
        'shifted_frame_grid':grid,'near_grid_rays_under_06m':sum(g['hit'] is not None and g['hit']['distance']<.6 for g in grid),
        'terrain_grid_rays':sum(g['hit'] is not None and g['hit']['object']=='SITE_Continuous_BearRun_Terrain' for g in grid)})
report['rays_cast']=geo.calls
report['status']='FAIL' if any(c['issue'] for c in report['cameras']) else 'GEOMETRY_ONLY_PASS_VISUAL_PENDING'
report['camera_count']=len(cfg)
cr.write_json(ROOT/f'qa/{a.prefix}.json',report)
print('CAMERA06_CHECK '+json.dumps({'scene':Path(bpy.data.filepath).name,'status':report['status'],'cameras':len(cfg),'rays':geo.calls,
                                    'failures':[c['camera'] for c in report['cameras'] if c['issue']]}),flush=True)
