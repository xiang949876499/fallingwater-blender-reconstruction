import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scene/Fallingwater_masonry_tower_candidate12a.blend'))
rows=[]
for name in ('MAIN_chimney_cap','MAIN_chimney_flue','MAIN_chimney_flue.001','MAIN_stone_tower_north','MAIN_stone_tower_west'):
 o=bpy.context.scene.objects[name]
 rows.append({'name':name,'mesh_users':o.data.users,'modifiers':[{'name':m.name,'type':m.type,'show_render':m.show_render,'show_viewport':m.show_viewport} for m in o.modifiers],
              'matrix':[list(r) for r in o.matrix_world],'vertices':[list(o.matrix_world@v.co) for v in o.data.vertices],'polygons':[list(p.vertices) for p in o.data.polygons]})
(R/'qa/masonry12b-guard-probe.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps([{k:r[k] for k in ('name','mesh_users','modifiers')} for r in rows],indent=2))
