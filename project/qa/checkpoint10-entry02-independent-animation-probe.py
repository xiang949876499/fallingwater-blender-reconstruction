"""Read saved affected camera matrices only; no navigation checks or mutation."""
from pathlib import Path
import bpy,json,hashlib,math
R=Path(__file__).resolve().parents[1];Q=R/'qa'
BASE=json.loads((Q/'checkpoint10-entry02-independent.json').read_text(encoding='utf-8'))
OUT=Q/'checkpoint10-entry02-independent-animation-probe.json';assert not OUT.exists()
def read(path,expected):
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==expected
    bpy.ops.wm.open_mainfile(filepath=path);s=bpy.context.scene;rows={}
    for f in range(3744,3842):
        s.frame_set(f);ob=s.objects['CAM_TOUR_SUPPLEMENTAL'];m=ob.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world
        rows[str(f)]={'matrix_world':[list(r) for r in m],'location':list(m.translation),'quaternion':list(m.to_quaternion())}
    return rows
a=read(BASE['source']['path'],BASE['source']['sha256']);b=read(BASE['rebuild']['path'],BASE['rebuild']['sha256'])
different=[]
for f in a:
    if a[f]['matrix_world']!=b[f]['matrix_world']:
        different.append({'frame':int(f),'source':a[f],'rebuild':b[f],
                          'translation_delta_m':[b[f]['location'][i]-a[f]['location'][i] for i in range(3)],
                          'max_abs_matrix_component_delta':max(abs(b[f]['matrix_world'][i][j]-a[f]['matrix_world'][i][j]) for i in range(4) for j in range(4))})
out={'status':'PASS_EXACT_SAVED_ANIMATION' if not different else 'FAIL_TRUE_SAVED_ANIMATION_DIFFERENCE',
     'source':BASE['source'],'rebuild':BASE['rebuild'],'segment':'MAIN_L1_SERVICE_STAIR','camera':'CAM_TOUR_SUPPLEMENTAL',
     'frames_checked':98,'range':[3744,3841],'changed_frame_count':len(different),'changed_frames':[r['frame'] for r in different],
     'boundaries':{f:{'equal':a[str(f)]==b[str(f)],'source':a[str(f)],'rebuild':b[str(f)]} for f in (3744,3745,3840,3841)},
     'differing_actual_evaluated_matrices':different,'no_tolerance':True,'navigation_rerun':False,'saved':False,'rendered':False,
     'source_files_unchanged':all(hashlib.sha256(Path(BASE[k]['path']).read_bytes()).hexdigest()==BASE[k]['sha256'] for k in ('source','rebuild'))}
OUT.write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k not in ('differing_actual_evaluated_matrices','boundaries','changed_frames')},indent=2),flush=True)
