"""INEGI geometry snapshot, raw provenance, CRS transformation and display-only simplification."""
import sys,json,hashlib,datetime,gzip,time,urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'.runtime/python'))
from pyproj import Transformer
import shapely
from shapely.geometry import shape,mapping
from shapely.ops import transform
SNAPSHOT='2026-11-04'
BASE='https://gaia.inegi.org.mx/wscatgeo/v2/geo/'
OUT=ROOT/'frontend/public/geo';OUT.mkdir(parents=True,exist_ok=True)
RAW=ROOT/'data/bronze/inegi'/SNAPSHOT;RAW.mkdir(parents=True,exist_ok=True)

def fetch(key):
 file_stem='states' if key=='states' else f'municipalities-{key}'
 url=BASE+('mgee/' if key=='states' else f'mgem/{key}')
 p=RAW/(file_stem+'.json')
 if not p.exists():
  for attempt in range(3):
   try:
    with urllib.request.urlopen(url,timeout=120) as r:b=r.read()
    x=json.loads(b)
    assert x.get('type')=='FeatureCollection' and x.get('features'),'Not a geometry collection'
    temp=p.with_suffix('.part');temp.write_bytes(b);temp.replace(p);break
   except Exception:
    if attempt==2:raise
    time.sleep(2)
 b=p.read_bytes();x=json.loads(b);features=x['features'];ids=[str(f['properties']['cvegeo']) for f in features]
 assert len(ids)==len(set(ids))
 assert all(len(i)==(2 if key=='states' else 5) and (key=='states' or i[:2]==key) for i in ids)
 original=[shape(f['geometry']) for f in features]
 assert all(g.is_valid and not g.is_empty for g in original),'Invalid original geometry; manual review required'
 crs={f['geometry'].get('crs',{}).get('properties',{}).get('name') for f in features}
 assert crs=={'EPSG:6365'},str(crs)
 tx=Transformer.from_crs('EPSG:6365','EPSG:4326',always_xy=True)
 transformed=[transform(tx.transform,g) for g in original]
 try:
  simple=list(shapely.coverage_simplify(transformed,0.0015));method='coverage_simplify'
  assert all(g.is_valid and not g.is_empty for g in simple)
 except Exception:
  simple=[g.simplify(0.0015,preserve_topology=True) for g in transformed];method='simplify_preserve_topology_per_feature'
 result=[];names={}
 for feature,g in zip(features,simple):
  props=feature['properties'];code=str(props['cvegeo']);name=props['nomgeo'];names[code]=name
  result.append({'type':'Feature','properties':{'name':code,'cvegeo':code,'nomgeo':name},'geometry':mapping(g)})
 data={'type':'FeatureCollection','features':result}
 payload=json.dumps(data,ensure_ascii=False,separators=(',',':')).encode('utf-8')
 with gzip.open(OUT/(file_stem+'.json.gz'),'wb',compresslevel=6) as f:f.write(payload)
 meta={'key':key,'url':url,'snapshot':SNAPSHOT,'source_metadata':x.get('metadatos'),'source_crs':'EPSG:6365','web_crs':'EPSG:4326','transformation':tx.description,'simplification':{'method':method,'tolerance_degrees':0.0015,'purpose':'display_only_not_spatial_inference'},'features':len(result),'raw_path':p.relative_to(ROOT).as_posix(),'raw_bytes':len(b),'raw_sha256':hashlib.sha256(b).hexdigest(),'web_sha256':hashlib.sha256(payload).hexdigest(),'names':names}
 print('GEOMETRY',key,len(result),len(payload),flush=True)
 return meta

def main():
 records=[];errors=[]
 with ThreadPoolExecutor(max_workers=4) as pool:
  pending={pool.submit(fetch,key):key for key in ['states']+[f'{i:02}' for i in range(1,33)]}
  for future in as_completed(pending):
   key=pending[future]
   try:records.append(future.result())
   except Exception as e:errors.append({'key':key,'error':str(e)});print('ERROR',key,str(e),flush=True)
 manifest={'snapshot':SNAPSHOT,'geographic_vintage':'INEGI Marco Geoestadístico diciembre 2025','historical_crosswalk':'not_applied','source_documentation':'https://www.inegi.org.mx/servicios/catalogounico/','records':sorted(records,key=lambda r:r['key']),'errors':errors}
 (ROOT/'reports/GEOMETRY_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
 names={k:v for r in records if r['key']!='states' for k,v in r['names'].items()}
 public={'snapshot':SNAPSHOT,'vintage':manifest['geographic_vintage'],'names':names,'states':next((r['names'] for r in records if r['key']=='states'),{}),'available_states':[r['key'] for r in records if r['key']!='states'],'historical_warning':'Límites de diciembre 2025; no se han homologado retrospectivamente municipios nuevos o modificados.','source':manifest['source_documentation']}
 (OUT/'index.json').write_text(json.dumps(public,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 if errors:raise RuntimeError(str(errors))
if __name__=='__main__':main()
