"""Candidate-only circulation overlays for the unchanged production tour module.

No production JSON or scene is saved. All mutable tour inputs/outputs must use
the isolated caller workspace. Frozen 10f physical evidence is not imported as
a navigation PASS: explicit changed routes are tested against the loaded mesh.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
CANDIDATE_SHA='7286427d1f47ae9219204ed5dd54a970387683c8b384d1b4259244a7b991d852'
SOURCE_SHA='489b05e403aa9d02c3568a8e3813a24235ee5b7e782df4d1f149b3ff6673e331'

def source(p):
    return [3.4+(p[0]-325)*.05256,37.1+(422-p[1])*.05272,8.4+p[2]]

def join(*pieces):
    result=[]
    for piece in pieces:
        for p in piece:
            p=list(p)
            if not result or (Vector(result[-1])-Vector(p)).length>.00001:result.append(p)
    return result

def physical_spec(scene,rooms):
    from guest_circulation10 import union_outline
    m=json.loads(bpy.data.texts['FW_GUEST_CIRCULATION10_CANDIDATE.json'].as_string())
    flights={f['id']:f for f in m['flights']}
    def flight(name,reverse=False):
        f=flights[name]
        p=[source([*f['source_start_px'],f['z0']])]+[t['center'] for t in f['treads']]+[source([*f['source_end_px'],f['z1']])]
        return p[::-1] if reverse else p
    def px(*points):return [source(p) for p in points]
    # All paths are foot coordinates until they enter the tour API. Northern
    # room attachments and southern turns follow the actual low/high surfaces.
    lower_turn=px((294.45,404.5,-1.18),(294.45,412.3,-1.18),(316.35,412.3,-1.18),(316.35,400.8,-1.18))
    upper_turn=px((296.75,405.5,1.4478),(296.75,412.3,1.4478),(316.35,412.3,1.4478),(316.35,405.5,1.4478))
    north_cross=px((316.35,350,0),(316.35,340,0),(296.75,340,0),(296.75,359.75,0))
    north_from_hall=px((296.75,359.75,0),(296.75,340,0),(316.35,340,0),(316.35,350,0))
    basement_to_hall=join(flight('F1_B1_LEFT_SOUTH'),lower_turn,flight('F2_LOWER_RIGHT_NORTH'),north_cross)
    upper=join(px((296.75,359.75,0),(296.75,369,0)),flight('F3_UPPER_LEFT_SOUTH'),upper_turn,
               flight('F4_UPPER_RIGHT_NORTH'),px((316.35,382,2.352675),(316.35,365,2.352675)))
    low_to_front=px((316.35,400.8,-1.18),(316.35,412.3,-1.18),(305,412.3,-1.18),(305,461,-1.18),(324,461,-1.18))
    front=join(north_from_hall,flight('F2_LOWER_RIGHT_NORTH',True),low_to_front,
               flight('W1_FRONT_WEST'),px((336,461,-.6742857142857143),(428,461,-.6742857142857143)),
               flight('W2_FRONT_EAST'),px((448,461,0),(466,461,0)))
    connector=join([m['connector'][0]['a']],[t['center'] for t in m['connector']],[m['connector'][-1]['b']],
                   px((305,423,-1.18),(305,412.3,-1.18),(316.35,412.3,-1.18),(316.35,400.8,-1.18)),
                   flight('F2_LOWER_RIGHT_NORTH'),north_cross)
    paths={
      'CAR_COURT_TO_HALL':{'from':'GUEST_L1_CAR_COURT','to':'GUEST_L1_STAIR_HALL',
                         'feet':px((296.75,340,0),(296.75,359.75,0)),'stairs':False},
      'HALL_TO_CHAUFFEUR':{'from':'GUEST_L1_STAIR_HALL','to':'GUEST_L1_CHAUFFEUR_LOUNGE',
                          'feet':px((296.75,359.75,0),(277,359.75,0)),'stairs':False},
      'HALL_TO_FRONT_TERRACE':{'from':'GUEST_L1_STAIR_HALL','to':'GUEST_L1_TERRACE','feet':front,'stairs':True},
      'REAL_SOUTHEAST_ENTRANCE':{'from':'GUEST_L1_TERRACE','to':'GUEST_L1_LOUNGE',
                                'feet':px((466,442,0),(466,424,0),(463,385,0),(450,383.24,0),(419.25,383.24,0)),'stairs':False},
      'BASEMENT_TWO_FLIGHTS':{'from':'GUEST_B1_STAIR','to':'GUEST_L1_STAIR_HALL','feet':basement_to_hall,'stairs':True},
      'BASEMENT_LAUNDRY_DOOR':{'from':'GUEST_B1_STAIR','to':'GUEST_B1_LAUNDRY',
                             'feet':px((294.45,364,-2.36),(278,364,-2.36)),'stairs':False},
      'UPPER_TWO_FLIGHTS':{'from':'GUEST_L1_STAIR_HALL','to':'GUEST_L2_HALL','feet':upper,'stairs':True},
      'MAIN_GUEST_CONNECTOR':{'from':'MAIN_L3_LINK','to':'GUEST_L1_STAIR_HALL','feet':connector,'stairs':True},
    }
    # Endpoints are real northern floor/landing positions. The original flat
    # census polygon is retained as an envelope, never used to create a floor.
    overrides={
      'GUEST_B1_STAIR':{'center':source((294.45,364,-2.36+1.55)),'entry':source((284,364,-2.36+.04)),
                        'polygon':union_outline([next(r['polygon'] for r in rooms if r['id']=='GUEST_B1_STAIR'),
                            [source((p[0],p[1],0))[:2] for p in next(p['polygon_px'] for p in m['platforms'] if p['id']=='P_B1_NORTH')]]),
                        'navigation_foot_anchors':px((294.45,362.5,-2.36),(294.45,364,-2.36)),
                        'surface_identity':'Nonplanar lower left flight, B1 northern door and south intermediate platform'},
      'GUEST_L1_STAIR_HALL':{'center':source((296.75,359.75,1.55)),'entry':source((296.75,347,.04)),
                           'navigation_foot_anchors':px((296.75,359.75,0),(296.75,351,0),(296.75,364,0)),
                           'surface_identity':'Northern L1 platform plus explicit descending/ascending flights and low south arrival; no uniform south0 floor'},
      'GUEST_L2_HALL':{'entry':source((316.35,382,2.352675+.04)),
                       'polygon':[source((x,y,0))[:2] for x,y in ((287,204),(326,204),(326,419.6),(287,419.6))],
                       'navigation_foot_anchors':px((316.35,365,2.352675),(316.35,350,2.352675)),
                       'surface_identity':'North L2 floor and actual right upper approach; south return is+1.4478, not L2'},
      'GUEST_L1_LOUNGE':{'entry':source((466,430,.04)),
                         'entry_identity':'Actual southeast glazed door; west corner is fixed glazing'},
      'GUEST_L1_TERRACE':{'entry':source((466,461,.04)),
                         'surface_identity':'East terrace0 plus source two stepped west paving groups; no flat west0 shortcut'},
    }
    return {'schema':'fallingwater.guest_circulation10.routes.v1','candidate_sha256':CANDIDATE_SHA,
            'source_sha256':SOURCE_SHA,'evidence':'C circulation levels/counts; A source identities retained separately in physical manifest',
            'adapter_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'numeric_build_input':json.loads((ROOT/'qa/guest-circulation10-design.json').read_text(encoding='utf-8')),
            'flights':m['flights'],'platforms':m['platforms'],'connector':m['connector'],
            'upper_source_divider':m['upper_source_divider'],'paths':paths,'room_overrides':overrides,
            'adjacency':m['adjacency'],'retracted_adjacency':m['retracted_adjacency'],
            'production_installation':False,'historical_checks_are_not_pass_inputs':True}

def prepare(workspace,scene,rooms,read_only=False):
    """Return a fresh tour module plus candidate room copies and auditable data."""
    work=Path(workspace).resolve()
    if work==ROOT or ROOT/'data'==work:raise ValueError('Isolated workspace required')
    if read_only:
        spec=json.loads((work/'data/guest_circulation10.json').read_text(encoding='utf-8'))
    else:
        spec=physical_spec(scene,rooms)
    spec_path=ROOT/'data/guest_circulation10.json'
    if not read_only:
        spec_path.write_text(json.dumps(spec,indent=2),encoding='utf-8')
        (work/'data/guest_circulation10.json').write_text(json.dumps(spec,indent=2),encoding='utf-8')
    updated=copy.deepcopy(rooms)
    for room in updated:
        if room['id'] in spec['room_overrides']:
            room.update(spec['room_overrides'][room['id']]);room['candidate_circulation_override']=True
    if not read_only:
        guestpath=work/'data/guest_house.json';guest=json.loads(guestpath.read_text(encoding='utf-8-sig'))
        guest['adjacency']=spec['adjacency'];guest['retracted_adjacency']=spec['retracted_adjacency']
        for wall in guest['walls']:
            if wall['id']=='GUEST_L1_WEST_LOUNGE':
                for op in wall.get('openings',[]):
                    if op['type']=='door':op['type']='window';op['candidate_source_correction']='Fixed corner glazing, not a door'
        guest['walls'].append({'id':'GUEST_C10_REAL_SOUTHEAST_DOOR','level':'L1','a':[457,430],'b':[476,430],
                               'thickness':.05,'openings':[{'type':'door','span':[0,1]}],
                               'evidence':'A guest01 source door identity; C frame/pose dimensions'})
        guest['connector']['points'][0][2]=5.28615
        guest['connector']['points'][-1][2]=7.22
        guestpath.write_text(json.dumps(guest,indent=2),encoding='utf-8')
        (work/'rooms.json').write_text(json.dumps(updated,indent=2),encoding='utf-8')
        (ROOT/'qa/guest-circulation10-navigation-room-overrides.json').write_text(json.dumps({
            'candidate_sha256':CANDIDATE_SHA,'room_overrides':spec['room_overrides'],
            'physical_planes_not_created_by_room_metadata':True,'candidate_only':True},indent=2),encoding='utf-8')
    module_spec=importlib.util.spec_from_file_location('tour_circulation10_candidate',ROOT/'scripts/tour.py')
    tour=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(tour);tour.ROOT=work
    original={n:getattr(tour,n) for n in ('Probe','hinted_connection','stair_connection','stair_space_anchors','room_candidates','connector_shot')}
    class EvaluatedProbe(original['Probe']):
        def __init__(self,scene,bounds=None):
            super().__init__(scene,bounds)
            verts=[];faces=[];owners=[]
            for ob in scene.objects:
                if ob.type not in ('MESH','CURVE','SURFACE','FONT') or ob.hide_render or ob.name.startswith(('REF_','QA_')):continue
                if bounds:
                    cc=[ob.matrix_world@Vector(v) for v in ob.bound_box]
                    if any(max(v[i] for v in cc)<bounds[i][0] or min(v[i] for v in cc)>bounds[i][1] for i in range(3)):continue
                eo=ob.evaluated_get(self.depsgraph);mesh=eo.to_mesh();offset=len(verts)
                verts.extend(eo.matrix_world@v.co for v in mesh.vertices)
                faces.extend(tuple(offset+i for i in p.vertices) for p in mesh.polygons)
                owners.extend([ob.name]*len(mesh.polygons));eo.to_mesh_clear()
            self.bvh=BVHTree.FromPolygons(verts,faces,epsilon=.001);self.face_owners=owners;self.cache.clear()
            self.mesh_counts={'vertices':len(verts),'polygons':len(faces),'evaluated_meshes':True}
            print('C10 evaluated full-scene BVH',self.mesh_counts,flush=True)
    tour.Probe=EvaluatedProbe
    by_pair={frozenset((v['from'],v['to'])):(k,v) for k,v in spec['paths'].items()}
    def tested_path(a,b,probe):
        key,path=by_pair[frozenset((a['id'],b['id']))]
        feet=path['feet'] if a['id']==path['from'] else path['feet'][::-1]
        points=[[p[0],p[1],p[2]+tour.EYE] for p in feet]
        old=probe.step_mode;probe.step_mode=path['stairs']
        try:failure=probe.path(points,True)
        finally:probe.step_mode=old
        endpoint_inside=[tour.inside(points[0],a['polygon']),tour.inside(points[-1],b['polygon'])]
        if not all(endpoint_inside) and not failure:failure={'reason':'EXPLICIT_PATH_ENDPOINT_OUTSIDE_ROOM','endpoint_inside':endpoint_inside}
        return {'status':'FAIL_C10_EXPLICIT_PHYSICAL_PATH' if failure else 'PASS_MESH_AND_GROUND',
                'from':a['id'],'to':b['id'],'points':points,'failure':failure,'candidate_path_id':key,
                'endpoint_inside_room_envelopes':endpoint_inside,'stair_mode':path['stairs'],
                'claim':'Actual complete path including northern room attachments; no film cut or old PASS satisfies this edge.'}
    def hinted(a,b,probe,candidates,hints,max_nodes=1800):
        if frozenset((a['id'],b['id'])) in by_pair:return tested_path(a,b,probe)
        return original['hinted_connection'](a,b,probe,candidates,hints,max_nodes)
    def stair(scene,a,b,probe,candidates,prefix):
        if frozenset((a['id'],b['id'])) in by_pair:return tested_path(a,b,probe)
        return original['stair_connection'](scene,a,b,probe,candidates,prefix)
    def candidates(room,probe,walk=True):
        if room.get('navigation_foot_anchors') and walk:
            old=probe.step_mode;probe.step_mode=True
            try:return [Vector((p[0],p[1],p[2]+tour.EYE)) for p in room['navigation_foot_anchors'] if probe.point((p[0],p[1],p[2]+tour.EYE),True) is None]
            finally:probe.step_mode=old
        return original['room_candidates'](room,probe,walk)
    def anchors(scene,rooms,probe,candidates):
        result,evidence=original['stair_space_anchors'](scene,rooms,probe,candidates)
        for r in rooms:
            if r.get('navigation_foot_anchors'):
                result[r['id']]=list(candidates[r['id']])
                evidence.append({'room_id':r['id'],'candidate_circulation10_anchors':r['navigation_foot_anchors'],
                                 'basis':'Actual candidate platforms; each anchor independently checked on this scene'})
        return result,evidence
    def connector_shot(probe):
        byid={r['id']:r for r in updated};result=tested_path(byid['MAIN_L3_LINK'],byid['GUEST_L1_STAIR_HALL'],probe)
        if result['status']!='PASS_MESH_AND_GROUND':return None,result
        return {'points':result['points'],'target':None,'mode':'NORMAL_WALK_ON_STAIRS',
                'ground_height_tested':True,'body_clearance_tested':True,
                'candidate_circulation10_path':'MAIN_GUEST_CONNECTOR'},result
    tour.hinted_connection=hinted;tour.stair_connection=stair;tour.room_candidates=candidates
    tour.stair_space_anchors=anchors;tour.connector_shot=connector_shot
    tour.circulation10_spec=spec
    tour.circulation10_limits={
        'global_legacy_body_column_top_m':1.71,'global_legacy_ground_tolerance_m':.19,
        'global_body_radius_m':.18,'changed_geometry_local_headroom_screen_m':1.95,
        'local_body_evidence':'qa/guest-circulation10-final-audit.json; no imported navigation PASS',
        'camera_and_global_navigation_not_equal_to_local_construction_screen':True}
    return tour,updated,spec
