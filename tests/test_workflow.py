import json
import re
import tempfile
import threading
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from career_copilot.cli import main
from career_copilot.server import create_server
from career_copilot.store import DEFAULT_PROFILE, Store, now


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = Store(self.temp.name)

    def add(self, url="https://example.com/jobs/finance-1", **kwargs):
        return self.store.application({"company": "Fictional Co", "role": "Finance Intern", "url": url, **kwargs})

    def test_profile_survives_new_session_and_init_does_not_reset_it(self):
        profile = self.store.profile()
        profile.update(name="Fictional Candidate", target_roles="Finance internships", timezone="America/Los_Angeles")
        profile["facts"] = [{"field": "education", "value": "Finance student", "source": "fictional test confirmation", "confirmed_at": "2026-01-01"}]
        self.store.save_profile(profile)
        main(["--data-dir", self.temp.name, "init"])
        loaded = Store(self.temp.name).profile()
        self.assertEqual(loaded, profile)
        self.assertTrue((Path(self.temp.name) / "MEMORY.md").exists())

    def test_submission_requires_receipt_and_rolls_back_on_failure(self):
        with self.assertRaisesRegex(ValueError, "evidence"):
            self.add(status="submitted")
        self.assertEqual(self.store.state()["applications"], [])
        self.assertEqual(self.store.events(), [])

    def test_uncertain_does_not_count_and_later_receipt_counts_once(self):
        app_id = self.add(status="uncertain")
        self.assertEqual(self.store.state()["summary"]["verified_total"], 0)
        self.store.application({"status": "submitted", "submission_evidence": "FICTIONAL TEST receipt", "submitted_at": now()}, app_id)
        self.store.application({"status": "assessment", "evidence": "FICTIONAL TEST invite"}, app_id)
        self.store.application({"status": "rejected", "evidence": "FICTIONAL TEST rejection"}, app_id)
        summary = self.store.state()["summary"]
        self.assertEqual(summary["verified_total"], 1)
        self.assertEqual(summary["verified_today"], 1)
        with self.assertRaisesRegex(ValueError, "immutable"):
            self.store.application({"submission_evidence": "replacement"}, app_id)

    def test_tracking_alias_is_duplicate_but_distinct_roles_stay_separate(self):
        self.add("https://EXAMPLE.com/jobs/finance-1/?utm_source=mail")
        with self.assertRaisesRegex(ValueError, "already tracked"):
            self.add("https://example.com/jobs/finance-1#application")
        self.add("https://example.com/jobs/finance-2")
        self.assertEqual(len(self.store.state()["applications"]), 2)

    def test_query_role_identifiers_are_preserved(self):
        self.add("https://example.com/apply?role=1&utm_source=mail")
        self.add("https://example.com/apply?role=2&utm_source=mail")
        self.assertEqual(len(self.store.state()["applications"]), 2)

    def test_two_assessments_are_independent(self):
        one, two = self.add(), self.add("https://example.com/jobs/finance-2")
        t1 = self.store.task({"title": "Record video for role 1", "application_id": one})
        self.store.task({"title": "Record video for role 2", "application_id": two})
        self.store.task({"done": True}, t1)
        state = self.store.state()
        self.assertEqual(state["summary"]["my_tasks"], 1)
        self.assertEqual(state["summary"]["verified_total"], 0)

    def test_submission_count_uses_candidate_timezone(self):
        profile = self.store.profile()
        profile["timezone"] = "America/Los_Angeles"
        self.store.save_profile(profile)
        # Find a completed UTC midnight within the past 3 days. In LA it is the preceding date.
        day = datetime.now(timezone.utc).replace(hour=0, minute=30, second=0, microsecond=0) - timedelta(days=2)
        self.add(status="submitted", submitted_at=day.isoformat(), submission_evidence="FICTIONAL TEST receipt")
        app = self.store.state()["applications"][0]
        self.assertEqual(app["submitted_at"], day.isoformat(timespec="seconds"))
        self.assertEqual(self.store.state()["summary"]["verified_today"], 0)

    def test_invalid_timezones_and_naive_times_are_rejected(self):
        with self.assertRaises(ValueError):
            self.store.save_profile({"timezone": "not/a-zone"})
        with self.assertRaises(ValueError):
            self.add(status="submitted", submitted_at="2026-01-01T12:00:00", submission_evidence="fictional")
        with self.assertRaises(ValueError):
            self.store.task({"title": "Test", "due": "2026-01-01T12:00:00"})

    def test_invalid_profile_fact_and_unknown_fields_rejected(self):
        with self.assertRaises(ValueError):
            self.store.save_profile({"facts": [{"field": "school", "value": "Fictional"}]})
        with self.assertRaises(ValueError):
            self.store.save_profile({"password": "do not store"})
        with self.assertRaises(ValueError):
            self.add(url="javascript:alert(1)")

    def test_unknown_foreign_key_task_does_not_save(self):
        with self.assertRaisesRegex(ValueError, "not found"):
            self.store.task({"title": "test", "application_id": 999})
        self.assertEqual(self.store.state()["tasks"], [])


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = Store(self.temp.name)
        self.server = create_server(self.store, 0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_port}"
        self.addCleanup(self.close)
        with urlopen(self.base) as r:
            html = r.read().decode()
            self.assertIn("Career Copilot", html)
        self.token = re.search(r'name="career-token" content="([^"]+)"', html)[1]

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.temp.cleanup()

    def request(self, path, data=None, origin=None, token=True):
        headers = {"Content-Type": "application/json"}
        if token:
            headers["X-Career-Token"] = self.token
        if origin:
            headers["Origin"] = origin
        req = Request(self.base + path, data=json.dumps(data).encode() if data is not None else None, headers=headers)
        return urlopen(req)

    def test_save_and_reload_profile_over_http(self):
        with self.request("/api/profile", {"name": "Fictional Finance Student"}, self.base) as r:
            self.assertEqual(r.status, 200)
        with self.request("/api/state") as r:
            self.assertEqual(json.load(r)["profile"]["name"], "Fictional Finance Student")

    def test_dashboard_edit_preserves_newer_codex_profile_updates(self):
        # Dashboard loads the old profile. Codex then confirms new information.
        with self.request("/api/state") as r:
            stale = json.load(r)["profile"]
        current = self.store.profile()
        current["connections"]["email"] = "Fictional candidate account verified"
        current["permissions"]["applications"] = "Prepare drafts only"
        current["facts"] = [{"field":"education", "value":"Finance", "source":"test", "confirmed_at":"2026-01-01"}]
        current["target_roles"] = "Treasury internships"
        self.store.save_profile(current)
        # Only the name differs from the dashboard snapshot, so only it is sent.
        edited = {**stale, "name": "New fictional name"}
        changes = {k:v for k,v in edited.items() if v != stale[k]}
        with self.request("/api/profile", changes, self.base) as r:
            self.assertEqual(r.status, 200)
        actual = self.store.profile()
        self.assertEqual(actual, {**current, "name":"New fictional name"})

    def test_cross_origin_and_missing_token_are_blocked(self):
        for origin, token in (("https://example.com", True), (self.base, False), (None, True)):
            with self.assertRaises(HTTPError) as e:
                self.request("/api/profile", {"name": "untrusted"}, origin, token)
            self.assertEqual(e.exception.code, 403)
            e.exception.close()
        with self.assertRaises(HTTPError) as e:
            self.request("/api/state", token=False)
        self.assertEqual(e.exception.code, 403)
        e.exception.close()
        self.assertEqual(self.store.profile()["name"], "")

    def test_server_cannot_serve_private_files_or_arbitrary_paths(self):
        for path in ("/private/career.sqlite3", "/../career.py", "/career.py"):
            with self.assertRaises(HTTPError) as e:
                urlopen(self.base + path)
            self.assertEqual(e.exception.code, 404)
            e.exception.close()

    def test_malformed_records_fail_without_mutation(self):
        for value in (None, [], {"name": None}, {"timezone": "unknown"}):
            # null is sent explicitly here rather than interpreted as a GET.
            req = Request(self.base+"/api/profile", data=json.dumps(value).encode(), headers={"Origin":self.base,"X-Career-Token":self.token,"Content-Type":"application/json"})
            with self.assertRaises(HTTPError) as e:
                urlopen(req)
            self.assertEqual(e.exception.code, 400)
            e.exception.close()
        self.assertEqual(self.store.profile(), DEFAULT_PROFILE)


if __name__ == "__main__":
    unittest.main()
