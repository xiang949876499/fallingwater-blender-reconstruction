"""Freeze explicitly accepted camera choices; no scene mutation or rendering."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))
def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def image_record(rel, status, observation, scene_sha):
    p = ROOT / rel
    return {'path': rel, 'sha256': digest(p), 'scene_sha256': scene_sha,
            'actually_opened_by': ['root', 'camera04'], 'status': status,
            'observation': observation, 'final_quality_accepted': False}

basepath = ROOT/'qa/camera06-settings-candidate-frozen.json'
activepath = ROOT/'data/camera-settings-reviewed.json'
assert digest(basepath) == '8ca887363c8b6a7d3ccadc613576726c9acb261c83691499e95742fbae5bbba6'
assert digest(activepath) == '34e4bc6b9ca8555ba57832b830c575658955da7fc9c947b9c5721dfede31bd9e', 'Concurrent production mutation; inspect before overwriting'
old = read(activepath)
base = read(basepath)
config = copy.deepcopy(base)
scene = ROOT/'scene/Fallingwater_furniture_candidate07e.blend'
scene_sha = digest(scene)
assert scene_sha == 'd6084c1ebca7e1328f1a008b673d86e55c738da4b5ee8a52c5b7e5ce86b8eadd'
lighting_sha = read(ROOT/'renders/previews/iteration07-lighting-skyfill/render-benchmark.json')['scene_sha256']
seat = image_record('renders/previews/iteration07e-wide-seat/CAM_GUEST_L1_LOUNGE_A_EV3p6.png',
    'STAGED_COMPOSITION_ACCEPTED',
    'Broad seating-side room view: fireplace opening and hearth at right, bookcase edge, left windows and sofa, glass door and table visible. Firebox is dark, table partly cropped, diagnostic material/lighting quality remains unfinished.', scene_sha)
entry = image_record('renders/previews/iteration07e-wide-entry/CAM_GUEST_L1_LOUNGE_A_EV3p6.png',
    'FRAMING_FAIL_NOT_ADOPTED',
    'Bookcase occupies the right foreground and obscures the fireplace opening; retain as rejected backup.', scene_sha)
living = image_record('renders/previews/iteration07-lighting-skyfill/CAM_MAIN_L1_LIVING_A_EV2p4.png',
    'STAGED_EXPOSURE_ACCEPTED',
    'Root selected EV2.4 from sky-strength 0.36 lighting candidate. Room and terrace readable; new integrated07 lighting and geometry still require checks.', lighting_sha)
akey = 'CAM_GUEST_L1_LOUNGE_A'
config[akey] = read(ROOT/'qa/camera07e-wide-3-seating_side.json')[akey]
config[akey].update({
    'exposure': 3.6,
    'evidence': 'Source A11 relational composition, C-level camera placement. Seating-side viewpoint is in front of the bookcase; actual07e image reviewed by root and camera04. STAGED_COMPOSITION_ACCEPTED only; final integrated07 quality and exposure brackets pending.',
    'render_reviewed': True,
    'composition_status': 'STAGED_COMPOSITION_ACCEPTED',
    'final_quality_accepted': False,
    'composition_review': seat,
    'exposure_evidence': 'EV3.6 retained by root after actual07e seating-side image review. Final07 with proposed sky strength0.36 requires fresh exposure brackets; no final illumination acceptance.'
})
config['CAM_GUEST_L1_LOUNGE_B']['exposure'] = 3.0
config['CAM_GUEST_L1_LOUNGE_B']['exposure_evidence'] = 'Root explicitly retained EV3.0 for the preserved readable secondary room viewpoint. Corrected-screen07e geometry was reviewed at EV3.6; EV3.0 is provisional pending integrated07 brackets.'
config['CAM_MAIN_L1_LIVING_A']['exposure'] = 2.4
config['CAM_MAIN_L1_LIVING_A']['exposure_evidence'] = 'Root selected EV2.4 after actually viewing the sky-strength0.36 lighting candidate bracket. STAGED_EXPOSURE_ACCEPTED; full integrated07 final quality remains pending.'
config['CAM_MAIN_L1_LIVING_A']['exposure_review'] = living
assert len(config) == 120 and config.keys() == base.keys()
pose_fields = ('location', 'target', 'lens', 'shift_x', 'shift_y', 'support_z', 'support_object', 'outside_room_polygon')
changed_pose = [k for k in config if any(config[k].get(f) != base[k].get(f) for f in pose_fields)]
assert changed_pose == [akey], changed_pose
allowed_exposures = {akey, 'CAM_GUEST_L1_LOUNGE_B', 'CAM_MAIN_L1_LIVING_A'}
assert all(config[k]['exposure'] == base[k]['exposure'] for k in config if k not in allowed_exposures)
for k in ('CAM_MAIN_L1_LOGGIA_A', 'CAM_MAIN_B_PLUNGE_A'):
    assert config[k] == base[k], k
assert all(config['CAM_GUEST_L1_LOUNGE_B'].get(f) == base['CAM_GUEST_L1_LOUNGE_B'].get(f) for f in pose_fields)
frozen = ROOT/'qa/camera07e-settings-frozen.json'
assert not frozen.exists(), 'Keep frozen artifacts immutable'
save(frozen, config)
activepath.write_bytes(frozen.read_bytes())
changed_production_poses = [k for k in config if any(config[k].get(f) != old[k].get(f) for f in pose_fields)]
manifest = {
    'status': 'FROZEN_GEOMETRY_VERIFICATION_PENDING',
    'scene': 'scene/Fallingwater_furniture_candidate07e.blend', 'scene_sha256': scene_sha,
    'scene_scope': 'Independent furniture candidate07e, not final integrated07. Geometry checks do not include vegetation or illumination acceptance.',
    'config': 'qa/camera07e-settings-frozen.json', 'active_config': 'data/camera-settings-reviewed.json',
    'config_sha256': digest(frozen), 'camera_count': len(config),
    'base_config': 'qa/camera06-settings-candidate-frozen.json', 'base_config_sha256': digest(basepath),
    'previous_production_config': 'qa/camera05-settings-frozen-v2.json',
    'previous_production_sha256': '34e4bc6b9ca8555ba57832b830c575658955da7fc9c947b9c5721dfede31bd9e',
    'changed_poses_vs_base': changed_pose, 'changed_poses_vs_previous_production': changed_production_poses,
    'exposure_delta_vs_base': {k: {'before': base[k]['exposure'], 'after': config[k]['exposure']} for k in config if base[k]['exposure'] != config[k]['exposure']},
    'preserved_support_repairs': ['CAM_MAIN_L1_LOGGIA_A', 'CAM_MAIN_B_PLUNGE_A'],
    'preserved_secondary_pose': 'CAM_GUEST_L1_LOUNGE_B',
    'reviewed_images': [seat, entry, living],
    'final_quality_accepted': False,
    'scope': 'Production camera JSON only. No new pose search, render, sky, geometry, furnishings or navigation graph mutation. Source-related camera framing is C, not calibrated photo match.',
    'verification': 'qa/camera07e-final-verification.json',
    'integration_next': 'Use this exact config for root full07 build, then fresh geometry verification and exposure/visual review on that exact scene.'
}
save(ROOT/'qa/camera07e-final-manifest.json', manifest)
print(json.dumps({'config_sha256': digest(frozen), 'camera_count': len(config), 'changed_poses_vs_previous_production': changed_production_poses, 'exposure_delta_vs_base': manifest['exposure_delta_vs_base']}, indent=2))
