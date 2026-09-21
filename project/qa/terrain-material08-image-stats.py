"""Read-only image statistics; no derived images or scene changes."""
import json, hashlib, math
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def stats(array):
    a=np.asarray(array,dtype=float)/255
    if a.ndim==2:return {'min':float(a.min()),'max':float(a.max()),'mean':float(a.mean()),'p05_p50_p95':[float(x) for x in np.percentile(a,[5,50,95])]}
    a=a[:,:,:3];lo=a.min(axis=2);hi=a.max(axis=2)
    return {'mean_rgb':a.mean(axis=(0,1)).tolist(),'channel_std':a.std(axis=(0,1)).tolist(),
            'mean_channel_range':float((hi-lo).mean()),'white_gt_095_allchannels_fraction':float((lo>.95).mean()),
            'mean_luma_709_encoded_not_scene_linear':float((a@np.array([.2126,.7152,.0722])).mean())}
textures=[]
for suffix in ('diff','rough','disp'):
    path=ROOT/f'assets/textures/forrest_ground_01_{suffix}_2k.jpg';im=Image.open(path)
    arr=np.asarray(im if suffix=='diff' else im.convert('L'))
    row={'file':str(path.relative_to(ROOT)),'size':list(im.size),'md5':hashlib.md5(path.read_bytes()).hexdigest(),'stats':stats(arr)}
    if suffix=='diff':
        c=np.asarray(im.convert('RGB'),dtype=float)/255
        lin=np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)
        row['linear_mean_rgb']=lin.mean(axis=(0,1)).tolist()
        row['linear_mean_rgb_after_current_multiply']=(lin*np.array([.85,.92,.80])).mean(axis=(0,1)).tolist()
    textures.append(row)
patches=[]
for camera,boxes in {'CAM_HERO':[(55,390,150,485)],'CAM_MAIN_L1_LOGGIA_B':[(65,170,155,260),(350,175,420,255)],'CAM_MAIN_L1_LIVING_A':[(450,175,550,205)]}.items():
    path=ROOT/f'renders/previews/iteration08-focus/{camera}.png';im=Image.open(path)
    for box in boxes:patches.append({'camera':camera,'box_xyxy':box,'stats':stats(np.asarray(im)[box[1]:box[3],box[0]:box[2]])})
probe=json.loads((ROOT/'qa/terrain-material08-probe.json').read_text(encoding='utf8'))
samples=[]
for row in probe['visible_samples']:
    samples.append({'camera':row['camera'],'pixel':row['pixel'],'world':row.get('terrain_hit'),
                    'first_hit':row.get('first_scene_hit'),'distance_m':row.get('distance_m'),
                    'mm_per_pixel':[round(d['world_m_per_pixel']*1000,2) for d in row.get('scale_derivatives',[])],
                    'exposure_multiplier':2**row.get('render_exposure_stops',0)})
result={'status':'READ_ONLY_TEXTURE_AND_RENDER_PIXEL_STATISTICS','textures':textures,'render_patches':patches,'ray_summary':samples,
         'limits':'Image patch RGB includes illumination/shadows and occasional vegetation, and is AgX display output. Do not divide it by source albedo or call it measured soil reflectance. Linear texture averages use standard sRGB conversion independently of Blender.'}
(ROOT/'qa/terrain-material08-image-stats.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps({'textures':textures,'ray_summary':samples},indent=2))
