# deforescat — Predicción de focos de incendio a 1-2 días en Perú

Proyecto integrador: ¿se puede predecir, con datos satelitales públicos, en qué zonas de Perú habrá focos de calor al día siguiente (t+1) o a los dos días (t+2)?
Todo se calcula con **datos reales descargados** (ningún dato simulado). Los resultados están en [`docs/INFORME.md`](docs/INFORME.md) y las fuentes en [`docs/FUENTES.md`](docs/FUENTES.md).

## 1. Qué se hizo (resumen)
1. **Descarga** de focos de calor reales VIIRS S-NPP de Perú, 2021-2024 (NASA FIRMS, 336 433 detecciones; 306 500 tras el filtro).
2. **Cuadrícula** de 0.5° x 0.5° y conteo de focos por celda y día.
3. **Selección** de las 100 celdas con más focos **usando solo 2021-2023** (evita fuga de información hacia el test).
4. **Clima diario** real por celda desde NASA POWER (temperatura máxima, lluvia, viento máximo, humedad relativa).
5. **Variables** (features): focos acumulados en 1/3/7/14 días, día del año, clima del día, lluvia acumulada 7 y 30 días.
6. **Etiqueta**: 1 si la celda tiene al menos un foco en t+1 (o t+2), 0 si no.
7. **Modelo** LightGBM entrenado con 2021-2023 y evaluado en 2024 (partición temporal), comparado con la línea base de persistencia ("hubo foco hoy").

## 2. Qué se usó (versiones verificadas en PyPI al momento de crear el proyecto)
Python 3.13 gestionado con **uv 0.11.32**. Dependencias fijadas en `pyproject.toml`/`uv.lock`:
pandas 3.1.0, numpy 2.5.4, scikit-learn 1.9.1, lightgbm 4.7.0, requests 2.34.2, pyarrow 26.0.0; desarrollo: pytest 9.2.0, ruff 0.17.3; build: hatchling 1.33.0.

## 3. Cómo reproducirlo
```bash
uv sync                          # instala entorno exacto
uv run python download_data.py   # baja los 4 CSV de focos a data/raw/ (~20 MB c/u, sin clave)
uv run python run_pipeline.py    # descarga clima NASA POWER (cache en data/weather.parquet), entrena, evalúa
uv run pytest -q && uv run ruff check .
```
La salida queda en `docs/resultados.json`. Necesita acceso a `firms.modaps.eosdis.nasa.gov` y `power.larc.nasa.gov`. La primera ejecución tarda unos minutos por las 100 consultas de clima; luego usa la caché. `data/` no se versiona.

## 4. Estructura del código
| Archivo | Función |
|---|---|
| `download_data.py` | Descarga los CSV anuales de FIRMS (Perú). |
| `src/deforescat/dataset.py` | Filtra focos (`type==0` vegetación, sin confianza `l`), asigna celdas de 0.5°, arma el panel celda-día, features de focos y etiqueta t+h. |
| `src/deforescat/weather.py` | Cliente NASA POWER (diario, por punto; -999 → NaN). |
| `src/deforescat/model.py` | Partición temporal, LightGBM, métricas AP/AUC y línea base de persistencia. |
| `src/deforescat/firms.py` | Cliente de la API `area` de FIRMS (requiere `FIRMS_MAP_KEY`; **no se usó ni se probó**, queda para datos recientes). |
| `run_pipeline.py` | Orquesta todo para horizontes 1 y 2 días. |
| `tests/test_pipeline.py` | Prueba de que la etiqueta mira al futuro (datos sintéticos mínimos, solo para el código). |

## 5. Cómo seguir trabajándolo
- Cambiar zona: `download_data.py` (nombre de país) y `TOP_CELLS`, `START/END` en `run_pipeline.py`.
- Año de prueba: `TEST_START`. Probar otros años (p. ej. test 2023) para ver la variabilidad.
- Añadir NDVI (MODIS), relieve (SRTM), comparar con EFFIS/GWIS: pendientes, ver `docs/INFORME.md`.
- Datos recientes sin archivo anual: usar `firms.py` con una MAP_KEY gratuita de FIRMS.
