"""Read-only camera rays locate the actual nearby bare banks before detailing."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'scene/Fallingwater_geology_candidate07c.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.frame_set(48)
deps=bpy.context.evaluated_depsgraph_get();terrain=scene.objects['SITE_Continuous_BearRun_Terrain']
bvh=BVHTree.FromObject(terrain,deps);records=[]
for name in ('CAM_HERO','CAM_MAIN_L1_LIVING_A','CAM_MAIN_L1_LOGGIA_B'):
    camera=scene.objects[name];frame=camera.data.view_frame(scene=scene)
    xmin=min(v.x for v in frame);xmax=max(v.x for v in frame);ymin=min(v.y for v in frame);ymax=max(v.y for v in frame);z=frame[0].z
    visible=[];all_near=[]
    for row in range(18):
        for col in range(32):
            ray=(camera.matrix_world.to_3x3()@Vector((xmin+(xmax-xmin)*(col+.5)/32,ymin+(ymax-ymin)*(row+.5)/18,z))).normalized()
            hit,normal,index,distance=bvh.ray_cast(camera.location,ray,150)
            if hit is None or (hit-Vector((5,5,0))).length>40:continue
            point={'pixel_grid':[col,row],'world':list(hit),'normal':list(normal),'distance':distance}
            all_near.append(point)
            origin=camera.location.copy();first=None
            for attempt in range(12):
                ok,p,n,face,obj,matrix=scene.ray_cast(deps,origin,ray,distance=distance+1)
                if not ok:break
                if obj.hide_render or any(m and ('glass' in m.name.lower() or 'water' in m.name.lower()) for m in getattr(obj.data,'materials',[])):
                    origin=p+ray*.025;continue
                first=obj.name;break
            if first==terrain.name:visible.append(point)
    def bounds(points):return [[round(min(p['world'][k] for p in points),3),round(max(p['world'][k] for p in points),3)] for k in range(3)] if points else None
    records.append({'camera':name,'camera_position':list(camera.location),'visible_points':visible,'visible_bounds':bounds(visible),'near_terrain_bounds':bounds(all_near)})
out={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'scope':'32x18 first-hit scene rays with transparent/water/hidden objects skipped; diagnostic only, no render','cameras':records}
(ROOT/'qa/bank07-visible-terrain-probe.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print(json.dumps([{k:r[k] for k in ('camera','camera_position','visible_bounds','near_terrain_bounds')}|{'visible_points':len(r['visible_points'])} for r in records],indent=2),flush=True)
