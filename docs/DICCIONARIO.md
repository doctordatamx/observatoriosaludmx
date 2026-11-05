# Diccionario inicial

## Piloto: contrato comprobado
`year`: entero 2001–2007; `series`: urgencias o egresos; `count`: frecuencia entera no negativa; `source_id`: ssdf_603; `coverage`: SSDF; `geography`: Distrito Federal (ámbito institucional, no residencia individual). Una fila es un agregado anual, no una persona.
No hay edad, sexo, diagnóstico, municipio ni denominador. No crear estas variables a partir del tabulado.

## Contrato nacional propuesto, no nombres de campos confirmados
fecha_evento, fecha_registro, edad_valor, edad_unidad, sexo_original, diagnostico_principal, diagnosticos_secundarios, causa_basica, causa_externa, entidad_residencia, municipio_residencia, entidad_atencion, municipio_atencion, CLUES, institucion, condicion_egreso y estancia.
Cada adaptador requiere diccionario y catálogo del archivo/año. Si no existe variable, marcar no disponible; jamás sustituirla por otra geografía o código. Claves territoriales como cadenas con ceros iniciales, catálogo versionado y control de municipios nuevos. Edad en días/meses/años conserva unidad y códigos especiales. CIE se valida contra catálogo de revisión correspondiente; regex no acredita un código válido.
