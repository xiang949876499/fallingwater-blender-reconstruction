"""Fresh-process candidate08 core, path/soil and affected vegetation readback."""
import bpy,json,hashlib,struct
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
audit=json.loads((ROOT/'qa/bank08-candidate-check.json').read_text(encoding='utf8'))
path=Path(audit['candidate']);sha=hashlib.sha256(path.read_bytes()).hexdigest();assert sha==audit['candidate_sha256']
bpy.ops.wm.open_mainfile(filepath=str(path));scene=bpy.context.scene;scene.frame_set(48)
terrain=scene.objects['SITE_Continuous_BearRun_Terrain'];bvh=BVHTree.FromObject(terrain,bpy.context.evaluated_depsgraph_get())
path_bvh=BVHTree.FromObject(scene.objects['SITE_Path_bridge_north_approach'],bpy.context.evaluated_depsgraph_get())
def zhit(tree,x,y):return tree.ray_cast(Vector((x,y,60)),Vector((0,0,-1)),130)[0]
core=[]
for r in json.loads((ROOT/'qa/core-geology07c-fresh-module-reproduction.json').read_text(encoding='utf8'))['objects']:
    ob=scene.objects[r['object']];h=hashlib.sha256()
    for v in ob.data.vertices:h.update(struct.pack('<3f',*(ob.matrix_world@v.co)))
    for p in ob.data.polygons:
        h.update(struct.pack('<I',len(p.vertices)))
        for i in p.vertices:h.update(struct.pack('<I',i))
    core.append({'object':ob.name,'world_geometry_sha256':h.hexdigest(),'equal_to_07c_frozen_core':h.hexdigest()==r['world_geometry_sha256']})
assert all(r['equal_to_07c_frozen_core'] for r in core)
cross=[]
for s in audit['cross_sections']:
    for r in s['samples']:
        x,y=r['xy'];t=zhit(bvh,x,y);p=zhit(path_bvh,x,y)
        cross.append({'label':s['label'],'offset_m':r['offset_from_actual_edge_m'],'soil_z':t.z,'paving_z':p.z if p else None,
                      'soil_paving_gap_m':t.z-p.z if p else None,'difference_from_build_check_m':t.z-r['candidate_terrain_z']})
assert max(abs(r['difference_from_build_check_m']) for r in cross)<1e-5
inside=[r for r in cross if r['offset_m']<0]
assert all(r['soil_paving_gap_m'] is not None and r['soil_paving_gap_m']<-.035 for r in inside)
roots=[]
for r in audit['tree_contact']:
    ob=scene.objects[r['object']];p=ob.matrix_world.translation;ground=zhit(bvh,p.x,p.y)
    roots.append({'object':ob.name,'anchor_gap_m':p.z-ground.z})
out={'status':'PASS_INDEPENDENT_SAVED_READBACK_VISUAL_NOT_RUN','candidate_sha256':sha,'frame':48,
     'core':core,'actual_cross_section_points':cross,'tree_anchor_checks':roots,
     'terrain_vertex_count':len(terrain.data.vertices),'terrain_face_count':len(terrain.data.polygons),
     'actual_terrain_material':terrain.data.materials[0].name,'candidate_file_unchanged':hashlib.sha256(path.read_bytes()).hexdigest()==sha,
     'limits':'No render or new scene. Core hash/readback and contact are not visual acceptance. Full07 navigation final checks remain root-owned.'}
(ROOT/'qa/bank08-reopen.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print('BANK08_REOPEN',json.dumps({'status':out['status'],'core_all_equal':all(r['equal_to_07c_frozen_core'] for r in core),'inside_paving_gap_range_m':[min(r['soil_paving_gap_m'] for r in inside),max(r['soil_paving_gap_m'] for r in inside)],'roots':roots,'file_unchanged':out['candidate_file_unchanged']}),flush=True)
