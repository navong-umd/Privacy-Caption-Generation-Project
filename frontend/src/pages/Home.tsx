import { Link } from "react-router-dom";
import { Container } from "@/components/layout/Container";
import { useOverview } from "@/api/queries";
import { Banner } from "@/components/ui/Banner";
import { Card, Section, Stat } from "@/components/ui/primitives";
import { ErrorState, LoadingRows, Skeleton } from "@/components/ui/states";
import { PipelineFlow } from "@/components/pipeline/PipelineFlow";
import { int, pct } from "@/lib/format";

export function Home() {
  const { data, isLoading, isError, error, refetch } = useOverview();

  return (
    <Container>
      {/* Masthead — restrained, no giant hero */}
      <div className="border-b border-line pb-9">
        <div className="text-xs font-medium uppercase tracking-widest text-accent">
          Android Privacy Research
        </div>
        <h1 className="mt-2 max-w-3xl text-3xl font-semibold leading-tight tracking-tight text-ink sm:text-4xl">
          Privacy Caption Generation
        </h1>
        <p className="mt-4 max-w-2xl text-[0.975rem] leading-relaxed text-muted">
          Given an Android APK, we build a privacy-aware graph of the program, trace how personal
          data flows from sources to sinks, classify the privacy practice and purpose, and generate
          evidence-grounded privacy captions and GDPR/CCPA policy notices. The central question:
          does a graph representation improve privacy understanding over code-only approaches?
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link
            to="/pipeline"
            className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-paper transition-colors hover:bg-accent-hover"
          >
            Explore the pipeline
          </Link>
          <Link
            to="/results"
            className="rounded-md border border-line px-4 py-2 text-sm font-medium text-ink transition-colors hover:border-accent hover:text-accent"
          >
            View results
          </Link>
          <Link
            to="/analysis"
            className="rounded-md border border-line px-4 py-2 text-sm font-medium text-ink transition-colors hover:border-accent hover:text-accent"
          >
            Inspect analyzed apps
          </Link>
        </div>
      </div>

      {isError && (
        <div className="mt-8">
          <ErrorState error={error} onRetry={() => refetch()} />
        </div>
      )}

      {/* Corpus stats */}
      <div className="mt-8 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {isLoading || !data ? (
          Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-[86px] rounded-lg" />)
        ) : (
          <>
            <Stat label="Apps analyzed" value={int(data.n_apps)} hint="real corpus" accent />
            <Stat label="Privacy slices" value={int(data.n_prcs)} hint="source → sink flows" />
            <Stat label="LLM captions" value={int(data.n_captions_llm)} hint="OpenAI, evidence-grounded" />
            <Stat
              label="Test split"
              value={int(data.splits?.test ?? null)}
              hint="held-out, leak-safe"
            />
          </>
        )}
      </div>

      {/* Honesty banners */}
      {data && data.banners.length > 0 && (
        <div className="mt-6 space-y-2">
          {data.banners.map((b, i) => (
            <Banner key={i} banner={b} />
          ))}
        </div>
      )}

      {/* Pipeline strip */}
      <div className="mt-12">
        <Section
          eyebrow="Method"
          title="The research pipeline"
          description="Eight stages from raw APK to an evidence-grounded caption. Each stage's output is the next stage's input."
          right={
            <Link
              to="/pipeline"
              className="hidden shrink-0 text-sm font-medium text-accent hover:underline sm:block"
            >
              Interactive view →
            </Link>
          }
        >
          {data ? (
            <PipelineFlow stages={data.pipeline} />
          ) : (
            <LoadingRows rows={1} className="[&>div]:h-16" />
          )}
        </Section>
      </div>

      {/* Results snapshot */}
      <Section
        eyebrow="Findings so far"
        title="Current results"
        description="Preliminary. Classification runs on weak (heuristic) labels; caption quality is scored by an LLM judge. Human evaluation is the reserved final gate."
        right={
          <Link to="/results" className="hidden shrink-0 text-sm font-medium text-accent hover:underline sm:block">
            Full results →
          </Link>
        }
      >
        <div className="grid gap-3 sm:grid-cols-3">
          {isLoading || !data ? (
            Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-[86px] rounded-lg" />)
          ) : (
            <>
              <Stat
                label="Practice macro-F1"
                value={data.practice_macro_f1 !== null ? data.practice_macro_f1.toFixed(3) : "—"}
                hint={data.n_test ? `RGCN · n=${int(data.n_test)} · weak labels` : "weak labels"}
              />
              <Stat
                label="Caption judge win rate"
                value={data.caption_judge?.llm_win_rate != null ? pct(data.caption_judge.llm_win_rate, 0) : "—"}
                hint="PPG caption vs Code2Seq baseline"
                accent
              />
              <Stat
                label="Purpose macro-F1"
                value={data.purpose_macro_f1 !== null ? data.purpose_macro_f1.toFixed(3) : "—"}
                hint="macro over 4 purpose labels"
              />
            </>
          )}
        </div>
      </Section>

      {/* Deeper links */}
      <Section eyebrow="Read more" title="Go deeper">
        <div className="grid gap-3 sm:grid-cols-3">
          <NavCard to="/research" title="Research" body="Problem, questions, methodology, and the full documentation set." />
          <NavCard to="/analysis" title="Analysis" body="Inspect real apps, browse privacy slices, and read generated captions." />
          <NavCard to="/results" title="Results" body="Classification metrics, caption evaluation, and GDPR/CCPA compliance." />
        </div>
      </Section>
    </Container>
  );
}

function NavCard({ to, title, body }: { to: string; title: string; body: string }) {
  return (
    <Link to={to} className="group">
      <Card className="h-full px-4 py-4 transition-colors group-hover:border-accent-border">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-ink">{title}</h3>
          <span className="text-accent opacity-0 transition-opacity group-hover:opacity-100">→</span>
        </div>
        <p className="mt-1.5 text-sm text-muted">{body}</p>
      </Card>
    </Link>
  );
}
