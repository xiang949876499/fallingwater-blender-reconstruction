"""Independent actual integrated-scene recheck of identified geometry defects.

No render, scene modification or GPU use. Includes furnishings and terrain in rays.
"""
import bpy
import json
import math
from pathlib import Path
import re
import sys
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import main_house

bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'scene/Fallingwater_working.blend'))
scene = bpy.context.scene
dg = bpy.context.evaluated_depsgraph_get()

def ray(origin, direction, distance=100):
    hit, position, normal, index, obj, matrix = scene.ray_cast(dg, Vector(origin), Vector(direction), distance=distance)
    return {'object': obj.name, 'position': list(position), 'normal': list(normal), 'distance': (position-Vector(origin)).length} if hit else None

def clearance(point, top):
    up = ray((point[0], point[1], top+.025), (0, 0, 1), 10)
    return None if not up else {'object': up['object'], 'clearance_m': up['position'][2]-top}

report = {'scene': bpy.data.filepath, 'scene_mtime': Path(bpy.data.filepath).stat().st_mtime,
          'method': 'Actual integrated evaluated-scene rays, including furniture/site. Tread centers plus lateral offsets; vertical headroom, horizontal radius probes and door-plane crossing. Sampled checks, not continuous swept-body or final navigation acceptance.',
          'stairs': [], 'doors': [], 'thresholds': []}

for prefix in ('MAIN_stair2_', 'MAIN_pool_eastterrace_stair_', 'MAIN_water_stair_', 'GUEST_SERVICE_ASCENT_tread_'):
    steps = sorted((o for o in scene.objects if re.fullmatch(re.escape(prefix)+r'\d+', o.name)), key=lambda o: o.name)
    samples = []
    for step in steps:
        corners = [step.matrix_world @ Vector(v) for v in step.bound_box]
        top = max(v.z for v in corners)
        center = step.matrix_world.translation
        lateral = step.matrix_world.to_3x3() @ Vector((0, 1, 0)); lateral.normalize()
        for off in (-.22, 0, .22):
            point = center+lateral*off
            ground = ray((point.x, point.y, top+.065), (0, 0, -1), .15)
            head = clearance(point, top)
            body = []
            # Center radial probes cover a 0.44m body envelope; lateral samples
            # independently check ground and headroom across this same envelope.
            if off == 0:
                for height in (.30, .75, 1.20, 1.65, 1.93):
                    for i in range(8):
                        a = i*math.tau/8
                        hit = ray((point.x, point.y, top+height), (math.cos(a), math.sin(a), 0), .22)
                        if hit: body.append({'height': height, 'object': hit['object'], 'distance': hit['distance']})
            ok = bool(ground) and abs(ground['position'][2]-top)<.03 and (not head or head['clearance_m']>=1.95) and not body
            samples.append({'step': step.name, 'offset_m': off, 'ground': ground, 'headroom': head, 'body_hits': body, 'status': 'PASS' if ok else 'FAIL'})
    report['stairs'].append({'prefix': prefix, 'count': len(steps), 'samples': samples,
                             'status': 'PASS' if samples and all(s['status']=='PASS' for s in samples) else 'FAIL'})

# Test the actual missing-pane interval rather than trusting opening-width tags.
for sill in scene.objects:
    if not sill.name.endswith('_sill') or '_open_casement' in sill.name or sill.get('opening_use')!='terrace_door':
        continue
    base = sill.name[:-5]
    mullions = [o for o in scene.objects if re.fullmatch(re.escape(base)+r'_mullion_\d+', o.name)]
    n = len(mullions)-1
    length = max(v.co.x for v in sill.data.vertices)-min(v.co.x for v in sill.data.vertices)
    local_x = -length/2+(n//2+.5)*length/n
    center = sill.matrix_world @ Vector((local_x, 0, 0))
    normal = sill.matrix_world.to_3x3() @ Vector((0, 1, 0)); normal.normalize()
    hits = []
    for h in (.35, .9, 1.65, 1.94):
        before = center-normal*.20; before.z = center.z+h
        hit = ray(before, normal, .4)
        if hit: hits.append({'height_above_sill': h, 'object': hit['object']})
    report['doors'].append({'id': base, 'modeled_clear_width_m': length/n-.038, 'crossing_hits': hits, 'status': 'PASS' if not hits else 'FAIL'})

for name, rid, rect, level, mat, path in main_house.THRESHOLDS:
    a, b = Vector(main_house.xy(path[0])), Vector(main_house.xy(path[1]))
    z = main_house.LEVELS[level]
    ground_fail = []; body_hits = []
    for i in range(13):
        p = a.lerp(b, i/12)
        hit = ray((p.x,p.y,z+.2), (0,0,-1), .45)
        if not hit or abs(hit['position'][2]-z)>.16: ground_fail.append({'fraction': i/12, 'hit': hit})
        for h in (.35,.9,1.65):
            # Detect a component enclosing the point by paired short rays. A
            # nearby edge alone is not a centerline penetration assertion.
            forward = ray((p.x,p.y,z+h), (1,.137,.051), .07)
            backward = ray((p.x,p.y,z+h), (-1,-.137,-.051), .07)
            if forward and backward and forward['object']==backward['object']:
                body_hits.append({'fraction':i/12, 'height':h, 'object':forward['object']})
    report['thresholds'].append({'id': name, 'ground_failures':ground_fail, 'body_penetrations':body_hits, 'status':'PASS' if not ground_fail and not body_hits else 'FAIL'})

report['main_pool_exposure'] = ray(main_house.xyz((615,402),-2.49),(0,0,-1),3)
report['guest_pool_preservation'] = ray((24.69994,35.6797,9.3),(0,0,-1),2)
report['hatch_top_vertical_plane'] = []
for h in (.3,.9,1.65,1.93):
    a = main_house.xyz((457,480),.1+h); b = Vector(main_house.xyz((462,480),.1+h))
    delta=b-Vector(a); hit=ray(a,delta.normalized(),delta.length)
    if hit:report['hatch_top_vertical_plane'].append({'height':h,'object':hit['object']})

roomdata = json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())
report['materials'] = []
for room in roomdata:
    if room['kind'] not in ('bath','bathroom','kitchen'):continue
    objects = [o for o in scene.objects if o.type=='MESH' and (o.get('room_id')==room['id'] or o.name.startswith(room['id'])) and not o.name.startswith('FW_FURN_')]
    report['materials'].append({'room_id':room['id'], 'surfaces':[{'object':o.name,'materials':[m.name for m in o.data.materials if m]} for o in objects]})
rubber=bpy.data.materials.get('MAIN_Kitchen_9inch_Cherokee_Rubber')
report['kitchen_grid'] = {'material':rubber.name if rubber else None,'tile_size_m':rubber.get('tile_size_m') if rubber else None}
report['summary'] = {'stairs_failed':[s['prefix'] for s in report['stairs'] if s['status']=='FAIL'],
                     'doors_failed':[d['id'] for d in report['doors'] if d['status']=='FAIL'],
                     'thresholds_failed':[d['id'] for d in report['thresholds'] if d['status']=='FAIL']}
(ROOT/'qa/automated-iteration02.geometry.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report['summary']),flush=True)
