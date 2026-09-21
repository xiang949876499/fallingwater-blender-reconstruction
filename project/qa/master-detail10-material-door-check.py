"""Read-only final material scope, actual door clearance and floor refresh QA."""
import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import master_detail10 as md
import main_house as mh
BASE=R/'scene/Fallingwater_main_interface_candidate10c.blend';SRC=R/'scene/Fallingwater_master_detail_candidate10f.blend'
def material_fp(m):
 out={'name':m.name,'nodes':[],'links':[]}
 for n in m.node_tree.nodes:
  vals=[]
  for p in n.inputs:
   if not hasattr(p,'default_value'):continue
   v=p.default_value
   try:v=list(v)
   except TypeError:v=v if isinstance(v,(int,float,str,bool)) else str(v)
   vals.append([p.name,v])
  out['nodes'].append([n.name,n.bl_idname,vals,n.image.name if hasattr(n,'image') and n.image else None,n.object.name if hasattr(n,'object') and n.object else None])
 for l in m.node_tree.links:out['links'].append([l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name])
 return hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(BASE));basefp={m.name:material_fp(m) for m in bpy.data.materials if m.use_nodes}
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
changedold=[n for n,v in basefp.items() if n not in bpy.data.materials or material_fp(bpy.data.materials[n])!=v]
mat=bpy.data.materials['FW_MasterSource10_horizontal_veneer'];nodes=mat.node_tree.nodes
channels={n:[(l.from_node.name,l.from_socket.name) for l in nodes[n].inputs['Vector'].links] for n in ('PH_Diffuse','PH_Rough','PH_Displacement')}
coord=nodes['MASTER_SHARED_WARDROBE_COORD'];root=coord.object
assignments=[o.name for o in s.objects if any(m==mat for m in getattr(o.data,'materials',[]))]
unexpected=[n for n in assignments if not n.startswith(('MASTER_DETAIL10_wardrobe_','MASTER_DETAIL10_continuous_overdoor_'))]
door=[]
for px in (353.0,359,365.0):
 for py in (302,303,304):
  xy=mh.xy((px,py));h,p,no,f,o,matr=s.ray_cast(deps,Vector((*xy,md.TOP+.10)),Vector((0,0,1)),distance=3)
  door.append({'source_xy':[px,py],'ceiling':o.name if h else None,'height':p.z-md.TOP if h else None,'pass':h and p.z-md.TOP>=1.95-.0001})
oldfloor=md.master_floor_polygon(False);newfloor=md.master_floor_polygon(True)
def area(p):return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1])))/2*mh.SX*mh.SY
oldworld=[tuple(s.objects[n].matrix_world@v.co) for n in ['MAIN_L2_MASTER_finish'] for v in s.objects[n].data.vertices]
refresh=md.refresh_master_floor(True);bpy.context.view_layer.update()
o=s.objects['MAIN_L2_MASTER_finish'];edge=max((o.matrix_world@v.co).x for v in o.data.vertices)
# The root's bath helper owns the actual new threshold: only declare shared
# coordinates here. Do not mutate its mesh in this independent QA process.
report={'status':'PASS_SCOPED_MATERIAL_AND_DOOR_NO_SAVE','candidate':str(SRC),'sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'old_material_changes':changedold,'shared_channels':channels,'coordinate_object':root.name,'coordinate_object_matrix':[list(v) for v in root.matrix_world],'shared_scale':nodes['MASTER_SHARED_METRE_SCALE'].inputs['Scale'].default_value,'shared_axis':list(nodes['MASTER_HORIZONTAL_GRAIN_ROTATE'].inputs['Axis'].default_value),'shared_angle':nodes['MASTER_HORIZONTAL_GRAIN_ROTATE'].inputs['Angle'].default_value,'new_material_assignments':assignments,'unexpected_material_assignments':unexpected,'door_clearance_samples':door,'nominal_door':{'finished_clear_width_m':14*mh.SX-.032,'finished_clear_height_m':1.98-.022},'integration_refresh':{'not_saved':True,'info':refresh,'actual_east_world_x':edge,'old_floor_area_m2':area(oldfloor),'combined_floor_area_m2':area(newfloor),'restored_old_notch_area_m2':area(newfloor)-area(oldfloor),'bath_threshold_required_west_x':edge,'new_bath_entry_source_y':[390.5,405]},'limits':['Local material rotation is C and requires actual render inspection.','This transient floor refresh does not certify the separate bath threshold or combined routes.','All original camera/lights/routes remain unchanged in the saved candidate.']}
assert not changedold and not unexpected and all(v==[('MASTER_HORIZONTAL_GRAIN_ROTATE','Vector')] for v in channels.values())
assert all(x['pass'] for x in door)
(R/'qa/master-detail10-material-door-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
