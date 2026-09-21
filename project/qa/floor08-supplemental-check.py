"""Resolve nine fixture-occluded grid samples, and inspect the L3 bath doorway."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
base=json.loads((R/'qa/floor08-candidate-check.json').read_text());out={}
for version,path in [('before',R/'scene/Fallingwater_iteration07.blend'),('after',R/'scene/Fallingwater_floor_candidate08.blend')]:
    bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=640;s.render.resolution_y=360;s.render.resolution_percentage=100;dg=bpy.context.evaluated_depsgraph_get()
    bvhs={}
    for ob in s.objects:
        if ob.type=='MESH' and ob.name.startswith('MAIN_') and ob.name.endswith('_finish'):
            e=ob.evaluated_get(dg);m=e.to_mesh();bvhs[ob.name]=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]);e.to_mesh_clear()
    def surfaces(q):
        vals=[]
        for name,b in bvhs.items():
            p,n,f,dist=b.ray_cast(Vector((q[0],q[1],q[2]+.08)),Vector((0,0,-1)),.16)
            if p is not None and abs(p.z-q[2])<.001:vals.append(name)
        return vals
    cam=s.objects['CAM_MAIN_L3_BATH_B'];co=cam.data.view_frame(scene=s);xmin,xmax=min(v.x for v in co),max(v.x for v in co);ymin,ymax=min(v.y for v in co),max(v.y for v in co);pixels=[]
    for x,y in [(210,337),(216,319),(194,338),(230,350)]:
        d=(cam.matrix_world.to_quaternion()@Vector((xmin+(x+.5)/640*(xmax-xmin),ymax-(y+.5)/360*(ymax-ymin),co[0].z))).normalized()
        hit,p,n,f,ob,_=s.ray_cast(dg,cam.matrix_world.translation,d,distance=100);q=cam.matrix_world.translation+d*((5.28615-cam.matrix_world.translation.z)/d.z)
        pixels.append({'pixel':[x,y],'first':ob.name if hit else None,'point':list(p) if hit else None,'source_px':[q.x/.0524+327,540-q.y/.0531],'surfaces':surfaces(q)})
    out[version]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'l3bath_pixels':pixels}
    if version=='after':
        under=[]
        for r in base['grid']:
            if r['pass_']:continue
            q=(*r['xy'],2.8668);vals=surfaces(q);under.append({'original_first_hit':r,'underlying_finish':vals,'pass_':vals==[r['room']+'_finish']})
        out['fixture_occluded_samples']=under
out['status']='PASS_FLOOR_UNDER_ALL_NINE_FIXTURES' if all(r['pass_'] for r in out['fixture_occluded_samples']) else 'FAIL_FLOOR_UNDER_FIXTURES'
out['limitation']='Original nine whole-scene first-hit differences remain preserved. These direct evaluated floor rays prove support beneath fixtures, not unobstructed walkable positions.'
(R/'qa/floor08-supplemental-check.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
