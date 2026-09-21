"""Separate source head from stable free discharge using the completed real cache."""
import sys,json,time,hashlib,statistics,math
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import water_integration as wi
source=ROOT/'scene/Fallingwater_iteration04.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()==wi.FROZEN04_SHA
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scene/Fallingwater_fluid_run06.blend'))
scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=8
domain=scene.objects['WATER_Mantaflow_Local_Cascade']
with bpy.data.libraries.load(str(source),link=False) as (src,dst):
    dst.objects=[wi.SURFACE,'SITE_Continuous_BearRun_Terrain']
for obj in dst.objects:scene.collection.objects.link(obj)
surface=scene.objects[wi.SURFACE];wi.repair_surface_normals(scene)
rocktrees=[wi._bvh(o) for o in scene.objects if o.get('fluid_collision')]
terrain=wi._bvh(scene.objects['SITE_Continuous_BearRun_Terrain'])
lip=Vector((2.4,-2.83,0));down=Vector((-.882352948,-.470588356,0));across=Vector((.470588356,-.882352948,0))
ss=[-.55+i*.025 for i in range(51)]
cc=[-3.4+i*6.8/60 for i in range(61)]
axis_s=[-8+i*.10 for i in range(141)]
def point(s,c=0):return lip+down*s+across*c
def hit(tree,p):
    h=tree.ray_cast(Vector((p.x,p.y,2)),Vector((0,0,-1)),12)
    return h[0].z if h[0] is not None else None
def rock(p):
    values=[z for tree in rocktrees if (z:=hit(tree,p)) is not None]
    z=hit(terrain,p)
    return {'collision_rock_top':max(values) if values else None,'scene_terrain_z':z,
            'visible_bed_top':max(values+([z] if z is not None else [])) if values or z is not None else None}
report={'run':'run06','frames':[],'along_m':ss,'cross_m':cc,'axis_s_m':axis_s,
        'source_top_m':-2.67,'source_bottom_m':-2.99,'source_along_m':[-1,-.42],
        'pool_boundary_top_m':-5.965,'isolevel_m':-3.06,
        'axis_bed':[rock(point(s)) for s in axis_s],
        'source_scene_sha256':wi.FROZEN04_SHA,'measurement_scope':'Actual top rays; regular profile uses exact cache. Fixed contour validation will be a separate exact ray pass.'}
path=ROOT/'qa/fluid-head-profile-run06.json';started=time.perf_counter()
for frame in range(24,49):
    scene.frame_set(frame);water=wi._bvh(domain);river=wi._bvh(surface)
    grid=[[hit(water,point(s,c)) for s in ss] for c in cc]
    iso=[]
    for values in grid:
        crossings=[]
        for i,(za,zb) in enumerate(zip(values,values[1:])):
            if za is not None and zb is not None and za>-3.06>=zb and abs(zb-za)<.35:
                crossings.append(ss[i]+(-3.06-za)/(zb-za)*.025)
        iso.append(crossings[0] if crossings else None)
    row={'frame':frame,'free_discharge_grid_z':grid,'isolevel_along_m':iso,
         'axis_water_z':[hit(water,point(s)) for s in axis_s],
         'axis_procedural_z':[hit(river,point(s)) for s in axis_s]}
    report['frames'].append(row);wi._write(path,report)
    print('HEAD_PROFILE',frame,'missing_iso',sum(s is None for s in iso),'seconds',round(time.perf_counter()-started,2),flush=True)
fixed=[]
for j,c in enumerate(cc):
    values=[f['isolevel_along_m'][j] for f in report['frames'] if f['isolevel_along_m'][j] is not None]
    s=statistics.median(values) if len(values)==25 else None
    fixed.append({'cross_m':c,'along_m':s,'along_min_m':min(values) if values else None,
                  'along_max_m':max(values) if values else None,'valid_frames':len(values),
                  'bed':rock(point(s,c)) if s is not None else None})
report['fixed_contour']=fixed;report['fixed_contour_frames']=[]
for frame in range(24,49):
    scene.frame_set(frame);water=wi._bvh(domain)
    values=[hit(water,point(q['along_m'],q['cross_m'])) if q['along_m'] is not None else None for q in fixed]
    report['fixed_contour_frames'].append({'frame':frame,'water_z':values})
    wi._write(path,report);print('FIXED_CONTOUR_EXACT',frame,flush=True)
report['seconds']=time.perf_counter()-started
report['status']='MEASURED_NOT_HYDRAULIC_OR_VISUAL_ACCEPTANCE'
wi._write(path,report)
print('HEAD_PROFILE_COMPLETE',round(report['seconds'],2),flush=True)
