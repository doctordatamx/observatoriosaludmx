# Correcciones de integridad y visualización

- Se reprodujo el origen del incidente con los archivos históricos y se comprobó que el origen actual responde 404 para el catálogo sintético. [Auditoría de datos ficticios](AUDITORIA_DATOS_FICTICIOS.md)
- Se contrastó el cálculo que alimenta el tablero con consultas independientes de DuckDB sobre Silver. Coincidieron siete cifras representativas de mortalidad 2024 y todas las celdas de sus consultas. [Auditoría de cifras](AUDITORIA_CIFRAS.md)
- Se verificó igualdad de totales y participaciones a dos tamaños y se redujo la densidad de etiquetas en móvil. [Auditoría responsive](AUDITORIA_RESPONSIVE.md)
- Se incorporó un Atlas público estatal de referencia y se reforzaron las pruebas de claves y procedencia. [Validación geográfica](VALIDACION_GEOGRAFICA.md)
- Se rechaza un cubo con esquema incompatible. La falta de una partición municipal solicitada muestra indisponibilidad en lugar de usar un agregado nacional.
- El pie muestra el commit y la fecha de compilación, además de la versión del catálogo de datos cuando existe. La fecha de compilación no representa la hora de propagación de Pages. La versión local actual del catálogo es 2026-11-04.

Pruebas ejecutadas: 16 de Python, 8 de Node y contraste reproducible de cifras. GitHub Actions valida el artefacto público, el renderizado de estados de disponibilidad y los cálculos que no requieren microdatos. Los contrastes con Silver y la validación geométrica completa se ejecutan localmente, donde están los originales. La conciliación externa y la revisión de redistribución y supresión siguen pendientes para publicar indicadores epidemiológicos.
