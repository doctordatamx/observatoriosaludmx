# Implementación local 0.2

## Flujo ejecutado
Python/Arrow abre ZIP en streaming, selecciona únicamente la tabla principal de cada fuente y escribe una proyección Silver en Parquet/Zstd y CSV. Conserva columnas como cadenas originales; los diccionarios y el hash enlazan la proyección con Bronze. No se fusionan afecciones/procedimientos/productos con egresos para evitar multiplicación de filas.
Silver actual es una proyección para el MVP, no una homologación completa de todas las variables. Municipio, fechas completas, condiciones de egreso y estancias permanecen en Bronze y requieren adaptadores posteriores.
R/data.table normaliza las dimensiones del MVP y genera un cubo conjunto de entidad, sexo, edad, mes y categoría CIE-10; jsonlite escribe JSON compacto y gzip. targets registra manifiesto y archivos Silver como entradas. renv.lock y package-lock.json fijan las dependencias respectivas.

## Reglas operativas
- Defunciones: entidad de residencia y mes de registro; no confundir con ocurrencia.
- Egresos institucionales y urgencias: entidad de residencia y mes estadístico.
- Lesiones: entidad de ocurrencia del evento, según descriptor; mes estadístico.
- Egresos sectoriales: entidad de atención y mes reportado; serie separada.
- Edad DGIS de atenciones: 2 horas, 3 días, 4 meses, 5 años; comprobado en catálogos institucional, sectorial y catálogo anidado de lesiones. Se desconocen valores incompatibles con unidad/rango.
- Edad de defunciones: códigos del catálogo 2024; 1/2/3 identifican edades menores de un año y 4 años cumplidos, con códigos especiales tratados aparte.
- Sexo 1 y 2 mantiene etiquetas oficiales; 3 separado en las fuentes que lo permiten; otros códigos colapsados en desconocidos con valor original retenido en Silver.
- Causa: mayúsculas, sin punto, tres primeros caracteres solo si formato admisible. Esto no acredita elegibilidad ni validez clínica de cada código.
- Mes no válido queda en 0; edad desconocida se conserva como grupo 19. No se borran para forzar totales.
- La pirámide muestra solo categorías 1/2; el total y nota inferior incluyen las demás.

## Producto
La interfaz mantiene en memoria únicamente el agregado consultado y caché máxima de dos archivos. Los paquetes van de aproximadamente 0.88 a 5.88 MB comprimidos; algunos exceden el presupuesto inicial de 2 MB. Antes de publicación, particionar por causa/territorio o evaluar consultas sobre Arrow. El navegador no carga las bases completas.
Compartir consulta copia la URL local con filtros; no habilita acceso remoto. La ficha PDF usa impresión del navegador y requiere que el usuario elija guardar PDF. No hay exportación PDF de servidor.

## Límites actuales
No hay mapas, municipios, ajuste por edad, tasas, IC, comparaciones anuales automáticas, estancia o condición de egreso. Vistas clínicas usan categorías individuales a tres caracteres, sin grupos clínicos revisados aún. Laboratorio bloqueado. Se requieren denominadores, geometrías, listas de causas y revisión de comparabilidad antes de habilitarlos.
Los recursos Gold en frontend/public son para localhost; no cuentan todavía con supresión de celdas pequeñas. No desplegar ni compartir estos directorios sin revisar riesgo de reconstrucción, licencia y autorización.


## Extensión desde 2020
Se procesan 31 tablas principales. La proyección reconoce ZIP anidado, delimitador por encabezado y nombres sin distinción de mayúsculas, conservando mapeo explícito. No se omiten filas incorrectas: únicamente se reconoce el pie de exportación SQL documentado y se verifica su total. Catálogos de edad de mortalidad por año; unidades de edad y ámbito geográfico contrastados contra metadatos históricos. La coexistencia de años no constituye prueba de comparabilidad.
