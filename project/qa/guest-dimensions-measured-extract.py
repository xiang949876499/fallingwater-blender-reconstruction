"""Independently measure the saved iteration03 mesh. Read-only; no GPU/render."""
import bpy,json,sys,hashlib,math,datetime
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path('D:/zx/test/project');src=root/'scene/Fallingwater_working.blend'
d=json.loads((root/'data/guest_house.json').read_text(encoding='utf-8'))
config=json.loads((root/'config.json').read_text(encoding='utf-8'))
reg=dict(d['registration']);reg.update(config.get('guest_registration',{}))
sx,sy=reg['meters_per_pixel'];ox,oy=reg['origin_px'];wx,wy,gz=reg['world_origin']
def P(x,y,z):return (wx+(x-ox)*sx,wy+(oy-y)*sy,z)
deps=bpy.context.evaluated_depsgraph_get();meshes={}
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not o.name.startswith('GUEST') or o.name=='GUEST_LAYERED_SANDSTONE_COURSES':continue
 if o.get('role')=='furniture' or o.get('component')=='furniture':continue
 ev=o.evaluated_get(deps);m=ev.to_mesh();verts=[tuple(o.matrix_world@v.co) for v in m.vertices];faces=[tuple(f.vertices) for f in m.polygons]
 if verts and faces:
  meshes[o.name]={'verts':verts,'edges':[tuple(e.vertices) for e in m.edges],'bvh':BVHTree.FromPolygons(verts,faces,all_triangles=False),'bounds':[[min(v[i] for v in verts) for i in range(3)],[max(v[i] for v in verts) for i in range(3)]],'material':o.active_material.name if o.active_material else None}
 ev.to_mesh_clear()
def names(prefixes):return [n for n in meshes if any(n.startswith(p) for p in prefixes)]
def hit(origin,direction,allowed):
 candidates=[]
 for n in allowed:
  loc,norm,idx,distance=meshes[n]['bvh'].ray_cast(Vector(origin),Vector(direction),50)
  if loc is not None:candidates.append((distance,n,loc,norm))
 if not candidates:return None
 dist,n,loc,norm=min(candidates,key=lambda x:x[0]);return {'object':n,'point_m':[round(float(v),7) for v in loc],'normal':[round(float(v),5) for v in norm],'distance_m':float(dist)}
def extreme(allowed,axis,highest=True):
 allv=[(v[axis],n,v) for n in allowed for v in meshes[n]['verts']];val,n,v=(max if highest else min)(allv,key=lambda t:t[0]);return {'object':n,'point_m':[round(float(c),7) for c in v],'coordinate_m':float(val)}
mainfloor=extreme(['GUEST_L1_MAIN_FLOOR'],2);floorz=mainfloor['coordinate_m']
records={x['id']:{'id':x['id'],'source':x['source'],'original':x['original'],'reference_m':x['meters'],'source_reading_uncertainty_m':x['uncertainty_m'],'tolerance_m':max(.020,.005*x['meters']),'status':'NOT_RUN','actual_mesh_measurement_m':None,'delta_m':None,'endpoints':None,'method':None,'evidence':'A source label; independent mesh measurement pending'} for x in d['dimensions']}
def store(key,val,ends,method,evidence='A printed label; C endpoint interpretation from plan/elevation; actual evaluated mesh'):
 r=records['GUEST_'+key];r.update(actual_mesh_measurement_m=round(val,7),delta_m=round(val-r['reference_m'],7),endpoints=ends,method=method,evidence=evidence,status='PASS' if abs(val-r['reference_m'])<=r['tolerance_m'] else 'FAIL')
def axisclear(key,xy,axis,allowed,z):
 dirs=[0,0,0];dirs[axis]=1;neg=[-v for v in dirs]
 a,b=hit(P(*xy,z),neg,names(allowed)),hit(P(*xy,z),dirs,names(allowed))
 if a and b:store(key,b['point_m'][axis]-a['point_m'][axis],[a,b],f'Opposed world axis{axis} rays to actual named structural/finish faces from drawing pixel{xy},Z{z:.5f}. Opening-free section selected; decorative coursing and furnishings excluded. Nominal room dimension axis follows plan aspect and adjacent dimension chain.')
 else:records['GUEST_'+key]['method']='NOT_RUN: opposed structural rays did not resolve both intended faces.'
