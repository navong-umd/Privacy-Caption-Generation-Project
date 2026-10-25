import { Container } from "@/components/layout/Container";
import {
  useCaptionResults,
  useClassification,
  useCompliance,
  useExperiments,
} from "@/api/queries";
import { Banner } from "@/components/ui/Banner";
import { Card, Section, Stat } from "@/components/ui/primitives";
import { DataUnavailable, ErrorState, LoadingRows } from "@/components/ui/states";
import { CompareBars, MetricBar } from "@/components/ui/charts";
import { int, num, pct } from "@/lib/format";
import type { LabelMetric } from "@/types/api";

export default function Results() {
  const cls = useClassification();
  const cap = useCaptionResults();
  const comp = useCompliance();
  const exp = useExperiments();

  return (
    <Container>
      <header className="border-b border-line pb-6">
        <div className="text-xs font-medium uppercase tracking-widest text-accent">Evaluation</div>
        <h1 className="mt-2 text-2xl font-semibold text-ink">Results</h1>
        <p className="mt-2 max-w-2xl text-sm text-muted">
          Every figure below is read from a real pipeline artifact. Classification is on weak
          (heuristic) labels; caption quality is scored by an LLM judge. These caveats are marked on
          each section. Human evaluation and the full experiment matrix are reserved.
        </p>
      </header>

      {/* Classification */}
      <div className="mt-8">
        <Section eyebrow="Model" title="PAcT classification (RGCN)">
          {cls.isLoading ? (
            <LoadingRows rows={4} />
          ) : cls.isError ? (
            <ErrorState error={cls.error} onRetry={() => cls.refetch()} />
          ) : cls.data ? (
            <div className="space-y-5">
              <Banner banner={cls.data.banner} />
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                <Stat label="Practice macro-F1" value={num(cls.data.practice_macro_f1)} accent />
                <Stat label="Practice micro-F1" value={num(cls.data.practice_micro_f1)} />
                <Stat label="Purpose macro-F1" value={num(cls.data.purpose_macro_f1)} accent />
                <Stat label="Purpose micro-F1" value={num(cls.data.purpose_micro_f1)} />
              </div>
              <div className="grid gap-4 lg:grid-cols-2">
                <LabelTable title="Practice head" rows={cls.data.practice_labels} />
                <LabelTable title="Purpose head" rows={cls.data.purpose_labels} />
              </div>
              <p className="text-xs text-faint">
                Held-out test set: {int(cls.data.n_test)} slices. Labels with zero support report 0
                and are a known limitation of the weak-label bootstrap.
              </p>
            </div>
          ) : null}
        </Section>
      </div>

      {/* Captions */}
      <Section eyebrow="Generation" title="Caption evaluation (LLM-as-judge)">
        {cap.isLoading ? (
          <LoadingRows rows={3} />
        ) : cap.isError ? (
          <ErrorState error={cap.error} onRetry={() => cap.refetch()} />
        ) : cap.data ? (
          <div className="space-y-5">
            <Banner banner={cap.data.banner} />
            <div className="grid gap-4 lg:grid-cols-[1fr_18rem]">
              <Card className="px-5 py-5">
                <h3 className="mb-4 text-sm font-semibold text-ink">
                  Mean judge scores — PPG caption vs Code2Seq baseline
                </h3>
                {cap.data.llm_mean && cap.data.baseline_mean ? (
                  <CompareBars
                    max={5}
                    aLabel="PPG caption"
                    bLabel="Code2Seq baseline"
                    rows={[
                      {
                        label: "Accuracy (1–5)",
                        a: cap.data.llm_mean.accuracy ?? null,
                        b: cap.data.baseline_mean.accuracy ?? null,
                      },
                      {
                        label: "Readability (1–5)",
                        a: cap.data.llm_mean.readability ?? null,
                        b: cap.data.baseline_mean.readability ?? null,
                      },
                    ]}
                  />
                ) : (
                  <DataUnavailable what="no judge means recorded for this run." />
                )}
              </Card>
              <div className="space-y-3">
                <Stat
                  label="Judge win rate"
                  value={cap.data.pairwise ? pct(cap.data.pairwise.llm_win_rate, 0) : "—"}
                  hint={
                    cap.data.pairwise
                      ? `${int(cap.data.pairwise.llm_wins)} of ${int(
                          cap.data.n_captions,
                        )} blind comparisons`
                      : undefined
                  }
                  accent
                />
                <Stat label="Captions judged" value={int(cap.data.n_captions)} hint={`judge: ${cap.data.judge ?? "—"}`} />
              </div>
            </div>
          </div>
        ) : null}
      </Section>

      {/* Compliance */}
      <Section
        eyebrow="Policy"
        title="GDPR / CCPA completeness"
        description="Structural check: are the detected privacy facts surfaced in each app's generated policy? This measures coverage, not legal correctness."
      >
        {comp.isLoading ? (
          <LoadingRows rows={4} />
        ) : comp.isError ? (
          <ErrorState error={comp.error} onRetry={() => comp.refetch()} />
        ) : comp.data ? (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <Stat label="Overall completeness" value={pct(comp.data.overall_completeness)} accent />
              <Stat label="Apps" value={int(comp.data.per_app.length)} />
            </div>
            <Card className="overflow-hidden p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-line bg-surface text-left text-xs uppercase tracking-wide text-faint">
                      <th className="px-4 py-2.5 font-medium">App</th>
                      <th className="px-4 py-2.5 text-right font-medium">Facts</th>
                      <th className="px-4 py-2.5 text-right font-medium">Surfaced</th>
                      <th className="px-4 py-2.5 text-right font-medium">Completeness</th>
                      <th className="px-4 py-2.5 text-right font-medium">GDPR</th>
                      <th className="px-4 py-2.5 text-right font-medium">CCPA</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-line">
                    {comp.data.per_app.map((a) => (
                      <tr key={a.package} className="transition-colors hover:bg-surface">
                        <td className="px-4 py-2.5">
                          <div className="font-medium text-ink">{a.display_name}</div>
                          <div className="mono text-xs text-faint">{a.package}</div>
                        </td>
                        <td className="px-4 py-2.5 text-right tabular-nums">{int(a.facts)}</td>
                        <td className="px-4 py-2.5 text-right tabular-nums">{int(a.surfaced)}</td>
                        <td className="px-4 py-2.5 text-right tabular-nums">{pct(a.completeness, 0)}</td>
                        <td className="px-4 py-2.5 text-right tabular-nums text-muted">{int(a.gdpr_reqs)}</td>
                        <td className="px-4 py-2.5 text-right tabular-nums text-muted">{int(a.ccpa_reqs)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          </div>
        ) : null}
      </Section>

      {/* Experiments */}
      <Section
        eyebrow="Reproducibility"
        title="Experiment matrix"
        description="The ten-arm comparison (graph, code tokens and knowledge overlay, baselines and caption conditions) and human evaluation are reserved for a budget-approved run. Numbers appear here only from real logged manifests."
      >
        {exp.isLoading ? (
          <LoadingRows rows={2} />
        ) : exp.isError ? (
          <ErrorState error={exp.error} onRetry={() => exp.refetch()} />
        ) : exp.data ? (
          exp.data.available ? (
            <Stat label="Logged experiment runs" value={int(exp.data.logged_runs)} />
          ) : (
            <DataUnavailable what={exp.data.note} />
          )
        ) : null}
      </Section>
    </Container>
  );
}

function LabelTable({ title, rows }: { title: string; rows: LabelMetric[] }) {
  return (
    <Card className="overflow-hidden p-0">
      <div className="border-b border-line bg-surface px-4 py-2.5 text-sm font-semibold text-ink">
        {title}
      </div>
      <div className="space-y-3 px-4 py-4">
        {rows.map((r) => (
          <MetricBar key={r.label} label={`${r.label} · F1`} value={r.f1} />
        ))}
      </div>
      <div className="overflow-x-auto border-t border-line">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs uppercase tracking-wide text-faint">
              <th className="px-4 py-2 font-medium">Label</th>
              <th className="px-4 py-2 text-right font-medium">P</th>
              <th className="px-4 py-2 text-right font-medium">R</th>
              <th className="px-4 py-2 text-right font-medium">F1</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {rows.map((r) => (
              <tr key={r.label}>
                <td className="px-4 py-1.5 text-ink">{r.label}</td>
                <td className="px-4 py-1.5 text-right tabular-nums text-muted">{num(r.precision, 2)}</td>
                <td className="px-4 py-1.5 text-right tabular-nums text-muted">{num(r.recall, 2)}</td>
                <td className="px-4 py-1.5 text-right tabular-nums text-ink">{num(r.f1, 2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
