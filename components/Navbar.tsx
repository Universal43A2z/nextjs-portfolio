"use client";

import { useState } from "react";

const links = [
  { href: "#home", label: "Home" },
  { href: "#about", label: "About" },
  { href: "#experience", label: "Experience" },
  { href: "#projects", label: "Projects" },
  { href: "#skills", label: "Skills" },
  { href: "#contact", label: "Contact" },
];

export function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const toggleMenu = () => setIsMenuOpen((open) => !open);
  const closeMenu = () => setIsMenuOpen(false);

  return (
    <nav
      aria-label="Primary navigation"
      className="sticky top-0 z-50 border-b border-border bg-bg/90 backdrop-blur"
    >
      <div className="relative mx-auto flex h-16 max-w-[1080px] items-center justify-between px-6">
        <a
          href="#home"
          aria-label="Khent Vincent C. Amor, home"
          className="w-fit text-lg font-extrabold text-text no-underline"
        >
          KV<span className="text-accent">.</span>Amor
        </a>
        <div className="hidden items-center gap-7 md:flex">
          <ul className="flex items-center gap-6">
            {links.map((link) => (
              <li key={link.href}>
                <a
                  href={link.href}
                  className="text-sm text-muted transition-colors hover:text-accent"
                >
                  {link.label}
                </a>
              </li>
            ))}
          </ul>
          <a
            href="/resume.pdf"
            className="font-semibold text-accent transition-colors hover:text-text"
            download
          >
            Resume
          </a>
        </div>
        <button
          type="button"
          className="rounded-lg border border-border px-3 py-2 text-sm font-semibold text-text transition-colors hover:border-accent hover:text-accent md:hidden"
          aria-expanded={isMenuOpen}
          aria-controls="mobile-navigation"
          aria-label={isMenuOpen ? "Close navigation menu" : "Open navigation menu"}
          onClick={toggleMenu}
        >
          {isMenuOpen ? "Close" : "Menu"}
        </button>
        <div
          id="mobile-navigation"
          className={`${isMenuOpen ? "block" : "hidden"} absolute left-0 right-0 top-full border-b border-border bg-card p-4 shadow-xl md:hidden`}
        >
          <ul className="grid gap-1">
            {links.map((link) => (
              <li key={link.href}>
                <a
                  href={link.href}
                  onClick={closeMenu}
                  className="block rounded-md px-3 py-2.5 text-sm text-muted transition-colors hover:bg-bg-alt hover:text-accent"
                >
                  {link.label}
                </a>
              </li>
            ))}
            <li>
              <a
                href="/resume.pdf"
                onClick={closeMenu}
                className="block rounded-md px-3 py-2.5 text-sm font-semibold text-accent transition-colors hover:bg-bg-alt"
                download
              >
                Download Resume
              </a>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
}
