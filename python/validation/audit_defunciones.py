"""Audit DGIS 2024 in streaming; never write individual records to public outputs."""
from pathlib import Path
import csv, io, json, zipfile, hashlib
from collections import Counter
ROOT = Path(__file__).resolve().parents[2]

def audit():
    folder = ROOT / "data/bronze/defunciones/2024"
    with zipfile.ZipFile(folder / "DESCRIPTOR_CAMPOS_DEFUN_2024.zip") as z:
        raw = z.read(z.namelist()[0])
        # Descriptor is double-encoded in the official archive: reversible text repair only.
        text = raw.decode("utf-8-sig")
        try: text = text.encode("cp1252").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError): pass
        descriptors = list(csv.DictReader(io.StringIO(text)))
        expected = [list(r.values())[3].strip() for r in descriptors]
    counts = {k: Counter() for k in ["anio_regis", "anio_ocur", "sexo", "ent_resid"]}
    empty = Counter(); malformed = 0; n = 0
    with zipfile.ZipFile(folder / "DEFUN_2024.zip") as z:
        if z.testzip() is not None: raise ValueError("CRC failed")
        name = next(n for n in z.namelist() if n.endswith(".csv"))
        size = z.getinfo(name).file_size
        with z.open(name) as f:
            reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig", newline=""))
            fields = reader.fieldnames
            for row in reader:
                n += 1
                if None in row or any(v is None for v in row.values()): malformed += 1
                for key in counts: counts[key][row.get(key)] += 1
                for key, value in row.items():
                    if value is None or not value.strip(): empty[key] += 1
    with zipfile.ZipFile(folder / "CATALOGOS_DEFUN_2024.zip") as z:
        if z.testzip() is not None: raise ValueError("Catalogue CRC failed")
        catalogues = [x.filename for x in z.infolist() if not x.is_dir()]
    result = dict(source="DGIS DEFUN_2024.zip", unit="registro individual de defunción registrada", records=n,
                  fields=len(fields), field_names=fields, uncompressed_csv_bytes=size, malformed_rows=malformed,
                  descriptor_fields=len(expected), missing_from_data=sorted(set(expected)-set(fields)),
                  missing_from_descriptor=sorted(set(fields)-set(expected)),
                  distributions={k:dict(sorted(v.items())) for k,v in counts.items()},
                  empty_fields=dict(empty), catalogue_count=len(catalogues), catalogues=catalogues,
                  validation="structural_only", external_total_reconciliation="pending", publication="blocked_pending_methodology_license_privacy")
    out = ROOT / "reports/DEFUNCIONES_2024_AUDIT.json"
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({k:result[k] for k in ["records","fields","malformed_rows","descriptor_fields","missing_from_data","missing_from_descriptor","catalogue_count"]}))
    return result

if __name__ == "__main__": audit()
