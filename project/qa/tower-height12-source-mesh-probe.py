"""Read-only actual horizontal terrace/coping/core/outlet surfaces, frame48."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];Q=R/'qa';sys.path.insert(0,str(Q))
import shrub08_auditlib as audit
P=R/'scene/Fallingwater_iteration10.blend';SHA='1e7b17d9c2396513f005724e50788bf834097eedb401b91a7f1030825e2c4ed9'
assert hashlib.sha256(P.read_bytes()).hexdigest()==SHA
bpy.ops.wm.open_mainfile(filepath=str(P));bpy.context.scene.frame_set(48);dep=bpy.context.evaluated_depsgraph_get()
names=['MAIN_chimney_cap','MAIN_chimney_flue','MAIN_chimney_flue.001','MAIN_stone_tower_west','MAIN_stone_tower_north',
       'MAIN_L1_TERRACE_W_finish','MAIN_L1_TERRACE_W_slab','MAIN_L1_TERRACE_E_finish','MAIN_L1_TERRACE_E_slab',
       'MAIN_L2_TERRACE_S_finish','MAIN_L2_TERRACE_S_slab','MAIN_L3_TERRACE_finish','MAIN_L3_TERRACE_slab']
rows=[];missing=[]
for name in names:
 o=bpy.context.scene.objects.get(name)
 if o is None:missing.append(name);continue
 e=o.evaluated_get(dep);m=e.to_mesh();verts=[e.matrix_world@v.co for v in m.vertices];surfaces=[]
 for poly in m.polygons:
  normal=e.matrix_world.to_3x3().inverted().transposed()@poly.normal;normal.normalize()
  vs=[verts[i] for i in poly.vertices]
  if normal.z>.99999 and max(v.z for v in vs)-min(v.z for v in vs)<1e-5:
   surfaces.append({'polygon':poly.index,'world_normal':list(normal),'z_m':sum(v.z for v in vs)/len(vs),'world_vertices':[list(v) for v in vs],
                    'evaluated_vertex_ids':list(poly.vertices),'centroid_world':list(sum(vs,Vector())/len(vs))})
 row={'object':name,'materials':[m.name if m else None for m in o.data.materials],'bounds':[[min(v[i] for v in verts),max(v[i] for v in verts)] for i in range(3)],
      'horizontal_upward_surfaces':surfaces,'properties':dict(o.items()),'physical_hash':audit.physical_hash(o)}
 e.to_mesh_clear();rows.append(row)
index={r['object']:r for r in rows};zero=max(t['z_m'] for t in index['MAIN_L1_TERRACE_W_finish']['horizontal_upward_surfaces'])
nominal=(32*12+9.5)*.0254
comparisons=[]
for name in names[:5]:
 top=max(t['z_m'] for t in index[name]['horizontal_upward_surfaces']);span=top-zero
 comparisons.append({'upper_object':name,'upper_surface_z_m':top,'lower_object':'MAIN_L1_TERRACE_W_finish','lower_finished_surface_z_m':zero,
                     'actual_relative_height_m':span,'nominal_m':nominal,'difference_m':span-nominal,
                     'role':'proposed continuous finished masonry/coping counterpart' if name=='MAIN_chimney_cap' else 'diagnostic only; do not substitute this endpoint'})
texts=[{'name':t.name,'contains_main_datum':'Main level terrace' in t.as_string()} for t in bpy.data.texts if 'config' in t.name.lower() or 'main' in t.name.lower()]
out={'status':'READ_ONLY_ENDPOINT_PROBE_COMPLETE_NO_MODEL_CHANGE','source':str(P),'source_sha256':SHA,'frame':48,'objects':rows,'missing_requested_names':missing,
     'comparisons':comparisons,'nominal_label':'MAIN TOWER 32 ft9 1/2 in','label_evidence':'A printed HABS datum','endpoint_mapping_evidence':'C graphic-to-current-model identification; source marker not an explicit component-name label',
     'datum_model_world_offset_m':zero,'z0_is_not_finished_terrace':True,'embedded_text_inventory':texts,'saved':False,'rendered':False,
     'source_unchanged':hashlib.sha256(P.read_bytes()).hexdigest()==SHA}
(Q/'tower-height12-source-mesh-probe.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({'comparisons':comparisons,'missing':missing,'source_unchanged':out['source_unchanged']},indent=2))
