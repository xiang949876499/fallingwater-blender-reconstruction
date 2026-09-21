"""Source-supported guest NW corner firebox. All unsurveyed dimensions remain C."""
import bpy
from fwlib import poly_prism, box, tag


def build(ctx, data, p, gz, col):
    spec=data.get('fireplace_detail',{})
    if not spec.get('enabled'):return []
    made=[]
    stone=ctx.mats['stone']
    lining=bpy.data.materials.get('FW_GUEST_firebrick')
    if lining is None:
        lining=bpy.data.materials.new('FW_GUEST_firebrick');lining.diffuse_color=(.115,.072,.045,1)
        lining.use_nodes=True
        node=lining.node_tree.nodes.get('Principled BSDF')
        node.inputs['Base Color'].default_value=(.115,.072,.045,1)
        node.inputs['Roughness'].default_value=.86
    def block(name,xy,bottom,top,mat=stone):
        x0,y0,x1,y1=xy
        ob=poly_prism(name,[p(v) for v in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]],gz+bottom,gz+top,mat,col)
        tag(ob,room_id='GUEST_L1_LOUNGE',reference='HABS guest01 / guest04 section / PA-5346-A-11',evidence='B form; C unmeasured chamber dimensions',role='architecture')
        ob['component']='guest_fireplace';made.append(ob)
        return ob
    x0,y0,x1,y1=spec['source_bounds_px'];hearth=spec['hearth_top_m'];head=spec['opening_head_m'];top=spec['hood_top_m']
    # Real chamber enclosure: two opaque backs, open east and south faces, raised
    # hearth and cantilevered hood. No black plane is substituted for a cavity.
    block('GUEST_FIREPLACE_north_mass',(324.5,348,378.30593607305934,y0),0,top)
    block('GUEST_FIREPLACE_west_back',(324.5,y0,x0,y1),0,top)
    block('GUEST_FIREPLACE_corner_hood',(x0,y0,x1,y1),head,top)
    block('GUEST_FIREPLACE_hearth',(x0,y0,x1+.8,y1+.8),0,hearth)
    # Section photograph shows brick-sized lining inside the recess. Variation
    # only describes the lining; no guessed hidden flue mechanism or live fire.
    mortar=.008;brickh=.063;brickw=.20
    wx0,wy0=p((x0,y0));wx1,wy1=p((x1,y1))
    rows=int((head-hearth-.018)/(brickh+mortar))
    for row in range(rows):
        z=gz+hearth+.012+brickh/2+row*(brickh+mortar)
        for axis,length in [('north',wx1-wx0),('west',wy0-wy1)]:
            cursor=0
            while cursor<length-.01:
                width=min(brickw-(brickw/2 if row%2 and cursor==0 else 0),length-cursor-.005)
                if width<=.006:break
                if axis=='north':
                    center=(wx0+cursor+width/2,wy0-.011,z);size=(width,.022,brickh)
                else:
                    center=(wx0+.011,wy0-cursor-width/2,z);size=(.022,width,brickh)
                ob=box('GUEST_FIREPLACE_firebrick_'+axis,center,size,lining,col,.002)
                tag(ob,room_id='GUEST_L1_LOUNGE',evidence='B brick lining from guest04; C individual courses',role='architecture')
                ob['component']='guest_fireplace_lining';made.append(ob)
                cursor+=width+mortar
    return made
