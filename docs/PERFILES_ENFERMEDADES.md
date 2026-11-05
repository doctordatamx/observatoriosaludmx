# Perfiles de enfermedades · versión local 0.4

En **Enfermedades**, busca y selecciona una categoría CIE-10 a tres caracteres. La ficha usa el código y el nombre del catálogo DGIS disponible. No añade definiciones diagnósticas ni agrupa automáticamente códigos clínicamente relacionados. La categoría puede corresponder a una causa, afección, lesión o motivo codificado de atención.

La unidad depende de la fuente: causa básica en defunciones y afección principal registrada en las fuentes asistenciales. La proporción divide los registros de la categoría entre todos los registros de la misma fuente, año, territorio, sexo y edad, incluidos los códigos sin clasificación válida. No es prevalencia.

**Evolución anual:** carga explícita y secuencial de agregados. Respeta los filtros y señala periodos parciales y archivos o municipios no disponibles, sin sustituirlos por ceros. Usa las particiones municipales y exige correspondencia de catálogo y geometría para cada año. No se homogenizan las coberturas ni los límites históricos. El CSV conserva código, ámbito, filtros, disponibilidad y corte.

**Comparación territorial:** mismo año, fuente, categoría, edad y sexo. Permite comparar entidades o municipios dentro de la entidad seleccionada. Los conteos dependen de cobertura y población; no se calculan tasas ni diferencias de riesgo.

El enlace al atlas conserva los filtros. La pirámide, el detalle mensual y la ficha imprimible reutilizan la consulta existente. No se descargan microdatos ni se publica la aplicación.
