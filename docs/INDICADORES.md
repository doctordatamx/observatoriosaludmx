# Fichas iniciales

| Campo | Frecuencia de urgencias / egresos del piloto |
|---|---|
| Fórmula | Conteo anual publicado, sin recalcular eventos individuales |
| Numerador | Atenciones de urgencias o egresos, separados |
| Denominador | No aplica; no son tasas |
| Fuente | SSDF, cuadro 6.3, anuario 2007 |
| Cobertura | Secretaría de Salud del Distrito Federal; no todo México |
| Periodo | 2001–2007 |
| Exclusiones | No hay desagregación individual disponible |
| Incertidumbre | No estimada: conteos administrativos tabulados |
| Limitaciones | Pie identifica SIS/SAEH 2006 pese a incluir 2007; pendiente aclaración. Urgencias calificadas y no calificadas. No personas únicas. |

## Indicadores nacionales propuestos, no habilitados
Tasa cruda: D/P × 100000, con residencia, sexo, edad y periodo compatibles; IC Poisson exacto si justificado. Tasa ajustada directa: suma de pesos estándar por tasas específicas × 100000; pesos suman uno y estratos coinciden. Documentar estándar, año, fuente y sensibilidad. No usar total poblacional como denominador de incidencia de demanda parcial hospitalaria.
Proporción de egresos por defunción: egresos con condición defunción / egresos con condición conocida × 100; reportar proporción desconocida y sensibilidad usando todos los egresos. IC binomial apropiado si la interpretación probabilística está justificada; nunca ranking de calidad.
Toda ficha futura incluirá versión de fuente, filtros, numerador, denominador, exclusiones, cobertura, incertidumbre, revisión y fecha. Ausencia de denominador bloquea tasas, no se reemplaza por cero.


## Frecuencias de microdatos implementadas en la versión 0.1
Numerador: filas de la tabla principal que cumplen filtros; agrupación por categoría CIE-10 a tres caracteres. Denominador: ninguno para frecuencias; para proporción de causa, total de registros filtrados de la misma fuente/periodo. No son tasas poblacionales ni personas únicas.
Fuentes: paquetes DGIS 2024–2026 disponibles, con hash y URL en la vista de trazabilidad. Cobertura institucional variable y pendiente de conciliación externa. Tiempo y territorio por fuente se documentan en docs/IMPLEMENTACION.md. Exclusiones: no se eliminan registros por dimensiones inválidas; se conservan categorías desconocidas. Incertidumbre: no estimada ni representada como IC. La proporción se interpreta únicamente dentro de la consulta, no como prevalencia.
