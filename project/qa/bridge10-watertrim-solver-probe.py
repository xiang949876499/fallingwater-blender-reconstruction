import bpy,bmesh,sys,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'qa'))
import bridge10_watertrim_auditlib as t
S=ROOT/'scene/Fallingwater_bridge10_endfix.blend'
bpy.ops.wm.open_mainfile(filepath=str(S));w=bpy.data.objects['WATER_BearRun_Continuous_Upstream_Downstream'];bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
orig=t.evaluate(w);cores={s:t.exact_core(bpy.data.objects['SITE_Bridge10_Stone_Return_'+s],n) for s,n in [('SW',58),('SE',54)]};samples=t.shore_samples(orig,cores)
r={'original':orig['quality'],'triangulation':[],'masks':[],'frames':[],'rendered':False}
tri=w.modifiers.new('probe exact quad tessellation','TRIANGULATE')
for mode in ['FIXED','BEAUTY','SHORTEST_DIAGONAL','LONGEST_DIAGONAL','FIXED_ALTERNATE']:
 tri.quad_method=mode;bpy.context.view_layer.update();d=t.evaluate(w)
 # Geometry of retained original surface, not topology/order.
 checks=t.shore_compare([dict(p,kind='WET_CHANNEL') for p in samples],d)
 r['triangulation'].append({'mode':mode,'max_height_error':checks['max_retained_wet_height_error_m'],'failures':len(checks['failures'])})
 print('TRI_MODE',r['triangulation'][-1],flush=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scene/Fallingwater_bridge10_watertrim.blend'));w=bpy.data.objects['WATER_BearRun_Continuous_Upstream_Downstream']
for name in ['WATERTRIM10_SW_Actual_Masonry_Union','WATERTRIM10_SE_Actual_Masonry_Union']:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data)
 bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY')
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
 bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.000001)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
 r['masks'].append({'name':name,'quality':t.evaluate(o)['quality']});print('CLEAN_MASK',json.dumps(r['masks'][-1]),flush=True)
mods=[m for m in w.modifiers if m.type=='BOOLEAN'];r['solver_enums']=list(mods[0].bl_rna.properties['solver'].enum_items.keys());print('SOLVERS',r['solver_enums'],flush=True)
tri=w.modifiers.new('Preserve original water surface triangulation','TRIANGULATE');tri.quad_method=min(r['triangulation'],key=lambda x:x['max_height_error'])['mode'];w.modifiers.move(len(w.modifiers)-1,1)
for m in mods:m.solver='EXACT';m.use_self=False
for frame in [1,24]:
 st=time.monotonic();bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();d=t.evaluate(w)
 checks=t.shore_compare(samples,d) if frame==1 else None
 r['frames'].append({'frame':frame,'seconds':time.monotonic()-st,'quality':d['quality'],'shore_at_1':checks})
 print('MANIFOLD',frame,json.dumps({'quality':d['quality'],'shore_fail':len(checks['failures']) if checks else None,'s':r['frames'][-1]['seconds']}),flush=True)
(ROOT/'qa/bridge10-watertrim-solver-probe.json').write_text(json.dumps(r,indent=2),encoding='utf8')
