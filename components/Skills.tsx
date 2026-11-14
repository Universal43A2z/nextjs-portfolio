export function Skills() {
  const skills = [
    {
      title: "Primary full-stack tools",
      items: [
        "TypeScript",
        "JavaScript",
        "React",
        "Next.js",
        "Node.js",
        "Express",
        "REST APIs",
      ],
    },
    {
      title: "Data & platform",
      items: [
        "PostgreSQL",
        "Supabase",
        "Row-Level Security",
        "SQL",
        "Docker",
        "Vercel",
      ],
    },
    {
      title: "Application security",
      items: [
        "Secure authentication",
        "Input validation",
        "Web application security",
        "Burp Suite",
        "Wireshark",
        "nmap",
        "CTF design",
      ],
    },
    {
      title: "Networking & additional tools",
      items: [
        "TCP/IP",
        "Starlink deployment",
        "Linux / Bash",
        "Git / GitHub",
        "Python",
        "Java",
        "HTML / CSS",
        "Tailwind CSS",
      ],
    },
  ];

  return (
    <section
      id="skills"
      className="scroll-mt-24 border-y border-border bg-bg-alt py-20"
    >
      <div className="mx-auto max-w-[1080px] px-6">
        <p className="mb-3 font-mono text-xs font-semibold tracking-[0.16em] text-accent">
          CAPABILITIES
        </p>
        <h2 className="mb-9 text-3xl font-extrabold md:text-4xl">
          Tools I use to deliver
        </h2>
        <div className="grid gap-[18px] md:grid-cols-2">
          {skills.map((skill) => (
            <div
              key={skill.title}
              className="rounded-xl border border-border bg-card p-5 sm:p-6"
            >
              <h3 className="mb-4 text-base font-bold">{skill.title}</h3>
              <ul className="flex flex-wrap gap-2">
                {skill.items.map((item) => (
                  <li
                    key={item}
                    className="rounded-md border border-border bg-bg-alt px-2.5 py-1.5 text-sm text-muted"
                  >
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
