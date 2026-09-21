"""Bounded full-scene dynamic water integration and actual seam evaluation."""
import sys,json,time,hashlib
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import water_integration as wi
source=ROOT/'scene/Fallingwater_iteration04.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()==wi.FROZEN04_SHA
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=8
report=wi.install_dynamic(scene)
report['source_scene']=str(source);report['source_sha256']=wi.FROZEN04_SHA
output=ROOT/'scene/Fallingwater_fluid_dynamic_run06.blend'
path=ROOT/'qa/water-dynamic-integration-run06.json'
domain=next(o for o in scene.objects if o.name.startswith('WATER_Mantaflow_Local_Cascade'))
lip=Vector((2.4,-2.83,0));down=Vector((-.882352948,-.470588356,0));across=Vector((.470588356,-.882352948,0))
report['evaluated_union_frames']=[];failures=[]
for frame in range(24,49):
    started=time.perf_counter();scene.frame_set(frame);tree=wi._bvh(domain)
    row={'frame':frame,'boundaries':{}}
    for spec in report['fixed_boundaries']:
        samples=[]
        for k in range(61):
            c=spec['cross'][0]+(spec['cross'][1]-spec['cross'][0])*k/60
            heights=[]
            for offset in (-.08,-.02,0,.02,.08):
                p=lip+down*(spec['target_along']+offset)+across*c
                hit=tree.ray_cast(Vector((p.x,p.y,0)),Vector((0,0,-1)),10)
                z=hit[0].z if hit[0] is not None else None
                valid=z is not None and (z>-3.35 if spec['name']=='UPSTREAM' else -6.3<z<-5.35)
                heights.append(z)
                if not valid:failures.append({'frame':frame,'boundary':spec['name'],'cross':c,'along_offset':offset,'z':z})
            samples.append({'cross':c,'along_offsets':[-.08,-.02,0,.02,.08],'water_z':heights})
        row['boundaries'][spec['name']]=samples
    row['seconds']=time.perf_counter()-started
    report['evaluated_union_frames'].append(row)
    report['union_invalid_samples']=failures
    wi._write(path,report)
    print('DYNAMIC_UNION_FRAME',frame,'invalid',len(failures),'seconds',round(row['seconds'],2),flush=True)
report['status']='FAIL_DYNAMIC_UNION_COVERAGE' if failures else 'PASS_SAMPLED_INTEGER_FRAME_SEAM_COVERAGE_PENDING_RENDER'
scene.frame_set(48);scene.camera=scene.objects['CAM_HERO']
data=bpy.data.cameras.new('CAM_WATER_OUTLET_QA');data.lens=40;data.clip_start=.02
outlet=bpy.data.objects.new('CAM_WATER_OUTLET_QA',data);bpy.data.collections['80_CAMERAS'].objects.link(outlet)
outlet.location=(-6,-12,-3.4);outlet.rotation_euler=(Vector((1,-4.2,-5.25))-outlet.location).to_track_quat('-Z','Y').to_euler()
outlet['owner']='fw_water_integration';outlet['fw_exposure']=.8
scene['water_integration_status']=report['status']
bpy.ops.wm.save_as_mainfile(filepath=str(output));report['output_scene']=str(output)
wi._write(path,report)
if '--render' in sys.argv and not failures:
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24
    scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.025;scene.cycles.use_denoising=True
    scene.render.resolution_x=960;scene.render.resolution_y=540;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.use_persistent_data=True
    folder=ROOT/'renders/previews/fluid-dynamic-run06';folder.mkdir(parents=True,exist_ok=True)
    for name in ('CAM_HERO','CAM_WATER_OUTLET_QA'):
        scene.camera=scene.objects[name];scene.view_settings.exposure=float(scene.camera.get('fw_exposure',.8))
        scene.render.filepath=str(folder/f'{name}.png')
        started=time.perf_counter();bpy.ops.render.render(write_still=True)
        report.setdefault('renders',[]).append({'camera':name,'path':scene.render.filepath,'seconds':time.perf_counter()-started,
                    'resolution':[960,540],'samples':24,'device':'CPU','threads':8,'frame':48})
        wi._write(path,report)
print('DYNAMIC_COMPLETE',report['status'],flush=True)
