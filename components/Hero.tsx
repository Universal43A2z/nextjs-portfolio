export function Hero() {
  return (
    <header
      id="home"
      className="border-b border-border py-[90px] md:py-[110px]"
    >
      <div className="mx-auto grid max-w-[1080px] items-center gap-14 px-6 md:grid-cols-[1.1fr_0.9fr]">
        <div>
          <p className="font-mono text-sm text-accent">$ whoami</p>
          <h1 className="mt-4 text-4xl font-extrabold leading-tight md:text-5xl">
            Hi, I&apos;m <span className="text-accent">Khent Vincent Amorl</span>
          </h1>
          <p className="mt-4 max-w-[520px] text-lg text-muted">
            Cybersecurity &amp; Full-Stack Developer — building secure platforms,
            CTF challenges, and awareness programs.
          </p>
          <div className="mt-8 flex flex-wrap gap-4">
            <a
              href="#projects"
              className="rounded-lg bg-accent px-6 py-3 font-semibold text-[#06211a] transition-all hover:-translate-y-0.5 hover:bg-accent-dim"
            >
              View My Work
            </a>
            <a
              href="#contact"
              className="rounded-lg border border-border px-6 py-3 font-semibold text-text transition-colors hover:border-accent hover:text-accent"
            >
              Contact Me
            </a>
          </div>
          <p className="mt-4 font-mono text-xs text-[#5a6180]">
            {"// github.com/yourusername"}
          </p>
        </div>

        <div className="overflow-hidden rounded-xl border border-border bg-card shadow-[0_24px_60px_rgba(0,0,0,0.45)]">
          <div className="flex items-center gap-2 border-b border-border bg-bg-alt px-4 py-3">
            <span className="h-3 w-3 rounded-full bg-[#ff5f57]" />
            <span className="h-3 w-3 rounded-full bg-[#febc2e]" />
            <span className="h-3 w-3 rounded-full bg-[#28c840]" />
            <span className="ml-2 font-mono text-xs text-muted">~/khent</span>
          </div>
          <pre className="overflow-x-auto p-5 font-mono text-[0.86rem] leading-relaxed text-muted">
{`khent@portfolio:~$ `}<span className="text-accent">{`ls ./projects
`}</span>{`ctf-project/     netrecon/      (Python)
bank-system/     passaudit/     (Java/Py)
task-api/        cyber-awareness/
nodejs-practice/ advanced-database/

khent@portfolio:~$ `}<span className="text-accent">{`cat ./status.txt
`}</span>{`Passionate about cybersecurity,
web security, and building
things that people can use.

khent@portfolio:~$ `}<span className="text-accent">_</span>
          </pre>
        </div>
      </div>
    </header>
  );
}