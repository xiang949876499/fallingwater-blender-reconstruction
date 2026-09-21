"""Extract bounded, faithful local reference crops; no synthesis or scene access."""
from pathlib import Path
from PIL import Image
import hashlib, json

Q = Path(__file__).resolve().parent
W = Q.parents[1]
Image.MAX_IMAGE_PIXELS = 300_000_000
specs = [
    ('face0-top', Q/'master-source10-face0-2880.jpg', (0, 0, 2880, 1150), False, False),
    ('face1-top', Q/'panorama10/master-bedroom-face1.jpg', (0, 0, 800, 380), False, False),
    ('face2-top', Q/'master-source10-face2-2880.jpg', (0, 0, 2880, 1120), False, False),
    ('face3-top', Q/'master-detail10-face3-2880.jpg', (0, 0, 2880, 1540), False, False),
    ('main05-master', Q/'dimension-sources08-main05-original.tif', (298, 289, 435, 425), True, True),
    ('main10-master-section', W/'research/references/architecture/main-10-original.tif', (416, 514, 558, 582), True, True),
    ('main11-hearth', W/'research/references/architecture/main-11-sheet.jpg', (390, 280, 633, 469), False, False),
]
rows = []
for label, path, box, turn, normalized in specs:
    with Image.open(path) as raw:
        original_size = raw.size
        im = raw.rotate(-90, expand=True) if turn else raw.copy()
        native = tuple(round(v*im.width/1024) for v in box) if normalized else box
        pic = im.crop(native).convert('RGB')
        pic.thumbnail((1700, 1700))
        out = Q / ('master-ceiling11-source-'+label+'.png')
        pic.save(out)
        rows.append(dict(id=label, source=str(path), source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                         source_size=original_size, rotation_degrees=-90 if turn else 0,
                         oriented_size=im.size, box_input=box, box_unit='width1024' if normalized else 'native_pixels',
                         oriented_native_box=native, output=str(out), output_size=pic.size,
                         view_status='NOT_YET_VIEWED',
                         rights='REFERENCE_ONLY_EXCLUDE_PUBLIC_PACKAGE' if label.startswith('face') else 'HABS_SOURCE_REFERENCE'))
(Q/'master-ceiling11-source-crops.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps([dict(id=r['id'], output_size=r['output_size']) for r in rows]))
