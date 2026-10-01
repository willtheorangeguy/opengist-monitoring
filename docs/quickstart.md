# opengist-monitoring — Quickstart

## Prerequisites

Docker Compose, OpenGist data directory and native metrics endpoint, Prometheus and Grafana.

## Set up

Enable OpenGist native metrics. Copy .env.example to .env, set OPENGIST_DATA_DIR and OPENGIST_NETWORK, create secrets/metrics-token, then run docker compose up -d --build. Adapt examples/prometheus-scrape.yml and import the dashboard.

The example Prometheus scrape job names are `opengist`.

## Confirm data

In Prometheus, check `up{job="opengist"}` and inspect a panel query in Grafana.
For missing data, see [troubleshooting](./troubleshooting.md).
