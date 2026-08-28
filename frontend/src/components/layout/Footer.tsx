import { Container } from "./Container";

export function Footer() {
  return (
    <footer className="mt-20 border-t border-line bg-surface">
      <Container className="flex flex-col gap-4 py-8 text-xs text-faint sm:flex-row sm:items-center sm:justify-between">
        <div className="max-w-xl">
          <div className="font-medium text-muted">Privacy Caption Generation</div>
          <p className="mt-1">
            A research pipeline for Android privacy analysis. All figures are served from real
            pipeline artifacts; weak-label and LLM-judge results are marked as such.
          </p>
        </div>
        <div className="flex items-center gap-5">
          <a
            className="transition-colors hover:text-accent"
            href={`${(import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "")}/docs`}
            target="_blank"
            rel="noreferrer"
          >
            API docs
          </a>
          <span className="mono">Python 3.14 · FastAPI · React</span>
        </div>
      </Container>
    </footer>
  );
}
