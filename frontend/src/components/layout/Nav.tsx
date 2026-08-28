import { useState } from "react";
import { NavLink } from "react-router-dom";
import { Container } from "./Container";
import { cx } from "@/components/ui/primitives";

const LINKS = [
  { to: "/", label: "Home", end: true },
  { to: "/research", label: "Research" },
  { to: "/pipeline", label: "Pipeline" },
  { to: "/results", label: "Results" },
  { to: "/analysis", label: "Analysis" },
  { to: "/about", label: "About" },
];

function linkClass(isActive: boolean): string {
  return cx(
    "relative py-1.5 text-sm font-medium transition-colors",
    isActive ? "text-ink" : "text-muted hover:text-ink",
  );
}

export function Nav() {
  const [open, setOpen] = useState(false);
  return (
    <header className="sticky top-0 z-40 border-b border-line bg-paper/85 backdrop-blur-sm">
      <Container className="flex h-14 items-center justify-between">
        <NavLink to="/" className="flex items-center gap-2.5" onClick={() => setOpen(false)}>
          <span className="grid h-6 w-6 place-items-center rounded bg-ink text-[0.65rem] font-bold text-paper">
            PP
          </span>
          <span className="text-sm font-semibold tracking-tight text-ink">
            Privacy Caption Generation
          </span>
        </NavLink>

        <nav className="hidden items-center gap-6 md:flex">
          {LINKS.map((l) => (
            <NavLink key={l.to} to={l.to} end={l.end} className={({ isActive }) => linkClass(isActive)}>
              {({ isActive }) => (
                <span className="relative">
                  {l.label}
                  {isActive && (
                    <span className="absolute -bottom-[1.15rem] left-0 h-0.5 w-full bg-accent" />
                  )}
                </span>
              )}
            </NavLink>
          ))}
          <a
            href={`${(import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "")}/docs`}
            target="_blank"
            rel="noreferrer"
            className="ml-1 rounded border border-line px-2 py-1 text-xs font-medium text-muted transition-colors hover:border-accent hover:text-accent"
            title="OpenAPI documentation"
          >
            API
          </a>
        </nav>

        <button
          className="rounded border border-line p-1.5 text-muted md:hidden"
          aria-label="Toggle menu"
          aria-expanded={open}
          onClick={() => setOpen((v) => !v)}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            {open ? <path d="M6 6l12 12M18 6L6 18" /> : <path d="M4 7h16M4 12h16M4 17h16" />}
          </svg>
        </button>
      </Container>

      {open && (
        <nav className="border-t border-line bg-paper md:hidden">
          <Container className="flex flex-col py-2">
            {LINKS.map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                end={l.end}
                onClick={() => setOpen(false)}
                className={({ isActive }) =>
                  cx(
                    "py-2 text-sm font-medium",
                    isActive ? "text-accent" : "text-muted",
                  )
                }
              >
                {l.label}
              </NavLink>
            ))}
          </Container>
        </nav>
      )}
    </header>
  );
}
