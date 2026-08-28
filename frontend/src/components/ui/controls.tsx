import type { ReactNode } from "react";
import { cx } from "./primitives";

export function Tabs({
  tabs,
  active,
  onChange,
}: {
  tabs: Array<{ key: string; label: string; count?: number }>;
  active: string;
  onChange: (key: string) => void;
}) {
  return (
    <div className="flex gap-1 border-b border-line" role="tablist">
      {tabs.map((t) => {
        const on = t.key === active;
        return (
          <button
            key={t.key}
            role="tab"
            aria-selected={on}
            onClick={() => onChange(t.key)}
            className={cx(
              "-mb-px border-b-2 px-3 py-2 text-sm font-medium transition-colors",
              on
                ? "border-accent text-ink"
                : "border-transparent text-muted hover:text-ink",
            )}
          >
            {t.label}
            {t.count !== undefined && (
              <span className="ml-1.5 text-xs tabular-nums text-faint">{t.count}</span>
            )}
          </button>
        );
      })}
    </div>
  );
}

export function Select({
  value,
  onChange,
  options,
  placeholder,
  label,
}: {
  value: string;
  onChange: (v: string) => void;
  options: Array<{ value: string; label: string }>;
  placeholder: string;
  label?: string;
}) {
  return (
    <label className="flex flex-col gap-1">
      {label && <span className="text-xs font-medium text-faint">{label}</span>}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="h-9 min-w-0 rounded-md border border-line bg-paper px-2.5 text-sm text-ink outline-none transition-colors focus:border-accent"
      >
        <option value="">{placeholder}</option>
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </label>
  );
}

export function SearchInput({
  value,
  onChange,
  placeholder = "Search…",
}: {
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
}) {
  return (
    <div className="relative">
      <svg
        className="pointer-events-none absolute left-2.5 top-1/2 -translate-y-1/2 text-faint"
        width="15"
        height="15"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
      >
        <circle cx="11" cy="11" r="7" />
        <path d="M21 21l-4.3-4.3" />
      </svg>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="h-9 w-full rounded-md border border-line bg-paper pl-8 pr-3 text-sm text-ink outline-none transition-colors placeholder:text-faint focus:border-accent"
      />
    </div>
  );
}

export function SegToggle({
  value,
  onChange,
  options,
}: {
  value: string;
  onChange: (v: string) => void;
  options: Array<{ value: string; label: ReactNode }>;
}) {
  return (
    <div className="inline-flex rounded-md border border-line bg-surface p-0.5">
      {options.map((o) => (
        <button
          key={o.value}
          onClick={() => onChange(o.value)}
          className={cx(
            "rounded px-3 py-1 text-sm font-medium transition-colors",
            value === o.value ? "bg-paper text-ink shadow-sm" : "text-muted hover:text-ink",
          )}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}
