"""Read final candidate profiles and vegetation contacts in a fresh process."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
audit=json.loads((ROOT/'qa/near-terrain07b-candidate-check.json').read_text(encoding='utf8'))
contacts='--contacts' in sys.argv
if contacts:
    fix=json.loads((ROOT/'qa/near-terrain07b-contact-repair.json').read_text(encoding='utf8'))
    audit['candidate']=fix['candidate'];audit['candidate_sha256']=fix['candidate_sha256']
    audit['result']['vegetation']=fix['updated_vegetation_records']
path=Path(audit['candidate']);before=hashlib.sha256(path.read_bytes()).hexdigest()
assert before==audit['candidate_sha256']
bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.scene.frame_set(48)
terrain=bpy.data.objects['SITE_Continuous_BearRun_Terrain'];bvh=BVHTree.FromObject(terrain,bpy.context.evaluated_depsgraph_get())
def hit(x,y):return bvh.ray_cast(Vector((x,y,60)),Vector((0,0,-1)),130)[0]
def stats(v):return {'count':len(v),'min':min(v),'max':max(v),'mean':sum(v)/len(v)} if v else None
old=json.loads((ROOT/'qa/bank07b-saved-terrain-inspect.json').read_text(encoding='utf8'))
profiles={}
for name,rows in old['profiles'].items():
    profiles[name]=[{'xy':r['xy'],'original_z':r['actual_z'],'candidate_z':hit(*r['xy']).z,'delta_m':hit(*r['xy']).z-r['actual_z']} for r in rows]
vegetation=[]
for r in audit['result']['vegetation']['tree_pairs']:
    ob=bpy.data.objects[r['object']];p=ob.matrix_world.translation
    vegetation.append({'object':ob.name,'root_z':p.z,'actual_ground_z':hit(p.x,p.y).z,'actual_anchor_gap_m':p.z-hit(p.x,p.y).z})
groundcover=[]
for r in audit['result']['vegetation']['aggregate_groundcover']:
    ob=bpy.data.objects[r['object']];changed={x['vertex'] for x in r['vertices']};vg=[];fg=[];points={}
    for i in changed:
        p=ob.matrix_world@ob.data.vertices[i].co;points[i]=p;vg.append(p.z-hit(p.x,p.y).z)
    for face in ob.data.polygons:
        if not any(i in changed for i in face.vertices):continue
        pp=[ob.matrix_world@ob.data.vertices[i].co for i in face.vertices]
        p=sum(pp,Vector())/len(pp);fg.append(p.z-hit(p.x,p.y).z)
    groundcover.append({'object':ob.name,'changed_vertex_gaps':stats(vg),'affected_face_center_gaps':stats(fg)})
report={'status':'READBACK_COMPLETE_VISUAL_NOT_RUN','candidate_sha256':before,'frame':48,'profiles':profiles,'tree_anchor_gaps':vegetation,'aggregate_groundcover_contact':groundcover,'source_candidate_unchanged':hashlib.sha256(path.read_bytes()).hexdigest()==before}
if contacts:
    leaves=next(r for r in groundcover if r['object']=='TREE_Fallen_Leaves_Ground_Litter')
    assert leaves['affected_face_center_gaps']['min']>=-.0011
    assert leaves['affected_face_center_gaps']['max']<=.0171
    report['status']='PASS_SAVED_CONTACT_REPAIR_VISUAL_NOT_RUN'
(ROOT/('qa/near-terrain07b-contacts-reopen.json' if contacts else 'qa/near-terrain07b-reopen.json')).write_text(json.dumps(report,indent=2),encoding='utf8')
print('NEAR07B_READBACK',json.dumps({'status':report['status'],'tree_gap':stats([r['actual_anchor_gap_m'] for r in vegetation]),'groundcover':groundcover,'candidate_unchanged':report['source_candidate_unchanged']}),flush=True)
