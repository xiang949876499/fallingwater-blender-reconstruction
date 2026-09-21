"""Integrate authored modules in a new background Blender process.

Run: blender --background --factory-startup --python scripts/build_scene.py
The script writes a checkpoint, never opens or clears an existing user file.
"""
import bpy, sys, json, math, csv, time, importlib.util, hashlib
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from fwlib import collection
from materials import build_materials
import main_house, guest_house, furnishings, navigation


def camera(name,location,target,lens=35,room=None,label=None,kind='QA'):
    data=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,data)
    collection('80_CAMERAS').objects.link(ob)
    ob.location=location;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    data.lens=lens;data.clip_start=.02;data.clip_end=2500;data.dof.use_dof=False
    ob['label']=label or name;ob['kind']=kind
    if room: ob['room_id']=room['id'];ob['reference']=room['reference']
    return ob


def lighting(scene):
    world=bpy.data.worlds.new('FW_Daylight');world.use_nodes=True;scene.world=world
    nodes=world.node_tree.nodes;links=world.node_tree.links
    sky=nodes.new('ShaderNodeTexSky');sky.sky_type='HOSEK_WILKIE'
    sky.sun_direction=Vector((-0.45,-.65,.65)).normalized();sky.turbidity=3.1;sky.ground_albedo=.22
    links.new(sky.outputs[0],nodes.get('Background').inputs['Color'])
    nodes.get('Background').inputs['Strength'].default_value=.55
    sun=bpy.data.lights.new('FW_Sun_Daylight','SUN');sun.energy=2.0;sun.angle=math.radians(3.0)
    ob=bpy.data.objects.new('FW_Sun_Daylight',sun);collection('70_LIGHTS').objects.link(ob)
    ob.rotation_euler=Vector((.45,.65,-.65)).to_track_quat('-Z','Y').to_euler()
    sun.color=(1,.91,.77)
    scene['lighting_preset']='Reference daylight; artistic exposure, not measured illuminance'
    scene['lighting_daylight']=json.dumps({'sun_energy':2,'sun_direction':[-.45,-.65,.65],'sun_angle_degrees':3,'sky_strength':.55})
    scene['lighting_evening']=json.dumps({'sun_energy':1.3,'sun_direction':[-.7,-.65,.22],'sun_angle_degrees':2,'sky_strength':.25,'sun_color':[1,.62,.34]})


def room_cameras(rooms):
    def inside(x,y,poly):
        odd=False;j=len(poly)-1
        for i,(xi,yi) in enumerate(poly):
            xj,yj=poly[j]
            if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi)+xi:odd=not odd
            j=i
        return odd
    for r in rooms:
        cx,cy=r['center'][:2];poly=r['polygon'];z=r['z'];h=r['height']
        candidates=[]
        for x,y in poly:
            q=(cx+(x-cx)*.70,cy+(y-cy)*.70)
            if inside(*q,poly):candidates.append(q)
        if not candidates:candidates=[(cx,cy)]
        a=max(candidates,key=lambda p:(p[0]-cx)**2+(p[1]-cy)**2)
        b=max(candidates,key=lambda p:(p[0]-a[0])**2+(p[1]-a[1])**2)
        eye=min(1.6,max(.5,h-.25))
        if r['kind'] in ('pool','foundation'):eye=1.6
        for suffix,p in [('A',a),('B',b)]:
            target=(cx,cy,z+eye-.12)
            if math.hypot(p[0]-cx,p[1]-cy)<.05:target=(cx,cy+.4,z+eye-.12)
            camera('CAM_'+r['id']+'_'+suffix,(*p,z+eye),target,28,r,r['label']+' / '+suffix)
        r['qa_cameras']=['CAM_'+r['id']+'_A','CAM_'+r['id']+'_B']
        r['model_status']='built; integrated visual and traversal QA pending'
        r['qa_status']='NOT_ACCEPTED'


