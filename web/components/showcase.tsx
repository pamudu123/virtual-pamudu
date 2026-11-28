"use client";

import {
  CopilotChat,
  CopilotKitProvider,
  useAgent,
  useConfigureSuggestions,
  useCopilotKit,
  useInterrupt,
  useRenderTool,
  type Message,
} from "@copilotkit/react-core/v2";
import { useCallback, type ReactNode } from "react";

import { AGENT_ID, profile, starterSuggestions, topics } from "@/lib/profile";
import {
  AskVisitorCard,
  FeedbackCard,
  MessageApprovalCard,
  readInterrupt,
  type ApprovalDecision,
} from "./interrupts";
import {
  ArticleCards,
  ContactCard,
  ProfileSection,
  RepoCards,
  RoleFitCard,
  StatTiles,
  StatusPill,
  TodoList,
  VideoCards,
  parseResult,
} from "./tool-cards";

type ToolRenderProps = {
  name: string;
  parameters: unknown;
  status: "inProgress" | "executing" | "complete";
  result: string | undefined;
};

const KNOWLEDGE_TOOLS = new Set(["read_file", "ls", "glob", "grep"]);

/**
 * A lookup that never got its result. While the agent is still working the
 * loading placeholder is right; once the run has ended (it failed or was
 * stopped) the placeholder would sit there forever, so say so instead.
 */
function Lookup({ done, label, children }: { done: boolean; label: string; children: ReactNode }) {
  const { agent } = useAgent({ agentId: AGENT_ID });
  if (!done && !agent.isRunning) return <StatusPill text={`Couldn't load ${label}`} done />;
  return <>{children}</>;
}

/** Turns the agent's tool calls into components inside the conversation. */
function renderTool({ name, parameters, status, result }: ToolRenderProps) {
  const done = status === "complete";
  const args = (parameters ?? {}) as Record<string, unknown>;

  switch (name) {
    case "list_github_repos":
    case "search_github_repos":
      return (
        <Lookup done={done} label="his repositories">
          <RepoCards result={result} done={done} />
        </Lookup>
      );
    case "list_medium_articles":
    case "search_medium_articles":
      return (
        <Lookup done={done} label="his articles">
          <ArticleCards result={result} done={done} />
        </Lookup>
      );
    case "list_youtube_videos":
    case "search_youtube_videos":
      return (
        <Lookup done={done} label="his videos">
          <VideoCards result={result} done={done} />
        </Lookup>
      );
    case "show_profile_section":
      return <ProfileSection args={args} />;
    case "show_contact_card":
      return <ContactCard result={result} done={done} />;
    case "show_stats":
      return <StatTiles args={args} />;
    case "show_role_fit":
      return <RoleFitCard args={args} />;
    case "show_quick_actions":
      return done ? <QuickActions result={result} /> : <></>;
    case "write_todos":
      return <TodoList todos={args.todos as never} />;
    case "task": {
      const who = args.subagent_type === "code-researcher" ? "Reading the code" : "Reading the source";
      return <StatusPill text={done ? `${who} · done` : `${who}…`} done={done} />;
    }
    case "send_message_to_pamudu": {
      if (!done) return <></>;
      const sent = result?.includes('"sent": true') || result?.includes('"sent":true');
      // An `error` means the visitor pressed Send and delivery failed, which
      // is different from the visitor cancelling the draft.
      const failed = !sent && Boolean(result?.includes('"error"'));
      const text = sent
        ? "Message delivered to Pamudu"
        : failed
          ? "Couldn't deliver the message"
          : "Message not sent";
      return <StatusPill text={text} done />;
    }
    case "ask_feedback":
      return done && result?.includes("Feedback received") ? (
        <StatusPill text="Feedback received" done />
      ) : (
        <></>
      );
    case "suggest_followups":
    case "ask_visitor":
      return <></>;
    default:
      if (KNOWLEDGE_TOOLS.has(name)) {
        // Reading a skill playbook is internal housekeeping, not a profile lookup.
        if (JSON.stringify(args).includes("/skills/")) return <></>;
        return <StatusPill text={done ? "Checked his profile" : "Checking his profile…"} done={done} />;
      }
      return <StatusPill text={done ? "Done" : "Working…"} done={done} />;
  }
}

/** Follow-up questions the agent attached to its latest answer. */
function readFollowups(messages: readonly Message[]): string[] {
  for (let i = messages.length - 1; i >= 0; i--) {
    const message = messages[i];
    if (message.role === "user") return [];
    if (message.role !== "assistant") continue;
    const call = message.toolCalls?.find((c) => c.function.name === "suggest_followups");
    if (!call) continue;
    try {
      const questions: unknown = JSON.parse(call.function.arguments).questions;
      return Array.isArray(questions)
        ? questions.filter((q): q is string => typeof q === "string").slice(0, 3)
        : [];
    } catch {
      return [];
    }
  }
  return [];
}

function useFollowups(): string[] {
  const { agent } = useAgent({ agentId: AGENT_ID });
  return agent.isRunning ? [] : readFollowups(agent.messages);
}

function useSendMessage() {
  // Until the runtime connection is up, `agent` is a stand-in; sending to it
  // would silently drop the message, so callers disable their buttons.
  const { agent, isReady } = useAgent({ agentId: AGENT_ID });
  const { copilotkit } = useCopilotKit();
  const send = useCallback(
    (content: string) => {
      if (!isReady || agent.isRunning) return;
      agent.addMessage({ id: crypto.randomUUID(), role: "user", content });
      void copilotkit.runAgent({ agent });
    },
    [agent, copilotkit, isReady],
  );
  return { send, isReady };
}

type QuickAction =
  | { id: string; kind: "link"; label: string; href: string }
  | { id: string; kind: "prompt"; label: string; prompt: string };

