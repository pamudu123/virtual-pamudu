"use client";

import { useState } from "react";

// ---------- shapes of the two pauses the agent can raise ----------

export type AskVisitorValue = { type: "ask_visitor"; question: string; options: string[] };

export type ApprovalValue = {
  action_requests: { name: string; args: Record<string, string> }[];
};

export function readInterrupt(raw: unknown): AskVisitorValue | ApprovalValue | null {
  let value = raw;
  if (typeof value === "string") {
    try {
      value = JSON.parse(value);
    } catch {
      return null;
    }
  }
  // Standard AG-UI interrupts wrap the payload in `{ value }`.
  if (value && typeof value === "object" && "value" in value && !("type" in value)) {
    return readInterrupt((value as { value: unknown }).value);
  }
  if (!value || typeof value !== "object") return null;
  if ((value as AskVisitorValue).type === "ask_visitor") return value as AskVisitorValue;
  if (Array.isArray((value as ApprovalValue).action_requests)) return value as ApprovalValue;
  return null;
}

const cardClass = "my-3 rounded-2xl border border-vp-accent/40 bg-vp-surface p-4 shadow-sm";
const primaryButton =
  "rounded-full bg-vp-accent px-4 py-2 text-sm font-medium text-white transition hover:opacity-90 disabled:opacity-50";
const quietButton =
  "rounded-full border border-vp-line px-4 py-2 text-sm font-medium text-vp-ink transition hover:border-vp-accent hover:text-vp-accent disabled:opacity-50";
const inputClass =
  "w-full rounded-lg border border-vp-line bg-vp-surface-2 px-3 py-2 text-sm text-vp-ink outline-none focus:border-vp-accent";

// ---------- the agent asks the visitor a question ----------

export function AskVisitorCard({
  value,
  onAnswer,
}: {
  value: AskVisitorValue;
  onAnswer: (answer: string) => void;
}) {
  const [text, setText] = useState("");
  const [sent, setSent] = useState(false);

  const answer = (choice: string) => {
    if (sent || !choice.trim()) return;
    setSent(true);
    onAnswer(choice.trim());
  };

  return (
    <div className={cardClass}>
      <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-vp-accent">Quick question</p>
      <p className="mt-1 text-sm font-medium text-vp-ink">{value.question}</p>
      {value.options.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {value.options.map((option) => (
            <button key={option} disabled={sent} onClick={() => answer(option)} className={quietButton}>
              {option}
            </button>
          ))}
        </div>
      )}
      <form
        className="mt-3 flex gap-2"
        onSubmit={(event) => {
          event.preventDefault();
          answer(text);
        }}
      >
        <input
          value={text}
          disabled={sent}
          onChange={(event) => setText(event.target.value)}
          placeholder="Or type your own answer"
          className={inputClass}
        />
        <button type="submit" disabled={sent || !text.trim()} className={primaryButton}>
          Answer
        </button>
      </form>
    </div>
  );
}

// ---------- the visitor approves a message to Pamudu ----------

export type ApprovalDecision =
  | { type: "approve" }
  | { type: "edit"; edited_action: { name: string; args: Record<string, string> } }
  | { type: "reject"; message: string };

export function MessageApprovalCard({
  value,
  onDecide,
}: {
  value: ApprovalValue;
  onDecide: (decision: ApprovalDecision) => void;
}) {
  const action = value.action_requests[0];
  const [draft, setDraft] = useState<Record<string, string>>(action.args);
  const [sent, setSent] = useState(false);
  const edited = JSON.stringify(draft) !== JSON.stringify(action.args);
  const valid = Boolean(
    draft.sender_name?.trim() && /.+@.+\..+/.test(draft.sender_email ?? "") && draft.message?.trim(),
  );

  const field = (key: string) => ({
    value: draft[key] ?? "",
    disabled: sent,
    onChange: (event: { target: { value: string } }) => setDraft({ ...draft, [key]: event.target.value }),
    className: inputClass,
  });

  const decide = (decision: ApprovalDecision) => {
    if (sent) return;
    setSent(true);
    onDecide(decision);
  };

  return (
    <div className={cardClass}>
      <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-vp-accent">
        Message to Pamudu · review before sending
      </p>
      <div className="mt-3 grid gap-2 sm:grid-cols-2">
        <label className="text-xs text-vp-muted">
          Your name
          <input {...field("sender_name")} />
        </label>
        <label className="text-xs text-vp-muted">
          Your email
          <input type="email" {...field("sender_email")} />
        </label>
      </div>
      <label className="mt-2 block text-xs text-vp-muted">
        Subject
        <input {...field("subject")} />
      </label>
      <label className="mt-2 block text-xs text-vp-muted">
        Message
        <textarea rows={5} {...field("message")} />
      </label>
      <div className="mt-3 flex flex-wrap items-center gap-2">
        <button
          disabled={sent || !valid}
          className={primaryButton}
          onClick={() =>
            decide(
              edited
                ? { type: "edit", edited_action: { name: action.name, args: draft } }
                : { type: "approve" },
            )
          }
        >
          {sent ? "Sending…" : "Send to Pamudu"}
        </button>
        <button
          disabled={sent}
          className={quietButton}
          onClick={() => decide({ type: "reject", message: "The visitor cancelled; do not send." })}
        >
          Cancel
        </button>
        <span className="text-[11px] text-vp-muted">Only Pamudu receives this. He can reply to your email.</span>
      </div>
    </div>
  );
}
