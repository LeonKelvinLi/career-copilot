---
name: career-copilot
description: Set up and run this user's career assistant in Codex, including a saved candidate profile, natural résumé and LinkedIn writing, job research, application tracking, email reply checks, and outstanding tasks. Use for this repository's onboarding and career workflow.
---

# Career Copilot

Read the repository's `AGENTS.md`. The repo root is three directories above this skill folder. Run commands from that root. This is a Codex workflow with a local tracker; the Python app does not itself connect to accounts, generate AI text or run jobs in the background.

## First-time setup

Read the saved profile, tracker and any existing `private/MEMORY.md` before asking questions, using `python3 career.py profile show` and `python3 career.py status` when Python is available. If a previous setup saved `private/profile-draft.json` while Python was unavailable and no profile exists yet, import it before continuing. If the profile is empty, **ask the current user for their own details**. Do not ask them to get information from a friend. Handle initialization with `python3 career.py init` yourself; use the runtime fallback in `AGENTS.md` if needed.

Read [references/onboarding.md](references/onboarding.md) for the conversational intake and saved progress. Ask at most three short questions at a time. Learn the person's goals, interests, strengths, projects, work preferences, practical constraints, desired support and writing style, building on supplied material. Start with background, what they want next and work location; résumé and LinkedIn are optional. A user can skip or defer anything and receive useful drafts early. The initial intended user was described as a finance student around 25: confirm their actual education and experience from their own answers, rather than assuming engineering experience or treating this description as verified application data. Never borrow the repository creator's personal facts, résumé, or global memory for a different candidate.

Build the profile from the material supplied; ask only for remaining useful or consequential facts. Confirm work authorization/sponsorship **per work country**, actual language levels, study status/graduation, notice/start dates and scheduling constraints when needed. Store unknowns as blank, not guesses. Save dated, sourced confirmations in `facts`, `onboarding` progress and `private/MEMORY.md`. Summarize what you learned in a private career-direction draft and use it to personalize job matches and writing. Read [references/setup.md](references/setup.md) for account setup and first-session deliverables.

Use a normal human voice by default: simple words, short sentences, and specific details from the candidate's experience. The intended tone is someone in their mid-twenties studying finance talking to another person. Do not sound like a corporate press release or inflate seniority to make the person sound older. Apply [references/writing.md](references/writing.md) to all résumés, cover letters, LinkedIn text, recruiter drafts and user-facing explanations. A short voluntary writing sample improves matching; it is not a setup blocker. Writing naturally does not authorize false claims or misrepresenting AI participation where disclosure is required.

## Ongoing work

- Profile/résumé/LinkedIn: read the current profile and source documents; use the writing reference, verify dates and metrics, and save drafts privately. Edit the user's own account when authorized; verify the saved result. Do not mark a draft as published.
- Job search/applications: read [references/jobs.md](references/jobs.md). Verify official postings, fit, country eligibility and deduplication. Proceed within the user's confirmed action scope. Evidence-backed submissions and assessments are different tracker events.
- “Any replies?” / “what's outstanding?”: read [references/replies.md](references/replies.md). Use full messages and actual coverage; keep next steps for each role separate.
- Recurring work: only create a schedule when the current user asks for it. Use Codex's native automation tools when available. Confirm timezone/time/target and scope if unknown, save the actual automation ID locally, and notify only on meaningful changes unless the user requests routine updates. A prompt file is not an active schedule.

## Tracker

`python3 career.py --help` and subcommand `--help` describe the interface. Import a complete profile JSON using `profile import --file private/profile-draft.json`; start with `profile show` so existing fields are preserved. `profile.example.json` documents the schema, using blank values. Records are in `private/career.sqlite3` and never belong in a public commit.

Use `application add/update` and `task add/update` for writes. Add receipts as `submission_evidence` and a timezone-qualified `submitted_at`; original verified receipt/date are immutable to prevent accidental double counting. Later stage changes use `evidence` and notes. A clear portal confirmation or employer receipt qualifies; a spinner, form reset, guessed email or draft does not. Do not retry an uncertain submission until its state is checked.

Use `private/resumes/` for current approved files and `private/evidence/` for proof. Keep a small `private/reports/` record of what you checked and couldn't access. Preserve meaningful source dates. Do not change the active candidate or silently overwrite conflicting confirmed facts.
