# Virtual Pamudu

An AI assistant that represents [Pamudu Ranasinghe](https://github.com/pamudu123) and showcases his work. Visitors chat with it and it answers by *showing* things: project cards, a career timeline, articles, videos, and a contact form, all streamed live into the conversation.

```
web/  Next.js + CopilotKit  ──AG-UI over SSE──►  api/  FastAPI + deepagents
      chat, cards, chips, approval                    ├─ digital_brain/ as a read-only filesystem
                                                      ├─ tools: GitHub, Medium, YouTube, contact
                                                      ├─ subagents: code-researcher, content-researcher
                                                      └─ checkpointer (conversation state)
```

## What it does

| In the chat | How |
|---|---|
| Answers stream token by token | AG-UI events over SSE |
| Repo, article and video cards | `list_*` / `search_*` tool results rendered by the frontend |
| Experience timeline, skill chips, project and publication cards | `show_profile_section` tool |
| Contact links card | `show_contact_card` tool |
| Live plan checklist on multi-step questions | deepagents todo list |
| Follow-up question chips after every answer | `suggest_followups` tool |
| The assistant asks the visitor a question, with option buttons | `ask_visitor` tool (pauses the run) |
| Editable "message to Pamudu" draft with Send / Cancel | human-in-the-loop interrupt on `send_message_to_pamudu` |

The agent is public, so it is locked down: its filesystem tools are read-only (`ls`, `read_file`, `glob`, `grep`), writes are denied by a permission rule, it has no shell, and the contact tool can only email Pamudu.

## Layout

- `api/main.py` — FastAPI app; mounts the agent at `POST /agent` (AG-UI) and `GET /health`.
- `api/agent/graph.py` — the deep agent: model, backend, subagents, middleware, approval rule.
- `api/agent/prompts.py` — system prompts.
- `api/agent/tools/` — GitHub, Medium, YouTube, contact, and UI tools.
- `api/digital_brain/` — the knowledge base (markdown/YAML). `AGENTS.md` is the index the agent loads as memory.
- `web/app/api/copilotkit/` — CopilotKit runtime route that proxies the browser to the agent.
- `web/components/showcase.tsx` — page layout, tool-call rendering, follow-ups, interrupts.
- `web/components/tool-cards.tsx`, `interrupts.tsx` — the components shown in the chat.
- `web/lib/profile.ts` — the static name, bio, links and starter prompts in the page chrome.

## Run locally

Copy `.env.example` to `.env` in the repo root and fill in at least `OPENROUTER_API_KEY`.

```bash
# terminal 1: agent API on :8000
cd api
uv sync
uv run uvicorn main:app --port 8000

# terminal 2: website on :3000
cd web
npm install
npm run dev
```

Open http://localhost:3000.

## Tests

```bash
cd api
uv run pytest
```

The tests mock all network calls and never call the model.

## Deploy (Vercel)

One Vercel project with two [Services](https://vercel.com/docs/services) (beta), defined in the root `vercel.json`. The website is public; the API is private and reached through a service binding.

| Project | Root directory | Environment variables |
|---|---|---|
| API | `api` | `OPENROUTER_API_KEY`, `GITHUB_TOKEN`, `BREVO_API_KEY`, `DATABASE_URL`, `ALLOWED_ORIGINS` |
| Website | `web` | `AGENT_URL` = `https://<api-domain>/agent` |

`DATABASE_URL` must point at a Postgres database (for example Neon from the Vercel Marketplace, using the pooled connection string). Without it conversation state lives in one process only, and on serverless a follow-up request, an approval, or an answer to the assistant's question can land on a different instance and fail. The tables are created automatically on first start.

## Updating what the assistant knows

Edit the files in `api/digital_brain/` and redeploy the API. If you add a new file or folder, add a row for it in `api/digital_brain/AGENTS.md` so the agent knows it exists.
