import { Link } from "react-router-dom";
import { Container } from "@/components/layout/Container";

export default function NotFound() {
  return (
    <Container size="prose">
      <div className="py-16 text-center">
        <div className="mono text-sm text-faint">404</div>
        <h1 className="mt-2 text-2xl font-semibold text-ink">Page not found</h1>
        <p className="mt-2 text-muted">That route does not exist in this research site.</p>
        <Link
          to="/"
          className="mt-6 inline-block rounded-md border border-line px-4 py-2 text-sm font-medium text-ink transition-colors hover:border-accent hover:text-accent"
        >
          ← Back home
        </Link>
      </div>
    </Container>
  );
}