# Pool clear shell dimensions: rays below finite water skin to its actual inside faces.
water=meshes['GUEST_POOL_water']['bounds'];cx=(water[0][0]+water[1][0])/2;cy=(water[0][1]+water[1][1])/2
shell=names(['GUEST_POOL_shell_'])
for key,axis in [('POOL_LENGTH',0),('POOL_WIDTH',1)]:
 direction=[0,0,0];direction[axis]=1
 a,b=hit((cx,cy,floorz),[-x for x in direction],shell),hit((cx,cy,floorz),direction,shell)
 store(key,b['point_m'][axis]-a['point_m'][axis],[a,b],'Opposed ray intersections with evaluated pool shell inner faces at guest datum; finite water mesh deliberately not used as the clear-basin size.','A printed pool dimensions; unambiguous inner shell face intersections')
axisclear('BOILER_DIM_1',(353,333),1,['GUEST_L1_BOILER_NORTH','GUEST_L1_BOILER_SOUTH'],floorz+.35)
axisclear('BOILER_DIM_2',(353,343),0,['GUEST_L1_BOILER_WEST','GUEST_L1_BOILER_EAST'],floorz+.35)
axisclear('GUEST_ROOM_LENGTH',(580,425),0,['GUEST_L1_BATH_EAST','GUEST_L1_BED_EAST'],floorz+.35)
axisclear('GUEST_ROOM_DEPTH',(580,400),1,['GUEST_L1_NORTH_STONE_SPINE','GUEST_L1_BED_FRONT'],floorz+.35)
basementfloor=extreme(['GUEST_B1_FLOOR'],2)['coordinate_m']
axisclear('LAUNDRY_LENGTH',(258,393),1,['GUEST_B1_BASE_NORTH','GUEST_B1_BASE_SOUTH'],basementfloor+.50)
axisclear('LAUNDRY_DEPTH',(255,406),0,['GUEST_B1_BASE_BATH_EAST','GUEST_B1_BASE_EAST'],basementfloor+.50)
axisclear('BASE_BATH_LENGTH',(216,400),1,['GUEST_B1_BASE_BATH_NORTH','GUEST_B1_BASE_SOUTH'],basementfloor+.50)
axisclear('BASE_BATH_WIDTH',(216,404),0,['GUEST_B1_BASE_BATH_WEST','GUEST_B1_BASE_BATH_EAST'],basementfloor+.50)
coping_ring=[n for n in meshes if n.startswith('GUEST_POOL_coping_') and n[len('GUEST_POOL_coping_'):].isdigit()]
a,b=extreme(coping_ring,0,False),extreme(coping_ring,0,True)
store('POOL_OUTER_WIDTH',b['coordinate_m']-a['coordinate_m'],[a,b],'WorldX extrema of actual evaluated outer coping ring; compared with the separate printed pool exterior horizontal chain.','A source pool exterior chain; actual mesh extrema')
for key,allowed in [('SECOND_LEVEL',['GUEST_L2_BEDROOM_FLOOR']),('TOP_STONE',names(['GUEST_L2_UPPER_TERRACE_DIAGONAL','GUEST_L2_UPPER_TERRACE_NORTHEAST','GUEST_L2_UPPER_TERRACE_EAST'])),('PARAPET',names(['GUEST_LOW_ARM_ROOF_parapet_'])),('CHIMNEY',names(['GUEST_STONE_CHIMNEY'])),('LOW_STONE',names(['GUEST_L1_NORTH_STONE_SPINE'])),('POOL_TOP',coping_ring)]:
 top=extreme(allowed,2);store(key,top['coordinate_m']-floorz,[mainfloor,top],'Difference between actual mesh topZ and actual guest L1 slab topZ. TOP_STONE uses pointed service terrace enclosing stone walls visible at west elevation left; roof finish/other chimneys are not substituted.','A elevation label; C wall identity mapping for TOP_STONE, A direct object mapping for other levels')
