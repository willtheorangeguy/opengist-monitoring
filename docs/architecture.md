# opengist-monitoring — Architecture

OpenGist SQLite and bare Git repositories -> read-only exporter. OpenGist native /metrics -> filtered relay in the same process. Authenticated /metrics -> Prometheus -> Grafana.

## Components

- [compose.yml](../compose.yml): container deployment
- [dashboards/](../dashboards): Grafana dashboard definitions
- [examples/](../examples): deployment and scrape examples
- [src/](../src): collector or proxy implementation

## Data interpretation

The exporter reads its mounted data directory in read-only mode and aggregates native request metrics without URL and Host labels. Repository size is logical file bytes, not allocated filesystem blocks.
