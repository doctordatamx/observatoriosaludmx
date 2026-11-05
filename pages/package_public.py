"""Add only project documentation to the static Pages build."""
from pathlib import Path
from shutil import copytree

ROOT = Path(__file__).resolve().parents[1]
output = ROOT / "frontend" / "dist-pages"
if not (output / "index.html").is_file() or (output / "data").exists() or (output / "geo").exists():
    raise SystemExit("Se requiere una compilación de Pages sin archivos de datos o geometrías.")
copytree(ROOT / "frontend" / "public" / "docs", output / "docs", dirs_exist_ok=True)
copytree(ROOT / "pages" / "geography", output / "geo")
(output / ".nojekyll").touch()
