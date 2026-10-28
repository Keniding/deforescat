# Informe de viabilidad — Perú (iteración 2)

## Datos reales
- **Focos**: FIRMS VIIRS S-NPP, archivos anuales de Perú 2021-2025; tras filtros (vegetación, sin confianza baja) 355 506 detecciones.
- **Clima**: NASA POWER (MERRA-2) por celda, 2021-2025: T2M_MAX, PRECTOTCORR, WS10M_MAX, RH2M.
- **Datos nuevos**: archivo NRT de FIRMS (últimos 7 días, Sudamérica, recortado a Perú).
- Descartado: Open-Meteo (HTTP 429), API FIRMS por MAP_KEY (sin clave).

## Diseño
Celdas de 0.5°, 100 celdas más activas por cada pliegue (elegidas con datos previos al año de prueba; 115 celdas distintas en total). Pliegues: test 2023, 2024 y 2025, entrenando solo con años anteriores. Etiqueta = foco en t+1 / t+2. Métricas: AP (precisión promedio), AUC, precisión en el 10 % de celdas-día con mayor riesgo. Una semilla.

## Resultados (promedio de los 3 años de prueba)
| Horizonte | Variante | AP | AUC | Precisión top 10 % | AP persistencia | Prevalencia |
|---|---|---|---|---|---|---|
| t+1 | solo_focos | 0.599 | 0.816 | 0.717 | 0.421 | 0.237 |
| t+1 | **operacional** | **0.606** | 0.819 | 0.720 | 0.421 | 0.237 |
| t+1 | investigacion | 0.632 | 0.838 | 0.748 | 0.421 | 0.237 |
| t+2 | solo_focos | 0.533 | 0.787 | 0.643 | 0.358 | 0.237 |
| t+2 | **operacional** | **0.533** | 0.790 | 0.646 | 0.358 | 0.237 |
| t+2 | investigacion | 0.557 | 0.805 | 0.671 | 0.358 | 0.237 |

Por año (t+1, operacional): AP 0.645 (2023), 0.648 (2024), 0.523 (2025; prevalencia 0.207). Detalle completo en `docs/resultados.json`.

## Lectura
1. **Es posible** predecir presencia de focos a 1-2 días con ganancia clara sobre la persistencia y sobre el azar, en los tres años probados. El rendimiento baja de t+1 a t+2 y fue peor en 2025 (año con menos fuegos).
2. **Casi toda la capacidad viene del historial de focos y la estación.** Añadir clima del mismo día mejora ~+0.03 AP; el clima realmente disponible en tiempo real (t-7) aporta casi nada (+0.007 AP en t+1, 0 en t+2). Con estos datos, el clima observado y con retraso no es la palanca; un **pronóstico** meteorológico real podría serlo (no probado).
3. Cambio frente a la iteración 1: el AP de 2024 pasó de 0.684 a 0.675 (variante investigación) por la purga de etiquetas y por elegir celdas por pliegue; esperable.

## Prueba con datos nuevos (anécdota, no evidencia)
`predict.py --as-of 2026-10-26` y `--verify` contra el 2026-10-27: 10 de 100 celdas con foco; AP 0.181 (azar 0.10, persistencia 0.114). Es un solo día fuera de temporada con 6 días de historial NRT (las ventanas de 7 días quedaron incompletas); no permite concluir nada. La evaluación real requiere acumular pronósticos diarios.

## Limitaciones
- Se predice **detección satelital de foco** en celdas ya activas, no ignición ni zonas nuevas; por eso la prevalencia (~24 %) es alta. Resultados no extrapolables a todo Perú.
- Mismas celdas en train y test (sin validación espacial); una semilla; sin intervalos de confianza.
- Clima: observado (no pronóstico), resolución ~0.5° x 0.625°, retraso de ~7 días medido una vez (2026-10-28) y que puede variar.
- NRT vs archivo anual: procesamiento distinto y sin filtro `type`; el pronóstico de datos nuevos usa solo las 100 celdas del entrenamiento final.
- Nubes pueden ocultar fuegos; sin NDVI/relieve ni comparación con EFFIS/GWIS/FWI.

## Próximos pasos
1. Pronóstico meteorológico real (t+1/t+2) en lugar de clima observado con retraso.
2. Validación espacial (por regiones) y todas las celdas de Perú; intervalos de confianza con varias semillas.
3. NDVI MODIS, SRTM; comparación con FWI/EFFIS-GWIS.
4. Ejecutar `predict.py` a diario y acumular `--verify` para una evaluación en tiempo real.
