// Tiny dependency-free charts: a labeled metric bar and a horizontal bar list.
// Research values are always shown as text next to the bar, never chart-only.

import { int } from "@/lib/format";

export function MetricBar({
  label,
  value,
  max = 1,
  suffix = "",
}: {
  label: string;
  value: number | null;
  max?: number;
  suffix?: string;
}) {
  const has = value !== null && value !== undefined && !Number.isNaN(value);
  const w = has ? Math.max(0, Math.min(100, (value! / max) * 100)) : 0;
  return (
    <div className="flex items-center gap-3">
      <div className="w-40 shrink-0 truncate text-sm text-muted" title={label}>
        {label}
      </div>
      <div className="h-2 flex-1 overflow-hidden rounded-full bg-surface-2">
        <div
          className="h-full rounded-full bg-accent transition-[width] duration-300"
          style={{ width: `${w}%` }}
        />
      </div>
      <div className="w-14 shrink-0 text-right text-sm tabular-nums text-ink">
        {has ? value!.toFixed(suffix === "%" ? 1 : 3) + suffix : "—"}
      </div>
    </div>
  );
}

export function BarList({
  items,
  emptyLabel = "None",
}: {
  items: Array<{ name: string; count: number }>;
  emptyLabel?: string;
}) {
  if (items.length === 0)
    return <p className="text-sm text-faint">{emptyLabel}</p>;
  const max = Math.max(...items.map((i) => i.count), 1);
  return (
    <div className="space-y-1.5">
      {items.map((it) => (
        <div key={it.name} className="flex items-center gap-3">
          <div className="w-44 shrink-0 truncate text-sm text-ink" title={it.name}>
            {it.name}
          </div>
          <div className="h-4 flex-1 overflow-hidden rounded bg-surface-2">
            <div
              className="h-full rounded bg-accent/80"
              style={{ width: `${(it.count / max) * 100}%` }}
            />
          </div>
          <div className="w-12 shrink-0 text-right text-sm tabular-nums text-muted">
            {int(it.count)}
          </div>
        </div>
      ))}
    </div>
  );
}

/** Two-series comparison bars (e.g. PPG-LLM vs baseline mean scores). */
export function CompareBars({
  rows,
  max,
  aLabel,
  bLabel,
}: {
  rows: Array<{ label: string; a: number | null; b: number | null }>;
  max: number;
  aLabel: string;
  bLabel: string;
}) {
  return (
    <div className="space-y-4">
      <div className="flex gap-4 text-xs text-muted">
        <span className="flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-sm bg-accent" /> {aLabel}
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-sm bg-stone-400" /> {bLabel}
        </span>
      </div>
      {rows.map((r) => (
        <div key={r.label}>
          <div className="mb-1 flex justify-between text-sm">
            <span className="text-muted">{r.label}</span>
            <span className="tabular-nums text-ink">
              {r.a?.toFixed(2) ?? "—"} <span className="text-faint">/ {r.b?.toFixed(2) ?? "—"}</span>
            </span>
          </div>
          <div className="space-y-1">
            <Bar value={r.a} max={max} tone="bg-accent" />
            <Bar value={r.b} max={max} tone="bg-stone-400" />
          </div>
        </div>
      ))}
    </div>
  );
}

function Bar({ value, max, tone }: { value: number | null; max: number; tone: string }) {
  const w = value === null ? 0 : Math.max(0, Math.min(100, (value / max) * 100));
  return (
    <div className="h-2 overflow-hidden rounded-full bg-surface-2">
      <div className={`h-full rounded-full ${tone}`} style={{ width: `${w}%` }} />
    </div>
  );
}
