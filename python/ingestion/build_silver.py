"""Engineering projection: preserve selected original fields and stream ZIP -> Silver.
All clinical/statistical transformations are performed by R/build_gold.R.
"""
import csv, hashlib, io, json, re, zipfile
from contextlib import contextmanager, ExitStack
from pathlib import Path
import pyarrow as pa
import pyarrow.csv as pc
import pyarrow.parquet as pq
ROOT=Path(__file__).resolve().parents[2]

@contextmanager
def record_archive(path):
 """Unwrap official one-ZIP wrappers, retaining every original archive."""
 with ExitStack() as stack:
  z=stack.enter_context(zipfile.ZipFile(path))
  for depth in range(4):
   payload=[n for n in z.namelist() if not n.endswith('/')]
   nested=[n for n in payload if n.lower().endswith('.zip')]
   if len(payload)!=1 or len(nested)!=1:break
   z=stack.enter_context(zipfile.ZipFile(io.BytesIO(z.read(nested[0]))))
   if z.testzip() is not None:raise ValueError('Nested archive CRC failed')
  yield z


def jobs():
 manifest=json.loads((ROOT/'data/bronze/manifest.json').read_text(encoding='utf-8'))
 for item in manifest:
  path=Path(item['path']);name=path.name.lower()
  if not name.endswith('.zip') or any(s in name for s in ['catalog','descriptor']):continue
  year=int(re.findall(r'20\d{2}',name)[-1])
  source=item.get('source','defunciones')
  if source=='egresos' and 'sectorial' in name:source='sectorial'
  if source=='defunciones':
   cols=['ent_resid','mun_resid','sexo','edad','causa_def','mes_regis','anio_regis','anio_ocur','mes_ocurr'];marker='conjunto_de_datos_defunciones'
  elif source=='egresos':cols=['ENTIDAD','MUNIC','SEXO','EDAD','CVEEDAD','AFECPRIN','MES_ESTADISTICO'];marker='egresos'
  elif source=='urgencias':cols=['ENTRESIDENCIA','MUNRESIDENCIA','SEXO','EDAD','CVEEDAD','AFECPRIN','MES_ESTADISTICO'];marker='urgencias'
  elif source=='lesiones':cols=['CodEstado','CodMunicipio','SEXO','Edad','CVEEDAD','AFECPRIN','MES_ESTADISTICO'];marker='d_evento'
  elif source=='sectorial':cols=['CEDOCVE','SEXO','EDAD1','CLAVE_EDAD','AFECPRIN4','MES'];marker='egresos_sectorial'
  else:continue
  yield dict(source=source,year=year,original=item['path'],sha256=item['sha256'],columns=cols,marker=marker,url=item['url'])

