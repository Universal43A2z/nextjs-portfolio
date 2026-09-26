export function Contact() {
  return (
    <section id="contact" className="py-20">
      <div className="mx-auto max-w-[1080px] px-6 text-center">
        <p className="font-mono text-sm text-accent">{"// contact"}</p>
        <h2 className="mt-2 mb-4 text-3xl font-extrabold">Let&apos;s Connect</h2>
        <p className="mb-7 text-muted">
          Have a project idea or want to collaborate on security research? Reach
          out.
        </p>
        <div className="mb-5 flex flex-wrap justify-center gap-4">
          <a
            href="mailto:amorkhentvincent@gmail.com"
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
            href="https://github.com/yourusername"
            target="_blank"
            rel="noreferrer"
            className="rounded-lg border border-border px-6 py-3 font-semibold text-text transition-colors hover:border-accent hover:text-accent"
          >
            GitHub
          </a>
        </div>
        <p className="font-mono text-xs text-[#5a6180]">
          amorkhentvincent@gmail.com · 0921 352 3734 · github.com/yourusername
        </p>
      </div>
    </section>
  );
}