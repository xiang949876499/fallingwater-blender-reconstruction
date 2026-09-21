"""Read-only10e corner rays and d->e protection; no gait repetition or helper execution."""
from pathlib import Path
from array import array
import bpy,bmesh,json,hashlib,struct
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
D=R/'scene/Fallingwater_master_bath_candidate10d.blend'
E=R/'scene/Fallingwater_master_bath_candidate10e.blend'
OUT=R/'qa/master-bath-detail10-independent-e-audit.json'
assert not OUT.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(D)=='2c7e8259b24936caad76979b985af86e5360548162cba3d666a9c7bd2b9dcca5'
expected='180c16e5d1cc2e77e4377560c00aa7a49560545924c3c42b9af6060461e8baee';assert sha(E)==expected
def val(v):
    if isinstance(v,(str,int,float,bool)) or v is None:return v
    try:return [float(x) for x in v]
    except Exception:return str(v)
def mats():
    result={}
    for m in bpy.data.materials:
        nodes=[];links=[]
        if m.node_tree:
            for n in m.node_tree.nodes:
                row={'name':n.name,'type':n.bl_idname,'inputs':{s.identifier:val(s.default_value) for s in n.inputs if hasattr(s,'default_value')}}
                for k in ('operation','rotation_type','blend_type','projection','interpolation','extension','space','vector_type','distribution','subsurface_method'):
                    if hasattr(n,k):row[k]=val(getattr(n,k))
                for k in ('image','object'):
                    if hasattr(n,k):row[k]=getattr(n,k).name if getattr(n,k) else None
                if hasattr(n,'color_ramp'):row['ramp']=[(e.position,list(e.color)) for e in n.color_ramp.elements]
                nodes.append(row)
            links=sorted((l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in m.node_tree.links)
        result[m.name]={'diffuse':list(m.diffuse_color),'nodes':sorted(nodes,key=lambda n:n['name']),'links':links}
    return result
def objects():
    result={};cache={}
    for o in bpy.context.scene.objects:
        row={'type':o.type,'matrix':[list(v) for v in o.matrix_world],'parent':o.parent.name if o.parent else None,
             'render_visible':not o.hide_render,'viewport_visible':not o.hide_viewport,'collections':sorted(c.name for c in o.users_collection)}
        if o.type=='MESH':
            key=o.data.as_pointer()
            if key not in cache:
                h=hashlib.sha256();a=array('f',[0.0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a);h.update(a.tobytes())
                for f in o.data.polygons:h.update(struct.pack('<IIB',len(f.vertices),f.material_index,f.use_smooth));h.update(struct.pack('<'+'I'*len(f.vertices),*f.vertices))
                cache[key]=h.hexdigest()
            row['mesh']=cache[key];row['materials']=[m.name if m else None for m in o.data.materials]
            row['modifiers']=[(m.name,m.type) for m in o.modifiers]
        elif o.type=='CURVE':
            row['curve']=[{'type':s.type,'points':[list(p.co) for p in s.points],
                'bezier':[(list(p.co),list(p.handle_left),list(p.handle_right)) for p in s.bezier_points]} for s in o.data.splines]
            row['curve_settings']=[o.data.bevel_depth,o.data.bevel_resolution,o.data.resolution_u,o.data.use_fill_caps]
            row['materials']=[m.name if m else None for m in o.data.materials]
        elif o.type=='LIGHT':row['light']=[o.data.type,o.data.energy,list(o.data.color)]
        elif o.type=='CAMERA':row['camera']=[o.data.type,o.data.lens,o.data.clip_start,o.data.clip_end,o.data.sensor_width]
        result[o.name]=row
    return result
bpy.ops.wm.open_mainfile(filepath=str(D));before=objects();mat_before=mats()
bpy.ops.wm.open_mainfile(filepath=str(E));bpy.context.scene.render.threads_mode='FIXED';bpy.context.scene.render.threads=4
after=objects();mat_after=mats()
changed={n:{'before':before[n],'after':after[n]} for n in before.keys()&after.keys() if before[n]!=after[n]}
removed=sorted(before.keys()-after.keys());added=sorted(after.keys()-before.keys())
unexpected=[n for n in changed if not n.startswith('MASTER_BATH10_south_window_') and n!='MASTER_BATH10_gathered_curtain']
curtain_geometry_unchanged=before['MASTER_BATH10_gathered_curtain']['mesh']==after['MASTER_BATH10_gathered_curtain']['mesh']
material_changes=[n for n in mat_before if n not in mat_after or mat_before[n]!=mat_after[n]]
# Regional evaluated geometry supplies actual closure probes, with glass retained.
deps=bpy.context.evaluated_depsgraph_get();vs=[];fs=[];owners=[];face_mats=[];target_mesh=[]
for o in bpy.context.scene.objects:
    if o.type not in ('MESH','CURVE') or o.name.startswith(('QA_','REF_')):continue
    corners=[o.matrix_world@Vector(p) for p in o.bound_box]
    if any(max(v[k] for v in corners)<lo or min(v[k] for v in corners)>hi for k,(lo,hi) in enumerate(((4.5,5.7),(6.35,7.35),(3.65,5.1)))):continue
    ev=o.evaluated_get(deps);m=ev.to_mesh();base=len(vs)
    vs.extend(o.matrix_world@v.co for v in m.vertices)
    fs.extend(tuple(base+i for i in f.vertices) for f in m.polygons);owners.extend([o.name]*len(m.polygons))
    face_mats.extend(m.materials[f.material_index].name if len(m.materials)>f.material_index else None for f in m.polygons)
    if o.name.startswith(('MASTER_BATH10_south_window_','MASTER_BATH10_southwest_return_')):
        bm=bmesh.new();bm.from_mesh(m);target_mesh.append({'name':o.name,'boundary':sum(e.is_boundary for e in bm.edges),
          'nonmanifold':sum(not e.is_manifold for e in bm.edges),'volume':bm.calc_volume(signed=True)});bm.free()
    ev.to_mesh_clear()
tree=BVHTree.FromPolygons(vs,fs,epsilon=0);rays=[]
for x in (4.988,4.999,5.003,5.008,5.013,5.017,5.028):
    for z in (3.75,4.0,4.40,4.80,4.95):
        co,no,ix,dd=tree.ray_cast(Vector((x,6.95,z)),Vector((0,-1,0)),.45)
        rays.append({'x':x,'z':z,'control':x in (4.988,5.028),
          'hit':{'object':owners[ix],'material':face_mats[ix],'point':list(co),'normal':list(no),'distance':dd} if co is not None else None})
rec={'candidate':str(E),'candidate_sha256':sha(E),'d_sha256':sha(D),'candidate_unchanged':sha(E)==expected,
     'status':'PASS_CLOSED_CORNER_SCOPE_PROTECTED' if all(r['hit'] for r in rays) and not unexpected and not material_changes and removed==['MASTER_BATH10_southwest_return_mullion_1'] and not added and curtain_geometry_unchanged else 'FAIL',
     'before_object_count':len(before),'after_object_count':len(after),'changed':changed,'removed':removed,'added':added,
     'unexpected_changed':unexpected,'unchanged_object_count':len(before.keys()&after.keys())-len(changed),'curtain_geometry_unchanged':curtain_geometry_unchanged,
     'source_materials_count':len(mat_before),'changed_source_materials':material_changes,'added_materials':sorted(mat_after.keys()-mat_before.keys()),
     'actual_white_curtain_material':mat_after['FW_MasterBath_WhiteCurtain10'],'rays':rays,'evaluated_window_topology':target_mesh,
     'limits':['No gait or whole-scene route repetition: d gait evidence retained only because floors,body obstacles,fixtures and routes are unchanged.',
       'Object protection compares actual raw geometry/world transforms/material slots/visibility/curve settings/light and camera basics; material protection compares complete stored node links/input values and ramps. Not a binary.blend equality claim.',
       'No render or save; visual acceptance separately reviewed.']}
OUT.write_text(json.dumps(rec,indent=2),encoding='utf-8')
print(json.dumps({'status':rec['status'],'changed':sorted(changed),'removed':removed,'added':added,
 'unchanged_objects':rec['unchanged_object_count'],'material_changes':material_changes,'new_materials':rec['added_materials'],
 'seam_rays_pass':sum(bool(r['hit']) for r in rays),'seam_rays_total':len(rays)},indent=2))
