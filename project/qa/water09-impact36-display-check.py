"""Reopen display scene and compare native evaluation at1/18/36; never render/save."""
import json,hashlib
from pathlib import Path
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'qa';d=json.loads((P/'water09-impact36-display.json').read_text(encoding='utf-8'));r=json.loads((P/'water09-impact36.json').read_text(encoding='utf-8'));path=Path(d['output'])
assert hashlib.sha256(path.read_bytes()).hexdigest()==d['output_sha256'];bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;obj=s.objects[d['native_domain']];assert s.camera.name=='CAM_WATER_FOOT' and not obj.hide_render
assert all(s.objects[name].hide_render for name in d['hidden_previous_water_or_sim_objects']);rows=[]
for f in (1,18,36):
 s.frame_set(f);bpy.context.view_layer.update();ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();counts={p.settings.type:len(p.particles) for p in ev.particle_systems};want=r['frames'][f-1]
 assert len(me.vertices)==want['mesh_vertices']
 assert counts=={p['type']:p['count'] for p in want['particle_systems']},(f,counts)
 rows.append({'frame':f,'native_mesh_vertices':len(me.vertices),'particle_counts':counts,'matches_local_native_cache':True});ev.to_mesh_clear()
assert hashlib.sha256(path.read_bytes()).hexdigest()==d['output_sha256'];result={'status':'REOPEN_EVALUATED1_18_36_PASS_NOT_RENDERED','display_sha256':d['output_sha256'],'frames':rows,'old_water_hidden':True,'camera':'CAM_WATER_FOOT','bakes':0,'renders':0,'saves':0}
(P/'water09-impact36-display-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print('DISPLAY09_CHECK',json.dumps(result),flush=True)
