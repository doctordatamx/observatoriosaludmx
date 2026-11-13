# Observatorio Salud MX

**Datos abiertos para comprender la salud de México.**

Un proyecto de **Doctor Data MX**.

Observatorio Salud MX es una plataforma de código abierto para explorar registros de salud de México, estudiar su evolución temporal y comparar su distribución territorial. Integra herramientas de consulta, visualización y análisis descriptivo con una cadena de procesamiento reproducible.

Está dirigido a profesionales de salud, investigadores, docentes, estudiantes y personas interesadas en comprender las fuentes públicas de información sanitaria.

[Visitar el observatorio](https://doctordatamx.github.io/observatoriosaludmx/) · [Consultar la metodología](METODOLOGIA.md) · [Revisar las fuentes](docs/FUENTES_OFICIALES.md)

## Objetivos

- Facilitar la consulta de defunciones, egresos hospitalarios, atenciones de urgencias y registros de lesiones.
- Explorar diferencias por periodo, territorio, sexo, edad y categoría diagnóstica cuando la fuente lo permite.
- Hacer explícitos la cobertura, el corte y las limitaciones de cada conjunto.
- Permitir que cada resultado pueda rastrearse hasta su archivo de origen y sus transformaciones.
- Apoyar la investigación y la docencia mediante métodos y código revisables.

## Fuentes y cobertura

La fuente principal es la Dirección General de Información en Salud de la Secretaría de Salud. El proyecto utiliza también información de defunciones del INEGI y su cartografía oficial.

| Serie procesada | Periodos locales | Geografía de referencia |
|---|---|---|
| Defunciones registradas | 2020–2024 | Residencia habitual |
| Egresos institucionales | 2020–2026 | Residencia habitual |
| Urgencias | 2020–2026 | Residencia habitual |
| Lesiones | 2020–2026 | Ocurrencia del evento |
| Egresos sectoriales | 2020–2024 | Entidad de atención |

La colección local comprende 31 conjuntos anuales. Los archivos de 2026 tienen cortes parciales que se muestran en la consulta. El periodo disponible depende de cada fuente y de la versión procesada.

El INEGI publicó las defunciones definitivas de 2025 el 10 de noviembre de 2026. Su incorporación a la colección detallada está pendiente. [Publicación oficial EDR 2025](https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2026/edr/EDR2025-def_CP.pdf)

## Herramientas del observatorio

| Módulo | Qué permite explorar |
|---|---|
| Panorama | Conteos, distribución mensual, edad y sexo, diagnósticos y territorios |
| Egresos, urgencias y lesiones | Consultas de cada universo estadístico con filtros coordinados |
| Enfermedades | Perfiles por categoría CIE-10, evolución anual y comparación territorial |
| Atlas | Selección de entidades y municipios con claves y geometrías INEGI |
| Laboratorio | Agrupamiento de entidades, dispersión MDS, dendrograma y análisis espacial y temporal exploratorio |
| Fuentes y metodología | Procedencia, hashes, cobertura, métodos y límites de interpretación |

Las consultas detalladas permiten exportar tablas CSV, gráficas SVG y fichas mediante impresión o guardado como PDF. Los filtros se reflejan en la URL para compartir una consulta.

## Edición pública y ejecución local

El sitio de GitHub Pages publica series nacionales de las cuatro fuentes de 2020 a 2024. También muestra las defunciones por entidad de residencia y las principales causas de 2024 del INEGI.

La ejecución local utiliza la colección detallada y habilita los filtros demográficos y diagnósticos, el Atlas municipal y el Laboratorio. En la edición pública se puede conectar una copia de la carpeta `frontend/public` desde **Fuentes y trazabilidad** para usar esos mismos recursos en el dispositivo. La selección de carpeta depende de las capacidades del navegador.

La publicación de los cruces detallados continúa sujeta a revisión de cobertura, condiciones de reutilización y protección de celdas pequeñas.

## Recomendaciones para su uso

1. Comprueba la fuente, el año, el corte y la geografía antes de interpretar una cifra.
2. Compara periodos completos y revisa los cambios en cobertura y codificación.
3. Interpreta los conteos según su universo. Una fila puede representar una defunción, un egreso o una atención. Una persona puede generar varios eventos.
4. Conserva separados los universos institucionales y sectoriales para evitar sumar coberturas que puedan solaparse.
5. Consulta los códigos incluidos en una categoría antes de asignarle un significado clínico específico.
6. Usa los modelos como herramientas de exploración y contrasta los patrones con otras fuentes.
7. Al reutilizar resultados, cita la fuente original, el periodo y los filtros, además de describir las transformaciones del Observatorio.

### Buscar enfermedades

El buscador detallado reconoce códigos, descripciones y sinónimos seleccionados, con normalización de acentos y mayúsculas. Escribe el término y selecciona la categoría encontrada para aplicar el filtro.

- **Ca de colon** o **cáncer de colon** orientan a **C18**, tumor maligno del colon.
- **Hepatocarcinoma** orienta a **C22**, tumor maligno del hígado y de las vías biliares intrahepáticas. Esta categoría también incluye otros tumores y su conteo tiene un alcance más amplio.
- Los perfiles utilizan categorías CIE-10 de tres caracteres. La interpretación debe respetar ese nivel de detalle.

## Alcance metodológico

Las visualizaciones describen registros administrativos. La cobertura depende de las unidades informantes, el acceso a los servicios y los procesos de registro. Las comparaciones territoriales requieren considerar esos factores y el tamaño de la población.

Las tasas y los indicadores ajustados requieren denominadores oficiales compatibles. La conciliación con tabulados externos, la correspondencia territorial histórica y la revisión clínica de códigos siguen desarrollándose. Las diferencias temporales y asociaciones espaciales requieren evaluación adicional para una interpretación causal.

## Arquitectura reproducible

- **Bronze** conserva los archivos originales y metadatos de descarga con SHA-256.
- **Silver** proyecta campos originales a CSV y Parquet mediante Python y Arrow.
- **Gold** genera agregados e indicadores mediante R y data.table.
- **Frontend** presenta las consultas con React, TypeScript, Vite y ECharts.
- **Validación** utiliza Python, DuckDB, Node y R para contrastar cifras y operaciones.

Los archivos masivos y los agregados locales se excluyen del repositorio. Los catálogos y scripts permiten documentar y reproducir la preparación de datos.

## Ejecución local

Requisitos principales para la aplicación web, Node.js 24 y npm.

```powershell
cd frontend
npm ci
npm run dev -- --port 5173
```

Abrir [el servidor local](http://127.0.0.1:5173/). Los módulos detallados requieren disponer de los datos procesados en `frontend/public/data` y de las geometrías en `frontend/public/geo`.

Para reconstruir los datos se requieren Python 3.11 o posterior y R, con las dependencias declaradas en `pyproject.toml`, `renv.lock` y los archivos de requisitos.

```powershell
python -m pip install -e ".[data,test]"
python python/ingestion/download_recent.py
python python/ingestion/build_silver.py
Rscript R/epidemiology/build_gold.R
Rscript R/spatial/build_municipal.R
```

Las descargas verificadas conservan sus hashes y las versiones anteriores. Los fallos de red se registran para su revisión. Los detalles de instalación, catálogos y modelos se describen en la documentación.

## Pruebas y publicación

Desde la raíz del repositorio, con los datos locales disponibles.

```powershell
python -m unittest discover -s tests -v
python python/validation/audit_pipeline.py
Rscript tests/test_age.R
node --test frontend/tests/*.test.mjs
```

Para compilar la edición pública.

```powershell
cd frontend
npm run build:pages
cd ..
python pages/check_public.py
```

GitHub Actions comprueba la compilación y las pruebas que pueden ejecutarse sin archivos masivos. GitHub Pages sirve la raíz de la rama `gh-pages`. El despliegue utiliza el contenido validado de `frontend/dist-pages`.

## Documentación

- [Metodología](METODOLOGIA.md)
- [Arquitectura](ARQUITECTURA.md)
- [Diccionario](docs/DICCIONARIO.md)
- [Fuentes oficiales](docs/FUENTES_OFICIALES.md)
- [Calidad de datos](docs/CALIDAD_DATOS.md)
- [Perfiles de enfermedades](docs/PERFILES_ENFERMEDADES.md)
- [Atlas municipal](docs/ATLAS_MUNICIPAL.md)
- [Modelos avanzados](docs/MODELOS_AVANZADOS.md)
- [Auditoría técnica](docs/AUDITORIA_TECNICA.md)
- [Plan de evolución](ROADMAP.md)

## Licencia y atribución

El código y los documentos propios se distribuyen bajo la [licencia MIT](LICENSE). Los datos y la cartografía mantienen las condiciones de sus instituciones de origen. Las vistas publicadas incluyen atribución a la Secretaría de Salud / DGIS y al INEGI según corresponda.

**Doctor Data MX** desarrolla e interpreta los resultados del Observatorio como proyecto independiente.