def save_manifests(rooms,config):
    (ROOT/'rooms.json').write_text(json.dumps(rooms,ensure_ascii=False,indent=2),encoding='utf8')
    keys=['id','label','building','level','z','height','kind','center','entry','polygon','reference','evidence','model_status','qa_cameras','qa_status','notes']
    with (ROOT/'rooms.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');w.writeheader()
        for r in rooms:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items() if k in keys})
    dims=[];adj=[]
    for path in (ROOT/'data/main_house.json',ROOT/'data/guest_house.json'):
        d=json.loads(path.read_text(encoding='utf8'))
        for a in d['adjacency']:adj.append({'from':a['from'],'to':a['to'],'connection':a.get('type',a.get('connection')),'evidence':a.get('evidence'),'status':a.get('status','modeled; traversal not accepted')})
        for a in d['dimensions']:
            dims.append({'component_id':a['id'],'source':a['source'],'original':a.get('raw',a.get('original')),'original_unit':'feet/inches','meters':a['meters'],'method':a.get('method',a.get('reading')),'uncertainty_m':a.get('uncertainty_m'),'model_m':a.get('model_m',a.get('model_value_m')),'difference_m':a.get('delta_m'),'evidence':a.get('label_evidence',a.get('evidence')),'notes':a.get('note','')})
    adj.append({'from':'MAIN_L3_LINK','to':'GUEST_L1_STAIR_HALL','connection':'covered exterior stair canopy','evidence':'C cross-building elevation provisional','status':'modeled; traversal not accepted'})
    for file,rows in [('dimensions.csv',dims),('adjacency.csv',adj)]:
        with (ROOT/file).open('w',newline='',encoding='utf-8-sig') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (ROOT/'qa/resolved-config.json').write_text(json.dumps(config,ensure_ascii=False,indent=2),encoding='utf8')


