"""One bounded terrain-only diagnosis; no model save or rendering."""
import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'qa'))
import understory_detail08 as asset
import shrub08_auditlib as audit
source=ROOT/'scene/Fallingwater_iteration08.blend'
source_sha=hashlib.sha256(source.read_bytes()).hexdigest()
assert source_sha=='c5cd501e4c8ae0205ecb2437cd2d06d0c92bcc9a87e7d93d3986aeef976070d7'
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.scene.frame_set(48)
design=json.loads((ROOT/'qa/terrain-material08-shrub-design.json').read_text())
details={};generated={}
for index in (2,3):
    old_b=bpy.data.meshes[f'TREE_Understory_{index}_Stems'];old_l=bpy.data.meshes[f'TREE_Understory_{index}_Leaves']
    b,l,r=asset.make_asset(index,old_b.materials[0],list(old_l.materials));generated[index]=(b,l);details[index]=r
for row in design['selection']:
    b,l=generated[row['asset']]
    bpy.data.objects[row['branch_object']].data=b;bpy.data.objects[row['leaf_object']].data=l
bpy.context.view_layer.update()
terrain=bpy.data.objects['SITE_Continuous_BearRun_Terrain'];tbvh,_=audit.world_bvh([terrain],True)
remove={2:set(),3:set()};records=[]
for row in design['selection']:
    obj=bpy.data.objects[row['leaf_object']];bvh,_=audit.world_bvh([obj])
    intersecting={pair[1]//12 for pair in tbvh.overlap(bvh)}
    failed=[]
    for k,rec in enumerate(details[row['asset']]['leaves']):
        points=[obj.matrix_world@obj.data.vertices[i].co for i in range(rec['first_vertex'],rec['first_vertex']+11)]
        points.extend(obj.matrix_world@obj.data.polygons[i].center for i in range(rec['first_polygon'],rec['first_polygon']+12))
        gaps=[p.z-tbvh.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),250)[0].z for p in points]
        if min(gaps)<.012 or k in intersecting:
            failed.append({'design_leaf_id':rec['design_leaf_id'],'min_gap_m':min(gaps),'triangle_intersects':k in intersecting})
            remove[row['asset']].add(rec['design_leaf_id'])
    records.append({'object':obj.name,'asset':row['asset'],'leaves_to_remove':failed})
assert all(len(ids)<=24 for ids in remove.values()),remove
report={'status':'ONE_BOUNDED_SHARED_LEAF_PRUNING_PLAN_NO_SAVE_NO_RENDER','source_sha256':source_sha,
        'removed_design_leaf_ids':{str(k):sorted(v) for k,v in remove.items()},'instance_evidence':records,
        'rule':'Union of actual leaf/terrain failures across approved roots; applies only to the two new shared meshes. No root, terrain, material or old shared asset change.',
        'root_radius_local_m':[.0125,.0145], 'rendered':False,'scene_saved':False}
(ROOT/'qa/shrub08-prune-plan.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('SHRUB08_PRUNE',json.dumps({'removed':report['removed_design_leaf_ids'],'instances':[r for r in records if r['leaves_to_remove']]}),flush=True)
