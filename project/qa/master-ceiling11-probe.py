"""Read-only bounded inventory of frozen10 ceiling interfaces. CPU4, no render."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
SRC=R/'scene/Fallingwater_iteration10.blend'
SHA='1e7b17d9c2396513f005724e50788bf834097eedb401b91a7f1030825e2c4ed9'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SHA
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
rows=[]
for o in s.objects:
    if o.type!='MESH':continue
    pts=[o.matrix_world@Vector(v) for v in o.bound_box]
    b=[[min(p[k] for p in pts),max(p[k] for p in pts)] for k in range(3)]
    if b[0][1]<-.8 or b[0][0]>5.1 or b[1][1]<6.5 or b[1][0]>11 or b[2][1]<4.75 or b[2][0]>5.4:continue
    row={'name':o.name,'bounds':b,'room_id':o.get('room_id'),'type':o.get('component_type'),'materials':[m.name for m in o.data.materials],'polygons':len(o.data.polygons),'modifiers':[(m.name,m.type) for m in o.modifiers]}
    if len(o.data.vertices)<50:row['world_vertices']=[list(o.matrix_world@v.co) for v in o.data.vertices]
    rows.append(row)
rayrows=[]
for px,py in [(335,355),(330,354),(329,360),(328,380),(320,385),(318,409),(380,410.5),(416.8,400),(417.4,396),(417.4,405),(417.4,409)]:
    x,y=(px-327)*.0524,(540-py)*.0531
    origin=Vector((x,y,4.7));hits=[]
    for _ in range(12):
        hit,p,n,f,o,m=s.ray_cast(dg,origin,Vector((0,0,1)),distance=.9)
        if not hit:break
        hits.append({'name':o.name,'z':p.z,'normal':list(n)});origin=p+Vector((0,0,.0001))
    rayrows.append({'source_xy':[px,py],'hits':hits})
out={'source':str(SRC),'sha256':SHA,'objects':rows,'rays':rayrows,'saved':False,'rendered':False}
(R/'qa/master-ceiling11-probe.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({'objects':[{k:v for k,v in r.items() if k not in ('world_vertices','modifiers','materials')} for r in rows],'rays':rayrows},indent=2))
