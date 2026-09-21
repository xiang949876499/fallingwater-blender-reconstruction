"""Candidate-only upper-tower height completion, on frozen accepted-direction12a.

The printed tower top is9.9949m above the main terrace. This candidate explicitly
maps that terrace to the actual visible finish. It does not fix unknown outlet
plan locations, rebuild lower window interfaces, or alter shared materials.
"""
import bpy, hashlib, json, random
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
import masonry_tower12 as base

NAMESPACE = 'MASONRY12b_TopCompletion'
MODIFIED = base.GUARDS
LOWER = tuple(base.NAMESPACE + '_' + s for s in ('W','E','South_Return'))
NOMINAL_M = 9.9949
SOURCE_BLEND_SHA = 'b267636a9cbbe297513968f08f3b85930c0302cae1ebb75ed775043250e11a48'
BASE_HELPER_SHA = 'e71403d89289db9e1ad5efb005a4b86072d7c8ac7d11335426dbec5e082cc391'
X0,X1,Y0,Y1 = base.X0,base.X1,base.Y0,base.Y1

def top(obj):
    e=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh()
    try:return max((e.matrix_world@v.co).z for v in m.vertices)
    finally:e.to_mesh_clear()

class SplitBatch(base.Batch):
    """Only the new upper courses get bounded small angular edge breaks."""
    def add(self, ring, z0, z1, rng, description):
        if sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)))<0:
            ring=list(reversed(ring))
        n=len(ring);off=len(self.vertices);fs=len(self.faces)
        lo=[z0+rng.uniform(0,.004) for _ in ring]
        hi=[z1-rng.uniform(0,.004) for _ in ring]
        mid=z0+(z1-z0)*rng.uniform(.37,.64)
        mr=[]
        for x,y in ring:
            # Keep backing coordinates exact; relief remains in the old35.5mm
            # silhouette allowance. Piece-specific facets, no smooth inflation.
            if x<X0:x=max(X0-.0354,min(X0-.017,x+rng.uniform(-.003,.004)))
            if x>X1:x=min(X1+.0354,max(X1+.017,x+rng.uniform(-.004,.003)))
            if y<Y0:y=max(Y0-.0354,min(Y0-.017,y+rng.uniform(-.003,.004)))
            mr.append((x,y))
        self.vertices.extend((x,y,z) for (x,y),z in zip(ring,lo))
        self.vertices.extend((x,y,mid) for x,y in mr)
        self.vertices.extend((x,y,z) for (x,y),z in zip(ring,hi))
        for layer in range(2):
            for i in range(n):
                j=(i+1)%n;a=off+layer*n+i;b=off+layer*n+j;c=b+n;d=a+n
                self.faces.extend(((a,b,c),(a,c,d)))
        flat=[Vector((x,y,0)) for x,y in ring]
        for a,b,c in tessellate_polygon([flat]):
            if (flat[b]-flat[a]).cross(flat[c]-flat[a]).z<0:b,c=c,b
            self.faces.append((off+c,off+b,off+a))
            self.faces.append((off+2*n+a,off+2*n+b,off+2*n+c))
        self.components.append({'id':description,'vertex_start':off,'vertex_count':3*n,
            'face_start':fs,'face_count':len(self.faces)-fs,'z_interval':[z0,z1],
            'footprint':ring,'back_embed_m':base.EMBED,'edge_chip_max_m':.004})

