# Validation — October 29, 2026

## Autonomous candidate rehearsal

A separate Codex agent read the repository guidance and skill, then acted as a fictional first-time candidate: Alex Example, 25, studying finance, June 2027 graduation, a coursework cash-flow comparison in Excel, no paid finance experience, seeking hybrid London internships. Salary, current residence and UK work authorization were deliberately unconfirmed. Email and LinkedIn were deliberately disconnected.

The agent executed **15 isolated CLI checks** as fresh subprocesses, with all data outside this repository. These covered initialization, persisted profile and sourced facts, preparation-only scope, unknown fields staying blank, uncertain submissions not counting, rejection of evidence-free submission, one synthetic receipt counting once after a stage change, distinct same-company roles and tasks, URL deduplication, original receipt-date preservation, task reopen/history, and desired work location staying distinct from current residence.

It also rehearsed the conversation: first setup asks the candidate for their own information; a subsequent session reuses saved answers; “any replies?” with no mailbox access admits that nothing was searched; “what's outstanding?” uses separate role-specific tasks. This was an agent-driven behavioral rehearsal plus real CLI execution, **not** a separately launched new Codex desktop installation or a live human onboarding test.

Example draft produced from only the fictional candidate's facts:

> Hi, I'm Alex. I'm studying finance and looking for a finance internship in London. For a class project, I used Excel to compare companies' cash flow. I'd like to build on that work in an internship. Do you have any suitable openings?
>
> Thanks, Alex

## Bug found and fixed

The agent's follow-up review found that an older open dashboard could overwrite newer facts, permissions and connection notes saved by Codex. The dashboard now sends only changed visible fields, and the server merges them into the latest profile inside a transaction. The agent independently repeated this scenario over an isolated HTTP server and confirmed that newer facts, permissions, connections and target roles all survive a name-only edit.

## Automated and browser checks

`python3 -m unittest discover -s tests -v`: **15 tests passed**. Tests cover profile persistence, receipt/date and count invariants, role identity and deduplication, separate assessment tasks, validation, local HTTP profile saves, preservation of concurrent Codex updates, rejection of cross-origin and unauthenticated requests, and inability to serve private/arbitrary files.

`node --check career_copilot/web/app.js`: passed. The bundled skill-creator validator also passed for `.agents/skills/career-copilot`.

The dashboard was opened in Chrome against isolated fictional data. Actual browser interactions saved a profile, reloaded persisted answers, added an uncertain application, linked and completed a candidate task, edited the existing application with a clearly synthetic receipt, and verified one counted submission with no remaining candidate tasks. The profile-save flow was rechecked after the concurrency fix. `dashboard.png` is a screenshot of that fictional test; no personal account data appears in it.

## Limits

The tests do not establish that a particular user's Codex plan or device has Gmail, LinkedIn browser control, calendar, document tools or scheduling access. Those must be discovered and authenticated in that user's own session. No live email was read, no LinkedIn profile edited, no employer form submitted, and no recurring schedule created for the fictional candidate.

The tracker requires evidence text; Codex must independently verify that the referenced receipt actually exists and supports the claim. Python does not authenticate receipts or decide hiring outcomes. All copied prompts and skill instructions remain subject to the user's authorization and the current environment's tool policies.
