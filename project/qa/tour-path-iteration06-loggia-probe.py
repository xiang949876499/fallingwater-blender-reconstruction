"""Bounded real-mesh lower Loggia approach checks; no scene edits."""
import bpy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import tour
p=tour.Probe(bpy.context.scene,((10,21),(5,12),(-4,3)))
p.step_mode=True
down=tour.stair_mesh_points(bpy.context.scene,'MAIN_loggia_pool_stair_',True)
up=tour.stair_mesh_points(bpy.context.scene,'MAIN_pool_eastterrace_stair_',False)
def deck(x,y):return [x,y,-.9]
routes={
 'north_corrected_center':down+[deck(19.0736,9.1332),deck(19.126,8.345),deck(11.1612,8.345),deck(11.1612,6.07)]+up,
 'south_deck_alternative':down+[deck(19.0736,9.1332),deck(19.126,8.345),deck(19.126,6.07),deck(11.1612,6.07)]+up,
}
records=[]
for name,points in routes.items():
    parts=[{'index':i,'from':a,'to':b,'failure':p.segment(a,b,True)} for i,(a,b) in enumerate(zip(points,points[1:]))]
    records.append({'id':name,'points':points,'segments':parts,'failures':sum(r['failure'] is not None for r in parts)})
result={'scene':bpy.data.filepath,'stair_only':{'loggia':p.path(down,True),'east':p.path(up,True)},'routes':records}
(ROOT/'qa/tour-path-iteration06-loggia-probe.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('LOGGIA_PROBE',json.dumps({'stairs':result['stair_only'],'routes':[{'id':r['id'],'failures':[p for p in r['segments'] if p['failure']]} for r in records]}),flush=True)
