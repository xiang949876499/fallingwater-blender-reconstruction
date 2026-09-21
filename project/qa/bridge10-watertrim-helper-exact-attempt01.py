"""Animated, local water difference using the two actual bridge10 masonry solids.

Only two final Boolean modifiers are added to the existing animated river.
The shape keys, drivers, base water mesh, existing Solidify and every cutter
object remain unchanged. No photograph, texture, proxy AABB or fixed-frame
replacement mesh is used.
"""
import time
import bpy

SOURCE_SHA256='2a7630b8024c37bd768e563236807f8049469172c7e44b03379a450f91637063'
WATER_NAME='WATER_BearRun_Continuous_Upstream_Downstream'
CUTTERS=('SITE_Bridge10_Stone_Return_SW','SITE_Bridge10_Stone_Return_SE')
MODIFIERS=('Bridge10 SW actual solid difference','Bridge10 SE actual solid difference')
MASK_NAMES=('WATERTRIM10_SW_Actual_Masonry_Union','WATERTRIM10_SE_Actual_Masonry_Union')


def _static_actual_union(source,name,boundary_count):
    """Union the real masonry components once, on a small static mask only."""
    mesh=bpy.data.meshes.new(name+'_InitialCore')
    mesh.from_pydata([tuple(v.co) for v in list(source.data.vertices)[:2*boundary_count+2]],[],
                     [tuple(p.vertices) for p in list(source.data.polygons)[:3*boundary_count]])
    for mat in source.data.materials:mesh.materials.append(mat)
    mask=bpy.data.objects.new(name,mesh);source.users_collection[0].objects.link(mask)
    mask.matrix_world=source.matrix_world.copy()
    mask.hide_render=True;mask.hide_select=True;mask.display_type='WIRE'
    mod=mask.modifiers.new('Resolve actual static masonry union once','BOOLEAN')
    mod.operation='UNION';mod.operand_type='OBJECT';mod.object=source
    mod.solver='EXACT';mod.use_self=True;mod.use_hole_tolerant=False
    start=time.monotonic();bpy.context.view_layer.update()
    deps=bpy.context.evaluated_depsgraph_get()
    final=bpy.data.meshes.new_from_object(mask.evaluated_get(deps),preserve_all_data_layers=True,depsgraph=deps)
    seconds=time.monotonic()-start
    mask.modifiers.remove(mod);mask.data=final
    mask.hide_set(True)
    mask['scope']='Exact static union of photographed-identity C masonry; Boolean-only hidden mask, not scene navigation geometry'
    return mask,{'name':name,'source_actual_masonry':source.name,'union_seconds':seconds,
                 'vertices':len(final.vertices),'polygons':len(final.polygons),'source_geometry_changed':False}


def apply():
    """Caller opens/audits the frozen bridge10 candidate; no file operations."""
    water=bpy.context.scene.objects.get(WATER_NAME)
    if water is None or water.type!='MESH':raise ValueError('Expected frozen animated river mesh')
    if any(n in water.modifiers for n in MODIFIERS):raise ValueError('Water trim already present; do not append again')
    if [m.type for m in water.modifiers]!=['SOLIDIFY']:
        raise ValueError('Unexpected water modifier stack; review this scene revision')
    if not water.data.shape_keys:raise ValueError('Expected original animated water shape keys')
    cutters=[]
    if any(name in bpy.context.scene.objects for name in MASK_NAMES):raise ValueError('Static water masks already present')
    for name in CUTTERS:
        obj=bpy.context.scene.objects.get(name)
        if obj is None or obj.type!='MESH':raise ValueError(('Missing actual L masonry',name))
        cutters.append(obj)
    masks=[];mask_records=[]
    for obj,name,count in zip(cutters,MASK_NAMES,(58,54)):
        mask,record=_static_actual_union(obj,name,count);masks.append(mask);mask_records.append(record)
    active=next((m for m in water.modifiers if m.is_active),None)
    for name,obj in zip(MODIFIERS,masks):
        mod=water.modifiers.new(name,'BOOLEAN')
        mod.operation='DIFFERENCE';mod.operand_type='OBJECT';mod.object=obj
        mod.solver='EXACT';mod.use_self=False;mod.use_hole_tolerant=False
        if hasattr(mod,'material_mode'):mod.material_mode='INDEX'
    if active:active.is_active=True
    return {'status':'ANIMATED_BOOLEAN_CANDIDATE_UNVALIDATED','water':water.name,
            'new_modifiers':list(MODIFIERS),'actual_cutters':list(CUTTERS),'static_masks':mask_records,
            'preserved':'original shape keys/drivers, base mesh and physical volume modifier',
            'strategy':'evaluate animated water and Solidify, then subtract the actual closed SW/SE masonry solids each frame',
            'new_proxy_geometry':'Two exact static unions of actual masonry, not bounding boxes','baked_frame':None}
