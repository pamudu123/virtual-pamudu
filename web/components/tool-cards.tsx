"use client";

import type { ReactNode } from "react";

// ---------- helpers ----------

export function parseResult<T>(result: string | undefined): T | null {
  if (!result) return null;
  try {
    return JSON.parse(result) as T;
  } catch {
    return null;
  }
}

function formatDate(value: string | undefined): string {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

function Frame({ label, children }: { label: string; children: ReactNode }) {
  return (
    <section className="my-3">
      <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.14em] text-vp-muted">{label}</p>
      {children}
    </section>
  );
}

function Tag({ children }: { children: ReactNode }) {
  return (
    <span className="rounded-full border border-vp-line bg-vp-surface-2 px-2 py-0.5 text-[11px] text-vp-muted">
      {children}
    </span>
  );
}

function Skeleton({ label }: { label: string }) {
  return (
    <Frame label={label}>
      <div className="grid gap-3 sm:grid-cols-2">
        {[0, 1].map((i) => (
          <div key={i} className="h-24 animate-pulse rounded-xl border border-vp-line bg-vp-surface-2" />
        ))}
      </div>
    </Frame>
  );
}

// ---------- status pill for background work ----------

export function StatusPill({ text, done }: { text: string; done: boolean }) {
  return (
    <div className="my-1.5 inline-flex items-center gap-2 rounded-full border border-vp-line bg-vp-surface-2 px-3 py-1 text-xs text-vp-muted">
      <span
        className={
          done ? "h-1.5 w-1.5 rounded-full bg-vp-accent" : "h-1.5 w-1.5 animate-pulse rounded-full bg-vp-accent"
        }
      />
      {text}
    </div>
  );
}

// ---------- GitHub ----------

type Repo = {
  name: string;
  description: string;
  language: string;
  stars: number;
  updated: string;
  url: string;
};

export function RepoCards({ result, done }: { result?: string; done: boolean }) {
  if (!done) return <Skeleton label="GitHub" />;
  const repos = parseResult<{ repos?: Repo[] }>(result)?.repos ?? [];
  if (repos.length === 0) return <StatusPill text="No matching repositories" done />;
  return (
    <Frame label="GitHub">
      <div className="grid gap-3 sm:grid-cols-2">
        {repos.map((repo) => (
          <a
            key={repo.url}
            href={repo.url}
            target="_blank"
            rel="noreferrer"
            className="group flex flex-col rounded-xl border border-vp-line bg-vp-surface p-4 transition hover:-translate-y-0.5 hover:border-vp-accent hover:shadow-md"
          >
            <span className="font-mono text-sm font-semibold text-vp-ink group-hover:text-vp-accent">
              {repo.name}
            </span>
            <span className="mt-1 line-clamp-2 flex-1 text-[13px] leading-snug text-vp-muted">
              {repo.description || "No description"}
            </span>
            <span className="mt-3 flex items-center gap-3 text-[11px] text-vp-muted">
              {repo.language && (
                <span className="flex items-center gap-1">
                  <span className="h-2 w-2 rounded-full bg-vp-accent" />
                  {repo.language}
                </span>
              )}
              {repo.stars > 0 && <span>★ {repo.stars}</span>}
              {repo.updated && <span>Updated {formatDate(repo.updated)}</span>}
            </span>
          </a>
        ))}
      </div>
    </Frame>
  );
}

// ---------- Medium ----------

type Article = {
  title: string;
  date: string;
  url: string;
  preview: string;
  image: string;
  tags: string[];
};

export function ArticleCards({ result, done }: { result?: string; done: boolean }) {
  if (!done) return <Skeleton label="Writing" />;
  const articles = parseResult<{ articles?: Article[] }>(result)?.articles ?? [];
  if (articles.length === 0) return <StatusPill text="No matching articles" done />;
  return (
    <Frame label="Writing">
      <div className="flex flex-col gap-3">
        {articles.map((article) => (
          <a
            key={article.url}
            href={article.url}
            target="_blank"
            rel="noreferrer"
            className="group flex gap-4 rounded-xl border border-vp-line bg-vp-surface p-3 transition hover:border-vp-accent hover:shadow-md"
          >
            {article.image && (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={article.image}
                alt=""
                loading="lazy"
                className="hidden h-20 w-28 shrink-0 rounded-lg object-cover sm:block"
              />
            )}
            <span className="flex min-w-0 flex-col">
              <span className="text-sm font-semibold leading-snug text-vp-ink group-hover:text-vp-accent">
                {article.title}
              </span>
              <span className="mt-1 line-clamp-2 text-[13px] leading-snug text-vp-muted">{article.preview}</span>
              <span className="mt-2 flex flex-wrap items-center gap-2 text-[11px] text-vp-muted">
                <span>{formatDate(article.date)}</span>
                {article.tags?.slice(0, 3).map((tag) => <Tag key={tag}>{tag}</Tag>)}
              </span>
            </span>
          </a>
        ))}
      </div>
    </Frame>
  );
}

