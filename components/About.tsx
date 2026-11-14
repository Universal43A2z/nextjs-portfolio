import Image from "next/image";

export function About() {
  const strengths = [
    {
      title: "End-to-end delivery",
      description:
        "Builds web experiences across the interface, APIs, data layer, and deployment.",
    },
    {
      title: "Security-minded engineering",
      description:
        "Applies access control, validation, and server-side safeguards to practical products.",
    },
    {
      title: "Practical troubleshooting",
      description:
        "Combines client-facing IT support with hands-on network deployment experience.",
    },
  ];

  const facts = [
    { label: "Focus", value: "Full-stack development · application security" },
    { label: "Location", value: "Iloilo City, Philippines" },
    { label: "Experience", value: "Freelance development since 2024" },
    {
      label: "Education",
      value: "Senior High School · ICT — Computer Systems Servicing (CS8)",
    },
  ];

  return (
    <section id="about" className="scroll-mt-24 py-20">
      <div className="mx-auto max-w-[1080px] px-6">
        <div className="scroll-reveal mb-10 max-w-3xl">
          <p className="mb-3 font-mono text-xs font-semibold tracking-[0.16em] text-accent">
            PROFILE
          </p>
          <h2 className="text-3xl font-extrabold leading-tight md:text-4xl">
            Product delivery, grounded in a security mindset.
          </h2>
          <p className="mt-5 text-base leading-relaxed text-muted md:text-lg">
            I&apos;m a technology student and freelance developer focused on
            building useful web products. My work spans full-stack development,
            cybersecurity training platforms, and hands-on network deployment.
            In 2026, my team won the PHINMA AI Builder Workshop with Dugtong.
          </p>
        </div>

        <div className="grid items-start gap-10 md:grid-cols-[1.35fr_0.65fr] md:gap-14">
          <div className="grid gap-4 sm:grid-cols-2">
            {strengths.map((strength) => (
              <article
                key={strength.title}
                className="scroll-reveal motion-card rounded-xl border border-border bg-card p-5"
              >
                <h3 className="font-bold">{strength.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted">
                  {strength.description}
                </p>
              </article>
            ))}
          </div>

          <aside className="scroll-reveal flex flex-col gap-5">
            <div className="flex w-full items-center justify-center">
              <Image
                src="/photo.png"
                alt="Portrait of Khent Vincent C. Amor"
                width={320}
                height={320}
                className="h-auto w-full max-w-[220px] rounded-full border border-border object-cover shadow-[0_16px_48px_rgba(0,0,0,0.3)]"
              />
            </div>
            <div className="rounded-xl border border-border bg-card p-5 sm:p-6">
              <h3 className="mb-3 text-base font-bold">At a glance</h3>
              <dl>
                {facts.map((fact) => (
                  <div
                    key={fact.label}
                    className="border-b border-dashed border-border py-2.5 last:border-none"
                  >
                    <dt className="font-mono text-xs text-accent">
                      {fact.label}
                    </dt>
                    <dd className="mt-1 text-sm leading-relaxed text-text">
                      {fact.value}
                    </dd>
                  </div>
                ))}
              </dl>
            </div>
          </aside>
        </div>
      </div>
    </section>
  );
}
