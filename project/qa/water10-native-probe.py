"""Read only finalized frame1 metadata and mesh-coordinate mapping."""
import bpy,openvdb,numpy as np,json,gzip,struct,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]; C=R/'caches/fluid_water10/natural48'
assert (C/'mesh/fluid_mesh_0003.bobj.gz').exists(),'Require later completed mesh before reading frame1'
meta=openvdb.readAllGridMetadata(str(C/'data/fluid_data_0001.vdb'))
out={'grids':[{'name':g.name,'type':g.valueTypeName,'metadata':{k:str(v) for k,v in g.metadata.items()}} for g in meta]}
conf=gzip.decompress((C/'config/config_0001.uni').read_bytes());out['config']={'len':len(conf),'tail':str(conf[-4:]),'res':list(struct.unpack_from('<3i',conf,4)),'dt':struct.unpack_from('<f',conf,20)[0],'T':struct.unpack_from('<f',conf,196)[0]}
raw=gzip.decompress((C/'mesh/fluid_mesh_0001.bobj.gz').read_bytes());n=struct.unpack_from('<i',raw,0)[0];v=np.frombuffer(raw,'<f4',count=n*3,offset=4).reshape(-1,3).astype(float)
bpy.ops.wm.open_mainfile(filepath=str(R/'scene/Fallingwater_water10_natural48.blend'));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;s.frame_set(1)
o=s.objects['WATER10_Natural_Channel_Domain'];ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();a=np.array([tuple(o.matrix_world@p.co) for p in me.vertices]);out['raw_vertices']=n;out['Blender_eval_vertices']=len(a)
if len(a)==n:
    affine=np.linalg.lstsq(np.column_stack((v,np.ones(n))),a,rcond=None)[0];out['affine']=affine.tolist();out['max_error']=float(np.linalg.norm(np.column_stack((v,np.ones(n)))@affine-a,axis=1).max())
out['raw_domain_vertices']=[list(o.matrix_world@p.co) for p in o.data.vertices]
(R/'qa/water10-native-probe.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print('NATIVE_PROBE',json.dumps(out),flush=True)
