"""Exact horizontal liquid sections; avoids a steep sheet skipped by vertical grids."""
import sys,time,json,math,statistics
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import water_integration as wi
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scene/Fallingwater_fluid_run06.blend'))
scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=8
domain=scene.objects['WATER_Mantaflow_Local_Cascade']
lip=Vector((2.4,-2.83,0));down=Vector((-.882352948,-.470588356,0));across=Vector((.470588356,-.882352948,0))
cc=[-3.4+i*6.8/60 for i in range(61)];levels=[-3.06,-3.10,-3.14]
def point(s,c,z):
    p=lip+down*s+across*c;p.z=z;return p
def top(tree,p):
    p=p.copy();p.z=0;h=tree.ray_cast(p,Vector((0,0,-1)),10)
    return h[0].z if h[0] is not None else None
def intervals(tree,c,z):
    cursor=-.65;inside=None;result=[];crossings=[]
    for _ in range(24):
        h=tree.ray_cast(point(cursor,c,z),down,1.5-cursor)
        if h[0] is None:break
        s=(h[0]-lip).dot(down);n=h[1].dot(down)
        crossings.append([s,n])
        if n<0:inside=s
        elif inside is not None:
            if s-inside>.003:result.append([inside,s])
            inside=None
        cursor=s+.0001
        if cursor>1.3:break
    return result,crossings
report={'run':'run06','cross_m':cc,'levels_m':levels,'frames':[],
        'scope':'Exact horizontal BVH ray entering/exiting intervals on actual cached liquid, then all-frame common volume and exact top-height validation'}
path=ROOT/'qa/fluid-section-profile-run06.json';started=time.perf_counter()
for frame in range(24,49):
    scene.frame_set(frame);tree=wi._bvh(domain);rows=[]
    for z in levels:
        values=[intervals(tree,c,z) for c in cc]
        rows.append({'z':z,'intervals':[v[0] for v in values],'crossings':[v[1] for v in values]})
    report['frames'].append({'frame':frame,'levels':rows});wi._write(path,report)
    print('SECTION_PROFILE',frame,'seconds',round(time.perf_counter()-started,2),flush=True)
common=[]
for index,z in enumerate(levels):
    points=[]
    for j,c in enumerate(cc):
        bands=[[-.65,1.3]]
        for frame in report['frames']:
            bands=[[max(a[0],b[0]),min(a[1],b[1])] for a in bands for b in frame['levels'][index]['intervals'][j]
                   if min(a[1],b[1])-max(a[0],b[0])>.006]
        band=max(bands,key=lambda b:b[1]-b[0]) if bands else None
        points.append({'cross_m':c,'common_intervals':bands,
                       'along_m':band[1]-.003 if band else None})
    common.append({'z':z,'points':points,'missing_columns':sum(p['along_m'] is None for p in points)})
report['common_sections']=common;report['exact_top_frames']=[]
for frame in range(24,49):
    scene.frame_set(frame);tree=wi._bvh(domain)
    rows=[]
    for section in common:
        rows.append({'z':section['z'],'top_z':[top(tree,point(p['along_m'],p['cross_m'],0)) if p['along_m'] is not None else None for p in section['points']]})
    report['exact_top_frames'].append({'frame':frame,'levels':rows});wi._write(path,report)
    print('SECTION_TOP',frame,flush=True)
report['seconds']=time.perf_counter()-started;report['status']='MEASURED_NOT_VISUAL_OR_HYDRAULIC_ACCEPTANCE'
wi._write(path,report)
print('SECTION_COMPLETE',[(s['z'],s['missing_columns']) for s in common],flush=True)
