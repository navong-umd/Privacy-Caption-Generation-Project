import { Link, useParams } from "react-router-dom";
import { Container } from "@/components/layout/Container";
import { useApp } from "@/api/queries";
import { Badge, Card, Section, Stat } from "@/components/ui/primitives";
import { BarList } from "@/components/ui/charts";
import { ErrorState, LoadingRows } from "@/components/ui/states";
import { humanizeCategory, int, pct } from "@/lib/format";

export default function AppDetail() {
  const { package: pkg } = useParams();
  const { data, isLoading, isError, error, refetch } = useApp(pkg);

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
        <>
          <header className="border-b border-line pb-6">
            <h1 className="text-2xl font-semibold text-ink">{data.display_name}</h1>
            <div className="mono mt-1 text-sm text-faint">{data.package}</div>
          </header>

          <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
            <Stat label="Privacy slices" value={int(data.n_prcs)} accent />
            <Stat label="Data types" value={int(data.collected.length)} />
            <Stat label="Policy completeness" value={pct(data.completeness)} />
            <Stat label="GDPR / CCPA" value={`${int(data.gdpr_reqs)} / ${int(data.ccpa_reqs)}`} />
          </div>

          <div className="mt-8 grid gap-4 lg:grid-cols-2">
            <Card className="px-5 py-5">
              <h3 className="mb-4 text-sm font-semibold text-ink">Personal information collected</h3>
              <BarList
                items={data.top_pi_categories.map((c) => ({ name: humanizeCategory(c.name), count: c.count }))}
                emptyLabel="No PI categories detected."
              />
            </Card>
            <Card className="px-5 py-5">
              <h3 className="mb-4 text-sm font-semibold text-ink">Where data goes (sink types)</h3>
              <BarList items={data.top_sink_types} emptyLabel="No sinks detected." />
            </Card>
          </div>

          <Section eyebrow="Privacy elements" title="Detected practices" description="">
            <div className="grid gap-4 sm:grid-cols-3">
              <FactCard title="Purposes" items={data.purposes} />
              <FactCard title="Data collected" items={data.collected.map(humanizeCategory)} />
              <FactCard title="Shared with (sinks)" items={data.shared_with} />
            </div>
          </Section>

          {data.sample_captions.length > 0 && (
            <Section eyebrow="Generation" title="Sample captions" description="Evidence-grounded captions for this app's privacy slices.">
              <div className="space-y-3">
                {data.sample_captions.map((c) => (
                  <Card key={c.prcs_id} className="px-4 py-3.5">
                    <div className="mb-2 flex items-center gap-2">
                      <Link to={`/analysis/prcs/${c.prcs_id}`} className="mono text-xs text-accent hover:underline">
                        {c.prcs_id.replace("prcs_", "")}
                      </Link>
                      <Badge tone="bg-accent-soft text-accent border-accent-border">{c.provider}</Badge>
                    </div>
                    <p className="whitespace-pre-line text-sm leading-relaxed text-ink">{c.caption}</p>
                  </Card>
                ))}
              </div>
              <div className="mt-3">
                <Link to="/analysis" className="text-sm font-medium text-accent hover:underline">
                  Browse all slices for this app in the explorer →
                </Link>
              </div>
            </Section>
          )}

          <Section eyebrow="Compliance" title="Regulatory obligations" description="Requirements the generated policy maps to, from the detected practices.">
            <div className="grid gap-4 lg:grid-cols-2">
              <ReqList title="GDPR" items={data.gdpr} />
              <ReqList title="CCPA" items={data.ccpa} />
            </div>
          </Section>
        </>
      ) : null}
    </Container>
  );
}

function FactCard({ title, items }: { title: string; items: string[] }) {
  return (
    <Card className="px-4 py-4">
      <div className="text-xs font-medium uppercase tracking-wide text-faint">{title}</div>
      <div className="mt-2 flex flex-wrap gap-1.5">
        {items.length === 0 ? (
          <span className="text-sm text-faint">—</span>
        ) : (
          items.map((i) => <Badge key={i}>{i}</Badge>)
        )}
      </div>
    </Card>
  );
}

function ReqList({ title, items }: { title: string; items: string[] }) {
  return (
    <Card className="px-5 py-4">
      <h3 className="mb-3 text-sm font-semibold text-ink">{title}</h3>
      {items.length === 0 ? (
        <p className="text-sm text-faint">None.</p>
      ) : (
        <ul className="space-y-1.5">
          {items.map((i) => (
            <li key={i} className="flex gap-2 text-sm text-muted">
              <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-accent" />
              <span>{i}</span>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
