"""Regenerate terrain then _geology with the real module seed in a fresh process."""
import bpy,sys,json,hashlib,struct,random,importlib.util
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from materials import build_materials
from fwlib import collection
spec=importlib.util.spec_from_file_location('fw_site',ROOT/'scripts/site.py')
site=importlib.util.module_from_spec(spec);spec.loader.exec_module(site)
# This script is launched only in factory-startup, never in a user's open scene.
for obj in list(bpy.data.objects):bpy.data.objects.remove(obj,do_unlink=True)
cfg=json.loads((ROOT/'data/site.json').read_text(encoding='utf8'))
ctx=SimpleNamespace(root=ROOT,config=json.loads((ROOT/'config.json').read_text(encoding='utf8')),mats=build_materials(),collection=collection)
cfg.update(ctx.config.get('site',{}));site._resolve_guest(ctx,cfg);site._resolve_main(ctx,cfg)
cfg['_terrain_river_path']=list(reversed(cfg.get('river_upstream_extension',[])[1:]))+cfg['river_path']
assert cfg['core_bedrock_revision']=='discontinuous_beds_v3'
rng=random.Random(cfg['seed']);coll=collection('10_SITE')
# Exact preceding site module entry: terrain consumes the same rng instance.
site._terrain(ctx,cfg,rng,coll);count=site._geology(ctx,cfg,rng,coll)
expected=json.loads((ROOT/'qa/core-geology-candidate07c-check.json').read_text(encoding='utf8'))
results=[]
for g in expected['geometry']:
    o=bpy.data.objects[g['object']];h=hashlib.sha256()
    for v in o.data.vertices:h.update(struct.pack('<3f',*(o.matrix_world@v.co)))
    for p in o.data.polygons:
        h.update(struct.pack('<I',len(p.vertices)))
        for i in p.vertices:h.update(struct.pack('<I',i))
    actual=h.hexdigest();results.append({'object':o.name,'world_geometry_sha256':actual,'expected_sha256':g['mesh_sha256'],'equal':actual==g['mesh_sha256']})
report={'status':'PASS_FRESH_GEOMETRY_REPRODUCTION' if all(r['equal'] for r in results) else 'FAIL',
        'source_candidate_sha256':expected['candidate_sha256'],'site_config_sha256':hashlib.sha256((ROOT/'data/site.json').read_bytes()).hexdigest(),
        'site_script_sha256':hashlib.sha256((ROOT/'scripts/site.py').read_bytes()).hexdigest(),
        'enabled_revision':cfg['core_bedrock_revision'],'objects':results,'geology_objects':count,
        'scope':'Fresh factory-startup executes the exact site terrain -> geology order and RNG. Forest/bridge/water routines after geology are omitted because they cannot change these three meshes. No previous blend geometry used, no render or save.'}
(ROOT/'qa/core-geology07c-fresh-module-reproduction.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report,indent=2),flush=True)
assert report['status']!='FAIL'
