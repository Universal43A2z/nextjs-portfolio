export function Footer() {
  return (
    <footer className="border-t border-border py-6">
      <div className="mx-auto flex max-w-[1080px] flex-col gap-3 px-6 text-center text-sm text-muted sm:flex-row sm:items-center sm:justify-between sm:text-left">
        <p>© 2026 Khent Vincent C. Amor</p>
        <a
          href="https://github.com/Universal43A2z"
          target="_blank"
          rel="noreferrer"
          className="font-mono text-xs transition-colors hover:text-accent"
        >
          GitHub ↗
        </a>
      </div>
    </footer>
  );
}
