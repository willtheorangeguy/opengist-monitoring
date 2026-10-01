# OpenGist Monitoring

A read-only SQLite and bare Git repository exporter combined with filtered native OpenGist metrics and a Grafana dashboard.

## Key features

- Read-only SQLite and bare Git repository inventory.
- Filtered OpenGist native metrics on the same scrape.
- Bearer protected exporter endpoint and health status.
- Application dashboard for content and request activity.

## Quick start

Open Grafana and import `dashboards/opengist-application.json` through **Dashboards → New → Import**. Select the configured data source and match the dashboard variables to your labels. See [Getting started](getting-started.md) for prerequisites and setup.

## Where to next

<div class="wt-grid" markdown>

[:material-rocket-launch: **Getting started**<br>Set up the required integrations](getting-started.md){ .wt-card }

[:material-download: **Installation**<br>Install and connect the required services](installation.md){ .wt-card }

[:material-tune: **Configuration**<br>Review scrape examples and dashboard variables](configuration.md){ .wt-card }

[:material-sitemap: **Architecture**<br>Follow metrics from source to dashboard](architecture.md){ .wt-card }

[:material-view-dashboard: **Dashboard usage**<br>Import and use the dashboard](usage.md){ .wt-card }

</div>

## Support

{{ support() }}
