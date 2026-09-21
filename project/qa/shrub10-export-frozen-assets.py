"""Export the exact four accepted mesh datablocks as a portable asset library."""
from pathlib import Path
import bpy,sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import understory_detail
source=ROOT/'scene/Fallingwater_shrub_integration09.blend'
output=ROOT/'assets/models/site_understory16.blend'
report=ROOT/'qa/shrub10-frozen-assets-export.json'
assert not output.exists() and not report.exists()
assert hashlib.sha256(source.read_bytes()).hexdigest()=='3de043c500dc6735bcdefe8f4a5362d2afa65387a38b9f24768a2862fff5fa80'
bpy.ops.wm.open_mainfile(filepath=str(source))
meshes=set();rows=[]
for data in understory_detail.APPROVED['assets'].values():
    for part in ('branch','leaf'):
        mesh=bpy.data.meshes[data['new_'+part+'_mesh']]
        signature=understory_detail.mesh_signature(mesh)
        assert signature==data['new_'+part+'_signature']
        meshes.add(mesh);rows.append({'mesh':mesh.name,'signature':signature,
          'vertices':len(mesh.vertices),'polygons':len(mesh.polygons),
          'materials':[m.name if m else None for m in mesh.materials]})
bpy.data.libraries.write(str(output),meshes,path_remap='RELATIVE',fake_user=True,compress=True)
record={'status':'EXPORTED_EXACT_ACCEPTED_MESHES_ROUNDTRIP_PENDING','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'library_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'library_bytes':output.stat().st_size,'meshes':rows,
        'geometry_generated_or_edited':False,'reason':'Preserve accepted mesh identity across independent combined rebuilds'}
report.write_text(json.dumps(record,indent=2),encoding='utf8');print(json.dumps(record),flush=True)
