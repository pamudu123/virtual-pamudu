"use client";

import { useState } from "react";

// ---------- shapes of the pauses the agent can raise ----------

export type AskVisitorValue = {
  type: "ask_visitor";
  question: string;
  options: string[];
  /** Labels of short inputs to collect together, e.g. name and email. */
  fields?: string[];
};

export type FeedbackValue = { type: "feedback"; question: string };

export type FeedbackAnswer = { rating: number; name: string; comment: string } | { skipped: true };

export type ApprovalValue = {
  action_requests: { name: string; args: Record<string, string> }[];
};

export function readInterrupt(raw: unknown): AskVisitorValue | FeedbackValue | ApprovalValue | null {
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
  if ((value as FeedbackValue).type === "feedback") return value as FeedbackValue;
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

  const fields = (value.fields ?? []).filter((label) => label.trim());
  const [details, setDetails] = useState<Record<string, string>>({});
  const isEmail = (label: string) => /e-?mail/i.test(label);
  const filled = (label: string) => {
    const text = (details[label] ?? "").trim();
    return isEmail(label) ? /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(text) : Boolean(text);
  };

  // A small form: every field is answered in this one panel.
  if (fields.length > 0) {
    const ready = fields.every(filled);
    return (
      <div className={cardClass}>
        <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-vp-accent">Quick question</p>
        <p className="mt-1 text-sm font-medium text-vp-ink">{value.question}</p>
        <form
          className="mt-3"
          onSubmit={(event) => {
            event.preventDefault();
            if (!ready) return;
            answer(fields.map((label) => `${label}: ${(details[label] ?? "").trim()}`).join("\n"));
          }}
        >
          <div className={fields.length > 1 ? "grid gap-2 sm:grid-cols-2" : "grid gap-2"}>
            {fields.map((label, index) => (
              <label key={label} className="text-xs text-vp-muted">
                {label}
                <input
                  type={isEmail(label) ? "email" : "text"}
                  autoComplete={isEmail(label) ? "email" : /name/i.test(label) ? "name" : "off"}
                  placeholder={isEmail(label) ? "you@example.com" : ""}
                  autoFocus={index === 0}
                  value={details[label] ?? ""}
                  disabled={sent}
                  onChange={(event) => setDetails({ ...details, [label]: event.target.value })}
                  className={inputClass}
                />
              </label>
            ))}
          </div>
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <button type="submit" disabled={sent || !ready} className={primaryButton}>
              Continue
            </button>
            <button
              type="button"
              disabled={sent}
              className={quietButton}
              onClick={() => answer("The visitor chose not to share these details.")}
            >
              Skip
            </button>
          </div>
        </form>
      </div>
    );
  }

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

// ---------- the visitor rates the assistant ----------

const RATINGS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

export function FeedbackCard({
  value,
  onSubmit,
}: {
  value: FeedbackValue;
  onSubmit: (answer: FeedbackAnswer) => void;
}) {
  const [rating, setRating] = useState<number | null>(null);
  const [name, setName] = useState("");
  const [comment, setComment] = useState("");
  const [sent, setSent] = useState(false);

  const finish = (answer: FeedbackAnswer) => {
    if (sent) return;
    setSent(true);
    onSubmit(answer);
  };

  return (
    <form
      className={cardClass}
      onSubmit={(event) => {
        event.preventDefault();
        if (rating === null) return;
        finish({ rating, name: name.trim(), comment: comment.trim() });
      }}
    >
      <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-vp-accent">Your feedback</p>
      <p id="feedback-question" className="mt-1 text-sm font-medium text-vp-ink">
        {value.question}
      </p>

      <div role="radiogroup" aria-labelledby="feedback-question" className="mt-3 grid grid-cols-5 gap-1.5 sm:grid-cols-10">
        {RATINGS.map((n) => {
          const selected = rating === n;
          return (
            <button
              key={n}
              type="button"
              role="radio"
              aria-checked={selected}
              aria-label={`${n} out of 10`}
              disabled={sent}
              onClick={() => setRating(n)}
              className={
                selected
                  ? "flex h-11 items-center justify-center rounded-lg sm:aspect-square sm:h-auto border border-vp-ink bg-vp-ink text-sm font-semibold text-white disabled:opacity-60"
                  : "flex h-11 items-center justify-center rounded-lg sm:aspect-square sm:h-auto border border-vp-line bg-vp-surface text-sm font-medium text-vp-ink transition hover:border-vp-ink disabled:opacity-60"
              }
            >
              {n}
            </button>
          );
        })}
      </div>
      <div className="mt-1 flex justify-between text-[11px] text-vp-muted">
        <span>Not at all</span>
        <span>Absolutely</span>
      </div>

      <label className="mt-3 block text-xs text-vp-muted">
        Your name (optional)
        <input
          value={name}
          disabled={sent}
          maxLength={80}
          autoComplete="name"
          onChange={(event) => setName(event.target.value)}
          className={inputClass}
        />
      </label>
      <label className="mt-2 block text-xs text-vp-muted">
        Suggestions, or what you think (optional)
        <textarea
          rows={3}
          value={comment}
          disabled={sent}
          maxLength={2000}
          onChange={(event) => setComment(event.target.value)}
          className={inputClass}
        />
      </label>

      <div className="mt-3 flex flex-wrap items-center gap-2">
        <button type="submit" disabled={sent || rating === null} className={primaryButton}>
          {sent ? "Submitting…" : "Submit"}
        </button>
        <button type="button" disabled={sent} className={quietButton} onClick={() => finish({ skipped: true })}>
          Not now
        </button>
        {rating === null && !sent && <span className="text-[11px] text-vp-muted">Pick a number to submit.</span>}
      </div>
    </form>
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
  const hasName = Boolean(draft.sender_name?.trim());
  const hasEmail = /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test((draft.sender_email ?? "").trim());
  const valid = hasName && hasEmail && Boolean(draft.message?.trim());
  // The agent leaves name and email blank when it does not know them; this
  // panel is where the visitor supplies them.
  const needsDetails = !action.args.sender_name?.trim() || !action.args.sender_email?.trim();
  const missing = [!hasName && "your name", !hasEmail && "your email"].filter(Boolean).join(" and ");
  const fieldClass = (ok: boolean) =>
    ok || sent ? inputClass : inputClass.replace("border-vp-line", "border-vp-accent");

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
        Message to Pamudu · {needsDetails ? "add your details and review" : "review before sending"}
      </p>
      <div className="mt-3 grid gap-2 sm:grid-cols-2">
        <label className="text-xs text-vp-muted">
          Your name
          <input
            {...field("sender_name")}
            className={fieldClass(hasName)}
            placeholder="Your name"
            autoComplete="name"
            autoFocus={!action.args.sender_name?.trim()}
          />
        </label>
        <label className="text-xs text-vp-muted">
          Your email
          <input
            type="email"
            {...field("sender_email")}
            className={fieldClass(hasEmail)}
            placeholder="you@example.com"
            autoComplete="email"
            autoFocus={Boolean(action.args.sender_name?.trim()) && !action.args.sender_email?.trim()}
          />
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
        <span className="text-[11px] text-vp-muted">
          {!sent && missing
            ? `Add ${missing} to send.`
            : "Only Pamudu receives this. He can reply to your email."}
        </span>
      </div>
    </div>
  );
}
