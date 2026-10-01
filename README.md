<h1 align="center">opengist-monitoring</h1>
<h4 align="center">A read-only SQLite and bare Git repository exporter combined with filtered native OpenGist metrics and a Grafana dashboard.</h4>

<div align="center">
  <img alt="GitHub Issues" src="https://img.shields.io/github/issues/willtheorangeguy/opengist-monitoring">
  <img alt="GitHub Pull Requests" src="https://img.shields.io/github/issues-pr/willtheorangeguy/opengist-monitoring">
  <img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-blue">
  <img alt="gitleaks workflow" src="https://github.com/willtheorangeguy/opengist-monitoring/actions/workflows/gitleaks.yml/badge.svg">
  <img alt="testing workflow" src="https://github.com/willtheorangeguy/opengist-monitoring/actions/workflows/testing.yml/badge.svg">
</div>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#documentation">Documentation</a> •
  <a href="#support">Support</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#license">License</a>
</p>

<!-- Screenshot: after adding opengist-monitoring/overview.png to .github/icons/, replace this comment with ![Dashboard overview](https://raw.githubusercontent.com/willtheorangeguy/.github/main/icons/opengist-monitoring/overview.png). -->

A read-only SQLite and bare Git repository exporter combined with filtered native OpenGist metrics and a Grafana dashboard.

## Key Features

- Read-only SQLite and bare Git repository inventory.
- Filtered OpenGist native metrics on the same scrape.
- Bearer protected exporter endpoint and health status.
- Application dashboard for content and request activity.

## Installation

Docker Compose, OpenGist data directory and native metrics endpoint, Prometheus and Grafana. Enable OpenGist native metrics. Copy .env.example to .env, set OPENGIST_DATA_DIR and OPENGIST_NETWORK, create secrets/metrics-token, then run docker compose up -d --build. Adapt examples/prometheus-scrape.yml and import the dashboard. See [installation](docs/installation.md) for more detail.

## Usage

Import [opengist-application.json](dashboards/opengist-application.json) in Grafana using **Dashboards → New → Import**. Choose the data source and match the dashboard variables to your monitoring labels. See [dashboard usage](docs/usage.md).

## Documentation

Full documentation lives in [docs/](docs/index.md): [Quickstart](docs/getting-started.md) · [Configuration](docs/configuration.md) · [Architecture](docs/architecture.md) · [Dashboard usage](docs/usage.md) · [Troubleshooting](docs/troubleshooting.md).

## Support

Open a [GitHub Discussion](https://github.com/willtheorangeguy/opengist-monitoring/discussions/new) or file an [issue](https://github.com/willtheorangeguy/opengist-monitoring/issues/new/choose).

## Contributing

Contributions welcome. See the org-wide [Contributing Guide](https://github.com/willtheorangeguy/.github/blob/main/CONTRIBUTING.md) and [Code of Conduct](https://github.com/willtheorangeguy/.github/blob/main/CODE_OF_CONDUCT.md).

## License

MIT — see [LICENSE.md](LICENSE.md).
