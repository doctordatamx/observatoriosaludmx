import gzip,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
manifest=json.loads((ROOT/'reports/silver_manifest.json').read_text(encoding='utf-8'))
geo=json.loads((ROOT/'frontend/public/geo/index.json').read_text(encoding='utf-8'));lookup=set(geo['names'])
out=ROOT/'.runtime/municipal-cache';out.mkdir(parents=True,exist_ok=True)
for job in manifest:
 if job['source']=='sectorial':continue
 id=f"{job['source']}-{job['year']}";folder=ROOT/'frontend/public/data/municipal'/id
 info={};total=0;unmatched=0
 for p in folder.glob('*.json.gz'):
  with gzip.open(p,'rt',encoding='utf-8') as f:c=json.load(f)
  n=sum(r[5] for r in c['rows']);u=sum(r[5] for r in c['rows'] if c['municipalities'][r[6]] not in lookup)
  total+=n;unmatched+=u;state=c['states'][0]
  info[state]={'file':f'municipal/{id}/{p.name}','total':n,'unmatched_geometry':u,'cells':len(c['rows']),'municipalities':len(c['municipalities'])}
 if total!=job['records']:continue
 payload={'info':{'source':job['source'],'year':job['year'],'states':info,'total':total,'sha256':job['sha256']},'quality':{'records':job['records'],'aggregated_total':total,'unmatched_geometry':unmatched}}
 (out/(id+'.json')).write_text(json.dumps(payload,separators=(',',':')),encoding='utf-8');print('RECOVERED',id,total,flush=True)
