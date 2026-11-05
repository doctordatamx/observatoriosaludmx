# Auditoría de cifras

Mortalidad registrada DGIS/INEGI, año de registro 2024, residencia habitual. La columna frontend ejecuta la función que alimenta el tablero local. La referencia usa DuckDB sobre `data/silver/defunciones/2024/selected.parquet` y el catálogo etario 2024. La edición pública informa indisponibilidad y carece de cifras epidemiológicas visibles.

| Consulta | Frontend | SQL | Diferencia absoluta | Diferencia relativa | Agregado y SHA-256 | Resultado |
|---|---:|---:|---:|---:|---|---|
| Nacional, todos los filtros | 819,672 | 819,672 | 0 | 0.0000 % | `defunciones-2024.json.gz` · `c16328ac68ab533175a70e9e42c13411918a2c2cd7dc5718f3afefa74753d3e9` | Coincide |
| Nuevo León, entidad 19 | 36,807 | 36,807 | 0 | 0.0000 % | `municipal/defunciones-2024/19.json.gz` · `de5b30a5522ff348db92219e4b237207db694a14d8505bbf7f76c195c2e27ea9` | Coincide |
| Monterrey, municipio 19039 | 9,859 | 9,859 | 0 | 0.0000 % | `municipal/defunciones-2024/19.json.gz` · `de5b30a5522ff348db92219e4b237207db694a14d8505bbf7f76c195c2e27ea9` | Coincide |
| Mujeres, edad 65–69, E11, Nuevo León | 184 | 184 | 0 | 0.0000 % | `municipal/defunciones-2024/19.json.gz` · `de5b30a5522ff348db92219e4b237207db694a14d8505bbf7f76c195c2e27ea9` | Coincide |
| Nacional, mujeres de 65–69 años | 33,399 | 33,399 | 0 | 0.0000 % | `defunciones-2024.json.gz` · `c16328ac68ab533175a70e9e42c13411918a2c2cd7dc5718f3afefa74753d3e9` | Coincide |
| Nacional, mes de registro enero | 79,252 | 79,252 | 0 | 0.0000 % | `defunciones-2024.json.gz` · `c16328ac68ab533175a70e9e42c13411918a2c2cd7dc5718f3afefa74753d3e9` | Coincide |
| Nacional, diagnóstico E11 | 85,395 | 85,395 | 0 | 0.0000 % | `defunciones-2024.json.gz` · `c16328ac68ab533175a70e9e42c13411918a2c2cd7dc5718f3afefa74753d3e9` | Coincide |

Cada consulta compara además todas sus celdas de edad, sexo, causa, territorio y mes, incluidos los códigos desconocidos. Para la participación se valida que los conteos de las categorías exhaustivas sumen el denominador filtrado. Las tablas de categorías principales muestran un subconjunto y sus porcentajes redondeados pueden sumar menos de 100 %.

Regenerar desde la raíz con `python python/validation/audit_figures.py`. Este contraste de visualizaciones cubre mortalidad 2024. La auditoría Bronze–Silver–Gold y las pruebas existentes cubren los totales y consultas adicionales de otras series.
