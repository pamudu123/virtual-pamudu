import type { Metadata } from "next";

import { ShowcaseLoader } from "@/components/showcase-loader";

// Chat only, no sidebar. Loaded in an iframe by the portfolio site's
// "Pamudu AI" panel, so it should not be indexed as a page of its own.
export const metadata: Metadata = {
  title: "Pamudu AI",
  robots: { index: false },
};

export default function Embed() {
  return <ShowcaseLoader embedded />;
}
