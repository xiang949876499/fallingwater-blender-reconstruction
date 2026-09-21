"""Create an explicit re-render queue from new mesh/visibility evidence and old pending views."""
import json,math,hashlib,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(n):return json.loads((ROOT/'qa'/n).read_text(encoding='utf-8'))
old=read('camera06-baseline05.json');new=read('camera06-full-check.json')
cfg=read('camera05-settings-frozen-v2.json');pending=read('camera05-freeze-manifest.json')
assert old['settings_sha256']==new['settings_sha256']=='34e4bc6b9ca8555ba57832b830c575658955da7fc9c947b9c5721dfede31bd9e'
assert new['scene_sha256']=='172b76340d1224a2b98f415b21042d19ad7fba4d849543d7156beb17e5fcf055'
before=old['object_fingerprints'];after=new['object_fingerprints']
added=set(after)-set(before);removed=set(before)-set(after)
changed={n for n in set(before)&set(after) if before[n]['sha256']!=after[n]['sha256']}
affected=added|removed|changed
oldcams={c['camera']:c for c in old['cameras']}
prior={r['camera'] for r in pending['pose_changes']}
rows=[]
for c in new['cameras']:
    n=c['camera'];o=oldcams[n];reasons=[]
    if n in prior:reasons.append('05_REVISED_POSE_STILL_NEEDS_IMAGE_REVIEW')
    if c['issue']:reasons.append('06_POINT_GEOMETRY_FAIL_FIX_BEFORE_RENDER')
    lost={k:v-c['visible_witnesses'].get(k,0) for k,v in o['visible_witnesses'].items() if v>c['visible_witnesses'].get(k,0)}
    gained={k:v-o['visible_witnesses'].get(k,0) for k,v in c['visible_witnesses'].items() if v>o['visible_witnesses'].get(k,0)}
    if lost:reasons.append('06_FEWER_VISIBLE_SEMANTIC_WITNESSES')
    if gained:reasons.append('06_NEWLY_VISIBLE_SEMANTIC_WITNESSES')
    hits=collections.Counter();ray_deltas=[]
    for idx,(x,y) in enumerate(zip(o['shifted_frame_grid'],c['shifted_frame_grid'])):
        a=x['hit'];b=y['hit'];an=a['object'] if a else None;bn=b['object'] if b else None
        if bn in affected:hits[bn]+=1
        if an!=bn or a and b and abs(a['distance']-b['distance'])>.03:
            ray_deltas.append({'index':idx,'uv':y['uv'],'before_hit':a,'after_hit':b})
    if hits:reasons.append('06_CHANGED_MESH_IS_FIRST_HIT_IN_FRAME')
    if ray_deltas:reasons.append('06_FRAME_SURFACE_RAYS_CHANGED')
    # Deep roof overhangs and real openings affect indirect illumination even
    # when their undersides are outside the sampled camera frame.
    guest_envelope=c['room_id'].startswith(('GUEST_L1_','GUEST_L2_'))
    if guest_envelope:reasons.append('06_GUEST_ENVELOPE_LIGHTING_RECHECK_REQUIRED')
    # A changed terrain object may be hit at an identical unchanged local
    # surface. That alone is contextual, not evidence of a changed composition.
    substantive=[r for r in reasons if r!='06_CHANGED_MESH_IS_FIRST_HIT_IN_FRAME']
    rows.append({'camera':n,'room_id':c['room_id'],'priority':'FIX_GEOMETRY' if c['issue'] else ('RENDER_AND_REVIEW' if substantive else ('CONTEXT_ONLY_RECHECK' if reasons else 'NO_DETECTED_GEOMETRY_CHANGE')),
                 'reasons':reasons,'lost_witness_counts':lost,'gained_witness_counts':gained,'changed_objects_first_hit':dict(hits),
                 'frame_changed_ray_count':len(ray_deltas),'frame_ray_changes':ray_deltas,
                 'geometry_issue':c['issue'],'near_grid_rays_before':o['near_grid_rays_under_06m'],'near_grid_rays_after':c['near_grid_rays_under_06m'],
                 'semantic_status':c['semantic_witness_status'],'actual_visual_acceptance':'NOT_ESTABLISHED_BY_THIS_CHECK'})
