# Defunciones DGIS: granularidad confirmada

Fuente: [http://www.dgis.salud.gob.mx/contenidos/basesdedatos/da_defunciones_gobmx.html](http://www.dgis.salud.gob.mx/contenidos/basesdedatos/da_defunciones_gobmx.html). Consulta y descarga: 2026-11-04.

## Hallazgos comprobados directamente
- Página recuperada mediante cliente HTTP; el 502 del navegador de investigación no impide la descarga directa.
- 48 enlaces ZIP inventariados: registros, descriptores y catálogos para 16 periodos etiquetados desde 1998 hasta 2024. Los archivos anteriores a 2024 siguen sin descargar ni verificar internamente.
- Paquete DEFUN_2024.zip: **30,983,992 bytes** descargados; CSV interno de **240,335,661 bytes**.
- **819,672 registros individuales y 74 columnas**, contados por lectura completa en streaming.
- **74 campos en el descriptor**, sin campos ausentes o adicionales frente al encabezado del CSV.
- **48 archivos de catálogos**; integridad CRC correcta en los tres ZIP descargados.
- Cero filas con número de columnas inconsistente. Esto no prueba ausencia de duplicados ni validez de todos los códigos.

## Granularidad disponible
Geografía separada: entidad, municipio y localidad de registro (`ent_regis`, `mun_regis`, `loc_regis`), residencia (`ent_resid`, `mun_resid`, `loc_resid`) y ocurrencia (`ent_ocurr`, `mun_ocurr`, `loc_ocurr`). Hay además territorio de ocurrencia de lesión. No intercambiar esas geografías.
Demografía: `sexo`, `edad`, `edad_agru`, nacimiento y otras características. Edad es un código compuesto con unidades y códigos especiales: 4065 no significa 4065 años. Se requiere validar catálogo antes de convertir.
Causas: `causa_def`, `cod_adicio`, `lista_mex`, `capitulo`, `grupo`. No se asume que código adicional represente todas las causas múltiples del certificado.
Tiempo: día/mes/año de ocurrencia, registro, nacimiento y certificación, con códigos especiales. No es una base de supervivencia.
Sitio y contexto: `sitio_ocur`, `derechohab`, `asist_medi` y variables de causas externas, entre otras. No son indicadores de calidad hospitalaria.

## Distinción temporal comprobada
Año de registro: {"2024": 819672}.
El archivo incluye defunciones ocurridas antes de 2024. Para análisis temporal se debe elegir explícitamente año de registro u ocurrencia; no presentar el total como defunciones ocurridas en 2024.

## Trazabilidad y reproducción
- `config/defunciones_files.json`: URLs y etiquetas de los 48 recursos.
- `data/bronze/manifest.json`: URL, versión en query, descarga UTC, bytes y SHA-256.
- `python/validation/audit_defunciones.py`: auditoría completa, sin publicar registros individuales.
- `reports/DEFUNCIONES_2024_AUDIT.json`: esquema y resultados estructurales.
- Originales en `data/bronze/defunciones/2024/`, excluidos del repositorio.

## Pendiente antes del uso analítico
Validar códigos contra catálogos (incluyendo claves especiales), encoding por recurso, fechas válidas, duplicados, edades y temporalidad; contrastar total y desagregaciones contra tabulados oficiales independientes; confirmar cobertura, estado definitivo/preliminar y licencia. El descriptor presenta texto con problemas de codificación; el auditor intenta reparación reversible de etiquetas sin alterar originales. No se han homologado catálogos históricos.

## Decisión de arquitectura
Microdatos oficiales serán la base local de Bronze y Silver; Gold se calculará desde ellos. El frontend recibirá agregados auditados con filtros de diagnóstico, edad, sexo, tiempo y geografía cuando sus controles estén completos. Localidad es disponibilidad técnica, no autorización para publicar celdas pequeñas.
El tabulado SSDF previo queda como evidencia auxiliar, no como sustituto del piloto nacional. Prioridad inmediata: validar y normalizar estos microdatos 2024; después extender historia por versiones y repetir para egresos, urgencias y lesiones.
