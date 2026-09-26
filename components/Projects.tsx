import Image from "next/image";

type Project = {
  icon: string;
  tag: string;
  title: string;
  description: string;
  tags: string[];
  links: { label: string; href: string; download?: boolean }[];
  image?: string;
};

const projects: Project[] = [
  {
    icon: "🎓",
    tag: "Full-Stack · Next.js + Supabase",
    title: "F1 STACKMIND Cyber Academy — Cybersecurity Training Platform",
    description:
      "A live mentor-and-mentee learning platform for an 8-week cybersecurity program. Mentees read weekly lessons, take anti-copy timed quizzes scored entirely on the server, mark attendance, and send feedback reports; mentors publish content, build quizzes, review mentee performance, resolve feedback, and read a full audit log. Deployed on Vercel with a Supabase backend (Postgres with Row Level Security on every table, OTP-verified accounts, MENTOR access-code signup, rate limiting, CSP/HSTS headers, and an 8-layer security model).",
    tags: ["Next.js", "React", "TypeScript", "Supabase", "PostgreSQL", "RLS", "Tailwind", "Zod", "Vercel"],
    links: [
      { label: "GitHub", href: "https://github.com/Universal43A2z/cyber-academy" },
      { label: "Live App", href: "https://cyber-academy-sooty.vercel.app" },
    ],
  },
  {
    icon: "🧩",
    tag: "Vanilla JS · Engine",
    title: "Workflow Runner — No-Code Workflow Engine",
    description:
      "Design workflows in YAML or JSON and run them on an event-driven engine built with pure JavaScript and Vite. Features a state machine (running/paused/done), typed HTTP steps, delays, a hand-written YAML parser, live step-by-step run log, and a mock API client — fully unit-tested with Vitest. Ships with a sample 'Security Alert Response' workflow.",
    tags: ["JavaScript", "Vite", "State Machine", "YAML", "Events", "Vitest"],
    links: [
      {
        label: "GitHub",
        href: "https://github.com/yourusername/vanilla-workflow-editor",
      },
    ],
  },
  {
    icon: "🏴",
    tag: "Full-Stack",
    title: "Cyber CTF Platform",
    description:
      "Full-stack Capture The Flag platform with 58 challenges across 6 categories — cryptography, forensics, OSINT, and web exploitation. Includes secure auth (bcrypt, CSRF, rate limiting, account lockout), downloadable challenge files, and a leaderboard admin panel.",
    tags: ["Node.js", "Express", "EJS", "Helmet", "bcrypt"],
    links: [
      { label: "GitHub", href: "https://github.com/yourusername/ctf-project" },
    ],
  },
  {
    icon: "🛡️",
    tag: "Security Program",
    title: "Cyber Security Awareness Program",
    description:
      "Designed a month-long campus cyber security awareness initiative — program proposal, Knowledge Day & Skills Day schedules, interactive sessions, and slide decks on phishing, password hygiene, and safe browsing.",
    tags: ["Program Design", "Presentations", "Security Awareness"],
    links: [
      {
        label: "GitHub",
        href: "https://github.com/yourusername/cyber-awareness-program",
      },
    ],
  },
  {
    icon: "⚙️",
    tag: "Backend",
    title: "Node.js Server Practice",
    description:
      "Hands-on Node.js exercises: an HTTP server with routing and 404 handling, plus filesystem scripts for reading and writing data — the fundamentals of server-side JavaScript.",
    tags: ["Node.js", "HTTP", "File System"],
    links: [
      { label: "GitHub", href: "https://github.com/yourusername/nodejs-practice" },
    ],
  },
  {
    icon: "🗄️",
    tag: "Database",
    title: "Advanced Database Module",
    description:
      "Modular Node.js program demonstrating student records with modules, callbacks, arrays, objects, and control flow — applying database concepts in real JavaScript code.",
    tags: ["Node.js", "Modules", "Callbacks", "OOP"],
    links: [
      {
        label: "GitHub",
        href: "https://github.com/yourusername/advanced-database-module",
      },
    ],
  },
  {
    icon: "📡",
    tag: "Python · Security",
    title: "NetRecon v2 — Reconnaissance Framework",
    description:
      "Powerful, dependency-free network recon framework. Expands CIDR blocks and ranges, discovers live hosts, scans ports with profiles, fingerprints services/TLS, grades HTTP security headers (A–F), guesses OS from TTL, runs traceroute, and exports JSON/CSV/HTML reports.",
    tags: ["Python", "CIDR", "Service Detection", "TLS", "HTTP Audit", "Reporting"],
    links: [
      { label: "GitHub", href: "https://github.com/yourusername/netrecon" },
      {
        label: "Download",
        href: "/projects/python-network-scanner/netrecon.py",
        download: true,
      },
    ],
  },
  {
    icon: "🔑",
    tag: "Python · Security",
    title: "PassAudit — Password Auditor",
    description:
      "Identity-security tool that scores password strength (entropy, pattern detection, crack-time estimate) and performs authorized dictionary attacks against MD5/SHA1/SHA256/SHA512 hashes using leetspeak and suffix mutation rules. Batch-audits password files with JSON export.",
    tags: ["Python", "Hashing", "Entropy", "Dictionary Attack", "Regex"],
    links: [
      { label: "GitHub", href: "https://github.com/yourusername/passaudit" },
      {
        label: "Download",
        href: "/projects/python-password-auditor/passaudit.py",
        download: true,
      },
    ],
  },
  {
    icon: "☕",
    tag: "Java · GUI + Backend",
    title: "BankSystem — Banking Engine + Swing GUI",
    description:
      "Concurrent retail-banking engine with a desktop Swing GUI and a CLI. Open accounts, deposit, withdraw, and transfer money while an immutable audit ledger updates live — then run a stress test that proves the totals still balance under load. Exact integer money math and deadlock-free lock ordering.",
    tags: ["Java", "Swing GUI", "Concurrency", "Records", "Audit Trail"],
    image: "/projects/java-bank-system/screenshot.png",
    links: [
      { label: "GitHub", href: "https://github.com/yourusername/bank-system" },
      {
        label: "GUI",
        href: "/projects/java-bank-system/BankSystemGui.java",
        download: true,
      },
      {
        label: "CLI",
        href: "/projects/java-bank-system/BankSystem.java",
        download: true,
      },
    ],
  },
  {
    icon: "🌐",
    tag: "Java · REST API",
    title: "TaskAPI — Dependency-Free REST API",
    description:
      "REST API built on the JDK's built-in HTTP server — no frameworks or dependencies. Full CRUD with correct status codes, a hand-written recursive-descent JSON parser, thread-pooled handling, CORS, request logging, validation, and file-backed persistence across restarts.",
    tags: ["Java", "REST", "HTTP", "JSON", "Concurrency", "Persistence"],
    links: [
      { label: "GitHub", href: "https://github.com/yourusername/task-api" },
      {
        label: "Download",
        href: "/projects/java-rest-api/TaskApi.java",
        download: true,
      },
    ],
  },
];

