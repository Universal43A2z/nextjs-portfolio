export function Experience() {
  const experiences = [
    {
      role: "Freelance Web Developer & IT Support",
      org: "Self-employed",
      date: "2024 – Present",
      details: [
        "Build and maintain client-facing web applications, working directly with clients to gather requirements and deliver updates.",
        "Troubleshoot hardware, software, and network issues; configure Linux environments and document solutions for non-technical users.",
      ],
      tags: ["Web Development", "Client Work", "Linux", "IT Support"],
    },
    {
      role: "Starlink Deployment Team Member",
      org: "Department of Information and Communications Technology (DICT)",
      date: "2-month field deployment",
      details: [
        "Installed and configured Starlink connectivity at public schools, including satellite hardware, routers, and network wiring.",
        "Performed on-site setup and connectivity troubleshooting to support reliable school internet access.",
      ],
      tags: ["Networking", "Starlink", "Router Configuration", "Field Deployment"],
    },
  ];

  return (
    <section
      id="experience"
      className="scroll-mt-24 border-y border-border bg-bg-alt py-20"
    >
      <div className="mx-auto max-w-[1080px] px-6">
        <p className="scroll-reveal mb-3 font-mono text-xs font-semibold tracking-[0.16em] text-accent">
          EXPERIENCE
        </p>
        <h2 className="scroll-reveal mb-9 text-3xl font-extrabold">Work experience</h2>
        <div className="grid gap-[18px]">
          {experiences.map((exp) => (
            <article
              key={exp.role}
              className="scroll-reveal motion-card rounded-xl border border-border bg-card p-6"
            >
              <div className="mb-2.5 flex flex-wrap items-start justify-between gap-4">
                <div>
                  <h3 className="text-lg font-bold">{exp.role}</h3>
                  <p className="mt-1 font-mono text-xs text-accent">{exp.org}</p>
                </div>
                <span className="rounded-full border border-border px-3.5 py-1.5 font-mono text-xs text-muted">
                  {exp.date}
                </span>
              </div>
              <ul className="mb-4 grid gap-2 text-sm leading-relaxed text-muted">
                {exp.details.map((detail) => (
                  <li key={detail} className="flex gap-2.5">
                    <span className="text-accent" aria-hidden="true">
                      ▸
                    </span>
                    <span>{detail}</span>
                  </li>
                ))}
              </ul>
              <div className="flex flex-wrap gap-2">
                {exp.tags.map((tag) => (
                  <span
                    key={tag}
                    className="rounded border border-border bg-bg-alt px-2.5 py-1 font-mono text-xs text-muted"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
