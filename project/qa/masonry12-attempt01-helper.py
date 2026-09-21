"""Bounded C split-stone finish for the existing upper main west tower.

No global material or structural edits. Native closed components, no booleans.
The 300 old boxes are validated before replacement. This is a candidate,
not a surveyed bond or an accepted photoreal finish.
"""
import bpy, math, json, hashlib, random
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

TARGETS=tuple(f'MAIN_tower_course_course{r:02}_{j:02}_{side}' for r in range(30) for j in range(5) for side in (-1,1))
GUARDS=('MAIN_chimney_cap','MAIN_chimney_flue','MAIN_chimney_flue.001','MAIN_stone_tower_north','MAIN_stone_tower_west')
SOURCE_GEOMETRY='c5012722c9a247748b31b0659ae543640d1818bc7af03801eba984ce6548510d'
NAMESPACE='MASONRY12_Upper_Tower'
X0,X1,Y0,Y1=-.9414,-.2114,8.3898,11.3634
EMBED=.0008
MIN_Z,MAX_Z=5.277,9.439
MAX_DEPTH=.0355

def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def geometry_hash(obj):
    e=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh()
    try:
        d={'v':[[round(c,8) for c in (e.matrix_world@v.co)] for v in m.vertices], 'p':[list(p.vertices) for p in m.polygons]}
        return hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()
    finally:e.to_mesh_clear()

def bounds(obj):
    vs=[obj.matrix_world@Vector(v) for v in obj.bound_box]
    return [[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)]

def overlap(a,b):return all(a[i][0]<=b[i][1] and a[i][1]>=b[i][0] for i in range(3))

def subtract(rect,cut):
    u0,u1,z0,z1=rect;a,b,c,d=cut
    a,b=max(a,u0),min(b,u1);c,d=max(c,z0),min(d,z1)
    if a>=b or c>=d:return [rect]
    return [r for r in ((u0,a,z0,z1),(b,u1,z0,z1),(a,b,z0,c),(a,b,d,z1)) if r[1]-r[0]>=.045 and r[3]-r[2]>=.024]

def face_point(face,u,depth):
    if face=='W':return (X0-depth,u)
    if face=='E':return (X1+depth,u)
    return (u,Y0-depth)

def face_ring(face,u0,u1,rng):
    ring=[face_point(face,u0,-EMBED),face_point(face,u1,-EMBED)]
    for t in (1,.76,.48,.24,0):
        ring.append(face_point(face,u0+(u1-u0)*t,rng.uniform(.018,.0335)))
    return ring

def corner_ring(east,lx,ly,rng):
    dw,ds=rng.uniform(.022,.031),rng.uniform(.022,.031)
    p=[(X0+EMBED,Y0+ly),(X0+EMBED,Y0+EMBED),(X0+lx,Y0+EMBED)]
    for t in (1,.67,.33):p.append((X0+lx*t,Y0-rng.uniform(.019,.033)))
    p.append((X0-dw,Y0-ds))
    for t in (.28,.61,1):p.append((X0-rng.uniform(.019,.033),Y0+ly*t))
    if east:p=[(X1-(x-X0),y) for x,y in p]
    return p

class Batch:
    def __init__(self,name):self.name=name;self.vertices=[];self.faces=[];self.components=[]
    def add(self,ring,z0,z1,rng,description):
        if sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)))<0:ring=list(reversed(ring))
        n=len(ring);off=len(self.vertices);fs=len(self.faces)
        lo=[z0+rng.uniform(0,.0018) for _ in ring];hi=[z1-rng.uniform(0,.0018) for _ in ring]
        mid=z0+(z1-z0)*rng.uniform(.43,.57)
        # Independent top/bottom inward chips; closed angular vertical strata.
        for zz in (lo,[mid]*n,hi):self.vertices.extend((x,y,z) for (x,y),z in zip(ring,zz))
        for layer in range(2):
            for i in range(n):
                j=(i+1)%n;a=off+layer*n+i;b=off+layer*n+j;c=b+n;d=a+n
                self.faces.extend(((a,b,c),(a,c,d)))
        flat=[Vector((x,y,0)) for x,y in ring]
        for t in tessellate_polygon([flat]):
            ids=[next(i for i,v in enumerate(flat) if v==q) for q in t]
            a,b,c=ids
            if (flat[b]-flat[a]).cross(flat[c]-flat[a]).z<0:b,c=c,b
            self.faces.append((off+c,off+b,off+a));self.faces.append((off+2*n+a,off+2*n+b,off+2*n+c))
        self.components.append({'id':description,'vertex_start':off,'vertex_count':3*n,'face_start':fs,'face_count':len(self.faces)-fs,
                                'z_interval':[z0,z1],'footprint':ring,'back_embed_m':EMBED})

