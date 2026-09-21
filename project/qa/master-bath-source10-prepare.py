"""Read original institutional photo and make a source-plan inspection crop."""
from pathlib import Path
import urllib.request, urllib.parse, xml.etree.ElementTree as ET
import hashlib, json
from PIL import Image
root=Path(__file__).resolve().parents[1]
base='https://projects.mcah.columbia.edu/ha/panos/Fallingwater/Master-Bathroom/'
tree=ET.fromstring((root/'qa/panorama10/master-bathroom-config0.xml').read_bytes())
url=urllib.parse.urljoin(base,tree.find('input').get('tile2url'))
photo=root/'qa/master-bath-source10-face2-2880.jpg'
data=photo.read_bytes() if photo.exists() else urllib.request.urlopen(url,timeout=30).read(10000000)
if not photo.exists(): photo.write_bytes(data)
with Image.open(photo) as im:
    dimensions=im.size
    im.verify()
plan=root/'qa/dimension-sources08-main05-original.tif'
Image.MAX_IMAGE_PIXELS=300000000  # Known local HABS sheet,241081920pixels.
with Image.open(plan) as im:
    # This TIFF follows sheet04's landscape axes only after rotate -90.
    # Save a low-resolution whole sheet first; crop follows visual confirmation.
    im.thumbnail((1600,1600))
    im.convert('RGB').save(root/'qa/master-bath-source10-plan-whole.jpg',quality=94)
record={'page':base,'url':url,'path':photo.name,'sha256':hashlib.sha256(data).hexdigest(),
        'bytes':len(data),'dimensions':dimensions,'attribution':tree.find('userdata').attrib,
        'distribution':'REFERENCE_ONLY_EXCLUDE_PUBLIC_PACKAGE','actual_view':'NOT_VIEWED',
        'plan_path':str(plan.relative_to(root))}
(root/'qa/master-bath-source10-download.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(record))
