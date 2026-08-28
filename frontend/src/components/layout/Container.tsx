import type { ReactNode } from "react";
import { cx } from "@/components/ui/primitives";

export function Container({
  children,
  className,
  size = "default",
}: {
  children: ReactNode;
  className?: string;
  size?: "default" | "wide" | "prose";
}) {
  const max =
    size === "wide" ? "max-w-7xl" : size === "prose" ? "max-w-3xl" : "max-w-6xl";
  return <div className={cx("mx-auto w-full px-6", max, className)}>{children}</div>;
}
