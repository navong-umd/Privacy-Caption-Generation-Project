import { useMemo } from "react";
import { Link, useParams } from "react-router-dom";
import { Container } from "@/components/layout/Container";
import { usePrcs } from "@/api/queries";
import { Badge, Card, CodeBlock, KeyValue, Mono, Section } from "@/components/ui/primitives";
import { BarList } from "@/components/ui/charts";
import { ErrorState, LoadingRows } from "@/components/ui/states";
import { humanizeCategory, labelSourceTone, sinkTypeTone } from "@/lib/format";
import type { PrcsDetail as Prcs } from "@/types/api";

export default function PrcsDetail() {
  const { id } = useParams();
  const { data, isLoading, isError, error, refetch } = usePrcs(id);

  return (
    <Container>
      <div className="mb-6 text-sm">
        <Link to="/analysis" className="text-muted hover:text-accent">
          ← Analysis
        </Link>
      </div>

      {isLoading ? (
        <LoadingRows rows={6} />
      ) : isError ? (
        <ErrorState error={error} onRetry={() => refetch()} />
      ) : data ? (
        <Detail p={data} />
      ) : null}
    </Container>
  );
}

function Detail({ p }: { p: Prcs }) {
  const edgeTypes = useMemo(() => {
    const counts = new Map<string, number>();
    for (const e of p.subgraph.edges) counts.set(e.type, (counts.get(e.type) ?? 0) + 1);
    return [...counts.entries()].map(([name, count]) => ({ name, count })).sort((a, b) => b.count - a.count);
  }, [p.subgraph.edges]);

  const threats = p.privacy_threat ? p.privacy_threat.split(";").map((t) => t.trim()).filter(Boolean) : [];

  return (
    <>
      <header className="border-b border-line pb-5">
        <div className="flex flex-wrap items-center gap-2">
          <Mono className="text-lg font-semibold text-ink">{p.prcs_id}</Mono>
          {p.split && <Badge tone="bg-surface-2 text-muted border-line">{p.split}</Badge>}
          <Badge tone={labelSourceTone(p.label_source)}>{p.label_source} label</Badge>
        </div>
        <div className="mono mt-1 text-sm text-faint">
          <Link to={`/analysis/apps/${p.app_package}`} className="hover:text-accent">
            {p.app_package}
          </Link>
        </div>
      </header>

      {/* Flow / evidence */}
      <Card className="mt-6 px-5 py-5">
        <div className="text-xs font-medium uppercase tracking-wide text-faint">Data flow</div>
        <div className="mt-3 flex flex-col gap-3 sm:flex-row sm:items-center">
          <div className="min-w-0 flex-1 rounded-md border border-line bg-surface p-3">
            <div className="text-xs text-faint">Source</div>
            <Mono className="text-sm text-ink">{p.source_api || "—"}</Mono>
            {p.pi_category && (
              <div className="mt-2">
                <Badge>{humanizeCategory(p.pi_category)}</Badge>
              </div>
            )}
          </div>
          <div className="shrink-0 text-center text-faint">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="mx-auto">
              <path d="M5 12h14M13 6l6 6-6 6" />
            </svg>
            <div className="mono text-xs">{p.hop_count} hops</div>
          </div>
          <div className="min-w-0 flex-1 rounded-md border border-line bg-surface p-3">
            <div className="text-xs text-faint">Sink</div>
            <Mono className="text-sm text-ink">{p.sink_api || "—"}</Mono>
            {p.sink_type && (
              <div className="mt-2">
                <Badge tone={sinkTypeTone(p.sink_type)}>{p.sink_type}</Badge>
              </div>
            )}
          </div>
        </div>
        {threats.length > 0 && (
          <div className="mt-4">
            <div className="text-xs font-medium uppercase tracking-wide text-faint">LINDDUN threats</div>
            <div className="mt-1.5 flex flex-wrap gap-1">
              {threats.map((t) => (
                <Badge key={t} tone="bg-warn-soft text-warn border-warn-border">
                  {t}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </Card>

      {/* Labels */}
      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        <Card className="px-5 py-4">
          <div className="text-xs font-medium uppercase tracking-wide text-faint">Practice</div>
          <div className="mt-2 flex flex-wrap gap-1.5">
            {p.practice.length ? p.practice.map((x) => <Badge key={x}>{x}</Badge>) : <span className="text-sm text-faint">—</span>}
          </div>
        </Card>
        <Card className="px-5 py-4">
          <div className="text-xs font-medium uppercase tracking-wide text-faint">Purpose</div>
          <div className="mt-2 flex flex-wrap gap-1.5">
            {p.purpose.length ? p.purpose.map((x) => <Badge key={x} tone="bg-accent-soft text-accent border-accent-border">{x}</Badge>) : <span className="text-sm text-faint">—</span>}
          </div>
        </Card>
      </div>

      {/* Captions */}
      <Section eyebrow="Generation" title="Captions">
        <div className="space-y-3">
          {p.llm_caption && <CaptionBlock label="Real LLM (OpenAI)" text={p.llm_caption} primary />}
          {p.mock_caption && <CaptionBlock label="Template" text={p.mock_caption} />}
          {p.baseline_caption && <CaptionBlock label="Code2Seq baseline" text={p.baseline_caption} muted />}
          {!p.llm_caption && !p.mock_caption && (
            <p className="text-sm text-faint">No caption recorded for this slice.</p>
          )}
        </div>
      </Section>

      {/* Metadata */}
      <Section eyebrow="Provenance" title="Slice metadata">
        <Card className="px-5 py-2">
          <KeyValue
            items={[
              { k: "Class", v: <Mono>{p.class_name}</Mono> },
              { k: "Method", v: <Mono>{p.method_signature || p.method_name}</Mono> },
              { k: "PI type", v: p.pi_type || "—" },
              { k: "Permission", v: p.permission ? <Mono>{p.permission}</Mono> : "—" },
              { k: "Sink label", v: p.sink_label || "—" },
              { k: "Subgraph", v: `${p.subgraph.nodes.length} nodes · ${p.subgraph.edges.length} edges` },
            ]}
          />
        </Card>
      </Section>

      {/* Code */}
      {p.code_snippet && (
        <Section eyebrow="Evidence" title="Code snippet" description="The disassembled statements along the tainted flow, grouped by method.">
          <CodeBlock code={p.code_snippet} />
        </Section>
      )}

      {/* Graph structure */}
      <Section eyebrow="Structure" title="Privacy subgraph">
        <div className="grid gap-4 lg:grid-cols-2">
          <Card className="px-5 py-5">
            <h3 className="mb-4 text-sm font-semibold text-ink">Edge types</h3>
            <BarList items={edgeTypes} emptyLabel="No edges." />
          </Card>
          <Card className="px-5 py-5">
            <h3 className="mb-3 text-sm font-semibold text-ink">Methods on the flow</h3>
            <ul className="space-y-1.5">
              {p.involved_methods.map((m) => (
                <li key={m} className="flex gap-2 text-sm">
                  <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-accent" />
                  <Mono className="text-muted">{m}</Mono>
                </li>
              ))}
              {p.involved_methods.length === 0 && <li className="text-sm text-faint">—</li>}
            </ul>
          </Card>
        </div>
      </Section>
    </>
  );
}

function CaptionBlock({ label, text, primary, muted }: { label: string; text: string; primary?: boolean; muted?: boolean }) {
  return (
    <Card className={primary ? "border-accent-border px-4 py-3.5" : "px-4 py-3.5"}>
      <div className="mb-1.5 flex items-center gap-2">
        <span className="text-xs font-medium uppercase tracking-wide text-faint">{label}</span>
        {primary && <Badge tone="bg-accent-soft text-accent border-accent-border">primary</Badge>}
      </div>
      <p className={`whitespace-pre-line text-sm leading-relaxed ${muted ? "text-muted" : "text-ink"}`}>{text}</p>
    </Card>
  );
}
