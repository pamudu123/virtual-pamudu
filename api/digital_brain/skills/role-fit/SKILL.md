---
name: role-fit
description: How to assess and show Pamudu's fit for a job or role. Read this when a visitor shares a job description, names a role, or asks "is he a good fit for…" or "would he suit…".
---

# Showing how Pamudu fits a role

The result is a **role fit card** (`show_role_fit`): the role's requirements sorted into strong matches, partial matches and things not covered, each with evidence.

## Step 1: know the role

- If the visitor pasted a job description or described the role, use that.
- If they only said "is he a good fit?" with no role, ask once with the question panel: `ask_visitor` with the question "Which role do you have in mind?" and `fields=["Role or job title"]`. They can also paste a full description in the chat.
- Do not invent requirements. If you only have a title, use the handful of requirements that any such role clearly has, and say in the summary that it is based on the title alone.

## Step 2: read his background

Read `/brain/resume/experience.md`, `/brain/resume/skills.md` and `/brain/resume/projects.md`. Add `/brain/resume/publications.md` or `/brain/resume/patents.md` when the role involves research or document AI.

## Step 3: sort the requirements

Pick the 5 to 8 requirements that matter most and put each in one group:

- **Strong:** the knowledge base clearly shows it. Name the evidence: the employer, project or paper, with a figure if there is one.
- **Partial:** he has related experience but not exactly this. Say what he does have.
- **Not covered:** nothing in the knowledge base shows it. This means "not shown here", not "he cannot do it".

Be honest. A card that is all green is not believable and does not help the visitor. Never move something to Strong without evidence, and never invent experience, years or tools.

## Step 4: show it

1. Call `show_role_fit` with the role, the three groups and a one or two sentence summary.
2. Add one or two sentences of your own: the single strongest reason he fits, and anything worth asking him directly.
3. Call `show_quick_actions` with `["message", "experience", "projects"]` so the visitor can contact him or look closer.

Do not repeat the card's contents as a text list.
