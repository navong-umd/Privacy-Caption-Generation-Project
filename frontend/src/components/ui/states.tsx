import type { ReactNode } from "react";
import { ApiError } from "@/api/client";
import { cx } from "./primitives";

export function Skeleton({ className }: { className?: string }) {
  return <div className={cx("animate-pulse rounded bg-surface-2", className)} />;
}

export function LoadingRows({ rows = 6, className }: { rows?: number; className?: string }) {
  return (
    <div className={cx("space-y-2", className)} aria-hidden>
      {Array.from({ length: rows }).map((_, i) => (
        <Skeleton key={i} className="h-9 w-full" />
      ))}
    </div>
  );
}

export function ErrorState({
  error,
  onRetry,
}: {
  error: unknown;
  onRetry?: () => void;
}) {
  const isApi = error instanceof ApiError;
  const status = isApi ? error.status : undefined;
  const title =
    status === 404
      ? "Not found"
      : status === 0
        ? "Cannot reach the API"
        : "Something went wrong";
  const message = isApi ? error.message : "An unexpected error occurred.";
  const detail = isApi ? error.detail : undefined;

  return (
    <div className="rounded-lg border border-line bg-surface px-5 py-6 text-sm">
      <div className="font-medium text-ink">{title}</div>
      <p className="mt-1 text-muted">{message}</p>
      {detail && <p className="mt-1 text-faint">{detail}</p>}
      {status === 0 && (
        <p className="mt-2 text-xs text-faint">
          Start it with <span className="mono">uvicorn webapi.main:app --port 8000</span>.
        </p>
      )}
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-3 rounded border border-line px-3 py-1.5 text-sm font-medium text-ink transition-colors hover:border-accent hover:text-accent"
        >
          Retry
        </button>
      )}
    </div>
  );
}

export function EmptyState({ title, hint }: { title: string; hint?: ReactNode }) {
  return (
    <div className="rounded-lg border border-dashed border-line-strong bg-surface px-5 py-10 text-center">
      <div className="text-sm font-medium text-muted">{title}</div>
      {hint && <div className="mt-1 text-xs text-faint">{hint}</div>}
    </div>
  );
}

export function DataUnavailable({ what }: { what: string }) {
  return (
    <div className="rounded-lg border border-dashed border-line-strong bg-surface px-5 py-6 text-sm text-muted">
      <span className="font-medium text-ink">Data unavailable</span> — {what}
    </div>
  );
}
