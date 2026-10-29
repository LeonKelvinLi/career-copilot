import argparse
import json
import sys
from pathlib import Path

from .store import STATUSES, Store


def emit(value):
    print(json.dumps(value, indent=2, ensure_ascii=False))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Career Copilot — local tracker for your Codex career assistant")
    parser.add_argument("--data-dir", type=Path, help="Override private storage directory")
    cmds = parser.add_subparsers(dest="command", required=True)
    cmds.add_parser("init", help="Initialize private local storage; safe to run again")
    cmds.add_parser("status", help="Show profile, applications, tasks and verified counts as JSON")
    cmds.add_parser("history", help="Show last 100 tracker changes")
    profile = cmds.add_parser("profile", help="Read/import your profile; import replaces the whole profile")
    prof = profile.add_subparsers(dest="action", required=True)
    prof.add_parser("show")
    prof.add_parser("import").add_argument("--file", type=Path, required=True)
    apps = cmds.add_parser("application").add_subparsers(dest="action", required=True)
    for action in ("add", "update"):
        sub = apps.add_parser(action)
        if action == "update":
            sub.add_argument("id", type=int)
        for field in ("company", "role", "url", "notes", "evidence", "submitted-at", "submission-evidence"):
            sub.add_argument("--" + field, required=action == "add" and field in ("company", "role", "url"))
        sub.add_argument("--status", choices=STATUSES)
    tasks = cmds.add_parser("task").add_subparsers(dest="action", required=True)
    for action in ("add", "update"):
        sub = tasks.add_parser(action)
        if action == "update":
            sub.add_argument("id", type=int)
        sub.add_argument("--title", required=action == "add")
        sub.add_argument("--application-id", type=int)
        sub.add_argument("--owner", choices=("me", "assistant", "employer"))
        sub.add_argument("--due", help="YYYY-MM-DD or ISO timestamp with timezone")
        sub.add_argument("--notes")
        group = sub.add_mutually_exclusive_group()
        group.add_argument("--done", action="store_const", const=1, default=None)
        group.add_argument("--reopen", dest="done", action="store_const", const=0)
    serve = cmds.add_parser("serve", help="Open local dashboard; no email/API credentials required")
    serve.add_argument("--port", type=int, default=8765)
    serve.add_argument("--open", action="store_true", help="Launch your browser")
    args = parser.parse_args(argv)
    try:
        store = Store(args.data_dir)
        if args.command == "init":
            for folder in ("sources", "resumes", "drafts", "reports", "evidence"):
                (store.directory / folder).mkdir(exist_ok=True, mode=0o700)
            memory = store.directory / "MEMORY.md"
            if not memory.exists():
                memory.write_text("# Candidate memory\n\nConfirmed facts, dates, sources and open questions go here.\n", encoding="utf-8")
            print(f"Ready. Private data: {store.directory.resolve()}")
            print("Open this folder in Codex and say: Set up Career Copilot for me.")
        elif args.command == "profile":
            emit(store.profile() if args.action == "show" else store.save_profile(json.loads(args.file.read_text(encoding="utf-8"))))
        elif args.command == "status":
            emit(store.state())
        elif args.command == "history":
            emit(store.events())
        elif args.command in ("application", "task"):
            data = {k: v for k, v in vars(args).items() if k not in ("command", "action", "id", "data_dir") and v is not None}
            item_id = getattr(store, args.command)(data, getattr(args, "id", None))
            emit({"id": item_id})
        elif args.command == "serve":
            from .server import serve
            serve(store, args.port, args.open)
    except (ValueError, OSError) as exc:
        parser.exit(2, f"Error: {exc}\n")
    except KeyboardInterrupt:
        print("\nStopped. Your data is saved locally.", file=sys.stderr)
