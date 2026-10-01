# Installation

## Requirements

Docker Compose, OpenGist data directory and native metrics endpoint, Prometheus and Grafana.

## Procedure

Enable OpenGist native metrics. Copy .env.example to .env, set OPENGIST_DATA_DIR and OPENGIST_NETWORK, create secrets/metrics-token, then run docker compose up -d --build. Adapt examples/prometheus-scrape.yml and import the dashboard.

The files under [examples](https://github.com/willtheorangeguy/opengist-monitoring/tree/HEAD/examples) are reference configuration. Replace example addresses, token paths and bind addresses for your deployment.

Next, review [configuration](configuration.md) and [dashboard usage](usage.md).

## Compose lifecycle

From the repository root run `docker compose up -d --build` when Compose builds a local image, or `docker compose up -d` for prebuilt images. Inspect container output with `docker compose logs`. Keep credential files out of Git.

## Verify the installation

Check that the configured scrape target is healthy in Prometheus, then import the dashboard in Grafana and confirm its panels return data. Use the target and label names documented in [Getting started](getting-started.md).

## Upgrading

Update the dashboard JSON from this repository when you adopt a newer version. Update any exporter or monitored service using that project's upgrade instructions.

## Uninstalling

Remove the dashboard from Grafana and remove only the scrape or deployment entries you added for this project. Keep shared monitoring services that other dashboards use.
