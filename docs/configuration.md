# Configuration

## Precedence

This repository combines dashboard defaults with settings for external services. It defines no shared command-line, environment variable and configuration-file override order; each external service resolves its own settings.

## Integration settings

The exporter defaults to port 9179 and polls database and repositories every 300 seconds. BIND_IP defaults to 127.0.0.1. Set OPENGIST_NATIVE_METRICS_URL to the Docker-reachable native endpoint. config.example.yml lists process settings such as database path, repository root and request timeout.

## Dashboard variables

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `opengist-application.json / prometheus_ds` | datasource | `prometheus` | Grafana data source selected by the dashboard. |
| `opengist-application.json / job_opengist` | textbox | `opengist` | Dashboard variable whose value selects a scrape job, instance or endpoint. |
| `opengist-application.json / instance` | query | `label_values(up{job="${job_opengist}"}, instance)` | Queries the data source for available values. |

## Prometheus jobs

The supplied [scrape example](https://github.com/willtheorangeguy/opengist-monitoring/blob/HEAD/examples/prometheus-scrape.yml) defines `opengist`. Copy its entries into your own scrape_configs and replace documentation hostnames. Job names can change if the dashboard variables change with them.

## Environment example

Start from [.env.example](https://github.com/willtheorangeguy/opengist-monitoring/blob/HEAD/.env.example). Keep the resulting .env and all secret files outside version control.

## Examples

The complete scrape job examples are in [`examples/prometheus-scrape.yml`](https://github.com/willtheorangeguy/opengist-monitoring/blob/HEAD/examples/prometheus-scrape.yml). Copy the relevant job into your Prometheus configuration and replace the example targets.
