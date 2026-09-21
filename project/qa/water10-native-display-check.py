"""Reopen display candidate, compare cached geometry/counts at1/24/48. No render/save."""
import json,gzip,struct,importlib.util
from pathlib import Path
import bpy,numpy as np
spec=importlib.util.spec_from_file_location('natural48',Path(__file__).with_name('water10-natural48.py'))
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
r=json.loads((w.P/'water10-native-display.json').read_text(encoding='utf8'));mapping=json.loads((w.P/'water10-native-mapping.json').read_text(encoding='utf8'));affine=np.array(mapping['mesh_world_affine'])
assert w.sha(Path(r['output']))==r['output_sha256'];bpy.ops.wm.open_mainfile(filepath=r['output']);s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4
o=s.objects[r['native_domain']];d=next(m.domain_settings for m in o.modifiers if m.type=='FLUID');assert Path(bpy.path.abspath(d.cache_directory)).resolve()==w.CACHE.resolve()
assert not o.hide_render;assert s.objects[r['camera_primary']].type=='CAMERA'
for record in r['hidden_original_water']:assert s.objects[record['name']].hide_render
for group in [d.fluid_group,d.effector_group]:
 for ob in group.objects:assert ob.hide_render and not ob.hide_viewport
checks=[]
for frame in [1,24,48]:
 s.frame_set(frame);ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles();v=np.array([tuple(o.matrix_world@p.co) for p in me.vertices]);faces=np.array([tuple(t.vertices) for t in me.loop_triangles])
 raw=gzip.decompress((w.CACHE/'mesh'/f'fluid_mesh_{frame:04}.bobj.gz').read_bytes());n=struct.unpack_from('<i',raw,0)[0];rv=np.frombuffer(raw,'<f4',count=n*3,offset=4).reshape(-1,3);offset=4+n*12;nn=struct.unpack_from('<i',raw,offset)[0];offset+=4+nn*12;nf=struct.unpack_from('<i',raw,offset)[0];offset+=4;rf=np.frombuffer(raw,'<i4',count=nf*3,offset=offset).reshape(-1,3)
 expected=np.column_stack((rv,np.ones(n)))@affine;assert len(v)==n and np.array_equal(faces,rf)
 error=float(np.linalg.norm(v-expected,axis=1).max());assert error<2e-6
 counts=[{'type':ps.settings.type,'count':len(ps.particles),'render_type':ps.settings.render_type} for ps in ev.particle_systems]
 checks.append({'frame':frame,'actual_display_vertices':n,'actual_triangles':nf,'max_vertex_error_from_raw_m':error,'particle_systems':counts});ev.to_mesh_clear()
 assert w.h.shape_hash(s.objects['SITE_Core_Continuous_Fractured_Sandstone'])==w.CONFIG['frozen_core_sha256']
assert w.sha(Path(r['output']))==r['output_sha256'];assert w.sha(Path(r['native_source']))==r['native_source_sha256'];assert w.sha(w.SOURCE)==r['full_context_source_sha256']
assert w.manifest()==json.loads((w.P/'water10-natural48-preserved-cache-manifest.json').read_text(encoding='utf8'))
r['reopen_checks']=checks;r['status']='DISPLAY_REOPEN_RAW_GEOMETRY_PASS_NOT_RENDERED_NOT_PRODUCTION'
(w.P/'water10-native-display.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print('WATER10_DISPLAY_REOPEN_PASS',json.dumps(checks),flush=True)
