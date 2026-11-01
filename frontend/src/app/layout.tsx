import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Project Udyam Digital | Accel Telecom B2B",
  description: "Digital acquisition and onboarding for India's 6 Crore+ MSMEs in one sitting.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50 text-slate-900 antialiased flex flex-col font-sans">
        {/* Top Telecom Brand Bar */}
        <header className="sticky top-0 z-50 bg-white border-b border-slate-200 shadow-sm">
          <div className="max-w-4xl mx-auto px-4 py-2.5 flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-red-600 flex items-center justify-center font-bold text-white tracking-wider text-sm shadow">
                UD
              </div>
              <div>
                <span className="font-extrabold text-base tracking-tight text-slate-900 block leading-tight">
                  Udyam<span className="text-red-600">Digital</span>
                </span>
                <span className="text-[10px] text-slate-500 font-medium tracking-wide block uppercase">
                  Accel Telecom B2B
                </span>
              </div>
            </Link>

            {/* Navigation pills */}
            <nav className="flex items-center gap-1 sm:gap-2 text-xs font-semibold">
              <Link
                href="/"
                className="px-2.5 py-1.5 rounded-md hover:bg-slate-100 text-slate-700 transition"
              >
                Advisor
              </Link>
              <Link
                href="/quote"
                className="px-2.5 py-1.5 rounded-md hover:bg-slate-100 text-slate-700 transition"
              >
                Quote
              </Link>
              <Link
                href="/kyc"
                className="px-2.5 py-1.5 rounded-md hover:bg-slate-100 text-slate-700 transition"
              >
                KYC
              </Link>
              <Link
                href="/tracker"
                className="px-2.5 py-1.5 rounded-md hover:bg-slate-100 text-slate-700 transition"
              >
                Tracker
              </Link>
              <Link
                href="/partner"
                className="px-2.5 py-1.5 rounded-md bg-slate-900 text-white hover:bg-slate-800 transition shadow-sm"
              >
                Partner Desk
              </Link>
            </nav>
          </div>
        </header>

        {/* DPDP Compliance Notice Badge */}
        <div className="bg-red-50 border-b border-red-100 px-4 py-1 text-center text-[11px] text-red-800 font-medium">
          🔒 DPDP Act 2023 Compliant · Zero-Hallucination Deterministic Engine · 15-Minute Digital Onboarding
        </div>

        {/* Main Content Area (Mobile viewport constrained) */}
        <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-6">
          {children}
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-slate-200 py-4 text-center text-xs text-slate-400">
          Project Udyam Digital · Enterprise Track A Submission · Airtel SYNC
        </footer>
      </body>
    </html>
  );
}
