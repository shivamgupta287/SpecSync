import type { Metadata } from "next";
import { Geist } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geist = Geist({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "SpecSync",
  description: "Search phones and brands from GSMArena with AI assistance",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className={`${geist.className} min-h-full flex flex-col bg-gray-950 text-gray-100`}>
        <nav className="border-b border-gray-800 px-6 py-4 flex gap-6 items-center">
          <Link href="/" className="font-bold text-lg text-white">
            SpecSync
          </Link>
          <Link href="/" className="text-gray-400 hover:text-white text-sm transition-colors">
            Search
          </Link>
          <Link href="/ai" className="text-gray-400 hover:text-white text-sm transition-colors">
            AI Recommend
          </Link>
        </nav>
        <main className="flex-1 max-w-5xl w-full mx-auto px-6 py-10">{children}</main>
      </body>
    </html>
  );
}
