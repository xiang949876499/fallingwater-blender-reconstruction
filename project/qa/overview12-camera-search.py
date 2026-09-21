"""Search visible exterior camera positions; never move scene geometry."""
from pathlib import Path
import bpy,math,json,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'scene/Fallingwater_iteration10.blend'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()=='1e7b17d9c2396513f005724e50788bf834097eedb401b91a7f1030825e2c4ed9'
bpy.ops.wm.open_mainfile(filepath=str(SRC));scene=bpy.context.scene;scene.frame_set(48)
deps=bpy.context.evaluated_depsgraph_get()
def cast(p,d,length):
    hit,loc,normal,index,obj,matrix=scene.ray_cast(deps,Vector(p),Vector(d).normalized(),distance=length)
    return {'name':obj.name,'point':list(loc),'distance':(loc-Vector(p)).length} if hit else None
target=Vector((3.7,7.0,3.2));rows=[]
for azimuth in (-65,-50,-35,-20,-5,10,25,40,55,70):
    for radius in (24,32,40,48):
        for z in (7,11,15,19,23):
            angle=math.radians(azimuth);eye=target+Vector((radius*math.cos(angle),radius*math.sin(angle),z-target.z))
            nearby=[cast(eye,d,.45) for d in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))]
            if any(nearby):continue
            rotation=(target-eye).to_track_quat('-Z','Y')
            # Explicit same35mm full-frame lens,16:9 image; actual scene hits.
            rays=[]
            for u in (-.8,-.4,0,.4,.8):
                for v in (-.7,-.35,0,.35,.7):
                    direction=rotation@Vector((u*18/35,v*10.125/35,-1)).normalized()
                    hit=cast(eye,direction,150)
                    rays.append({'uv':[u,v],'hit':hit})
            main=sum(r['hit'] is not None and r['hit']['name'].startswith('MAIN_') for r in rays)
            vegetation=sum(r['hit'] is not None and (r['hit']['name'].startswith(('FW_Tree','Tree','SITE_TREE','SITE_Understory')) or 'leaf' in r['hit']['name'].lower() or 'branch' in r['hit']['name'].lower()) for r in rays)
            near=sum(r['hit'] is not None and r['hit']['distance']<3 for r in rays)
            center=rays[12]['hit'];center_main=center is not None and center['name'].startswith('MAIN_')
            score=main*3-vegetation-near*4+(3 if center_main else -4)-abs(z-11)*.035
            rows.append({'location':list(eye),'target':list(target),'lens':35,'exposure':.8,
                         'score':score,'main_hits':main,'vegetation_hits':vegetation,'near_hits':near,
                         'center_main':center_main,'scope':'Exterior flying overview, not a surveyed photo or pedestrian station','rays':rays})
rows.sort(key=lambda r:-r['score'])
result={'source':str(SRC),'frame':48,'geometry_edited':False,'candidate_count':len(rows),'top':rows[:12],
        'limits':'Visibility ranking only; root actual render required. Trees are retained.'}
(ROOT/'qa/overview12-camera-search.json').write_text(json.dumps(result,indent=2),encoding='utf8')
best={k:rows[0][k] for k in ('location','target','lens','exposure')}
(ROOT/'qa/overview12-camera-settings.json').write_text(json.dumps({'CAM_MAIN_OVERVIEW':best},indent=2),encoding='utf8')
print(json.dumps({'candidates':len(rows),'best':best,'score':rows[0]['score'],'main_hits':rows[0]['main_hits']}),flush=True)
