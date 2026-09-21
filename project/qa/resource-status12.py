import json
import psutil

v = psutil.virtual_memory()
print(json.dumps({'memory_total_gb': v.total/2**30, 'memory_available_gb':v.available/2**30, 'memory_percent':v.percent}))
for p in psutil.process_iter(['pid','name','memory_info','cpu_times','create_time']):
    if p.info['name'].lower() in ('blender.exe','powershell.exe','pwsh.exe'):
        a=p.info
        print(a['pid'], a['name'], round(a['memory_info'].rss/2**30,3), 'GiB', a['cpu_times'])
