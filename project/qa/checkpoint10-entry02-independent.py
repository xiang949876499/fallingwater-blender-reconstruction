"""Read-only exact saved object/camera comparison; terrain may only reindex."""
from pathlib import Path
import bpy,hashlib,json,struct,time,ast,math,array,collections
R=Path(__file__).resolve().parents[1];Q=R/'qa'
FILES=[R/'scene/Fallingwater_iteration10.blend',R/'scene/Fallingwater_iteration10_rebuilt02.blend']
EXPECTED=['1e7b17d9c2396513f005724e50788bf834097eedb401b91a7f1030825e2c4ed9','c2a7ebb018c2a1d3773298b736b6519cdd5b8a996e7f1966321ded8798959629']
OUT=Q/'checkpoint10-entry02-independent.json'
TERRAIN='SITE_Continuous_BearRun_Terrain'
CAMERAS=['CAM_MAIN_L2_BATH_M_A','CAM_MAIN_L2_BATH_M_B','CAM_MAIN_L2_MASTER_A','CAM_MAIN_L2_MASTER_B']
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not OUT.exists() and [sha(p) for p in FILES]==EXPECTED
tree=ast.parse((Q/'master-ceiling11-build-check.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'prop_state','materials'}],type_ignores=[]),'<read-only material state utilities>','exec'))

def canonical_json(v):return json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':'))
def digest(v):return hashlib.sha256(canonical_json(v).encode()).hexdigest()
def matrix(m):return [list(r) for r in m]
def exact(v):
    if isinstance(v,(str,int,float,bool)) or v is None:return v
    if isinstance(v,bpy.types.ID):return (v.bl_rna.identifier,v.name)
    if hasattr(v,'to_dict'):return {k:exact(val) for k,val in v.to_dict().items()}
    if hasattr(v,'to_list'):return [exact(x) for x in v.to_list()]
    try:return [exact(x) for x in v]
    except TypeError:return str(v)

def terrain_state(ob):
    m=ob.data;v=[struct.pack('<3f',*(ob.matrix_world@p.co)) for p in m.vertices]
    verts=sorted(v);faces=[]
    for f in m.polygons:
        pts=[v[i] for i in f.vertices]
        # Cyclic shifts allowed; reversal expressly forbidden.
        loop=min(tuple(pts[i:]+pts[:i]) for i in range(len(pts)))
        faces.append(struct.pack('<IIB',len(loop),f.material_index,f.use_smooth)+b''.join(loop))
    faces.sort();edges=sorted(b''.join(sorted((v[e.vertices[0]],v[e.vertices[1]]))) for e in m.edges)
    seq={'vertex_multiset':verts,'oriented_face_multiset':faces,'edge_multiset':edges}
    summary={'counts':[len(m.vertices),len(m.edges),len(m.polygons)],'uv_layers':len(m.uv_layers),'material_names':[x.name if x else None for x in m.materials],'matrix_world':matrix(ob.matrix_world),
             'hashes':{k:hashlib.sha256(b''.join(val)).hexdigest() for k,val in seq.items()},'local_indexed_vertex_hash':hashlib.sha256(b''.join(struct.pack('<3f',*p.co) for p in m.vertices)).hexdigest()}
    return seq,summary

def animation(ob):
    if not ob.animation_data:return None
    ad=ob.animation_data;result={'action':None,'drivers':[],'nla_tracks':len(ad.nla_tracks)}
    if ad.action:
        rows=[]
        for li,l in enumerate(ad.action.layers):
            for si,s in enumerate(l.strips):
                for bi,b in enumerate(s.channelbags):
                    for f in b.fcurves:
                        rows.append({'layer':li,'strip':si,'bag':bi,'path':f.data_path,'axis':f.array_index,'extrapolation':f.extrapolation,
                            'keys':[(list(k.co),k.interpolation,list(k.handle_left),list(k.handle_right),k.handle_left_type,k.handle_right_type) for k in f.keyframe_points],
                            'modifiers':[prop_state(m) for m in f.modifiers]})
        result['action']=rows
    for d in ad.drivers:result['drivers'].append((d.data_path,d.array_index,d.driver.expression,d.driver.type))
    return result

