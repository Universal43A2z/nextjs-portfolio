import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Khent Vincent C. Amor | Security-Focused Full-Stack Developer",
  description:
    "Full-stack developer focused on secure, useful web products. Explore Khent Vincent C. Amor's projects in Next.js, TypeScript, cybersecurity education, and networking.",
  openGraph: {
    title: "Khent Vincent C. Amor | Security-Focused Full-Stack Developer",
    description:
      "Full-stack developer focused on secure, useful web products, cybersecurity education, and practical engineering.",
    type: "website",
    locale: "en_PH",
  },
  twitter: {
    card: "summary",
    title: "Khent Vincent C. Amor | Full-Stack Developer",
    description:
      "Full-stack developer focused on secure, useful web products.",
  },
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
