import bpy,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'qa'))
import shrub08_auditlib as audit
bpy.ops.wm.open_mainfile(filepath=str(R/'scene/Fallingwater_forest_litter_candidate12a.blend'))
expected=json.loads((R/'qa/forest-litter12-candidate-fingerprint.json').read_text())
diff={}
for o in bpy.context.scene.objects:
    if not o.name.startswith('LITTER12_Fern_'):continue
    before=expected['objects'][o.name];after={'properties':json.loads(json.dumps(audit.props(o))),
                                            'world_matrix':[list(r)for r in o.matrix_world]}
    row={}
    for key,value in after.items():
        if value!=before[key]:
            if isinstance(value,dict):row[key]={k:{'before':before[key].get(k),'after':v}for k,v in value.items()if before[key].get(k)!=v}
            else:row[key]={'before':before[key],'after':value}
    if row:diff[o.name]=row
image_diff={}
for im in bpy.data.images:
    value=[im.filepath,im.source,im.colorspace_settings.name,im.alpha_mode]
    before=expected['global']['images'].get(im.name)
    if value!=before:image_diff[im.name]={'before':before,'after':value}
out={'new_fern_changes':diff,'image_changes':image_diff}
out['missing_image_ids']={name:value for name,value in expected['global']['images'].items()if name not in bpy.data.images}
(R/'qa/forest-litter12-reopen-diagnosis.json').write_text(json.dumps(out,indent=2))
print(json.dumps({'ferns':len(diff),'example':next(iter(diff.values())),'images':image_diff,'missing_image_ids':out['missing_image_ids']},indent=2))
