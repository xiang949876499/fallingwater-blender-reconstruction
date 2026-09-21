import bpy,sys,json,time,numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'qa'))
import bridge10_watertrim_auditlib as t
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scene/Fallingwater_bridge10_endfix.blend'));scene=bpy.context.scene;water=bpy.data.objects['WATER_BearRun_Continuous_Upstream_Downstream']
scene.frame_set(1);bpy.context.view_layer.update();before=t.evaluate(water);cores={s:t.exact_core(scene.objects['SITE_Bridge10_Stone_Return_'+s],n) for s,n in [('SW',58),('SE',54)]};samples=t.shore_samples(before,cores)
keys=water.data.shape_keys.key_blocks
arrays=[]
for k in keys:
 a=np.empty(len(k.data)*3,dtype=np.float32);k.data.foreach_get('co',a);arrays.append(a.reshape(-1,3))
amp=np.sqrt((arrays[1]-arrays[0])**2+(arrays[2]-arrays[0])**2)+.07501
lo,hi=arrays[0]-amp,arrays[0]+amp
sel=(hi[:,0]>=23.20)&(lo[:,0]<=31.46)&(hi[:,1]>=-4.20)&(lo[:,1]<=-2.40)
zmin,zmax=float(lo[sel,2].min()),float(hi[sel,2].max())
print('ALLTIME_Z_ENVELOPE',zmin,zmax,flush=True)
coll=bpy.data.collections.new('Bridge10 physical components probe');scene.collection.children.link(coll);records=[]
for side,n in [('SW',58),('SE',54)]:
 obj=scene.objects['SITE_Bridge10_Stone_Return_'+side];vbase=2*n+2;fbase=3*n;panels=(len(obj.data.vertices)-vbase)//8
 chunks=[('core',0,vbase,0,fbase)]
 for i in range(panels):
  vs=list(obj.data.vertices)[vbase+i*8:vbase+(i+1)*8];zs=[v.co.z for v in vs]
  if max(zs)>=zmin and min(zs)<=zmax:chunks.append((str(i),vbase+i*8,8,fbase+i*8,8))
 for ident,offset,nv,fo,nf in chunks:
  m=bpy.data.meshes.new('mask_'+side+'_'+ident);m.from_pydata([tuple(v.co) for v in list(obj.data.vertices)[offset:offset+nv]],[],[tuple(i-offset for i in p.vertices) for p in list(obj.data.polygons)[fo:fo+nf]])
  mask=bpy.data.objects.new(m.name,m);coll.objects.link(mask);mask.hide_render=True
 records.append({'side':side,'all_panels':panels,'selected_closed_components':len(chunks)})
tri=water.modifiers.new('actual evaluated surface triangulation','TRIANGULATE');tri.quad_method='FIXED';tri.ngon_method='BEAUTY'
mod=water.modifiers.new('difference actual physical components','BOOLEAN');mod.operation='DIFFERENCE';mod.operand_type='COLLECTION';mod.collection=coll;mod.solver='EXACT';mod.use_self=False
r={'components':records,'z_envelope':[zmin,zmax],'frames':[],'rendered':False}
for frame in [1,24]:
 st=time.monotonic();scene.frame_set(frame);bpy.context.view_layer.update();a=t.evaluate(water);shore=t.shore_compare(samples,a) if frame==1 else None
 r['frames'].append({'frame':frame,'quality':a['quality'],'seconds':time.monotonic()-st,'shore':shore})
 print('COMPONENTS_RESULT',frame,json.dumps({'quality':a['quality'],'s':r['frames'][-1]['seconds'],'shore_fail':len(shore['failures']) if shore else None}),flush=True)
(ROOT/'qa/bridge10-watertrim-components-probe.json').write_text(json.dumps(r,indent=2),encoding='utf8')
