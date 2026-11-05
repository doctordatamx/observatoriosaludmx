import io, sys, tempfile, unittest, zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'python/ingestion'))
from build_silver import record_archive
class ArchiveTests(unittest.TestCase):
 def test_nested_official_wrapper_is_read_without_extraction(self):
  payload=io.BytesIO()
  with zipfile.ZipFile(payload,'w') as z:z.writestr('records.CSV','sexo,edad\n2,4065\n')
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'wrapped.zip'
   with zipfile.ZipFile(p,'w') as z:z.writestr('official/inner.zip',payload.getvalue())
   original=p.read_bytes()
   with record_archive(p) as z:self.assertEqual(z.read('records.CSV'),b'sexo,edad\n2,4065\n')
   self.assertEqual(p.read_bytes(),original)
 def test_plain_archive_is_not_reinterpreted(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'plain.zip'
   with zipfile.ZipFile(p,'w') as z:z.writestr('D_Evento.txt','CodEstado,SEXO\n19,2\n')
   with record_archive(p) as z:self.assertEqual(z.namelist(),['D_Evento.txt'])
