# Observatorio Epidemiológico de México · Doctor Data MX

Versión local 0.5 — 4 de noviembre de 2026. React + TypeScript + Vite, ingeniería Python/Arrow y agregación epidemiológica en R/data.table con targets y renv.

## Abrir
Desde `frontend`: `npm ci` y `npm run dev -- --port 5173`.
Abrir http://127.0.0.1:5173/ . El servidor escucha solo en loopback. Los módulos analíticos requieren reconstruir los datos locales.

La edición de [GitHub Pages](https://doctordatamx.github.io/observatoriosaludmx/) muestra el estado de disponibilidad, la metodología y un mapa estatal de referencia del INEGI sin cifras epidemiológicas. Desde `frontend`, ejecutar `npm ci` y `npm run build:pages` (requiere Python 3). Vite desactiva la copia de `public/` y el empaquetado añade documentación y cartografía de referencia. Desde la raíz, `python pages/check_public.py` valida rutas y contenido. Tras las pruebas, desplegar el contenido de `frontend/dist-pages/` en la raíz de `gh-pages`, incluyendo `.nojekyll`.

## Qué funciona
- 31 conjuntos anuales reales desde 2020, sin unir fuentes ni deduplicar personas entre ellas.
- Filtros coordinados por fuente, año, entidad, sexo, grupo etario y categoría CIE-10 de tres caracteres.
- Serie mensual, pirámide por edad/sexo, causas principales, tabla y distribución territorial.
- URL con filtros, CSV de causas de la consulta, SVG por gráfico y ficha mediante impresión/guardar PDF del navegador.
- Vistas de fuentes, hashes y metodología descargable.
- Carga diferida de agregados comprimidos por fuente/año; nunca microdatos en el navegador.

## Reconstruir datos
Los originales ya están en `data/bronze/`, excluidos de Git. No descargarlos de nuevo si sus hashes coinciden.
1. `python python/ingestion/download_recent.py` (opcional: actualizar inventarios y descargar; requiere red).
2. `python python/ingestion/build_silver.py` (Arrow proyecta columnas originales a CSV y Parquet, sin interpretar códigos).
3. En R, `source('R/bootstrap.R')` para restaurar `.runtime/R` desde renv.lock si hace falta.
4. Desde la raíz: `Rscript -e ".libPaths(c('.runtime/R',.libPaths())); targets::tar_make(callr_function=NULL)"`.
5. Desde frontend: `npm run build`.
R está en este equipo en `C:/Program Files/R/R-4.6.1/bin/Rscript.exe`; puede usarse la ruta completa si no está en PATH.
Python: instalar `python -m pip install -e ".[data,test]"` cuando falten dependencias. Versiones utilizadas en docs/ENTORNO.json.

## Verificar
`python -m unittest discover -s tests -v` comprueba conservación de todos los cubos y compara una consulta filtrada contra SQL independiente en DuckDB.
`Rscript tests/test_age.R` comprueba límites etarios, unidades y desconocidos.
`node --test frontend/tests/*.test.mjs` comprueba perfiles, comparaciones y variación interanual con Node 24. `python python/validation/audit_pipeline.py` verifica la cadena Bronze–Silver–Gold y genera un reporte local.
`cd frontend` y `npm run build` comprueba TypeScript y genera dist.

## Alcance científico
Exploración local provisional: no se presenta como validación epidemiológica definitiva. No hay denominadores poblacionales ni tasas; homologación histórica territorial, grupos clínicos compuestos y modelos están pendientes. 2026 tiene corte al 15 de octubre en los archivos procesados. Metadatos compartidos 2023–2025 no prueban por sí mismos comparabilidad de 2026.
Los datos detallados de Gold contienen celdas pequeñas para investigación local. **No publicar dist ni los agregados antes de resolver licencia, política de supresión y revisión metodológica.**

## Documentación
METODOLOGIA.md, ARQUITECTURA.md, AUDITORIA_FUENTES.md, docs/IMPLEMENTACION.md, docs/INDICADORES.md, reports/CALIDAD.md, reports/GOLD_QUALITY.json.
LICENSE aplica al código y documentos propios; las fuentes mantienen sus condiciones de origen.

[Auditoría técnica](docs/AUDITORIA_TECNICA.md) · [Fuentes oficiales](docs/FUENTES_OFICIALES.md) · [Calidad](docs/CALIDAD_DATOS.md) · [Cambios](docs/CHANGELOG.md).


## Cobertura ampliada desde 2020
Defunciones y egresos sectoriales 2020–2024; egresos institucionales, urgencias y lesiones 2020–2026. Véase reports/AMPLIACION_2020.md. El último año conserva su corte parcial.


## Atlas municipal
Disponible en la pestaña Atlas: mapa estatal y municipios para las cuatro fuentes con campo directo. Geometrías INEGI de diciembre 2025, con aviso de correspondencia histórica pendiente. Egresos sectoriales se mantienen solo por entidad de atención. Detalles y reconstrucción: docs/ATLAS_MUNICIPAL.md.

**Perfiles:** ficha por CIE-10, evolución anual y comparación territorial en Enfermedades. Véase docs/PERFILES_ENFERMEDADES.md.

**Laboratorio:** agrupamiento, Moran descriptivo y revisión de meses fuera de rango. Véase docs/MODELOS_AVANZADOS.md.