def build(ctx):
    scene=bpy.context.scene
    if hashlib.sha256(__import__('pathlib').Path(base.__file__).read_bytes()).hexdigest()!=BASE_HELPER_SHA:
        raise ValueError('Frozen12a helper changed')
    previous=bpy.data.collections.get(NAMESPACE)
    if previous:
        expected=json.loads(previous['geometry'])
        if set(o.name for o in previous.objects)!=set(json.loads(previous['added'])):
            raise ValueError('Partial12b completion')
        if any(n not in scene.objects or base.geometry_hash(scene.objects[n])!=h for n,h in expected.items()):
            raise ValueError('Changed12b geometry')
        return {'status':'SKIPPED_ALREADY_APPLIED','objects':json.loads(previous['added'])}
    coll12a=bpy.data.collections.get(base.NAMESPACE)
    if coll12a is None or any(n not in scene.objects for n in LOWER+MODIFIED):
        raise ValueError('Requires complete frozen12a candidate')
    frozen_lower=json.loads(coll12a['geometry']);guards=json.loads(coll12a['source_guards'])
    if set(frozen_lower)!=set(LOWER) or set(guards)!=set(MODIFIED):raise ValueError('Unexpected12a whitelist')
    if any(base.geometry_hash(scene.objects[n])!=h for n,h in (frozen_lower|guards).items()):
        raise ValueError('Changed12a source')
    terrace=scene.objects['MAIN_L1_TERRACE_W_finish'];datum=top(terrace)
    if abs(datum-.022)>1e-6:raise ValueError('Main terrace finish datum changed')
    old_cap_top=top(scene.objects['MAIN_chimney_cap']);target=datum+NOMINAL_M;delta=target-old_cap_top
    if not .4568<delta<.4570:raise ValueError('Unexpected tower correction')
    source_bounds={n:base.bounds(scene.objects[n]) for n in MODIFIED}
    # Preserve all matrices and every vertex below the old top plane on the two
    # structural bodies. Cap/outlets translate by the same delta in mesh space.
    changes=[]
    for name in MODIFIED:
        ob=scene.objects[name]
        if ob.type!='MESH' or ob.modifiers or ob.data.users!=1:raise ValueError(('Unsupported source tower object',name))
        old_mesh=ob.data;mesh=old_mesh.copy();mesh.name=name+'_12b_HeightMesh'
        inverse=ob.matrix_world.inverted();upper=source_bounds[name][2][1];changed=[]
        for v in mesh.vertices:
            world=ob.matrix_world@v.co
            if name.startswith('MAIN_stone_tower_') and world.z<upper-1e-6:continue
            before=list(world);world.z+=delta;v.co=inverse@world;changed.append({'id':v.index,'before':before,'after':list(world)})
        ob.data=mesh;mesh.update();changes.append({'object':name,'changed_vertices':changed,'before_bounds':source_bounds[name]})
    bpy.context.view_layer.update()
    low=base.MAX_Z+.008
    high=source_bounds['MAIN_chimney_cap'][2][0]+delta-.001
    envelope=[[X0-base.MAX_DEPTH,X1+base.MAX_DEPTH],[Y0-base.MAX_DEPTH,Y1],[low,high]]
    excluded=set(LOWER)|set(MODIFIED)
    constraints=[]
    for ob in scene.objects:
        if ob.type!='MESH' or ob.hide_render or ob.name in excluded:continue
        b=base.bounds(ob)
        if base.overlap(envelope,b):constraints.append({'name':ob.name,'bounds':b,'geometry_hash':base.geometry_hash(ob)})
    # The original north return is an intentional adjacent structural obstacle.
    constraints.append({'name':'MAIN_stone_tower_north','bounds':base.bounds(scene.objects['MAIN_stone_tower_north']),
                        'geometry_hash':base.geometry_hash(scene.objects['MAIN_stone_tower_north'])})
    masks={}
    for face,plane,axis in [('W',X0,0),('E',X1,0),('S',Y0,1)]:
        ar=[plane-base.MAX_DEPTH,plane+base.EMBED] if face in ('W','S') else [plane-base.EMBED,plane+base.MAX_DEPTH]
        masks[face]=[]
        for c in constraints:
            b=c['bounds']
            if b[axis][1]<ar[0] or b[axis][0]>ar[1]:continue
            masks[face].append({'name':c['name'],'cut':[b[1-axis][0]-.002,b[1-axis][1]+.002,b[2][0]-.002,b[2][1]+.002]})
    rng=random.Random(53461202)
    nominal=[.062,.106,.038,.081,.119,.044]
    gaps=[.0075,.009,.0065,.010,.008]
    factor=(high-low-sum(gaps))/sum(nominal);heights=[v*factor for v in nominal]
    batches={k:SplitBatch(NAMESPACE+'_'+k) for k in ('W','E','South_Return')};trimmed=[];rows=[]
    def add_face(face,u0,u1,a,b,identity):
        rects=[(u0,u1,a,b)]
        for m in masks[face]:
            nxt=[q for r in rects for q in base.subtract(r,m['cut'])]
            if nxt!=rects:trimmed.append({'component':identity,'obstacle':m['name']})
            rects=nxt
        for i,(l,r,z0,z1) in enumerate(rects):
            if l>u0+1e-8:l+=.003
            if r<u1-1e-8:r-=.003
            if z0>a+1e-8:z0+=.003
            if z1<b-1e-8:z1-=.003
            if r-l<.045 or z1-z0<.024:continue
            batches['South_Return' if face=='S' else face].add(base.face_ring(face,l,r,rng),z0,z1,rng,identity+f':part{i}')
    z=low
    for row,h in enumerate(heights):
        a,b=z,z+h;lxw,lxe=rng.uniform(.17,.235),rng.uniform(.17,.235);lyw,lye=rng.uniform(.28,.56),rng.uniform(.28,.56)
        for label,east,lx,ly in [('SW',False,lxw,lyw),('SE',True,lxe,lye)]:
            ring=base.corner_ring(east,lx,ly,rng)
            rb=[[min(p[i] for p in ring),max(p[i] for p in ring)] for i in range(2)]+[[a,b]]
            bad=[c['name'] for c in constraints if base.overlap(rb,c['bounds'])]
            if bad:raise ValueError(('New top corner protected-volume conflict',label,row,bad))
            batches['South_Return'].add(ring,a,b,rng,f'{row:02}:{label}:bonded_L')
        add_face('S',X0+lxw+.008,X1-lxe-.008,a,b,f'{row:02}:S:center')
        for face,leg in [('W',lyw),('E',lye)]:
            u=Y0+leg+.008;end=Y1-.006;index=0
            while u<end-.05:
                length=rng.uniform(.35,.96)
                if end-u-length<.16:length=end-u
                stop=min(end,u+length)
                if h>.085 and (index+row)%4==1:
                    split=a+h*.34
                    add_face(face,u,stop,a,split,f'{row:02}:{face}:{index}:packing')
                    add_face(face,u,stop,split+.007,b,f'{row:02}:{face}:{index}:thick')
                else:add_face(face,u,stop,a,b,f'{row:02}:{face}:{index}')
                u=stop+rng.uniform(.006,.013);index+=1
        rows.append({'row':row,'z0':a,'z1':b,'body_height':h,'gap_after':gaps[row] if row<5 else 0})
        z=b+(gaps[row] if row<5 else 0)
    count=sum(len(b.components) for b in batches.values());tris=sum(len(b.faces) for b in batches.values())
    if count>95 or tris>6000:raise ValueError(('Upper completion budget',count,tris))
    for b in batches.values():
        if any(not all(envelope[i][0]-1e-6<=v[i]<=envelope[i][1]+1e-6 for i in range(3)) for v in b.vertices):raise ValueError('New top finish outside bounded envelope')
    coll=bpy.data.collections.new(NAMESPACE);scene.collection.children.link(coll)
    material=bpy.data.materials[base.NAMESPACE+'_Stone'];added=[]
    for b in batches.values():
        mesh=bpy.data.meshes.new(b.name+'_Mesh');mesh.from_pydata(b.vertices,[],b.faces);mesh.update();mesh.materials.append(material)
        ob=bpy.data.objects.new(b.name,mesh);coll.objects.link(ob);ob['evidence']='C';ob['role']='upper tower height completion';ob['nominal_height_evidence']='HABS MAIN TOWER32ft9.5in relative main terrace0ft; graphic-to-mesh correspondence C'
        added.append(ob.name)
    bpy.context.view_layer.update()
    expected={n:base.geometry_hash(scene.objects[n]) for n in added+list(MODIFIED)+list(LOWER)+['MAIN_L1_TERRACE_W_finish']}
    coll['geometry']=json.dumps(expected,sort_keys=True);coll['added']=json.dumps(added)
    if any(base.geometry_hash(scene.objects[n])!=h for n,h in frozen_lower.items()):raise ValueError('Lower12a finish changed')
    return {'status':'HEIGHT_CANDIDATE_NOT_VISUALLY_ACCEPTED','added':added,'modified':list(MODIFIED),'changed_vertex_records':changes,
            'components':{b.name:b.components for b in batches.values()},'component_count':count,'triangles':tris,'rows':rows,
            'actual_source_constraints':constraints,'surface_masks':masks,'trimmed_components':trimmed,'allowed_envelope':envelope,
            'actual_datum_finish_z':datum,'nominal_relative_height_m':NOMINAL_M,'target_continuous_top_world_z':target,
            'old_continuous_top_world_z':old_cap_top,'correction_m':delta,'lower_finish_exact':True,
            'outlet_status':'Original C XY, dimensions and40mm relative top offset retained; old10mm gap and unknown source outlet mapping NOT repaired or accepted.',
            'cap_status':'Original C cap plan and120mm thickness retained; broad overhang source correspondence NOT validated.',
            'declared_datum':'Actual visible MAIN_L1_TERRACE_W_finish; C source-to-model mapping, explicit22mm above model structural zero'}
