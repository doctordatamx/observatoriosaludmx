# Descarga local de fuentes DGIS desde 2020

Fecha de consulta: 4 de noviembre de 2026.

## Alcance
Originales de defunciones, egresos institucionales, egresos sectoriales, urgencias y lesiones. Selección por año indicado en las rutas oficiales, incluyendo diccionarios y catálogos compartidos cuyo periodo alcanza 2020 o posteriores. No se descarga una serie anterior solo por tener una fecha de actualización reciente.

El plan exacto está en `reports/download_plan_2020_onward.json`. Las versiones se conservan en las URLs completas, incluida su query. Para actualizar el inventario y descargar ejecutar desde la raíz:

```powershell
python python/ingestion/download_recent.py
```

Requiere acceso de red a DGIS. El script usa streaming y archivos temporales `.part`; mueve a nombre final solo después de validar longitud HTTP, cuando está disponible, y CRC de ZIP/XLSX. No descomprime bases completas ni modifica originales. Reutiliza descargas cuyo SHA-256 coincide con el manifiesto. Una nueva versión con URL diferente se vuelve a descargar; para conservación histórica de versiones futuras deberá añadirse partición por versión antes de actualizaciones que reemplacen un nombre existente.

## Productos
- `data/bronze/`: originales locales, excluidos de Git.
- `data/bronze/manifest.json`: trazabilidad, tamaño real, hash y estado de integridad.
- `config/*_files.json`: recursos encontrados por fuente.
- `reports/DESCARGAS_2020_A_FECHA.json`: resumen de la ejecución y errores, generado al terminar.

## Interpretación
No confundir validación de transporte e integridad del archivo con validación epidemiológica. Aún se requieren conteos de filas, esquemas, catálogos, faltantes, duplicación, cobertura y conciliación de totales. Metadatos compartidos 2023–2025 no se asumen compatibles con 2026. La disponibilidad del ZIP 2026 no demuestra un año completo.

Egresos institucionales y sectoriales se almacenan separados para evitar su suma indebida. Las licencias de origen siguen pendientes de revisión. Ningún archivo se publica ni se transfiere al frontend.

Se puede elegir el inicio con `python python/ingestion/download_recent.py --from-year 2020`; el valor por defecto es 2020.
