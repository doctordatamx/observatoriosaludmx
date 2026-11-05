# Auditoría preliminar de fuentes
Actualización: defunciones 2024 descargadas y auditadas estructuralmente; véase docs/DEFUNCIONES_GRANULARIDAD.md. La consulta HTTP directa funcionó, a diferencia del navegador de investigación.

Consulta: 4 de noviembre de 2026. Alcance documental; **no se han validado microdatos nacionales**.

## Inventario de disponibilidad declarada
Fuente oficial: [SINBA, cubos dinámicos](https://sinba.salud.gob.mx/CubosDinamicos). Copia local en docs/evidence/sinba_cubos.html. Los periodos siguientes son declaraciones del portal, no inventario de archivos descargables.

| Base | Periodos anunciados / versión | Variables mencionadas | Unidad |
|---|---|---|---|
| Egresos | SS 2000–2023; OPD 2024–2025 definitivos; 2026 preliminar. Sector 2004–2024 definitivo, 2025–2026 preliminar | Afección principal, sexo, edad, estancia | Egreso |
| Urgencias | 2007–2023 definitivo; OPD incorporado desde 2024, 2024–2025 cerrado; 2026 preliminar | Afección principal, tipo de urgencia, sexo, edad | Atención |
| Defunciones | Enlace 1998–2024; textos históricos contradictorios | Causa básica, edad, sexo, registro/residencia | Defunción registrada |
| Lesiones | 2010–2023 definitivo; OPD desde 2024, 2024–2025 cerrado; 2026 preliminar | Afección, causa externa, intencionalidad, edad, sexo | Registro |

No equiparar cerrado con definitivo. La página contiene metadatos antiguos incompatibles con encabezados actuales; confirmar versión por archivo. Egresos institucionales y sectoriales pueden solaparse. Mantener separados.

## Obstáculos observados
La [página principal DGIS](http://www.dgis.salud.gob.mx/contenidos/basesdedatos/Datos_Abiertos_gobmx.html) y rutas de egresos/urgencias devolvieron 502 al navegador de investigación. datos.gob.mx respondió 403. Los diccionarios enlazados de egresos/defunciones agotaron tiempo de consulta. No equivale a demostrar que no existen datos.
Se encontró [catálogo institucional INSP de egresos](https://riisp.insp.mx/nada/index.php/catalog/EGRESOS) como alternativa por auditar; no se descargó ni se asumió equivalencia con SAEH.

## Inventario por archivo: pendiente explícito
Para egresos, urgencias y lesiones, config/sources.json conserva null para número de registros, bytes, formatos descargables, URL de archivo, licencia, diccionario confirmado y catálogos confirmados. null significa no verificado, nunca cero. No inferir esos campos desde cubos. Los enlaces HTML son puntos de consulta, no archivos CSV.
Por cada archivo recuperar: nombre, URL directa, años, versión, fecha, tamaño, conteo físico y lógico, separador/encoding, diccionario, catálogos, cobertura institucional y territorial, variables demográficas/temporales, diagnósticos y condición de egreso. Comparar cambios de esquema y catálogos entre años. Confirmar entidades y municipios por separado para residencia, ocurrencia y atención.
No se ha confirmado licencia de redistribución de las cuatro series; no extender la licencia de un recurso a todos. No integrar ni publicar hasta revisión.

## Piloto real independiente de las cuatro descargas nacionales
[SSDF, cuadro 6.3, anuario 2007](https://data.salud.cdmx.gob.mx/portal/media/estadistica2007/estadistica/603.htm). Se extraen solo urgencias y egresos, siete años por serie. Véase reports/CALIDAD.md, manifiesto SHA-256 y scripts. Universo institucional local; no representativo de hospitales nacionales. No hay variables clínicas o demográficas. Pie de fuente fechado 2006 pese a columnas hasta 2007: inconsistencia pendiente. La comprobación es de transcripción del tabulado, no validación externa.

## Fuentes complementarias por incorporar
INEGI EDR y población; CONAPO conciliación/proyecciones; CLUES; CIE-10; catálogo geoestadístico y geometrías; población estándar elegida por protocolo. No se descargaron ni validaron en esta entrega. Revisar solapamientos DGIS/INEGI antes de cualquier integración. No fusionar defunciones registradas y mortalidad hospitalaria.


## Actualización: páginas directas de egresos y urgencias
Consulta HTTP directa exitosa el 2026-11-04 para ambas páginas:
- http://www.dgis.salud.gob.mx/contenidos/basesdedatos/da_egresoshosp_gobmx.html : 66 enlaces de recursos. Registros etiquetados 2010–2026 y serie sectorial 2004–2024; incluye descriptores y catálogos. Inventario: config/egresos_files.json.
- http://www.dgis.salud.gob.mx/contenidos/basesdedatos/da_urgencias_gobmx.html : 33 enlaces de recursos. Registros etiquetados 2008–2026, descriptores y catálogos. Inventario: config/urgencias_files.json.
Estos intervalos corresponden exclusivamente a enlaces localizados en estas páginas, no a toda disponibilidad histórica. Se corrigió la estrategia de descubrimiento: el error 502 del navegador no describe el acceso HTTP directo, que sí funciona.
Tamaños declarados del paquete de registros 2024: egresos 105 Mb, egresos sectorial 78.4 Mb y urgencias 221 Mb, según etiquetas del sitio; bytes efectivos y filas aún sin verificar. Los enlaces 2026 no acreditan año completo ni versión definitiva. No asumir que el descriptor 2023–2025 sirve para 2026.
No se descargaron aún estos paquetes de registros. Granularidad interna, campos, catálogos, cobertura, licencia y totales siguen pendientes de inspección. Mantener series institucional y sectorial separadas por posible solapamiento; nunca concatenarlas sin evaluar duplicación y cobertura.


## Descarga reciente completada
Se descargaron los 21 recursos seleccionados desde 2024, incluyendo lesiones. Las afirmaciones anteriores de descargas pendientes quedan actualizadas por reports/DESCARGAS_2024_A_FECHA.md; validación analítica aún pendiente.


## Actualización desde 2020
Se recuperaron los 67 recursos seleccionados desde 2020, incluidos diccionarios y catálogos. Las 31 tablas principales se proyectaron a Silver. Véase reports/AMPLIACION_2020.md; periodos disponibles no equivalen a cobertura constante.
