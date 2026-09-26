export function About() {
  const facts = [
    { k: "name:", v: "Khent Vincent Amorl" },
    { k: "also known:", v: "Khent / khent" },
    { k: "focus:", v: "Cybersecurity, Full-Stack Web" },
    { k: "email:", v: "amorkhentvincent@gmail.com" },
    { k: "location:", v: "Iloilo City, Philippines" },
  ];

  return (
    <section id="about" className="py-20">
      <div className="mx-auto max-w-[1080px] px-6">
        <p className="font-mono text-sm text-accent">{"// about"}</p>
        <h2 className="mt-2 mb-9 text-3xl font-extrabold">Who I Am</h2>
        <div className="grid gap-12 md:grid-cols-[1.4fr_1fr]">
          <div className="text-[1.02rem] leading-relaxed text-muted">
            <p className="mb-4">
              I&apos;m a technology student focused on{" "}
              <strong className="text-accent">cybersecurity</strong> and{" "}
              <strong className="text-accent">web development</strong>. I enjoy
              the intersection of both — building platforms that are not only
              functional but also secure against real-world attacks.
            </p>
            <p className="mb-4">
              I&apos;ve designed a full Capture The Flag (CTF) platform with 58
              challenges for hands-on security training, wrote a campus-wide
              cyber awareness program, and continue sharpening my skills with
              Node.js, database design, and offensive/defensive security tools.
            </p>
            <p className="mb-4">
              I also spent two months with{" "}
              <strong className="text-accent">DICT</strong> (Department of
              Information and Communications Technology) deploying and
              installing <strong className="text-accent">Starlink</strong> WiFi
              setups in public schools — hands-on networking experience
              configuring and maintaining connectivity hardware on site.
            </p>
            <p className="mb-6">
              Since 2024 I&apos;ve worked as a{" "}
              <strong className="text-accent">freelance web developer</strong>,
              shipping client-facing apps end to end with React/Next.js,
              Node.js/Express, and REST APIs — with a security-first mindset on
              every layer.
            </p>

            <h3 className="mb-3 text-base font-bold">Expertise</h3>
            <ul className="mb-6 space-y-2">
              {[
                "Full-stack web development (JavaScript/Node.js, React/Next.js, Python)",
                "Web application security, audit & pen-testing (Kali, Wireshark)",
                "REST API design, databases & concurrency",
                "Offensive tooling: recon frameworks, password auditing",
                "Networking: setup, diagnostics & field deployment",
              ].map((item) => (
                <li key={item} className="flex gap-2">
                  <span className="text-accent">▸</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>

            <h3 className="mb-3 text-base font-bold">Services I Offer</h3>
            <ul className="mb-4 space-y-2">
              {[
                "Custom websites & full-stack web apps",
                "Backend APIs, databases & integrations",
                "Security audits & penetration testing",
                "CTF challenge design & security training",
                "Network setup & troubleshooting",
              ].map((item) => (
                <li key={item} className="flex gap-2">
                  <span className="text-accent">▸</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="flex flex-col gap-6">
            <div className="flex aspect-[4/3] w-full flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed border-border bg-card p-5 text-center">
              <span className="text-4xl">🖼️</span>
              <p className="font-semibold text-muted">Your photo goes here</p>
              <code className="rounded border border-border bg-bg-alt px-2 py-0.5 font-mono text-xs text-accent">
                public/photo.jpg
              </code>
            </div>
            <div className="h-fit rounded-xl border border-border bg-card p-6">
              <h3 className="mb-4 text-base font-bold">Quick Facts</h3>
              <ul>
                {facts.map((fact) => (
                  <li
                    key={fact.k}
                    className="border-b border-dashed border-border py-2 text-sm last:border-none"
                  >
                    <span className="font-mono text-accent">{fact.k}</span>{" "}
                    {fact.v}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}