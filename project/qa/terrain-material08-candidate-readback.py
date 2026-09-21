"""Fresh-process shader dependency readback; no scene mutations or rendering."""
import bpy,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
audit=json.loads((ROOT/'qa/terrain-material08-candidate-check.json').read_text(encoding='utf8'))
path=Path(audit['candidate']);assert hashlib.sha256(path.read_bytes()).hexdigest()==audit['candidate_sha256']
bpy.ops.wm.open_mainfile(filepath=str(path));scene=bpy.context.scene
terrain=scene.objects['SITE_Continuous_BearRun_Terrain'];mat=terrain.data.materials[0]
assert mat.name==audit['copied_material']
nodes=mat.node_tree.nodes;p=nodes['Principled BSDF']
images=[]
for suffix,space in [('Diffuse','sRGB'),('Rough','Non-Color'),('Displacement','Non-Color')]:
    node=nodes['PH_'+suffix];im=node.image;file=Path(bpy.path.abspath(im.filepath))
    # External pixels are lazy-loaded on open; reading size resolves the image.
    was_loaded=im.has_data;size=list(im.size)
    print('IMAGE_LOAD',json.dumps({'node':node.name,'path':str(file),'loaded_before':was_loaded,'loaded_after_size':im.has_data,'size':size,'colorspace':im.colorspace_settings.name,'exists':file.exists()}),flush=True)
    assert im.has_data and size==[2048,2048] and im.colorspace_settings.name==space and file.exists()
    images.append({'node':node.name,'path':str(file),'size':size,'colorspace':space,
                   'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'projection':node.projection,'blend':node.projection_blend})
assert p.inputs['Base Color'].links[0].from_node==nodes['Mix (Legacy)']
assert p.inputs['Roughness'].links[0].from_node==nodes['PH_Rough']
assert p.inputs['Normal'].links[0].from_node==nodes['Bump.001']
assert not nodes['Material Output'].inputs['Displacement'].is_linked
assert not terrain.modifiers
report={'status':'PASS_FRESH_PROCESS_IMAGE_DEPENDENCIES_AND_ACTIVE_CONNECTIONS',
        'candidate_sha256':audit['candidate_sha256'],'images':images,
        'scale':nodes['Vector Math.001'].inputs['Scale'].default_value,
        'tile_width_m':1/nodes['Vector Math.001'].inputs['Scale'].default_value,
        'bump_strength':nodes['Bump.001'].inputs['Strength'].default_value,
        'bump_distance_m':nodes['Bump.001'].inputs['Distance'].default_value,
        'geometry_displacement':False,'rendered':False,'saved':False}
assert hashlib.sha256(path.read_bytes()).hexdigest()==audit['candidate_sha256']
(ROOT/'qa/terrain-material08-candidate-readback.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('TERRAIN_MATERIAL08_READBACK',json.dumps(report),flush=True)
