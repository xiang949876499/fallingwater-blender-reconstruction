import bpy,bmesh
bpy.ops.wm.open_mainfile(filepath='D:/zx/test/project/scene/Fallingwater_water12_surface04.blend')
o=bpy.data.objects['WATER12_Continuous_Upper_9Branches_Pool_OuterRiver'];b=bmesh.new();b.from_mesh(o.data)
print('NONMANIFOLD_LOCATIONS',[(list(e.verts[0].co),list(e.verts[1].co),len(e.link_faces)) for e in b.edges if not e.is_manifold],flush=True)
