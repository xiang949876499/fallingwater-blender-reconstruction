"""Bounded actual-mesh check of the bridge approach and plunge terrain repair."""
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path
from types import SimpleNamespace
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import tour
spec=importlib.util.spec_from_file_location('fw_site',ROOT/'scripts/site.py')
fw_site=importlib.util.module_from_spec(spec);spec.loader.exec_module(fw_site)
source=ROOT/'scene/Fallingwater_iteration05.blend'
sha=hashlib.sha256(source.read_bytes()).hexdigest()
assert sha=='6bcfee7841c22e8e2b636352cfca79ae94968afb4235fc20cdc57e250ae046ff'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
points=tour.stair_mesh_points(scene,'MAIN_loggia_pool_stair_',True)
bounds=((9,21.5),(5,11),(-4,3))
def check():
    probe=tour.Probe(scene,bounds=bounds);probe.step_mode=True
    result=[]
    for i,(a,b) in enumerate(zip(points,points[1:])):
        a,b=Vector(a),Vector(b)
        count=max(1,math.ceil((b-a).length/.10))
        for j in range(count+1):
            p=a+(b-a)*(j/count)
            issue=probe.point(p,True)
            result.append({'segment':i,'t':j/count,'eye':list(p),'expected_floor':p.z-1.6,'failure':issue})
    return {'samples':result,'sample_count':len(result),'failed_samples':sum(x['failure'] is not None for x in result),
            'full_segment_result':probe.path(points,True),'ray_calls':probe.calls,'scope':'Only the actual named main loggia descending flight; not the complete pool perimeter or all adjacency.'}
before=check()
cfg=json.loads((ROOT/'data/site.json').read_text(encoding='utf8'))
ctx=SimpleNamespace(root=ROOT,config=json.loads((ROOT/'config.json').read_text(encoding='utf8')))
fw_site._resolve_guest(ctx,cfg);fw_site._resolve_main(ctx,cfg)
cfg['_terrain_river_path']=list(reversed(cfg.get('river_upstream_extension',[])[1:]))+cfg['river_path']
terrain=scene.objects['SITE_Continuous_BearRun_Terrain']
assert terrain.matrix_world==__import__('mathutils').Matrix.Identity(4)
changed=[]
for vertex in terrain.data.vertices:
    x,y,z=vertex.co
    # Contains every new cap/blend and both old/new north-approach path envelopes.
    if not (7.0<x<32 and 2.0<y<16.1):continue
    value=fw_site._height(x,y,cfg)
    if abs(value-z)>1e-6:
        changed.append({'vertex':vertex.index,'xy':[x,y],'before':z,'after':value})
        vertex.co.z=value
terrain.data.update()
old=scene.objects['SITE_Path_bridge_north_approach']
material=old.data.materials[0];collection=old.users_collection[0]
bpy.data.objects.remove(old,do_unlink=True)
ctx.mats={'gravel':material}
route=next(x for x in cfg['paths'] if x['name']=='bridge_north_approach')
fw_site._route_mesh(ctx,route,collection)
bpy.context.view_layer.update()
after=check()
output=ROOT/'qa/site-iteration06-candidate.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(output),compress=True)
report={'source_scene':str(source),'source_sha256':sha,'site_config_sha256':hashlib.sha256((ROOT/'data/site.json').read_bytes()).hexdigest(),
        'before':before,'after':after,'terrain_modified_vertices':changed,'modified_objects':['SITE_Continuous_BearRun_Terrain','SITE_Path_bridge_north_approach'],
        'bridge_and_stair_meshes_changed':False,'candidate_scene':str(output),
        'status':'PASS_LOCAL_STAIR' if after['failed_samples']==0 and after['full_segment_result'] is None else 'FAIL',
        'limits':'C landscape alignment and grade repair supported by the open stair in main04. Full site rebuild, plant contact, pool perimeter route and actual rendered views still required.'}
(ROOT/'qa/site-iteration06-check.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print({k:report[k] for k in ['status','candidate_scene']},'before',before['failed_samples'],'after',after['failed_samples'],flush=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
if report['status']=='FAIL':raise RuntimeError('Local stair repair failed; inspect retained candidate and report')
