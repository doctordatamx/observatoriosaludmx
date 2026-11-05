# Auditoría de consistencia entre tamaños de pantalla

Se comparó la misma URL local del Atlas y Panorama con Defunciones, 2024 y sin otros filtros en el navegador integrado. Se aplicaron tamaños de 1366 × 900 y 390 × 844 píxeles. Ambos mostraron **819,672** defunciones registradas y las mismas tres primeras filas en el Atlas.

| Clave | Registros a 1366 px | Registros a 390 px | Participación en ambos |
|---|---:|---:|---:|
| 15 | 99,701 | 99,701 | 12.2 % |
| 09 | 67,080 | 67,080 | 8.2 % |
| 30 | 61,341 | 61,341 | 7.5 % |

El documento no desbordó horizontalmente a ninguno de los tamaños. El gráfico mensual pasó de 12 etiquetas visibles a seis, con los mismos 12 puntos disponibles. Las gráficas de barras reducen el espacio y densidad de etiquetas según el ancho del contenedor. Los tooltips quedan confinados a la gráfica y conservan el conteo completo. El Atlas adapta su altura y sus controles táctiles. Las tablas conservan desplazamiento propio.

La comparación HTTP con distintos identificadores de navegador comprueba el recurso servido por el origen. La prueba visual usó un solo motor con dos tamaños. Quedan pendientes Chrome Android físico, Firefox nativo, navegación privada y diagnóstico de la caché del dispositivo original.
