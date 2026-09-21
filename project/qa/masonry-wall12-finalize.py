"""Reconcile final owned handoff from actual machine reports, without Blender."""
import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];Q=R/'qa'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
check=json.loads((Q/'masonry-wall12-check.json').read_text());reopen=json.loads((Q/'masonry-wall12-reopen.json').read_text())
assert check['status']=='PASS_LOCAL_PHYSICAL_AND_CHANGED_OBJECT_REGRESSION_VISUAL_NOT_RUN'
assert reopen['status']=='PASS_INDEPENDENT_REOPEN_LOCAL_PHYSICS'
assert sha(Path(check['candidate']))==check['candidate_sha256']==reopen['candidate_sha256']
app=check['application'];stones=[s for f in app['faces'] for s in f['stones']];rows=[r for f in app['faces'] for r in f['rows']]
references=[R/'renders/previews/checkpoint10-exterior/CAM_HERO.png',R/'renders/previews/main-terrace11a/CAM_MAIN_L2_TERRACE_W_A.png',
            Q/'forest-canopy11-source-official-east.jpg',Q/'forest-canopy11-source-official-classic.jpg']
references.extend(R.parent/'research/references/architecture'/f'main-{i:02}-sheet.jpg' for i in (5,6,7,8,9,10))
sourceviews=[{'path':str(p),'sha256':sha(p),'viewed':True,'used_as_texture':False,'scope':'Reference diagnosis, plane/opening identity or morphology; no individual bond/RGB measurement'} for p in references]
(Q/'masonry-wall12-source-viewed.json').write_text(json.dumps(sourceviews,indent=2),encoding='utf8')
final={'status':'READY_FOR_ROOT_RENDER_PHYSICAL_REOPEN_PASS_VISUAL_NOT_RUN','source':str(R/'scene/Fallingwater_navigation_candidate10a.blend'),
       'source_sha256':check['source_sha256'],'candidate':check['candidate'],'candidate_sha256':check['candidate_sha256'],
       'helper':str(R/'scripts/masonry_wall12.py'),'helper_sha256':sha(R/'scripts/masonry_wall12.py'),
       'interface':'import masonry_wall12; manifest = masonry_wall12.apply(bpy.context.scene)',
       'changed_original_objects':check['changed_original_objects'],'original_objects_unchanged':check['original_objects_unchanged'],
       'new_objects':app['new_objects'],'new_material':app['private_material'],'shared_materials_images_cameras_lights_world_unchanged':True,
       'stones':len(stones),'triangles':app['triangles'],'stone_face_area_m2':app['surface_m2'],
       'course_body_height_range_m':[min(r['height'] for r in rows),max(r['height'] for r in rows)],
       'front_depth_range_m':[min(s['depth_range_m'][0] for s in stones),max(s['depth_range_m'][1] for s in stones)],
       'back_contact_samples':reopen['contact_samples'],'window_rays':reopen['window_rays'],'frame_support_points':reopen['frame_seating_points'],
       'current_route_changed_object_rays':check['route_changed_geometry_regression']['ray_count'],
       'camera_positions_checked':len(check['all_131_cameras']),'integer_frames':reopen['integer_frames'],
       'strict_integer_body_sweep_rays':reopen['strict_integer_body_sweep_rays'],'new_collisions':0,
       'independent_snapshot_equal':reopen['snapshot_exact'],'rendered':False,'production_modified':False,'visual_status':'NOT_RUN',
       'source_scope':'Only two west stone faces. HABS supports stone and Study window identity; bond, color/depth, retained window heights are C.',
       'render_comparison':{'same_existing_cameras':['CAM_HERO','CAM_MAIN_L2_TERRACE_W_A'],'frame':48,'parameters':'Integrator should use identical baseline/candidate camera/exposure/light settings; no saved camera changes.'},
       'negative_evidence':['masonry-wall12-probe.json: original blocked window3 rays',
                            'masonry-wall12-attempt01-check.json/log: aggregate bounding masks produced empty stone batches; unsaved',
                            'masonry-wall12-attempt02-check.json/log: new stones intersected original roof; unsaved',
                            'masonry-wall12-attempt03-check.json/log: generic Boolean changed outerZ dimension/material slots; unsaved'],
       'neat_reconciliation':'Owned design, source-view manifest, final handoff and failure records reconciled. Existing root AGENTS/README continue to state ongoing production status; no other owner files modified.'}
(Q/'masonry-wall12-final.json').write_text(json.dumps(final,indent=2),encoding='utf8')
handoff=f'''# Masonry wall12a handoff

**READY FOR ROOT RENDER; independent physical readback PASS; visual NOT_RUN.**

- Source: `{final['source']}`; SHA256 `{final['source_sha256']}`.
- Candidate: `{final['candidate']}`; SHA256 `{final['candidate_sha256']}`.
- Helper: `{final['helper']}`; SHA256 `{final['helper_sha256']}`. Call `{final['interface']}` once on the guarded source. It rejects duplicate finish or changed wall geometry.
- Exactly one original object's mesh changes: `MAIN_L3_study_core_0`, to create the real frame-aligned west window aperture. Its transform, dimensions, bevel and material slots remain exact. The Dressing core is among the {final['original_objects_unchanged']:,} unchanged original objects.
- Two new mesh batches contain {final['stones']} individual closed stones / {final['triangles']:,} triangles. Actual front depth is {1000*final['front_depth_range_m'][0]:.3f}–{1000*final['front_depth_range_m'][1]:.3f} mm; stone face area is{final['stone_face_area_m2']:.3f} m². Only these west faces receive finish, with a private copied stone material. The tower, other Dressing pieces and other wall faces are outside scope.
- Fresh reopened geometry: {final['back_contact_samples']:,} stone backing contacts, {final['window_rays']} window aperture rays, {final['frame_support_points']} frame-seat probes, no inter-stone or protected-surface collisions. Actual corrected core is closed and remains inside the original outer bounds.
- Route evidence: {final['current_route_changed_object_rays']:,} changed-object route rays; all131 cameras; all7,584 saved integer camera positions; {final['strict_integer_body_sweep_rays']:,} readback rays with1.95 m walking body columns,0.18 m radial offsets and integer-frame sweeps against added finish. Zero new obstruction. This is local change regression, not a fresh all-adjacency or GUI-navigation certificate.
- Independent reopened snapshot exactly equals the pre-save snapshot, with no normalization exceptions. Source hash is still unchanged. Scene frame73 and saved camera settings remain preserved; root comparison should explicitly useframe48 in both files.

Use the unchanged `CAM_HERO` and `CAM_MAIN_L2_TERRACE_W_A` at matched baseline/candidate settings. No render was started here. The new aperture should be inspected visually as well as the two stone faces; preserved glass and the inset framing are expected, not a walk-through doorway.

See `masonry-wall12-design.md`, `masonry-wall12-final.json`, `masonry-wall12-check.json`, `masonry-wall12-reopen.json`, `masonry-wall12-reopen-physical.json`, `masonry-wall12-reopen-integer-frames.json`. All old failure reports/logs and the frozen source remain. Source photographs are reference-only and are not textures. CC0 rock maps are inherited unchanged; authored bond and relief are explicitC.
'''
(Q/'masonry-wall12-handoff.md').write_text(handoff,encoding='utf8')
print(json.dumps({k:final[k] for k in ('status','candidate_sha256','helper_sha256','stones','triangles','integer_frames','strict_integer_body_sweep_rays')}))
