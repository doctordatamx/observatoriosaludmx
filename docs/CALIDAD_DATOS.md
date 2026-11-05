# Calidad y disponibilidad de datos

| Universo DGIS | Archivos locales | Geografía del agregado |
|---|---|---|
| Defunciones registradas | 2020–2024 | Residencia |
| Egresos institucionales | 2020–2026 | Residencia |
| Urgencias | 2020–2026 | Residencia |
| Lesiones | 2020–2026 | Ocurrencia |
| Egresos sectoriales | 2020–2024 | Entidad de atención |

Los tres conjuntos de 2026 son parciales. El catálogo local muestra el corte por conjunto. Cobertura y completitud epidemiológica requieren validación externa. Un conteo describe registros de una fuente, periodo y filtro. La suma entre fuentes solo tiene uso operativo.

El reporte local generado por `python python/validation/audit_pipeline.py` incluye fecha, URL, SHA-256, tamaño, campos proyectados, filas, códigos territoriales, meses y estado parcial. Sus indicadores Gold incluyen edad desconocida, sexo desconocido, causa con formato no válido, mes desconocido y entidad no estándar. Para expresar cada indicador como porcentaje se divide su conteo entre el total del mismo conjunto. Un valor desconocido puede reflejar ausencia de dato o código fuera del dominio validado. El reporte conserva ambas limitaciones sin asignar una puntuación global.

La auditoría no mide duplicados de evento. Los registros que coinciden en las dimensiones proyectadas pueden corresponder a eventos distintos. Las pruebas de claves municipales verifican el cruce técnico de catálogos y geometrías; la correspondencia histórica queda pendiente.
