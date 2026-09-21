"""Apply the visually accepted sixteen-root shrub08 shape without respawning.

Call build(ctx, {'enabled': True}) after final site/root seating and before
navigation validation. No geometry fitting, root relocation or material edits.
The approved mesh/matrix manifest is embedded; QA files are not runtime inputs.
"""
import bpy
import hashlib
import json
import math
import re
import struct
from pathlib import Path

# Generated immutable manifest; readable copy: qa/shrub09-integration-manifest.json.
APPROVED = json.loads(r'''{"accepted_candidate_sha256":"7dc113c93cab8dfae0ea73f1c797f92849d9e183f00a697040cfed346c06dc97","generator_sha256":"ecda4c99d9f36608241e78be34e1ba3e81208ea3bede5a6a0060a111bcf05bc2","assets":{"2":{"old_branch_mesh":"TREE_Understory_2_Stems","old_leaf_mesh":"TREE_Understory_2_Leaves","new_branch_mesh":"CANDIDATE08_RhododendronLike_2_Branches","new_leaf_mesh":"CANDIDATE08_RhododendronLike_2_Leaves","new_branch_signature":"9d534eba6fabf45fddae1cb442d82eb1f8743ab11d2dc6cb13ff2bc492d4bfe5","new_leaf_signature":"994efaea1b941fde110900624178a8a55e72c4a2cbba31d9d69958e703467385","leaf_count":236,"total_triangles":3832,"removed_design_leaf_ids":[154,160,170,182]},"3":{"old_branch_mesh":"TREE_Understory_3_Stems","old_leaf_mesh":"TREE_Understory_3_Leaves","new_branch_mesh":"CANDIDATE08_RhododendronLike_3_Branches","new_leaf_mesh":"CANDIDATE08_RhododendronLike_3_Leaves","new_branch_signature":"d3be8d51e6454d9ff8246d5d949cc8b090374782877f0832c1b9e5164059facd","new_leaf_signature":"7711ae8385e4a76d86326a58b46eefe09a29ea1ae81fb7b1d69131f5c62bb2e3","leaf_count":286,"total_triangles":4632,"removed_design_leaf_ids":[100,103]}},"objects":[{"name":"TREE_Understory_0062_Branches","asset":2,"part":"branches","matrix":[[0.4470835328102112,0.920619547367096,0,-9.555996894836426],[-0.920619547367096,0.4470835328102112,0,5.880136489868164],[0,0,1.0234373807907104,1.2008448839187622],[0,0,0,1]],"old_mesh":"TREE_Understory_2_Stems","old_signature":"81459d042dfaaeca80f7347200700462c1bba58f8d2eb82dbe261fca9cc7566f","new_mesh":"CANDIDATE08_RhododendronLike_2_Branches","new_signature":"9d534eba6fabf45fddae1cb442d82eb1f8743ab11d2dc6cb13ff2bc492d4bfe5"},{"name":"TREE_Understory_0062_Leaves","asset":2,"part":"leaves","matrix":[[0.4470835328102112,0.920619547367096,0,-9.555996894836426],[-0.920619547367096,0.4470835328102112,0,5.880136489868164],[0,0,1.0234373807907104,1.2008448839187622],[0,0,0,1]],"old_mesh":"TREE_Understory_2_Leaves","old_signature":"c26d45b89537949adb552839d27d1eafe8e8afe2056d56614e514b42b2785a32","new_mesh":"CANDIDATE08_RhododendronLike_2_Leaves","new_signature":"994efaea1b941fde110900624178a8a55e72c4a2cbba31d9d69958e703467385"},{"name":"TREE_Understory_0558_Branches","asset":2,"part":"branches","matrix":[[0.15309010446071625,1.2470813989639282,0,-8.507365226745605],[-1.2470813989639282,0.15309010446071625,0,1.5759412050247192],[0,0,1.256442904472351,-1.4715489149093628],[0,0,0,1]],"old_mesh":"TREE_Understory_2_Stems","old_signature":"81459d042dfaaeca80f7347200700462c1bba58f8d2eb82dbe261fca9cc7566f","new_mesh":"CANDIDATE08_RhododendronLike_2_Branches","new_signature":"9d534eba6fabf45fddae1cb442d82eb1f8743ab11d2dc6cb13ff2bc492d4bfe5"},{"name":"TREE_Understory_0558_Leaves","asset":2,"part":"leaves","matrix":[[0.15309010446071625,1.2470813989639282,0,-8.507365226745605],[-1.2470813989639282,0.15309010446071625,0,1.5759412050247192],[0,0,1.256442904472351,-1.4715489149093628],[0,0,0,1]],"old_mesh":"TREE_Understory_2_Leaves","old_signature":"c26d45b89537949adb552839d27d1eafe8e8afe2056d56614e514b42b2785a32","new_mesh":"CANDIDATE08_RhododendronLike_2_Leaves","new_signature":"994efaea1b941fde110900624178a8a55e72c4a2cbba31d9d69958e703467385"},{"name":"TREE_Understory_0679_Branches","asset":3,"part":"branches","matrix":[[-1.201249122619629,0.4855377972126007,0,-11.869314193725586],[-0.4855377972126007,-1.201249122619629,0,7.974980354309082],[0,0,1.2956644296646118,1.5661860704421997],[0,0,0,1]],"old_mesh":"TREE_Understory_3_Stems","old_signature":"7f406e83cf1377ef4031ad1dd34936366db8224db9c47037ab885568dcb2bca2","new_mesh":"CANDIDATE08_RhododendronLike_3_Branches","new_signature":"d3be8d51e6454d9ff8246d5d949cc8b090374782877f0832c1b9e5164059facd"},{"name":"TREE_Understory_0679_Leaves","asset":3,"part":"leaves","matrix":[[-1.201249122619629,0.4855377972126007,0,-11.869314193725586],[-0.4855377972126007,-1.201249122619629,0,7.974980354309082],[0,0,1.2956644296646118,1.5661860704421997],[0,0,0,1]],"old_mesh":"TREE_Understory_3_Leaves","old_signature":"c9e441f79bf039096e72097c098f005e04badca3bb4496772a3ac136833da304","new_mesh":"CANDIDATE08_RhododendronLike_3_Leaves","new_signature":"7711ae8385e4a76d86326a58b46eefe09a29ea1ae81fb7b1d69131f5c62bb2e3"},{"name":"TREE_Understory_0895_Branches","asset":3,"part":"branches","matrix":[[-0.487539678812027,0.9134591817855835,0,-14.315200805664062],[-0.9134591817855835,-0.487539678812027,0,-0.030478311702609062],[0,0,1.0354238748550415,-0.2519749701023102],[0,0,0,1]],"old_mesh":"TREE_Understory_3_Stems","old_signature":"7f406e83cf1377ef4031ad1dd34936366db8224db9c47037ab885568dcb2bca2","new_mesh":"CANDIDATE08_RhododendronLike_3_Branches","new_signature":"d3be8d51e6454d9ff8246d5d949cc8b090374782877f0832c1b9e5164059facd"},{"name":"TREE_Understory_0895_Leaves","asset":3,"part":"leaves","matrix":[[-0.487539678812027,0.9134591817855835,0,-14.315200805664062],[-0.9134591817855835,-0.487539678812027,0,-0.030478311702609062],[0,0,1.0354238748550415,-0.2519749701023102],[0,0,0,1]],"old_mesh":"TREE_Understory_3_Leaves","old_signature":"c9e441f79bf039096e72097c098f005e04badca3bb4496772a3ac136833da304","new_mesh":"CANDIDATE08_RhododendronLike_3_Leaves","new_signature":"7711ae8385e4a76d86326a58b46eefe09a29ea1ae81fb7b1d69131f5c62bb2e3"},{"name":"TREE_Understory_1191_Branches","asset":3,"part":"branches","matrix":[[0.5731304883956909,-0.9655048847198486,0,-8.364734649658203],[0.9655048847198486,0.5731304883956909,0,0.7919427156448364],[0,0,1.122799277305603,-2.6123266220092773],[0,0,0,1]],"old_mesh":"TREE_Understory_3_Stems","old_signature":"7f406e83cf1377ef4031ad1dd34936366db8224db9c47037ab885568dcb2bca2","new_mesh":"CANDIDATE08_RhododendronLike_3_Branches","new_signature":"d3be8d51e6454d9ff8246d5d949cc8b090374782877f0832c1b9e5164059facd"},{"name":"TREE_Understory_1191_Leaves","asset":3,"part":"leaves","matrix":[[0.5731304883956909,-0.9655048847198486,0,-8.364734649658203],[0.9655048847198486,0.5731304883956909,0,0.7919427156448364],[0,0,1.122799277305603,-2.6123266220092773],[0,0,0,1]],"old_mesh":"TREE_Understory_3_Leaves","old_signature":"c9e441f79bf039096e72097c098f005e04badca3bb4496772a3ac136833da304","new_mesh":"CANDIDATE08_RhododendronLike_3_Leaves","new_signature":"7711ae8385e4a76d86326a58b46eefe09a29ea1ae81fb7b1d69131f5c62bb2e3"},{"name":"TREE_Understory_1590_Branches","asset":2,"part":"branches","matrix":[[0.36922264099121094,0.7600151896476746,0,-14.227423667907715],[-0.7600151896476746,0.36922264099121094,0,1.136614441871643],[0,0,0.8449546694755554,0.02340039052069187],[0,0,0,1]],"old_mesh":"TREE_Understory_2_Stems","old_signature":"81459d042dfaaeca80f7347200700462c1bba58f8d2eb82dbe261fca9cc7566f","new_mesh":"CANDIDATE08_RhododendronLike_2_Branches","new_signature":"9d534eba6fabf45fddae1cb442d82eb1f8743ab11d2dc6cb13ff2bc492d4bfe5"},{"name":"TREE_Understory_1590_Leaves","asset":2,"part":"leaves","matrix":[[0.36922264099121094,0.7600151896476746,0,-14.227423667907715],[-0.7600151896476746,0.36922264099121094,0,1.136614441871643],[0,0,0.8449546694755554,0.02340039052069187],[0,0,0,1]],"old_mesh":"TREE_Understory_2_Leaves","old_signature":"c26d45b89537949adb552839d27d1eafe8e8afe2056d56614e514b42b2785a32","new_mesh":"CANDIDATE08_RhododendronLike_2_Leaves","new_signature":"994efaea1b941fde110900624178a8a55e72c4a2cbba31d9d69958e703467385"},{"name":"TREE_Understory_1990_Branches","asset":2,"part":"branches","matrix":[[0.2181062549352646,-1.2940431833267212,0,-9.967323303222656],[1.2940431833267212,0.2181062549352646,0,1.6403555870056152],[0,0,1.3122949600219727,-0.3317936956882477],[0,0,0,1]],"old_mesh":"TREE_Understory_2_Stems","old_signature":"81459d042dfaaeca80f7347200700462c1bba58f8d2eb82dbe261fca9cc7566f","new_mesh":"CANDIDATE08_RhododendronLike_2_Branches","new_signature":"9d534eba6fabf45fddae1cb442d82eb1f8743ab11d2dc6cb13ff2bc492d4bfe5"},{"name":"TREE_Understory_1990_Leaves","asset":2,"part":"leaves","matrix":[[0.2181062549352646,-1.2940431833267212,0,-9.967323303222656],[1.2940431833267212,0.2181062549352646,0,1.6403555870056152],[0,0,1.3122949600219727,-0.3317936956882477],[0,0,0,1]],"old_mesh":"TREE_Understory_2_Leaves","old_signature":"c26d45b89537949adb552839d27d1eafe8e8afe2056d56614e514b42b2785a32","new_mesh":"CANDIDATE08_RhododendronLike_2_Leaves","new_signature":"994efaea1b941fde110900624178a8a55e72c4a2cbba31d9d69958e703467385"},{"name":"TREE_Understory_1998_Branches","asset":2,"part":"branches","matrix":[[0.8648484349250793,0.10920873284339905,0,-11.402466773986816],[-0.10920873284339905,0.8648484349250793,0,3.112031936645508],[0,0,0.871716320514679,0.3677760064601898],[0,0,0,1]],"old_mesh":"TREE_Understory_2_Stems","old_signature":"81459d042dfaaeca80f7347200700462c1bba58f8d2eb82dbe261fca9cc7566f","new_mesh":"CANDIDATE08_RhododendronLike_2_Branches","new_signature":"9d534eba6fabf45fddae1cb442d82eb1f8743ab11d2dc6cb13ff2bc492d4bfe5"},{"name":"TREE_Understory_1998_Leaves","asset":2,"part":"leaves","matrix":[[0.8648484349250793,0.10920873284339905,0,-11.402466773986816],[-0.10920873284339905,0.8648484349250793,0,3.112031936645508],[0,0,0.871716320514679,0.3677760064601898],[0,0,0,1]],"old_mesh":"TREE_Understory_2_Leaves","old_signature":"c26d45b89537949adb552839d27d1eafe8e8afe2056d56614e514b42b2785a32","new_mesh":"CANDIDATE08_RhododendronLike_2_Leaves","new_signature":"994efaea1b941fde110900624178a8a55e72c4a2cbba31d9d69958e703467385"},{"name":"TREE_Understory_0055_Branches","asset":3,"part":"branches","matrix":[[1.1767663955688477,0.6998964548110962,0,24.964004516601562],[-0.6998964548110962,1.1767663955688477,0,11.966643333435059],[0,0,1.3691728115081787,1.335618019104004],[0,0,0,1]],"old_mesh":"TREE_Understory_3_Stems","old_signature":"7f406e83cf1377ef4031ad1dd34936366db8224db9c47037ab885568dcb2bca2","new_mesh":"CANDIDATE08_RhododendronLike_3_Branches","new_signature":"d3be8d51e6454d9ff8246d5d949cc8b090374782877f0832c1b9e5164059facd"},{"name":"TREE_Understory_0055_Leaves","asset":3,"part":"leaves","matrix":[[1.1767663955688477,0.6998964548110962,0,24.964004516601562],[-0.6998964548110962,1.1767663955688477,0,11.966643333435059],[0,0,1.3691728115081787,1.335618019104004],[0,0,0,1]],"old_mesh":"TREE_Understory_3_Leaves","old_signature":"c9e441f79bf039096e72097c098f005e04badca3bb4496772a3ac136833da304","new_mesh":"CANDIDATE08_RhododendronLike_3_Leaves","new_signature":"7711ae8385e4a76d86326a58b46eefe09a29ea1ae81fb7b1d69131f5c62bb2e3"},{"name":"TREE_Understory_1071_Branches","asset":3,"part":"branches","matrix":[[-0.8270652890205383,-0.30539432168006897,0,26.908525466918945],[0.30539432168006897,-0.8270652890205383,0,10.073202133178711],[0,0,0.8816477060317993,2.459946632385254],[0,0,0,1]],"old_mesh":"TREE_Understory_3_Stems","old_signature":"7f406e83cf1377ef4031ad1dd34936366db8224db9c47037ab885568dcb2bca2","new_mesh":"CANDIDATE08_RhododendronLike_3_Branches","new_signature":"d3be8d51e6454d9ff8246d5d949cc8b090374782877f0832c1b9e5164059facd"},{"name":"TREE_Understory_1071_Leaves","asset":3,"part":"leaves","matrix":[[-0.8270652890205383,-0.30539432168006897,0,26.908525466918945],[0.30539432168006897,-0.8270652890205383,0,10.073202133178711],[0,0,0.8816477060317993,2.459946632385254],[0,0,0,1]],"old_mesh":"TREE_Understory_3_Leaves","old_signature":"c9e441f79bf039096e72097c098f005e04badca3bb4496772a3ac136833da304","new_mesh":"CANDIDATE08_RhododendronLike_3_Leaves","new_signature":"7711ae8385e4a76d86326a58b46eefe09a29ea1ae81fb7b1d69131f5c62bb2e3"},{"name":"TREE_Understory_1334_Branches","asset":2,"part":"branches","matrix":[[-1.2348171472549438,-0.30289962887763977,0,31.19938850402832],[0.30289962887763977,-1.2348171472549438,0,16.473295211791992],[0,0,1.2714250087738037,4.27230167388916],[0,0,0,1]],"old_mesh":"TREE_Understory_2_Stems","old_signature":"81459d042dfaaeca80f7347200700462c1bba58f8d2eb82dbe261fca9cc7566f","new_mesh":"CANDIDATE08_RhododendronLike_2_Branches","new_signature":"9d534eba6fabf45fddae1cb442d82eb1f8743ab11d2dc6cb13ff2bc492d4bfe5"},{"name":"TREE_Understory_1334_Leaves","asset":2,"part":"leaves","matrix":[[-1.2348171472549438,-0.30289962887763977,0,31.19938850402832],[0.30289962887763977,-1.2348171472549438,0,16.473295211791992],[0,0,1.2714250087738037,4.27230167388916],[0,0,0,1]],"old_mesh":"TREE_Understory_2_Leaves","old_signature":"c26d45b89537949adb552839d27d1eafe8e8afe2056d56614e514b42b2785a32","new_mesh":"CANDIDATE08_RhododendronLike_2_Leaves","new_signature":"994efaea1b941fde110900624178a8a55e72c4a2cbba31d9d69958e703467385"},{"name":"TREE_Understory_2150_Branches","asset":2,"part":"branches","matrix":[[-1.2643015384674072,0.583620548248291,0,28.64962387084961],[-0.583620548248291,-1.2643015384674072,0,11.335426330566406],[0,0,1.392505407333374,2.93221378326416],[0,0,0,1]],"old_mesh":"TREE_Understory_2_Stems","old_signature":"81459d042dfaaeca80f7347200700462c1bba58f8d2eb82dbe261fca9cc7566f","new_mesh":"CANDIDATE08_RhododendronLike_2_Branches","new_signature":"9d534eba6fabf45fddae1cb442d82eb1f8743ab11d2dc6cb13ff2bc492d4bfe5"},{"name":"TREE_Understory_2150_Leaves","asset":2,"part":"leaves","matrix":[[-1.2643015384674072,0.583620548248291,0,28.64962387084961],[-0.583620548248291,-1.2643015384674072,0,11.335426330566406],[0,0,1.392505407333374,2.93221378326416],[0,0,0,1]],"old_mesh":"TREE_Understory_2_Leaves","old_signature":"c26d45b89537949adb552839d27d1eafe8e8afe2056d56614e514b42b2785a32","new_mesh":"CANDIDATE08_RhododendronLike_2_Leaves","new_signature":"994efaea1b941fde110900624178a8a55e72c4a2cbba31d9d69958e703467385"},{"name":"TREE_Understory_0110_Branches","asset":2,"part":"branches","matrix":[[-0.7146003842353821,0.3566915988922119,0,29.238452911376953],[-0.3566915988922119,-0.7146003842353821,0,17.400630950927734],[0,0,0.798675537109375,4.419167518615723],[0,0,0,1]],"old_mesh":"TREE_Understory_2_Stems","old_signature":"81459d042dfaaeca80f7347200700462c1bba58f8d2eb82dbe261fca9cc7566f","new_mesh":"CANDIDATE08_RhododendronLike_2_Branches","new_signature":"9d534eba6fabf45fddae1cb442d82eb1f8743ab11d2dc6cb13ff2bc492d4bfe5"},{"name":"TREE_Understory_0110_Leaves","asset":2,"part":"leaves","matrix":[[-0.7146003842353821,0.3566915988922119,0,29.238452911376953],[-0.3566915988922119,-0.7146003842353821,0,17.400630950927734],[0,0,0.798675537109375,4.419167518615723],[0,0,0,1]],"old_mesh":"TREE_Understory_2_Leaves","old_signature":"c26d45b89537949adb552839d27d1eafe8e8afe2056d56614e514b42b2785a32","new_mesh":"CANDIDATE08_RhododendronLike_2_Leaves","new_signature":"994efaea1b941fde110900624178a8a55e72c4a2cbba31d9d69958e703467385"},{"name":"TREE_Understory_1338_Branches","asset":2,"part":"branches","matrix":[[-1.1035057306289673,-0.6786905527114868,0,28.42341423034668],[0.6786905527114868,-1.1035057306289673,0,10.084847450256348],[0,0,1.2955098152160645,2.50893497467041],[0,0,0,1]],"old_mesh":"TREE_Understory_2_Stems","old_signature":"81459d042dfaaeca80f7347200700462c1bba58f8d2eb82dbe261fca9cc7566f","new_mesh":"CANDIDATE08_RhododendronLike_2_Branches","new_signature":"9d534eba6fabf45fddae1cb442d82eb1f8743ab11d2dc6cb13ff2bc492d4bfe5"},{"name":"TREE_Understory_1338_Leaves","asset":2,"part":"leaves","matrix":[[-1.1035057306289673,-0.6786905527114868,0,28.42341423034668],[0.6786905527114868,-1.1035057306289673,0,10.084847450256348],[0,0,1.2955098152160645,2.50893497467041],[0,0,0,1]],"old_mesh":"TREE_Understory_2_Leaves","old_signature":"c26d45b89537949adb552839d27d1eafe8e8afe2056d56614e514b42b2785a32","new_mesh":"CANDIDATE08_RhododendronLike_2_Leaves","new_signature":"994efaea1b941fde110900624178a8a55e72c4a2cbba31d9d69958e703467385"},{"name":"TREE_Understory_1342_Branches","asset":2,"part":"branches","matrix":[[-0.7309195399284363,-0.4866516590118408,0,29.383419036865234],[0.4866516590118408,-0.7309195399284363,0,8.856287956237793],[0,0,0.8781077861785889,1.0620356798171997],[0,0,0,1]],"old_mesh":"TREE_Understory_2_Stems","old_signature":"81459d042dfaaeca80f7347200700462c1bba58f8d2eb82dbe261fca9cc7566f","new_mesh":"CANDIDATE08_RhododendronLike_2_Branches","new_signature":"9d534eba6fabf45fddae1cb442d82eb1f8743ab11d2dc6cb13ff2bc492d4bfe5"},{"name":"TREE_Understory_1342_Leaves","asset":2,"part":"leaves","matrix":[[-0.7309195399284363,-0.4866516590118408,0,29.383419036865234],[0.4866516590118408,-0.7309195399284363,0,8.856287956237793],[0,0,0.8781077861785889,1.0620356798171997],[0,0,0,1]],"old_mesh":"TREE_Understory_2_Leaves","old_signature":"c26d45b89537949adb552839d27d1eafe8e8afe2056d56614e514b42b2785a32","new_mesh":"CANDIDATE08_RhododendronLike_2_Leaves","new_signature":"994efaea1b941fde110900624178a8a55e72c4a2cbba31d9d69958e703467385"},{"name":"TREE_Understory_1043_Branches","asset":3,"part":"branches","matrix":[[-0.6817524433135986,0.6172019243240356,0,31.073415756225586],[-0.6172019243240356,-0.6817524433135986,0,15.664605140686035],[0,0,0.9196328520774841,4.092354774475098],[0,0,0,1]],"old_mesh":"TREE_Understory_3_Stems","old_signature":"7f406e83cf1377ef4031ad1dd34936366db8224db9c47037ab885568dcb2bca2","new_mesh":"CANDIDATE08_RhododendronLike_3_Branches","new_signature":"d3be8d51e6454d9ff8246d5d949cc8b090374782877f0832c1b9e5164059facd"},{"name":"TREE_Understory_1043_Leaves","asset":3,"part":"leaves","matrix":[[-0.6817524433135986,0.6172019243240356,0,31.073415756225586],[-0.6172019243240356,-0.6817524433135986,0,15.664605140686035],[0,0,0.9196328520774841,4.092354774475098],[0,0,0,1]],"old_mesh":"TREE_Understory_3_Leaves","old_signature":"c9e441f79bf039096e72097c098f005e04badca3bb4496772a3ac136833da304","new_mesh":"CANDIDATE08_RhododendronLike_3_Leaves","new_signature":"7711ae8385e4a76d86326a58b46eefe09a29ea1ae81fb7b1d69131f5c62bb2e3"}]}''')


