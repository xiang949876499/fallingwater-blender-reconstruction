"""Exact world-coordinate topology comparison for reindexed terrain vertices."""
from pathlib import Path
import bpy,numpy as np,hashlib,json,struct,time
ROOT=Path(__file__).resolve().parents[1]
def state(path):
    bpy.ops.wm.open_mainfile(filepath=str(path));ob=bpy.data.objects['SITE_Continuous_BearRun_Terrain'];m=ob.data
    coords=[tuple(ob.matrix_world@v.co) for v in m.vertices]
    vertex_keys=[struct.pack('<3f',*p) for p in coords]
    verts=hashlib.sha256(b''.join(sorted(vertex_keys))).hexdigest()
    polygons=[]
    for p in m.polygons:
        pts=[vertex_keys[i] for i in p.vertices]
        start=min(range(len(pts)),key=lambda i:tuple(pts[i:]+pts[:i]))
        loop=pts[start:]+pts[:start]
        polygons.append(struct.pack('<IIB',len(loop),p.material_index,p.use_smooth)+b''.join(loop))
    edges=[b''.join(sorted((vertex_keys[e.vertices[0]],vertex_keys[e.vertices[1]]))) for e in m.edges]
    return {'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'vertex_multiset':verts,
        'oriented_face_multiset':hashlib.sha256(b''.join(sorted(polygons))).hexdigest(),
        'edge_multiset':hashlib.sha256(b''.join(sorted(edges))).hexdigest(),
        'counts':[len(m.vertices),len(m.edges),len(m.polygons)],'uv_layers':len(m.uv_layers),
        'material_names':[mat.name if mat else None for mat in m.materials]}
a=state(ROOT/'scene/Fallingwater_iteration10.blend');b=state(ROOT/'scene/Fallingwater_iteration10_rebuilt.blend')
keys=[k for k in a if k!='source_sha256'];same={k:a[k]==b[k] for k in keys}
record={'status':'PASS_EXACT_GEOMETRY_REINDEXED' if all(same.values()) else 'FAIL_REAL_SURFACE_DIFFERENCE',
        'source':a,'rebuild':b,'matches':same,
        'scope':'Exact float32 coordinate multiset, oriented face cycles with material/smooth, and edge multiset. No coordinate tolerance; vertex IDs may differ. Only terrain has this diagnostic.'}
(ROOT/'qa/terrain10-rebuild-semantic-check.json').write_text(json.dumps(record,indent=2),encoding='utf8')
print(json.dumps(record),flush=True)
assert all(same.values())
