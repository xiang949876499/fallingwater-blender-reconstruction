"""Read-only independent frozen-scene review. Does not import repair helpers."""
import bpy, sys, json, hashlib, time, math
from pathlib import Path
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'scripts'),str(R/'qa')]
import shrub08_auditlib as audit
import dimension_supplement12 as dimensions
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
CASE=args[0] if args else '12a'
assert CASE in ('12a','12b')
PREFIX='terrace12-independent' if CASE=='12a' else 'terrace12-independent-12b'
CASES=[('before','Fallingwater_navigation_candidate11a.blend','d66ded0f23b7d19c20b81d2f59f94aa5aa77747be4568e85e1d105395fc219ff'),
       ('after','Fallingwater_terrace_interface_candidate'+CASE+'.blend',{'12a':'0499c4594e4143ebc8ae28735417ae17765e1ffdafe20285903f654768958fa1','12b':'285ea6d0c29b0ff483fb6f582c644f5286b23e83f1d894bedf32546fbca3a14c'}[CASE])]
TARGETS=['MAIN_L2_TERRACE_W_slab','MAIN_L2_TERRACE_S_slab']
NAMES=TARGETS+['MAIN_L2_west_parapet_0','MAIN_L2_south_parapet_0','MAIN_L2_TERRACE_W_finish','MAIN_L2_TERRACE_S_finish','MAIN_floor_threshold_dressing_terrace','MAIN_floor_threshold_dressing_terrace_finish','MAIN_floor_threshold_master_terrace','MAIN_floor_threshold_master_terrace_finish']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def serial(x):return json.loads(json.dumps(x))
def geometry(o):
    e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();m.calc_loop_triangles()
    v=[list(e.matrix_world@p.co) for p in m.vertices]
    f=[list(p.vertices) for p in m.polygons];t=[list(p.vertices) for p in m.loop_triangles]
    edges=Counter(tuple(sorted((a,b))) for p in f for a,b in zip(p,p[1:]+p[:1]))
    volume=sum(Vector(v[a]).dot(Vector(v[b]).cross(Vector(v[c])))/6 for a,b,c in t)
    out={'vertices':v,'polygons':f,'triangles':t,'volume_m3':volume,'edge_degree_counts':dict(Counter(edges.values())),
         'degenerate_triangle_count':sum((Vector(v[b])-Vector(v[a])).cross(Vector(v[c])-Vector(v[a])).length<1e-10 for a,b,c in t),
         'bounds':[[min(p[k] for p in v),max(p[k] for p in v)] for k in range(3)],'modifiers':[(x.name,x.type,audit.props(x)) for x in o.modifiers]}
    e.to_mesh_clear();return out
def tree(g):return BVHTree.FromPolygons([Vector(v) for v in g['vertices']],g['polygons'])
def hit(b,origin,direction):
    p,n,f,d=b.ray_cast(Vector(origin),Vector(direction),80)
    return None if p is None else {'point':list(p),'normal':list(n),'polygon':f,'distance_m':d}
def diff(a,b,path=''):
    if type(a)!=type(b):return [path]
    if isinstance(a,dict):
        out=[]
        for k in set(a)|set(b):
            if k not in a or k not in b:out.append(path+'/'+str(k))
            else:out+=diff(a[k],b[k],path+'/'+str(k))
        return out
    if isinstance(a,list):
        if len(a)!=len(b):return [path+'/length']
        out=[]
        for i,(x,y) in enumerate(zip(a,b)):out+=diff(x,y,path+'/'+str(i))
        return out
    return [] if a==b else [path]
records=[];snapshots=[];start=time.monotonic()
for label,filename,expected in CASES:
    path=R/'scene'/filename;assert sha(path)==expected
    bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update()
    print('INDEPENDENT12_EXTRACT',label,flush=True)
    geoms={name:geometry(bpy.context.scene.objects[name]) for name in NAMES}
    (R/'qa'/f'{PREFIX}-{label}-geometry.json').write_text(json.dumps(geoms),encoding='utf8')
    measure=dimensions.measure(bpy.context.scene)
    rays=[]
    for part,wall in [('W','MAIN_L2_west_parapet_0'),('S','MAIN_L2_south_parapet_0')]:
        slab='MAIN_L2_TERRACE_'+part+'_slab';wt=tree(geoms[wall]);st=tree(geoms[slab])
        box=geoms[wall]['bounds']
        # Same physical outward-face profiles in both cases, including the bottom bevel.
        for axis,sgn in [(0,-1),(1,-1),(1,1)] if part=='W' else [(0,-1),(0,1),(1,-1)]:
            other=1-axis
            for u in [.03,.15,.5,.85,.97]:
                for z in [2.625,2.63,2.635,2.65,2.72,2.80,2.84]:
                    o=[0.,0.,z];o[axis]=box[axis][0]-1 if sgn==-1 else box[axis][1]+1;o[other]=box[other][0]+u*(box[other][1]-box[other][0]);d=[0.,0.,0.];d[axis]=-sgn
                    a=hit(st,o,d);b=hit(wt,o,d)
                    rays.append({'part':part,'origin':o,'direction':d,'slab':a,'parapet':b,
                                 'coincident_m':None if a is None or b is None else abs(a['distance_m']-b['distance_m'])})
    print('INDEPENDENT12_SNAPSHOT',label,flush=True);snap=serial(audit.snapshot());snapshots.append(snap)
    rec={'label':label,'scene':str(path),'source_sha256':expected,'read_only_file_hash_unchanged':sha(path)==expected,
         'geometry_file':f'{PREFIX}-{label}-geometry.json','dimensions':measure,'outer_face_rays':rays,
         'snapshot_sha256':audit.digest(snap),'object_count':len(snap['objects'])}
    records.append(rec)
    (R/'qa'/f'{PREFIX}-{label}-extract.json').write_text(json.dumps(rec,indent=2),encoding='utf8')
before,after=snapshots
changes=diff(before,after)
allowed=[];unexpected=[]
for p in changes:
    ok=False
    if p=='/global/scene/custom_properties/terrace12_slab_interface':ok=True
    for name in TARGETS:
        if p in ['/objects/'+name+'/data_hash','/objects/'+name+'/properties/data/1','/objects/'+name+'/properties/custom_properties/terrace12_slab_interface']:ok=True
        if p.startswith('/objects/'+name+'/properties/dimensions/'):ok=True
        for meshname in [before['objects'][name]['properties']['data'][1],after['objects'][name]['properties']['data'][1]]:
            if p=='/meshes/'+meshname:ok=True
    (allowed if ok else unexpected).append(p)
out={'cases':[{k:v for k,v in x.items() if k not in ('outer_face_rays','dimensions')} for x in records],
     'all_snapshot_differences':changes,'explicit_allowed_differences':allowed,'unexpected_snapshot_differences':unexpected,
     'non_target_objects_exact':all(before['objects'][n]==after['objects'].get(n) for n in before['objects'] if n not in TARGETS),
     'object_sets_identical':set(before['objects'])==set(after['objects']),
     'materials_exact':before['global']['materials']==after['global']['materials'],
     'camera_objects_exact':all(before['objects'][n]==after['objects'].get(n) for n in before['objects'] if n.startswith('CAM_')),
     'action_keyframes_exact':before['global']['actions']==after['global']['actions'],'seconds':time.monotonic()-start,'rendered':False,'saved':False}
(R/'qa'/f'{PREFIX}-extract.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print('INDEPENDENT12_EXTRACT_RESULT',json.dumps(out),flush=True)
