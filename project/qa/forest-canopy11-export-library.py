import bpy,sys,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];Q=ROOT/'qa';sys.path.insert(0,str(ROOT/'scripts'))
import forest_canopy_detail11 as entry
SOURCE=ROOT/'scene/Fallingwater_forest_canopy_candidate11a.blend';TARGET=ROOT/'assets/models/site_canopy18.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SOURCE)==entry.ACCEPTED_SHA256 and not TARGET.exists()
check=json.loads((Q/'forest-canopy11-check.json').read_text(encoding='utf-8'))
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene
meshes=[];records=[]
for row in check['selection']:
 for part,suffix in (('branch','_Branches'),('leaf','_Leaves')):
  obj=scene.objects[row['stem']+suffix];old=bpy.data.meshes[row[part+'_data']];new=obj.data
  records.append({'name':obj.name,'asset':row['asset'],'part':part,'matrix':[list(r) for r in obj.matrix_world],
                  'old_mesh':old.name,'old_signature':entry.mesh_signature(old),'new_mesh':new.name,'new_signature':entry.mesh_signature(new)})
  if not any(r['name']==new.name for r in meshes):
   new.calc_loop_triangles()
   meshes.append({'name':new.name,'old_mesh':old.name,'signature':entry.mesh_signature(new),'use_fake_user':new.use_fake_user,
                  'materials':[m.name if m else None for m in new.materials],'vertices':len(new.vertices),'polygons':len(new.polygons),
                  'triangles':len(new.loop_triangles),'original_vertices':len(old.vertices),'original_polygons':len(old.polygons),
                  'polygon_material_counts':{str(i):sum(p.material_index==i for p in new.polygons) for i in range(len(new.materials))}})
assert len(meshes)==6 and {r['name'] for r in records}==entry.TARGETS
bpy.data.libraries.write(str(TARGET),{bpy.data.meshes[r['name']] for r in meshes},path_remap='RELATIVE',fake_user=True,compress=True)
data={'schema_version':1,'signature_method':'forest11-strict-v1','acceptance':'ROOT_VISUALLY_ACCEPTED_LOCAL_18_ROOT_CANOPY_ONLY','environment_acceptance':'FAIL_GLOBAL_PHOTOREALISM',
      'accepted_candidate_sha256':entry.ACCEPTED_SHA256,'helper_path':'scripts/forest_canopy_detail11.py','helper_sha256':sha(ROOT/'scripts/forest_canopy_detail11.py'),
      'library_path':'assets/models/site_canopy18.blend','library_sha256':sha(TARGET),'library_bytes':TARGET.stat().st_size,
      'root_count':18,'target_object_count':36,'original_generator_retained':'scripts/forest_canopy11.py','generator_runtime_required':False,'qa_runtime_required':False,
      'material_binding':'Assign the existing original material into each existing loaded slot; never clear slots or regenerate per-face indices.',
      'content_check':'Exact ordered vertices, edge order, loop vertex/edge indices, ordered polygons, smooth/material indices, all UVs and supported attributes, material slot names; no canonical edge relaxation.',
      'meshes':meshes,'objects':records}
(ROOT/'data/forest_canopy11.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
(Q/'forest-canopy11-library-export.json').write_text(json.dumps({'status':'EXPORTED_EXACT_ACCEPTED_SIX_MESHES','source_sha256':sha(SOURCE),'library_sha256':sha(TARGET),'library_bytes':TARGET.stat().st_size,'mesh_count':6,'source_saved':False,'rendered':False},indent=2),encoding='utf-8')
print('FOREST11_EXPORTED',sha(TARGET),TARGET.stat().st_size,flush=True)