def main():
 plans=[]
 for job in jobs():
  dest=ROOT/'data/silver'/job['source']/str(job['year']);dest.mkdir(parents=True,exist_ok=True)
  csvpath=dest/'selected.csv';pqpath=dest/'selected.parquet';metapath=dest/'projection.json'
  if metapath.exists():
   old=json.loads(metapath.read_text())
   if old['sha256']==job['sha256'] and set(job['columns']).issubset(old['columns']) and csvpath.exists() and pqpath.exists():plans.append(old);print('REUSE',job['source'],job['year'],flush=True);continue
  with record_archive(ROOT/job['original']) as z:
   # Select by required schema, not historic archive/member naming conventions.
   candidates=[]
   for member_name in z.namelist():
    if not member_name.lower().endswith(('.csv','.txt')):continue
    with z.open(member_name) as f:raw_header=f.readline()
    delimiter='|' if b'|' in raw_header else ','
    header=next(csv.reader(io.StringIO(raw_header.decode('utf-8-sig')),delimiter=delimiter))
    lookup={h.strip().lower():h for h in header}
    if all(c.lower() in lookup for c in job['columns']):candidates.append((member_name,header,lookup,delimiter))
   if len(candidates)!=1:raise ValueError(f"Expected one principal table: {job['source']} {job['year']}; found {len(candidates)}")
   member,head,lookup,delimiter=candidates[0]
   canonical=job['columns']+(['Fecha_Corte'] if 'fecha_corte' in lookup else [])
   cols=[lookup[c.lower()] for c in canonical]
   job['column_mapping']=dict(zip(cols,canonical));job['delimiter']=delimiter
   trailers=[]
   def handle_invalid(row):
    match=re.fullmatch(r'\((\d+) row\(s\) affected\)',row.text.strip())
    if match:
     trailers.append({'text':row.text,'declared_records':int(match.group(1))});return 'skip'
    return 'error'
   with z.open(member) as f:
    reader=pc.open_csv(f,read_options=pc.ReadOptions(block_size=8*1024*1024,encoding='utf8'),parse_options=pc.ParseOptions(delimiter=delimiter,invalid_row_handler=handle_invalid),convert_options=pc.ConvertOptions(include_columns=cols,column_types={c:pa.string() for c in cols},strings_can_be_null=False))
    out_schema=pa.schema([(c,pa.string()) for c in canonical])
    writer=pq.ParquetWriter(pqpath,out_schema,compression='zstd');cw=pc.CSVWriter(csvpath,out_schema);n=0;cutoffs=set()
    try:
     for batch in reader:
      batch=batch.rename_columns(canonical)
      writer.write_batch(batch);cw.write_batch(batch);n+=batch.num_rows
      if 'Fecha_Corte' in canonical:cutoffs.update(batch.column(canonical.index('Fecha_Corte')).unique().to_pylist())
    finally:writer.close();cw.close()
  if trailers and (len(trailers)!=1 or trailers[0]['declared_records']!=n):raise ValueError(f'Export trailer count mismatch: {trailers}, read {n}')
  job.update(non_record_trailers=trailers,records=n,member=member,silver_csv=csvpath.relative_to(ROOT).as_posix(),silver_parquet=pqpath.relative_to(ROOT).as_posix(),cutoffs=sorted(cutoffs),schema_status='projection_preserves_original_strings')
  metapath.write_text(json.dumps(job,ensure_ascii=False,indent=2),encoding='utf-8');plans.append(job)
  print('SILVER',job['source'],job['year'],n,job['cutoffs'],flush=True)
 (ROOT/'reports/silver_manifest.json').write_text(json.dumps(plans,ensure_ascii=False,indent=2),encoding='utf-8')
 extract_catalogues()

def extract_catalogues():
 labels={};states={};age_catalogue={}
 for folder in ['egresos','defunciones']:
  candidates=[p for p in (ROOT/'data/bronze'/folder).rglob('*.zip') if 'catalog' in p.name.lower() and (folder!='egresos' or p.name.lower().startswith('ssa_'))]
  p=max(candidates,key=lambda p:max(map(int,re.findall(r'20\d{2}',p.name))))
  with zipfile.ZipFile(p) as z:
   for n in z.namelist():
    if not n.lower().endswith('.csv'):continue
    if not any(s in n.lower() for s in ['cat_cie_10','catentidadres','catalogos/edad.csv']):continue
    raw=z.read(n)
    try:text=raw.decode('utf-8-sig')
    except UnicodeDecodeError:text=raw.decode('cp1252')
    rows=list(csv.reader(io.StringIO(text),delimiter='|' if '|' in text.splitlines()[0] else ','))
    for row in rows[1:]:
     if len(row)<2:continue
     if 'cat_cie_10' in n.lower():
      key=row[2].strip();label=row[3].strip()
     else:key=row[0].strip();label=row[1].strip()
     if 'catentidadres' in n.lower():states[key]=label
     elif n.lower().endswith('/edad.csv'):age_catalogue[key]=label
     elif len(key)==3 and re.fullmatch('[A-Z][0-9]{2}',key):labels[key]=label
 ages_by_year={}
 for p in (ROOT/'data/bronze/defunciones').rglob('*.zip'):
  if 'catalog' not in p.name.lower():continue
  year=re.findall(r'20\d{2}',p.name)[-1]
  with record_archive(p) as z:
   for n in z.namelist():
    if n.lower().endswith('/edad.csv') or n.lower()=='edad.csv':
     raw=z.read(n)
     try:text=raw.decode('utf-8-sig')
     except UnicodeDecodeError:text=raw.decode('cp1252')
     rows=list(csv.reader(io.StringIO(text),delimiter=',' if ',' in text.splitlines()[0] else '|'))
     ages_by_year[year]={r[0].strip():r[1].strip() for r in rows[1:] if len(r)>1}
 (ROOT/'config/catalogue_labels.json').write_text(json.dumps(dict(causes=labels,states=states,death_ages=age_catalogue,death_ages_by_year=ages_by_year),ensure_ascii=False),encoding='utf-8')
if __name__=='__main__':main()