export function Projects() {
  return (
    <section id="projects" className="py-20">
      <div className="mx-auto max-w-[1080px] px-6">
        <p className="font-mono text-sm text-accent">{"// projects"}</p>
        <h2 className="mt-2 mb-9 text-3xl font-extrabold">Featured Work</h2>
        <div className="grid gap-6 md:grid-cols-2">
          {projects.map((project) => (
            <article
              key={project.title}
              className="flex flex-col rounded-xl border border-border bg-card p-6 transition-all hover:-translate-y-1 hover:border-accent-dim"
            >
              {project.image && (
                <a href={project.image} target="_blank" rel="noreferrer">
                  <Image
                    src={project.image}
                    alt={`${project.title} screenshot`}
                    width={940}
                    height={643}
                    className="mb-4 block h-[180px] w-full rounded-lg border border-border object-cover object-top hover:opacity-85"
                  />
                </a>
              )}
              <div className="mb-3.5 flex items-center justify-between">
                <span className="text-[1.6rem]">{project.icon}</span>
                <span className="rounded-full border border-accent-dim px-2.5 py-1 font-mono text-xs text-accent">
                  {project.tag}
                </span>
              </div>
              <h3 className="mb-2.5 text-xl font-bold">{project.title}</h3>
              <p className="mb-4 flex-grow text-sm leading-relaxed text-muted">
                {project.description}
              </p>
              <div className="mb-4 flex flex-wrap gap-2">
                {project.tags.map((tag) => (
                  <span
                    key={tag}
                    className="rounded border border-border bg-bg-alt px-2.5 py-1 font-mono text-xs text-muted"
                  >
                    {tag}
                  </span>
                ))}
              </div>
              <div className="flex flex-wrap gap-2.5">
                {project.links.map((link) => (
                  <a
                    key={link.label}
                    href={link.href}
                    download={link.download}
                    target={link.download ? undefined : "_blank"}
                    rel={link.download ? undefined : "noreferrer"}
                    className={
                      link.download
                        ? "rounded-md border border-border px-4 py-2 text-sm font-semibold text-text transition-colors hover:border-accent hover:text-accent"
                        : "rounded-md bg-accent px-4 py-2 text-sm font-semibold text-[#06211a] transition-colors hover:bg-accent-dim"
                    }
                  >
                    {link.label}
                  </a>
                ))}
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}