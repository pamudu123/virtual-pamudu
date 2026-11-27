import { HttpAgent } from "@ag-ui/client";
import {
  CopilotRuntime,
  InMemoryAgentRunner,
  createCopilotRuntimeHandler,
} from "@copilotkit/runtime/v2";

// The browser only ever talks to this route. It forwards runs to the Python
// deep agent, which streams AG-UI events back over SSE.
// On Vercel the API is a private service in the same deployment, reached
// through the AGENT_INTERNAL_URL binding. AGENT_URL overrides it; local
// development falls back to the uvicorn server.
const AGENT_URL =
  process.env.AGENT_URL ??
  (process.env.AGENT_INTERNAL_URL
    ? new URL("/agent", process.env.AGENT_INTERNAL_URL).toString()
    : "http://localhost:8000/agent");

const runtime = new CopilotRuntime({
  agents: {
    virtual_pamudu: new HttpAgent({ url: AGENT_URL }),
  },
  runner: new InMemoryAgentRunner(),
});

const handler = createCopilotRuntimeHandler({
  runtime,
  basePath: "/api/copilotkit",
});

export const maxDuration = 300;

export const GET = handler;
export const POST = handler;
export const PATCH = handler;
export const DELETE = handler;
