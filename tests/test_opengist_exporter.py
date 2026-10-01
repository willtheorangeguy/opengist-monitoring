import os
import pathlib
import sqlite3
import subprocess
import sys
import tempfile
import unittest


sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "src"))

from opengist_exporter import (  # noqa: E402
    ExporterState,
    collect_database_metrics,
    collect_repository_metrics,
    filter_native_metrics,
    render_metrics,
    strip_openmetrics_eof,
)


SCHEMA = """
CREATE TABLE gists (id INTEGER, private INTEGER, archived NUMERIC, nb_files INTEGER,
  nb_likes INTEGER, nb_forks INTEGER, expires_at INTEGER, updated_at INTEGER);
CREATE TABLE gist_languages (gist_id INTEGER, language TEXT);
CREATE TABLE gist_topics (gist_id INTEGER, topic TEXT);
CREATE TABLE users (id INTEGER, is_admin NUMERIC);
CREATE TABLE ssh_keys (id INTEGER);
CREATE TABLE access_tokens (id INTEGER);
CREATE TABLE gist_init_queues (gist_id INTEGER);
"""


class OpenGistExporterTests(unittest.TestCase):
    def test_database_metrics_use_only_stored_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "opengist.db"
            database = sqlite3.connect(path)
            database.executescript(SCHEMA)
            database.executemany(
                "INSERT INTO gists VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                [(1, 0, None, 2, 3, 0, 0, 100), (2, 1, 1, 4, 0, 1, 200, 300), (3, 2, 0, 1, 0, 0, 0, 250)],
            )
            database.executemany("INSERT INTO gist_languages VALUES (?, ?)", [(1, "Python"), (1, "Python"), (2, "Bash")])
            database.executemany("INSERT INTO gist_topics VALUES (?, ?)", [(1, "infra"), (2, "infra"), (2, "shell")])
            database.executemany("INSERT INTO users VALUES (?, ?)", [(1, 1), (2, 0)])
            database.execute("INSERT INTO ssh_keys VALUES (1)")
            database.execute("INSERT INTO access_tokens VALUES (1)")
            database.execute("INSERT INTO gist_init_queues VALUES (2)")
            database.commit()
            database.close()

            text = render_metrics(collect_database_metrics(str(path)))
            self.assertIn("opengist_instance_gists 3", text)
            self.assertIn('opengist_instance_gists_by_state{archived="false",visibility="public"} 1', text)
            self.assertIn('opengist_instance_gists_by_state{archived="true",visibility="unlisted"} 1', text)
            self.assertIn('opengist_instance_gists_by_language{language="Python"} 1', text)
            self.assertIn("opengist_instance_gist_files 7", text)
            self.assertIn("opengist_instance_expiring_gists 1", text)
            self.assertIn("opengist_instance_gist_init_queue_items 1", text)
            self.assertNotIn("issue", text)
            self.assertNotIn("pull_request", text)

    @unittest.skipIf(os.name == "nt" and not os.environ.get("PATH"), "git unavailable")
    def test_repository_metrics_count_bare_repositories_bytes_and_revisions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory) / "repos"
            repository = root / "owner" / "repo-id"
            repository.parent.mkdir(parents=True)
            subprocess.run(["git", "init", "--bare", str(repository)], check=True, capture_output=True)
            text = render_metrics(collect_repository_metrics(str(root)))
            self.assertIn("opengist_instance_repositories 1", text)
            self.assertIn("opengist_instance_revisions 0", text)
            storage_line = next(line for line in text.splitlines() if line.startswith("opengist_instance_repository_storage_bytes "))
            self.assertGreater(int(storage_line.split()[1]), 0)

    def test_failure_retains_last_successful_snapshot(self):
        state = ExporterState()
        state.record_success("opengist_instance_gists 60\n", 0.2)
        successful_timestamp = state.last_success
        state.record_failure(1.0, "database unavailable")
        text = state.metrics()
        self.assertIn("opengist_instance_gists 60", text)
        self.assertIn("opengist_exporter_up 0", text)
        self.assertIn("opengist_exporter_collection_failures_total 1", text)
        self.assertEqual(state.last_success, successful_timestamp)

    def test_native_relay_removes_openmetrics_eof(self):
        self.assertEqual(strip_openmetrics_eof("metric 1\n# EOF\n"), "metric 1\n")

    def test_native_relay_removes_invalid_duplicate_gauges(self):
        source = (
            "# HELP opengist_gists_total Total number of gists\n"
            "# TYPE opengist_gists_total gauge\n"
            "opengist_gists_total 60\n"
            "# HELP http_request_duration_seconds Request duration\n"
            "# TYPE http_request_duration_seconds histogram\n"
            "http_request_duration_seconds_count 2\n# EOF\n"
        )
        filtered = filter_native_metrics(source)
        self.assertNotIn("opengist_gists_total", filtered)
        self.assertIn("http_request_duration_seconds_count 2", filtered)

    def test_native_request_metrics_are_exactly_aggregated_without_url_or_host(self):
        source = (
            "# HELP opengist_requests_total Total HTTP requests\n"
            "# TYPE opengist_requests_total counter\n"
            'opengist_requests_total{code="200",host="example",method="GET",url="/alice/a"} 3\n'
            'opengist_requests_total{code="200",host="other",method="GET",url="/bob/b"} 4\n'
            'opengist_requests_total{code="404",host="example",method="GET",url="/missing"} 2\n'
            "# EOF\n"
        )
        filtered = filter_native_metrics(source)
        self.assertNotIn("url=", filtered)
        self.assertNotIn("host=", filtered)
        self.assertIn('opengist_requests_total{code="200",method="GET"} 7', filtered)
        self.assertIn('opengist_requests_total{code="404",method="GET"} 2', filtered)


if __name__ == "__main__":
    unittest.main()
    filter_native_metrics,
