# opengist-monitoring — Installation

## Requirements

Docker Compose, OpenGist data directory and native metrics endpoint, Prometheus and Grafana.

## Procedure

Enable OpenGist native metrics. Copy .env.example to .env, set OPENGIST_DATA_DIR and OPENGIST_NETWORK, create secrets/metrics-token, then run docker compose up -d --build. Adapt examples/prometheus-scrape.yml and import the dashboard.

The files under [examples](../examples) are reference configuration. Replace example addresses, token paths and bind addresses for your deployment.

Next, review [configuration](./configuration.md) and [dashboard usage](./usage.md).

## Compose lifecycle

From the repository root run `docker compose up -d --build` when Compose builds a local image, or `docker compose up -d` for prebuilt images. Inspect container output with `docker compose logs`. Keep credential files out of Git.
