import bpy,json,hashlib
from pathlib import Path
root=Path(r'D:\zx\test\project')
records=[]
for obj in bpy.data.objects:
    if not obj.name.startswith(('TREE_Landmark_','TREE_Near_','TREE_Sapling_')) or not obj.name.endswith('_Branches'):continue
    asset=obj.data.name
    if not asset.startswith('TREE_Asset_'):continue
    index=int(asset.split('_')[2])
    records.append({'name':obj.name[:-9],'asset':index,'location':[round(v,6) for v in obj.location],
                    'angle':round(obj.rotation_euler.z,8),'scale':[round(v,7) for v in obj.scale]})
report={'source_scene':bpy.data.filepath,'source_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
        'purpose':'Preserve near trees across distant terrain/forest revisions; positions are still C authored placements, not surveyed individual trees.',
        'placements':sorted(records,key=lambda r:r['name'])}
meshes={m for m in bpy.data.meshes if m.name.startswith('TREE_Asset_')}
library=root/'qa'/'site_revision4_near_trees.blend'
bpy.data.libraries.write(str(library),meshes,fake_user=True,compress=True)
report['geometry_library']=str(library.relative_to(root))
report['geometry_library_sha256']=hashlib.sha256(library.read_bytes()).hexdigest()
(root/'qa'/'site_revision4_preserved.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('PRESERVED_NEAR_TREES',len(records))
