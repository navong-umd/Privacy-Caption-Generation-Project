import { Link } from "react-router-dom";
import { Container } from "@/components/layout/Container";
import { Card, Section } from "@/components/ui/primitives";

const STACK = [
  { area: "Static analysis", items: ["androguard (Dalvik disassembly)", "NetworkX graphs"] },
  { area: "Privacy analysis", items: ["Taint propagation", "SuSi source/sink catalog", "LINDDUN threat model"] },
  { area: "Learning", items: ["PyTorch Geometric (RGCN)", "scikit-learn baselines"] },
  { area: "Generation", items: ["LLM captions (provider-agnostic)", "GDPR / CCPA policy assembly"] },
  { area: "Serving", items: ["FastAPI (read-only API)", "Python 3.14"] },
  { area: "Interface", items: ["React + TypeScript", "Vite + Tailwind", "TanStack Query"] },
];

export default function About() {
  return (
    <Container size="prose">
      <header className="border-b border-line pb-6">
        <div className="text-xs font-medium uppercase tracking-widest text-accent">About</div>
        <h1 className="mt-2 text-2xl font-semibold text-ink">About this project</h1>
      </header>

      <Section eyebrow="Overview" title="What this is">
        <div className="space-y-3 text-[0.95rem] leading-relaxed text-muted">
          <p>
            Privacy Caption Generation is a research pipeline for Android privacy analysis. It takes
            an APK, builds a privacy-aware graph of the program, traces how personal data flows to
            sinks, classifies the privacy practice and purpose, and generates evidence-grounded
            privacy captions and GDPR/CCPA policy notices.
          </p>
          <p>
            This site is a read-only window onto a real pipeline run over seven popular Android apps.
            Every figure is served from an on-disk artifact. Results computed on heuristic labels or
            scored by an LLM judge are marked as such; human evaluation is a reserved final gate.
          </p>
        </div>
      </Section>

      <Section eyebrow="Goals" title="Research goals">
        <ul className="space-y-2 text-[0.95rem] text-muted">
          {[
            "Represent Android programs as privacy-aware graphs rather than linear token sequences.",
            "Trace personal-data flows with defensible, per-edge provenance.",
            "Generate privacy captions grounded strictly in the analyzed evidence.",
            "Evaluate whether the graph representation improves over code-only baselines.",
          ].map((g) => (
            <li key={g} className="flex gap-2">
              <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-accent" />
              <span>{g}</span>
            </li>
          ))}
        </ul>
      </Section>

      <Section eyebrow="Technology" title="Stack">
        <div className="grid gap-3 sm:grid-cols-2">
          {STACK.map((s) => (
            <Card key={s.area} className="px-4 py-4">
              <div className="text-xs font-medium uppercase tracking-wide text-faint">{s.area}</div>
              <ul className="mt-2 space-y-1 text-sm text-ink">
                {s.items.map((i) => (
                  <li key={i}>{i}</li>
                ))}
              </ul>
            </Card>
          ))}
        </div>
      </Section>

      <Section eyebrow="Provenance" title="Team, affiliation, and references">
        <Card className="px-5 py-4 text-sm text-muted">
          <p>
            The repository does not specify a research team, institutional affiliation, or associated
            publications, so none are listed here. This page will not fabricate them. Contributor
            identity is available from the project's version-control history.
          </p>
          <p className="mt-3">
            For the technical write-up, see the{" "}
            <Link to="/research" className="text-accent hover:underline">
              research documentation
            </Link>{" "}
            or the{" "}
            <a
              className="text-accent hover:underline"
              href={`${(import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "")}/docs`}
              target="_blank"
              rel="noreferrer"
            >
              API reference
            </a>
            .
          </p>
        </Card>
      </Section>
    </Container>
  );
}
