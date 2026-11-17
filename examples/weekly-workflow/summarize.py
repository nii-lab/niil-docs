import csv,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((root/'raw/measurements.csv').open()))
result={}
for key in ('A','B'):
 values=[float(r['latency_ms']) for r in rows if r['config']==key and r['latency_ms']]
 result[key]={'mean_latency_ms':sum(values)/len(values)}
(root/'results/summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