result={'scene':new['scene'],'scene_sha256':new['scene_sha256'],'settings_sha256':new['settings_sha256'],
        'status':'GEOMETRY_FAILURES_PENDING' if any(c['issue'] for c in new['cameras']) else 'GEOMETRY_ONLY_PASS_VISUAL_PENDING',
        'scope':'Same05-v2 poses cast against both complete05 and06 evaluated nonvegetation geometry. Shifted77-ray grids and sparse actual furniture/stair witnesses establish measured changes, not photographs or lighting acceptance.',
        'changed_mesh_counts':{'added':len(added),'removed':len(removed),'modified':len(changed)},
        'changed_meshes':{'added':sorted(added),'removed':sorted(removed),'modified':sorted(changed)},
        'previous_pending_pose_count':len(prior),'required_room_rerender_count':sum(c['priority'] in ('FIX_GEOMETRY','RENDER_AND_REVIEW') for c in rows),
        'context_only_count':sum(c['priority']=='CONTEXT_ONLY_RECHECK' for c in rows),'cameras':rows,
        'additional_showcase_renders':['CAM_GUEST_POOL','CAM_GUEST_OVERVIEW','CAM_HERO','CAM_UPSTREAM'],
        'showcase_scope':'These lie outside the120 room-camera set; guest roof/coping and rebuilt site/vegetation warrant separate full-scene rendered comparison. No showcase geometric or visual PASS claimed here.'}
(ROOT/'qa/camera06-rerender-queue.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# 第06轮需要复渲的机位','','同一05-v2参数分别读取05与06真实几何。此列表包含上一轮41个待看图新机位，以及06结构/遮挡/客楼檐下照明影响；不代表其他图已通过。',
       '',f"房间机位需复渲：{result['required_room_rerender_count']}/120。展示机位另列 Guest Pool、Guest Overview、Hero、Upstream。",'',
       '| 机位 | 原因 | 几何状态 |','|---|---|---|']
labels={'05_REVISED_POSE_STILL_NEEDS_IMAGE_REVIEW':'05新构图待图','06_POINT_GEOMETRY_FAIL_FIX_BEFORE_RENDER':'06位置失败须先修',
        '06_FEWER_VISIBLE_SEMANTIC_WITNESSES':'目标可见见证减少','06_NEWLY_VISIBLE_SEMANTIC_WITNESSES':'目标可见见证增加',
        '06_CHANGED_MESH_IS_FIRST_HIT_IN_FRAME':'画幅射线命中新改网格','06_FRAME_SURFACE_RAYS_CHANGED':'画幅首命中变化',
        '06_GUEST_ENVELOPE_LIGHTING_RECHECK_REQUIRED':'客楼深檐/开孔照明待实图'}
for c in rows:
    if c['priority'] in ('FIX_GEOMETRY','RENDER_AND_REVIEW'):lines.append('| '+c['camera']+' | '+'；'.join(labels[x] for x in c['reasons'])+' | '+('FAIL' if c['geometry_issue'] else '仅点位通过')+' |')
lines.extend(['','另有 '+str(result['context_only_count'])+' 位射线命中了其他部分发生变化的同一网格对象，但局部首命中位置未测出变化，仅列环境上下文复查，不计为实质画幅变化。JSON保留全部120位，不把未触发稀疏射线差异解释为视觉通过。'])
(ROOT/'qa/camera06-rerender-queue.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'status':result['status'],'changed_mesh_counts':result['changed_mesh_counts'],'rerender_count':result['required_room_rerender_count'],
                  'fails':[c['camera'] for c in rows if c['geometry_issue']],'witness_losses':[(c['camera'],c['lost_witness_counts']) for c in rows if c['lost_witness_counts']]}))
