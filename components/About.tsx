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
        <div className="grid items-center gap-8 md:grid-cols-[1.35fr_0.65fr] md:gap-14">
          <div className="scroll-reveal max-w-3xl">
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

          <aside className="scroll-reveal rounded-2xl border border-border bg-card p-5 shadow-[0_16px_48px_rgba(0,0,0,0.2)] sm:p-6">
            <div className="flex flex-col items-center text-center">
              <Image
                src="/photo.png"
                alt="Portrait of Khent Vincent C. Amor"
                width={320}
                height={320}
                className="size-40 rounded-full border border-border object-cover object-center shadow-[0_12px_36px_rgba(0,0,0,0.25)] md:size-36 lg:size-40"
              />
              <div className="mt-4">
                <p className="font-mono text-xs font-semibold tracking-[0.12em] text-accent">
                  PORTFOLIO
                </p>
                <h3 className="mt-1 text-xl font-bold leading-snug">
                  Khent Vincent C. Amor
                </h3>
                <p className="mt-1 text-sm leading-relaxed text-muted">
                  Full-stack developer · security focus
                </p>
              </div>
            </div>
          </aside>
        </div>

        <div className="mt-10 grid gap-4 md:grid-cols-3">
          {strengths.map((strength, index) => (
            <article
              key={strength.title}
              data-reveal-order={index}
              className="scroll-reveal motion-card rounded-xl border border-border bg-card p-5"
            >
              <h3 className="font-bold">{strength.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted">
                {strength.description}
              </p>
            </article>
          ))}
        </div>

        <div className="scroll-reveal mt-4 rounded-xl border border-border bg-card p-5 sm:p-6">
          <h3 className="mb-4 text-base font-bold">At a glance</h3>
          <dl className="grid gap-x-6 gap-y-4 sm:grid-cols-2 lg:grid-cols-4">
            {facts.map((fact) => (
              <div key={fact.label} className="border-l border-accent-dim pl-3">
                <dt className="font-mono text-xs text-accent">{fact.label}</dt>
                <dd className="mt-1 text-sm leading-relaxed text-text">
                  {fact.value}
                </dd>
              </div>
            ))}
          </dl>
        </div>
      </div>
    </section>
  );
}
