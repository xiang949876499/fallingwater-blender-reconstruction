"""Explain, rather than ignore, five fresh-rebuild comparison differences."""
from pathlib import Path
import bpy,json,hashlib,numpy as np
ROOT=Path(__file__).resolve().parents[1]
paths=[ROOT/'scene/Fallingwater_iteration10.blend',ROOT/'scene/Fallingwater_iteration10_rebuilt.blend']
cams=['CAM_MAIN_L2_MASTER_A','CAM_MAIN_L2_MASTER_B','CAM_MAIN_L2_BATH_M_A','CAM_MAIN_L2_BATH_M_B']
def array(items,field,n,dtype):
    out=np.empty(len(items)*n,dtype=dtype);items.foreach_get(field,out);return out.reshape((len(items),n))
def state(path):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    m=bpy.data.objects['SITE_Continuous_BearRun_Terrain'].data
    data={'coords':array(m.vertices,'co',3,'f4'),'edges':array(m.edges,'vertices',2,'i4'),
          'faces':[tuple(p.vertices) for p in m.polygons],
          'indices':array(m.polygons,'material_index',1,'i4'),'smooth':array(m.polygons,'use_smooth',1,'i4'),
          'uvs':{uv.name:array(uv.data,'uv',2,'f4') for uv in m.uv_layers},
          'materials':[x.name if x else None for x in m.materials]}
    return data,{name:{'location':list(bpy.data.objects[name].location),'rotation':list(bpy.data.objects[name].rotation_euler),
                     'lens':bpy.data.objects[name].data.lens,'shift':[bpy.data.objects[name].data.shift_x,bpy.data.objects[name].data.shift_y],
                     'clip':[bpy.data.objects[name].data.clip_start,bpy.data.objects[name].data.clip_end],
                     'matrix':[list(r) for r in bpy.data.objects[name].matrix_world]} for name in cams}
(a,ca),(b,cb)=map(state,paths)
d=b['coords']-a['coords'];different=np.flatnonzero(np.max(np.abs(d),axis=1)>0)
result={'terrain_coordinate_changed_vertices':len(different),'terrain_max_abs_vertex_delta_m':float(np.max(np.abs(d))),
        'vertex_examples':[{'id':int(i),'old':a['coords'][i].tolist(),'new':b['coords'][i].tolist()} for i in different[:10]],
        'ordered_faces_same':a['faces']==b['faces'],'same_material_names':a['materials']==b['materials'],
        'old_material_names':a['materials'],'new_material_names':b['materials'],
        'ordered_edges_same':bool(np.array_equal(a['edges'],b['edges'])),
        'material_indices_same':bool(np.array_equal(a['indices'],b['indices'])),
        'smooth_flags_same':bool(np.array_equal(a['smooth'],b['smooth'])),
        'uvs':{n:{'same':bool(np.array_equal(a['uvs'][n],b['uvs'][n])),'max_delta':float(np.max(np.abs(a['uvs'][n]-b['uvs'][n])))} for n in a['uvs']},
        'camera_differences':{name:{k:{'old':ca[name][k],'new':cb[name][k]} for k in ca[name] if ca[name][k]!=cb[name][k]} for name in cams},
        'source_files_unchanged':[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]}
(ROOT/'qa/checkpoint10-entry-diagnostic.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result),flush=True)