const actionClass =
  "rounded-full border border-vp-line bg-vp-surface px-3.5 py-1.5 text-[13px] font-medium text-vp-ink transition hover:border-vp-ink disabled:opacity-50";

/** Buttons for the visitor's next step: open a profile, or start a conversation. */
function QuickActions({ result }: { result?: string }) {
  const { send, isReady } = useSendMessage();
  const actions = parseResult<{ actions?: QuickAction[] }>(result)?.actions ?? [];
  if (actions.length === 0) return <></>;
  return (
    <div className="my-3 flex flex-wrap gap-2">
      {actions.map((action) =>
        action.kind === "link" ? (
          <a key={action.id} href={action.href} target="_blank" rel="noreferrer" className={actionClass}>
            {action.label} ↗
          </a>
        ) : (
          <button
            key={action.id}
            type="button"
            disabled={!isReady}
            onClick={() => send(action.prompt)}
            className={actionClass}
          >
            {action.label}
          </button>
        ),
      )}
    </div>
  );
}

function Sidebar() {
  const { send, isReady } = useSendMessage();
  return (
    <aside className="flex flex-col gap-6 border-b border-vp-line bg-vp-surface px-6 py-6 lg:h-dvh lg:overflow-y-auto lg:border-b-0 lg:border-r lg:px-8 lg:py-10">
      <div className="flex items-center gap-4 lg:flex-col lg:items-start">
        <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-vp-accent text-lg font-semibold text-white lg:h-16 lg:w-16">
          {profile.initials}
        </div>
        <div>
          <h1 className="text-xl font-semibold tracking-tight text-vp-ink lg:text-2xl">{profile.name}</h1>
          <p className="text-sm font-medium text-vp-accent">{profile.headline}</p>
        </div>
      </div>

      <p className="hidden text-sm leading-relaxed text-vp-muted lg:block">{profile.bio}</p>

      <div className="hidden flex-wrap gap-1.5 lg:flex">
        {profile.focus.map((item) => (
          <span key={item} className="rounded-full bg-vp-accent-soft px-2.5 py-1 text-xs font-medium text-vp-accent">
            {item}
          </span>
        ))}
      </div>

      <div>
        <p className="mb-2 hidden text-[11px] font-semibold uppercase tracking-[0.14em] text-vp-muted lg:block">
          Explore
        </p>
        <div className="flex gap-2 overflow-x-auto lg:grid lg:grid-cols-2 lg:overflow-visible">
          {topics.map((topic) => (
            <button
              key={topic.label}
              disabled={!isReady}
              onClick={() => send(topic.prompt)}
              className="disabled:opacity-50shrink-0 rounded-xl border border-vp-line px-3 py-2 text-left text-sm font-medium text-vp-ink transition hover:border-vp-accent hover:text-vp-accent"
            >
              {topic.label}
            </button>
          ))}
        </div>
      </div>

      <div className="hidden lg:mt-auto lg:block">
        <div className="flex flex-wrap gap-x-4 gap-y-2">
          {profile.links.map((link) => (
            <a
              key={link.label}
              href={link.href}
              target="_blank"
              rel="noreferrer"
              className="text-sm text-vp-muted transition hover:text-vp-accent"
            >
              {link.label} ↗
            </a>
          ))}
        </div>
        <p className="mt-4 text-[11px] leading-relaxed text-vp-muted">
          You are chatting with an AI assistant that represents Pamudu. It answers from his own profile,
          code, articles and videos.
        </p>
      </div>
    </aside>
  );
}

function Chat() {
  const followups = useFollowups();

  useRenderTool({ name: "*", render: renderTool }, []);

  useConfigureSuggestions(
    followups.length > 0
      ? { suggestions: followups.map((q) => ({ title: q, message: q })), available: "always" }
      : { suggestions: starterSuggestions, available: "before-first-message" },
    [followups.join("|")],
  );

  useInterrupt({
    agentId: AGENT_ID,
    render: ({ event, resolve }) => {
      const value = readInterrupt(event.value);
      if (!value) return <></>;
      if ("type" in value && value.type === "feedback") {
        return <FeedbackCard value={value} onSubmit={(answer) => void resolve(answer)} />;
      }
      if ("type" in value) {
        return <AskVisitorCard value={value} onAnswer={(answer) => void resolve(answer)} />;
      }
      return (
        <MessageApprovalCard
          value={value}
          onDecide={(decision: ApprovalDecision) => void resolve({ decisions: [decision] })}
        />
      );
    },
  });

  return (
    <main className="flex min-h-0 flex-1 flex-col lg:h-dvh">
      <CopilotChat
        agentId={AGENT_ID}
        className="min-h-0 flex-1"
        labels={{
          chatInputPlaceholder: "Ask about Pamudu's work, projects, research…",
          welcomeMessageText: "Hi, I'm Pamudu's AI assistant. What would you like to know about him?",
          chatDisclaimerText: "AI assistant representing Pamudu. Answers come from his own material.",
        }}
      />
    </main>
  );
}

/**
 * `embedded` renders the chat alone, for showing inside another site's panel
 * (the portfolio's "Pamudu AI" drawer loads `/embed` in an iframe).
 */
export function Showcase({ embedded = false }: { embedded?: boolean }) {
  return (
    <CopilotKitProvider runtimeUrl="/api/copilotkit" agentId={AGENT_ID} useSingleEndpoint={false} enableInspector={false}>
      <div
        className={
          embedded
            ? "flex h-dvh flex-col bg-vp-surface"
            : "flex h-dvh flex-col lg:grid lg:grid-cols-[340px_1fr]"
        }
      >
        {!embedded && <Sidebar />}
        <Chat />
      </div>
    </CopilotKitProvider>
  );
}
