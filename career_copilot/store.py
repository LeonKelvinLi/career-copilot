import copy
import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

ROOT = Path(__file__).resolve().parents[1]
STATUSES = ("discovered", "draft", "blocked", "uncertain", "submitted", "assessment", "interview", "offer", "rejected", "withdrawn")
DEFAULT_PROFILE = {
    "name": "", "email": "", "linkedin": "", "github": "", "portfolio": "",
    "location": "", "timezone": "UTC", "target_roles": "", "target_locations": "",
    "remote_preference": "", "salary_preference": "", "resume_paths": "",
    "experience_and_education": "", "languages": "", "work_authorization": "",
    "availability": "", "writing_style": "Natural voice for a finance student in their mid-twenties. Simple words, short sentences, real details. No corporate filler, generic AI phrases, or inflated claims.",
    "excluded_companies": "", "daily_target": 0,
    "permissions": {"applications": "Not yet discussed", "profile_edits": "Not yet discussed",
                    "email": "Draft only; ask before sending", "schedule": "Not requested"},
    "facts": [], "connections": {},
}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def text(value, field, limit=30000):
    if not isinstance(value, str) or len(value) > limit:
        raise ValueError(f"{field} must be text under {limit} characters")
    return value.strip()


def web_url(value):
    value = text(value, "URL", 4000)
    try:
        u = urlsplit(value)
        if u.scheme != "https" or not u.hostname or u.username or u.password or u.port not in (None, 443):
            raise ValueError
    except ValueError:
        raise ValueError("Use an HTTPS URL without credentials or a custom port") from None
    return value


def canonical_url(value):
    u = urlsplit(web_url(value))
    # Preserve role/application IDs and all unknown query parameters.
    query = [(k, v) for k, v in parse_qsl(u.query, keep_blank_values=True)
             if not k.lower().startswith("utm_") and k.lower() not in ("gclid", "fbclid")]
    return urlunsplit((u.scheme, u.netloc.lower(), u.path.rstrip("/") or "/", urlencode(sorted(query)), ""))


def timestamp(value):
    value = text(value, "timestamp", 100)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError
        return parsed.astimezone(timezone.utc).isoformat(timespec="seconds")
    except ValueError:
        raise ValueError("Use an ISO timestamp with timezone, for example 2026-10-29T14:00:00-07:00") from None


def validate_profile(raw):
    if not isinstance(raw, dict) or set(raw) - set(DEFAULT_PROFILE):
        raise ValueError("Profile must be an object with known fields; see profile.example.json")
    p = copy.deepcopy(DEFAULT_PROFILE)
    p.update(raw)
    for k, default in DEFAULT_PROFILE.items():
        if isinstance(default, str):
            p[k] = text(p[k], k)
    for k in ("linkedin", "github", "portfolio"):
        if p[k]:
            web_url(p[k])
    try:
        ZoneInfo(p["timezone"])
    except (ZoneInfoNotFoundError, ValueError):
        raise ValueError("Unknown IANA timezone; use e.g. America/Sao_Paulo or Europe/London") from None
    if type(p["daily_target"]) is not int or not 0 <= p["daily_target"] <= 100:
        raise ValueError("daily_target must be an integer from 0 to 100; 0 means not set")
    if not isinstance(p["permissions"], dict) or set(p["permissions"]) - set(DEFAULT_PROFILE["permissions"]):
        raise ValueError("Unknown permissions field")
    p["permissions"] = {**DEFAULT_PROFILE["permissions"], **p["permissions"]}
    for k, v in p["permissions"].items():
        p["permissions"][k] = text(v, k)
    if not isinstance(p["facts"], list) or not isinstance(p["connections"], dict):
        raise ValueError("facts must be a list and connections an object")
    for fact in p["facts"]:
        if not isinstance(fact, dict) or set(fact) != {"field", "value", "source", "confirmed_at"}:
            raise ValueError("Each fact needs field, value, source and confirmed_at")
        for k, v in fact.items():
            text(v, k)
        try:
            date.fromisoformat(fact["confirmed_at"])
        except ValueError:
            raise ValueError("fact confirmed_at must be YYYY-MM-DD") from None
    for k, v in p["connections"].items():
        text(k, "connection name")
        text(v, "connection description")
    return p


