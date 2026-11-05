"""Collapse state cubes for R models; use unsimplified INEGI state polygons."""
import csv,gzip,json,re
from pathlib import Path
from collections import Counter
from shapely.geometry import shape
ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'frontend/public/data'
OUT=ROOT/'data/silver/lab'
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 meta=json.loads((DATA/'index.json').read_text(encoding='utf-8'))
 for d in meta['datasets']:
  if d['partial']:continue
  with gzip.open(DATA/d['file'],'rt',encoding='utf-8') as f:c=json.load(f)
  counts=Counter()
  for st,sex,age,month,ca,n in c['rows']:
   counts[c['states'][st],month,c['causes'][ca]]+=n
  assert sum(counts.values())==d['total'],d['id']
  with (OUT/(d['id']+'.csv')).open('w',encoding='utf-8',newline='') as f:
   w=csv.writer(f);w.writerow(['state','month','cause','n'])
   w.writerows((*key,n) for key,n in counts.items())
  print(d['id'],len(counts),flush=True)
 geo=json.loads((ROOT/'reports/GEOMETRY_MANIFEST.json').read_text(encoding='utf-8'))
 raw=next(r for r in geo['records'] if r['key']=='states')
 features=json.loads((ROOT/raw['raw_path']).read_bytes())['features']
 polygons={f['properties']['cvegeo']:shape(f['geometry']) for f in features}
 assert len(polygons)==32 and all(g.is_valid for g in polygons.values())
 edges=[]
 for i,a in enumerate(sorted(polygons)):
  for b in sorted(polygons)[i+1:]:
   shared=polygons[a].boundary.intersection(polygons[b].boundary)
   if not shared.is_empty:edges.append([a,b,shared.length>0])
 assert len(edges)>32
 (OUT/'neighbors.json').write_text(json.dumps(dict(edges=edges,raw_sha256=raw['raw_sha256'],vintage=geo['geographic_vintage']),ensure_ascii=False),encoding='utf-8')
if __name__=='__main__':main()
