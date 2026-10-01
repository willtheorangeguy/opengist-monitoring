# opengist-monitoring — Configuration

The exporter defaults to port 9179 and polls database and repositories every 300 seconds. BIND_IP defaults to 127.0.0.1. Set OPENGIST_NATIVE_METRICS_URL to the Docker-reachable native endpoint. config.example.yml lists process settings such as database path, repository root and request timeout.

## Dashboard variables

| Dashboard | Variable | Type | Default or query |
|---|---|---|---|
| `opengist-application.json` | `prometheus_ds` | datasource | `prometheus` |
| `opengist-application.json` | `job_opengist` | textbox | `opengist` |
| `opengist-application.json` | `instance` | query | `label_values(up{job="${job_opengist}"}, instance)` |

## Prometheus jobs

The supplied [scrape example](../examples/prometheus-scrape.yml) defines `opengist`. Copy its entries into your own scrape_configs and replace documentation hostnames. Job names can change if the dashboard variables change with them.

## Environment example

Start from [.env.example](../.env.example). Keep the resulting .env and all secret files outside version control.
