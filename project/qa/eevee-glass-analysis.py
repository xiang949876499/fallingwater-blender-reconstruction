"""Verify completed diagnostic images and generate unretouched contact sheets."""
import hashlib
import json
import statistics
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

qa = Path(__file__).resolve().parent
variants = ['baseline', 'linked_thickness', 'thin_preview', 'thin_blended',
            'baseline-probe', 'thin_blended-probe-two-sided']
summary = {'static': [], 'sequence': {}, 'visual_acceptance': 'PENDING_HUMAN_IMAGE_REVIEW'}
sheet = Image.new('RGB', (960, 3*290), (25, 28, 30))
draw = ImageDraw.Draw(sheet)
for index, variant in enumerate(variants):
    directory = qa/('eevee-glass-'+variant)
    report = json.loads((directory/'report.json').read_text())
    frame = report['frames'][0]
    path = Path(frame['path'])
    image = Image.open(path).convert('RGB')
    assert image.size == (960, 540)
    assert hashlib.sha256(path.read_bytes()).hexdigest() == frame['sha256']
    x, y = (index % 2)*480, (index//2)*290
    sheet.paste(image.resize((480,270), Image.Resampling.LANCZOS), (x,y+20))
    draw.text((x+5,y+4),variant,fill='white')
    summary['static'].append({'variant': variant, 'seconds': frame['seconds'],
        'sha256': frame['sha256'], 'verified': True, 'size': image.size})
sheet.save(qa/'eevee-glass-six-variants-contact.png')
before = np.asarray(Image.open(qa/'eevee-glass-baseline/frame_0001.png').convert('RGB'),dtype=float)
thickness = np.asarray(Image.open(qa/'eevee-glass-linked_thickness/frame_0001.png').convert('RGB'),dtype=float)
diff = np.abs(before-thickness)
summary['thickness_comparison'] = {'mean_absolute_8bit_difference': float(diff.mean()),
    'p95': float(np.percentile(diff,95)), 'max': float(diff.max())}
directory = qa/'eevee-glass-thin_blended-probe-two-sided-sequence'
report = json.loads((directory/'report.json').read_text())
frames = report['frames']; assert len(frames) == 12
contact = Image.new('RGB', (1280,3*260),(25,28,30)); draw = ImageDraw.Draw(contact)
hashes = []; images = []
for i, frame in enumerate(frames):
    path = Path(frame['path'])
    image = Image.open(path).convert('RGB'); assert image.size == (960,540)
    digest = hashlib.sha256(path.read_bytes()).hexdigest(); assert digest == frame['sha256']
    hashes.append(digest); images.append(np.array(image,dtype=float))
    x,y=(i%4)*320,(i//4)*260
    contact.paste(image.resize((320,180),Image.Resampling.LANCZOS),(x,y+20))
    # Exact-pixel opening-window crop below each full-frame thumbnail.
    crop=image.crop((610,240,750,295))
    contact.paste(crop,(x,y+203))
    draw.text((x+4,y+3),f"Frame {i+1:02d} | {frame['offset_m']:.3f} m",fill='white')
contact.save(qa/'eevee-glass-12frames-contact.png')
adjacent = [float(np.abs(b-a).mean()) for a,b in zip(images,images[1:])]
summary['sequence'] = {'frames':12,'size':[960,540],'fps':24,'duration_seconds':.5,
    'translation_m':.24, 'all_hashes_verified':True, 'unique_frame_hashes':len(set(hashes)),
    'first_seconds':frames[0]['seconds'],'warm_median_seconds':statistics.median(f['seconds'] for f in frames[1:]),
    'total_seconds':sum(f['seconds'] for f in frames),'adjacent_full_frame_mae_8bit':adjacent,
    'metric_limitation':'Image difference includes intentional camera parallax and is not an isolated flicker measurement',
    'source_sha256':report['source_sha256'], 'geometry_and_cycles_invariants':report['invariants']}
(qa/'eevee-glass-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary['sequence'],indent=2))