for key,note,diag in [('THEATER_LENGTH','Nominal27′9×19′5 is printed inside a skew, recessed theater. Neither dimension is drawn with explicit endpoints; true door recess and nonparallel walls make world-axis extent an invalid substitute.',None),('THEATER_DEPTH','Same nonrectangular theater endpoint ambiguity; no independent source principal-axis endpoint correspondence has been established.',None),('SERVICE_Y_CHAIN','Printed50′10¼ vertical witness line starts at an angled service-wall projection. Mapping that witness to a specific inner/outer finished vertex is unresolved.',None),('THEATER_NORTH_RISE','Printed14′5⅝ north angled-wall projected rise lacks established inner/outer vertex identity in the current traced mesh. Do not substitute whole object boundingbox.',None),('THEATER_EAST_SEGMENT','Printed12′8¾ is a partial east-wall interval terminating at a projection line; no named mesh vertex fixes that witness endpoint, so whole east-wall length is not equivalent.',None)]:
 records['GUEST_'+key].update(method='NOT_RUN: '+note,evidence='A printed source; U exact source-to-mesh endpoints')
# Real evaluated mesh edges for diagnostic projection overlays; not dimension boxes.
plan=[];west=[]
for n,m in meshes.items():
 isplan=(n.startswith('GUEST_L1_') or n.startswith('GUEST_POOL_') or n.startswith('GUEST_SERVICE_ASCENT') or n.startswith('GUEST_LAUNDRY_DESCENT')) and 'open_leaf' not in n and 'handle' not in n
 iswest=any(s in n for s in ['CHAUFFEUR_WEST','CHAUFFEUR_SOUTH','THEATER_WEST','THEATER_DIAGONAL_BACK','THEATER_NORTHEAST','UPPER_WEST','UPPER_SOUTH','UPPER_TERRACE_','WEST_LOUNGE','SERVICE_BEDROOM_ROOF','LOW_ARM_ROOF','GUEST_CONNECTOR_canopy','GUEST_CONNECTOR_roof_riser','GUEST_CONNECTOR_lowwall','GUEST_L2_BEDROOM_FLOOR','GUEST_L2_NORTH_TERRACE','GUEST_L1_THEATER_FLOOR','GUEST_BOILER_ROOF']) and 'open_leaf' not in n
 if not(isplan or iswest):continue
 lines=[[m['verts'][a],m['verts'][b]] for a,b in m['edges']]
 if isplan:plan.append({'object':n,'edges_world':lines})
 if iswest:west.append({'object':n,'edges_world':lines})
scenehash=hashlib.sha256(src.read_bytes()).hexdigest()
report={'status':'FAIL' if any(r['status']=='FAIL' for r in records.values()) else 'INCOMPLETE','source_scene':str(src),'source_scene_sha256':scenehash,'source_scene_mtime':datetime.datetime.fromtimestamp(src.stat().st_mtime).isoformat(),'blender_version':bpy.app.version_string,'threads':4,'rendered':False,'measurement_method':'Loaded saved iteration03 .blend; evaluated object meshes transformed into world coordinates; measured ray intersections/extrema. Source model_value_m fields were never used. Reference values are only comparison targets.','tolerance_rule':'research/qa-spec.md GEO-02: abs(error)<=max(0.020m,0.005×referenceLength); larger source uncertainty disclosed separately, never silently widens acceptance.','coordinate_registration':reg,'floor_datum_actual':mainfloor,'counts':{s:sum(r['status']==s for r in records.values()) for s in ['PASS','FAIL','NOT_RUN']},'measurements':list(records.values()),'limitations':['Decorative ashlar projections excluded from clear-room dimensions; cork wall linings included when intersected.','Room label axes inferred from plan geometry; finished-face definition remains a stated modeling interpretation.','TOP_STONE identity is the pointed upper service terrace enclosure; other stone elements must not be substituted to get the desired number.','NOT_RUN anchors remain unmeasured for acceptance, rather than borrowing data-file targets.','This subtask reports evidence only and intentionally changes no scene/data dimensions.']}
(root/'qa/guest-dimensions-measured.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(root/'qa/guest-dimensions-measured-projection.json').write_text(json.dumps({'scene_sha256':scenehash,'plan':plan,'west':west}),encoding='utf-8')
print(json.dumps({'counts':report['counts'],'measurements':[{k:r[k] for k in ['id','status','actual_mesh_measurement_m','delta_m']} for r in report['measurements']]},ensure_ascii=False))
