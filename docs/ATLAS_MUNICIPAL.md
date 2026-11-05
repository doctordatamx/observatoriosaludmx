# Atlas estatal y municipal · versión local 0.3

## Qué se implementó
Mapa nacional por entidad y exploración municipal al seleccionar una entidad. Los filtros de año, causa CIE-10, sexo y edad actualizan el mapa y el perfil; seleccionar municipio actualiza serie mensual, pirámide, causas y tablas. El municipio se conserva en la URL como clave concatenada entidad(2)+municipio(3). No se interpretan las frecuencias como tasas o riesgo.

| Fuente | Ámbito geográfico | Municipio |
|---|---|---|
| Defunciones | Residencia habitual | mun_resid junto con ent_resid |
| Egresos institucionales | Residencia habitual | MUNIC junto con ENTIDAD |
| Urgencias | Residencia habitual | MUNRESIDENCIA junto con ENTRESIDENCIA |
| Lesiones | Ocurrencia del evento | CodMunicipio junto con CodEstado |
| Egresos sectoriales | Atención | Solo CEDOCVE; no se infiere municipio desde CLUES |

## Geometrías y procedencia
Fuente: [INEGI, Servicio Web del Catálogo Único](https://www.inegi.org.mx/servicios/catalogounico/), rutas oficiales `geo/mgee/` y `geo/mgem/{entidad}`. La respuesta declara **Marco Geoestadístico, diciembre de 2025**; instantánea consultada el 4 de noviembre de 2026. Se descargaron 32 entidades y 2,478 áreas municipales. No se consumen poblaciones censales de la respuesta como denominadores.
Originales inalterados: data/bronze/inegi/2026-11-04. URL, metadatos, bytes, SHA-256 y transformaciones: reports/GEOMETRY_MANIFEST.json. El servicio declara EPSG:6365 por geometría; pyproj transforma a EPSG:4326 con orden XY explícito. Se comprueba que los polígonos originales y derivados sean válidos y no vacíos.
Se simplifica para dibujo a tolerancia 0.0015 grados con preservación de cobertura cuando es posible; el manifiesto identifica el método por archivo. La simplificación no se usa para medir áreas, construir vecindades o hacer inferencia espacial. Los GeoJSON web eliminan atributos poblacionales y conservan código/nombre.

## Correspondencia temporal: límite explícito
El mapa representa límites de diciembre de 2025; **no es una reconstrucción de límites para cada año sanitario**. No se aplican equivalencias, prorrateos, fusiones ni redistribuciones retrospectivas. Un código que coincide no prueba que los límites históricos sean iguales. La advertencia es visible. Antes de comparar espacialmente años o estimar tasas municipales, incorporar límites por edición y tablas de equivalencia auditadas.

## Catálogos sanitarios y códigos especiales
La correspondencia exige clave exacta en el catálogo DGIS del año o periodo declarado y en la geometría INEGI. Auditoría: reports/MUNICIPAL_CATALOGUE_AUDIT.json. Los catálogos anteriores de mortalidad tienen encabezados diferentes, tabulaciones o carecen de cvegeo: se usan cve_ent y cve_mun de entradas municipales, con reglas explícitas. Nunca convertir municipio a entero sin volver a su ancho oficial.
Los catálogos 2023–2025 se usan como contraste provisional de códigos para 2026, con aviso de vigencia pendiente. Códigos nuevos, extranjeros, desconocidos y claves fuera de catálogo se conservan en agregados y tablas, pero no se pintan por aproximación. La interfaz cuenta los registros no representables de la consulta; gris significa sin registros o sin correspondencia validada, no ausencia de enfermedad.

## Datos, rendimiento y publicación
Silver conserva el municipio original como cadena. R usa las mismas funciones de edad, sexo y causas del agregado estatal y genera particiones por fuente/año/entidad. Cada fila Gold municipal incluye las seis dimensiones existentes y un índice municipal adicional. Se conservan desconocidos para conciliar totales. Nacional usa el agregado estatal; el nivel municipal carga solo una entidad, nunca microdatos.
Los 26 conjuntos con municipio directo se procesan separados; las cinco ediciones sectoriales conservan el atlas estatal. Son agregados de investigación **local** con celdas pequeñas; no publicar sin política de supresión complementaria, revisión de privacidad y licencia. No se generan tasas, suavizados ni mapas de riesgo en esta etapa.

## Reconstrucción
1. `python python/ingestion/build_silver.py` amplía las columnas proyectadas y reutiliza solo proyecciones compatibles.
2. `python python/ingestion/fetch_geography.py` descarga/conserva la instantánea y genera GeoJSON web (requiere red y dependencias espaciales).
3. `python python/validation/audit_municipal_catalogues.py` cruza catálogos del periodo y geometrías.
4. R: `.libPaths(c('.runtime/R',.libPaths())); targets::tar_make(script='_targets_municipal.R',store='_targets_municipal',callr_function=NULL)`.
5. `python tests/test_spatial.py -v` y `npm --prefix frontend run build`.

Se conserva el caché local por fuente/año para continuar actualizaciones interrumpidas. Su firma incluye SHA-256 de código, proyección, catálogo, geometría y original; cambiar cualquiera invalida la reutilización. No tratar el caché como validación externa. El pipeline principal estatal conserva sus resultados; la ampliación municipal se valida contra ellos.


## Verificación de esta entrega
Las cinco pruebas espaciales definidas pasaron: geometrías, filtro de catálogos, conservación en los 26 conjuntos, rollup completo de mortalidad 2024 y cuatro consultas municipales independientes en DuckDB. Compilación TypeScript/Vite correcta. El navegador confirmó selección por mapa, zoom y actualización de perfil/URL. Véase reports/ATLAS_VERIFICACION.json y reports/atlas-municipal.jpg.
