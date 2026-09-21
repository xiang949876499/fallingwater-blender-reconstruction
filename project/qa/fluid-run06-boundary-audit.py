"""Outlet, bank and building-foot context for the existing run06 only."""
import sys,json,hashlib,math,time
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import water_integration as wi
import fluid_water
source=ROOT/'scene/Fallingwater_iteration04.blend';assert hashlib.sha256(source.read_bytes()).hexdigest()==wi.FROZEN04_SHA
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scene/Fallingwater_fluid_run06.blend'))
scene=bpy.context.scene;domain=scene.objects['WATER_Mantaflow_Local_Cascade']
with bpy.data.libraries.load(str(source),link=False) as (src,dst):
    dst.objects=[name for name in src.objects if name in {wi.SURFACE,'SITE_Continuous_BearRun_Terrain','MAIN_B_lower_platform'} or name.startswith('MAIN_B_foundation_pier_')]
for obj in dst.objects:scene.collection.objects.link(obj)
wi.repair_surface_normals(scene);surface=scene.objects[wi.SURFACE]
rocks=[wi._bvh(o) for o in scene.objects if o.get('fluid_collision') and o.name.startswith('SITE_')]
bed=wi._bvh(scene.objects['FLUID_Local_Closed_Riverbed']);terrain=wi._bvh(scene.objects['SITE_Continuous_BearRun_Terrain'])
lip=Vector((2.4,-2.83,0));down=Vector((-.882352948,-.470588356,0));across=Vector((.470588356,-.882352948,0))
def point(s,c):return lip+down*s+across*c
def hit(tree,p):
    h=tree.ray_cast(Vector((p.x,p.y,3)),Vector((0,0,-1)),13)
    return h[0].z if h[0] is not None else None
def context(p):
    values=[v for tree in rocks if (v:=hit(tree,p)) is not None]
    return {'xy':[p.x,p.y],'rock_top_m':max(values) if values else None,
            'local_closed_bed_m':hit(bed,p),'source_scene_terrain_m':hit(terrain,p)}
cross=[-4.2+i*8.4/60 for i in range(61)]
report={'run':'run06','outlet_along_m':4.3,'outlet_cross_m':cross,'outlet_static_context':[context(point(4.3,c)) for c in cross],
        'upstream_cross_context':[dict(along_m=s,cross_m=c,**context(point(s,c))) for s in (-2,-1,-.7,-.4,0,.2) for c in (-4.4,-3.4,0,3.4,4.4)],'frames':[]}
cfg=json.loads((ROOT/'data/site.json').read_text(encoding='utf-8'));site=fluid_water._site_module()
report['building_foot_context']=[]
for obj in dst.objects:
    if not obj.name.startswith('MAIN_B_'):continue
    corners=[obj.matrix_world@Vector(p) for p in obj.bound_box]
    bounds=[[min(p[i] for p in corners),max(p[i] for p in corners)] for i in range(3)]
    center=Vector(tuple((q[0]+q[1])/2 for q in bounds))
    dist,t,z,width,segment=site._river_near(center.x,center.y,cfg['river_path'])
    report['building_foot_context'].append({'object':obj.name,'bounds_m':bounds,'center_distance_to_program_creek_axis_m':dist,
        'program_creek_width_m':width,'program_base_water_z_m':z,'center_inside_program_channel':dist<width*.5,
        'clearance_top_above_program_water_m':bounds[2][1]-z,
        'hypothetical_global_source_head_raise_m':-2.634-z,
        'hypothetical_source_head_minus_top_m':-2.634-bounds[2][1],
        'note':'Bounding-box/river-plan screening only. No global water level raise is applied.'})
path=ROOT/'qa/fluid-run06-boundary-audit.json';started=time.perf_counter()
for frame in range(24,49):
    scene.frame_set(frame);water=wi._bvh(domain);river=wi._bvh(surface)
    samples=[]
    for c in cross:
        p=point(4.3,c)
        samples.append({'cross_m':c,'cached_water_z':hit(water,p),'program_water_z':hit(river,p),
                        'inset_water_z':[hit(water,point(4.3+offset,c)) for offset in (-.12,.12)]})
    report['frames'].append({'frame':frame,'samples':samples});wi._write(path,report)
    print('OUTLET_AUDIT',frame,flush=True)
report['seconds']=time.perf_counter()-started;report['status']='MEASURED_NOT_INSTALLED_OR_RENDER_ACCEPTED'
wi._write(path,report)
print('OUTLET_AUDIT_COMPLETE',round(report['seconds'],2),flush=True)
