# OpenGist exporter and application dashboard

Portable monitoring bundle with example configuration. Replace example addresses and token paths for your installation; no live credentials are included.

## Requirements

The included exporter needs read-only access to OpenGist's SQLite database and bare repository directory, plus its native metrics endpoint.

## Dashboards

- `dashboards/opengist-application.json`

Import the JSON in Grafana using **Dashboards > New > Import**. Select your data source from the dashboard variable(s) at the top. Update the Prometheus job variables to match your `scrape_configs` job names; use the Instance selector when present. The dashboard's JSON is also suitable for file provisioning after you have selected or provisioned data source UIDs.

Expected default job labels:

- `opengist-application.json`: opengist

## Monitoring code

See the code and example configuration in this folder, if present. Keep API keys and metrics bearer tokens in local secret files or another secret manager; never commit them. Scrape examples use documentation addresses and must be edited for your network.

## Before publishing

Test against the application and Grafana versions you intend to support. Add a license you choose and check attribution for upstream components. No release or Grafana catalog upload has been performed.

## Run the exporter

Enable OpenGist's native metrics listener, copy `.env.example` to `.env`, set the real read-only OpenGist data directory and Docker network, create `secrets/metrics-token`, then run `docker compose up -d --build`. Set `BIND_IP` to a Prometheus-reachable address when needed. The public `/metrics` endpoint requires the bearer token; `/healthz` reports collection health. Run `python -m unittest discover -s tests -v` before release. Scrape it as job `opengist` or change the dashboard job variable.

A sample `scrape_configs` fragment is in `examples/prometheus-scrape.yml`; replace the example hosts and token paths.
