"""Unhooked interface10 candidate repair for the frozen integrated09 main house.

Source identity: HABS main04 continuous entry stone/paving; main05 door-side
floor beside the stone core. All traced XY accuracy remains C (~1 JPEG px).
Only the explicit interfaces below change. No doors, stairs, cameras or lights
are edited. Existing doorway registration questions remain unresolved.
"""
import bpy
from mathutils import Matrix
import main_house as mh

CHANGED = ('MAIN_L1_entry_east_corner_core',
           'MAIN_floor_threshold_entry_loggia',
           'MAIN_floor_threshold_entry_loggia_finish',
           'MAIN_L2_CLOSET_M_slab','MAIN_L2_CLOSET_M_finish')
REMOVED = ('MAIN_L1_entry_east_1',)

def source_specs():
    # Union the old corner and east leg into one closed L prism, then extend
    # just its eastern face to main04's x535 trace. This removes their old
    # coincident cap overlap instead of adding a thin overlapping cover.
    west_leg=527-.255/mh.SX
    west_corner=527-.005/mh.SX
    north=334-.255/mh.SY
    stone=[(west_corner,north),(535.05,north),(535.05,409),
           (west_leg,409),(west_leg,334),(west_corner,334)]
    # Existing Coat south face is y303.35405; 5mm lap enters wall volume.
    north_paving=301+.125/mh.SY-.005/mh.SY
    paving=[(510,north_paving),(529,north_paving),(529,306),
            (537,306),(537,307+2/30),(535,307),(535,332),(510,332)]
    # Actual core east face x332, north partition inner face y305.07156.
    # Existing Master supplies y312 onward and x368 onward; share these edges.
    west=332-.005/mh.SX; north_closet=303+.11/mh.SY-.005/mh.SY
    # Preserve the hall_master threshold at x367..391 through y307.
    closet=[(west,north_closet),(367,north_closet),(367,307),
            (368,307),(368,312),(west,312)]
    return [('MAIN_L1_entry_east_corner_core',stone,.1,2.58),
            ('MAIN_floor_threshold_entry_loggia',paving,-.08,.1),
            ('MAIN_floor_threshold_entry_loggia_finish',paving,.1,.122),
            ('MAIN_L2_CLOSET_M_slab',closet,2.6248,2.8448),
            ('MAIN_L2_CLOSET_M_finish',closet,2.8448,2.8668)]

def prism_mesh(name,polygon,z0,z1,materials):
    pts=[mh.xy(p) for p in polygon]
    if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(pts,pts[1:]+pts[:1]))<0:pts.reverse()
    n=len(pts);verts=[(x,y,z0) for x,y in pts]+[(x,y,z1) for x,y in pts]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new(name+'_interface10');mesh.from_pydata(verts,[],faces);mesh.update()
    for m in materials:mesh.materials.append(m)
    return mesh

def apply():
    scene=bpy.context.scene
    assert all(n in scene.objects for n in CHANGED+REMOVED), 'Requires original integrated09 interfaces; not idempotent.'
    manifest=[]
    for name,p,z0,z1 in source_specs():
        ob=scene.objects[name]
        old=[list(ob.matrix_world@v.co) for v in ob.data.vertices]
        ob.data=prism_mesh(name,p,z0,z1,list(ob.data.materials))
        ob.matrix_world=Matrix.Identity(4)
        ob['physical_revision']='interface10 source-bounded closed stone / shared floor edges'
        ob['evidence']='C source trace; no doorway/stair identity change'
        manifest.append(dict(name=name,source_polygon=p,z=[z0,z1],before_world_vertices=old,after_world_vertices=[list(v.co) for v in ob.data.vertices]))
    # The old east-leg volume is entirely represented by the unified L core.
    # Its separate7mm edge dressing is removed only at this unified wall target.
    bpy.data.objects.remove(scene.objects['MAIN_L1_entry_east_1'],do_unlink=True)
    bpy.context.view_layer.update()
    return dict(changed=list(CHANGED),removed=list(REMOVED),added=[],geometry=manifest,
                open_questions=['Main05 master-entry plan registration',
                                'Main04 south-Coat/west bar under-stair 3D extent'])
