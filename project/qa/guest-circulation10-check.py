"""Actual evaluated geometry regression, CPU only. No image rendering."""
import bpy, sys, json, hashlib, math, array, time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/zx/test/project');sys.path.insert(0,str(ROOT/'scripts'))
import guest_circulation10 as c10


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def signature(o):
    h=hashlib.sha256()
    h.update(str((o.type,tuple(tuple(r) for r in o.matrix_world),o.hide_render)).encode())
    if o.type=='MESH':
        coords=array.array('f',[0.0])*(len(o.data.vertices)*3)
        o.data.vertices.foreach_get('co',coords);h.update(coords.tobytes())
        loops=array.array('i',[0])*len(o.data.loops)
        o.data.loops.foreach_get('vertex_index',loops);h.update(loops.tobytes())
    h.update(str([m.name for m in getattr(o.data,'materials',[]) if m]).encode())
    return h.hexdigest()


def rounded(p):return [round(float(q),7) for q in p]


class Actual:
    def __init__(self):
        dg=bpy.context.evaluated_depsgraph_get();verts=[];faces=[];self.owners=[]
        count=0
        for o in bpy.context.scene.objects:
            if o.type not in {'MESH','CURVE','SURFACE','FONT'} or o.hide_render or o.name.startswith(('REF_','QA_')):continue
            cs=[o.matrix_world@Vector(v) for v in o.bound_box]
            bounds=((-5.5,25),(22,52),(4.0,14.5))
            if any(max(v[a] for v in cs)<bounds[a][0] or min(v[a] for v in cs)>bounds[a][1] for a in range(3)):continue
            eo=o.evaluated_get(dg);mesh=eo.to_mesh();offset=len(verts)
            verts.extend(eo.matrix_world@v.co for v in mesh.vertices)
            faces.extend(tuple(offset+i for i in f.vertices) for f in mesh.polygons)
            self.owners.extend([o.name]*len(mesh.polygons));eo.to_mesh_clear();count+=1
        self.bvh=BVHTree.FromPolygons(verts,faces,epsilon=0.000001)
        self.stats={'evaluated_objects':count,'vertices':len(verts),'faces':len(faces),'epsilon_m':.000001}
        self.rays=0
    def ray(self,p,d,dist):
        self.rays+=1;loc,n,index,t=self.bvh.ray_cast(Vector(p),Vector(d),dist)
        return None if loc is None else {'object':self.owners[index],'location':rounded(loc),'normal':rounded(n),'distance':round(t,7)}
    def check(self,p,stair=False,side=None):
        x,y,z=p;issues=[];head=[]
        # Ground is checked to 4mm, not the much wider navigation stride band.
        offsets=[(0,0)]
        if side is not None:offsets.extend([(side[0]*.18,side[1]*.18),(-side[0]*.18,-side[1]*.18)])
        for dx,dy in offsets:
            hit=self.ray((x+dx,y+dy,z+.205),(0,0,-1),.225)
            if hit is None or hit['normal'][2]<.8 or abs(hit['location'][2]-z)>.004:
                # Diagnostic full vertical ray records what actually supports
                # the failed point, without changing the pass criterion.
                actual=self.ray((x+dx,y+dy,z+.32),(0,0,-1),2)
                issues.append({'reason':'GROUND','offset':[dx,dy],'expected':z,'hit':hit,'nearby_vertical':actual})
        for i in range(13):
            angle=(i-1)*math.tau/12;dx,dy=(0,0) if i==0 else (.18*math.cos(angle),.18*math.sin(angle))
            low=.20 if stair else .025
            hit=self.ray((x+dx,y+dy,z+low),(0,0,1),1.95-low)
            if hit:issues.append({'reason':'BODY_COLUMN','offset':[dx,dy],'hit':hit})
            overhead=self.ray((x+dx,y+dy,z+.20),(0,0,1),5)
            if overhead:head.append({'clearance':overhead['location'][2]-z,'hit':overhead})
        for height in (.30,.72,1.20,1.65,1.945):
            for i in range(12):
                ang=i*math.tau/12
                hit=self.ray((x,y,z+height),(math.cos(ang),math.sin(ang),0),.18)
                if hit:issues.append({'reason':'BODY_RADIUS','height':height,'hit':hit})
        return issues,min(head,key=lambda r:r['clearance']) if head else None


def line(a,b,spacing=.025):
    a,b=Vector(a),Vector(b);n=max(1,math.ceil((b-a).length/spacing))
    return [list(a.lerp(b,i/n)) for i in range(n+1)]


