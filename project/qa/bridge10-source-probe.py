"""Read-only source09 bridge identity, retained support and source registration."""
import bpy,json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'qa'))
import shrub08_auditlib as audit
source=ROOT/'scene/Fallingwater_iteration09.blend';sha=hashlib.sha256(source.read_bytes()).hexdigest()
assert sha=='489b05e403aa9d02c3568a8e3813a24235ee5b7e782df4d1f149b3ff6673e331'
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.scene.frame_set(48)
rows=[]
for obj in bpy.context.scene.objects:
    if not obj.name.startswith(('SITE_Bridge_','SITE_BearRun_Bridge_','SITE_Path_bridge_')):continue
    rows.append({'name':obj.name,'bounds_xyz_pairs':audit.bounds(obj),'materials':[m.name for m in obj.data.materials],
                 'matrix':[list(r) for r in obj.matrix_world],'vertices':len(obj.data.vertices),'polygons':len(obj.data.polygons),
                 'modifiers':[(m.name,m.type) for m in obj.modifiers],
                 'replace':obj.name.startswith('SITE_Bridge_Parapet_')})
raw=(ROOT/'qa/tour-path-route-iteration09-attempt01.json').read_bytes();route=json.loads(raw)
assert route['source_scene_sha256']==sha
(ROOT/'qa/bridge10-frozen-route09.json').write_bytes(raw)
report={'source_sha256':sha,'frame':48,'bridge_objects':rows,
        'exact_replace_names':[r['name'] for r in rows if r['replace']],
        'retain_names':[r['name'] for r in rows if not r['replace']],
        'route_sha256':hashlib.sha256(raw).hexdigest(),'rendered':False,'scene_saved':False}
(ROOT/'qa/bridge10-source-probe.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('BRIDGE10_SOURCE',json.dumps({'replace_count':len(report['exact_replace_names']),'retain_count':len(report['retain_names']),
      'non_flags':[r for r in rows if not r['name'].startswith(('SITE_Bridge_Flag_','SITE_Bridge_Parapet_'))]}),flush=True)
