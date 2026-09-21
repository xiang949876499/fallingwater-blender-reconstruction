from pathlib import Path
import json,hashlib
r=Path('project');p=r/'scripts/bridge_watertrim10.py';s=p.read_text(encoding='utf8')
(r/'qa/bridge10-watertrim-helper-manifold-failed.py').write_text(s,encoding='utf8')
s=s.replace('import bmesh\n','')
s=s.replace("FILTER_NAME='Bridge10 remove evaluated points with zero incident faces'\nTRI_NAME='Bridge10 preserve original evaluated water triangles'\nGROUP_NAME='Bridge10_Evaluated_Orphan_Point_Filter'\n",'')
a=s.index('    # Exact union leaves collinear/duplicate computational fragments.')
b=s.index('    mask.modifiers.remove(mod);mask.data=final',a);s=s[:a]+s[b:]
a=s.index('\n\ndef _evaluation_filter(water):');b=s.index('\n\ndef apply():',a);s=s[:a]+s[b:]
s=s.replace('    _evaluation_filter(water)\n','').replace("mod.solver='MANIFOLD';mod.use_self=False","mod.solver='EXACT';mod.use_self=False")
s=s.replace("'new_modifiers':[FILTER_NAME,TRI_NAME,*MODIFIERS]","'new_modifiers':list(MODIFIERS)")
s=s.replace("'strategy':'animate and Solidify, discard only zero-face evaluated points, preserve FIXED evaluated triangles, subtract clean actual SW/SE masonry union masks with MANIFOLD each frame'","'strategy':'evaluate animated water and Solidify, then subtract the actual closed SW/SE masonry solids each frame'")
a=r/'qa/bridge10-watertrim-helper-exact-attempt01.py';a.write_text(s,encoding='utf8')
expected=json.loads((r/'qa/bridge10-watertrim-check.json').read_text())['dependencies'];expected=next(v for k,v in expected.items() if k.replace('\\','/').endswith('scripts/bridge_watertrim10.py'));actual=hashlib.sha256(a.read_bytes()).hexdigest();print('ARCHIVED_ORIGINAL_HELPER_SHA',actual,'EXPECTED',expected,'MATCH',actual==expected)
assert actual==expected
s=s.replace('def apply():','def apply(*, diagnostic=False):').replace('    scene=bpy.context.scene','    scene=bpy.context.scene')
s=s.replace('    water=bpy.context.scene.objects.get(WATER_NAME)',"    if not diagnostic:\n        raise ValueError('Known multi-frame geometry failures: diagnostic=True is required only to reproduce the retained failed candidate; do not integrate into production')\n    water=bpy.context.scene.objects.get(WATER_NAME)")
s=s.replace("'status':'ANIMATED_BOOLEAN_CANDIDATE_UNVALIDATED'","'status':'KNOWN_FAILED_MULTI_FRAME_DIAGNOSTIC_ONLY'")
s=s.replace('Only two final Boolean modifiers are added to the existing animated river.','Known physical-validation failure: this helper reproduces a diagnostic scene.\nOnly two final Boolean modifiers are added to the existing animated river.')
p.write_text(s,encoding='utf8')
