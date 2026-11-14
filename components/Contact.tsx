export function Contact() {
  return (
    <section id="contact" className="scroll-mt-24 py-20">
      <div className="mx-auto max-w-[760px] px-6 text-center">
        <p className="mb-3 font-mono text-xs font-semibold tracking-[0.16em] text-accent">
          GET IN TOUCH
        </p>
        <h2 className="mb-4 text-3xl font-extrabold md:text-4xl">
          Let&apos;s talk about what you&apos;re building.
        </h2>
        <p className="mx-auto mb-8 max-w-2xl leading-relaxed text-muted">
          For hiring conversations, web development projects, or cybersecurity
          training collaboration, email is the best way to reach me.
        </p>
        <div className="mb-6 flex flex-wrap justify-center gap-3">
          <a
            href="mailto:amorkhentvincent@gmail.com?subject=Portfolio%20inquiry"
            className="rounded-lg bg-accent px-6 py-3 font-semibold text-[#06211a] transition-all hover:-translate-y-0.5 hover:bg-accent-dim"
          >
            Email Me
          </a>
          <a
            href="/resume.pdf"
            download
            className="rounded-lg border border-border px-6 py-3 font-semibold text-text transition-colors hover:border-accent hover:text-accent"
          >
            Download Resume
          </a>
          <a
            href="https://github.com/Universal43A2z"
            target="_blank"
            rel="noreferrer"
            className="rounded-lg border border-border px-6 py-3 font-semibold text-text transition-colors hover:border-accent hover:text-accent"
          >
            GitHub <span aria-hidden="true">↗</span>
          </a>
        </div>
        <p className="font-mono text-sm text-muted">
          amorkhentvincent@gmail.com · Iloilo City, Philippines
        </p>
      </div>
    </section>
  );
}
