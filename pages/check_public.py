"""Validate relative assets and prevent accidental data publication."""
from html.parser import HTMLParser
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
allowed = {".nojekyll", "index.html", "assets", "docs"}
if {path.name for path in root.iterdir()} != allowed:
    raise SystemExit("Contenido inesperado en el artefacto público.")
if any(file.suffix != ".md" for file in (root / "docs").rglob("*") if file.is_file()):
    raise SystemExit("La carpeta pública de documentación solo admite Markdown.")
if any(file.suffix not in {".js", ".css"} for file in (root / "assets").rglob("*") if file.is_file()):
    raise SystemExit("La carpeta de recursos solo admite JavaScript y CSS compilados.")
print("Recursos relativos verificados. Artefacto sin archivos de datos ni geometrías.")
