export function Hero() {
  return (
    <header
      id="home"
      className="hero-shell border-b border-border py-16 md:py-24"
    >
      <div className="hero-content mx-auto grid max-w-[1080px] items-center gap-10 px-6 md:grid-cols-[1.1fr_0.9fr] md:gap-14">
        <div>
          <p className="hero-enter hero-enter-1 mb-5 inline-flex rounded-full border border-accent-dim bg-accent/10 px-3 py-1 font-mono text-xs font-semibold text-accent">
            <span className="pulse-dot mr-2 size-1.5 rounded-full bg-accent" aria-hidden="true" />
            FULL-STACK DEVELOPMENT · SECURITY FOCUS
          </p>
          <h1 className="hero-enter hero-enter-2 text-4xl font-extrabold leading-tight tracking-tight md:text-5xl">
            Hi, I&apos;m <span className="text-accent">Khent Vincent C. Amor</span>
          </h1>
          <p className="hero-enter hero-enter-3 mt-5 max-w-[560px] text-xl font-semibold leading-snug text-text">
            I build useful web products with security in mind.
          </p>
          <p className="hero-enter hero-enter-4 mt-3 max-w-[560px] text-base leading-relaxed text-muted md:text-lg">
            Full-stack developer working across React, Next.js, Node.js, and
            PostgreSQL—with hands-on experience in cybersecurity training and
            network deployment.
          </p>
          <div className="hero-enter hero-enter-5 mt-8 flex flex-wrap gap-3">
            <a
              href="#projects"
              className="rounded-lg bg-accent px-5 py-3 font-semibold text-[#06211a] transition-colors hover:bg-accent-dim"
            >
              Explore My Work
            </a>
            <a
              href="/resume.pdf"
              download
              className="rounded-lg border border-border px-5 py-3 font-semibold text-text transition-colors hover:border-accent hover:text-accent"
            >
              Download Resume
            </a>
          </div>
          <a
            href="https://github.com/Universal43A2z"
            target="_blank"
            rel="noreferrer"
            className="hero-enter hero-enter-6 mt-5 inline-block font-mono text-sm text-muted transition-colors hover:text-accent"
          >
            GitHub: Universal43A2z ↗
          </a>
        </div>

        <aside className="hero-feature-card rounded-2xl border border-border bg-card p-6 shadow-[0_24px_60px_rgba(0,0,0,0.28)] md:p-7">
          <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
            <p className="font-mono text-xs font-semibold tracking-[0.14em] text-accent">
              RECENT RECOGNITION
            </p>
            <span className="rounded-full border border-accent-dim px-3 py-1 font-mono text-xs text-accent">
              2026
            </span>
          </div>
          <p className="text-sm font-semibold text-muted">
            PHINMA AI Builder Workshop · Champion team
          </p>
          <h2 className="mt-3 text-2xl font-bold leading-tight">
            Dugtong — OJT Hour Tracker
          </h2>
          <p className="mt-3 text-sm leading-relaxed text-muted">
            A team-built platform that replaces paper hour logs with student
            submissions, coordinator approvals, and printable reports.
          </p>
          <div className="mt-5 flex flex-wrap gap-2">
            {["Next.js", "TypeScript", "Supabase"].map((item) => (
              <span
                key={item}
                className="rounded-md border border-border bg-bg-alt px-2.5 py-1 font-mono text-xs text-muted"
              >
                {item}
              </span>
            ))}
          </div>
          <a
            href="https://dugtong-ojt.vercel.app"
            target="_blank"
            rel="noreferrer"
            className="mt-6 inline-flex items-center gap-2 font-semibold text-accent transition-colors hover:text-text"
          >
            See the live project <span aria-hidden="true">↗</span>
          </a>
        </aside>
      </div>
    </header>
  );
}
