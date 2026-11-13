"""Add only project documentation to the static Pages build."""
import sys
from pathlib import Path
from shutil import copytree

ROOT = Path(__file__).resolve().parents[1]
output = ROOT / "frontend" / "dist-pages"
if "--full" in sys.argv:
    if not all((output / p).is_file() for p in ("index.html","data/index.json","data/lab/index.json","data/municipal-index.json","geo/index.json")):
        raise SystemExit("Faltan recursos de la edición completa.")
    (output / ".nojekyll").touch()
    raise SystemExit(0)
if not (output / "index.html").is_file() or (output / "data").exists() or (output / "geo").exists():
    raise SystemExit("Se requiere una compilación de Pages sin archivos de datos o geometrías.")
copytree(ROOT / "frontend" / "public" / "docs", output / "docs", dirs_exist_ok=True)
copytree(ROOT / "pages" / "geography", output / "geo")
analysis = ROOT / "pages/analysis"
if analysis.exists():
    copytree(analysis, output / "analysis")
(output / ".nojekyll").touch()
