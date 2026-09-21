"""Actual evaluated mesh validation; immutable guest-only input, no rendering."""
import bpy,json,hashlib,sys,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path('D:/zx/test/project');src=root/'qa/guest-iteration06-module.blend'
bpy.ops.wm.open_mainfile(filepath=str(src));scene=bpy.context.scene
data=json.loads((root/'data/guest_house.json').read_text(encoding='utf-8'));reg=data['registration'];sx,sy=reg['meters_per_pixel'];ox,oy=reg['origin_px'];wx,wy,gz=reg['world_origin']
def p(x,y):return (wx+(x-ox)*sx,wy+(oy-y)*sy)
def ray(q,v,length):
    hit,loc,n,idx,obj,m=scene.ray_cast(bpy.context.evaluated_depsgraph_get(),Vector(q),Vector(v),distance=length)
    return {'hit':obj.name if hit else None,'point':list(loc) if hit else None}
notch=data['pool']['dry_west_notch'];a=Vector(p(*notch['stair_from']));b=Vector(p(*notch['stair_to']));rise=.70485;count=notch['count'];length=(b-a).length
def check_path():
    samples=[]
    n=math.ceil((length+.45)/.05)
    for k in range(n+1):
        along=-.15+(length+.45)*k/n;x=a.x+along;y=a.y
        top=gz if along<=0 else gz+rise*min(count,math.floor(along/length*count)+1)/count
        ground=[];body=[]
        for dx,dy in [(0,0),(-.18,0),(.18,0),(0,-.18),(0,.18)]:
            g=ray((x+dx,y+dy,top+.60),(0,0,-1),1.0)
            g['offset']=[dx,dy];g['status']='PASS' if g['hit'] and abs(g['point'][2]-top)<=rise/count+.015 else 'FAIL';ground.append(g)
            c=ray((x+dx,y+dy,top+.24),(0,0,1),1.51);c['offset']=[dx,dy];c['status']='PASS' if c['hit'] is None else 'FAIL';body.append(c)
        for height in [.30,.9,1.6]:
            for dim in [0,1]:
                q=[x,y,top+height];q[dim]-=.18;direction=[0,0,0];direction[dim]=1
                c=ray(q,direction,.36);c.update(height=height,axis=dim,status='PASS' if c['hit'] is None else 'FAIL');body.append(c)
        samples.append({'point':[x,y,top],'ground':ground,'body':body,'status':'PASS' if all(t['status']=='PASS' for t in ground+body) else 'FAIL'})
    return samples
good=check_path()
# Append the exact obstructing old evaluated source object as a negative control.
with bpy.data.libraries.load(str(root/'scene/Fallingwater_iteration05.blend'),link=False) as (available,target):
    target.objects=['GUEST_POOL_coping_16']
old=target.objects[0];scene.collection.objects.link(old);old.name='QA_OLD_coping_16';bpy.context.view_layer.update()
bad=check_path();bpy.data.objects.remove(old,do_unlink=True);bpy.context.view_layer.update()
roof=next(x for x in data['roofs'] if x['id']=='GUEST_LOW_ARM_ROOF');holes=[]
for i,(x0,y0,x1,y1) in enumerate(roof['openings_px']):
    for tx,ty in [(.5,.5),(.15,.15),(.85,.85)]:
        q=p(x0+(x1-x0)*tx,y0+(y1-y0)*ty);r=ray((*q,gz+1.9),(0,0,1),.6)
        r.update(opening=i,source_px=[x0+(x1-x0)*tx,y0+(y1-y0)*ty],status='PASS' if r['hit'] is None else 'FAIL');holes.append(r)
soffit=[]
for x,y in [(350,455),(400,475),(450,487),(487,475),(550,473),(679,450)]:
    q=p(x,y);r=ray((*q,gz+1.9),(0,0,1),.5);r.update(source_px=[x,y],status='PASS' if r['hit']=='GUEST_LOW_ARM_ROOF' else 'FAIL');soffit.append(r)
