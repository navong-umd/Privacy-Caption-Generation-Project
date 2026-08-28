import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useApps, useCaptions } from "@/api/queries";
import type { CaptionFilters } from "@/api/queries";
import { useDebounced } from "@/hooks/useDebounced";
import { Badge, Card } from "@/components/ui/primitives";
import { SearchInput, Select, SegToggle } from "@/components/ui/controls";
import { ErrorState, EmptyState, LoadingRows } from "@/components/ui/states";
import { Pagination } from "@/components/ui/Pagination";
import { labelSourceTone } from "@/lib/format";

const PAGE_SIZE = 20;

export function CaptionsPanel({ initialApp }: { initialApp?: string }) {
  const apps = useApps();
  const [provider, setProvider] = useState<"llm" | "mock">("llm");
  const [app, setApp] = useState(initialApp ?? "");
  const [q, setQ] = useState("");
  const [page, setPage] = useState(1);
  const dq = useDebounced(q, 300);

  const filters: CaptionFilters = useMemo(
    () => ({ provider, app: app || undefined, q: dq || undefined, page, page_size: PAGE_SIZE }),
    [provider, app, dq, page],
  );
  const { data, isLoading, isError, error, refetch, isFetching } = useCaptions(filters);
  const appOptions = (apps.data ?? []).map((a) => ({ value: a.package, label: a.display_name }));

  return (
    <div className="space-y-4">
      <Card className="flex flex-wrap items-end gap-3 p-3">
        <div className="flex flex-col gap-1">
          <span className="text-xs font-medium text-faint">Provider</span>
          <SegToggle
            value={provider}
            onChange={(v) => { setPage(1); setProvider(v as "llm" | "mock"); }}
            options={[
              { value: "llm", label: "Real LLM" },
              { value: "mock", label: "Template" },
            ]}
          />
        </div>
        <div className="w-48">
          <Select label="App" placeholder="All apps" value={app} onChange={(v) => { setPage(1); setApp(v); }} options={appOptions} />
        </div>
        <div className="min-w-[12rem] flex-1">
          <span className="mb-1 block text-xs font-medium text-faint">Search</span>
          <SearchInput value={q} onChange={(v) => { setPage(1); setQ(v); }} placeholder="Caption text or id…" />
        </div>
      </Card>

      {provider === "mock" && (
        <p className="text-xs text-faint">
          Template captions are deterministic and cover all {" "}
          <span className="tabular-nums">10,721</span> slices. Real-LLM captions are a curated subset.
        </p>
      )}

      {isError ? (
        <ErrorState error={error} onRetry={() => refetch()} />
      ) : isLoading && !data ? (
        <LoadingRows rows={6} className="[&>div]:h-24" />
      ) : data && data.items.length === 0 ? (
        <EmptyState title="No captions match." />
      ) : data ? (
        <>
          <div className="space-y-3">
            {data.items.map((c) => (
              <Card key={c.prcs_id} className="px-4 py-3.5">
                <div className="mb-2 flex items-center justify-between gap-2">
                  <Link
                    to={`/analysis/prcs/${c.prcs_id}`}
                    className="mono text-xs text-accent hover:underline"
                  >
                    {c.prcs_id.replace("prcs_", "")}
                  </Link>
                  <div className="flex items-center gap-1.5">
                    <Badge tone="bg-surface-2 text-muted border-line">{c.app_package.split(".").slice(-1)}</Badge>
                    <Badge tone="bg-accent-soft text-accent border-accent-border">{c.provider}</Badge>
                    {c.label_source && <Badge tone={labelSourceTone(c.label_source)}>{c.label_source}</Badge>}
                  </div>
                </div>
                <p className="whitespace-pre-line text-sm leading-relaxed text-ink">{c.caption}</p>
                {c.baseline_caption && (
                  <p className="mt-2 border-t border-line pt-2 text-xs text-faint">
                    <span className="font-medium">Baseline:</span> {c.baseline_caption}
                  </p>
                )}
              </Card>
            ))}
          </div>
          <Pagination
            page={data.page}
            pageSize={data.page_size}
            total={data.total}
            hasMore={data.has_more}
            onPage={setPage}
            fetching={isFetching}
          />
        </>
      ) : null}
    </div>
  );
}