// ---------- YouTube ----------

type Video = {
  title: string;
  video_id: string;
  url: string;
  published: string;
  thumbnail: string;
};

export function VideoCards({ result, done }: { result?: string; done: boolean }) {
  if (!done) return <Skeleton label="Videos" />;
  const videos = parseResult<{ videos?: Video[] }>(result)?.videos ?? [];
  if (videos.length === 0) return <StatusPill text="No matching videos" done />;
  return (
    <Frame label="Videos">
      <div className="grid gap-3 sm:grid-cols-2">
        {videos.map((video) => (
          <a
            key={video.video_id}
            href={video.url}
            target="_blank"
            rel="noreferrer"
            className="group overflow-hidden rounded-xl border border-vp-line bg-vp-surface transition hover:-translate-y-0.5 hover:border-vp-accent hover:shadow-md"
          >
            <span className="relative block aspect-video bg-vp-surface-2">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={video.thumbnail} alt="" loading="lazy" className="h-full w-full object-cover" />
              <span className="absolute inset-0 flex items-center justify-center">
                <span className="flex h-10 w-10 items-center justify-center rounded-full bg-black/65 text-white transition group-hover:bg-vp-accent">
                  ▶
                </span>
              </span>
            </span>
            <span className="block p-3">
              <span className="line-clamp-2 text-sm font-semibold leading-snug text-vp-ink">{video.title}</span>
              <span className="mt-1 block text-[11px] text-vp-muted">{formatDate(video.published)}</span>
            </span>
          </a>
        ))}
      </div>
    </Frame>
  );
}

// ---------- Profile sections ----------

type ProfileItem = {
  title?: string;
  subtitle?: string;
  period?: string;
  description?: string;
  tags?: string[];
  url?: string;
};

type ProfileSectionArgs = {
  section?: string;
  heading?: string;
  items?: ProfileItem[];
};

