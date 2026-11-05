# Auditoría técnica del Observatorio Salud MX

## Estado inicial

La base auditada es el commit `9667c4b`. React 19, TypeScript y Vite sirven una aplicación estática con ECharts, SVG y exportaciones CSV y de impresión. El código se organiza por Panorama, Atlas, Perfiles y Laboratorio. `profileData.ts` reúne operaciones reutilizables de filtrado. La configuración de fuentes vive en `config/`. GitHub Pages publica la raíz de `gh-pages` bajo `/observatoriosaludmx/`. Al iniciar la auditoría, la rama pública contenía 25 escenarios sintéticos de 2020–2024 y el repositorio carecía de flujos activos de Actions.

## Arquitectura y archivos

| Capa | Entrada y salida | Implementación |
|---|---|---|
| Bronze | Archivos originales y catálogos ZIP, manifiesto JSON con URL, fecha y SHA-256 | Python, `download_recent.py` |
| Silver | Proyección de campos como cadenas, CSV y Parquet Zstandard con metadatos de esquema y corte | PyArrow, `build_silver.py` |
| Gold | Cubos estatales y particiones municipales JSON gzip, índices y reportes | R, data.table y targets |
| Modelos | JSON por fuente y periodo, vecindad estatal y análisis descriptivo | Python/Shapely y R |
| Visualización | Carga diferida de agregados, catálogo y GeoJSON comprimido | React, ECharts y Vite |
| Validación | Comparaciones independientes contra Silver, integridad de archivos, geometrías y pruebas de filtros | DuckDB, PyArrow, unittest, Node y R |

Los bloqueos de dependencias están en `frontend/package-lock.json`, `renv.lock` y `requirements-*.lock`. Las definiciones de ejecución están en `_targets.R`, `_targets_municipal.R` y `frontend/vite.config.ts`. Se conservan universos de fuente separados, mapas, filtros coordinados, perfiles, exportación, dispersión MDS y dendrograma en la edición local.

## Hallazgos y prioridades

| Prioridad | Hallazgo | Tratamiento |
|---|---|---|
| Crítica | La rama pública presentaba cifras y geometrías sintéticas. Los cubos locales incluyen celdas pequeñas y su redistribución sigue pendiente de revisión. | El nuevo artefacto de Pages muestra disponibilidad explícita y conserva navegación y metodología. Verifica que se empaqueten únicamente HTML, JS, CSS y documentación. |
| Alta | La descarga reutilizaba por URL aunque el servidor cambiara el archivo. Un clon limpio podía fallar al guardar evidencia. | Revalidación condicional cuando el servidor ofrece ETag o fecha, SHA-256, almacenamiento versionado, directorio de evidencia y error de proceso si falla alguna descarga. |
| Alta | El inventario documenta procedencia interna. Falta conciliación externa con tabulados y definición de comparabilidad anual, especialmente territorial. | Verificación local de la cadena completa y reporte por conjunto. Mantener bloqueada la difusión de datos hasta revisión. |
| Alta | Falta un identificador de evento validado de forma homogénea. La proyección Silver puede producir filas idénticas para eventos diferentes. | Mantener registros, documentar el límite y evaluar unicidad por fuente a partir de identificadores y reglas oficiales. |
| Media | La serie de perfiles no calculaba cambios interanuales. | Variación de conteos con denominador del año previo, años completos consecutivos y conteo previo positivo. Visible en tabla y CSV. |
| Media | Silver escribe las proyecciones directamente y depende de un marcador previo para reutilizar. El empaquetado inicial de JS ronda 307 kB gzip. | Pendientes transacción de proyecciones, prueba de interrupción, separación de módulos y mediciones móviles. |

## Datos y verificación

La ejecución de `python python/validation/audit_pipeline.py` verificó **31 conjuntos** y **100,302,235 filas**, sumadas solo como métrica operativa. Conciliaron SHA-256, tamaño de Bronze, URL DGIS registrada, esquema y conteo Parquet, total y meses del cubo y señalización parcial de 2026. El reporte local `reports/AUDITORIA_PIPELINE.json` detalla entidades/códigos, cortes, calidad y campos por conjunto. El portal general de DGIS devolvió HTTP 502 en la consulta de esta auditoría. La coincidencia de manifiestos y archivos locales acredita trazabilidad interna, con verificación externa pendiente.

Las pruebas locales de Python revisan preservación de agregados, consultas por edad, sexo, territorio y causa contrastadas con SQL, conservación municipal, geometrías y modelos. Node verifica el denominador del perfil y el cambio interanual. R comprueba los límites etarios y códigos desconocidos. La revisión exhaustiva de duplicados, faltantes por campo original, codificación histórica y conciliación contra tabulados oficiales sigue pendiente. También quedan pendientes pruebas de accesibilidad WCAG, dispositivos y exportaciones de extremo a extremo.

## Siguiente secuencia

1. Validar originales contra tabulados externos y catálogos por versión. Definir elegibilidad de publicación, supresión primaria y complementaria y riesgo de inferencia entre filtros.
2. Endurecer Silver y automatizar descubrimiento y validación de datos con retención de artefactos. Separar el flujo de publicación de la validación en GitHub Actions.
3. Integrar denominadores oficiales compatibles, versionados y revisados antes de habilitar tasas. Ampliar indicadores hospitalarios cuando se validen sus campos.
4. Continuar con rendimiento, accesibilidad, comparador, capítulos y agrupaciones clínicas, conservando los universos separados.
