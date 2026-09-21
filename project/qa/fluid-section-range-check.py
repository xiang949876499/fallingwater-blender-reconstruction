import sys,json
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import water_integration as wi
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scene/Fallingwater_fluid_run06.blend'))
bpy.context.scene.frame_set(24);tree=wi._bvh(bpy.data.objects['WATER_Mantaflow_Local_Cascade'])
lip=Vector((2.4,-2.83,0));down=Vector((-.882352948,-.470588356,0));across=Vector((.470588356,-.882352948,0))
out=[]
for c in (0,.227,.453,.68,1.133,1.7,2.267):
    for z in (-3.06,-3.1,-3.14,-3.3,-3.6):
        values=[]
        for s,direction in ((-4,down),(6,-down)):
            p=lip+down*s+across*c;p.z=z
            h=tree.ray_cast(p,direction,10)
            values.append({'s':(h[0]-lip).dot(down),'normal':list(h[1])} if h[0] is not None else None)
        out.append({'cross':c,'z':z,'hits':values})
(ROOT/'qa/fluid-section-range-check.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out),flush=True)