def build(ctx):
    scene=bpy.context.scene
    existing=bpy.data.collections.get(NAMESPACE)
    if existing:
        expected=json.loads(existing.get('geometry','{}'))
        if any(n in scene.objects for n in TARGETS) or not expected or set(o.name for o in existing.objects)!=set(expected):raise ValueError('Partial tower12 state')
        if any(geometry_hash(scene.objects[n])!=h for n,h in expected.items()):raise ValueError('Changed tower12 result')
        return {'status':'SKIPPED_ALREADY_APPLIED','objects':sorted(expected)}
    actual={n for n in scene.objects.keys() if n.startswith('MAIN_tower_course')}
    if actual!=set(TARGETS):raise ValueError('Old300 exact tower object set mismatch')
    names=TARGETS+GUARDS
    if any(n not in scene.objects for n in names):raise ValueError('Missing tower guards')
    source={n:geometry_hash(scene.objects[n]) for n in names}
    if digest(source)!=SOURCE_GEOMETRY:raise ValueError('Tower original geometry mismatch')
    if any(tuple(scene.objects[n].scale)!=(1,1,1) for n in names):raise ValueError('Tower scale changed')
    stone=bpy.data.materials.get('FW_stone')
    if stone is None or 'Bump.001' not in stone.node_tree.nodes:raise ValueError('Expected saved stone shader unavailable')
    envelope=[[X0-MAX_DEPTH,X1+MAX_DEPTH],[Y0-MAX_DEPTH,Y1],[MIN_Z,MAX_Z]]
    excluded=set(TARGETS)|{'MAIN_stone_tower_west'}
    constraints=[]
    for o in scene.objects:
        if o.type!='MESH' or o.hide_render or o.name in excluded or not o.name.startswith(('MAIN_','GUEST_','FW_MASONRY_')):continue
        b=bounds(o)
        if overlap(envelope,b):constraints.append({'name':o.name,'bounds':b,'geometry_hash':geometry_hash(o)})
    masks={}
    for face,plane,axis in [('W',X0,0),('E',X1,0),('S',Y0,1)]:
        axis_range=[plane-MAX_DEPTH,plane+EMBED] if face in ('W','S') else [plane-EMBED,plane+MAX_DEPTH]
        masks[face]=[]
        for c in constraints:
            b=c['bounds']
            if b[axis][1]<axis_range[0] or b[axis][0]>axis_range[1]:continue
            u=b[1-axis];z=b[2]
            masks[face].append({'name':c['name'],'cut':[u[0]-.002,u[1]+.002,z[0]-.002,z[1]+.002],
                                'basis':'Conservative projection of actual frozen mesh bounds; subsequent actual-triangle intersection QA required'})
    rng=random.Random(534612)
    nominal=[.058,.129,.041,.091,.172,.066,.113,.047,.088,.145,.053,.101,.038,.157,.074,.119,.044,.083,.137,.061,.097,.048,.168,.078,.109,.043,.092,.151,.056,.124,.039,.087,.163,.071,.106,.046,.134,.063,.098,.052,.142,.081,.117,.049]
    gaps=[rng.uniform(.0065,.0105) for _ in nominal[:-1]]
    factor=(MAX_Z-MIN_Z-sum(gaps))/sum(nominal);heights=[x*factor for x in nominal]
    batches={k:Batch(NAMESPACE+'_'+k) for k in ('W','E','South_Return')};rows=[];trimmed=[]
    z=MIN_Z
    def add_face(face,u0,u1,a,b,identity):
        rects=[(u0,u1,a,b)]
        for m in masks[face]:
            next_rects=[q for r in rects for q in subtract(r,m['cut'])]
            if next_rects!=rects:trimmed.append({'component':identity,'obstacle':m['name']})
            rects=next_rects
        for i,(l,r,low,high) in enumerate(rects):
            batches['South_Return' if face=='S' else face].add(face_ring(face,l,r,rng),low,high,rng,identity+f':part{i}')
    for row,h in enumerate(heights):
        bottom,top=z,z+h;g=.008;lxw,lxe=rng.uniform(.17,.235),rng.uniform(.17,.235)
        lyw,lye=rng.uniform(.28,.56),rng.uniform(.28,.56)
        corners=[('SW',False,lxw,lyw),('SE',True,lxe,lye)]
        for label,east,lx,ly in corners:
            ring=corner_ring(east,lx,ly,rng)
            rb=[[min(p[i] for p in ring),max(p[i] for p in ring)] for i in range(2)]+[[bottom,top]]
            # Corner lives away from protected neighboring walls; reject rather
            # than silently cutting a questionable new wrap around an opening.
            bad=[c['name'] for c in constraints if overlap(rb,c['bounds'])]
            if bad:raise ValueError(('Corner overlaps a protected source bounding volume',label,row,bad))
            batches['South_Return'].add(ring,bottom,top,rng,f'{row:02}:{label}:bonded_L')
        add_face('S',X0+lxw+g,X1-lxe-g,bottom,top,f'{row:02}:S:center')
        for face,leg in [('W',lyw),('E',lye)]:
            u=Y0+leg+g;end=Y1-.006;index=0
            while u<end-.05:
                length=rng.uniform(.38,1.02)
                if end-u-length<.16:length=end-u
                stop=min(end,u+length);split=(h>.11 and (row+index*2)%7==3)
                if split:
                    low=h*rng.uniform(.28,.39);localgap=.0075
                    add_face(face,u,stop,bottom,bottom+low,f'{row:02}:{face}:{index}:packing')
                    add_face(face,u,stop,bottom+low+localgap,top,f'{row:02}:{face}:{index}:thick')
                else:add_face(face,u,stop,bottom,top,f'{row:02}:{face}:{index}')
                u=stop+rng.uniform(.006,.013);index+=1
        rows.append({'row':row,'z0':bottom,'z1':top,'body_height':h,'gap_after':gaps[row] if row<len(gaps) else 0})
        z=top+(gaps[row] if row<len(gaps) else 0)
    count=sum(len(b.components) for b in batches.values());tris=sum(len(b.faces) for b in batches.values())
    if count>560 or tris>40000:raise ValueError(('Budget exceeded',count,tris))
    for b in batches.values():
        if any(not all(envelope[i][0]-1e-6<=v[i]<=envelope[i][1]+1e-6 for i in range(3)) for v in b.vertices):raise ValueError('Finish outside allowed shallow envelope')
    coll=bpy.data.collections.new(NAMESPACE);scene.collection.children.link(coll)
    private=stone.copy();private.name=NAMESPACE+'_Stone';private.node_tree.nodes['Bump.001'].inputs['Distance'].default_value=.006
    private['scope']='Only candidate12 upper tower finish; source PBR is CC0, bond geometry C';private['texture_coordinate_convention']='World metre vertex positions; identity object transform; original2m period'
    new=[]
    for b in batches.values():
        mesh=bpy.data.meshes.new(b.name+'_Mesh');mesh.from_pydata(b.vertices,[],b.faces);mesh.update();mesh.materials.append(private)
        obj=bpy.data.objects.new(b.name,mesh);coll.objects.link(obj);obj['evidence']='C';obj['role']='local upper tower split-stone candidate';obj['source']='HABS PA5346 sections/elevation; official East and Classic photographs; not measured bond'
        new.append(obj)
    # All source validation, design budgets, envelope and corner-volume checks
    # ran before old objects are removed. Original meshes/materials are untouched.
    for n in TARGETS:bpy.data.objects.remove(scene.objects[n],do_unlink=True)
    bpy.context.view_layer.update();coll['geometry']=json.dumps({o.name:geometry_hash(o) for o in new},sort_keys=True)
    return {'status':'CANDIDATE_APPLIED_NOT_VISUALLY_ACCEPTED','removed':list(TARGETS),'guards':{n:source[n] for n in GUARDS},
            'added':[o.name for o in new],'private_material':private.name,'components':{b.name:b.components for b in batches.values()},
            'component_count':count,'triangles':tris,'rows':rows,'actual_source_constraints':constraints,'surface_masks':masks,'trimmed_components':trimmed,
            'allowed_envelope':envelope,'source_geometry_digest':SOURCE_GEOMETRY,'source_core_unchanged':all(geometry_hash(scene.objects[n])==source[n] for n in GUARDS)}
