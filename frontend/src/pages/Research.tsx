import { Link } from "react-router-dom";
import { Container } from "@/components/layout/Container";
import { useDocs } from "@/api/queries";
import { Card, Section } from "@/components/ui/primitives";
import { ErrorState, LoadingRows } from "@/components/ui/states";

const QUESTIONS = [
  {
    q: "Does a privacy graph improve classification?",
    a: "Whether an RGCN over the full Privacy Property Graph beats a code-only baseline at predicting privacy Practice and Purpose.",
  },
  {
    q: "Which part of the graph carries the signal?",
    a: "Isolating the contribution of program structure, the knowledge-base overlay, and code tokens through an eight-arm ablation.",
  },
  {
    q: "Which evidence yields the best caption?",
    a: "Across six conditions (code only through full evidence), which representation produces the most accurate, grounded caption.",
  },
  {
    q: "Are captions evidence-grounded?",
    a: "What fraction of generated captions actually mention the data type and sink present in the evidence, with no invented recipients.",
  },
];

const METHOD = [
  { t: "App Property Graph (APG)", d: "Four interlocking views of the program: syntax tree, call graph, control flow, and data dependence." },
  { t: "Knowledge Base", d: "Classifies each API as a personal-information source or a data sink, with a provenance tier and Android permission." },
  { t: "Privacy Property Graph (PPG)", d: "Overlays privacy semantics and taint flows on the APG, each edge tagged with the rule that produced it." },
  { t: "Privacy-Relevant Code Slice (PRCS)", d: "One subgraph per source-to-sink flow, carrying full provenance back to the APK." },
  { t: "PAcT labels", d: "Multi-label Practice (Collecting / Processing / Sharing) and Purpose (Functionality / Advertisement / Analytics)." },
  { t: "Caption generation", d: "Evidence-grounded natural-language captions and GDPR/CCPA policy notices, verified against the evidence." },
];

export default function Research() {
  const docs = useDocs();

  return (
    <Container>
      <header className="border-b border-line pb-6">
        <div className="text-xs font-medium uppercase tracking-widest text-accent">Methodology</div>
        <h1 className="mt-2 text-2xl font-semibold text-ink">Research</h1>
        <p className="mt-3 max-w-2xl text-[0.975rem] leading-relaxed text-muted">
          Prior work captions code by encoding syntax-tree paths with a sequence model, a linear view
          that loses data-flow context. We instead represent a program as a privacy-aware graph and
          ask whether that representation improves privacy behavior understanding and caption
          generation.
        </p>
      </header>

      <Section eyebrow="Motivation" title="The problem">
        <div className="max-w-3xl space-y-3 text-[0.95rem] leading-relaxed text-muted">
          <p>
            Android apps collect personal data and send it to servers, storage, logs, and other
            components. Understanding <em>what</em> data an app touches, <em>where</em> it flows, and
            <em> why</em> is hard to do at scale, and privacy policies rarely reflect actual behavior.
          </p>
          <p>
            We build the behavior directly from the bytecode: trace real source-to-sink flows, attach
            privacy semantics from a knowledge base, and generate a caption grounded in that evidence
            rather than in free-form generation.
          </p>
        </div>
      </Section>

      <Section eyebrow="Investigation" title="Research questions">
        <div className="grid gap-3 sm:grid-cols-2">
          {QUESTIONS.map((x, i) => (
            <Card key={i} className="px-5 py-4">
              <div className="flex gap-3">
                <span className="mono text-sm font-semibold text-accent">Q{i + 1}</span>
                <div>
                  <h3 className="text-sm font-semibold text-ink">{x.q}</h3>
                  <p className="mt-1 text-sm text-muted">{x.a}</p>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </Section>

      <Section eyebrow="Approach" title="How the method works">
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {METHOD.map((m, i) => (
            <Card key={m.t} className="px-4 py-4">
              <div className="mb-1 text-xs font-semibold text-accent">{String(i + 1).padStart(2, "0")}</div>
              <h3 className="text-sm font-semibold text-ink">{m.t}</h3>
              <p className="mt-1 text-sm text-muted">{m.d}</p>
            </Card>
          ))}
        </div>
      </Section>

      <Section
        eyebrow="Reference"
        title="Documentation"
        description="The full research write-up: one document per subsystem, schema, and experiment, generated alongside the code."
      >
        {docs.isLoading ? (
          <LoadingRows rows={6} />
        ) : docs.isError ? (
          <ErrorState error={docs.error} onRetry={() => docs.refetch()} />
        ) : docs.data ? (
          <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {docs.data.map((d) => (
              <Link
                key={d.slug}
                to={`/research/${d.slug}`}
                className="group flex items-center justify-between rounded-md border border-line bg-paper px-3.5 py-2.5 transition-colors hover:border-accent-border hover:bg-surface"
              >
                <span className="min-w-0 truncate text-sm text-ink">{d.title}</span>
                <span className="ml-2 shrink-0 text-faint transition-colors group-hover:text-accent">→</span>
              </Link>
            ))}
          </div>
        ) : null}
      </Section>
    </Container>
  );
}