export function ProfileSection({ args }: { args: ProfileSectionArgs | undefined }) {
  const section = args?.section ?? "";
  const items = (args?.items ?? []).filter((item) => item && item.title);
  const heading = args?.heading || section || "Profile";
  if (items.length === 0) return <StatusPill text={`Preparing ${heading.toLowerCase()}`} done={false} />;

  if (section === "skills") {
    return (
      <Frame label={heading}>
        <div className="flex flex-col gap-3 rounded-xl border border-vp-line bg-vp-surface p-4">
          {items.map((item) => (
            <div key={item.title}>
              <p className="text-sm font-semibold text-vp-ink">{item.title}</p>
              <div className="mt-1.5 flex flex-wrap gap-1.5">
                {(item.tags ?? []).map((tag) => (
                  <span
                    key={tag}
                    className="rounded-full bg-vp-accent-soft px-2.5 py-1 text-xs font-medium text-vp-accent"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </Frame>
    );
  }

  if (section === "experience" || section === "education") {
    return (
      <Frame label={heading}>
        <ol className="relative ml-2 border-l border-vp-line">
          {items.map((item, index) => (
            <li key={`${item.title}-${index}`} className="relative pb-5 pl-6 last:pb-0">
              <span className="absolute -left-[5px] top-1.5 h-2.5 w-2.5 rounded-full border-2 border-vp-surface bg-vp-accent" />
              <p className="text-[11px] font-medium uppercase tracking-wide text-vp-muted">{item.period}</p>
              <p className="mt-0.5 text-sm font-semibold text-vp-ink">{item.title}</p>
              {item.subtitle && <p className="text-[13px] text-vp-accent">{item.subtitle}</p>}
              {item.description && (
                <p className="mt-1 text-[13px] leading-snug text-vp-muted">{item.description}</p>
              )}
              {item.tags && item.tags.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {item.tags.map((tag) => <Tag key={tag}>{tag}</Tag>)}
                </div>
              )}
            </li>
          ))}
        </ol>
      </Frame>
    );
  }

  // projects, awards, publications
  return (
    <Frame label={heading}>
      <div className="grid gap-3 sm:grid-cols-2">
        {items.map((item, index) => {
          const body = (
            <>
              <span className="text-sm font-semibold leading-snug text-vp-ink">{item.title}</span>
              {(item.subtitle || item.period) && (
                <span className="mt-0.5 text-[12px] text-vp-accent">
                  {[item.subtitle, item.period].filter(Boolean).join(" · ")}
                </span>
              )}
              {item.description && (
                <span className="mt-1.5 flex-1 text-[13px] leading-snug text-vp-muted">{item.description}</span>
              )}
              {item.tags && item.tags.length > 0 && (
                <span className="mt-2.5 flex flex-wrap gap-1.5">
                  {item.tags.map((tag) => <Tag key={tag}>{tag}</Tag>)}
                </span>
              )}
            </>
          );
          const className =
            "flex flex-col rounded-xl border border-vp-line bg-vp-surface p-4 transition hover:border-vp-accent hover:shadow-md";
          return item.url ? (
            <a key={index} href={item.url} target="_blank" rel="noreferrer" className={className}>
              {body}
            </a>
          ) : (
            <div key={index} className={className}>
              {body}
            </div>
          );
        })}
      </div>
    </Frame>
  );
}

// ---------- Contact card ----------

type Contact = {
  name: string;
  roles: string[];
  location: string;
  links: Record<string, string>;
};

const LINK_LABELS: Record<string, string> = {
  linkedin: "LinkedIn",
  github: "GitHub",
  youtube: "YouTube",
  google_scholar: "Google Scholar",
  medium: "Medium",
};

export function ContactCard({ result, done }: { result?: string; done: boolean }) {
  const contact = parseResult<Contact>(result);
  if (!done || !contact) return <StatusPill text="Getting contact links" done={false} />;
  return (
    <Frame label="Connect">
      <div className="rounded-xl border border-vp-line bg-vp-surface p-4">
        <p className="text-base font-semibold text-vp-ink">{contact.name}</p>
        <p className="text-[13px] text-vp-muted">
          {[contact.roles?.[0], contact.location].filter(Boolean).join(" · ")}
        </p>
        <div className="mt-3 flex flex-wrap gap-2">
          {Object.entries(contact.links ?? {}).map(([key, href]) => (
            <a
              key={key}
              href={href}
              target="_blank"
              rel="noreferrer"
              className="rounded-full border border-vp-line px-3 py-1.5 text-xs font-medium text-vp-ink transition hover:border-vp-accent hover:text-vp-accent"
            >
              {LINK_LABELS[key] ?? key} ↗
            </a>
          ))}
        </div>
      </div>
    </Frame>
  );
}

// ---------- Todo list ----------

type Todo = { content: string; status: "pending" | "in_progress" | "completed" };

export function TodoList({ todos }: { todos: Todo[] | undefined }) {
  if (!todos || todos.length === 0) return null;
  return (
    <Frame label="Plan">
      <ul className="flex flex-col gap-1.5 rounded-xl border border-vp-line bg-vp-surface p-3">
        {todos.map((todo, index) => (
          <li key={index} className="flex items-start gap-2 text-[13px]">
            <span
              className={
                todo.status === "completed"
                  ? "mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-vp-accent text-[10px] text-white"
                  : todo.status === "in_progress"
                    ? "mt-0.5 h-4 w-4 shrink-0 animate-pulse rounded-full border-2 border-vp-accent"
                    : "mt-0.5 h-4 w-4 shrink-0 rounded-full border-2 border-vp-line"
              }
            >
              {todo.status === "completed" ? "✓" : ""}
            </span>
            <span className={todo.status === "completed" ? "text-vp-muted line-through" : "text-vp-ink"}>
              {todo.content}
            </span>
          </li>
        ))}
      </ul>
    </Frame>
  );
}
