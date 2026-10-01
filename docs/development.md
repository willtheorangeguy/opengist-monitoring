# Development guide

The implementation and dashboard definitions are in the repository root. OpenGist SQLite and bare Git repositories -> read-only exporter. OpenGist native /metrics -> filtered relay in the same process. Authenticated /metrics -> Prometheus -> Grafana.

## Local checks

The repository CI workflow runs `python -m unittest discover -s tests -v`. Run it from the repository root after changing the relevant source or dashboard JSON.

When editing dashboards, export the final JSON from Grafana and keep data source variables, job names and panel descriptions in sync with [configuration](configuration.md).

The service lives in [src/opengist_exporter.py](https://github.com/willtheorangeguy/opengist-monitoring/blob/HEAD/src/opengist_exporter.py). Database reads use SQLite query-only mode; repository totals use filesystem traversal and Git commands; native metrics pass through a separate filter. [Dockerfile](https://github.com/willtheorangeguy/opengist-monitoring/tree/HEAD/Dockerfile) installs Git, and [compose.yml](https://github.com/willtheorangeguy/opengist-monitoring/blob/HEAD/compose.yml) mounts the OpenGist data read-only. Update [tests/](https://github.com/willtheorangeguy/opengist-monitoring/tree/HEAD/tests) when changing schema queries, native filtering or health behavior.
