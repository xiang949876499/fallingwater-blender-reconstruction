import bpy, json, sys, hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import main_house as mh
SRC=R/'scene/Fallingwater_structure_candidate09.blend'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()=='4fa1fc1f56795a2da88c97bacc9bd3b2a0730d3d085076173425b00addd744a0'
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4
dg=bpy.context.evaluated_depsgraph_get()
def cast(x,y,z,d=(0,0,-1),distance=10):
 h,p,n,f,o,_=s.ray_cast(dg,Vector((x,y,z)),Vector(d),distance=distance)
 return dict(object=o.name if h else None,point=list(p) if h else None,normal=list(n) if h else None)
points=[]
for label,xx,yy,z in [('Loggia',[530,531.4,532,533,534,534.7675,535,536,538,540,542,545],[298,300,300.7277,301.5,302,303,304,305,306,307,308],.122),('Alcove',[431.5,432,432.25,433,434,435,436],[255,258,259,265,270,276,280,286,290,291,294,302],5.28615)]:
 for x in xx:
  for y in yy:
   wx,wy=mh.xy((x,y));points.append(dict(label=label,source_px=[x,y],expected_z=z,ground=cast(wx,wy,z+.08),ceiling=cast(wx,wy,z+.12,(0,0,1),5)))
bounds={}
for o in s.objects:
 if o.type!='MESH' or not o.name.startswith('MAIN_'):continue
 vv=[o.matrix_world@Vector(v) for v in o.bound_box];bb=[[min(v[k] for v in vv),max(v[k] for v in vv)] for k in range(3)]
 targets=[(mh.xy((529,306)),.1,.8),(mh.xy((433,274)),5.26415,.7)]
 if any(bb[0][0]-r<=p[0]<=bb[0][1]+r and bb[1][0]-r<=p[1]<=bb[1][1]+r and bb[2][0]-.1<=z<=bb[2][1]+.1 for p,z,r in targets):bounds[o.name]=dict(world_bounds=bb,source_xy_bounds=[bb[0][0]/mh.SX+327,540-bb[1][1]/mh.SY,bb[0][1]/mh.SX+327,540-bb[1][0]/mh.SY])
result=dict(source=str(SRC),sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),points=points,bounds=bounds)
(R/'qa/structure09b-baseline-probe.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'bounds':bounds,'key_points':[p for p in points if p['source_px'] in [[534.7675,300.7277],[433,265]]]},indent=2))
