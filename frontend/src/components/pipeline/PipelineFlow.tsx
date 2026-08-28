import type { PipelineStage } from "@/types/api";
import { cx } from "@/components/ui/primitives";

/** Compact, horizontal stage flow. Optionally selectable (used interactively on /pipeline). */
export function PipelineFlow({
  stages,
  activeKey,
  onSelect,
}: {
  stages: PipelineStage[];
  activeKey?: string;
  onSelect?: (key: string) => void;
}) {
  return (
    <div className="flex flex-wrap items-stretch gap-1.5">
      {stages.map((s, i) => {
        const active = s.key === activeKey;
        const clickable = !!onSelect;
        const Tag = clickable ? "button" : "div";
        return (
          <div key={s.key} className="flex items-stretch gap-1.5">
            <Tag
              onClick={clickable ? () => onSelect!(s.key) : undefined}
              className={cx(
                "flex min-w-0 flex-col justify-center rounded-md border px-3 py-2 text-left transition-colors",
                active
                  ? "border-accent bg-accent-soft"
                  : "border-line bg-paper",
                clickable && !active && "hover:border-accent-border hover:bg-surface",
              )}
            >
              <span className="text-[0.65rem] font-medium uppercase tracking-wide text-faint">
                {String(i + 1).padStart(2, "0")}
              </span>
              <span className={cx("text-sm font-medium", active ? "text-accent" : "text-ink")}>
                {s.title}
              </span>
            </Tag>
            {i < stages.length - 1 && (
              <span aria-hidden className="flex items-center text-line-strong">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M5 12h14M13 6l6 6-6 6" />
                </svg>
              </span>
            )}
          </div>
        );
      })}
    </div>
  );
}
