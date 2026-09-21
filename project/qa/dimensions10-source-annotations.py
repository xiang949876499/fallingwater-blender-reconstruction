"""Faithful QA excerpt plus visible annotation; no source data/geometry edits."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
R=Path(__file__).resolve().parents[1]
p=R/'qa/dimensions10-main10-section-west.png';im=Image.open(p).convert('RGB')
draw=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23)
# Original excerpt spans source x240..690; 2000px output (not display resized).
def xp(v):return round((v-240)/450*im.width)
pts={'free_edge_source_x':268.1,'first_fullheight_stone_face_source_x':387.0,'calibration_end_source_x':657.8}
for key,value in pts.items():
    x=xp(value);draw.line((x,500,x,1385),fill=(194,25,25),width=3)
draw.rectangle((135,20,1500,122),fill='white')
draw.text((145,28),'GRAPHICAL / C. L2 south cantilever, west-looking section.',font=font,fill='black')
draw.text((145,63),'Free edge -> first full-height L1 stone pier. Low seat / glazing excluded.',font=font,fill='black')
draw.text((145,94),'Calibration: printed 67 ft 2 in between bottom witness marks.',font=font,fill='black')
for x,text in [(xp(268.1)+8,'FREE'),(xp(387.0)+8,'STONE FACE'),(xp(657.8)-120,'CAL END')]:draw.text((x,475),text,font=font,fill=(194,25,25))
dest=R/'qa/dimensions10-main10-cantilever-annotated.png';im.save(dest)
detail=Image.open(p).crop((80,570,760,980));detail.save(R/'qa/dimensions10-main10-support-detail.png')
scale=20.4724/(657.8-268.1);value=(387.0-268.1)*scale
record={'source_excerpt':str(p),'excerpt_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'annotation':str(dest),'source_normalized_x':pts,'calibration_printed_label':'67 ft 2 in','calibration_m':20.4724,'calibration_normalized_span_px':657.8-268.1,'meters_per_normalized_pixel':scale,'graphical_span_normalized_px':387.0-268.1,'graphical_target_m':value,'endpoint_reading_bound_normalized_px_each':.5,'calibration_tick_bound_normalized_px_each':.5,'conservative_total_reading_bound_m':.08,'survey_absolute_accuracy_m':None,'evidence':'C graphical, A printed calibration label, source-to-pier model identity C','source_image_unmodified':True,'annotation_is_not_source_geometry':True,'view_status':'NOT_YET_VIEWED'}
(R/'qa/dimensions10-main10-cantilever-reading.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
manifest=R/'qa/dimensions10-source-crops.json';rows=json.loads(manifest.read_text(encoding='utf-8'))
for row in rows:row['view_status']='ACTUALLY_VIEWED';row['view_method']='view_image; faithful high-resolution archival excerpt'
manifest.write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps(record,indent=2))
