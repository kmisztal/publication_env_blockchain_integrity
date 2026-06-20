Pobieranie danych z OpenAQ

```bash
python -m experiments.openaq.cli download `
  --api-key-file experiments\openaq\API_KEY `
  --dataset-id openaq_mvp `
  --selection-mode capital-triangles `
  --city warsaw `
  --city berlin `
  --city paris `
  --city madrid `
  --datetime-from 2025-07-01 `
  --datetime-to 2025-12-31 `
  --locations-per-city 3 `
  --sensors-per-location 3 `
  --city-radius-meters 25000 `
  --min-location-distance-meters 5000 `
  --candidate-locations-per-city 50 `
  --measurements-per-sensor 5000 `
  --max-retries 6 `
  --retry-backoff-seconds 3 `
  --resume `
  --progress
```

Generowanie mapy

```bash
python -m experiments.openaq.cli map `
  --metadata-file experiments\data\raw\openaq_mvp_openaq_v3_download_metadata.json
```