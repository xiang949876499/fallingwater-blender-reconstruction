"""Read saved Master candidate; actual evaluated triangles, contact and proposals."""
import bpy,json,sys,hashlib,math,itertools
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import main_house as mh
import master_detail10 as md
SRC=R/'scene/Fallingwater_master_detail_candidate10c.blend'
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
cache={}
def geom(o):
 if o.name not in cache:
  e=o.evaluated_get(deps);m=e.to_mesh();v=[e.matrix_world@q.co for q in m.vertices]
  tree=BVHTree.FromPolygons(v,[tuple(f.vertices) for f in m.polygons]);e.to_mesh_clear()
  cache[o.name]=(tree,[(min(q[k] for q in v),max(q[k] for q in v)) for k in range(3)])
 return cache[o.name]
def intersects(a,b,tol=1e-5):return all(min(x[1],y[1])-max(x[0],y[0])>tol for x,y in zip(a,b))
def bbox(n):return geom(s.objects[n])[1]
def group(o):
 if o.name.startswith('FW_FURN_MAIN_L2_MASTER_'):return o.get('asset_id',o.parent.name if o.parent else o.name)
 if o.get('component_type')!='furniture':return None
 for pre in ('wardrobe','continuous_overdoor','north_bedside','south_open_bedside'):
  if o.name.startswith('MASTER_DETAIL10_'+pre):return 'wardrobe' if pre=='continuous_overdoor' else pre
 return None
furn=[o for o in s.objects if o.type=='MESH' and group(o)]
arch=[o for o in s.objects if o.type=='MESH' and (o.name.startswith('MAIN_L2_') or o.name.startswith('MASTER_DETAIL10_') and o.get('component_type')!='furniture') and not o.name.endswith(('_slab','_finish'))]
cross=[]
for a in furn:
 ta,ba=geom(a)
 for b in arch:
  tb,bb=geom(b)
  if not intersects(ba,bb):continue
  pairs=ta.overlap(tb)
  if pairs:cross.append({'furniture':a.name,'architecture':b.name,'triangle_pairs':len(pairs),'bounds_a':ba,'bounds_b':bb})
pairs=[]
for a,b in itertools.combinations(furn,2):
 if group(a)==group(b):continue
 ta,ba=geom(a);tb,bb=geom(b)
 if intersects(ba,bb):
  hits=ta.overlap(tb)
  if hits:pairs.append({'a':a.name,'b':b.name,'triangles':len(hits)})
contacts=[]
def contact(label,top,bottom):
 hi=bbox(top)[2][1];lo=bbox(bottom)[2][0]
 contacts.append({'label':label,'support':top,'carried':bottom,'support_top':hi,'carried_bottom':lo,'gap_m':lo-hi,'pass':-.04<=lo-hi<=.00015})
contact('wardrobe_support','MASTER_DETAIL10_wardrobe_recessed_support','MASTER_DETAIL10_wardrobe_base')
contact('wardrobe_upper_shelf','MASTER_DETAIL10_wardrobe_top','MASTER_DETAIL10_continuous_overdoor_wood_shelf')
for side in ('north_bedside','south_open_bedside'):
 contact(side+'_light_standard','MASTER_DETAIL10_'+side+'_open_shelf_2','MASTER_DETAIL10_'+side+'_vertical_light_standard')
for i in range(10):
 n='MASTER_DETAIL10_south_open_bedside_book_%02d'%i
 if n in s.objects:contact('book_contact','MASTER_DETAIL10_south_open_bedside_open_shelf_1',n)
support=[]
for n in ['FW_FURN_MAIN_L2_MASTER_walnut_bed_00_recessed_support','FW_FURN_MAIN_L2_MASTER_bedroom_desk_02_leg','FW_FURN_MAIN_L2_MASTER_desk_chair_03_leg','MASTER_DETAIL10_wardrobe_recessed_support','MASTER_DETAIL10_north_bedside_side_-1','MASTER_DETAIL10_south_open_bedside_side_-1']:
 b=bbox(n);xy=[sum(b[k])/2 for k in (0,1)]
 h,p,no,f,o,mat=s.ray_cast(deps,Vector((*xy,md.TOP+.05)),Vector((0,0,-1)),distance=.10)
 support.append({'object':n,'bounds':b,'floor':o.name if h else None,'floor_z':p.z if h else None,'base_to_finish':b[2][0]-md.TOP,'pass':h and abs(p.z-md.TOP)<.0001 and -.03<=b[2][0]-md.TOP<=.00015})
all_local=[o for o in s.objects if o.type=='MESH' and (o.name.startswith(('MAIN_L2_','MAIN_stair2_','MAIN_floor_threshold_','MASTER_DETAIL10_','FW_FURN_MAIN_L2_MASTER_'))) ]
def body(px,py):
 xy=mh.xy((px,py));near=[]
 for dz in (.18,.6,1.1,1.6):
  q=Vector((*xy,md.TOP+dz))
  for ob in all_local:
   if ob.name.endswith(('_slab','_finish')) or 'threshold' in ob.name:continue
   t,b=geom(ob)
   if any(q[k]<b[k][0]-.18 or q[k]>b[k][1]+.18 for k in range(3)):continue
   p,no,f,d=t.find_nearest(q,.18)
   if p is not None:near.append({'object':ob.name,'z':q.z,'distance':d})
 h,p,no,f,o,mat=s.ray_cast(deps,Vector((*xy,md.TOP+.06)),Vector((0,0,-1)),distance=.1)
 return {'source_xy':[px,py],'body_hits':near,'floor':o.name if h else None,'pass':not near and h and abs(p.z-md.TOP)<.001}
camera_proposals=[]
for name,eye,target in [('PROPOSED_MASTER_NORTH_EAST',(359,381),(393,333)),('PROPOSED_MASTER_WEST_HEARTH',(380,385),(325,344))]:
 pos=(*mh.xy(eye),md.TOP+1.6);aim=(*mh.xy(target),md.TOP+1.02)
 camera_proposals.append({'name':name,'eye_source':eye,'target_source':target,'location_world':pos,'target_world':aim,'lens_mm':24,'sensor_width_mm':36,'body_check':body(*eye),'scene_camera_created':False})
newpath=[]
pts=[(359,342),(359,390),(397,390),(400,397),(413.4,397)]
for a,b in zip(pts,pts[1:]):
 count=max(2,math.ceil(math.dist(mh.xy(a),mh.xy(b))/.05))
 for i in range(count+1):newpath.append(body(a[0]+(b[0]-a[0])*i/count,a[1]+(b[1]-a[1])*i/count))
report={'source':str(SRC),'sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'furniture_architecture_intersections':cross,'between_asset_intersections':pairs,'contacts':contacts,'support':support,'camera_proposals':camera_proposals,'updated_source_path':pts,'updated_path_samples':newpath,'counts':{'furniture_architecture_intersections':len(cross),'between_asset_intersections':len(pairs),'contact_failures':sum(not x['pass'] for x in contacts),'support_failures':sum(not x['pass'] for x in support),'proposal_camera_failures':sum(not x['body_check']['pass'] for x in camera_proposals),'updated_path_samples':len(newpath),'updated_path_fails':sum(not x['pass'] for x in newpath)},'limits':['No scene edits or camera creation.','Path ends west of the still-old bath wall; actual bath entry must be checked after integration.','Triangle-overlap test supplements closed-mesh tests; it does not certify all potential containment cases.']}
(R/'qa/master-detail10-contact-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({'counts':report['counts'],'collisions':cross,'furniture':pairs,'failed_contacts':[x for x in contacts if not x['pass']],'cameras':camera_proposals},indent=2))
