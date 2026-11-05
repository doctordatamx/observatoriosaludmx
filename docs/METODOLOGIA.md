# Protocolo metodológico inicial · v0.1
Fecha: 2026-11-04. Documento de diseño, sujeto a revisión epidemiológica antes de resultados nacionales o modelos.

## 1. Diseño
Observatorio de registros administrativos con análisis descriptivo repetido y ecológico. Las bases responden a procesos distintos de captación; el sistema no es una cohorte de personas enlazadas.
## 2. Objetivos
Describir frecuencias, perfiles y diferencias territoriales y temporales dentro de coberturas verificadas. Estimar tasas poblacionales solo con numeradores y denominadores compatibles; no establecer causalidad.
## 3. Fuentes y poblaciones
Cada combinación de fuente, versión, institución, periodo y territorio define una población de estudio. Mantener SAEH institucional y sectorial separados; evaluar transferencias de unidades. EDR se analiza aparte de defunciones hospitalarias. Un portal accesible no equivale a archivos íntegros.
## 4. Unidades de observación
Egreso hospitalario, atención de urgencias, registro de lesión y defunción registrada son unidades diferentes. Una persona puede generar múltiples eventos. Nunca sumar fuentes para contar individuos.
## 5. Definiciones operativas
Fijar tiempo de registro versus ocurrencia y territorio de residencia versus atención/ocurrencia por indicador. La ficha acompañará cada descarga. No inferir residencia desde CLUES. Conteo no equivale a incidencia.
## 6. Códigos CIE
Listas de inclusión y exclusión revisadas por clínico y versionadas con fecha, descripción y nivel de agregación. Selección por catálogo, no solo por prefijos. No mezclar revisiones sin tabla de comparabilidad validada. No se aprobó todavía una lista de enfermedades.
## 7. Diagnósticos múltiples
Conteo principal por afección principal para egresos y causa básica para mortalidad; análisis secundarios de menciones separados y rotulados. Una mención no es otro egreso. Sin diagnósticos secundarios no estimar comorbilidad.
## 8. Denominadores
INEGI/CONAPO son candidatos, aún no descargados ni auditados. Registrar versión de población, periodo de referencia, edad, sexo y territorio. No mezclar proyecciones de distintas conciliaciones. No calcular tasas de riesgo poblacional con cobertura parcial de atenciones.
## 9. Ajuste por edad
Estandarización directa con estratos coincidentes y pesos de una población estándar seleccionada por pregunta. Registrar sumatoria de pesos, grupos abiertos y edades desconocidas. No renormalizar estratos faltantes silenciosamente; bloquear o definir análisis alternativo. Evaluar ajuste indirecto solo con justificación.
## 10. Incertidumbre
Conteos administrativos no son muestras aleatorias por defecto. IC Poisson para tasas o binomial para proporciones solo si el modelo se justifica; no capturan subregistro ni errores sistemáticos. Ajuste directo requiere método específico documentado, por ejemplo gamma cuando corresponda. Tasas pequeñas mostrarán advertencia o supresión según política aprobada.
## 11. Tendencias
Mostrar conteos y cobertura antes de modelar. No interpolar años ausentes como observados. Cambio porcentual descriptivo no implica tendencia inferencial. Modelos segmentados/GAM: especificar familia, exposición, autocorrelación, sobredispersión y selección de puntos; validar residuos y sensibilidad.
## 12. Cambios de cobertura
Construir panel de unidades informantes y matriz institución/año. Comparar universo común y universo disponible. Rotular rupturas y versiones preliminares; no interpretar saltos institucionales como cambios de riesgo.
## 13. Faltantes
Separar desconocido, no aplicable, no captado y código inválido; mantener valor original. Publicar porcentaje por variable, territorio y año. No imputar desenlace o causa básica automáticamente. Imputación, si procede, requiere mecanismo supuesto y sensibilidad.
## 14. Duplicados
Hash de archivo impide ingestión repetida. Duplicados de filas solo se señalan: atenciones semejantes pueden ser eventos reales. Eliminación exige identificador y regla de fuente documentada con registro de antes/después. No hacer record linkage entre fuentes.
## 15. Catálogos
Versionar CIE, CLUES y divisiones territoriales con vigencia. Registrar cambios de municipio e institución, categorías retiradas y códigos desconocidos. No proyectar fronteras actuales retrospectivamente sin equivalencias justificadas.
## 16. Espacio
Geometrías oficiales con fecha, CRS, claves y licencia verificadas. Elegir vecindad contigüidad/distancia antes de análisis; islas y territorios sin vecinos tratados explícitamente. Moran global/local y LISA requieren variables apropiadas, permutaciones, semilla y control de multiplicidad. Evaluar sensibilidad a vecindad y suavizado; presentar incertidumbre. La versión local habilita mapas de frecuencias con geometría oficial de diciembre de 2025, validez geométrica y cruces de códigos comprobados; correspondencia histórica pendiente, explícita en el mapa. No se aplican redistribuciones retrospectivas. Véase docs/ATLAS_MUNICIPAL.md.
## 17. Sensibilidad
Repetir bajo diferentes restricciones de cobertura, faltantes, exclusiones, grupos de edad, estándares y definición territorial. Comparar definitivos/preliminares sin sustituir versiones en silencio; reportar revisión de resultados.
## 18. Comparaciones múltiples
Familia de hipótesis definida a priori. Elegir FDR o control familiar según objetivo; mostrar estimaciones e incertidumbre, no solo valores p. Exploración de muchos territorios se rotula exploratoria.
## 19. Modelos
Clustering: variables justificadas, escalamiento, pesos y estabilidad por remuestreo; K-means/jerárquico/HDBSCAN se evaluarán sin asumir superioridad. PCA/UMAP son exploratorios y sus distancias no prueban mecanismos. Separar entrenamiento/validación por tiempo o espacio para evitar fuga. Forecast con backtesting y baseline; anomalías no equivalen a brotes. Sin tiempo de seguimiento y censura válidos no usar supervivencia. Ningún modelo avanzado implementado en esta entrega.
## 20. Falacia ecológica
Asociaciones entre territorios no se trasladan a individuos. Atender composición demográfica, acceso, referencia hospitalaria, selección y mezcla de casos. No atribuir exposición individual a partir de residencia agregada.
## 21. Interpretación
No evaluar calidad hospitalaria mediante mortalidad cruda. No interpretar demanda asistencial como incidencia ni asociaciones como causalidad. La fidelidad de extracción no valida cobertura. Cada gráfico mostrará fuente, unidad, periodo y limitaciones, y enlace a este protocolo.
## 22. Protección y publicación
Solo agregados, nunca registros personales. Política inicial: no publicar estratos pequeños hasta revisión del riesgo; definir umbral institucional y supresión complementaria antes de tablas detalladas. Revisar reconstrucción por filtros y diferencias; redondeo no basta. El piloto contiene únicamente totales institucionales anuales públicos. Publicación exige revisión de licencia, calidad, privacidad, comparabilidad y autorización del usuario.

## Reporte y auditoría
Usar STROBE y RECORD como listas de transparencia, sin sustituir validación. Referencia primaria: Benchimol et al. (2015), [RECORD](https://doi.org/10.1371/journal.pmed.1001885). Mantener historial de correcciones, informe de calidad y fichas de indicador (docs/INDICADORES.md). Un resultado que falle controles permanece bloqueado.
