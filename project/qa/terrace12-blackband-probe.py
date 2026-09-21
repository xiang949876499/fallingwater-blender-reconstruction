"""Read actual rendered facade ray stacks in source10 and combined11."""
from pathlib import Path
import bpy,json,sys,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
rows=[]
for label,filename in [('before','Fallingwater_iteration10.blend'),('after','Fallingwater_integration_candidate11a.blend')]:
    path=ROOT/'scene'/filename;bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.frame_set(48)
    s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
    bpy.context.view_layer.update();cam=s.objects['CAM_HERO'];dep=bpy.context.evaluated_depsgraph_get()
    trees=[];bounds={}
    for o in s.objects:
        if o.type!='MESH' or not o.name.startswith('MAIN_L2_') or not any(k in o.name for k in ('parapet','rounded_lip','TERRACE')):continue
        e=o.evaluated_get(dep);m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices]
        trees.append((o.name,BVHTree.FromPolygons(v,[tuple(p.vertices) for p in m.polygons]),[p.material_index for p in m.polygons],[x.name if x else None for x in m.materials]))
        bounds[o.name]=[[min(p[k] for p in v),max(p[k] for p in v)] for k in range(3)]
        e.to_mesh_clear()
    frame=cam.data.view_frame(scene=s)
    x0=min(v.x/-v.z for v in frame);x1=max(v.x/-v.z for v in frame)
    y0=min(v.y/-v.z for v in frame);y1=max(v.y/-v.z for v in frame)
    samples=[]
    for x in (510,620,750,840):
      for y in (324,329,333,337,341,345):
        d=cam.matrix_world.to_quaternion()@Vector((x0+(x1-x0)*x/1280,y0+(y1-y0)*(1-y/720),-1)).normalized()
        hits=[]
        for name,bvh,indices,mats in trees:
            origin=cam.matrix_world.translation.copy();travel=0.
            for k in range(6):
                p,n,f,t=bvh.ray_cast(origin,d,100)
                if p is None:break
                distance=(p-cam.matrix_world.translation).length
                hits.append({'object':name,'point':list(p),'normal':list(n),'distance':distance,'face':f,'material':mats[indices[f]] if mats else None})
                origin=p+d*.00001
        samples.append({'pixel':[x,y],'hits':sorted(hits,key=lambda h:h['distance'])})
    rows.append({'label':label,'scene':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bounds':bounds,'samples':samples})
out=ROOT/'qa/terrace12-blackband-probe.json';assert not out.exists();out.write_text(json.dumps(rows,indent=2),encoding='utf8')
print(json.dumps([{'label':r['label'],'samples':len(r['samples'])} for r in rows]),flush=True)
