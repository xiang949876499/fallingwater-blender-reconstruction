from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'qa/guest-window12-source-registration-probe.json').read_text(encoding='utf-8'))
obs=d['objects']
out={'counts':d['actual_counts'],'core_bounds':{n:o['evaluated_bounds'] for n,o in obs.items() if '_steel_window' not in n and not n.startswith('GUEST_LAYERED')},
 'posts':[],'front_windows':{n:o['evaluated_bounds'] for n,o in obs.items() if n.startswith('GUEST_L1_LOUNGE_FRONT_steel_window') and '_mullion' not in n}}
for p in d['model_posts']:
    ss=[]
    for r in p['crosssections']:
        h=r['stone_first_hit'];w=r['window_first_hit']
        ss.append({'Z':r['z'],'stone':h['object'] if h else None,'stone_Y':h['position_m'][1] if h else None,
          'stone_to_frame_depth_m':r['frame_outerY_minus_stone_frontY_m'],'window':w['object'] if w else None,
          'window_Y':w['position_m'][1] if w else None})
    out['posts'].append({'index':p['index'],'plan_xy':p['center_plan_normalized'],'world_center':p['center_world_m'],
          'bounds':p['evaluated_bounds'],'sections':ss})
(ROOT/'qa/guest-window12-source-registration-readout.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
