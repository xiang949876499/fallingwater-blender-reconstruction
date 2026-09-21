"""Print compact QA fields; never dump full object fingerprints."""
import json
from pathlib import Path

qa = Path(__file__).resolve().parent
for basename in ('build', 'plan', 'readback'):
    path = qa / ('forest-undergrowth13-' + basename + '.json')
    if not path.exists():
        print(basename, 'MISSING')
        continue
    value = json.loads(path.read_text(encoding='utf-8'))
    print('\n', basename, 'KEYS', list(value))
    for key, item in value.items():
        if key in ('application', 'changed_objects', 'selected', 'rejected', 'protected_physics', 'roots', 'original16', 'source_objects'):
            print(key, 'COUNT', len(item))
        elif len(str(item)) < 4000:
            print(key, json.dumps(item))
        else:
            print(key, 'TYPE', type(item).__name__, 'COUNT', len(item))
    if basename == 'build':
        print('ROUTE', json.dumps(value['current_route_regression'])[:6000])
        print('CAMERA_MIN', min(value['saved_camera_clearance'], key=lambda x: x['nearest_new_mesh_m']))
    if basename == 'plan':
        print('SELECTED_FIRST', json.dumps(value['selection'][0]))
        print('PHYSICAL_FIRST', json.dumps(value['physical_checks'][0]))
