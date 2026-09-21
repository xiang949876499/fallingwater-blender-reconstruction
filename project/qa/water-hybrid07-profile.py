"""Read actual frozen07c rock and original river to choose one branch."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import water_integration as wi
source=ROOT/'scene/Fallingwater_geology_candidate07c.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='24a2ca01d276cde137ff3e041ecbf5bdc028289f5b83e8be20167cb4a0c561f3'
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.frame_set(48)
river=scene.objects[wi.SURFACE];core=scene.objects['SITE_Core_Continuous_Fractured_Sandstone']
river.hide_set(False);scene.view_layers[0].update();rp=wi._bvh(river);rock=wi._bvh(core)
lip=Vector((2.4,-2.83,0));d=Vector((-.882352948,-.470588356,0));n=Vector((.470588356,-.882352948,0))
def pt(s,c,z=0):
 p=lip+d*s+n*c;p.z=z;return p
samples=[]
for c in [-3+i*.25 for i in range(25)]:
 row=[]
 for s in [-.8,-.6,-.4,-.2,0,.2,.4,.6,.8,1,1.2]:
  p=pt(s,c);a=rp.ray_cast(p,Vector((0,0,-1)),8);b=rock.ray_cast(p,Vector((0,0,-1)),8)
  row.append({'s':s,'water_z':a[0].z if a[0] is not None else None,'rock_z':b[0].z if b[0] is not None else None,
   'clearance':a[0].z-b[0].z if a[0] is not None and b[0] is not None else None})
 front=[]
 for z in [-3.06,-3.2,-3.4,-3.8,-4.2,-4.6,-5,-5.4,-5.8,-6.1]:
  h=rock.ray_cast(pt(3,c,z),-d,12)
  front.append({'z':z,'front_s':(h[0]-lip).dot(d) if h[0] is not None else None})
 samples.append({'c':c,'top':row,'front':front})
out={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'samples':samples}
(ROOT/'qa/water-hybrid07-profile.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print('PROFILE_COMPLETE',len(samples))