def mesh_signature(mesh):
    """Position/topology/material-index/smooth/UV/material-name signature."""
    h = hashlib.sha256()
    h.update(struct.pack('<III',len(mesh.vertices),len(mesh.edges),len(mesh.polygons)))
    for v in mesh.vertices:
        h.update(struct.pack('<3f',*v.co))
    for edge in mesh.edges:
        h.update(struct.pack('<2I',*edge.vertices))
    for poly in mesh.polygons:
        h.update(struct.pack('<IIB',len(poly.vertices),poly.material_index,poly.use_smooth))
        for index in poly.vertices:
            h.update(struct.pack('<I',index))
    for layer in mesh.uv_layers:
        h.update(layer.name.encode()+b'\0')
        for value in layer.data:
            h.update(struct.pack('<2f',*value.uv))
    h.update(json.dumps([m.name if m else None for m in mesh.materials]).encode())
    return h.hexdigest()


def _matrix_error(actual, expected):
    return max(abs(actual[i][j]-expected[i][j]) for i in range(4) for j in range(4))


def build(ctx, settings=None):
    options = {'enabled': False}
    options.update(settings or {})
    if set(options) != {'enabled'}:
        raise ValueError('Only the explicit enabled option is supported; labels and transforms are not mutable')
    if not options['enabled']:
        return {'status': 'NOT_RUN_DISABLED'}
    if APPROVED is None:
        raise RuntimeError('Approved manifest has not been embedded')
    import understory_detail08
    source = Path(understory_detail08.__file__)
    if hashlib.sha256(source.read_bytes()).hexdigest() != APPROVED['generator_sha256']:
        raise ValueError('The accepted geometry generator changed; re-approval required')
    bpy.context.view_layer.update()
    scene = bpy.context.scene
    count = sum(bool(re.fullmatch(r'TREE_Understory_\d{4}_Leaves',o.name)) for o in scene.objects)
    if count != 2400:
        raise ValueError('Understory population differs from the approved context')
    signatures = {}
    states = []
    errors = []
    for record in APPROVED['objects']:
        obj = scene.objects.get(record['name'])
        if obj is None or obj.type != 'MESH':
            errors.append((record['name'],'missing mesh object'))
            continue
        if _matrix_error(obj.matrix_world,record['matrix']) > 1e-6:
            errors.append((obj.name,'world matrix/root does not match approved source'))
        if obj.modifiers or obj.data.shape_keys:
            errors.append((obj.name,'unexpected modifier or shape key'))
        if obj.data.name not in signatures:
            signatures[obj.data.name] = mesh_signature(obj.data)
        if obj.data.name == record['old_mesh'] and signatures[obj.data.name] == record['old_signature']:
            states.append('source')
        elif obj.data.name == record['new_mesh'] and signatures[obj.data.name] == record['new_signature']:
            states.append('applied')
        else:
            errors.append((obj.name,'assigned data name/signature is not approved'))
    if errors:
        raise ValueError('No changes applied: '+repr(errors))
    if set(states)=={'applied'}:
        return {'status':'SKIPPED_ALREADY_APPLIED','instances':16,'target_objects':32,
                'generator_sha256':APPROVED['generator_sha256'],'mutated_properties':[]}
    if set(states)!={'source'}:
        raise ValueError('Partial previous application; no changes applied')
    for data in APPROVED['assets'].values():
        if any(bpy.data.meshes.get(name) for name in (data['new_branch_mesh'],data['new_leaf_mesh'])):
            raise ValueError('Conflicting pre-existing candidate meshes; no changes applied')
    assets = {}
    original = {r['name']:scene.objects[r['name']].data for r in APPROVED['objects']}
    new_meshes = []
    try:
        for key, data in APPROVED['assets'].items():
            old_bark=bpy.data.meshes[data['old_branch_mesh']]
            old_leaf=bpy.data.meshes[data['old_leaf_mesh']]
            bark,leaf,report=understory_detail08.make_asset(int(key),old_bark.materials[0],list(old_leaf.materials),data['removed_design_leaf_ids'])
            new_meshes.extend((bark,leaf))
            assert mesh_signature(bark)==data['new_branch_signature'],('Accepted branch reproduction mismatch',key)
            assert mesh_signature(leaf)==data['new_leaf_signature'],('Accepted leaf reproduction mismatch',key)
            assert report['leaf_count']==data['leaf_count'] and report['total_triangles']==data['total_triangles']
            assets[key]={'branches':bark,'leaves':leaf,'report':report}
        for record in APPROVED['objects']:
            scene.objects[record['name']].data=assets[str(record['asset'])][record['part']]
        bpy.context.view_layer.update()
        assert all(_matrix_error(scene.objects[r['name']].matrix_world,r['matrix'])<=1e-6 for r in APPROVED['objects'])
    except Exception:
        for name,mesh in original.items():
            scene.objects[name].data=mesh
        for mesh in new_meshes:
            if mesh.users==0:
                bpy.data.meshes.remove(mesh)
        raise
    return {'status':'APPLIED_ACCEPTED_16_SHRUB_SHAPES_VISUAL_SCOPE_ONLY','instances':16,'target_objects':32,
            'mutated_properties':['object.data'],'labels_changed':False,
            'generator_sha256':APPROVED['generator_sha256'],
            'accepted_candidate_sha256':APPROVED['accepted_candidate_sha256'],
            'assets':{key:value['report'] for key,value in assets.items()},
            'limits':'Local shape acceptance only; terrain/ecosystem still visually failed. Recheck actual terrain contacts and the current route after integration.'}
