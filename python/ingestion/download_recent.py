"""Download official DGIS resources covering a configurable start year onward; preserve original bytes."""
import argparse
import datetime, hashlib, html, json, re, urllib.request, zipfile
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.error import HTTPError
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
   evidence=ROOT/'docs/evidence'
   evidence.mkdir(parents=True,exist_ok=True)
   (evidence/f'{kind}.html').write_bytes(b)
   links=[]
   for href,label in re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',b.decode('utf-8',errors='replace'),re.S|re.I):
    if not re.search(r'\.(zip|rar|csv|xlsx?)(?:\?|$)',href,re.I):continue
    label=html.unescape(' '.join(re.sub('<[^>]+>',' ',label).split()))
    link={'url':urljoin(url,html.unescape(href).strip()),'label':label,'status':'listed_not_downloaded','source':kind}
    links.append(link)
    years=[int(y) for y in re.findall(r'(?<!\d)(?:19|20)\d{2}(?!\d)',urlparse(href).path)]
    if years and max(years)>=start_year:plan.append(link)
   if not links:raise ValueError('No downloadable resources found in DGIS inventory')
   save_json(ROOT/'config'/f'{kind}_files.json',links)
   print('INVENTORY',kind,len(links),flush=True)
  except Exception as e:errors.append({'source':kind,'error':str(e)})
 save_json(ROOT/f'reports/download_plan_{start_year}_onward.json',plan)
 for i,x in enumerate(plan,1):
  name=Path(urlparse(x['url']).path).name
  series='sectorial' if 'sectorial' in name.lower() else 'institucional' if x['source']=='egresos' else 'registros_y_metadatos'
  dest=ROOT/'data/bronze'/x['source']/series/name
  prev=byurl.get(x['url'])
  valid=prev and (ROOT/prev['path']).is_file() and digest(ROOT/prev['path'])==prev['sha256']
  headers={}
  if valid and prev.get('etag'):headers['If-None-Match']=prev['etag']
  if valid and prev.get('last_modified'):headers['If-Modified-Since']=prev['last_modified']
  dest.parent.mkdir(parents=True,exist_ok=True)
  part=None
  try:
   print('DOWNLOADING',i,len(plan),name,flush=True)
   request=urllib.request.Request(x['url'],headers=headers)
   with urllib.request.urlopen(request,timeout=120) as r, NamedTemporaryFile(dir=dest.parent,suffix='.part',delete=False) as f:
    part=Path(f.name)
    expected=r.headers.get('Content-Length');ctype=r.headers.get('Content-Type');finalurl=r.url
    etag=r.headers.get('ETag');last_modified=r.headers.get('Last-Modified')
    while chunk:=r.read(1024*1024):f.write(chunk)
   if not part.stat().st_size or (ctype and 'text/html' in ctype.lower()):raise ValueError('Empty or HTML response')
   if expected and part.stat().st_size!=int(expected):raise ValueError('Content-Length mismatch')
   if name.lower().endswith(('.zip','.xlsx')):
    with zipfile.ZipFile(part) as z:
     bad=z.testzip()
     if bad:raise ValueError('CRC failed: '+bad)
     members=[{'name':n.filename,'bytes':n.file_size} for n in z.infolist() if not n.is_dir()]
   else:members=None
   sha=digest(part)
   if valid and sha==prev['sha256']:
    prev.update(etag=etag,last_modified=last_modified)
    save_json(mp,list(byurl.values()))
    print('REUSE',name,flush=True);continue
   dest=dest.parent/sha/name
   dest.parent.mkdir(parents=True,exist_ok=True)
   part.replace(dest)
   entry=dict(x,path=dest.relative_to(ROOT).as_posix(),size_bytes=dest.stat().st_size,sha256=sha,downloaded_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),license='pending_review',validation='transport_and_archive_integrity_only',status='downloaded',content_type=ctype,resolved_url=finalurl,members=members,etag=etag,last_modified=last_modified)
   if prev:entry['previous_versions']=[*prev.get('previous_versions',[]),{k:prev.get(k) for k in ('path','sha256','downloaded_at')}]
   byurl[x['url']]=entry;save_json(mp,list(byurl.values()))
   print('OK',name,entry['size_bytes'],flush=True)
  except HTTPError as e:
   e.close()
   if e.code==304 and headers:
    print('REUSE',name,flush=True);continue
   errors.append({'url':x['url'],'error':str(e)});print('ERROR',name,str(e),flush=True)
  except Exception as e:
   errors.append({'url':x['url'],'error':str(e)});print('ERROR',name,str(e),flush=True)
  finally:
   if part is not None:part.unlink(missing_ok=True)
 report={'date':datetime.datetime.now(datetime.timezone.utc).isoformat(),'requested_start_year':start_year,'planned_resources':len(plan),'downloaded_resources':sum(x['url'] in byurl for x in plan),'total_manifest_bytes':sum(x['size_bytes'] for x in byurl.values()),'errors':errors,'note':'2026 may be partial; archive integrity is not epidemiological validation.'}
 save_json(ROOT/f'reports/DESCARGAS_{start_year}_A_FECHA.json',report);print(json.dumps(report),flush=True)
 return not errors
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--from-year',type=int,default=2020);args=parser.parse_args();raise SystemExit(not run(args.from_year))
