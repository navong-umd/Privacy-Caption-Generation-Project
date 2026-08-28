import type { ReactNode } from "react";

export function cx(...parts: Array<string | false | null | undefined>): string {
  return parts.filter(Boolean).join(" ");
}

export function Card({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div className={cx("rounded-lg border border-line bg-paper", className)}>{children}</div>
  );
}

export function Section({
  eyebrow,
  title,
  description,
  children,
  right,
}: {
  eyebrow?: string;
  title: string;
  description?: ReactNode;
  children?: ReactNode;
  right?: ReactNode;
}) {
  return (
    <section className="mb-12">
      <div className="mb-5 flex items-end justify-between gap-4">
        <div>
          {eyebrow && (
            <div className="mb-1 text-xs font-medium uppercase tracking-widest text-accent">
              {eyebrow}
            </div>
          )}
          <h2 className="text-xl font-semibold text-ink">{title}</h2>
          {description && <p className="mt-1.5 max-w-2xl text-sm text-muted">{description}</p>}
        </div>
        {right}
      </div>
      {children}
    </section>
  );
}

export function Badge({
  children,
  tone = "bg-surface-2 text-muted border-line",
  className,
  title,
}: {
  children: ReactNode;
  tone?: string;
  className?: string;
  title?: string;
}) {
  return (
    <span
      title={title}
      className={cx(
        "inline-flex items-center gap-1 rounded border px-1.5 py-0.5 text-xs font-medium",
        tone,
        className,
      )}
    >
      {children}
    </span>
  );
}

export function Stat({
  label,
  value,
  hint,
  accent = false,
}: {
  label: string;
  value: ReactNode;
  hint?: string;
  accent?: boolean;
}) {
  return (
    <div className="rounded-lg border border-line bg-paper px-4 py-3.5">
      <div className="text-xs uppercase tracking-wide text-faint">{label}</div>
      <div
        className={cx(
          "mt-1 text-2xl font-semibold tabular-nums",
          accent ? "text-accent" : "text-ink",
        )}
      >
        {value}
      </div>
      {hint && <div className="mt-0.5 text-xs text-faint">{hint}</div>}
    </div>
  );
}

export function Mono({ children, className }: { children: ReactNode; className?: string }) {
  return <span className={cx("mono text-[0.85em] break-all", className)}>{children}</span>;
}

export function CodeBlock({ code, className }: { code: string; className?: string }) {
  return (
    <pre
      className={cx(
        "overflow-x-auto rounded-md border border-line bg-surface p-4 text-xs leading-relaxed text-ink",
        className,
      )}
    >
      <code className="mono">{code}</code>
    </pre>
  );
}

export function KeyValue({ items }: { items: Array<{ k: string; v: ReactNode }> }) {
  return (
    <dl className="divide-y divide-line">
      {items.map(({ k, v }) => (
        <div key={k} className="grid grid-cols-[9rem_1fr] gap-4 py-2 text-sm">
          <dt className="text-faint">{k}</dt>
          <dd className="min-w-0 text-ink">{v}</dd>
        </div>
      ))}
    </dl>
  );
}
