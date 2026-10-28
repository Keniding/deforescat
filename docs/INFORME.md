# Informe de viabilidad — Perú (iteración 1)

## Datos reales
- **Focos**: FIRMS, VIIRS S-NPP, archivos anuales de Perú 2021-2024 (67 346 + 89 580 + 79 578 + 99 933 filas = 336 433). Filtro: `type==0` (vegetación presunta) → 327 006; sin `confidence=='l'` → 306 500.
- **Clima**: NASA POWER daily/point (MERRA-2) para el centro de cada una de 100 celdas, 2021-01-01 a 2024-12-31 (146 100 filas, sin faltantes): T2M_MAX, PRECTOTCORR, WS10M_MAX, RH2M.
- **Descartado**: Open-Meteo archive (HTTP 429, límite diario compartido); API FIRMS por MAP_KEY (no hay clave).

## Diseño experimental
- Celda 0.5°; las 100 celdas con más focos en **2021-2023**; panel diario 2021-2024 (1461 días x 100 celdas = 146 100 filas).
- Etiqueta: foco en la celda en t+h (se descartan los últimos h días sin etiqueta).
- Train: 2021-2023. Test: 2024 completo. Una semilla (0).
- Línea base: persistencia (`fires_1d>0`).

## Resultados (test 2024; AP = precisión promedio, AUC = ROC)
| Horizonte | Prevalencia | AP modelo | AUC modelo | AP persistencia |
|---|---|---|---|---|
| t+1 | 0.255 | 0.684 | 0.852 | 0.461 |
| t+2 | 0.255 | 0.606 | 0.822 | 0.391 |

Una predicción al azar tendría AP ≈ prevalencia (0.255). El modelo la supera claramente y también a la persistencia en ambos horizontes; el rendimiento baja de 1 a 2 días, como cabe esperar.

## Conclusión
En este escenario es **posible** predecir a 1-2 días la presencia de focos en celdas de 0.5° con ganancia real sobre la persistencia.

## Limitaciones
- Se predice **detección satelital de foco** en celdas ya activas, no ignición ni zonas nuevas; las 100 celdas son las más activas, por eso la prevalencia (25 %) es alta.
- Un solo año de test (2024, año de fuegos fuertes en la región) y una sola semilla: sin intervalos de confianza.
- Sin validación espacial (mismas celdas en train y test), sin NDVI/relieve/uso del suelo, sin comparación con EFFIS/GWIS ni con un índice tipo FWI.
- Clima de MERRA-2 (~0.5° x 0.625°), resolución gruesa; no se usó pronóstico, sino clima observado del propio día.
- Una detección VIIRS por pasada: nubes pueden ocultar fuegos.

## Próximos pasos
1. Validación cruzada por años (test 2022, 2023, 2024) y por regiones.
2. Añadir NDVI MODIS y SRTM; probar pronóstico meteorológico real para t+1/t+2.
3. Evaluar sobre todas las celdas de Perú, no solo las 100 más activas.
4. Comparar con FWI/EFFIS-GWIS y reportar intervalos de confianza.
