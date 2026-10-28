# Fuentes de datos y estado de verificación

| Fuente | Uso | Acceso | Estado |
|---|---|---|---|
| NASA FIRMS area API (`/api/area/csv/MAP_KEY/SOURCE/w,s,e,n/DAY_RANGE/DATE`) | focos de calor VIIRS/MODIS (etiquetas) | MAP_KEY gratis; 1-10 días por llamada; 5000 trans./10 min | Formato confirmado por búsqueda; **no probado** (host bloqueado en la sesión) |
| Open-Meteo archive (ERA5) | clima diario | sin clave (uso no comercial) | Endpoint por confirmar; nombres de variables diarias **sin verificar** |
| NDVI (MODIS/Sentinel-2), SRTM, EFFIS/GWIS | vegetación, relieve, comparación | pendiente | No investigado aún |

## Bloqueo actual
La sesión solo alcanza PyPI. Hay que permitir en la red del entorno:
`firms.modaps.eosdis.nasa.gov`, `archive-api.open-meteo.com`, `open-meteo.com`, `effis.jrc.ec.europa.eu`.
También se necesita `FIRMS_MAP_KEY` como variable de entorno.
No se ha descargado ningún dato real ni se reportan métricas: sin datos no hay resultados de viabilidad.
