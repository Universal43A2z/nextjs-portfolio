import Image from "next/image";

type Project = {
  category: string;
  badge?: string;
  title: string;
  description: string;
  result: string;
  tags: string[];
  links: { label: string; href: string; primary?: boolean }[];
  image?: { src: string; alt: string };
};

const projects: Project[] = [
  {
    category: "Full-stack · Team project",
    badge: "PHINMA AI Builder Workshop · 2026 Champion",
    title: "Dugtong — OJT Hour Tracker",
    description:
      "Replaces paper OJT records with student hour submissions, coordinator approvals, and printable reports. Built by the champion team at the PHINMA AI Builder Workshop and deployed with Supabase.",
    result: "Award-winning team project · live deployment",
    tags: ["Next.js", "TypeScript", "Supabase", "PostgreSQL", "Role-based access"],
    image: {
      src: "/projects/dugtong-hero.jpg",
      alt: "Dugtong OJT platform landing page and student time-tracking dashboard",
    },
    links: [
      { label: "GitHub", href: "https://github.com/Universal43A2z/DugtongOJT" },
      { label: "Live App", href: "https://dugtong-ojt.vercel.app", primary: true },
    ],
  },
  {
    category: "Full-stack · Cybersecurity education",
    title: "F1 STACKMIND Cyber Academy",
    description:
      "A live platform for an 8-week cybersecurity mentoring program. It brings weekly lessons, server-scored timed quizzes, attendance, mentor review, and audit logs into one workflow.",
    result: "8-week program · mentor and mentee workflows",
    tags: ["Next.js", "TypeScript", "Supabase", "PostgreSQL RLS", "Zod"],
    image: {
      src: "/projects/cyber-academy-hero.jpg",
      alt: "F1 STACKMIND Cyber Academy landing page and training capabilities",
    },
    links: [
      { label: "GitHub", href: "https://github.com/Universal43A2z/cyber-academy" },
      { label: "Live App", href: "https://cyber-academy-sooty.vercel.app", primary: true },
    ],
  },
  {
    category: "Security · Full-stack",
    title: "Cyber CTF Platform",
    description:
      "A hands-on Capture The Flag platform with challenges across cryptography, forensics, OSINT, and web security, plus challenge downloads and a leaderboard admin panel.",
    result: "58 challenges · 6 categories",
    tags: ["Node.js", "Express", "bcrypt", "CSRF protection", "Rate limiting"],
    links: [
      { label: "GitHub", href: "https://github.com/Universal43A2z/ctf-project", primary: true },
    ],
  },
  {
    category: "TypeScript · Developer tooling",
    title: "Workflow Runner — No-Code Workflow Engine",
    description:
      "A TypeScript engine for defining and running YAML or JSON workflows. Includes typed HTTP and delay steps, a step-by-step run log, an authenticated REST API, Docker support, and Vitest tests.",
    result: "YAML/JSON workflows · Docker and CI",
    tags: ["TypeScript", "REST API", "State machine", "Docker", "Vitest"],
    links: [
      {
        label: "GitHub",
        href: "https://github.com/Universal43A2z/vanilla-workflow-edito",
        primary: true,
      },
    ],
  },
];

export function Projects() {
  return (
    <section id="projects" className="scroll-mt-24 py-20">
      <div className="mx-auto max-w-[1080px] px-6">
        <div className="mb-9 max-w-3xl">
          <p className="mb-3 font-mono text-xs font-semibold tracking-[0.16em] text-accent">
            SELECTED WORK
          </p>
          <h2 className="text-3xl font-extrabold md:text-4xl">
            Projects built to solve real problems.
          </h2>
          <p className="mt-3 leading-relaxed text-muted">
            A mix of shipped products, security-focused learning tools, and
            engineering systems. Each project links to its source or live demo.
          </p>
        </div>
        <div className="grid gap-6 md:grid-cols-2">
          {projects.map((project) => (
            <article
              key={project.title}
              className="group flex flex-col overflow-hidden rounded-2xl border border-border bg-card transition-colors hover:border-accent-dim focus-within:border-accent-dim"
            >
              {project.image && (
                <div className="relative aspect-[16/9] overflow-hidden border-b border-border bg-bg-alt">
                  <Image
                    src={project.image.src}
                    alt={project.image.alt}
                    fill
                    sizes="(min-width: 768px) 50vw, 100vw"
                    className="object-cover object-top transition-transform duration-500 group-hover:scale-[1.02]"
                  />
                </div>
              )}
              <div className="flex flex-1 flex-col p-5 sm:p-6">
                <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
                  <p className="font-mono text-xs font-semibold tracking-wide text-accent">
                    {project.category}
                  </p>
                  {project.badge && (
                    <span className="rounded-full border border-accent-dim bg-accent/10 px-3 py-1 font-mono text-xs font-semibold text-accent">
                      {project.badge}
                    </span>
                  )}
                </div>
                <h3 className="text-xl font-bold leading-snug">
                  {project.title}
                </h3>
                <p className="mt-3 text-sm leading-relaxed text-muted">
                  {project.description}
                </p>
                <p className="mt-4 text-sm font-semibold text-text">
                  {project.result}
                </p>
                <ul className="mt-4 flex flex-wrap gap-2" aria-label="Technologies">
                  {project.tags.map((tag) => (
                    <li
                      key={tag}
                      className="rounded-md border border-border bg-bg-alt px-2.5 py-1 font-mono text-xs text-muted"
                    >
                      {tag}
                    </li>
                  ))}
                </ul>
                <div className="mt-auto flex flex-wrap gap-2.5 pt-6">
                  {project.links.map((link) => (
                    <a
                      key={link.label}
                      href={link.href}
                      target="_blank"
                      rel="noreferrer"
                      className={
                        link.primary
                          ? "rounded-md bg-accent px-4 py-2 text-sm font-semibold text-[#06211a] transition-colors hover:bg-accent-dim"
                          : "rounded-md border border-border px-4 py-2 text-sm font-semibold text-text transition-colors hover:border-accent hover:text-accent"
                      }
                    >
                      {link.label} <span aria-hidden="true">↗</span>
                    </a>
                  ))}
                </div>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
