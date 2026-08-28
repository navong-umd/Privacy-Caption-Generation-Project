import { useState } from "react";
import { Link } from "react-router-dom";
import { Container } from "@/components/layout/Container";
import { useOverview } from "@/api/queries";
import { PipelineFlow } from "@/components/pipeline/PipelineFlow";
import { Card, KeyValue } from "@/components/ui/primitives";
import { ErrorState, LoadingRows } from "@/components/ui/states";
import { int } from "@/lib/format";
import type { Overview } from "@/types/api";

// Real, backend-derived figures attached to each stage (no invented numbers).
function stageData(key: string, o: Overview): { k: string; v: string; to?: string } | null {
  switch (key) {
    case "apk":
      return { k: "APKs analyzed", v: int(o.n_apps), to: "/analysis" };
    case "ppg":
      return { k: "Privacy slices produced", v: int(o.n_prcs), to: "/analysis" };
    case "prcs":
      return { k: "PRCS records", v: int(o.n_prcs), to: "/analysis" };
    case "pact":
      return {
        k: "Train / val / test",
        v: `${int(o.splits?.train ?? null)} / ${int(o.splits?.val ?? null)} / ${int(o.splits?.test ?? null)}`,
      };
    case "model":
      return {
        k: "Practice macro-F1 (weak labels)",
        v: o.practice_macro_f1 !== null ? o.practice_macro_f1.toFixed(3) : "—",
        to: "/results",
      };
    case "caption":
      return { k: "LLM captions generated", v: int(o.n_captions_llm), to: "/analysis" };
    default:
      return null;
  }
}

export default function Pipeline() {
  const { data, isLoading, isError, error, refetch } = useOverview();
  const [active, setActive] = useState<string>("ppg");

  return (
    <Container>
      <header className="border-b border-line pb-6">
        <div className="text-xs font-medium uppercase tracking-widest text-accent">Method</div>
        <h1 className="mt-2 text-2xl font-semibold text-ink">The research pipeline</h1>
        <p className="mt-2 max-w-2xl text-sm text-muted">
          Eight stages transform a raw APK into an evidence-grounded privacy caption. Select a stage
          to see what it does, what it consumes, and what it produces.
        </p>
      </header>

      {isError && (
        <div className="mt-8">
          <ErrorState error={error} onRetry={() => refetch()} />
        </div>
      )}

      {isLoading || !data ? (
        <div className="mt-8">
          <LoadingRows rows={3} />
        </div>
      ) : (
        <>
          <div className="mt-8 overflow-x-auto pb-2">
            <PipelineFlow stages={data.pipeline} activeKey={active} onSelect={setActive} />
          </div>

          <div className="mt-6 grid gap-4 lg:grid-cols-[1fr_20rem]">
            {data.pipeline
              .filter((s) => s.key === active)
              .map((s) => {
                const i = data.pipeline.findIndex((x) => x.key === s.key);
                const d = stageData(s.key, data);
                return (
                  <div key={s.key} className="contents">
                    <Card className="px-6 py-6">
                      <div className="flex items-center gap-3">
                        <span className="grid h-7 w-7 place-items-center rounded-md bg-ink text-xs font-bold text-paper">
                          {String(i + 1).padStart(2, "0")}
                        </span>
                        <h2 className="text-lg font-semibold text-ink">{s.title}</h2>
                        <span className="mono text-xs text-faint">{s.tool}</span>
                      </div>
                      <p className="mt-4 text-[0.95rem] leading-relaxed text-muted">{s.description}</p>
                      <div className="mt-5 grid gap-4 sm:grid-cols-2">
                        <div className="rounded-md border border-line bg-surface p-3">
                          <div className="text-xs font-medium uppercase tracking-wide text-faint">Input</div>
                          <div className="mono mt-1 text-sm text-ink">{s.inputs}</div>
                        </div>
                        <div className="rounded-md border border-line bg-surface p-3">
                          <div className="text-xs font-medium uppercase tracking-wide text-faint">Output</div>
                          <div className="mono mt-1 text-sm text-ink">{s.outputs}</div>
                        </div>
                      </div>
                    </Card>

                    <Card className="h-fit px-5 py-5">
                      <div className="text-xs font-medium uppercase tracking-wide text-faint">
                        From the corpus run
                      </div>
                      {d ? (
                        <>
                          <KeyValue items={[{ k: d.k, v: <span className="tabular-nums">{d.v}</span> }]} />
                          {d.to && (
                            <Link to={d.to} className="text-sm font-medium text-accent hover:underline">
                              Explore →
                            </Link>
                          )}
                        </>
                      ) : (
                        <p className="mt-2 text-sm text-faint">
                          This stage runs upstream of the served artifacts. See the{" "}
                          <Link to="/research" className="text-accent hover:underline">
                            methodology
                          </Link>{" "}
                          for detail.
                        </p>
                      )}
                      <div className="mt-4 border-t border-line pt-3 text-xs text-faint">
                        Stage {i + 1} of {data.pipeline.length}
                      </div>
                    </Card>
                  </div>
                );
              })}
          </div>
        </>
      )}
    </Container>
  );
}
