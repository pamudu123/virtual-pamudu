import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";

import "@copilotkit/react-core/v2/styles.css";
import "./globals.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Pamudu Ranasinghe · AI Engineer",
  description:
    "Ask Pamudu's AI assistant about his experience, projects, research, articles and videos.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable}`}>
      <body className="antialiased">{children}</body>
    </html>
  );
}
