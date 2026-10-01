# Troubleshooting

| Symptom | Check |
| --- | --- |
| Exporter /healthz returns 503 | inspect SQLite schema, mounted data path, Git repository root and native metrics URL. |
| /metrics returns 401 | check bearer credentials. |
| Repository count blank | confirm data directory contains owner/repository bare Git layout. |

## First checks

Check the selected Grafana data source and dashboard variables in [configuration](configuration.md). For Prometheus, inspect the target state and the exact job and instance labels before changing panel queries.
