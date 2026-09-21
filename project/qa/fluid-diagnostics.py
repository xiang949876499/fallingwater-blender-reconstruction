"""Geometric diagnostics for actual cached liquid and its rock collision mesh."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[1]
run=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'run03'
bpy.ops.wm.open_mainfile(filepath=str(root/f'scene/Fallingwater_fluid_{run}.blend'))
domain=bpy.data.objects['WATER_Mantaflow_Local_Cascade']
lip=Vector((2.4,-2.83,0));down=Vector((-.882352948,-.470588356,0));across=Vector((-down.y,down.x,0))
def bvh(objects):
    deps=bpy.context.evaluated_depsgraph_get();verts=[];faces=[]
    for obj in objects:
        ev=obj.evaluated_get(deps);mesh=ev.to_mesh();offset=len(verts)
        verts.extend([obj.matrix_world@v.co for v in mesh.vertices])
        faces.extend([tuple(offset+j for j in p.vertices) for p in mesh.polygons])
        ev.to_mesh_clear()
    return BVHTree.FromPolygons(verts,faces)
rockobjs=list(bpy.data.collections['10_SITE_FLUID_COLLISION'].objects)
rocks=bvh(rockobjs)
out={'scope':'horizontal silhouette ray coverage and inlet exposed depth; not actual volume flux or final water acceptance','frames':[],'inlet_rock_tops':[]}
runsettings=json.loads((root/f'qa/fluid-{run}.json').read_text(encoding='utf-8'))['settings']
out['actual_inlet_rock_tops']=[]
along=runsettings.get('inflow_along_m',[-2.4,-1.85]);half=runsettings.get('inflow_half_width_m',4.1)
bottom=runsettings.get('inflow_bottom_m',-3.32)
for s in (along[0],sum(along)/2,along[1]):
    for ci in range(17):
        c=-half+2*half*ci/16;origin=lip+down*s+across*c;origin.z=0
        hit=rocks.ray_cast(origin,Vector((0,0,-1)),10)
        z=hit[0].z if hit[0] else -10
        out['actual_inlet_rock_tops'].append({'along':s,'cross':c,'rock_top_z':z,'source_bottom_m':bottom,'source_overlaps_rock':z>bottom})
for c in (-4,-3,-2,-1,0,1,2,3,4):
    origin=lip+down*(-2.1)+across*c;origin.z=0
    hit=rocks.ray_cast(origin,Vector((0,0,-1)),10)
    out['inlet_rock_tops'].append({'cross':c,'rock_top_z':hit[0].z if hit[0] else None})
last=domain.modifiers[0].domain_settings.cache_frame_end
for frame in (last//2,last):
    bpy.context.scene.frame_set(frame);water=bvh([domain]);rows=[]
    for z in (-3.6,-4.2,-4.8,-5.4):
        row=[]
        for ci in range(-8,9):
            c=ci*.5;origin=lip+down*8+across*c;origin.z=z
            rockhit=rocks.ray_cast(origin,-down,20);waterhit=water.ray_cast(origin,-down,20)
            row.append({'cross':c,'water_front_distance_m':waterhit[3] if waterhit[0] else None,
                        'rock_front_distance_m':rockhit[3] if rockhit[0] else None})
        rows.append({'z':z,'rays':row,'water_hit_count':sum(r['water_front_distance_m'] is not None for r in row)})
    out['frames'].append({'frame':frame,'rows':rows})
(root/f'qa/fluid-diagnostics-{run}.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({'inlet_rock_tops':out['inlet_rock_tops'],'actual_inlet_overlap_samples':[v for v in out['actual_inlet_rock_tops'] if v['source_overlaps_rock']], 'coverage':[{'frame':f['frame'],'water_hits':[(r['z'],r['water_hit_count']) for r in f['rows']]} for f in out['frames']]}),flush=True)
