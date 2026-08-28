import { Link } from "react-router-dom";
import { prefetchApp, useApps } from "@/api/queries";
import { Badge, Card } from "@/components/ui/primitives";
import { ErrorState, LoadingRows } from "@/components/ui/states";
import { humanizeCategory, int } from "@/lib/format";

export function AppsPanel() {
  const { data, isLoading, isError, error, refetch } = useApps();

  if (isLoading) return <LoadingRows rows={4} className="[&>div]:h-28" />;
  if (isError) return <ErrorState error={error} onRetry={() => refetch()} />;
  if (!data || data.length === 0) return null;

  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {data.map((app) => (
        <Link
          key={app.package}
          to={`/analysis/apps/${app.package}`}
          onMouseEnter={() => prefetchApp(app.package)}
          className="group"
        >
          <Card className="h-full px-4 py-4 transition-colors group-hover:border-accent-border">
            <div className="flex items-start justify-between gap-2">
              <div className="min-w-0">
                <h3 className="truncate text-sm font-semibold text-ink">{app.display_name}</h3>
                <div className="mono truncate text-xs text-faint">{app.package}</div>
              </div>
              <span className="shrink-0 rounded bg-surface-2 px-1.5 py-0.5 text-xs font-medium tabular-nums text-muted">
                {int(app.n_prcs)}
              </span>
            </div>

            <div className="mt-3">
              <div className="text-xs font-medium uppercase tracking-wide text-faint">Collects</div>
              <div className="mt-1.5 flex flex-wrap gap-1">
                {app.collected.slice(0, 5).map((c) => (
                  <Badge key={c}>{humanizeCategory(c)}</Badge>
                ))}
                {app.collected.length > 5 && (
                  <span className="text-xs text-faint">+{app.collected.length - 5}</span>
                )}
                {app.collected.length === 0 && <span className="text-xs text-faint">—</span>}
              </div>
            </div>

            <div className="mt-3 flex flex-wrap gap-1">
              {app.purposes.map((p) => (
                <Badge key={p} tone="bg-accent-soft text-accent border-accent-border">
                  {p}
                </Badge>
              ))}
            </div>

            <div className="mt-3 flex items-center justify-between border-t border-line pt-2.5 text-xs text-faint">
              <span>{int(app.gdpr_reqs)} GDPR · {int(app.ccpa_reqs)} CCPA</span>
              <span className="font-medium text-accent opacity-0 transition-opacity group-hover:opacity-100">
                Inspect →
              </span>
            </div>
          </Card>
        </Link>
      ))}
    </div>
  );
}
