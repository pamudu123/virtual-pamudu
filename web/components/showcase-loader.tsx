"use client";

import dynamic from "next/dynamic";

// The chat is fully interactive and per-visitor, so it renders in the browser
// only. The server sends the page shell and this placeholder.
const Showcase = dynamic(() => import("./showcase").then((m) => m.Showcase), {
  ssr: false,
  loading: () => (
    <div className="flex h-dvh items-center justify-center text-sm text-vp-muted">Loading…</div>
  ),
});

export function ShowcaseLoader({ embedded = false }: { embedded?: boolean }) {
  return <Showcase embedded={embedded} />;
}
