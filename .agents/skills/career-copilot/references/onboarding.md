# Get to know the person, without making setup feel like homework

## Start small

Read the saved profile, `onboarding`, and private memory first. Read supplied résumé/LinkedIn material before asking for facts it already answers. Default to a quick start; don't ask the user to choose a setup mode or fill out JSON. Codex handles files and commands. Explain simply: “I'll ask a few things to get started. You can skip anything and come back later.”

Ask **at most three short questions in one message**, then wait for answers. Keep related prompts together without hiding a long questionnaire inside one question. For an empty profile, a good opening is:

> What are you studying or working on at the moment? If you have a résumé, send it and I'll pull out the basics.
>
> What would you like to do next? It's fine if you're still figuring that out.
>
> Where would you like to work, and would you prefer remote, hybrid, or in person?

If the user already supplied these, ask the next useful questions instead. A résumé, LinkedIn, salary number, writing sample and account connections are **not prerequisites** for starting. Don't ask for exact age/date of birth, home address, government identifiers or optional demographic data just to get to know someone. Request an application-specific required field only when actually needed.

## Learn these topics over the conversation

This is a coverage guide for the assistant, not a form to dump on the user. Follow interesting answers rather than reciting the list in order. Use everyday language. Don't repeat prompts whose answers are clear in supplied material. Accept “not sure”, “skip” and “later”; distinguish unknown from “no”.

| Topic | Useful conversational prompts | Save in the profile |
|---|---|---|
| `background` | What are you studying, and when do you expect to finish? Any work, societies, volunteering or courses you want me to know about? | `experience_and_education`, `resume_paths`, `languages`, sourced `facts` |
| `goals` | What do you want from your next role? What would a good year from now look like? | `career_goals`, `target_roles` |
| `interests` | Which parts of your course or previous work did you enjoy? Anything you tried and didn't like? | `interests`, `dealbreakers` |
| `strengths` | What do people tend to ask you for help with? What would you like to get better at? | `strengths`, `skills_to_build` |
| `projects` | Tell me about one thing you worked on. What did you personally do, what was tricky, and what happened? | `projects_and_achievements`, sourced `facts` |
| `work_preferences` | What matters most: learning, pay, stability, flexibility or something else? Any industries, teams or companies you're drawn to or want to avoid? | `work_preferences`, `company_preferences`, `dealbreakers`, `excluded_companies` |
| `practicalities` | What can fit around your studies? When could you start? Any limits on location, travel or hours? When a real role needs it, confirm work authorization/sponsorship per country and salary currency/period. | `availability`, `practical_constraints`, `location`, `timezone`, `work_authorization`, `salary_preference` |
| `voice` | Want to share a short message you've written so I can match your style? Anything you never want me to say? | `writing_sample`, `writing_style` |
| `support` | What would be most useful right now: résumé, LinkedIn, finding roles or preparing for interviews? How much explanation or how many updates would you like? Any applications already in progress? | `support_preferences`, `search_context`, tracker |
| `permissions` | Do you want me to prepare things for you to review, or also submit suitable applications? Establish sending messages, profile publishing and schedules only as those actions become relevant. | `permissions`, dated private memory |

Finance is a starting context, not a box to put the person in. Don't assume they want banking, have modeling experience or should avoid other roles. If unsure, help them compare a few paths based on their actual interests and experience; label suggestions as suggestions. A stated strength is self-reported, not a verified professional credential. Ask for a concrete example before using a strong claim in an application. Preserve who did what in a group project and don't invent metrics, client work or outcomes.

## Save and resume

After each batch, save useful answers, dates and sources. Start from the current complete profile before importing it. Store longer notes privately. Update `onboarding`:

- `status`: `not_started`, `in_progress`, or `ready_to_start`.
- `covered_topics`: topics with enough actual information for now, not merely questions you asked.
- `deferred_topics`: topics the user explicitly skipped or chose to discuss later. An unanswered question is not a skip.
- `next_question`: one useful remaining question, or blank when none is needed.

Persist progress across sessions. Don't re-ask covered topics or skipped optional questions every time the user returns. Revisit deferred topics when the user asks or a real application makes them necessary; explain the reason once. Keep unknown eligibility facts unknown until confirmed. Corrections replace the current answer with dated provenance; retain context in private memory, not contradictory active values.

Don't make finishing all ten topics a condition for useful work. After a couple of exchanges, or sooner if the user wants to get going, produce a useful first draft/plan from confirmed facts and offer to fill in the rest while working. Record remaining topics honestly; `ready_to_start` means ready to help, **not** that every application field is known or a submission is authorized.

## Reflect back, then use what you learned

Give a short “Here's what I've understood” in normal language: what they want next, their concrete experience, top priorities, things to avoid and preferred voice. Invite corrections without requiring another approval round before reversible drafting. Save a tailored direction note in `private/drafts/career-direction.md` with:

- What we know, what remains unknown, and what was skipped.
- A few relevant role directions and why each fits their stated interests, including gaps honestly.
- Real examples available for a résumé, LinkedIn or interview story.
- The next useful action.

Use these details later: explain job matches in terms of the user's priorities, filter dealbreakers, tailor drafts to actual examples, honor their preferred tone and update cadence, and ask about a gap only when it affects the next action. Don't collect a thoughtful profile and then send generic job lists or boilerplate writing.
