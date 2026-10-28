# Fuentes de datos y estado de verificación

| Fuente | Uso | Acceso | Estado |
|---|---|---|---|
| NASA FIRMS, archivo anual por país `https://firms.modaps.eosdis.nasa.gov/data/country/viirs-snpp/AAAA/viirs-snpp_AAAA_Peru.csv` | focos (etiquetas) | sin clave | **Verificado** (200; columnas: latitude, longitude, bright_ti4, scan, track, acq_date, acq_time, satellite, instrument, confidence, version, bright_ti5, frp, daynight, type) |
| NASA FIRMS API area (`/api/area/csv/MAP_KEY/SOURCE/w,s,e,n/DAY_RANGE/DATE`) | focos recientes | MAP_KEY gratis; 1-10 días; 5000 trans./10 min | Formato por documentación; **no probada** (`Invalid MAP_KEY` con clave de prueba) |
| NASA POWER `https://power.larc.nasa.gov/api/temporal/daily/point` | clima diario | sin clave | **Verificado** (200, datos reales) |
| Open-Meteo archive | clima | sin clave | Respondió 429 (límite diario) |
| NDVI MODIS, SRTM, EFFIS/GWIS | vegetación, relieve, comparación | — | No investigado aún |
