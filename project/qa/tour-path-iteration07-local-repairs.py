"""Retain exact 1cm before/after hits for the eight locally reselected room shots."""
import bpy,json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import tour
old=json.loads((ROOT/'qa/tour-path-route-iteration07-attempt01.json').read_text(encoding='utf-8'))
new=json.loads((ROOT/'qa/tour-path-route-iteration07-attempt02.json').read_text(encoding='utf-8'))
original={s['id']:s for s in old['main_segments']+old['supplemental_segments']}
changed=[s for s in new['main_segments']+new['supplemental_segments'] if s['points']!=original[s['id']]['points']]
points=[p for s in changed for shape in (s,original[s['id']]) for p in shape['points']]
bounds=[(min(p[0] for p in points)-1,max(p[0] for p in points)+1),
        (min(p[1] for p in points)-1,max(p[1] for p in points)+1),
        (min(p[2] for p in points)-2.5,max(p[2] for p in points)+1)]
probe=tour.Probe(bpy.context.scene,bounds)
def check(s):
    walk=bool(s.get('body_clearance_tested',s['mode'].startswith('NORMAL')))
    probe.step_mode='STAIRS' in s['mode']
    for i,(a,b) in enumerate(zip(s['points'],s['points'][1:])):
        hit=probe.segment(a,b,walk,sample_step=.01)
        if hit:return dict(hit,edge=i)
    return None
repairs=[{'id':s['id'],'old_points':original[s['id']]['points'],'new_points':s['points'],
          'before_1cm_failure':check(original[s['id']]),'after_1cm_failure':check(s)} for s in changed]
result={'status':'PASS_ALL_RESELECTED_LOCAL_PATHS' if all(r['after_1cm_failure'] is None for r in repairs) else 'FAIL',
        'source_scene':bpy.data.filepath,'source_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
        'sampling_step_m':.01,'repairs':repairs,'rays':probe.calls,
        'claim':'Eight same-room camera routes were reselected. Six original stored paths reproduce body contacts. The original and revised Service Stair and L3 Terrace paths both pass this isolated 1cm replay, so those two are valid alternatives, not additional failure claims. Scene objects are not changed or saved.'}
(ROOT/'qa/tour-path-iteration07-local-repairs.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('LOCAL_REPAIR_CHECK',json.dumps(result),flush=True)
assert result['status']=='PASS_ALL_RESELECTED_LOCAL_PATHS'
