# opengist-monitoring — Dashboard Usage

Import the JSON files using **Grafana → Dashboards → New → Import**. Set the data source and variables listed in [configuration](./configuration.md).

## OpenGist Application Overview

Source: [opengist-application.json](../dashboards/opengist-application.json). Refresh: `30s`.

<!-- Screenshot: after adding opengist-application.png to .github/icons/opengist-monitoring/, replace this comment with ![OpenGist Application Overview](https://raw.githubusercontent.com/willtheorangeguy/.github/main/icons/opengist-monitoring/opengist-application.png). -->

### Panels

| Panel | Type | What it shows |
|---|---|---|
| Service Health | stat | Prometheus scrape, domain collector, and internal native relay must all be healthy. |
| Gists | stat | Exact gist rows stored by OpenGist. |
| Gist Files | stat | Sum of OpenGist's stored per-gist file counts. |
| Git Repositories | stat | Bare Git repositories found in OpenGist's repository store. |
| Reachable Revisions | stat | Sum of revisions reachable from every ref in all OpenGist repositories. |
| Repository Storage | stat | Logical bytes occupied by regular files in the bare Git store. |
| Initialization Queue | stat | The only durable background-work queue OpenGist stores. No task-progress value is invented. |
| Last Content Update Age | stat | Seconds since OpenGist's most recently stored gist update timestamp. |
| Gists by Visibility | bargauge | Visibility mapping comes directly from OpenGist 1.15.2: public, unlisted, and private. |
| Archived State | piechart | Gists grouped by OpenGist's stored archived boolean. |
| Gists by Detected Language | bargauge | OpenGist language associations. A multi-language gist appears once in each associated language, so bars need not sum to total gists. |
| Content and Access Inventory | bargauge | Directly stored aggregate values only; zero means OpenGist currently stores none. |
| Users by Administrator State | bargauge | User counts grouped by OpenGist's stored administrator flag. |
| Current Repository Ratios | bargauge | Direct current counts shown together without deriving unavailable repository types. |
| Gist and File History | timeseries | Prometheus history of directly collected gist and file totals. |
| Repository and Revision History | timeseries | Prometheus history of bare-repository count and reachable revisions. |
| Repository Storage History | timeseries | Logical bytes occupied by regular files in OpenGist's bare Git repository tree. |
| Visibility History | timeseries | Historical gist counts by directly stored visibility. |
| Language Association History | timeseries | Historical count of gists associated with each detected language. |
| HTTP Request Rate | timeseries | Exact OpenGist native request counter, aggregated before ingestion to remove URL and Host dimensions. |
| HTTP Requests by Status | timeseries | Request rate grouped by the native HTTP response code. |
| P95 HTTP Latency by Method | timeseries | 95th-percentile native request duration after exact aggregation by method and status. |
| HTTP Latency Quantiles | timeseries | Whole-instance latency quantiles calculated from OpenGist's native histogram. |
| Average HTTP Payload Size | timeseries | Average native request and response sizes. These are wire payload measurements, not repository content sizes. |
| Initialization Queue History | timeseries | The exact durable gist-initialization queue depth. OpenGist exposes no durable per-task progress. |
| Collector Duration | timeseries | Time required for the most recent read-only SQLite and Git collection. |
| Exporter Freshness | timeseries | Age of the most recent successful domain collection. |
| Collection Failures | timeseries | Cumulative domain-collection and native-relay failures since exporter start. |
| HTTP Error Share | timeseries | Share of request rate with a native HTTP 4xx or 5xx response code. |
| Exporter and Relay Health History | timeseries | Independent health signals for the read-only domain collector and Docker-internal native relay. |

<!-- Screenshot: add a focused panel or section image here after uploading it to .github/icons/opengist-monitoring/. -->

### Reading the results

The exporter reads its mounted data directory in read-only mode and aggregates native request metrics without URL and Host labels. Repository size is logical file bytes, not allocated filesystem blocks.

### Query reference

These expressions are copied from the dashboard JSON. Grafana substitutes the dashboard variables at runtime.

#### Service Health

```promql
min(up{job="${job_opengist}",instance="$instance"} or opengist_exporter_up{job="${job_opengist}",instance="$instance"} or opengist_native_metrics_up{job="${job_opengist}",instance="$instance"})
```

#### Gists

```promql
opengist_instance_gists{job="${job_opengist}",instance="$instance"}
```

#### Gist Files

```promql
opengist_instance_gist_files{job="${job_opengist}",instance="$instance"}
```

#### Git Repositories

```promql
opengist_instance_repositories{job="${job_opengist}",instance="$instance"}
```

#### Reachable Revisions

```promql
opengist_instance_revisions{job="${job_opengist}",instance="$instance"}
```

#### Repository Storage

```promql
opengist_instance_repository_storage_bytes{job="${job_opengist}",instance="$instance"}
```

#### Initialization Queue

```promql
opengist_instance_gist_init_queue_items{job="${job_opengist}",instance="$instance"}
```

#### Last Content Update Age

```promql
time() - opengist_instance_last_content_update_timestamp_seconds{job="${job_opengist}",instance="$instance"}
```

#### Gists by Visibility

```promql
sum by (visibility) (opengist_instance_gists_by_state{job="${job_opengist}",instance="$instance"})
```

#### Archived State

```promql
sum by (archived) (opengist_instance_gists_by_state{job="${job_opengist}",instance="$instance"})
```

#### Gists by Detected Language

```promql
opengist_instance_gists_by_language{job="${job_opengist}",instance="$instance"}
```

#### Content and Access Inventory

```promql
opengist_instance_gist_likes{job="${job_opengist}",instance="$instance"}
opengist_instance_gist_forks{job="${job_opengist}",instance="$instance"}
opengist_instance_topics{job="${job_opengist}",instance="$instance"}
opengist_instance_topic_assignments{job="${job_opengist}",instance="$instance"}
opengist_instance_ssh_keys{job="${job_opengist}",instance="$instance"}
opengist_instance_access_tokens{job="${job_opengist}",instance="$instance"}
opengist_instance_expiring_gists{job="${job_opengist}",instance="$instance"}
sum(opengist_instance_users{job="${job_opengist}",instance="$instance"})
```

#### Users by Administrator State

```promql
opengist_instance_users{job="${job_opengist}",instance="$instance"}
```

#### Current Repository Ratios

```promql
opengist_instance_gists{job="${job_opengist}",instance="$instance"}
opengist_instance_repositories{job="${job_opengist}",instance="$instance"}
opengist_instance_gist_files{job="${job_opengist}",instance="$instance"}
opengist_instance_revisions{job="${job_opengist}",instance="$instance"}
```

#### Gist and File History

```promql
opengist_instance_gists{job="${job_opengist}",instance="$instance"}
opengist_instance_gist_files{job="${job_opengist}",instance="$instance"}
```

#### Repository and Revision History

```promql
opengist_instance_repositories{job="${job_opengist}",instance="$instance"}
opengist_instance_revisions{job="${job_opengist}",instance="$instance"}
```

#### Repository Storage History

```promql
opengist_instance_repository_storage_bytes{job="${job_opengist}",instance="$instance"}
```

#### Visibility History

```promql
sum by (visibility) (opengist_instance_gists_by_state{job="${job_opengist}",instance="$instance"})
```

#### Language Association History

```promql
opengist_instance_gists_by_language{job="${job_opengist}",instance="$instance"}
```

#### HTTP Request Rate

```promql
sum(rate(opengist_requests_total{job="${job_opengist}",instance="$instance"}[$__rate_interval]))
```

#### HTTP Requests by Status

```promql
sum by (code) (rate(opengist_requests_total{job="${job_opengist}",instance="$instance"}[$__rate_interval]))
```

#### P95 HTTP Latency by Method

```promql
histogram_quantile(0.95, sum by (le, method) (rate(opengist_request_duration_seconds_bucket{job="${job_opengist}",instance="$instance"}[$__rate_interval])))
```

#### HTTP Latency Quantiles

```promql
histogram_quantile(0.50, sum by (le) (rate(opengist_request_duration_seconds_bucket{job="${job_opengist}",instance="$instance"}[$__rate_interval])))
histogram_quantile(0.95, sum by (le) (rate(opengist_request_duration_seconds_bucket{job="${job_opengist}",instance="$instance"}[$__rate_interval])))
histogram_quantile(0.99, sum by (le) (rate(opengist_request_duration_seconds_bucket{job="${job_opengist}",instance="$instance"}[$__rate_interval])))
```

#### Average HTTP Payload Size

```promql
sum(rate(opengist_request_size_bytes_sum{job="${job_opengist}",instance="$instance"}[$__rate_interval])) / clamp_min(sum(rate(opengist_request_size_bytes_count{job="${job_opengist}",instance="$instance"}[$__rate_interval])), 0.000001)
sum(rate(opengist_response_size_bytes_sum{job="${job_opengist}",instance="$instance"}[$__rate_interval])) / clamp_min(sum(rate(opengist_response_size_bytes_count{job="${job_opengist}",instance="$instance"}[$__rate_interval])), 0.000001)
```

#### Initialization Queue History

```promql
opengist_instance_gist_init_queue_items{job="${job_opengist}",instance="$instance"}
```

#### Collector Duration

```promql
opengist_exporter_collection_duration_seconds{job="${job_opengist}",instance="$instance"}
```

#### Exporter Freshness

```promql
time() - opengist_exporter_last_success_timestamp_seconds{job="${job_opengist}",instance="$instance"}
```

#### Collection Failures

```promql
opengist_exporter_collection_failures_total{job="${job_opengist}",instance="$instance"}
opengist_native_metrics_fetch_failures_total{job="${job_opengist}",instance="$instance"}
```

#### HTTP Error Share

```promql
100 * (sum(rate(opengist_requests_total{job="${job_opengist}",instance="$instance",code=~"4..|5.."}[$__rate_interval])) or vector(0)) / clamp_min(sum(rate(opengist_requests_total{job="${job_opengist}",instance="$instance"}[$__rate_interval])), 0.000001)
```

#### Exporter and Relay Health History

```promql
opengist_exporter_up{job="${job_opengist}",instance="$instance"}
opengist_native_metrics_up{job="${job_opengist}",instance="$instance"}
up{job="${job_opengist}",instance="$instance"}
```