def execute(reopen=False):
    started=time.monotonic()
    fresh_destination=ROOT/'scene/Fallingwater_guest_circulation_candidate10_rebuild.blend'
    if not reopen and fresh_destination.exists():
        raise RuntimeError('Preserve existing candidate: choose a new explicit fresh_destination before another build')
    source=ROOT/'scene/Fallingwater_iteration09.blend'
    assert sha(source)==c10.SOURCE_SHA
    prod={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'scripts/guest_house.py',ROOT/'data/guest_house.json',ROOT/'scripts/tour.py']}
    if reopen:
        manifest=json.loads(bpy.data.texts['FW_GUEST_CIRCULATION10_CANDIDATE.json'].as_string())
        invariant=json.loads((ROOT/'qa/guest-circulation10-invariant.json').read_text(encoding='utf-8'))
        original=invariant['original'];foreign=invariant['foreign']
    else:
        original={o.name:signature(o) for o in bpy.context.scene.objects}
        foreign={n:h for n,h in original.items() if not c10.removable(n) and n not in c10.MUTATE_EXACT}
        manifest=c10.apply()
        (ROOT/'qa/guest-circulation10-invariant.json').write_text(json.dumps({'original':original,'foreign':foreign,'production_sha256':prod},indent=2),encoding='utf-8')
        (ROOT/'qa/guest-circulation10-candidate-adjacency.json').write_text(json.dumps({k:manifest[k] for k in ('source_sha256','adjacency','retracted_adjacency')},indent=2),encoding='utf-8')
    changes=[]
    for n,h in foreign.items():
        if n not in bpy.data.objects or signature(bpy.data.objects[n])!=h:changes.append(n)
    assert not changes,('Unexpected edits outside whitelist',changes)
    checker=Actual();checks=[]
    def run(label,points,stair=False,side=None):
        failures=[];lowest=None
        for index,p in enumerate(points):
            issues,head=checker.check(p,stair,side)
            if issues:failures.append({'sample':index,'point':rounded(p),'issues':issues})
            if head and (lowest is None or head['clearance']<lowest['clearance']):lowest={'point':rounded(p),**head}
        row={'id':label,'status':'FAIL' if failures else 'PASS','samples':len(points),'failed_samples':len(failures),'failures':failures,'lowest_overhead':lowest,'stair_mode':stair}
        checks.append(row);print(label,row['status'],len(points),len(failures),flush=True)
    for f in manifest['flights']:
        a=Vector(c10.source_point(f['source_start_px']));b=Vector(c10.source_point(f['source_end_px']));unit=(b-a).normalized();side=(-unit.y,unit.x)
        pts=[]
        for t in f['treads']:
            aa=Vector(t['a'])+unit*.001;bb=Vector(t['b'])-unit*.001
            pts.extend(line([*aa,t['top']],[*bb,t['top']],.025))
        run(f['id'],pts,True,side)
        # Both sides of each physical riser face, including platform contacts.
        joints=[];going=f['going_m'];z0=8.4+f['z0']
        for j in range(f['risers']):
            pos=a+unit*j*going
            joints.extend([[*(pos-unit*.002),z0+j*f['riser_m']],
                           [*(pos+unit*.002),z0+(j+1)*f['riser_m']]])
        run(f['id']+'_JOINTS',joints,True,None)
    # Actual turns pass around the source divider, not through its center.
    paths={
        'B1_DOOR_APPROACH':[(278,364,-2.36),(294.45,364,-2.36),(294.45,367.95,-2.36)],
        'LOWER_RETURN':[(294.45,404.55,-1.18),(294.45,412.3,-1.18),(316.35,412.3,-1.18),(316.35,400.85,-1.18)],
        'NORTH_L1_CROSSOVER':[(316.35,349.95,0),(316.35,340,0),(296.75,340,0),(296.75,368.95,0)],
        'CHAUFFEUR_NORTH_DOOR':[(277,359.75,0),(284,359.75,0),(296.75,359.75,0)],
        'UPPER_RETURN':[(296.75,405.55,1.4478),(296.75,412.3,1.4478),(316.35,412.3,1.4478),(316.35,405.55,1.4478)],
        'NORTH_L2_APPROACH':[(316.35,381.95,2.352675),(316.35,340,2.352675)],
        'FRONT_LOW_TO_W1':[(305,423,-1.18),(305,461,-1.18),(323.95,461,-1.18)],
        'FRONT_MIDDLE':[(336.05,461,-.6742857142857143),(427.95,461,-.6742857142857143)],
        'FRONT_EAST':[(448.05,461,0),(650,461,0),(650,390,0)],
        'GUEST_EAST_DOOR':[(650,389,0),(624,389,0)],
        'GUEST_TO_GALLERY':[(550,397,0),(547,388,0),(547,374,0),(520,374,0),(481,373,0)],
        'GALLERY_TO_LOUNGE':[(480,376,0),(463,385,0),(450,383.24,0),(419.25,383.24,0)],
        'REAL_SOUTHEAST_LOUNGE_ENTRY':[(466,442,0),(466,424,0),(463,385,0),(450,383.24,0),(419.25,383.24,0)],
    }
    for label,nodes in paths.items():
        pp=[c10.world_point(p) for p in nodes];pts=[]
        for a,b in zip(pp,pp[1:]):pts.extend(line(a,b))
        run(label,pts,label in {'B1_DOOR_APPROACH','LOWER_RETURN','NORTH_L1_CROSSOVER','UPPER_RETURN','FRONT_LOW_TO_W1','FRONT_MIDDLE'},None)
    # Connector tread centers and dense same-height interiors are checked
    # against complete scene terrain, posts, canopy and the unmodified main.
    pts=[];jointpts=[]
    for i,t in enumerate(manifest['connector']):
        a,b=Vector(t['a']),Vector(t['b']);u=(b-a).normalized()
        pts.extend(line(a+u*.002,b-u*.002))
        if i:
            last=manifest['connector'][i-1]
            la,lb=Vector(last['a']),Vector(last['b']);ta,tb=Vector(t['a']),Vector(t['b'])
            jointpts.extend([list(lb-(lb-la).normalized()*.002),list(ta+(tb-ta).normalized()*.002)])
    run('MAIN_GUEST_CONNECTOR',pts,True,None)
    run('CONNECTOR_SEAMS',jointpts,True,None)
    run('CONNECTOR_MAIN_INTERFACE',line((5.4496,23.4702,5.28615),(5.70,23.4702,5.28615)),False,None)
    run('CONNECTOR_SOUTH_INTERFACE',line((2.1353,37.0468,7.22),c10.world_point((305,423,-1.18))),False,None)
    # New glazing must stop walking rays; the glass/sill is never inspection-
    # only pass permission.3 elevations*5 offsets independently hit its mesh.
    west=[]
    for yy in (417,421,425,430,434):
        for zz in (.15,.90,1.80):
            x,y=c10.source_point((330,yy));hit=checker.ray((x-.30,y,8.4+zz),(1,0,0),.60)
            west.append({'source_y':yy,'relative_z':zz,'hit':hit,'passed':bool(hit and (hit['object'].startswith(c10.PREFIX+'WEST_LOUNGE_WINDOW') or hit['object']=='GUEST_LAYERED_SANDSTONE_COURSES'))})
    report={'source':str(source),'source_sha256':c10.SOURCE_SHA,'reopened':reopen,
            'production_sha256':prod,'implementation_sha256':manifest.get('implementation_sha256'),'whitelist_removed':manifest['removed_objects'],'new_object_count':len(manifest['created_objects']),
            'unchanged_nonwhitelist_count':len(foreign),'unexpected_changes':changes,
            'retaining_wall_sha256':signature(bpy.data.objects[c10.FIXED_WALL]),
            'explicit_mutations':manifest.get('explicit_mutations',[]),'excavation_summary':{k:v for k,v in manifest.get('excavation',{}).items() if k!='vertex_changes'},
            'thresholds':{'headroom_m':1.95,'body_radius_m':.18,'ground_error_m':.004,'stair_legal_riser_band_m':.20},
            'evaluated_geometry':checker.stats,'ray_count':checker.rays,'checks':checks,
            'counts':{'PASS':sum(c['status']=='PASS' for c in checks),'FAIL':sum(c['status']=='FAIL' for c in checks),'NOT_RUN':0},
            'west_window_closure':west,'west_window_all_closed':all(w['passed'] for w in west),
            'full_tour':'NOT_RUN_CANDIDATE_LOCAL_SCOPE','elapsed_seconds':time.monotonic()-started}
    output=ROOT/('qa/guest-circulation10-reopen-check.json' if reopen else 'qa/guest-circulation10-check.json')
    output.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('C10 TOTAL',report['counts'],'WINDOW',report['west_window_all_closed'],flush=True)
    if not reopen:
        dest=fresh_destination
        bpy.ops.wm.save_as_mainfile(filepath=str(dest),check_existing=False)
        (ROOT/'qa/guest-circulation10-freeze.json').write_text(json.dumps({'candidate':str(dest),'sha256':sha(dest),'source_sha256':c10.SOURCE_SHA,'status':'LOCAL_CANDIDATE_NOT_APPROVED','counts':report['counts']},indent=2),encoding='utf-8')
    assert all(sha(ROOT/p)==h for p,h in prod.items())
    return report


if __name__=='__main__':execute('--reopen' in sys.argv)
