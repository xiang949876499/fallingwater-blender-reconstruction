"""Read saved prepared/baked switches; no state mutation or save."""
import bpy,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];rows=[]
for name in ['Fallingwater_water08_static_head24.blend1','Fallingwater_water08_static_head24.blend']:
 p=ROOT/'scene'/name;bpy.ops.wm.open_mainfile(filepath=str(p));o=bpy.context.scene.objects['WATER08_Static_Head_Control_Domain'];d=next(m.domain_settings for m in o.modifiers if m.type=='FLUID')
 row={'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'frame':bpy.context.scene.frame_current,'flags':{k:getattr(d,k) for k in ['use_foam_particles','use_spray_particles','use_bubble_particles','use_flip_particles','use_collision_border_bottom','use_collision_border_top','use_collision_border_front','use_collision_border_back','use_collision_border_left','use_collision_border_right','cache_directory']},'rna_descriptions':{k:d.bl_rna.properties[k].description for k in ['use_foam_particles','use_spray_particles','use_bubble_particles','use_collision_border_front']}}
 rows.append(row);print(json.dumps(row),flush=True)
(ROOT/'qa/water08-static-head24-settings-origin.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
