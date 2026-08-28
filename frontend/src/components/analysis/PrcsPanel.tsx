import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { prefetchPrcs, useApps, usePrcsList } from "@/api/queries";
import type { PrcsFilters } from "@/api/queries";
import { useDebounced } from "@/hooks/useDebounced";
import { Badge, Card } from "@/components/ui/primitives";
import { Select, SearchInput } from "@/components/ui/controls";
import { ErrorState, EmptyState, LoadingRows } from "@/components/ui/states";
import { Pagination } from "@/components/ui/Pagination";
import { humanizeCategory, labelSourceTone, shortApi, sinkTypeTone } from "@/lib/format";
import {
  LABEL_SOURCES,
  PI_CATEGORIES,
  PRACTICE_LABELS,
  PURPOSE_LABELS,
  SINK_TYPES,
  SPLITS,
} from "@/lib/vocab";

const PAGE_SIZE = 25;
const opts = (xs: string[], map?: (x: string) => string) =>
  xs.map((x) => ({ value: x, label: map ? map(x) : x }));

export function PrcsPanel({ initialApp }: { initialApp?: string }) {
  const navigate = useNavigate();
  const apps = useApps();
  const [f, setF] = useState<Omit<PrcsFilters, "q" | "page">>({ app: initialApp });
  const [q, setQ] = useState("");
  const [page, setPage] = useState(1);
  const dq = useDebounced(q, 300);

  const filters: PrcsFilters = useMemo(
    () => ({ ...f, q: dq || undefined, page, page_size: PAGE_SIZE }),
    [f, dq, page],
  );
  const { data, isLoading, isError, error, refetch, isFetching } = usePrcsList(filters);

  function set<K extends keyof typeof f>(key: K, value: string) {
    setPage(1);
    setF((prev) => ({ ...prev, [key]: value || undefined }));
  }

  const appOptions = (apps.data ?? []).map((a) => ({ value: a.package, label: a.display_name }));

  return (
    <div className="space-y-4">
      <Card className="p-3">
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-4">
          <Select label="App" placeholder="All apps" value={f.app ?? ""} onChange={(v) => set("app", v)} options={appOptions} />
          <Select label="Data type" placeholder="Any PI category" value={f.pi_category ?? ""} onChange={(v) => set("pi_category", v)} options={opts(PI_CATEGORIES, humanizeCategory)} />
          <Select label="Sink" placeholder="Any sink type" value={f.sink_type ?? ""} onChange={(v) => set("sink_type", v)} options={opts(SINK_TYPES)} />
          <Select label="Practice" placeholder="Any practice" value={f.practice ?? ""} onChange={(v) => set("practice", v)} options={opts(PRACTICE_LABELS)} />
          <Select label="Purpose" placeholder="Any purpose" value={f.purpose ?? ""} onChange={(v) => set("purpose", v)} options={opts(PURPOSE_LABELS)} />
          <Select label="Label source" placeholder="Any source" value={f.label_source ?? ""} onChange={(v) => set("label_source", v)} options={opts(LABEL_SOURCES)} />
          <Select label="Split" placeholder="Any split" value={f.split ?? ""} onChange={(v) => set("split", v)} options={opts(SPLITS)} />
          <label className="flex flex-col gap-1">
            <span className="text-xs font-medium text-faint">Search</span>
            <SearchInput value={q} onChange={(v) => { setPage(1); setQ(v); }} placeholder="API, method, id…" />
          </label>
        </div>
      </Card>

      {isError ? (
        <ErrorState error={error} onRetry={() => refetch()} />
      ) : isLoading && !data ? (
        <LoadingRows rows={8} />
      ) : data && data.items.length === 0 ? (
        <EmptyState title="No privacy slices match these filters." hint="Try clearing a filter." />
      ) : data ? (
        <>
          <Card className="overflow-hidden p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-line bg-surface text-left text-xs uppercase tracking-wide text-faint">
                    <th className="px-3 py-2.5 font-medium">Slice</th>
                    <th className="px-3 py-2.5 font-medium">Flow (source → sink)</th>
                    <th className="px-3 py-2.5 font-medium">Data</th>
                    <th className="px-3 py-2.5 font-medium">Sink</th>
                    <th className="px-3 py-2.5 font-medium">Labels</th>
                    <th className="px-3 py-2.5 text-right font-medium">Hops</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line">
                  {data.items.map((r) => (
                    <tr
                      key={r.prcs_id}
                      onClick={() => navigate(`/analysis/prcs/${r.prcs_id}`)}
                      onMouseEnter={() => prefetchPrcs(r.prcs_id)}
                      className="cursor-pointer transition-colors hover:bg-surface"
                    >
                      <td className="px-3 py-2.5 align-top">
                        <div className="mono text-xs text-accent">{r.prcs_id.replace("prcs_", "")}</div>
                        <div className="text-xs text-faint">{r.app_package.split(".").slice(-1)}</div>
                      </td>
                      <td className="px-3 py-2.5 align-top">
                        <div className="mono text-xs text-ink">{shortApi(r.source_api)}</div>
                        <div className="mono text-xs text-faint">→ {shortApi(r.sink_api)}</div>
                      </td>
                      <td className="px-3 py-2.5 align-top">
                        {r.pi_category ? <Badge>{humanizeCategory(r.pi_category)}</Badge> : <span className="text-faint">—</span>}
                      </td>
                      <td className="px-3 py-2.5 align-top">
                        {r.sink_type ? <Badge tone={sinkTypeTone(r.sink_type)}>{r.sink_type}</Badge> : <span className="text-faint">—</span>}
                      </td>
                      <td className="px-3 py-2.5 align-top">
                        <div className="flex flex-wrap gap-1">
                          {r.practice.slice(0, 2).map((p) => (
                            <Badge key={p} tone="bg-surface-2 text-muted border-line">{p}</Badge>
                          ))}
                          <Badge tone={labelSourceTone(r.label_source)}>{r.label_source}</Badge>
                        </div>
                      </td>
                      <td className="px-3 py-2.5 text-right align-top tabular-nums text-muted">{r.hop_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
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
