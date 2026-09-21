import bpy,bmesh,sys
sys.path.insert(0,'D:/zx/test/project/scripts');import hybrid_water as h
bpy.ops.wm.open_mainfile(filepath='D:/zx/test/project/scene/Fallingwater_water12_surface05.blend')
o=bpy.data.objects['WATER12_Continuous_Upper_9Branches_Pool_OuterRiver'];bm=bmesh.new();bm.from_mesh(o.data)
bad=[e for e in bm.edges if not e.is_manifold];print('BEFORE',len(bad),len(bm.verts),len(bm.faces),flush=True)
print(bmesh.ops.split_edges.__doc__,flush=True)
bmesh.ops.split_edges(bm,edges=bad)
print('AFTER',sum(not e.is_manifold for e in bm.edges),sum(e.is_boundary for e in bm.edges),len(bm.verts),len(bm.faces),flush=True)
