from pathlib import Path
import hashlib, json, shutil
import bpy

ROOT = Path(__file__).resolve().parents[1]
source = ROOT/'delivery/iteration04-checkpoint/Fallingwater.blend'
destination = ROOT/'qa/portability/iteration04-relocated-v2'
destination.mkdir(parents=True, exist_ok=True)
target = destination/'Fallingwater.blend'
if target.exists():
    raise FileExistsError('Preserve the existing relocation evidence')
shutil.copy2(source,target)
bpy.ops.wm.open_mainfile(filepath=str(target))
images=[]
for image in bpy.data.images:
    if image.source in {'GENERATED','VIEWER'}:
        continue
    if not image.packed_file:
        raise RuntimeError('Unpacked dependency: '+image.name)
    packed_bytes=bytes(image.packed_file.data)
    # After moving the .blend, its unneeded historical relative image paths no
    # longer resolve. Compare packed bytes to the source texture ledger folder.
    original=ROOT/'assets/textures'/image.name
    original_hash=hashlib.sha256(original.read_bytes()).hexdigest()
    packed_hash=hashlib.sha256(packed_bytes).hexdigest()
    if original_hash!=packed_hash:
        raise RuntimeError('Packed image differs: '+image.name)
    # The separately reopened test scene cannot resolve the former source path.
    # Every image remains packed, and the source project is left untouched.
    image.filepath='//SOURCE_TEXTURES_INTENTIONALLY_ABSENT/'+image.name
    images.append({'name':image.name,'bytes':len(packed_bytes),'sha256':packed_hash,
                   'external_path_exists':Path(bpy.path.abspath(image.filepath)).exists()})
if any(i['external_path_exists'] for i in images):
    raise RuntimeError('The sentinel directory must not exist')
bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
report={'source':str(source),'relocated':str(target),'images':images,
        'status':'PACKED_BYTES_MATCH; all external image paths intentionally absent; independent reopen/render pending'}
(ROOT/'qa/portability-iteration04-preparation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(report['status'],flush=True)
