# Fuentes de datos y estado de verificación

| Fuente | Uso | Acceso | Estado |
|---|---|---|---|
| NASA FIRMS, archivo anual por país `data/country/viirs-snpp/AAAA/viirs-snpp_AAAA_Peru.csv` (2021-2025; 2026 aún no existe: 404) | focos (etiquetas) | sin clave | **Verificado** |
| NASA FIRMS API area (`/api/area/csv/MAP_KEY/SOURCE/w,s,e,n/DAY_RANGE/DATE`) | focos recientes | MAP_KEY gratis; 1-10 días; 5000 trans./10 min | Formato por documentación; **no probada** (`Invalid MAP_KEY` con clave de prueba) |
| NASA POWER `https://power.larc.nasa.gov/api/temporal/daily/point` | clima diario | sin clave | **Verificado** (200, datos reales) |
| Open-Meteo archive | clima | sin clave | Respondió 429 (límite diario) |
| NDVI MODIS, SRTM, EFFIS/GWIS | vegetación, relieve, comparación | — | No investigado aún |

## Añadidos en la iteración 2
| Fuente | Uso | Estado |
|---|---|---|
| FIRMS NRT `data/active_fire/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_South_America_7d.csv` | datos nuevos (7 días) | **Verificado**; confianza en palabras, sin columna `type` |
| NASA POWER, latencia | clima reciente | Medido 2026-10-28: último día con datos = 2026-10-21 (~7 días) |
| Contorno de Perú (`johan/world.geo.json`, PER.geo.json) | solo dibujar mapas | Verificado; polígono muy simplificado |
