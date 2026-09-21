"""Read-only exact formula decomposition; no Blender/model edits or renders."""
import ast
import bisect
import hashlib
import json
import math
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / 'scripts/site.py').read_text(encoding='utf8')
names = {'_inside', '_segment_near', '_river_near', '_height', '_axis', '_resolve_guest', '_resolve_main'}
tree = ast.parse(source)
parts = [ast.get_source_segment(source, n) for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
ns = {'math': math, 'json': json, 'Path': Path}
exec('\n\n'.join(parts), ns)
cfg = json.loads((ROOT / 'data/site.json').read_text(encoding='utf8'))
ctx = SimpleNamespace(root=ROOT, config=json.loads((ROOT / 'config.json').read_text(encoding='utf8')))
cfg.update(ctx.config.get('site', {}))
ns['_resolve_guest'](ctx, cfg)
ns['_resolve_main'](ctx, cfg)
cfg['_terrain_river_path'] = list(reversed(cfg.get('river_upstream_extension', [])[1:])) + cfg['river_path']
height_src = next(p for p in parts if p.startswith('def _height'))
traced = height_src.replace('def _height(', 'def trace(')
traced = traced.replace('    # Wide forested', '    record = {}\n    zone_changes = []\n    path_changes = []\n    # Wide forested', 1)
traced = traced.replace('    dist, t, water_z', "    record['background'] = z\n    dist, t, water_z", 1)
traced = traced.replace('    # Bedrock occupies', "    record['river_carve'] = z\n    record['river'] = {'distance':dist, 'edge':edge, 'water_z':water_z, 'bed':bed, 'segment':i}\n    # Bedrock occupies", 1)
traced = traced.replace('    # Building interiors', "    record['core_cut'] = z\n    # Building interiors", 1)
traced = traced.replace('            z=target*(1-blend)+z*blend', "            prior = z\n            z=target*(1-blend)+z*blend\n            if abs(z-prior)>1e-9:zone_changes.append({'name':zone['name'], 'outside':outside, 'before':prior, 'after':z})", 1)
traced = traced.replace("    for route in cfg['paths']:", "    record['building_cut'] = z\n    record['zones'] = zone_changes\n    for route in cfg['paths']:", 1)
traced = traced.replace('                z = z*(1-w)+rz*w', "                prior=z\n                z = z*(1-w)+rz*w\n                if abs(z-prior)>1e-9:path_changes.append({'name':route['name'], 'distance':d, 'before':prior, 'after':z})", 1)
traced = traced.replace('    # Where a route', "    record['path_blend'] = z\n    record['paths'] = path_changes\n    # Where a route", 1)
traced = traced.replace('    return z', "    record['final'] = z\n    return record", 1)
exec(traced, ns)
axisx = ns['_axis'](cfg['terrain_bounds'][0], cfg['terrain_bounds'][1])
axisy = ns['_axis'](cfg['terrain_bounds'][2], cfg['terrain_bounds'][3])

def point(x, y):
    r = ns['trace'](x, y, cfg)
    assert abs(r['final'] - ns['_height'](x, y, cfg)) < 1e-10
    ix = bisect.bisect_right(axisx, x)-1
    iy = bisect.bisect_right(axisy, y)-1
    x0, x1 = axisx[ix:ix+2]
    y0, y1 = axisy[iy:iy+2]
    u = (x-x0)/(x1-x0)
    v = (y-y0)/(y1-y0)
    z00, z10, z11, z01 = [ns['_height'](a, b, cfg) for a,b in ((x0,y0),(x1,y0),(x1,y1),(x0,y1))]
    # Actual _terrain triangle split: (00,10,11), (00,11,01).
    mesh_z = z00*(1-u)+z10*(u-v)+z11*v if v <= u else z00*(1-v)+z11*u+z01*(v-u)
    return {'xy':[x,y], **r, 'mesh_z':mesh_z, 'formula_minus_mesh':r['final']-mesh_z}

profiles = {}
for name, fixed, lo, hi, mode in (
    ('west_cross_y0',0,-20,-4,'x'), ('west_long_xminus12',-12,-12,12,'y'),
    ('north_bridge_cross_y14',14,18,34,'x'), ('north_bridge_long_x26',26,2,20,'y'),
    ('east_bank_long_x20',20,-18,4,'y'), ('south_cross_yminus11',-11,-5,20,'x')):
    profiles[name] = [point(lo+i*.5,fixed) if mode=='x' else point(fixed,lo+i*.5) for i in range(int((hi-lo)*2)+1)]
probe = json.loads((ROOT / 'qa/bank07-visible-terrain-probe.json').read_text(encoding='utf8'))
visible = []
for camera in probe['cameras']:
    points = []
    for p in camera['visible_points']:
        x,y,z = p['world']
        q=point(x,y)
        q.update(pixel_grid=p['pixel_grid'], actual_prior_BVH_z=z, mesh_minus_BVH=q['mesh_z']-z)
        points.append(q)
    visible.append({'camera':camera['camera'], 'points':points,
                    'mesh_vs_saved_BVH_max_abs':max(abs(p['mesh_minus_BVH']) for p in points)})
out = {'status':'READ_ONLY_CAUSE_DIAGNOSIS_NO_MODEL_CHANGE',
       'site_script_sha256':hashlib.sha256((ROOT/'scripts/site.py').read_bytes()).hexdigest(),
       'site_config_sha256':hashlib.sha256((ROOT/'data/site.json').read_bytes()).hexdigest(),
       'resolved_exclusions':cfg['building_exclusions'], 'profiles':profiles, 'visible_formula_stage_points':visible,
       'limitations':['Existing camera BVH samples were captured from frozen07c; profile interpolation reproduces _terrain triangle split, not a new scene mesh.',
                     'All exact heights describe authored implementation, not surveyed terrain.']}
(ROOT/'qa/bank07b-terrain-cause-probe.json').write_text(json.dumps(out,indent=2),encoding='utf8')
for name, rows in profiles.items():
    print(name)
    for p in rows[::2]:
        print('xy',p['xy'],'z',round(p['mesh_z'],3),'bg',round(p['background'],3),'river',round(p['river_carve'],3),'core',round(p['core_cut'],3),'building',round(p['building_cut'],3),'path',round(p['path_blend'],3), 'zones',','.join(z['name'] for z in p['zones']))
print('saved07c_BVH_max_differences',[(v['camera'],v['mesh_vs_saved_BVH_max_abs']) for v in visible])
