"""Conservation and an independent raw-source query, using real local data."""
import gzip, json, unittest
from pathlib import Path
import duckdb
ROOT=Path(__file__).resolve().parents[1]
class GoldTests(unittest.TestCase):
 def test_every_cube_preserves_count(self):
  index=json.loads((ROOT/'frontend/public/data/index.json').read_text(encoding='utf-8'))
  silver=json.loads((ROOT/'reports/silver_manifest.json').read_text(encoding='utf-8'))
  self.assertEqual(len(index['datasets']),len(silver))
  for source in ['defunciones','egresos','urgencias','lesiones','sectorial']:
   self.assertTrue(set(range(2020,2025)).issubset({d['year'] for d in index['datasets'] if d['source']==source}))
  for d in index['datasets']:
   with self.subTest(dataset=d['id']):
    with gzip.open(ROOT/'frontend/public/data'/d['file'],'rt',encoding='utf-8') as f:c=json.load(f)
    self.assertEqual(sum(r[5] for r in c['rows']),d['total'])
    self.assertTrue(all(len(r)==6 and r[5]>0 for r in c['rows']))
    self.assertTrue(all(0<=r[0]<len(c['states']) and 0<=r[4]<len(c['causes']) and 0<=r[2]<=19 and 0<=r[3]<=12 for r in c['rows']))
 def test_2020_age_sex_territory_against_sql(self):
  con=duckdb.connect()
  specs={'defunciones':('ent_resid','sexo','edad',None),'egresos':('ENTIDAD','SEXO','EDAD','CVEEDAD'),'urgencias':('ENTRESIDENCIA','SEXO','EDAD','CVEEDAD'),'lesiones':('CodEstado','SEXO','Edad','CVEEDAD'),'sectorial':('CEDOCVE','SEXO','EDAD1','CLAVE_EDAD')}
  for source,(state,sex,age,unit) in specs.items():
   with self.subTest(source=source):
    age_clause=f"try_cast({age} as integer) between {4065 if source=='defunciones' else 65} and {4069 if source=='defunciones' else 69}"
    if unit:age_clause+=f" and try_cast({unit} as integer)=5"
    expected=con.execute(f"select count(*) from read_parquet(?) where try_cast({sex} as integer)=2 and try_cast({state} as integer)=19 and {age_clause}",[str(ROOT/f'data/silver/{source}/2020/selected.parquet')]).fetchone()[0]
    with gzip.open(ROOT/f'frontend/public/data/{source}-2020.json.gz','rt',encoding='utf-8') as f:c=json.load(f)
    actual=sum(r[5] for r in c['rows'] if c['states'][r[0]]=='19' and r[1]==2 and r[2]==14)
    self.assertEqual(actual,expected)
 def test_filtered_mortality_matches_original_projection(self):
  # Independent SQL bypasses R normalization and grouping implementation.
  con=duckdb.connect()
  raw=ROOT/'data/silver/defunciones/2024/selected.parquet'
  expected=con.execute("select count(*) from read_parquet(?) where sexo='2' and ent_resid='19' and edad between '4065' and '4069' and substr(causa_def,1,3)='E11'",[str(raw)]).fetchone()[0]
  with gzip.open(ROOT/'frontend/public/data/defunciones-2024.json.gz','rt',encoding='utf-8') as f:c=json.load(f)
  actual=sum(r[5] for r in c['rows'] if c['states'][r[0]]=='19' and r[1]==2 and r[2]==14 and c['causes'][r[4]]=='E11')
  self.assertGreater(expected,0)
  self.assertEqual(actual,expected)
if __name__=='__main__':unittest.main()
