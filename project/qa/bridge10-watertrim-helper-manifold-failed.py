"""Animated, local water difference using the two actual bridge10 masonry solids.

Only two final Boolean modifiers are added to the existing animated river.
The shape keys, drivers, base water mesh, existing Solidify and every cutter
object remain unchanged. No photograph, texture, proxy AABB or fixed-frame
replacement mesh is used.
"""
import time
import bpy
import bmesh

SOURCE_SHA256='2a7630b8024c37bd768e563236807f8049469172c7e44b03379a450f91637063'
WATER_NAME='WATER_BearRun_Continuous_Upstream_Downstream'
CUTTERS=('SITE_Bridge10_Stone_Return_SW','SITE_Bridge10_Stone_Return_SE')
MODIFIERS=('Bridge10 SW actual solid difference','Bridge10 SE actual solid difference')
MASK_NAMES=('WATERTRIM10_SW_Actual_Masonry_Union','WATERTRIM10_SE_Actual_Masonry_Union')
FILTER_NAME='Bridge10 remove evaluated points with zero incident faces'
TRI_NAME='Bridge10 preserve original evaluated water triangles'
GROUP_NAME='Bridge10_Evaluated_Orphan_Point_Filter'


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
    # Exact union leaves collinear/duplicate computational fragments. Clean
    # only the hidden mask at 1 micrometre; source masonry remains untouched.
    bm=bmesh.new();bm.from_mesh(final)
    bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY')
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.000001)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(final);bm.free();final.update()
    mask.modifiers.remove(mod);mask.data=final
    mask.hide_set(True)
    mask['scope']='Exact static union of photographed-identity C masonry; Boolean-only hidden mask, not scene navigation geometry'
    return mask,{'name':name,'source_actual_masonry':source.name,'union_seconds':seconds,
                 'vertices':len(final.vertices),'polygons':len(final.polygons),'source_geometry_changed':False}


def _evaluation_filter(water):
    """Delete only unused evaluated points, never a face or base/shape-key data."""
    if GROUP_NAME in bpy.data.node_groups:raise ValueError('Evaluation filter already exists')
    group=bpy.data.node_groups.new(GROUP_NAME,'GeometryNodeTree')
    group.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
    group.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    inp=group.nodes.new('NodeGroupInput');out=group.nodes.new('NodeGroupOutput')
    neighbors=group.nodes.new('GeometryNodeInputMeshVertexNeighbors')
    test=group.nodes.new('ShaderNodeMath');test.operation='LESS_THAN';test.inputs[1].default_value=.5
    delete=group.nodes.new('GeometryNodeDeleteGeometry');delete.domain='POINT';delete.mode='ALL'
    group.links.new(inp.outputs['Geometry'],delete.inputs['Geometry'])
    group.links.new(neighbors.outputs['Face Count'],test.inputs[0])
    group.links.new(test.outputs[0],delete.inputs['Selection'])
    group.links.new(delete.outputs['Geometry'],out.inputs['Geometry'])
    mod=water.modifiers.new(FILTER_NAME,'NODES');mod.node_group=group
    tri=water.modifiers.new(TRI_NAME,'TRIANGULATE');tri.quad_method='FIXED';tri.ngon_method='BEAUTY'


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
    _evaluation_filter(water)
    for name,obj in zip(MODIFIERS,masks):
        mod=water.modifiers.new(name,'BOOLEAN')
        mod.operation='DIFFERENCE';mod.operand_type='OBJECT';mod.object=obj
        mod.solver='MANIFOLD';mod.use_self=False;mod.use_hole_tolerant=False
        if hasattr(mod,'material_mode'):mod.material_mode='INDEX'
    if active:active.is_active=True
    return {'status':'ANIMATED_BOOLEAN_CANDIDATE_UNVALIDATED','water':water.name,
            'new_modifiers':[FILTER_NAME,TRI_NAME,*MODIFIERS],'actual_cutters':list(CUTTERS),'static_masks':mask_records,
            'preserved':'original shape keys/drivers, base mesh and physical volume modifier',
            'strategy':'animate and Solidify, discard only zero-face evaluated points, preserve FIXED evaluated triangles, subtract clean actual SW/SE masonry union masks with MANIFOLD each frame',
            'new_proxy_geometry':'Two exact static unions of actual masonry, not bounding boxes','baked_frame':None}
