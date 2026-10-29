# Setup and account connections

## Intake and memory

1. Read existing profile and memory before asking. Ask for the user's own résumé, LinkedIn (optional), target roles, work locations and salary preference. Empty setup must actually ask the user, not just create blank files and announce completion.
2. Parse supplied résumé/material using the available document tools. Extract employment/education dates and actual responsibilities. Do not manufacture missing facts. Finance examples may include coursework, university societies, internships, part-time work, spreadsheet projects or research only if the candidate actually supplied them. Being a finance student is not evidence of accounting, investment banking, modeling or Excel proficiency.
3. Save confirmed answers in a complete profile JSON imported through the CLI. Record `facts` entries with `field`, `value`, `source`, `confirmed_at` (YYYY-MM-DD). Source may be “user confirmed in this chat” or an actual file. Keep `private/MEMORY.md` concise: current résumé paths, dated confirmations, open questions, permissions and connection status. Do not store passwords, raw OAuth tokens or login cookies.
4. Resolve preferences as work needs them: graduation term, languages, country-specific authorization, start/notice date, schedule, salary currency/period, role exclusions. Do not make a long questionnaire a prerequisite for useful drafts. When the user confirms a detail once, reuse it. Re-check changing facts only when stale or contradicted.

## Connect the candidate's own accounts

Discover the current environment's available tools; account/plugin availability varies. Prefer service connectors when capable. Use the product's plugin/connection flow if present. Explain one missing connection at a time; the user signs in directly. Do not install a similarly named unverified connector, invent API access, promise automatic connections, or copy the creator's tokens. Available steps:

- Email: discover Gmail or the user's provider's connected tools. Read the authenticated mailbox identity and ask if it conflicts with their supplied application email. A disconnected inbox does not block résumé work. Record accessible folders/limitations. If unavailable, accept specific pasted emails as data and clearly label coverage as limited.
- LinkedIn: there may be no suitable API connector. Use a supported browser/computer tool with the user's own logged-in profile, inspect the profile identity before editing, and follow that tool's instructions. If browser access is unavailable, prepare a paste-ready headline, About section, Experience and Skills in `private/drafts/linkedin.md`. Do not request their password or claim publication without verification.
- Files: use local supplied résumé paths or an available Drive connector. Confirm which file is current; keep originals. Do not publish personal documents to a public GitHub repo or change file sharing merely to attach a résumé.
- Calendar: optional for interview availability; connect only when useful and authorized.
- GitHub/portfolio: optional, not a prerequisite for finance candidates. Validate provided work-sample links; don't invent a portfolio or imply one is needed for every role.

Record each service's actual state and account identity in profile `connections`, e.g. `"email": "Not connected"`. A stored connection note is not proof that today's token works: verify live access before claiming a check.

## Action scope, asked once

Ask what the user wants handled, in plain language. Offer preparation only, submitting suitable applications, or a custom scope. Separately establish profile publishing, recruiter email sending and recurring schedules when these become relevant. Save what they actually authorized in `permissions`; include dates or limits. Do not construe “set up” or “check replies” as permission to send email or submit applications. Conversely, don't repeatedly ask about an ordinary application or profile edit already covered by a clear request. Flag only genuinely new decisions such as unknown personal declarations, binding commitments or changing job preferences.

## First-session deliverables

Produce as much as available facts allow: a saved candidate profile, an honest list of missing facts/connections, a résumé review or draft, LinkedIn draft, initial target-role plan, and a tracker with concrete next steps. Match résumé language and file type to the user's preference and employer requirements. Keep a current source copy and approved version per language. Save no invented “verified” submissions to populate the dashboard.

The optional local dashboard starts with `python3 career.py serve --open`. It reads the same SQLite state as the CLI. It does not need API keys and has no direct account access. Python 3.10+ is required; some systems need the operating system's timezone database or Python's `tzdata` package for IANA timezones. Do not claim the setup is fully account-connected until access is actually verified.
