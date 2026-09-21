"""Make lossless, original-size QA contact pages from completed room renders."""
import hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'renders/room-contact-sheets/iteration07/views'
dest=ROOT/'renders/room-contact-sheets/iteration07/contact-review'
dest.mkdir(exist_ok=True)
cfg=json.loads((ROOT/'qa/camera07e-settings-frozen.json').read_text(encoding='utf-8'))
names=sorted(cfg)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pages=[]
for page_index in range(20):
    group=names[page_index*6:page_index*6+6]
    if not all((source/(name+'.png')).exists() for name in group):continue
    page_path=dest/f'page_{page_index+1:02d}.png'
    records=[]
    page=Image.new('RGB',(1280,1170),'#f1f0eb')
    draw=ImageDraw.Draw(page)
    for i,name in enumerate(group):
        p=source/(name+'.png')
        with Image.open(p) as img:
            assert img.size==(640,360), (p,img.size)
            x=(i%2)*640;y=(i//2)*390
            draw.text((x+8,y+5),name,fill='#171d23',font=font)
            page.paste(img.convert('RGB'),(x,y+30))
        records.append({'camera':name,'source':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':sha(p),'location_xy':[x,y+30],'source_dimensions':[640,360]})
    if not page_path.exists():page.save(page_path)
    pages.append({'page':str(page_path.relative_to(ROOT)).replace('\\','/'),'sha256':sha(page_path),'cameras':records})
benchmark=json.loads((source/'render-benchmark.json').read_text(encoding='utf-8'))
report={'scene_sha256':benchmark['scene_sha256'],'settings_sha256':sha(ROOT/'qa/camera07e-settings-frozen.json'),
        'method':'Lossless PNG contact pages, each2 columns x3 room-pair rows. Each source remains640x360 without resizing, color, brightness or geometry changes. Generating a page does not mean actually reviewed.',
        'expected_camera_count':120,'available_source_count':sum((source/(n+'.png')).exists() for n in names),
        'render_benchmark_status_at_build':benchmark['status'],'render_runs_at_build':len(benchmark['runs']),
        'page_count':len(pages),'pages':pages}
(ROOT/'qa/camera07-room-contact-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='pages'}))