class Store:
    def __init__(self, directory=None):
        self.directory = Path(directory) if directory else ROOT / "private"
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.db = self.directory / "career.sqlite3"
        with self.connect() as c:
            c.executescript("""
            CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS applications(
              id INTEGER PRIMARY KEY, company TEXT NOT NULL, role TEXT NOT NULL,
              url TEXT NOT NULL, canonical_url TEXT NOT NULL UNIQUE, status TEXT NOT NULL,
              notes TEXT NOT NULL DEFAULT '', evidence TEXT NOT NULL DEFAULT '',
              submitted_at TEXT NOT NULL DEFAULT '', submission_evidence TEXT NOT NULL DEFAULT '',
              created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS tasks(
              id INTEGER PRIMARY KEY, application_id INTEGER REFERENCES applications(id),
              title TEXT NOT NULL, owner TEXT NOT NULL, due TEXT NOT NULL DEFAULT '',
              notes TEXT NOT NULL DEFAULT '', done INTEGER NOT NULL DEFAULT 0,
              created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS events(
              id INTEGER PRIMARY KEY, kind TEXT NOT NULL, item_id INTEGER,
              details TEXT NOT NULL, created_at TEXT NOT NULL);
            """)
        os.chmod(self.db, 0o600)

    @contextmanager
    def connect(self):
        c = sqlite3.connect(self.db, timeout=15)
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA foreign_keys = ON")
        try:
            with c:
                yield c
        finally:
            c.close()

    def event(self, c, kind, item_id, details):
        c.execute("INSERT INTO events(kind,item_id,details,created_at) VALUES(?,?,?,?)",
                  (kind, item_id, json.dumps(details, ensure_ascii=False), now()))

    def profile(self):
        with self.connect() as c:
            row = c.execute("SELECT value FROM meta WHERE key='profile'").fetchone()
        return json.loads(row[0]) if row else copy.deepcopy(DEFAULT_PROFILE)

    def save_profile(self, raw):
        p = validate_profile(raw)
        with self.connect() as c:
            c.execute("INSERT INTO meta VALUES('profile',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                      (json.dumps(p, ensure_ascii=False),))
            self.event(c, "profile_updated", None, {"fields": list(raw)})
        return p

    def patch_profile(self, raw):
        # The dashboard edits only visible fields. Facts, permissions and account
        # notes may have changed in Codex since the page was opened.
        allowed = set(DEFAULT_PROFILE) - {"facts", "permissions", "connections"}
        if not isinstance(raw, dict) or set(raw) - allowed:
            raise ValueError("Dashboard profile changes must contain editable profile fields")
        with self.connect() as c:
            c.execute("BEGIN IMMEDIATE")
            row = c.execute("SELECT value FROM meta WHERE key='profile'").fetchone()
            current = json.loads(row[0]) if row else copy.deepcopy(DEFAULT_PROFILE)
            p = validate_profile({**current, **raw})
            c.execute("INSERT INTO meta VALUES('profile',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                      (json.dumps(p, ensure_ascii=False),))
            self.event(c, "profile_updated", None, {"fields": list(raw)})
        return p

    def application(self, data, item_id=None):
        allowed = {"company", "role", "url", "status", "notes", "evidence", "submitted_at", "submission_evidence"}
        if not isinstance(data, dict) or set(data) - allowed:
            raise ValueError("Unknown application fields")
        with self.connect() as c:
            old = None if item_id is None else c.execute("SELECT * FROM applications WHERE id=?", (item_id,)).fetchone()
            if item_id is not None and not old:
                raise ValueError("Application not found")
            p = {k: old[k] if old else "" for k in allowed}
            p["status"] = old["status"] if old else "discovered"
            p.update(data)
            p = {k: text(v, k) for k, v in p.items()}
            if not p["company"] or not p["role"]:
                raise ValueError("Company and role are required")
            if p["status"] not in STATUSES:
                raise ValueError("Unknown application status")
            url = canonical_url(p["url"])
            if p["status"] == "submitted" and not p["submitted_at"]:
                p["submitted_at"] = now()
            if bool(p["submitted_at"]) != bool(p["submission_evidence"]):
                raise ValueError("Verified submission requires both submitted_at and submission_evidence")
            if p["status"] == "submitted" and not p["submission_evidence"]:
                raise ValueError("A submitted application needs receipt/portal evidence")
            if p["submitted_at"]:
                p["submitted_at"] = timestamp(p["submitted_at"])
                if datetime.fromisoformat(p["submitted_at"]) > datetime.now(timezone.utc):
                    raise ValueError("Submission date cannot be in the future")
            if old and old["submitted_at"] and (p["submitted_at"], p["submission_evidence"]) != (old["submitted_at"], old["submission_evidence"]):
                raise ValueError("Original verified receipt/date are immutable; add corrections in notes/evidence")
            p["canonical_url"], p["updated_at"] = url, now()
            try:
                if old:
                    c.execute("UPDATE applications SET " + ",".join(f"{k}=?" for k in p) + " WHERE id=?", (*p.values(), item_id))
                else:
                    p["created_at"] = now()
                    cur = c.execute("INSERT INTO applications (" + ",".join(p) + ") VALUES (" + ",".join("?" for _ in p) + ")", tuple(p.values()))
                    item_id = cur.lastrowid
            except sqlite3.IntegrityError:
                raise ValueError("This role URL is already tracked; update it instead of adding a duplicate") from None
            self.event(c, "application_updated" if old else "application_added", item_id, p)
        return item_id

    def task(self, data, item_id=None):
        allowed = {"application_id", "title", "owner", "due", "notes", "done"}
        if not isinstance(data, dict) or set(data) - allowed:
            raise ValueError("Unknown task fields")
        with self.connect() as c:
            old = None if item_id is None else c.execute("SELECT * FROM tasks WHERE id=?", (item_id,)).fetchone()
            if item_id is not None and not old:
                raise ValueError("Task not found")
            p = dict(old) if old else {"application_id": None, "title": "", "owner": "me", "due": "", "notes": "", "done": 0, "created_at": now()}
            p.pop("id", None)
            p.update(data)
            for k in ("title", "owner", "due", "notes"):
                p[k] = text(p[k], k)
            if not p["title"] or p["owner"] not in ("me", "assistant", "employer"):
                raise ValueError("Task needs a title and owner: me, assistant or employer")
            if p["done"] not in (0, 1, False, True):
                raise ValueError("done must be true or false")
            p["done"] = int(p["done"])
            if p["application_id"] is not None:
                if type(p["application_id"]) is not int or not c.execute("SELECT 1 FROM applications WHERE id=?", (p["application_id"],)).fetchone():
                    raise ValueError("Linked application not found")
            if p["due"]:
                if len(p["due"]) == 10:
                    try:
                        date.fromisoformat(p["due"])
                    except ValueError:
                        raise ValueError("Date must be YYYY-MM-DD") from None
                else:
                    p["due"] = timestamp(p["due"])
            p["updated_at"] = now()
            if old:
                c.execute("UPDATE tasks SET " + ",".join(f"{k}=?" for k in p) + " WHERE id=?", (*p.values(), item_id))
            else:
                cur = c.execute("INSERT INTO tasks (" + ",".join(p) + ") VALUES (" + ",".join("?" for _ in p) + ")", tuple(p.values()))
                item_id = cur.lastrowid
            self.event(c, "task_updated" if old else "task_added", item_id, p)
        return item_id

    def state(self):
        p = self.profile()
        with self.connect() as c:
            apps = [dict(r) for r in c.execute("SELECT * FROM applications ORDER BY updated_at DESC,id DESC")]
            tasks = [dict(r) for r in c.execute("SELECT * FROM tasks ORDER BY done,due='',due,id")]
        today = datetime.now(ZoneInfo(p["timezone"])).date()
        today_count = sum(bool(a["submitted_at"]) and datetime.fromisoformat(a["submitted_at"]).astimezone(ZoneInfo(p["timezone"])).date() == today for a in apps)
        return {"profile": p, "applications": apps, "tasks": tasks, "statuses": STATUSES,
                "summary": {"today": str(today), "timezone": p["timezone"], "verified_today": today_count,
                            "verified_total": sum(bool(a["submitted_at"]) for a in apps),
                            "open_tasks": sum(not t["done"] for t in tasks),
                            "my_tasks": sum(not t["done"] and t["owner"] == "me" for t in tasks)}}

    def events(self):
        with self.connect() as c:
            return [dict(r) for r in c.execute("SELECT * FROM events ORDER BY id DESC LIMIT 100")]
