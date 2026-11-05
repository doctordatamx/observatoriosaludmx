# Arquitectura R-first + Python

## Contratos y flujo
Bronze conserva bytes originales fuera de Git; manifiesto con URL, fecha UTC, bytes, SHA-256, versión, licencia y validación. Las dos páginas públicas de evidencia se conservan localmente en docs/evidence; su licencia de redistribución sigue pendiente. No subirlas hasta resolverla.
Silver será Parquet particionado por fuente/año, con esquema por versión. Cada campo normalizado conserva campo original, regla y versión de catálogo; faltantes estructurales distintos de desconocidos. No homologar instituciones ni territorios sin equivalencia documentada.
Gold contendrá agregados por fuente, cobertura, año y dimensiones permitidas. Una tabla de calidad y un manifiesto acompañarán cada partición. Publicación exige gates de integridad, cobertura, privacidad y conciliación externa. Microdatos nunca se copian al frontend.

## Responsabilidades
Python obtiene archivos por streaming y hashes y valida contratos; el piloto HTML es una excepción de ingeniería para extraer un tabulado. R es dueño de indicadores, incertidumbre, estandarización, series y gráficos científicos; targets expresa dependencias, renv fija versiones reales. DuckDB/Arrow permiten trabajar por particiones sin cargar la serie completa; data.table procesa lotes. No se implementa el mismo estimador en Python y R.
React/TypeScript/Vite consume JSON de agregados para el piloto; Parquet y DuckDB-Wasm se evaluarán cuando el tamaño lo justifique. El navegador nunca descarga microdatos.

## Presupuestos propuestos
Fragmentos web de hasta 2 MB comprimidos y carga inicial de hasta 1 MB como objetivos de diseño, no límites del proveedor. Dimensiones de alta cardinalidad mediante particiones y carga diferida. Cachear por hash, invalidar por manifiesto, limitar memoria y medir con datos reales.
GitHub Pages serviría dist estático con base relativa. Almacenamiento externo de objetos: separa grandes agregados y permite caché, pero agrega costo por almacenamiento/egreso y CORS. Tarifas, límites vigentes de Pages y política institucional se verificarán antes del despliegue; no se cotizan aquí.

## Reproducibilidad y seguridad
No credenciales en Git. No enlaces de personas entre fuentes. Informes de calidad por corrida; fallo impide reemplazar la versión publicada. CI local de datos sintéticos solo para pruebas y build estático. CI no despliega ni descarga grandes bases automáticamente.
Estado actual: extractor y frontend ejecutables; pipeline R preparado pero no ejecutado, Silver nacional y Gold epidemiológico pendientes.


## Estado implementado 0.1
R 4.6.1 fue localizado y el pipeline R/data.table/targets ejecutado. 31 proyecciones Silver se materializaron en Parquet y CSV, con originales en Bronze. React consume cubos Gold gzip; caché de dos conjuntos. Véase docs/IMPLEMENTACION.md para límites y reglas. Los estados anteriores de pendiente en este documento se refieren al diseño nacional completo.
