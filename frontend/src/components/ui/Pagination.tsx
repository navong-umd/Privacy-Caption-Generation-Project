import { int } from "@/lib/format";

export function Pagination({
  page,
  pageSize,
  total,
  hasMore,
  onPage,
  fetching,
}: {
  page: number;
  pageSize: number;
  total: number;
  hasMore: boolean;
  onPage: (p: number) => void;
  fetching?: boolean;
}) {
  const from = total === 0 ? 0 : (page - 1) * pageSize + 1;
  const to = Math.min(page * pageSize, total);
  const btn =
    "rounded border border-line px-2.5 py-1 text-sm font-medium text-ink transition-colors enabled:hover:border-accent enabled:hover:text-accent disabled:cursor-not-allowed disabled:text-faint";

  return (
    <div className="flex items-center justify-between gap-4 text-sm text-muted">
      <span className="tabular-nums">
        {int(from)}–{int(to)} of {int(total)}
        {fetching && <span className="ml-2 text-faint">updating…</span>}
      </span>
      <div className="flex items-center gap-2">
        <button className={btn} onClick={() => onPage(page - 1)} disabled={page <= 1}>
          ← Prev
        </button>
        <span className="tabular-nums text-faint">page {int(page)}</span>
        <button className={btn} onClick={() => onPage(page + 1)} disabled={!hasMore}>
          Next →
        </button>
      </div>
    </div>
  );
}
