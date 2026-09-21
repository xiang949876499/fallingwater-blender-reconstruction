import bpy,json,math
from pathlib import Path
from mathutils import Vector
out=Path(r'D:\zx\test\project\qa')
core=bpy.data.objects['SITE_Core_Continuous_Fractured_Sandstone'].data
edge_use={}
for poly in core.polygons:
    vv=list(poly.vertices)
    for a,b in zip(vv,vv[1:]+vv[:1]):
        key=tuple(sorted((a,b)));edge_use[key]=edge_use.get(key,0)+1
core.calc_loop_triangles()
volume=sum(core.vertices[t.vertices[0]].co.dot(core.vertices[t.vertices[1]].co.cross(core.vertices[t.vertices[2]].co))/6 for t in core.loop_triangles)
tree_meshes=[m for m in bpy.data.meshes if m.name.startswith('TREE_Asset_') and 'Woody_Branches' in m.name]
obj=bpy.data.objects['WATER_Downstream_Advecting_Foam_00'];positions=[]
for frame in (1,14,241):
    bpy.context.scene.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();ev=obj.evaluated_get(deps)
    positions.append({'frame':frame,'position':list(ev.matrix_world.translation),'scale':list(ev.scale)})
report={'core_nonmanifold_edges':sum(v!=2 for v in edge_use.values()),'core_signed_volume_m3':volume,
        'core_materials':[m.name for m in core.materials],'all_tree_bark_faces_smooth':all(p.use_smooth for m in tree_meshes for p in m.polygons),
        'tree_asset_count':len(tree_meshes),'foam_motion_samples':positions,'foam_changed_after_13_frames':(Vector(positions[1]['position'])-Vector(positions[0]['position'])).length>1e-5,
        'rendered_visual_acceptance':'PENDING matched integrated rerender; no render run here'}
assert report['core_nonmanifold_edges']==0
assert volume>0
assert report['all_tree_bark_faces_smooth']
assert report['core_materials']==['FW_wet_rock','FW_rock']
assert report['foam_changed_after_13_frames']
(out/'site_revision3_geometry.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('SITE_REVISION3_GEOMETRY_OK',json.dumps(report))
