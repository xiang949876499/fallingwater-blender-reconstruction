"""Unretouched side-by-side exposure contact sheet from actual saved renders."""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
folder = ROOT/'renders/previews/iteration05-focus'
cameras = ['CAM_MAIN_B_BATH_A', 'CAM_MAIN_B_BATH_B', 'CAM_MAIN_L1_LIVING_B',
           'CAM_GUEST_L1_LOUNGE_A', 'CAM_GUEST_POOL']
labels = [('original', ''), ('EV +0.8', '_EV0p8'), ('EV +1.6', '_EV1p6'), ('EV +2.4', '_EV2p4')]
canvas = Image.new('RGB', (1600, 1250), '#171b1e')
draw = ImageDraw.Draw(canvas)
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 13)
records = []
for row, camera in enumerate(cameras):
    for col, (label, suffix) in enumerate(labels):
        path = folder/(camera+suffix+'.png')
        im = Image.open(path).convert('RGB')
        if im.size != (960,540):
            raise ValueError('Unexpected source size '+str(path))
        draw.text((col*400+5,row*250+3), camera.removeprefix('CAM_')+' | '+label, font=font, fill='white')
        canvas.paste(im.resize((400,225),Image.Resampling.LANCZOS),(col*400,row*250+23))
        records.append({'path':str(path.relative_to(ROOT)), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
target = ROOT/'qa/iteration05-exposure-contact.jpg'
canvas.save(target, quality=94)
(ROOT/'qa/iteration05-exposure-contact.json').write_text(json.dumps({
    'sources':records, 'scope':'Unretouched resized contact sheet. Same-linear-render absolute exposure brackets; not separate lighting renders.'},indent=2),encoding='utf8')
print(target)