def camera_state(ob,dep):
    return {'matrix_world':matrix(ob.matrix_world),'evaluated_matrix_world':matrix(ob.evaluated_get(dep).matrix_world),
            'matrix_local':matrix(ob.matrix_local),'rotation_mode':ob.rotation_mode,
            'active_rotation':list(ob.rotation_quaternion if ob.rotation_mode=='QUATERNION' else ob.rotation_axis_angle if ob.rotation_mode=='AXIS_ANGLE' else ob.rotation_euler),
            'location':list(ob.location),'scale':list(ob.scale),'data':prop_state(ob.data),'custom_properties':{k:exact(ob[k]) for k in sorted(ob.keys())},
            'constraints':[prop_state(c) for c in ob.constraints],'parent':ob.parent.name if ob.parent else None,'animation':animation(ob)}

def state(path,index):
    bpy.ops.wm.open_mainfile(filepath=str(path));scene=bpy.context.scene;scene.view_layers[0].update();dep=bpy.context.evaluated_depsgraph_get()
    cache={};objects={};aux={};cameras={};types=collections.Counter()
    for ob in scene.objects:
        types[ob.type]+=1;h=hashlib.sha256();h.update(ob.type.encode())
        for row in ob.matrix_world:h.update(struct.pack('<4f',*row))
        if ob.type=='MESH':
            mesh=ob.data;key=mesh.as_pointer()
            if key not in cache:
                mh=hashlib.sha256();mh.update(struct.pack('<III',len(mesh.vertices),len(mesh.edges),len(mesh.polygons)))
                for v in mesh.vertices:mh.update(struct.pack('<3f',*v.co))
                for a,b in sorted(tuple(sorted(e.vertices)) for e in mesh.edges):mh.update(struct.pack('<II',a,b))
                for p in mesh.polygons:
                    mh.update(struct.pack('<IIB',len(p.vertices),p.material_index,p.use_smooth));mh.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
                for uv in mesh.uv_layers:
                    mh.update(uv.name.encode())
                    for item in uv.data:mh.update(struct.pack('<2f',*item.uv))
                mh.update(repr([m.name if m else None for m in mesh.materials]).encode());cache[key]=mh.digest()
            h.update(cache[key])
        elif ob.type=='CURVE':
            h.update(repr((ob.data.bevel_depth,ob.data.bevel_resolution,ob.data.resolution_u)).encode())
            for sp in ob.data.splines:
                h.update(repr((sp.type,sp.use_cyclic_u)).encode())
                for p in sp.points:h.update(struct.pack('<4f',*p.co))
                for p in sp.bezier_points:
                    for v in (p.co,p.handle_left,p.handle_right):h.update(struct.pack('<3f',*v))
        elif ob.data:h.update(canonical_json(prop_state(ob.data)).encode())
        objects[ob.name]=h.hexdigest()
        aux[ob.name]={'hide_render':ob.hide_render,'hide_viewport':ob.hide_viewport,'hide_get':ob.hide_get(),'rotation_mode':ob.rotation_mode,'parent':ob.parent.name if ob.parent else None,
                      'modifiers':[prop_state(m) for m in ob.modifiers],'constraints':[prop_state(c) for c in ob.constraints],
                      'custom_properties':{k:exact(ob[k]) for k in sorted(ob.keys())},'collections':sorted(c.name for c in ob.users_collection)}
        if ob.type=='CAMERA':cameras[ob.name]=camera_state(ob,dep)
    seq,terrain=terrain_state(scene.objects[TERRAIN])
    rooms={r['id']:r for r in json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())}
    result={'path':str(path),'sha256':sha(path),'frame_current':scene.frame_current,'frame_range':[scene.frame_start,scene.frame_end],'active_camera':scene.camera.name,'objects':objects,'object_aux':aux,'types':dict(types),'rooms':rooms,'cameras':cameras,'materials':materials(),'terrain':terrain,
            'world':{'name':scene.world.name,'properties':prop_state(scene.world)},'camera_key_count':sum(len(f['keys']) for c in cameras.values() if c['animation'] and c['animation']['action'] for f in c['animation']['action'])}
    (Q/('checkpoint10-entry02-independent-state-'+str(index)+'.json')).write_text(json.dumps(result,indent=2),encoding='utf-8')
    print('READ_STATE',index,len(objects),dict(types),flush=True)
    return result,seq

