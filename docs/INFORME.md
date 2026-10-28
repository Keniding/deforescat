# Informe de viabilidad (iteración 1)

**Datos reales usados:** focos VIIRS S-NPP (archivo anual FIRMS por país, Bolivia 2021-2024, tipo 0 = vegetación, sin confianza baja) y clima diario NASA POWER (T2M_MAX, PRECTOTCORR, WS10M_MAX, RH2M). Open-Meteo devolvió 429 (límite diario) y la API con MAP_KEY de FIRMS no se usó (no hay clave); no hizo falta para el archivo anual.

**Diseño:** grilla de 0.5°, panel diario de las 100 celdas con más focos, etiqueta = hay foco en t+h. Entrenamiento 2021-2023, prueba 2024 (split temporal). Línea base de comparación = persistencia (hubo foco hoy).

| Horizonte | Prevalencia test | AP modelo | AUC modelo | AP persistencia |
|---|---|---|---|---|
| t+1 | 0.335 | 0.845 | 0.906 | 0.639 |
| t+2 | 0.335 | 0.778 | 0.873 | 0.568 |

**Lectura:** el modelo supera a la persistencia en ambos horizontes, así que predecir 1-2 días es viable en este escenario simplificado.

**Limitaciones (no sobreinterpretar):**
- Las 100 celdas se eligieron con focos de todos los años (incluido 2024), lo que sesga hacia celdas activas y eleva la prevalencia.
- 2024 fue un año excepcional de incendios en Bolivia; el test no es representativo de otros años.
- Sin validación espacial, sin NDVI, relieve ni comparación con EFFIS/GWIS; una sola semilla, sin intervalos de confianza.
- Es predicción de "foco detectado" (detección satelital), no de ignición.

**Siguiente:** elegir celdas solo con datos de entrenamiento, validación por años y por regiones, añadir NDVI (MODIS) y SRTM, y comparar con un índice de peligro tipo FWI.
