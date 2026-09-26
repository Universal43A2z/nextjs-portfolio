export function Skills() {
  const skills = [
    {
      title: "Languages",
      items: "JavaScript / Node.js · Python · Java · HTML · CSS · SQL",
    },
    {
      title: "Backend",
      items: "REST APIs · Express · GraphQL · SWR · JSON · Concurrency · Persistence",
    },
    {
      title: "Security",
      items: "Web Pentesting · Port Scanning · Password Auditing · Wireshark · Linux",
    },
    {
      title: "Networking",
      items: "Starlink Deployment · Router & AP Config · TCP/IP · Cabling · Diagnostics",
    },
    {
      title: "Frontend",
      items: "React · Next.js · TypeScript · Tailwind CSS · CSS Grid & Flexbox",
    },
    {
      title: "Toolchain",
      items: "Git · Yarn · NPM · Vercel · Bash scripting · Kali Linux",
    },
  ];

  return (
    <section id="skills" className="border-y border-border bg-bg-alt py-20">
      <div className="mx-auto max-w-[1080px] px-6">
        <p className="font-mono text-sm text-accent">{"// skills"}</p>
        <h2 className="mt-2 mb-9 text-3xl font-extrabold">Tech Stack</h2>
        <div className="grid gap-[18px] md:grid-cols-2">
          {skills.map((skill) => (
            <div
              key={skill.title}
              className="rounded-xl border border-border bg-card p-5"
            >
              <h4 className="mb-2 text-base font-bold">{skill.title}</h4>
              <p className="text-sm text-muted">{skill.items}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}