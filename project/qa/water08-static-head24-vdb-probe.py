"""Inspect existing failed control VDB only; no simulation or scene write."""
import json,sys
from pathlib import Path
import openvdb as vdb
ROOT=Path(__file__).resolve().parents[1]
print('VDB_VERSION',getattr(vdb,'__version__',None),flush=True)
print('READ_DOC',vdb.readAll.__doc__,flush=True)
print('METADATA_DOC',vdb.readAllGridMetadata.__doc__,flush=True)
grids=vdb.readAllGridMetadata(str(ROOT/'caches/fluid_water08/static_head24/data/fluid_data_0024.vdb'))
for g in grids:
 print('GRID',g.name,g.valueTypeName,g.background,g.evalActiveVoxelBoundingBox(),g.activeVoxelCount(),flush=True)
 print('COPY_DOC',getattr(g,'copyToArray',None).__doc__,flush=True)
