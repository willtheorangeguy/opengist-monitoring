#!/usr/bin/env python3
"""Read-only, low-cardinality OpenGist domain and native metrics exporter."""

from __future__ import annotations

import collections
import contextlib
import dataclasses
import hmac
import logging
import os
import re
import signal
import sqlite3
import subprocess
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Iterable


VERSION = "1.0.0"
VISIBILITIES = {0: "public", 1: "unlisted", 2: "private"}
INVALID_NATIVE_GAUGES = {"opengist_gists_total", "opengist_ssh_keys_total", "opengist_users_total"}
NATIVE_REQUEST_PREFIXES = (
    "opengist_request_duration_seconds",
    "opengist_request_size_bytes",
    "opengist_requests_total",
    "opengist_response_size_bytes",
)


@dataclasses.dataclass(frozen=True)
class Metric:
    name: str
    help: str
    metric_type: str
    samples: tuple[tuple[dict[str, str], float], ...]


def _escape_help(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\n", "\\n")


def _escape_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')


def render_metrics(metrics: Iterable[Metric]) -> str:
    lines: list[str] = []
    for metric in metrics:
        lines.append(f"# HELP {metric.name} {_escape_help(metric.help)}")
        lines.append(f"# TYPE {metric.name} {metric.metric_type}")
        for labels, value in metric.samples:
            label_text = ""
            if labels:
                rendered = ",".join(
                    f'{key}="{_escape_label(str(labels[key]))}"' for key in sorted(labels)
                )
                label_text = "{" + rendered + "}"
            lines.append(f"{metric.name}{label_text} {value:g}")
    return "\n".join(lines) + "\n"


def _single(value: float, labels: dict[str, str] | None = None) -> tuple[tuple[dict[str, str], float], ...]:
    return ((labels or {}, float(value)),)


def _rows(rows: Iterable[tuple[Any, ...]], names: tuple[str, ...]) -> tuple[tuple[dict[str, str], float], ...]:
    samples: list[tuple[dict[str, str], float]] = []
    for row in rows:
        labels = {name: str(value) for name, value in zip(names, row[:-1])}
        samples.append((labels, float(row[-1])))
    return tuple(samples)


def open_database(path: str) -> sqlite3.Connection:
    uri = Path(path).resolve().as_uri() + "?mode=ro"
    connection = sqlite3.connect(uri, uri=True, timeout=5.0)
    connection.execute("PRAGMA query_only = ON")
    return connection


def collect_database_metrics(path: str) -> list[Metric]:
    with contextlib.closing(open_database(path)) as database:
        database.execute("BEGIN")
        gist_total = database.execute("SELECT COUNT(*) FROM gists").fetchone()[0]
        gist_groups = database.execute(
            "SELECT private, COALESCE(archived, 0), COUNT(*) "
            "FROM gists GROUP BY private, COALESCE(archived, 0) ORDER BY private, COALESCE(archived, 0)"
        ).fetchall()
        visibility_samples = []
        for visibility, archived, count in gist_groups:
            visibility_name = VISIBILITIES.get(int(visibility), f"unknown_{visibility}")
            visibility_samples.append((
                {"visibility": visibility_name, "archived": "true" if archived else "false"},
                float(count),
            ))
        files, likes, forks = database.execute(
            "SELECT COALESCE(SUM(nb_files), 0), COALESCE(SUM(nb_likes), 0), "
            "COALESCE(SUM(nb_forks), 0) FROM gists"
        ).fetchone()
        languages = database.execute(
            "SELECT language, COUNT(DISTINCT gist_id) FROM gist_languages "
            "WHERE language <> '' GROUP BY language ORDER BY language"
        ).fetchall()
        topics = database.execute("SELECT COUNT(*) FROM gist_topics").fetchone()[0]
        distinct_topics = database.execute("SELECT COUNT(DISTINCT topic) FROM gist_topics").fetchone()[0]
        users = database.execute(
            "SELECT CASE WHEN COALESCE(is_admin, 0) <> 0 THEN 'true' ELSE 'false' END, COUNT(*) "
            "FROM users GROUP BY CASE WHEN COALESCE(is_admin, 0) <> 0 THEN 'true' ELSE 'false' END "
            "ORDER BY 1"
        ).fetchall()
        ssh_keys = database.execute("SELECT COUNT(*) FROM ssh_keys").fetchone()[0]
        access_tokens = database.execute("SELECT COUNT(*) FROM access_tokens").fetchone()[0]
        expiring = database.execute("SELECT COUNT(*) FROM gists WHERE expires_at > 0").fetchone()[0]
        queue_items = database.execute("SELECT COUNT(*) FROM gist_init_queues").fetchone()[0]
        last_update = database.execute("SELECT COALESCE(MAX(updated_at), 0) FROM gists").fetchone()[0]

    return [
        Metric("opengist_instance_gists", "Gists stored by OpenGist.", "gauge", _single(gist_total)),
        Metric(
            "opengist_instance_gists_by_state",
            "Gists by source-defined visibility and archived state.",
            "gauge",
            tuple(visibility_samples),
        ),
        Metric("opengist_instance_gist_files", "Sum of OpenGist's stored per-gist file counts.", "gauge", _single(files)),
        Metric("opengist_instance_gist_likes", "Sum of OpenGist's stored per-gist like counts.", "gauge", _single(likes)),
        Metric("opengist_instance_gist_forks", "Sum of OpenGist's stored per-gist fork counts.", "gauge", _single(forks)),
        Metric(
            "opengist_instance_gists_by_language",
            "Gists associated with each OpenGist-detected language; a multi-language gist can appear in multiple series.",
            "gauge",
            _rows(languages, ("language",)),
        ),
        Metric("opengist_instance_topic_assignments", "Gist-to-topic assignments stored by OpenGist.", "gauge", _single(topics)),
        Metric("opengist_instance_topics", "Distinct gist topics stored by OpenGist.", "gauge", _single(distinct_topics)),
        Metric("opengist_instance_users", "OpenGist users by administrator state.", "gauge", _rows(users, ("admin",))),
        Metric("opengist_instance_ssh_keys", "SSH keys stored by OpenGist.", "gauge", _single(ssh_keys)),
        Metric("opengist_instance_access_tokens", "Access tokens stored by OpenGist.", "gauge", _single(access_tokens)),
        Metric("opengist_instance_expiring_gists", "Gists with a nonzero expiry timestamp.", "gauge", _single(expiring)),
        Metric(
            "opengist_instance_gist_init_queue_items",
            "Items in OpenGist's durable gist initialization queue.",
            "gauge",
            _single(queue_items),
        ),
        Metric(
            "opengist_instance_last_content_update_timestamp_seconds",
            "Most recent gist update timestamp stored by OpenGist.",
            "gauge",
            _single(last_update),
        ),
    ]


def discover_repositories(root: str) -> list[Path]:
    repository_root = Path(root)
    if not repository_root.is_dir():
        raise RuntimeError(f"Repository root is not a directory: {root}")
    repositories: list[Path] = []
    for owner in repository_root.iterdir():
        if not owner.is_dir():
            continue
        for candidate in owner.iterdir():
            if candidate.is_dir() and (candidate / "HEAD").is_file() and (candidate / "objects").is_dir():
                repositories.append(candidate)
    return sorted(repositories)


def collect_repository_metrics(root: str) -> list[Metric]:
    repositories = discover_repositories(root)
    byte_total = 0
    revisions = 0
    for repository in repositories:
        for directory, _subdirectories, filenames in os.walk(repository):
            for filename in filenames:
                path = Path(directory) / filename
                try:
                    if path.is_file() and not path.is_symlink():
                        byte_total += path.stat().st_size
                except FileNotFoundError:
                    continue
        result = subprocess.run(
            ["git", "--git-dir", str(repository), "rev-list", "--all", "--count"],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        revisions += int(result.stdout.strip())
    return [
        Metric("opengist_instance_repositories", "Bare Git repositories found in OpenGist's repository store.", "gauge", _single(len(repositories))),
        Metric(
            "opengist_instance_repository_storage_bytes",
            "Logical bytes occupied by regular files in OpenGist's bare Git repository store.",
            "gauge",
            _single(byte_total),
        ),
        Metric("opengist_instance_revisions", "Sum of revisions reachable from all refs in OpenGist repositories.", "gauge", _single(revisions)),
    ]


def collect_domain_metrics(database_path: str, repository_root: str) -> list[Metric]:
    return collect_database_metrics(database_path) + collect_repository_metrics(repository_root)


def read_secret(path: str) -> str:
    with open(path, encoding="utf-8") as secret_file:
        value = secret_file.read().strip()
    if not value:
        raise RuntimeError(f"Secret file is empty: {path}")
    return value


class ExporterState:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.domain_text = ""
        self.up = 0.0
        self.failures = 0
        self.duration = 0.0
        self.last_success = 0.0
        self.last_error = "not collected yet"

    def record_success(self, domain_text: str, duration: float) -> None:
        with self.lock:
            self.domain_text = domain_text
            self.up = 1.0
            self.duration = duration
            self.last_success = time.time()
            self.last_error = ""

    def record_failure(self, duration: float, error: str) -> None:
        with self.lock:
            self.up = 0.0
            self.failures += 1
            self.duration = duration
            self.last_error = error

    def metrics(self) -> str:
        with self.lock:
            exporter_metrics = [
                Metric("opengist_exporter_build_info", "OpenGist exporter build information.", "gauge", _single(1, {"version": VERSION})),
                Metric("opengist_exporter_up", "Whether the most recent SQLite and Git collection succeeded.", "gauge", _single(self.up)),
                Metric("opengist_exporter_collection_failures_total", "SQLite or Git collection failures since exporter start.", "counter", _single(self.failures)),
                Metric("opengist_exporter_collection_duration_seconds", "Duration of the most recent SQLite and Git collection.", "gauge", _single(self.duration)),
                Metric("opengist_exporter_last_success_timestamp_seconds", "Unix timestamp of the most recent successful SQLite and Git collection.", "gauge", _single(self.last_success)),
            ]
            return render_metrics(exporter_metrics) + self.domain_text

    def health(self) -> tuple[bool, str]:
        with self.lock:
            return self.up == 1.0, self.last_error


class NativeRelay:
    def __init__(self, url: str, timeout: float) -> None:
        self.url = url
        self.timeout = timeout
        self.lock = threading.Lock()
        self.up = 0.0
        self.failures = 0
        self.duration = 0.0
        self.last_error = "not scraped yet"

    def fetch(self) -> str:
        started = time.monotonic()
        try:
            request = urllib.request.Request(self.url, headers={"User-Agent": f"opengist-exporter/{VERSION}"})
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                if response.status != 200:
                    raise RuntimeError(f"native metrics returned HTTP {response.status}")
                text = response.read().decode("utf-8")
            if "opengist_gists_total" not in text:
                raise RuntimeError("native metrics response did not contain OpenGist metrics")
            text = filter_native_metrics(text)
        except Exception as exc:
            with self.lock:
                self.up = 0.0
                self.failures += 1
                self.duration = time.monotonic() - started
                self.last_error = str(exc)
            logging.error("Native OpenGist metrics relay failed: %s", exc)
            return ""
        with self.lock:
            self.up = 1.0
            self.duration = time.monotonic() - started
            self.last_error = ""
        return text

    def metrics(self) -> str:
        with self.lock:
            return render_metrics([
                Metric("opengist_native_metrics_up", "Whether the most recent internal native metrics fetch succeeded.", "gauge", _single(self.up)),
                Metric("opengist_native_metrics_fetch_failures_total", "Internal native metrics fetch failures since exporter start.", "counter", _single(self.failures)),
                Metric("opengist_native_metrics_fetch_duration_seconds", "Duration of the most recent internal native metrics fetch.", "gauge", _single(self.duration)),
            ])

    def health(self) -> tuple[bool, str]:
        with self.lock:
            return self.up == 1.0, self.last_error


def strip_openmetrics_eof(text: str) -> str:
    lines = [line for line in text.splitlines() if line.strip() != "# EOF"]
    return "\n".join(lines).rstrip() + "\n"


def filter_native_metrics(text: str) -> str:
    """Remove invalid duplicates and aggregate unsafe URL/Host request labels."""
    kept: list[str] = []
    aggregates: collections.defaultdict[tuple[str, tuple[tuple[str, str], ...]], float] = collections.defaultdict(float)
    for line in strip_openmetrics_eof(text).splitlines():
        fields = line.split()
        metric_name = ""
        if len(fields) >= 3 and fields[0] in ("#",):
            metric_name = fields[2]
        elif fields:
            metric_name = fields[0].split("{", 1)[0]
        if metric_name in INVALID_NATIVE_GAUGES:
            continue
        if line.startswith("#"):
            kept.append(line)
            continue
        if metric_name.startswith(NATIVE_REQUEST_PREFIXES):
            match = re.match(r"^([A-Za-z_:][A-Za-z0-9_:]*)\{(.*)\}\s+([^\s]+)(?:\s+.*)?$", line)
            if not match:
                raise RuntimeError(f"Could not parse native request metric: {metric_name}")
            labels = {
                key: value.replace("\\\n", "\n").replace('\\"', '"').replace("\\\\", "\\")
                for key, value in re.findall(r'([A-Za-z_][A-Za-z0-9_]*)="((?:\\.|[^"\\])*)"', match.group(2))
            }
            safe_labels = {key: labels[key] for key in ("code", "method", "le") if key in labels}
            aggregates[(match.group(1), tuple(sorted(safe_labels.items())))] += float(match.group(3))
            continue
        kept.append(line)
    for (metric_name, labels), value in sorted(aggregates.items()):
        rendered = ",".join(f'{key}="{_escape_label(label)}"' for key, label in labels)
        kept.append(f"{metric_name}{{{rendered}}} {value:g}")
    return "\n".join(kept).rstrip() + "\n"


def collect_once(state: ExporterState, database_path: str, repository_root: str) -> None:
    started = time.monotonic()
    try:
        domain_text = render_metrics(collect_domain_metrics(database_path, repository_root))
    except Exception as exc:
        state.record_failure(time.monotonic() - started, str(exc))
        logging.error("OpenGist domain collection failed: %s", exc)
        return
    state.record_success(domain_text, time.monotonic() - started)


def make_handler(state: ExporterState, relay: NativeRelay, bearer_token: str):
    class Handler(BaseHTTPRequestHandler):
        server_version = "opengist-exporter/" + VERSION

        def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            path = urllib.parse.urlsplit(self.path).path
            if path == "/healthz":
                domain_ok, domain_error = state.health()
                native_ok, native_error = relay.health()
                healthy = domain_ok and native_ok
                errors = "; ".join(value for value in (domain_error, native_error) if value)
                payload = b"ok\n" if healthy else ("unhealthy: " + errors + "\n").encode()
                self.send_response(200 if healthy else 503)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return
            if path != "/metrics":
                self.send_error(404)
                return
            expected = "Bearer " + bearer_token
            if not hmac.compare_digest(self.headers.get("Authorization", ""), expected):
                payload = b"unauthorized\n"
                self.send_response(401)
                self.send_header("WWW-Authenticate", "Bearer")
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return
            native_text = relay.fetch()
            payload = (state.metrics() + relay.metrics() + native_text).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, fmt: str, *args: Any) -> None:
            logging.info("HTTP %s - %s", self.address_string(), fmt % args)

    return Handler


def main() -> None:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(message)s")
    database_path = os.getenv("OPENGIST_DATABASE_PATH", "/data/opengist.db")
    repository_root = os.getenv("OPENGIST_REPOSITORY_ROOT", "/data/repos")
    native_url = os.getenv("OPENGIST_NATIVE_METRICS_URL", "http://opengist:6158/metrics")
    bearer_token = read_secret(os.getenv("EXPORTER_BEARER_TOKEN_FILE", "/run/secrets/exporter_bearer_token"))
    poll_interval = max(30.0, float(os.getenv("POLL_INTERVAL_SECONDS", "300")))
    request_timeout = max(1.0, float(os.getenv("REQUEST_TIMEOUT_SECONDS", "5")))
    listen_address = os.getenv("LISTEN_ADDRESS", "0.0.0.0")
    listen_port = int(os.getenv("LISTEN_PORT", "9179"))

    state = ExporterState()
    relay = NativeRelay(native_url, request_timeout)
    collect_once(state, database_path, repository_root)
    relay.fetch()
    stop_event = threading.Event()

    def polling_loop() -> None:
        while not stop_event.wait(poll_interval):
            collect_once(state, database_path, repository_root)

    threading.Thread(target=polling_loop, name="opengist-poller", daemon=True).start()
    server = ThreadingHTTPServer((listen_address, listen_port), make_handler(state, relay, bearer_token))

    def stop_server(_signum: int, _frame: Any) -> None:
        stop_event.set()
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, stop_server)
    signal.signal(signal.SIGINT, stop_server)
    logging.info("Listening on %s:%d; polling read-only OpenGist data every %.0f seconds", listen_address, listen_port, poll_interval)
    try:
        server.serve_forever()
    finally:
        stop_event.set()
        server.server_close()


if __name__ == "__main__":
    main()
