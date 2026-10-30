# Adam's setup

Paste this into a local Codex chat:

> Set up Career Copilot for me from https://github.com/LeonKelvinLi/career-copilot using the Adam Zhang starter. Read AGENTS.md and starters/adam-zhang/README.md. Use the saved LinkedIn background, ask me only for what needs confirming or is missing, and handle the technical setup. Keep the writing natural.

Already in this project? Say **“Set this up for me using the Adam Zhang starter.”**

## Instructions for Codex

This starter uses professional details from [Adam's supplied LinkedIn profile](https://www.linkedin.com/in/adam-zhang-509ba2294/), read October 29, 2026. See [source-notes.md](source-notes.md) for source links and important qualifications. `profile.json` is a dated, self-reported source snapshot, not a new résumé approved by Adam or independent verification of employment, degrees, license status or performance.

It covers five listed roles, four education entries, four certification/license listings, all 31 listed skills, the portfolio-management course project and two volunteering entries. [Draft examples](draft-examples.md) give Codex a plain-language starting point; they are not published profile changes.

In `profile.json`, a fact's `confirmed_at` date records when the LinkedIn claim was observed. The `source` explicitly distinguishes that from Adam personally confirming it. Preserve that distinction when writing applications.

Use it only when the current user identifies as Adam or explicitly requests Adam's starter. Keep the generic setup for other candidates. Never replace an existing person's profile or overwrite Adam's newer answers. Read the active profile and private memory first; where there is a conflict, keep the newer candidate-confirmed value and ask only if it affects the next step. If an identity conflict is unresolved, do not import.

For a fresh Adam setup, initialize private storage and import the starter yourself:

```sh
python3 career.py init
python3 career.py profile import --file starters/adam-zhang/profile.json
```

If an Adam profile already exists, merge useful sourced facts into a fresh copy of it rather than running the replacement import above. Never refill a field that Adam explicitly corrected, declined or deferred merely because the older LinkedIn snapshot contains it. His future answers, private documents, email, permissions, application history and account connections belong only in `private/`, not this public starter. If Python is unavailable, follow the normal draft-profile fallback in `AGENTS.md`.

Start the conversation with at most three short questions:

1. “Your profile lists Guidepoint from January 2026 and Santa Clara studies ending in December 2025. Is that still accurate?”
2. “What would you like to do next, or what do you want help figuring out?”
3. “Where would you like to work, and do you prefer remote, hybrid or in person?”

Don't ask him to type his whole education or job history again. Don't describe him as a current student, assume London, assume he wants internships, or import any fictional Alex example. The profile supports an early-career finance background; his actual goals are still unknown. UTC is only the software's initial timezone default, so confirm his timezone before schedules or deadlines.

As work needs it, ask about actual Guidepoint duties and achievements, what he personally did in the class portfolio project, current Excel/Python/modeling proficiency, desired roles, salary/currency, work eligibility and sponsorship by country, start/notice dates, current résumé, language levels and his own writing style. Do not infer language or nationality from his name, Chinese internships or international coursework. Do not ask for private client names to make a résumé bullet sound stronger.

Follow the normal conversational onboarding for interests, priorities, strengths, things to avoid and preferred support. Produce useful drafts early. Keep all account connections disconnected until verified in his own session and leave external actions unauthorized until he requests them.
