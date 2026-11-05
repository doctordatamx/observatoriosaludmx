import gzip,json,unittest
from pathlib import Path
from collections import Counter
import duckdb
import shapely
from shapely.geometry import shape
ROOT=Path(__file__).resolve().parents[1]
def gz(path):
 with gzip.open(path,'rt',encoding='utf-8') as f:return json.load(f)
class SpatialTests(unittest.TestCase):
 def test_official_geometry_snapshot(self):
  meta=json.loads((ROOT/'reports/GEOMETRY_MANIFEST.json').read_text(encoding='utf-8'))
  self.assertEqual(len(meta['records']),33);self.assertFalse(meta['errors'])
  keys=set()
  for r in meta['records']:
   p=ROOT/'frontend/public/geo'/('states.json.gz' if r['key']=='states' else f"municipalities-{r['key']}.json.gz")
   c=gz(p);self.assertEqual(len(c['features']),r['features'])
   for f in c['features']:
    code=f['properties']['cvegeo'];g=shape(f['geometry']);self.assertTrue(g.is_valid and not g.is_empty)
    xmin,ymin,xmax,ymax=g.bounds;self.assertTrue(-120<xmin<xmax<-85 and 13<ymin<ymax<34)
    if r['key']!='states':self.assertEqual(code[:2],r['key']);self.assertNotIn(code,keys);keys.add(code)
  self.assertEqual(len(keys),2478)
 def test_municipal_cubes_preserve_totals(self):
  index=json.loads((ROOT/'frontend/public/data/municipal-index.json').read_text(encoding='utf-8'))
  self.assertEqual(len(index['datasets']),26)
  for id,d in index['datasets'].items():
   with self.subTest(dataset=id):
    total=0
    for st,part in d['states'].items():
     c=gz(ROOT/'frontend/public/data'/part['file']);n=sum(r[5] for r in c['rows'])
     self.assertEqual(n,part['total']);self.assertEqual(c['states'],[st]);total+=n
     self.assertTrue(all(len(r)==7 and r[5]>0 and 0<=r[6]<len(c['municipalities']) for r in c['rows']))
    self.assertEqual(total,d['total'])
 def test_rollup_matches_existing_mortality_cube(self):
  index=json.loads((ROOT/'frontend/public/data/municipal-index.json').read_text(encoding='utf-8'))
  aggregate=Counter()
  for st,part in index['datasets']['defunciones-2024']['states'].items():
   c=gz(ROOT/'frontend/public/data'/part['file'])
   for r in c['rows']:aggregate[(st,r[1],r[2],r[3],c['causes'][r[4]])]+=r[5]
  old=gz(ROOT/'frontend/public/data/defunciones-2024.json.gz')
  expected={(old['states'][r[0]],r[1],r[2],r[3],old['causes'][r[4]]):r[5] for r in old['rows']}
  self.assertEqual(dict(aggregate),expected)
 def test_monterrey_filtered_query_matches_raw_silver(self):
  index=json.loads((ROOT/'frontend/public/data/municipal-index.json').read_text(encoding='utf-8'));con=duckdb.connect()
  for source,st,mu,sex,age,unit in [('defunciones','ent_resid','mun_resid','sexo','edad',None),('egresos','ENTIDAD','MUNIC','SEXO','EDAD','CVEEDAD'),('urgencias','ENTRESIDENCIA','MUNRESIDENCIA','SEXO','EDAD','CVEEDAD'),('lesiones','CodEstado','CodMunicipio','SEXO','Edad','CVEEDAD')]:
   with self.subTest(source=source):
    clause=f"try_cast({age} as integer) between {4065 if unit is None else 65} and {4069 if unit is None else 69}"
    if unit:clause+=f" and try_cast({unit} as integer)=5"
    expected=con.execute(f"select count(*) from read_parquet(?) where try_cast({st} as integer)=19 and try_cast({mu} as integer)=39 and try_cast({sex} as integer)=2 and {clause}",[str(ROOT/f'data/silver/{source}/2024/selected.parquet')]).fetchone()[0]
    c=gz(ROOT/'frontend/public/data'/index['datasets'][source+'-2024']['states']['19']['file'])
    actual=sum(r[5] for r in c['rows'] if c['municipalities'][r[6]]=='19039' and r[1]==2 and r[2]==14)
    self.assertEqual(actual,expected)
 def test_source_catalogue_gate(self):
  c=json.loads((ROOT/'frontend/public/geo/health-catalogues.json').read_text(encoding='utf-8'))
  geo=json.loads((ROOT/'frontend/public/geo/index.json').read_text(encoding='utf-8'))
  self.assertEqual(len(c['eligible']),26)
  for id,keys in c['eligible'].items():
   self.assertGreater(len(keys),2000);self.assertTrue(set(keys).issubset(geo['names']));self.assertIn('19039',keys)

if __name__=='__main__':unittest.main()
