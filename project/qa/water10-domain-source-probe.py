"""Geometry arrays only: evaluate one C inlet against frozen actual triangles. Save no scene."""
import json,math
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'qa';g=np.load(P/'water10-domain-probe-grid.npz');old=json.loads((P/'water-hybrid07a-geometry.json').read_text(encoding='utf-8'));V=g['vertices'];F=g['faces'];tree=BVHTree.FromPolygons(V,F,all_triangles=True)
sections=old['sections'][135:144];vv=[];ff=[];width=.24;thickness=.23
for i,p in enumerate(sections):
 top=Vector(p['top']);tan=Vector(p['tangent']);depth=Vector(p['depth_axis']);side=tan.cross(depth).normalized()
 for j in range(40):
  a=j*math.tau/40;vv.append(tuple(top+side*(width*.5*math.cos(a))+depth*(thickness*(.5+.5*math.sin(a)))))
 if i:
  for j in range(40):
   a=(i-1)*40+j;b=(i-1)*40+(j+1)%40;c=i*40+(j+1)%40;d=i*40+j;ff.extend([(a,b,c),(a,c,d)])
for base,reverse in [(0,True),(len(vv)-40,False)]:
 for j in range(1,39):ff.append((base,base+j+1,base+j) if reverse else (base,base+j,base+j+1))
vv=np.array(vv);ff=np.array(ff);src=BVHTree.FromPolygons(vv,ff,all_triangles=True);pairs=src.overlap(tree);samples=np.vstack([vv,vv[ff].mean(1)]);near=[tree.find_nearest(Vector(p))[3] for p in samples];roi=np.array([[-16,8],[-17,6],[-7.7,-4.95]])
factor=40/8*math.sin(math.tau/40);speed=sections[4]['speed_m_s'];Q=factor*width*thickness*speed
out={'status':'ONE_C_SOURCE_GEOMETRY_ARRAY_PROBE_NOT_MODEL_OR_BAKE','basis':'Existing gravity centerline sections135-143; newCwidth/thickness, oldv3/terrain/banks unchanged','world_vertices':vv.tolist(),'triangles':ff.tolist(),'width_m':width,'thickness_m':thickness,'axial_centerline_length_m':float(sum(np.linalg.norm(np.array(sections[i+1]['top'])-sections[i]['top']) for i in range(len(sections)-1))),'center_velocity_world_m_s':list(Vector(sections[4]['tangent'])*speed),'nominal_speed_m_s':speed,'nominal_Q_m3_s':Q,'flow_is_authored_design_not_measured_discharge':True,'cross_section_area_m2':factor*width*thickness,'source_aabb_world_m':np.stack((vv.min(0),vv.max(0)),1).tolist(),'source_triangle_overlap_pairs_with_real_collision':len(pairs),'source_vertex_and_triangle_centroid_samples':len(samples),'min_sampled_clearance_to_frozen_triangles_m':float(min(near)),'source_fully_inside_proposed_domain':bool(np.all(vv>roi[:,0]) and np.all(vv<roi[:,1])),'cell_m_320':.075,'thickness_cells_320':thickness/.075,'width_cells_320':width/.075,'cell_m_384':.0625,'thickness_cells_384':thickness/.0625,'width_cells_384':width/.0625,'upstream_available_capped_6cm_area_at_s_minus0_2_m2':.17972631549835205,'upstream_mean_speed_required_if_all_this_area_used_m_s':Q/.17972631549835205,'upstream_geometry_join_status':'NOT_BUILT: cap-by-realbed thinbranch must follow actualrifts; do not install uniformwideellipse atlip','old70percentFAIL_unchanged':True}
(P/'water10-domain-source-probe.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print('W10_SOURCE',json.dumps({k:v for k,v in out.items() if k not in ['world_vertices','triangles']}),flush=True)
