"""Virtual Pamudu API: a deep agent streamed over the AG-UI protocol."""

import asyncio
import os
import sys
from contextlib import asynccontextmanager

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(usecwd=True))

from ag_ui_langgraph import add_langgraph_fastapi_endpoint  # noqa: E402
from copilotkit import LangGraphAGUIAgent  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from langgraph.checkpoint.memory import MemorySaver  # noqa: E402

from agent.graph import build_agent  # noqa: E402

AGENT_NAME = "virtual_pamudu"
# How many graph steps one answer may take. Each lookup costs a few steps, so
# LangGraph's default of 25 runs out in the middle of an answer that needs
# several lookups, and the run dies. The AG-UI adapter replaces the graph's own
# (much higher) limit with its config, so the limit has to be set here. It is
# kept finite so a confused run on this public agent still stops.
RECURSION_LIMIT = int(os.getenv("AGENT_RECURSION_LIMIT", "150"))
DATABASE_URL = os.getenv("DATABASE_URL")

if sys.platform == "win32" and DATABASE_URL:
    # psycopg's async driver cannot run on Windows' default Proactor loop.
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Without a database, threads live in this process only. That is fine locally,
# but on serverless a follow-up request can land on another instance, so
# production must set DATABASE_URL (see `ensure_checkpointer`).
graph = build_agent(MemorySaver())

_pool = None
_checkpointer_ready = False
_checkpointer_lock = asyncio.Lock()


async def ensure_checkpointer() -> None:
    """Swap the in-memory checkpointer for Postgres on first use, if configured."""
    global _pool, _checkpointer_ready
    if _checkpointer_ready or not DATABASE_URL:
        return
    async with _checkpointer_lock:
        if _checkpointer_ready:
            return
        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
        from psycopg.rows import dict_row
        from psycopg_pool import AsyncConnectionPool

        _pool = AsyncConnectionPool(
            DATABASE_URL,
            min_size=0,
            max_size=5,
            open=False,
            kwargs={"autocommit": True, "prepare_threshold": None, "row_factory": dict_row},
        )
        await _pool.open()
        saver = AsyncPostgresSaver(_pool)
        await saver.setup()
        graph.checkpointer = saver
        _checkpointer_ready = True


@asynccontextmanager
async def lifespan(_: FastAPI):
    await ensure_checkpointer()
    yield
    if _pool is not None:
        await _pool.close()


app = FastAPI(title="Virtual Pamudu API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def checkpointer_guard(request, call_next):
    # Covers platforms that do not run ASGI lifespan events.
    await ensure_checkpointer()
    return await call_next(request)


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "agent": AGENT_NAME,
        "persistence": "postgres" if _checkpointer_ready else "memory",
    }


add_langgraph_fastapi_endpoint(
    app=app,
    agent=LangGraphAGUIAgent(
        name=AGENT_NAME,
        description="Answers questions about Pamudu Ranasinghe and his work.",
        graph=graph,
        config={"recursion_limit": RECURSION_LIMIT},
        # Raw LangGraph events carry the system prompt and full tool payloads.
        # Visitors' browsers must never receive them.
        emit_raw_events=False,
    ),
    path="/agent",
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
