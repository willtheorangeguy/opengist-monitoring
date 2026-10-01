# API

OpenGist SQLite and bare Git repositories -> read-only exporter. OpenGist native /metrics -> filtered relay in the same process. Authenticated /metrics -> Prometheus -> Grafana.

## Interfaces

- `/metrics` requires the bearer token configured in the deployment. `/healthz` reports collector health.

## Prometheus scrape reference

See [examples/prometheus-scrape.yml](https://github.com/willtheorangeguy/opengist-monitoring/blob/HEAD/examples/prometheus-scrape.yml) for the target, job name and authorization settings.

## Collection sources

The exporter opens the mounted SQLite database in read-only query mode. It counts gists, files, likes, forks, languages, topics, users, SSH keys and access tokens. It walks the bare repository store for repository count and logical file bytes, and calls `git rev-list --all --count` for revision totals. Its native relay fetches OpenGist's `/metrics`, removes duplicate native gauges and aggregates request metrics without URL and Host labels.

`opengist_exporter_up` covers SQLite and Git collection; `opengist_native_metrics_up` covers the native metrics fetch. Check both when the dashboard's health panel changes. Metric names and HELP text are defined in [the exporter source](https://github.com/willtheorangeguy/opengist-monitoring/blob/HEAD/src/opengist_exporter.py).
