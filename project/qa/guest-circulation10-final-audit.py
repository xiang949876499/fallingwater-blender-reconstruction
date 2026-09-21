"""Independent reopen, full local replay and finish-plane/mesh audit."""
import bpy, sys, json, hashlib, importlib.util, collections
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/zx/test/project')
spec=importlib.util.spec_from_file_location('c10check',ROOT/'qa/guest-circulation10-check.py')
check=importlib.util.module_from_spec(spec);spec.loader.exec_module(check)
freeze=json.loads((ROOT/'qa/guest-circulation10-freeze.json').read_text(encoding='utf-8'))
actual_sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
assert actual_sha==freeze['sha256']
report=check.execute(reopen=True)
manifest=json.loads(bpy.data.texts['FW_GUEST_CIRCULATION10_CANDIDATE.json'].as_string())
dg=bpy.context.evaluated_depsgraph_get();verts=[];faces=[];owners=[]
targets=('GUEST_B1_BASE_EAST_pier_end','GUEST_LAYERED_SANDSTONE_COURSES',check.c10.FIXED_WALL)
for name in targets:
    ob=bpy.data.objects[name];eo=ob.evaluated_get(dg);mesh=eo.to_mesh();off=len(verts)
    verts.extend(eo.matrix_world@v.co for v in mesh.vertices)
    faces.extend(tuple(off+i for i in p.vertices) for p in mesh.polygons)
    owners.extend([name]*len(mesh.polygons));eo.to_mesh_clear()
tree=BVHTree.FromPolygons(verts,faces,epsilon=.000001)
measurements=[]
for yy in range(377,401):
    x,y=check.c10.source_point((294.45,yy))
    for z in (7.55,7.80,8.05):
        hits=[]
        for dx in (-1,1):
            loc,normal,index,dist=tree.ray_cast(Vector((x,y,z)),Vector((dx,0,0)),2)
            hits.append(None if loc is None else {'object':owners[index],'point':list(loc),'normal':list(normal)})
        width=hits[1]['point'][0]-hits[0]['point'][0] if all(hits) else None
        measurements.append({'source_y':yy,'z':z,'hits':hits,'width':width,
                             'within20mm':width is not None and abs(width-.7366)<=.020})
widths=[m['width'] for m in measurements if m['width'] is not None]
mesh_audit=[]
for name in dict.fromkeys(manifest['created_objects']+[m['object'] for m in manifest.get('explicit_mutations',[])]):
    ob=bpy.data.objects.get(name)
    if ob is None or ob.type not in {'MESH','CURVE'}:continue
    eo=ob.evaluated_get(dg);mesh=eo.to_mesh();edges=collections.Counter()
    for p in mesh.polygons:
        vv=list(p.vertices)
        for a,b in zip(vv,vv[1:]+vv[:1]):edges[tuple(sorted((a,b)))]+=1
    mesh_audit.append({'object':name,'vertices':len(mesh.vertices),'faces':len(mesh.polygons),
                       'boundary_edges':sum(n==1 for n in edges.values()),'nonmanifold_edges':sum(n>2 for n in edges.values())})
    eo.to_mesh_clear()
result={'candidate_sha256':actual_sha,'source_sha256':check.c10.SOURCE_SHA,
        'independent_reopen_counts':report['counts'],'actual_local_sample_count':sum(c['samples'] for c in report['checks']),
        'implementation_matches_loaded_candidate':hashlib.sha256((ROOT/'scripts/guest_circulation10.py').read_bytes()).hexdigest()==manifest.get('implementation_sha256'),
        'twoftfive_nominal_m':.7366,'finish_measurement_count':len(measurements),'finish_width_min_max':[min(widths),max(widths)],
        'finish_failures':[m for m in measurements if not m['within20mm']],'finish_measurements':measurements,
        'solid_mesh_audit':mesh_audit,'solid_mesh_failures':[m for m in mesh_audit if m['boundary_edges'] or m['nonmanifold_edges']],
        'terminal_union_removed_coincident_objects':manifest.get('terminal_paving_union_removed'),
        'connector_uniform_actual_riser_m':manifest.get('connector_actual_riser_m'),
        'no_full_tour_or_global_adjacency_claim':True,'not_installed_in_production':True}
(ROOT/'qa/guest-circulation10-final-audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('C10 FINAL',json.dumps({k:v for k,v in result.items() if k not in ('finish_measurements','solid_mesh_audit','finish_failures','solid_mesh_failures')}),flush=True)
assert result['implementation_matches_loaded_candidate']
assert report['counts']['FAIL']==0, 'Keep candidate negative, no local acceptance'
assert not result['finish_failures']
assert not result['solid_mesh_failures']