roof_ob=scene.objects['GUEST_LOW_ARM_ROOF'];ev=roof_ob.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
roof_bvh=BVHTree.FromPolygons([roof_ob.matrix_world@v.co for v in mesh.vertices],[tuple(f.vertices) for f in mesh.polygons],all_triangles=False);ev.to_mesh_clear()
support=[];outline=[Vector(p(*q)) for q in roof['parapet_polygon']]
for i,a in enumerate(outline):
    b=outline[(i+1)%len(outline)];n=Vector((-(b-a).y,(b-a).x)).normalized()
    for t in [.2,.5,.8]:
        for offset in [-.055,0,.055]:
            q=a+(b-a)*t+n*offset
            hit,normal,face,distance=roof_bvh.ray_cast(Vector((*q,gz+roof['height']+1)),Vector((0,0,-1)),2)
            support.append({'edge':i,'fraction':t,'offset':offset,'xy':list(q),'slab_hit':list(hit) if hit is not None else None,'status':'PASS' if hit is not None else 'FAIL'})
# World-space boundary edges of actual underside and raised parapet for an
# original-plan overlay; coplanar internal triangulation edges are omitted.
lines=[]
for ob in scene.objects:
    if ob.name!='GUEST_LOW_ARM_ROOF' and not ob.name.startswith('GUEST_LOW_ARM_ROOF_parapet_'):continue
    ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();verts=[ob.matrix_world@v.co for v in mesh.vertices]
    faces_by_edge={}
    for f in mesh.polygons:
        for edge in f.edge_keys:faces_by_edge.setdefault(tuple(sorted(edge)),[]).append(f.index)
    for e in mesh.edges:
        ia,ib=e.vertices;aa,bb=verts[ia],verts[ib]
        if ob.name=='GUEST_LOW_ARM_ROOF':
            if abs(aa.z-(gz+roof['height']))>.0002 or abs(bb.z-aa.z)>.0002:continue
            fs=faces_by_edge[tuple(sorted((ia,ib)))];norms=[mesh.polygons[f].normal for f in fs]
            if len(norms)==2 and abs(norms[0].dot(norms[1]))>.9999:continue
        elif abs(aa.z-bb.z)>.0002:continue
        lines.append({'object':ob.name,'world':[list(aa),list(bb)],'px':[[ox+(q.x-wx)/sx,oy-(q.y-wy)/sy] for q in [aa,bb]]})
    ev.to_mesh_clear()
report={'source_scene':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'method':'48mm or denser stair-aware path samples; radius.18m ground5/body5 vertical +6 cross-body rays; exact old coping16 appended as negative control. Roof holes: actual vertical rays through slab+weathering.','pool_path_samples':good,'negative_old_coping_failures':sum(t['status']=='FAIL' for t in bad),'negative_samples':[t for t in bad if t['status']=='FAIL'],'roof_opening_rays':holes,'roof_soffit_rays':soffit,'counts':{'pool_pass':sum(t['status']=='PASS' for t in good),'pool_total':len(good),'roof_hole_pass':sum(t['status']=='PASS' for t in holes),'roof_hole_total':len(holes),'roof_soffit_pass':sum(t['status']=='PASS' for t in soffit),'roof_soffit_total':len(soffit)},'limits':['Module only: scene terrain, furniture, masonry overlay and adjacent main link require root integration retest.','Source roof outside line and setback parapet were independently traced, not camera-fitted. A10 R01 identity remains U.']}
report['parapet_actual_slab_support']=support
report['counts']['parapet_support_pass']=sum(x['status']=='PASS' for x in support)
report['counts']['parapet_support_total']=len(support)
(root/'qa/guest-iteration06-pool-roof.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(root/'qa/guest-iteration06-roof-edges.json').write_text(json.dumps(lines,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report['counts']));print('NEGATIVE_FAIL',report['negative_old_coping_failures'])
for t in good:
    if t['status']=='FAIL':print('PATH_FAIL',json.dumps(t))
