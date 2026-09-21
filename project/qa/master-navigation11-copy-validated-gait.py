"""One-time static reuse of frozen10's tested sole/leg/body solver.

Changes are deliberately narrow and visible in the resulting owned11 source:
actual floor and track inputs; no torso uplift; separately executed directions.
This does not patch/import/modify the frozen10 file at runtime.
"""
from pathlib import Path
import ast
R=Path(__file__).resolve().parents[1]
source=(R/'scripts/master_navigation10.py').read_text(encoding='utf-8')
tree=ast.parse(source);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='sill_step')
fn='\n'.join(source.splitlines()[node.lineno-1:node.end_lineno])
fn=fn.replace('def sill_step(probe):','def fixed_torso_step(probe, floor_z, sill_rise_m, outward=True):')
fn=fn.replace('    x,y0,y1=2.62,7.11,6.59','    TOP=float(floor_z)\n    x=2.62\n    y0,y1=(7.11,6.59) if outward else (6.59,7.11)')
fn=fn.replace('    bump=.0522','    bump=float(sill_rise_m)')
fn=fn.replace('            body_floor=TOP+bump*math.sin(math.pi*(phase+t)/2)','            body_floor=TOP  # Same actual supporting floor throughout; feet cross, body does not rise.')
fn=fn.replace("'step_length_m':y0-y1", "'direction':'outward' if outward else 'inward','torso_vertical_displacement_m':0,'step_length_m':abs(y0-y1)")
fn=fn.replace("'source_identity':'Main05 and Columbia Master face2 show full-height operable terrace doors and track; exact active panel/swing78deg remains C.'", "'source_identity':'B outward terrace leaf and real track; explicit fixed-torso two-foot gait, sizes and support timing are C. Direction is actually simulated, not only an eye-path reversal.'")
dest=R/'scripts/master_navigation11.py';text=dest.read_text(encoding='utf-8')
assert text.count('# FIXED_TORSO_STEP_IMPLEMENTATION')==1
text=text.replace('# FIXED_TORSO_STEP_IMPLEMENTATION',fn);ast.parse(text);dest.write_text(text,encoding='utf-8')
print('Static gait copied; frozen10 source not changed;11 syntax parsed.')
