# Laboratorio de modelos · 0.5

El laboratorio utiliza agregados estatales y nacionales de archivos sin corte parcial, sin filtros de edad ni sexo. No produce tasas poblacionales, inferencias causales, predicciones, focos locales ni alertas. La conciliación externa y la comparabilidad de cobertura siguen pendientes.

- **Agrupamiento.** Entidades con al menos 1,000 registros de la fuente y año. Composición de las 12 categorías CIE-10 más frecuentes en ese universo y un resto que también incluye códigos inválidos. Raíz cuadrada de las proporciones y distancia euclídea, equivalente a Hellinger salvo un factor constante. Ward.D2 con cortes de 2, 3 y 4 grupos. Silueta media (solitarios puntúan 0) y Jaccard medio de pares coagrupados al retirar una categoría principal a la vez, sin renormalizar. Este último es un diagnóstico de sensibilidad, no una probabilidad.
- **Moran global.** Proporción de la causa entre todos los registros de cada entidad, con el mismo mínimo de 1,000 registros. Pesos binarios simétricos y diagonales nulas; contactos de bordes de geometrías originales de INEGI, diciembre 2025. Se comparan cualquier contacto y frontera de longitud positiva; sin tolerancia de ajuste. Se excluyen entidades aisladas y se exige variación y ocho entidades como mínimo. Se presenta el índice descriptivo sin pruebas de significación. Las fronteras de 2025 no reconstruyen ediciones históricas.
- **Meses fuera del rango.** Proporción nacional mensual (todos los códigos territoriales) frente a mediana, mínimo y máximo del mismo mes en años anteriores de la misma fuente. Solo meses con al menos 1,000 registros en cada archivo participante, tres antecedentes observados y mediana histórica de al menos 20 registros de la categoría. No se imputan meses sin registros del universo; cuando hay universo observado, una categoría sin registros se cuenta como cero. Sin corrección por cambios de cobertura, ni ajuste por multiplicidad: es una señal descriptiva de revisión.

Reconstrucción: ejecutar `python python/ingestion/build_lab_inputs.py` desde la raíz y después `Rscript R/epidemiology/build_lab.R`. Pruebas: `python tests/test_lab.py`. Se conserva SHA-256 de cada fuente y de la geometría en los metadatos. La aplicación lee resultados precalculados, sin microdatos.

Referencias: [Ward.D2 en R](https://search.r-project.org/R/refmans/stats/html/hclust.html), [fórmula de Moran](https://r-spatial.github.io/spdep/reference/moran.html).

En la instantánea usada, los dos criterios de vecindad produjeron las mismas 67 conexiones. No son dos comprobaciones espaciales independientes.

El dendrograma interactivo dibuja las uniones y alturas de la misma jerarquía Ward.D2 usada para los grupos. La línea de corte solo aparece cuando hay una separación estricta entre las alturas adyacentes. Se puede seleccionar una entidad por teclado, clic o menú.

**Dispersión MDS clásica.** Para la distancia euclídea de los perfiles transformados, las coordenadas principales se obtienen con la descomposición de la matriz centrada de perfiles (equivalente a MDS clásico). Se muestran los dos primeros ejes con escalas iguales, la fracción de variación retenida y la norma relativa del error de distancias. No es el estrés de Kruskal. Los grupos siguen siendo los de Ward en todas las dimensiones y la selección se comparte con el dendrograma.
