"""Validate relative assets and prevent accidental data publication."""
from html.parser import HTMLParser
import gzip
import hashlib
import json
from pathlib import Path


class Index(HTMLParser):
    assets = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and "src" in attrs:
            self.assets.append(attrs["src"])
        if tag == "link" and attrs.get("rel") in {"stylesheet", "modulepreload"}:
            self.assets.append(attrs["href"])


root = Path(__file__).resolve().parents[1] / "frontend/dist-pages"
html = Index()
html.feed((root / "index.html").read_text(encoding="utf-8"))
if not html.assets or not all(asset.startswith("./assets/") and (root / asset).is_file() for asset in html.assets):
    raise SystemExit("Los recursos de la página deben existir y ser relativos al sitio.")
# The complete edition must ship byte-identical research assets.
if (root / "data/index.json").is_file():
    source = root.parent / "public"
    files = {p.relative_to(source).as_posix(): p for folder in ("data", "geo") for p in (source / folder).rglob("*") if p.is_file() and p.name != ".gitkeep"}
    shipped = {p.relative_to(root).as_posix() for folder in ("data", "geo") for p in (root / folder).rglob("*") if p.is_file() and p.name != ".gitkeep"}
    assert shipped == set(files), "El inventario publicado difiere del local"
    for name, original in files.items():
        assert hashlib.sha256(original.read_bytes()).digest() == hashlib.sha256((root / name).read_bytes()).digest(), name
        assert original.suffix in {".json", ".gz"}, name
    catalog = json.loads((root / "data/index.json").read_text(encoding="utf-8"))
    for dataset in catalog["datasets"]:
        assert (root / "data" / dataset["file"]).is_file(), dataset["id"]
    assert {p.name for p in root.iterdir()} <= {".nojekyll","index.html","assets","docs","data","geo"}
    print(f"Edición completa: {len(catalog['datasets'])} conjuntos y {len(files)} archivos idénticos al entorno local.")
    raise SystemExit(0)
allowed = {".nojekyll", "index.html", "assets", "docs", "geo", "analysis"}
if {path.name for path in root.iterdir()} != allowed:
    raise SystemExit("Contenido inesperado en el artefacto público.")
if any(file.suffix != ".md" for file in (root / "docs").rglob("*") if file.is_file()):
    raise SystemExit("La carpeta pública de documentación solo admite Markdown.")
if any(file.suffix not in {".js", ".css"} for file in (root / "assets").rglob("*") if file.is_file()):
    raise SystemExit("La carpeta de recursos solo admite JavaScript y CSS compilados.")
for file in (root / "assets").rglob("*.js"):
    bundle = file.read_text(encoding="utf-8").casefold()
    if any(marker in bundle for marker in ("entidad ficticia", "municipio ficticio", "geometría esquemática ficticia", "resultados ilustrativos")):
        raise SystemExit(f"Se encontraron marcadores sintéticos en {file.name}.")
geo = root / "geo"
if {path.name for path in geo.iterdir()} != {"index.json", "states.json.gz"}:
    raise SystemExit("Solo se permite la cartografía estatal de referencia.")
metadata = json.loads((geo / "index.json").read_text(encoding="utf-8"))
payload = gzip.decompress((geo / "states.json.gz").read_bytes())
if hashlib.sha256(payload).hexdigest() != metadata["provenance"]["web_sha256"]:
    raise SystemExit("El hash de la cartografía no coincide con su manifiesto.")
features = json.loads(payload)["features"]
states = {f"{i:02}" for i in range(1,33)}
if (len(features) != 32 or set(metadata["states"]) != states
    or {item["properties"]["cvegeo"] for item in features} != states
    or any(item["properties"]["nomgeo"] != metadata["states"][item["properties"]["cvegeo"]]
           or item["geometry"]["type"] not in {"Polygon", "MultiPolygon"}
           or not item["geometry"]["coordinates"] for item in features)):
    raise SystemExit("La cartografía estatal no corresponde a las 32 claves y nombres oficiales.")
print("Recursos relativos y cartografía estatal verificados. Sin cubos ni archivos epidemiológicos locales.")

analysis = root / "analysis"
diseases = json.loads((analysis / "diseases.json").read_text(encoding="utf-8"))
assert diseases["suppression_minimum"] >= 20
for dataset in diseases["datasets"]:
    assert set(dataset) == {"id","source","year","partial","cutoffs","url","sha256","counts"}
    assert all(isinstance(n,int) and n >= 20 for n in dataset["counts"].values())
lab_index = json.loads((analysis / "lab/index.json").read_text(encoding="utf-8"))
assert lab_index["minimum_records"] >= 1000
for dataset in lab_index["datasets"]:
    model = json.loads((analysis / "lab" / (dataset["id"]+".json")).read_text(encoding="utf-8"))
    assert not model["anomalies"]
expected = {"diseases.json","lab/index.json"} | {"lab/"+d["id"]+".json" for d in lab_index["datasets"]}
assert {p.relative_to(analysis).as_posix() for p in analysis.rglob("*") if p.is_file()} == expected
