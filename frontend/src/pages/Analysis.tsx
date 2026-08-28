import { useState } from "react";
import { Container } from "@/components/layout/Container";
import { Tabs } from "@/components/ui/controls";
import { AppsPanel } from "@/components/analysis/AppsPanel";
import { PrcsPanel } from "@/components/analysis/PrcsPanel";
import { CaptionsPanel } from "@/components/analysis/CaptionsPanel";
import { useOverview } from "@/api/queries";
import { int } from "@/lib/format";

type Tab = "apps" | "prcs" | "captions";

export default function Analysis() {
  const [tab, setTab] = useState<Tab>("apps");
  const { data } = useOverview();

  return (
    <Container>
      <header className="border-b border-line pb-6">
        <div className="text-xs font-medium uppercase tracking-widest text-accent">Data</div>
        <h1 className="mt-2 text-2xl font-semibold text-ink">Analysis</h1>
        <p className="mt-2 max-w-2xl text-sm text-muted">
          Inspect the analyzed apps, browse individual privacy slices with their source-to-sink
          flows, and read the generated captions. Everything here comes from the real corpus run.
        </p>
      </header>

      <div className="mt-6">
        <Tabs
          active={tab}
          onChange={(k) => setTab(k as Tab)}
          tabs={[
            { key: "apps", label: "Apps", count: data?.n_apps },
            { key: "prcs", label: "Privacy Slices", count: data?.n_prcs },
            { key: "captions", label: "Captions", count: data?.n_captions_llm },
          ]}
        />
      </div>

      <div className="mt-6">
        {tab === "apps" && <AppsPanel />}
        {tab === "prcs" && <PrcsPanel />}
        {tab === "captions" && <CaptionsPanel />}
      </div>

      {tab === "prcs" && data && (
        <p className="mt-4 text-xs text-faint">
          {int(data.n_prcs)} slices across {int(data.n_apps)} apps. Click any row for its full
          subgraph, code, and caption.
        </p>
      )}
    </Container>
  );
}
