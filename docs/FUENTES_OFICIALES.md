# Fuentes oficiales y procedencia

- Defunciones registradas. [DGIS Defunciones](https://www.dgis.salud.gob.mx/contenidos/basesdedatos/da_defunciones_gobmx.html)
- Egresos institucionales y sectoriales, conservados por separado. [DGIS Egresos](https://www.dgis.salud.gob.mx/contenidos/basesdedatos/da_egresoshosp_gobmx.html)
- Atenciones de urgencias. [DGIS Urgencias](https://www.dgis.salud.gob.mx/contenidos/basesdedatos/da_urgencias_gobmx.html)
- Lesiones y causas externas. [DGIS Lesiones](https://www.dgis.salud.gob.mx/contenidos/basesdedatos/da_lesiones_gobmx.html)
- Claves y geometrías de referencia. [INEGI Catálogo Único](https://www.inegi.org.mx/servicios/catalogounico/)

Cada archivo local registra su URL exacta, hash, tamaño y fecha en el manifiesto Bronze. Las capas Silver y Gold conservan la referencia al original. Véanse [auditoría de fuentes](../AUDITORIA_FUENTES.md) y [calidad de datos](CALIDAD_DATOS.md). El repositorio todavía carece de una serie poblacional aprobada como denominador.

La revisión de egresos institucionales, urgencias y lesiones de 2020 a 2024 cotejó los 15 enlaces exactos del índice con las copias de los catálogos de Datos Abiertos de la DGIS. El alcance público propuesto es un total nacional anual por serie. Los 15 conteos coinciden con Gold y el menor es 496,335 registros. La interfaz atribuye las cifras a la Secretaría de Salud / DGIS e identifica al Observatorio como responsable del cálculo.

El manual oficial identifica los términos de libre uso de SSA/DGIS para Cubos Dinámicos. La política federal define la reutilización y redistribución de los datos publicados como abiertos. La portada de Datos Abiertos devolvió HTTP 502 durante la revisión y el texto remitido por el usuario quedó como evidencia adicional. Sigue pendiente la revisión de difusión de los archivos detallados y los cruces con celdas pequeñas. [Manual oficial de Cubos Dinámicos](https://sinba.salud.gob.mx/cubos/Manual_Usuario_Cubos_20220927.pdf) · [Guía federal de datos abiertos](https://sidof.segob.gob.mx/notas/docFuente/5507476)
