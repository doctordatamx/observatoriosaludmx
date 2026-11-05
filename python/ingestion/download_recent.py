"""Download official DGIS resources covering a configurable start year onward; preserve original bytes."""
import argparse
import datetime, hashlib, html, json, re, urllib.request, zipfile
from pathlib import Path
from urllib.parse import urljoin, urlparse
ROOT=Path(__file__).resolve().parents[2]
PAGES={'defunciones':'da_defunciones_gobmx.html','egresos':'da_egresoshosp_gobmx.html','urgencias':'da_urgencias_gobmx.html','lesiones':'da_lesiones_gobmx.html'}
def save_json(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True)
 temp=path.with_suffix('.tmp');temp.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8');temp.replace(path)
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  while b:=f.read(1024*1024):h.update(b)
 return h.hexdigest()
def run(start_year=2020):
 mp=ROOT/'data/bronze/manifest.json'
 manifest=json.loads(mp.read_text(encoding='utf-8')) if mp.exists() else []
 byurl={x['url']:x for x in manifest};plan=[];errors=[]
 for kind,slug in PAGES.items():
  url='http://www.dgis.salud.gob.mx/contenidos/basesdedatos/'+slug
  try:
   with urllib.request.urlopen(url,timeout=60) as r:b=r.read()
   (ROOT/'docs/evidence'/f'{kind}.html').write_bytes(b)
   links=[]
   for href,label in re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',b.decode('utf-8',errors='replace'),re.S|re.I):
    if not re.search(r'\.(zip|rar|csv|xlsx?)(?:\?|$)',href,re.I):continue
    label=html.unescape(' '.join(re.sub('<[^>]+>',' ',label).split()))
    link={'url':urljoin(url,href),'label':label,'status':'listed_not_downloaded','source':kind}
    links.append(link)
    years=[int(y) for y in re.findall(r'(?<!\d)(?:19|20)\d{2}(?!\d)',urlparse(href).path)]
    if years and max(years)>=start_year:plan.append(link)
   save_json(ROOT/'config'/f'{kind}_files.json',links)
   print('INVENTORY',kind,len(links),flush=True)
  except Exception as e:errors.append({'source':kind,'error':str(e)})
 save_json(ROOT/f'reports/download_plan_{start_year}_onward.json',plan)
 for i,x in enumerate(plan,1):
  name=Path(urlparse(x['url']).path).name
  series='sectorial' if 'sectorial' in name.lower() else 'institucional' if x['source']=='egresos' else 'registros_y_metadatos'
  dest=ROOT/'data/bronze'/x['source']/series/name
  prev=byurl.get(x['url'])
  if prev and (ROOT/prev['path']).exists() and digest(ROOT/prev['path'])==prev['sha256']:
   prev['status']='downloaded';print('REUSE',name,flush=True);continue
  dest.parent.mkdir(parents=True,exist_ok=True)
  part=dest.with_suffix(dest.suffix+'.part')
  try:
   print('DOWNLOADING',i,len(plan),name,flush=True)
   with urllib.request.urlopen(x['url'],timeout=120) as r,part.open('wb') as f:
    expected=r.headers.get('Content-Length');ctype=r.headers.get('Content-Type');finalurl=r.url
    while chunk:=r.read(1024*1024):f.write(chunk)
   if expected and part.stat().st_size!=int(expected):raise ValueError('Content-Length mismatch')
   if name.lower().endswith(('.zip','.xlsx')):
    with zipfile.ZipFile(part) as z:
     bad=z.testzip()
     if bad:raise ValueError('CRC failed: '+bad)
     members=[{'name':n.filename,'bytes':n.file_size} for n in z.infolist() if not n.is_dir()]
   else:members=None
   part.replace(dest)
   entry=dict(x,path=dest.relative_to(ROOT).as_posix(),size_bytes=dest.stat().st_size,sha256=digest(dest),downloaded_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),license='pending_review',validation='transport_and_archive_integrity_only',status='downloaded',content_type=ctype,resolved_url=finalurl,members=members)
   byurl[x['url']]=entry;save_json(mp,list(byurl.values()))
   print('OK',name,entry['size_bytes'],flush=True)
  except Exception as e:
   errors.append({'url':x['url'],'error':str(e)});print('ERROR',name,str(e),flush=True)
 report={'date':'2026-11-04','requested_start_year':start_year,'planned_resources':len(plan),'downloaded_resources':sum(x['url'] in byurl for x in plan),'total_manifest_bytes':sum(x['size_bytes'] for x in byurl.values()),'errors':errors,'note':'2026 may be partial; archive integrity is not epidemiological validation.'}
 save_json(ROOT/f'reports/DESCARGAS_{start_year}_A_FECHA.json',report);print(json.dumps(report),flush=True)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--from-year',type=int,default=2020);args=parser.parse_args();run(args.from_year)
