# Job search and application records

Read profile, permissions, current résumé and tracker first. Target roles come from this candidate's preferences, not the creator's engineering background. A finance student might target internships or analyst roles, but ask rather than assuming a specialty.

Use the deeper profile in actual selection: goals and interests inform role directions; work/company preferences and dealbreakers inform filtering; real projects and strengths supply relevant examples; skills-to-build identify learning opportunities without pretending the skill already exists. Explain a match using those details. If the user is exploring, offer a few directions and the reason for each. Never turn an inferred interest into confirmed experience or silently ignore their priorities to fill a quota.

For each candidate job, verify the live employer posting, location eligibility (including where remote work is allowed), required experience, education and language, type of employment, salary currency/period if published, deadlines and the correct application route. Third-party “worldwide” tags do not override official country restrictions. Preserve current residence versus future relocation. Do not infer work authorization, citizenship or sponsorship from name, school or residence. Financial job research is not personalized investment advice.

Deduplicate by employer role ID and URL, including prior tracker/history and receipt emails. The CLI removes tracking query parameters but cannot identify every redirected alias: also compare company, title and job IDs manually. Separate roles at one company remain separate applications. Prefer suitable roles over filling a daily quota. Explain when there are fewer good matches than requested; never invent submissions.

Draft with the writing reference and real facts, using the current approved résumé per language. Do not inflate tenure or convert student projects into paid work. If a required answer is unknown, save a draft, create a task for the user and continue useful independent work. Don't guess sensitive demographics, graduation date, salary consent, work authorization or legal declarations. Routine choices already covered by the user's preferences don't need repeat questions.

Before external submission, honor the user's confirmed scope and applicable tool/skill rules. A résumé attachment or form save is not proof of submission. After submitting, verify a clear portal result or employer receipt and save the source. If a form spins, resets or errors without a receipt, use `uncertain` and investigate before retrying. A required CAPTCHA, identity check, scored assessment or video recording is for the user. General practice/coaching is separate from completing a live scored assessment.

CLI examples, with fictional data only:

```sh
python3 career.py application add --company 'Example Company' --role 'Finance Intern' --url 'https://example.com/jobs/finance-intern' --status draft --notes 'Awaiting confirmed graduation date.'
python3 career.py task add --application-id 1 --title 'Confirm graduation term' --owner me
```

When verified, update the original record. Use the actual receipt time and timezone, not the current date if it was submitted earlier. `--status submitted --submission-evidence 'private/evidence/receipt.txt' --submitted-at '2026-10-29T14:00:00-07:00'` is a syntax example, not permission to invent evidence. Save later stages with `--status assessment --evidence 'actual source'`. Do not overwrite the original verified timestamp. Interview invitations, completed assessments and rejections update the original role and do not add to daily submission counts.

Keep assessments distinct by role. Completion is not a passing score. Record deadlines with their original timezone and convert for the user; an expired deadline does not prove the link works or the employer granted an extension. Save an extension request as a draft unless sending is authorized.
