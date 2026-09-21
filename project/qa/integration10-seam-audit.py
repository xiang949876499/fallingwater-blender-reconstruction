"""Independent fresh-process audit of cross-owner Master/Bath interfaces."""
from pathlib import Path
import bpy, json, math, sys, hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'scene/Fallingwater_integration_candidate10a.blend'
out=ROOT/'qa/integration10-seam-audit.json'
assert not out.exists(), 'Retain old test evidence'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=4
dg=bpy.context.evaluated_depsgraph_get()
floor_names=['MAIN_L2_MASTER_finish','MAIN_L2_BATH_M_finish']
floor_names += [o.name for o in scene.objects if 'master_bath' in o.name.lower() and 'threshold' in o.name.lower()]
floor_names=sorted(set(n for n in floor_names if n in scene.objects))
# Record actual naming rather than assuming a missed threshold is harmless.
floor_candidates=[o.name for o in scene.objects if 'master_bath' in o.name.lower() or 'bath_m' in o.name.lower() and 'finish' in o.name.lower()]
surfaces={}
for ob in scene.objects:
    if ob.type!='MESH':continue
    if not ('finish' in ob.name.lower() or 'threshold' in ob.name.lower()):continue
    cc=[ob.matrix_world@Vector(v) for v in ob.bound_box]
    if max(v.x for v in cc)<4.4 or min(v.x for v in cc)>5.3 or max(v.y for v in cc)<7 or min(v.y for v in cc)>9.8:continue
    ev=ob.evaluated_get(dg);m=ev.to_mesh()
    surfaces[ob.name]=BVHTree.FromPolygons([ev.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons],epsilon=0)
    ev.to_mesh_clear()
z=2.8668;rows=[]
for purpose,y0,y1 in [('new_door',7.22,7.90),('former_notch',8.30,9.20)]:
    for iy in range(19):
        y=y0+(y1-y0)*iy/18
        for ix in range(31):
            # The old notch must be repaired only in the Master floor. The new
            # door test spans the two true faces and the joining threshold.
            x=(4.56+(5.04-4.56)*ix/30) if purpose=='new_door' else (4.60+(4.73-4.60)*ix/30)
            hits=[]
            for name,bvh in surfaces.items():
                p,n,index,distance=bvh.ray_cast(Vector((x,y,z+.008)),Vector((0,0,-1)),.02)
                if p is not None and abs(p.z-z)<.004 and n.z>.9:hits.append({'name':name,'z':p.z})
            rows.append({'purpose':purpose,'xy':[x,y],'hits':hits,'status':'PASS' if len(hits)==1 else 'FAIL'})
result={'scene':str(source),'scene_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'status':'PASS' if all(r['status']=='PASS' for r in rows) else 'FAIL',
        'sample_count':len(rows),'failed_samples':[r for r in rows if r['status']!='PASS'],
        'surface_objects':list(surfaces),'name_diagnostics':floor_candidates,
        'method':'Independent evaluated surface rays; 8mm above expected finish,4mm floor tolerance, exact one-hit ownership',
        'scope':'Only Master/Bath common door seam and repaired old notch; full navigation tested separately',
        'all_samples':rows}
out.write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps({k:result[k] for k in ('status','sample_count','scene_sha256')}),flush=True)
print('FAILED',json.dumps(result['failed_samples'][:6]),flush=True)
if result['status']!='PASS':raise RuntimeError('Cross-owner seam audit failed; evidence retained')
