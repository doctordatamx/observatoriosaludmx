"""Verify local lineage and counts. The detailed report stays under reports/."""
import argparse
import gzip
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python" / "ingestion"))
from download_recent import digest, save_json


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def audit():
    bronze = {item["path"]: item for item in read("data/bronze/manifest.json")}
    projections = read("reports/silver_manifest.json")
    silver = {f'{item["source"]}-{item["year"]}': item for item in projections}
    index = read("frontend/public/data/index.json")
    gold = {item["id"]: item for item in index["datasets"]}
    if len(gold) != len(index["datasets"]) or len(silver) != len(projections) or set(gold) != set(silver):
        raise ValueError("Los inventarios Silver y Gold deben coincidir y tener identificadores únicos.")
    results = []
    for key, projection in silver.items():
        dataset = gold[key]
        original = ROOT / projection["original"]
        entry = bronze[projection["original"]]
        problems = []
        sha = digest(original)
        if not (sha == entry["sha256"] == projection["sha256"] == dataset["sha256"]):
            problems.append("SHA-256 divergente")
        if original.stat().st_size != entry["size_bytes"]:
            problems.append("Tamaño original divergente")
        official = urlsplit(entry["url"].strip()).hostname in {"www.dgis.salud.gob.mx", "dgis.salud.gob.mx"}
        if not official or entry["url"].strip() != projection["url"].strip() or entry["url"].strip() != dataset["url"].strip():
            problems.append("URL DGIS no trazable")
        parquet = pq.ParquetFile(ROOT / projection["silver_parquet"])
        fields = dict(zip(parquet.schema_arrow.names, map(str, parquet.schema_arrow.types)))
        mapping = projection.get("column_mapping")
        expected_fields = mapping.values() if mapping else projection["columns"]
        if set(fields) != set(expected_fields) or set(fields.values()) != {"string"}:
            problems.append("Esquema Silver divergente")
        with gzip.open(ROOT / "frontend/public/data" / dataset["file"], "rt", encoding="utf-8") as stream:
            cube = json.load(stream)
        months = sorted({row[3] for row in cube["rows"] if row[3]})
        if months != sorted(dataset["months"]):
            problems.append("Meses observados divergentes")
        total = sum(row[5] for row in cube["rows"])
        if not (total == dataset["total"] == projection["records"] == parquet.metadata.num_rows):
            problems.append("Conteos Silver y Gold divergentes")
        if dataset["year"] == 2026 and not (dataset["partial"] and dataset["cutoffs"]):
            problems.append("Falta indicar el corte parcial de 2026")
        results.append(dict(id=key, url=entry["url"].strip(), sha256=sha,
                            downloaded_at=entry.get("downloaded_at"), bytes=original.stat().st_size,
                            records=total, fields=fields, months=months, states=sorted(cube["states"]),
                            partial=dataset["partial"], cutoffs=dataset["cutoffs"], quality=dataset["quality"],
                            issues=problems))
        print(key, total, "; ".join(problems) or "OK", flush=True)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "reports/AUDITORIA_PIPELINE.json")
    results = audit()
    save_json(parser.parse_args().output, results)
    raise SystemExit(int(any(item["issues"] for item in results)))
