import type { Banner as BannerType } from "@/types/api";

const TONE: Record<string, string> = {
  bootstrap: "border-warn-border bg-warn-soft text-warn",
  weak: "border-warn-border bg-warn-soft text-warn",
  judge: "border-accent-border bg-accent-soft text-accent",
  none: "border-line bg-surface text-muted",
};

const ICON: Record<string, string> = {
  bootstrap: "▲",
  weak: "▲",
  judge: "◆",
  none: "•",
};

/** Honesty banner. Surfaces the BOOTSTRAP / LLM-JUDGED caveats the research carries. */
export function Banner({ banner }: { banner: BannerType }) {
  if (!banner?.text) return null;
  return (
    <div
      role="note"
      className={`flex items-start gap-2.5 rounded-md border px-3.5 py-2.5 text-xs leading-relaxed ${
        TONE[banner.kind] ?? TONE.none
      }`}
    >
      <span aria-hidden className="mt-px shrink-0 text-[0.7rem]">
        {ICON[banner.kind] ?? ICON.none}
      </span>
      <span>{banner.text}</span>
    </div>
  );
}
