export function Experience() {
  const experiences = [
    {
      role: "Starlink Deployment Team Member",
      org: "Department of Information and Communications Technology (DICT)",
      date: "2 months",
      description:
        "Installed and configured Starlink WiFi systems in public schools to bring internet access to underserved communities. Handled on-site setup of satellite dishes, routers, and network wiring, ensuring stable connectivity and proper configuration.",
      tags: ["Networking", "Starlink", "Router Config", "Field Deployment", "Public Schools"],
    },
    {
      role: "Freelance Web Developer & IT Support",
      org: "Self-employed",
      date: "2024 – Present",
      description:
        "Develop and maintain web applications for clients; collaborated directly with clients to gather and implement requirements. Troubleshot hardware, software, and network issues, wrote technical documentation for non-technical users, and set up Linux systems and development environments.",
      tags: ["Web Development", "Linux", "IT Support", "Client Work"],
    },
  ];

  return (
    <section id="experience" className="border-y border-border bg-bg-alt py-20">
      <div className="mx-auto max-w-[1080px] px-6">
        <p className="font-mono text-sm text-accent">{"// experience"}</p>
        <h2 className="mt-2 mb-9 text-3xl font-extrabold">
          Work &amp; Field Experience
        </h2>
        <div className="grid gap-[18px]">
          {experiences.map((exp) => (
            <article
              key={exp.role}
              className="rounded-xl border border-border bg-card p-6"
            >
              <div className="mb-2.5 flex flex-wrap items-start justify-between gap-4">
                <div>
                  <h3 className="text-lg font-bold">{exp.role}</h3>
                  <p className="mt-1 font-mono text-xs text-accent">{exp.org}</p>
                </div>
                <span className="whitespace-nowrap rounded-full border border-border px-3.5 py-1.5 font-mono text-xs text-muted">
                  {exp.date}
                </span>
              </div>
              <p className="mb-4 text-sm text-muted">{exp.description}</p>
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