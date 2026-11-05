"""Audit each projected municipal code against its source catalogue and the geometry snapshot."""
import sys,re,csv,io,json,hashlib
from pathlib import Path
import duckdb
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'python/ingestion'))
from build_silver import record_archive

def main():
 geo=json.loads((ROOT/'frontend/public/geo/index.json').read_text(encoding='utf-8'));geometry=set(geo['names'])
 jobs=json.loads((ROOT/'reports/silver_manifest.json').read_text(encoding='utf-8'))
 outputs={};eligible={};con=duckdb.connect()
 for job in jobs:
  k=job['source'];year=job['year']
  if k=='sectorial':continue
  paths=[p for p in (ROOT/'data/bronze'/k).rglob('*.zip') if 'catalog' in p.name.lower() and 'sectorial' not in p.name.lower()]
  if k=='defunciones':path=next(p for p in paths if str(year) in p.name)
  else:path=next(p for p in paths if ('2023_2025' in p.name if year>=2023 else str(year) in p.name))
  with record_archive(path) as z:
   n=next(n for n in z.namelist() if ('entidad_municipio_localidad' in n.lower() if k=='defunciones' else 'mpores' in n.lower() if k in ['egresos','urgencias'] else 'cmunicipios' in n.lower()))
   raw=z.read(n)
   try:t=raw.decode('utf-8-sig')
   except UnicodeDecodeError:t=raw.decode('cp1252')
   rows=[{key.strip().lower():value for key,value in r.items()} for r in csv.DictReader(io.StringIO(t),delimiter='|' if '|' in t.splitlines()[0] else ',')]
   keys=set()
   for r in rows:
    values=list(r.values())
    if k=='defunciones':
     c=r.get('cvegeo','').strip()
     if len(c)==5 and c.isdigit():keys.add(c)
     elif r.get('cve_loc','').strip()=='0000':
      st=r.get('cve_ent','').strip();mu=r.get('cve_mun','').strip()
      if st.isdigit() and mu.isdigit():keys.add(st.zfill(2)+mu.zfill(3))
    else:
     if len(values)>=2:
      st=values[0].strip();mu=values[1].strip()
      if st.isdigit() and mu.isdigit():keys.add(st.zfill(2)+mu.zfill(3))
  assert len(keys)>2000,f'Incomplete municipal catalogue: {path}, {len(keys)} keys'
  statecol,mucol={'defunciones':('ent_resid','mun_resid'),'egresos':('ENTIDAD','MUNIC'),'urgencias':('ENTRESIDENCIA','MUNRESIDENCIA'),'lesiones':('CodEstado','CodMunicipio')}[k]
  counts=con.execute(f"select {statecol}, {mucol}, count(*) from read_parquet(?) group by 1,2",[str(ROOT/job['silver_parquet'])]).fetchall()
  summaries={'total':job['records'],'catalogue_unknown_records':0,'geometry_unmatched_records':0,'eligible_records':0};unmatched=[]
  for st,mu,count in counts:
   code=(str(st).zfill(2)+str(mu).strip().zfill(3)) if str(st).isdigit() and str(mu).strip().isdigit() else str(st)+'???'
   source_ok=code in keys;geo_ok=code in geometry
   if not source_ok:summaries['catalogue_unknown_records']+=count
   if not geo_ok:summaries['geometry_unmatched_records']+=count
   if source_ok and geo_ok:summaries['eligible_records']+=count
   else:unmatched.append({'code':code,'records':count,'in_source_catalogue':source_ok,'in_geometry':geo_ok})
  id=f'{k}-{year}'
  eligible[id]=sorted(keys&geometry)
  outputs[id]={'catalogue':path.relative_to(ROOT).as_posix(),'catalogue_member':n,'catalogue_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'year':year,'applicability':'shared_2023_2025_pending_2026_review' if year==2026 else 'year_or_declared_period','summary':summaries,'unmatched':sorted(unmatched,key=lambda r:-r['records'])}
  print('MUNICIPAL CATALOGUE',id,summaries,flush=True)
 (ROOT/'reports/MUNICIPAL_CATALOGUE_AUDIT.json').write_text(json.dumps(outputs,ensure_ascii=False,indent=2),encoding='utf-8')
 (ROOT/'frontend/public/geo/health-catalogues.json').write_text(json.dumps({'eligible':eligible,'rule':'exact code in source-period catalogue and geometry; no historic spatial reallocation'},separators=(',',':')),encoding='utf-8')
if __name__=='__main__':main()