def main():
    t=time.perf_counter();config=json.loads((ROOT/'config.json').read_text(encoding='utf8'))
    for name in ('scene','qa','renders/previews','renders/stills','renders/rooms','animation','assets','caches','delivery'):(ROOT/name).mkdir(parents=True,exist_ok=True)
    # A fresh --factory-startup process only; this guard prevents accidental user-scene loss.
    if bpy.data.filepath:raise RuntimeError('Build in a fresh background process, not an opened project.')
    for ob in list(bpy.data.objects):bpy.data.objects.remove(ob,do_unlink=True)
    # Factory startup brush assets are unused; do not ship installation-linked libraries.
    bpy.data.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
    mats=build_materials();ctx=SimpleNamespace(root=ROOT,mats=mats,config=config,collection=collection)
    print('BUILD main',flush=True);rooms=main_house.build(ctx)
    print('BUILD guest',flush=True);rooms+=guest_house.build(ctx)
    print('BUILD architectural details',flush=True)
    import architectural_detail
    architectural_detail.build(ctx,rooms)
    print('BUILD furniture',flush=True);furnishings.build(ctx,rooms)
    print('BUILD masonry surface detail',flush=True)
    import masonry_detail
    masonry_detail.build(ctx,rooms)
    print('BUILD site',flush=True)
    spec=importlib.util.spec_from_file_location('fw_site',ROOT/'scripts/site.py');site=importlib.util.module_from_spec(spec);spec.loader.exec_module(site);site.build(ctx)
    import water_integration
    water_integration.repair_surface_normals(bpy.context.scene)
    import asset_materials
    asset_materials.apply(ROOT)
    scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    scene.render.engine='CYCLES';scene.cycles.samples=512;scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.015
    scene.render.use_persistent_data=True
    scene.cycles.use_denoising=True;scene.cycles.max_bounces=10;scene.cycles.transmission_bounces=8;scene.cycles.transparent_max_bounces=12
    scene.cycles.device='CPU'
    if config['render']['device']=='HIP':
        try:
            prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='HIP';prefs.get_devices()
            for dev in prefs.devices:dev.use=dev.type=='HIP'
            scene.cycles.device='GPU'
        except Exception as e:print('HIP config fallback',e)
    scene.eevee.use_raytracing=True;scene.eevee.taa_render_samples=32
    scene.eevee.ray_tracing_options.resolution_scale='1';scene.eevee.ray_tracing_options.screen_trace_quality=1.0
    scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.3
    scene.render.resolution_x=3840;scene.render.resolution_y=2160;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.fps=24
    scene.frame_start=1;scene.frame_end=240;scene.frame_set(73)
    room_cameras(rooms)
    for name,pos,target,lens,label in [
      ('HERO',(-25,-28,2.5),(5.5,6,2.1),42,'经典溪流侧总览'),
      ('MAIN_OVERVIEW',(30,-23,14),(5,7,3),45,'主楼与悬挑'),
      ('UPSTREAM',(39,-10,3),(11,6,2),40,'上游与桥'),
      ('WATER_DETAIL',(-7,-13,-3),(5,-.4,-1.8),35,'瀑布与岩层'),
      ('ENTRY',(17,10.5,1.7),(8.4,11.8,1.5),32,'入口'),
      ('CONNECTOR',(17,27,11),(3,29,7.6),40,'主客楼连廊'),
      ('GUEST_OVERVIEW',(32,20,17),(10,40,10),38,'客房与泳池'),
      ('GUEST_POOL',(29,29,10.6),(17,38,9),35,'泳池与客房'),
      ('SITE_OVERVIEW',(55,-47,42),(7,21,4.2),42,'全场地总览')]:
        camera('CAM_'+name,pos,target,lens,label=label,kind='SHOWCASE')
    scene.camera=bpy.data.objects['CAM_HERO']
    import lighting as fw_lighting
    fw_lighting.build(scene,rooms)
    if (ROOT/'data/camera-settings-reviewed.json').exists():
        import camera_review
        camera_review.integrate(scene,rooms)
    if config.get('bank_path_repair',{}).get('enabled',False):
        import near_terrain_detail
        bpy.context.view_layer.update()
        bank_report=near_terrain_detail.build_bridge_front08(ctx,config['bank_path_repair'])
        bank_path=ROOT/'qa'/('bank-path-build-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')+'.json')
        bank_path.write_text(json.dumps(bank_report,ensure_ascii=False,indent=2),encoding='utf8')
    navigation.install(scene)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                space=area.spaces.active;space.shading.type='SOLID';space.shading.color_type='MATERIAL';space.overlay.show_overlays=False
                space.clip_start=.02;space.clip_end=2500;space.lens=42
                region=space.region_3d;region.view_perspective='PERSP';region.view_distance=43
                region.view_rotation=scene.camera.rotation_euler.to_quaternion();region.view_location=Vector((5.5,6,2.1))
    scene['project_status']='INTEGRATED_CHECKPOINT — NOT FINAL ACCEPTANCE'
    scene['build_timestamp_utc']=datetime.now(timezone.utc).isoformat()
    build_sources=list((ROOT/'scripts').glob('*.py'))+list((ROOT/'data').glob('*.json'))
    inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(build_sources)}
    inputs['config.json']=hashlib.sha256((ROOT/'config.json').read_bytes()).hexdigest()
    provenance=bpy.data.texts.new('FW_BUILD_INPUTS.json');provenance.write(json.dumps(inputs,indent=2))
    scene['evidence_baseline']=config['baseline'];scene['rooms_count']=len(rooms)
    save_manifests(rooms,config)
    for name,file in [('FW_CONFIG.json',ROOT/'config.json'),('FW_ROOMS.json',ROOT/'rooms.json')]:
        txt=bpy.data.texts.new(name);txt.write(file.read_text(encoding='utf8'))
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'scene/Fallingwater_working.blend'),compress=True)
    # The initial CSV above contains source declarations. Replace model values
    # with independent evaluated-mesh measurements only after the scene is saved.
    from dimension_audit import audit_dimensions
    audit_dimensions(ROOT, scene_path=bpy.data.filepath,
                     prefix='dimensions-build-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S'))
    report={'seconds':time.perf_counter()-t,'rooms':len(rooms),'objects':len(scene.objects),'meshes':len(bpy.data.meshes),'vertices_unique':sum(len(m.vertices) for m in bpy.data.meshes),'status':'BUILD_PASS; visual/navigation acceptance pending'}
    (ROOT/'qa/integration-build.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(report,flush=True)


if __name__=='__main__':main()
