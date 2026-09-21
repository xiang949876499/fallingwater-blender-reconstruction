"""Compare saved geometry from source-overlay and fresh construction paths."""
from pathlib import Path
import bpy,hashlib,json,struct,time
ROOT=Path(__file__).resolve().parents[1]
sources=[ROOT/'scene/Fallingwater_integration_candidate10a.blend',ROOT/'scene/Fallingwater_rebuild_candidate10a.blend']
out=ROOT/'qa/rebuild10-comparison.json';assert not out.exists()
def state(path):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    cache={};objects={}
    for ob in bpy.context.scene.objects:
        h=hashlib.sha256();h.update(ob.type.encode())
        for row in ob.matrix_world:h.update(struct.pack('<4f',*row))
        if ob.type=='MESH':
            mesh=ob.data;key=mesh.as_pointer()
            if key not in cache:
                mh=hashlib.sha256()
                mh.update(struct.pack('<III',len(mesh.vertices),len(mesh.edges),len(mesh.polygons)))
                for v in mesh.vertices:mh.update(struct.pack('<3f',*v.co))
                for a,b in sorted(tuple(sorted(e.vertices)) for e in mesh.edges):mh.update(struct.pack('<II',a,b))
                for p in mesh.polygons:
                    mh.update(struct.pack('<IIB',len(p.vertices),p.material_index,p.use_smooth))
                    mh.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
                for uv in mesh.uv_layers:
                    for item in uv.data:mh.update(struct.pack('<2f',*item.uv))
                mh.update(repr([m.name if m else None for m in mesh.materials]).encode())
                cache[key]=mh.digest()
            h.update(cache[key])
        elif ob.type=='CURVE':
            h.update(repr((ob.data.bevel_depth,ob.data.bevel_resolution,ob.data.resolution_u)).encode())
            for spline in ob.data.splines:
                h.update(repr((spline.type,spline.use_cyclic_u)).encode())
                for p in spline.points:h.update(struct.pack('<4f',*p.co))
                for p in spline.bezier_points:
                    for v in (p.co,p.handle_left,p.handle_right):h.update(struct.pack('<3f',*v))
        elif ob.type=='CAMERA':
            h.update(repr((ob.data.lens,ob.data.shift_x,ob.data.shift_y,ob.data.clip_start,ob.data.clip_end)).encode())
        elif ob.type=='LIGHT':
            h.update(repr((ob.data.type,ob.data.energy,list(ob.data.color))).encode())
        objects[ob.name]=h.hexdigest()
    return {'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'objects':objects,
        'rooms':json.loads(bpy.data.texts['FW_ROOMS.json'].as_string())}
started=time.monotonic();a,b=map(state,sources)
common=a['objects'].keys()&b['objects'].keys()
added=sorted(b['objects'].keys()-a['objects'].keys());removed=sorted(a['objects'].keys()-b['objects'].keys())
changed=sorted(n for n in common if a['objects'][n]!=b['objects'][n])
record={'status':'PASS_SAVED_GEOMETRY_REPRODUCTION' if not added and not removed and not changed else 'FAIL_GEOMETRY_OR_CAMERA_DIFFERENCE',
 'source':{k:v for k,v in a.items() if k!='objects' and k!='rooms'},'rebuild':{k:v for k,v in b.items() if k!='objects' and k!='rooms'},
 'counts':[len(a['objects']),len(b['objects'])],'added':added,'removed':removed,'changed':changed,
 'unchanged_count':len(common)-len(changed),'room_counts':[len(a['rooms']),len(b['rooms'])],
 'room_metadata_changed':[x['id'] for x,y in zip(a['rooms'],b['rooms']) if x!=y],
 'method':'World transform plus vertices, canonical edge set, ordered polygons/material indices/smooth/UV/material names; curves and saved cameras/lights separately',
 'limits':'This comparison does not establish photographic acceptance or replace evaluated geometry/navigation checks',
 'seconds':time.monotonic()-started}
out.write_text(json.dumps(record,indent=2),encoding='utf8');print(json.dumps(record),flush=True)
if changed or added or removed:raise RuntimeError('Saved fresh rebuild differs; inspect explicit object list')
