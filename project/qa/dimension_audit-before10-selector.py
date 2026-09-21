"""Remeasure a saved, currently loaded scene; never use data-file model values.

Post-save integration API:
    audit_dimensions(root, scene_path=bpy.data.filepath, prefix='dimensions-iteration05')
This function only reads meshes and writes reports/CSV. It never builds, edits or
saves scene geometry. The CLI opens the requested frozen scene before calling it.
"""
import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nominal_targets import load_reviews, qualify


MAIN_LEVELS = {
    'MAIN_LEVEL_2': 'MAIN_L2_TERRACE_S_slab',
    'MAIN_LEVEL_3': 'MAIN_L3_TERRACE_slab',
    'MAIN_ROOF_EAST': 'MAIN_L3_gallery_roof',
    'MAIN_ROOF_WEST': 'MAIN_L3_study_roof',
}
GUEST_CLEAR = {
    'GUEST_BOILER_DIM_1': ((353,333),1,['GUEST_L1_BOILER_NORTH','GUEST_L1_BOILER_SOUTH'],'L1',.35),
    'GUEST_BOILER_DIM_2': ((353,343),0,['GUEST_L1_BOILER_WEST','GUEST_L1_BOILER_EAST'],'L1',.35),
    'GUEST_GUEST_ROOM_LENGTH': ((580,425),0,['GUEST_L1_BATH_EAST','GUEST_L1_BED_EAST'],'L1',.35),
    'GUEST_GUEST_ROOM_DEPTH': ((580,400),1,['GUEST_L1_NORTH_STONE_SPINE','GUEST_L1_BED_FRONT'],'L1',.35),
    'GUEST_LAUNDRY_LENGTH': ((258,393),1,['GUEST_B1_BASE_NORTH','GUEST_B1_BASE_SOUTH'],'B',.50),
    'GUEST_LAUNDRY_DEPTH': ((255,406),0,['GUEST_B1_BASE_BATH_EAST','GUEST_B1_BASE_EAST'],'B',.50),
    'GUEST_BASE_BATH_LENGTH': ((216,400),1,['GUEST_B1_BASE_BATH_NORTH','GUEST_B1_BASE_SOUTH'],'B',.50),
    'GUEST_BASE_BATH_WIDTH': ((216,404),0,['GUEST_B1_BASE_BATH_WEST','GUEST_B1_BASE_BATH_EAST'],'B',.50),
}
GUEST_HEIGHTS = {
    'GUEST_SECOND_LEVEL': ['GUEST_L2_BEDROOM_FLOOR'],
    'GUEST_TOP_STONE': ['GUEST_L2_UPPER_TERRACE_DIAGONAL','GUEST_L2_UPPER_TERRACE_NORTHEAST','GUEST_L2_UPPER_TERRACE_EAST'],
    'GUEST_PARAPET': ['GUEST_LOW_ARM_ROOF_parapet_'],
    'GUEST_CHIMNEY': ['GUEST_STONE_CHIMNEY'],
    'GUEST_LOW_STONE': ['GUEST_L1_NORTH_STONE_SPINE'],
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class MeshReader:
    """Evaluate only explicit structural selectors, preserving vertex/face IDs."""
    def __init__(self):
        self.deps = bpy.context.evaluated_depsgraph_get()
        self.cache = {}
        self.empty_coping_segments = []

    def pool_coping_names(self):
        """Measure surviving rim surfaces after the documented dry-entry cut.

        An evaluated Boolean may remove a whole rim segment. Record that empty
        segment explicitly; all missing/empty selectors elsewhere still fail.
        """
        names = self.names(pattern=r'GUEST_POOL_coping_\d+')
        surviving = []
        for name in names:
            ob = bpy.data.objects[name].evaluated_get(self.deps)
            mesh = ob.to_mesh()
            try:
                if mesh and len(mesh.vertices) and len(mesh.polygons):
                    surviving.append(name)
                else:
                    source = bpy.data.objects[name]
                    if not source.get('source_entry_cut'):
                        raise ValueError('Undocumented empty pool coping segment: ' + name)
                    if name not in self.empty_coping_segments:
                        self.empty_coping_segments.append(name)
            finally:
                ob.to_mesh_clear()
        if not surviving:
            raise ValueError('No surviving pool coping surfaces')
        return surviving

    def names(self, prefixes=None, exact=None, pattern=None):
        names = []
        for ob in bpy.context.scene.objects:
            if ob.type != 'MESH':
                continue
            if exact is not None and ob.name in exact:
                names.append(ob.name)
            elif prefixes and any(ob.name.startswith(p) for p in prefixes):
                names.append(ob.name)
            elif pattern and re.fullmatch(pattern, ob.name):
                names.append(ob.name)
        names.sort()
        if not names:
            raise ValueError(f'No mesh matches exact={exact}, prefixes={prefixes}, pattern={pattern}')
        if exact and set(names) != set(exact):
            raise ValueError(f'Missing exact object(s): {set(exact)-set(names)}')
        return names

    def mesh(self, name):
        if name not in self.cache:
            ob = bpy.data.objects[name].evaluated_get(self.deps)
            mesh = ob.to_mesh()
            try:
                vertices = [tuple(ob.matrix_world @ v.co) for v in mesh.vertices]
                faces = [tuple(p.vertices) for p in mesh.polygons]
                if not vertices or not faces:
                    raise ValueError(f'Empty evaluated mesh: {name}')
                self.cache[name] = {'vertices':vertices, 'faces':faces,
                    'bvh':BVHTree.FromPolygons(vertices, faces, all_triangles=False)}
            finally:
                ob.to_mesh_clear()
        return self.cache[name]

    def extreme(self, names, axis, side):
        choices = [(p[axis],name,i,p) for name in names
                   for i,p in enumerate(self.mesh(name)['vertices'])]
        value,name,index,p = (min if side == 'min' else max)(choices,key=lambda t:t[0])
        vertex_ids = [i for i,q in enumerate(self.mesh(name)['vertices']) if abs(q[axis]-value)<1e-6]
        return {'object':name,'axis':'XYZ'[axis],'side':side,'coordinate_m':value,
                'point_m':list(p),'evaluated_vertex_ids':vertex_ids,
                'representative_vertex_id':index,'selected_objects':names}

    def ray(self, names, origin, direction):
        hits = []
        for name in names:
            m = self.mesh(name)
            p,n,face,distance = m['bvh'].ray_cast(Vector(origin),Vector(direction),50)
            if p is not None:
                hits.append((distance,name,p,n,face))
        if not hits:
            raise ValueError('No actual face hit for explicit structural selector')
        distance,name,p,n,face = min(hits,key=lambda h:h[0])
        return {'object':name,'point_m':list(p),'normal':list(n),'evaluated_face_index':face,
                'evaluated_face_vertex_ids':list(self.mesh(name)['faces'][face]),
                'ray_origin_m':list(origin),'ray_direction':list(direction),
                'ray_distance_m':distance,'selected_objects':names}

    def opposite_rays(self, names, origin, axis):
        direction = [0,0,0];direction[axis]=1
        return [self.ray(names,origin,[-v for v in direction]),self.ray(names,origin,direction)]


def audit_dimensions(root, *, scene_path=None, prefix='dimensions-iteration05',
                     expected_sha256=None, write_csv=True):
    """Read saved/current scene and return a report; no scene mutation or save."""
    root = Path(root).resolve();scene_path = Path(scene_path or bpy.data.filepath).resolve()
    if not scene_path.is_file() or Path(bpy.data.filepath).resolve() != scene_path:
        raise ValueError('Load/save the intended scene before calling dimension_audit')
    if bpy.data.is_dirty:
        raise ValueError('Save the current scene before auditing; its disk hash must identify the measured state')
    scene_hash = sha(scene_path)
    if expected_sha256 and scene_hash != expected_sha256:
        raise ValueError(f'Scene SHA mismatch: {scene_hash}')
    if not re.fullmatch(r'[a-z0-9_-]+',prefix):
        raise ValueError('Invalid report prefix')
    qa=root/'qa';qa.mkdir(exist_ok=True)
    main=json.loads((root/'data/main_house.json').read_text(encoding='utf-8'))
    guest=json.loads((root/'data/guest_house.json').read_text(encoding='utf-8'))
    config=json.loads((root/'config.json').read_text(encoding='utf-8'))
    extra_path=root/'data/dimension-anchors-extra.json'
    extras=json.loads(extra_path.read_text(encoding='utf-8'))['dimensions'] if extra_path.exists() else []
    reg=dict(guest['registration']);reg.update(config.get('guest_registration',{}))
    sx,sy=reg['meters_per_pixel'];ox,oy=reg['origin_px'];wx,wy,_=reg['world_origin']
    def guest_origin(p,z):return (wx+(p[0]-ox)*sx,wy+(oy-p[1])*sy,z)
    historical={}
    for path in [qa/'main-dimensions-measured.json',qa/'guest-dimension-fixes-measured.json']:
        for r in json.loads(path.read_text(encoding='utf-8'))['measurements']:
            historical[r['id']]=r
    reader=MeshReader();rows=[];nominal_reviews=load_reviews(root)
    for building,data in [('MAIN',main),('GUEST',guest)]:
        for dim in data['dimensions']+[d for d in extras if d['building']==building]:
            key=dim['id'];reference=dim['meters'];unc=dim.get('uncertainty_m')
            tolerance=max(.020,.005*reference)
            row={'id':key,'building':building,'source':dim['source'],
                 'source_label':dim.get('raw',dim.get('original')),'reference_m':reference,
                 'source_reading_uncertainty_m':unc,'source_recorded_uncertainty_m':unc,'label_evidence':'A',
                 'nominal_target_review':None,'survey_absolute_accuracy_m':None,
                 'survey_absolute_accuracy_status':'UNKNOWN',
                 'endpoint_evidence':'C source-to-mesh correspondence, unless noted',
                 'tolerance_m':tolerance,'actual_mesh_m':None,'delta_m':None,
                 'numeric_result':'NOT_RUN','standard_result':'NOT_RUN',
                 'uncertainty_exceeds_tolerance':unc is not None and unc>tolerance,
                 'source_axis':dim.get('axis'),'source_pixels':dim.get('pixels',dim.get('label_bbox_normalized_px')),
                 'endpoints':[],'method':None,'feature_category':'plan_span',
                 'not_run_reason':None,'scene_sha256':scene_hash}
            try:
                ends=None;axis=None
                if key=='MAIN_CHAIN_03':
                    axis=0
                    ends=[reader.extreme(reader.names(exact=[n]),axis,'max') for n in ['MAIN_L1_north_spine_1','MAIN_L1_north_spine_3']]
                    row['method']='Actual evaluated east outer faces of two north masonry returns; original TIFF extension lines establish the correspondence.'
                elif key=='MAIN_LEVEL_2':
                    axis=2
                    ends=[reader.extreme(reader.names(exact=[n]),axis,'max') for n in ['MAIN_L1_TERRACE_W_finish','MAIN_L2_TERRACE_S_finish']]
                    row.update(feature_category='elevation',method='Actual evaluated finished terrace top Z difference. Both finish elevations are remeasured; no assumed cancellation of historic finish thicknesses.')
                elif key in MAIN_LEVELS:
                    axis=2
                    ends=[reader.extreme(reader.names(exact=[n]),axis,'max') for n in ['MAIN_L1_TERRACE_W_slab',MAIN_LEVELS[key]]]
                    row.update(feature_category='elevation',method='Actual slab top Z difference from actual main terrace datum slab; no finish thickness substituted.')
                elif key=='GUEST_LAUNDRY_STAIR_CLEAR':
                    row['feature_category']='connections'
                    names=reader.names(exact=['GUEST_B1_BASE_EAST_pier_end','GUEST_LAYERED_SANDSTONE_COURSES','GUEST_LAUNDRY_DESCENT_outer_retaining_wall'])
                    datum=reader.extreme(reader.names(exact=['GUEST_L1_MAIN_FLOOR']),2,'max')['coordinate_m']
                    stations=[]
                    # Registration-relative stations from the independently
                    # inspected source span; Z derives from real slab/treads.
                    for dx,dy,z in [(-1.624099994,1.687040710,datum-.35),
                                    (-1.624099994,2.569998169,reader.extreme(reader.names(exact=['GUEST_LAUNDRY_DESCENT_tread_11']),2,'max')['coordinate_m']+1.8),
                                    (-1.624099994,1.230001831,reader.extreme(reader.names(exact=['GUEST_LAUNDRY_DESCENT_tread_01']),2,'max')['coordinate_m']+.12)]:
                        pair=reader.opposite_rays(names,(wx+dx,wy+dy,z),0)
                        stations.append({'endpoints':pair,'actual_mesh_m':abs(pair[1]['point_m'][0]-pair[0]['point_m'][0])})
                    ends=stations[0]['endpoints'];axis=0
                    row.update(stations=stations,max_sampled_abs_error_m=max(abs(v['actual_mesh_m']-reference) for v in stations),
                               method='Three fresh opposed rays to visible laundry structural/rough-stone faces and the outer stair wall. One connection anchor; three stations are not three anchors or a global continuous minimum proof.',
                               endpoint_evidence='Verified opposing faces identified by explicit guest01 extension lines; rough-face nominal placement, wall height and material remain C.')
                elif key in GUEST_CLEAR:
                    p,axis,prefixes,level,height=GUEST_CLEAR[key]
                    datum_name='GUEST_L1_MAIN_FLOOR' if level=='L1' else 'GUEST_B1_FLOOR'
                    z=reader.extreme(reader.names(exact=[datum_name]),2,'max')['coordinate_m']
                    ends=reader.opposite_rays(reader.names(prefixes=prefixes),guest_origin(p,z+height),axis)
                    row.update(method='Opposed rays to named evaluated structural/lining faces. Drawing XY only seeds rays; ray intersections determine the measurement. Furnishings and decorative ashlar excluded.',endpoint_evidence='C inferred room-label axis and finished-face interpretation from existing guest audit; not explicit surveyed extension endpoints.')
                elif key in ('GUEST_POOL_LENGTH','GUEST_POOL_WIDTH'):
                    axis=0 if key.endswith('LENGTH') else 1
                    water=reader.names(exact=['GUEST_POOL_water'])
                    center=[(reader.extreme(water,a,'min')['coordinate_m']+reader.extreme(water,a,'max')['coordinate_m'])/2 for a in (0,1)]
                    z=reader.extreme(reader.names(exact=['GUEST_L1_MAIN_FLOOR']),2,'max')['coordinate_m']
                    ends=reader.opposite_rays(reader.names(prefixes=['GUEST_POOL_shell_']),(*center,z),axis)
                    row.update(feature_category='pool',method='Opposed rays to actual pool inner shell faces below water skin. Pool is not counted as a building door/window opening.',endpoint_evidence='A clear inner-shell correspondence to printed pool dimensions')
                elif key=='GUEST_POOL_OUTER_WIDTH':
                    axis=0;names=reader.pool_coping_names()
                    ends=[reader.extreme(names,axis,side) for side in ['min','max']]
                    row.update(feature_category='pool',method='Actual outer coping ring X extrema, matched to printed pool exterior horizontal chain.')
                elif key in GUEST_HEIGHTS or key=='GUEST_POOL_TOP':
                    axis=2
                    names=reader.pool_coping_names() if key=='GUEST_POOL_TOP' else reader.names(prefixes=GUEST_HEIGHTS[key])
                    ends=[reader.extreme(reader.names(exact=['GUEST_L1_MAIN_FLOOR']),axis,'max'),reader.extreme(names,axis,'max')]
                    row.update(feature_category='elevation',method='Actual selected mesh top Z minus actual guest main slab top Z. This is a local guest datum, not a measured cross-building height.')
                if ends is None:
                    prior=historical.get(key,{})
                    reason=prior.get('not_run_reason') or prior.get('method') or 'No validated source-to-mesh selector.'
                    # Historical main-only limitations do not disappear merely because site is now loaded.
                    row['not_run_reason']=reason+' Full-scene presence alone does not establish source endpoint identity.'
                else:
                    actual=abs(ends[1]['point_m'][axis]-ends[0]['point_m'][axis]);delta=actual-reference
                    numeric='PASS' if max(abs(delta),row.get('max_sampled_abs_error_m',0))<=tolerance else 'FAIL'
                    row.update(actual_mesh_m=actual,delta_m=delta,numeric_result=numeric,endpoints=ends,
                               within_source_reading_uncertainty=abs(delta)<=unc if unc is not None else None)
                    reviewed=qualify(row,nominal_reviews)
                    if reviewed:
                        row.update(nominal_target_review=reviewed,
                                   source_reading_uncertainty_m=None,
                                   source_reading_status='UNAMBIGUOUS_VERIFIED_GLYPH_NUMERIC_UNCERTAINTY_NOT_QUANTIFIED',
                                   uncertainty_exceeds_tolerance=None,
                                   within_source_reading_uncertainty=None,
                                   endpoint_evidence='Independently verified nominal target: '+reviewed['endpoint_basis'])
                    row['standard_result']='FAIL' if numeric=='FAIL' else ('PASS' if reviewed else ('SOURCE_PRECISION_LIMIT' if unc is None or row['uncertainty_exceeds_tolerance'] else 'PASS'))
            except (ValueError,KeyError,IndexError) as exc:
                row['not_run_reason']='Actual mesh selector failed: '+str(exc)
            rows.append(row)
    measured=[r for r in rows if r['actual_mesh_m'] is not None]
    if len({r['id'] for r in rows}) != len(rows):
        raise ValueError('Duplicate source anchor IDs; cannot count independent anchors')
    coverage={}
    for category in ['main','guest','elevation','cantilever','openings','connections','site']:
        selected=[r for r in measured if (r['building'].lower()==category if category in ('main','guest') else r['feature_category']==category)]
        coverage[category]={'measured_ids':[r['id'] for r in selected],
                           'numeric_pass_ids':[r['id'] for r in selected if r['numeric_result']=='PASS'],
                           'standard_pass_ids':[r['id'] for r in selected if r['standard_result']=='PASS'],
                           'coverage':'PRESENT' if selected else 'MISSING'}
    reasons={'cantilever':'No source-labeled support-face to free slab-edge projection selector is established; overall room/pool spans and roof Z do not measure cantilever length.',
             'openings':'No source-labeled door/window clear width or height selector is established. Navigation clearances and pool dimensions are not dimension-label opening anchors.',
             'connections':'No source-labeled stair/link span, rise or shared main-to-guest benchmark is established. Guest local level differences do not validate its estimated world datum.',
             'site':'No source-labeled bridge/retaining/creek station pair is established. Main chain site portions remain unresolved despite their meshes being present.'}
    for cat,reason in reasons.items():
        if coverage[cat]['coverage']=='MISSING':coverage[cat]['missing_reason']=reason
    pool_rows=[r for r in measured if r['id'].startswith('GUEST_POOL_')]
    coverage['site'].update(coverage='PARTIAL_POOL_ONLY',measured_ids=[r['id'] for r in pool_rows],
                           numeric_pass_ids=[r['id'] for r in pool_rows if r['numeric_result']=='PASS'],
                           standard_pass_ids=[r['id'] for r in pool_rows if r['standard_result']=='PASS'],
                           scope='Pool basin/coping only. Bridge, retaining, terrain and building-registration measurements remain missing.')
    ledger=root/'dimensions.csv';previous=qa/(prefix+'-previous.csv')
    if write_csv and ledger.exists() and not previous.exists():previous.write_bytes(ledger.read_bytes())
    report={'schema_version':2,'scene_path':str(scene_path),'scene_sha256':scene_hash,
            'blender_version':bpy.app.version_string,'scene_modified':False,'rendered':False,
            'method':'Fresh evaluated world-space mesh extrema and face-ray intersections in the loaded frozen integrated scene; data model_m/model_value_m and historical actual values are never measurement inputs.',
            'tolerance_rule':'GEO-02 max(0.020m,0.005*reference_m); a verified printed nominal target is distinct from graphical reading uncertainty and unknown absolute survey accuracy. No tolerance changes.',
            'numeric_counts':dict(Counter(r['numeric_result'] for r in rows)),
            'standard_counts':dict(Counter(r['standard_result'] for r in rows)),
            'independently_measured_anchor_count':len(measured),'minimum_20_numeric_count_met':len(measured)>=20,
            'category_coverage':coverage,'geo02_overall':'INCOMPLETE',
            'overall_reasons':['Count does not substitute for category coverage. Missing categories: '+', '.join(k for k,v in coverage.items() if v['coverage']=='MISSING')+'; site has pool-only partial coverage.','SOURCE_PRECISION_LIMIT rows are numeric agreement only, not GEO-02 standard passes.','Room-label face/axis interpretations remain explicitly C; mesh measurement cannot prove archival semantic precision.','Category counts overlap. Pool inner/outer anchors have distinct labels but correlated construction/calibration; repeated audit versions are not extra anchors.'],
            'data_sha256':{str(p.relative_to(root)):sha(p) for p in [root/'data/main_house.json',root/'data/guest_house.json',root/'config.json',root/'data/dimension-target-reviews.json',extra_path] if p.exists()},
            'selector_script_sha256':sha(Path(__file__)),
            'nominal_review_helper_sha256':sha(Path(__file__).with_name('nominal_targets.py')),
            'documented_empty_coping_segments':reader.empty_coping_segments,
            'previous_csv':{'path':str(previous),'sha256':sha(previous)} if previous.exists() else None,
            'measurements':rows}
    (qa/(prefix+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    if write_csv:
        fields=['component_id','source','original','original_unit','meters','method','uncertainty_m','source_recorded_uncertainty_m','survey_absolute_accuracy_m','nominal_target_review','model_m','difference_m','evidence','numeric_result','standard_result','tolerance_m','source_precision_exceeds_tolerance','building','feature_category','scene_sha256','mesh_selector_evidence','notes']
        with ledger.open('w',newline='',encoding='utf-8-sig') as f:
            writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
            for r in rows:
                writer.writerow(dict(component_id=r['id'],source=r['source'],original=r['source_label'],original_unit='feet/inches',meters=r['reference_m'],method=r['method'] or 'NOT_RUN',uncertainty_m=r['source_reading_uncertainty_m'],source_recorded_uncertainty_m=r['source_recorded_uncertainty_m'],survey_absolute_accuracy_m=r['survey_absolute_accuracy_m'],nominal_target_review=r['nominal_target_review']['review_report'] if r['nominal_target_review'] else '',model_m=r['actual_mesh_m'],difference_m=r['delta_m'],evidence=r['label_evidence']+' label; '+r['endpoint_evidence'],numeric_result=r['numeric_result'],standard_result=r['standard_result'],tolerance_m=r['tolerance_m'],source_precision_exceeds_tolerance=r['uncertainty_exceeds_tolerance'],building=r['building'],feature_category=r['feature_category'],scene_sha256=scene_hash,mesh_selector_evidence=json.dumps(r['endpoints'],ensure_ascii=False,separators=(',',':')),notes=r['not_run_reason'] or ('Verified nominal drawing-target comparison; absolute survey accuracy UNKNOWN.' if r['nominal_target_review'] else 'Numeric mesh comparison only; see category coverage and source precision in audit report.')))
    return report


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',required=True);parser.add_argument('--scene',required=True)
    parser.add_argument('--prefix',default='dimensions-iteration05');parser.add_argument('--expected-sha256')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    bpy.ops.wm.open_mainfile(filepath=args.scene)
    report=audit_dimensions(args.root,scene_path=args.scene,prefix=args.prefix,expected_sha256=args.expected_sha256)
    print(json.dumps({k:report[k] for k in ['scene_sha256','numeric_counts','standard_counts','independently_measured_anchor_count','geo02_overall']},indent=2))


if __name__=='__main__':main()
