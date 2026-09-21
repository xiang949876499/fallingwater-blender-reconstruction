"""Scientific scalar-map display of unchanged 16-bit source height data."""
import json, hashlib
from pathlib import Path
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'assets/textures/leaves_forest_ground_disp_2k.png'
im=Image.open(source);raw=np.asarray(im)
assert raw.ndim==2 and raw.max()>255
a=raw.astype(float)/65535
fig,ax=plt.subplots(figsize=(8,8),dpi=150)
plot=ax.imshow(a,cmap='gray',vmin=0,vmax=1,extent=[0,1.26,1.26,0],interpolation='nearest')
ax.set_title('leaves_forest_ground: original normalized height samples')
ax.set_xlabel('Scan width (m)');ax.set_ylabel('Scan height in texture plane (m)')
fig.colorbar(plot,ax=ax,label='16-bit value / 65535 (not measured z metres)',shrink=.75)
fig.tight_layout();fig.savefig(ROOT/'qa/terrain-material08-height-analysis.png');plt.close(fig)
report={'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'source_mode':im.mode,'dtype':str(raw.dtype),'size':list(im.size),'raw_min_max':[int(raw.min()),int(raw.max())],
        'normalized_min_max':[float(a.min()),float(a.max())],'normalized_p05_p50_p95':np.percentile(a,[5,50,95]).tolist(),
        'display':'Unchanged scalar source samples plotted grayscale; local direct view tool rejected the 16-bit PNG.',
        'height_z_amplitude':'Unknown scan z amplitude; shader bump settings remain C authored.'}
(ROOT/'qa/terrain-material08-height-analysis.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report))