started=time.monotonic();a,ta=state(FILES[0],0);b,tb=state(FILES[1],1)
common=set(a['objects'])&set(b['objects']);added=sorted(set(b['objects'])-set(a['objects']));removed=sorted(set(a['objects'])-set(b['objects']))
changed=sorted(n for n in common if a['objects'][n]!=b['objects'][n])
auxchanges={n:{k:{'source':a['object_aux'][n][k],'rebuild':b['object_aux'][n][k]} for k in a['object_aux'][n] if a['object_aux'][n][k]!=b['object_aux'][n][k]} for n in common if a['object_aux'][n]!=b['object_aux'][n]}
camchanges={n:{k:{'source':a['cameras'][n].get(k),'rebuild':b['cameras'][n].get(k)} for k in a['cameras'][n] if a['cameras'][n].get(k)!=b['cameras'][n].get(k)} for n in a['cameras'] if a['cameras'][n]!=b['cameras'].get(n)}
rooms={n:{k:{'source':a['rooms'][n].get(k),'rebuild':b['rooms'][n].get(k)} for k in set(a['rooms'][n])|set(b['rooms'][n]) if a['rooms'][n].get(k)!=b['rooms'][n].get(k)} for n in a['rooms'] if a['rooms'][n]!=b['rooms'].get(n)}
terrain_matches={k:ta[k]==tb[k] for k in ta}
terrain_matches.update({k:a['terrain'][k]==b['terrain'][k] for k in ('counts','uv_layers','material_names','matrix_world')})
terrain_pass=all(terrain_matches.values())
material_changes=sorted(n for n in set(a['materials'])|set(b['materials']) if a['materials'].get(n)!=b['materials'].get(n))
four={n:{'source':a['cameras'][n],'rebuild':b['cameras'][n],'all_fields_exactly_equal':a['cameras'][n]==b['cameras'][n],'both_quaternion':a['cameras'][n]['rotation_mode']==b['cameras'][n]['rotation_mode']=='QUATERNION'} for n in CAMERAS}
geometry_pass=not added and not removed and not(set(changed)-{TERRAIN}) and (TERRAIN not in changed or terrain_pass)
camera_pass=not camchanges and all(v['both_quaternion'] and v['all_fields_exactly_equal'] for v in four.values())
record={'status':'PASS_EXACT_SAVED_GEOMETRY_AND_CAMERAS' if geometry_pass and camera_pass else 'FAIL_SAVED_GEOMETRY_OR_CAMERA_REPRODUCTION',
        'source':{k:a[k] for k in ('path','sha256','frame_current','frame_range','active_camera','types','camera_key_count')},'rebuild':{k:b[k] for k in ('path','sha256','frame_current','frame_range','active_camera','types','camera_key_count')},
        'counts':[len(a['objects']),len(b['objects'])],'added':added,'removed':removed,'indexed_object_hash_changes':changed,'indexed_unchanged_count':len(common)-len(changed),
        'terrain_exact_reindex_proof':{'pass':terrain_pass,'matches':terrain_matches,'source':a['terrain'],'rebuild':b['terrain'],'method':'Direct equality of sorted byte sequences, with duplicate multiplicities retained; float32 coordinates exactly; oriented faces canonicalized by cyclic shift only, never reversed. No epsilon/rounding/tolerance.'},
        'four_quaternion_cameras':four,'all_camera_count':len(a['cameras']),'all_camera_changes':camchanges,'object_auxiliary_changes':auxchanges,'material_changes':material_changes,'room_metadata_changes':rooms,'room_id_sets_equal':set(a['rooms'])==set(b['rooms']),
        'geometry_reproduction_pass':geometry_pass,'camera_reproduction_pass':camera_pass,'all_materials_exactly_equal':not material_changes,'all_auxiliary_object_state_exactly_equal':not auxchanges,'all_room_metadata_exactly_equal':not rooms,
        'source_files_unchanged':[sha(p)==expected for p,expected in zip(FILES,EXPECTED)],'scripts_modified':False,'rendered':False,'saved':False,'navigation_rerun':False,'seconds':time.monotonic()-started,
        'limits':'Exact saved geometry/camera reproduction check, not photo/source precision/visual acceptance. Existing rebuild02 navigation results are only referenced, not rerun.'}
OUT.write_text(json.dumps(record,indent=2),encoding='utf-8')
(Q/'terrain10-rebuild02-independent.json').write_text(json.dumps(record['terrain_exact_reindex_proof'],indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in record.items() if k not in ('four_quaternion_cameras','room_metadata_changes','object_auxiliary_changes','all_camera_changes')},indent=2),flush=True)
assert geometry_pass and camera_pass and all(record['source_files_unchanged'])
