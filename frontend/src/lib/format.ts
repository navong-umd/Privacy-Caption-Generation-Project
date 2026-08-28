// Small pure formatting + display helpers.

export function pct(value: number | null | undefined, digits = 1): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return `${(value * 100).toFixed(digits)}%`;
}

export function num(value: number | null | undefined, digits = 3): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return value.toFixed(digits);
}

export function int(value: number | null | undefined): string {
  if (value === null || value === undefined) return "—";
  return value.toLocaleString("en-US");
}

// Turn a SuSi-style category (LOCATION_INFORMATION) into readable text.
export function humanizeCategory(raw: string): string {
  if (!raw) return "";
  return raw
    .toLowerCase()
    .replace(/_/g, " ")
    .replace(/\binformation\b/g, "info")
    .replace(/^\w/, (c) => c.toUpperCase());
}

// Short label for the last segment of a "pkg.Class->method" API string.
export function shortApi(api: string): string {
  if (!api) return "";
  const method = api.split("->").pop() ?? api;
  const cls = api.split("->")[0]?.split(".").pop() ?? "";
  return cls ? `${cls}.${method}` : method;
}

// Stable-ish color token per sink type (background + text classes).
export function sinkTypeTone(sinkType: string): string {
  switch (sinkType) {
    case "network":
      return "bg-blue-50 text-blue-800 border-blue-200";
    case "storage":
      return "bg-amber-50 text-amber-800 border-amber-200";
    case "logging":
      return "bg-stone-100 text-stone-700 border-stone-200";
    case "ipc":
      return "bg-violet-50 text-violet-800 border-violet-200";
    case "serialization":
      return "bg-teal-50 text-teal-800 border-teal-200";
    default:
      return "bg-stone-100 text-stone-600 border-stone-200";
  }
}

export function labelSourceTone(source: string): string {
  switch (source) {
    case "human":
      return "bg-good-soft text-good border-transparent";
    case "llm":
      return "bg-accent-soft text-accent border-accent-border";
    default: // weak
      return "bg-warn-soft text-warn border-warn-border";
  }
}
