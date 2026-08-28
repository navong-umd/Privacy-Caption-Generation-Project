// TanStack Query hooks + a shared client. Caching + dedupe + stale-while-revalidate.

import { QueryClient, useQuery } from "@tanstack/react-query";
import { apiGet } from "./client";
import type {
  AppDetail,
  AppSummary,
  CaptionPage,
  CaptionResults,
  ClassificationResults,
  ComplianceResults,
  DocContent,
  DocMeta,
  ExperimentsStatus,
  Overview,
  PrcsDetail,
  PrcsPage,
} from "@/types/api";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 min: research data is static within a session
      gcTime: 30 * 60 * 1000,
      refetchOnWindowFocus: false,
      retry: (count, err) => {
        // Do not retry 4xx; retry transient network/5xx once.
        const status = (err as { status?: number })?.status ?? 0;
        if (status >= 400 && status < 500) return false;
        return count < 1;
      },
    },
  },
});

// ---- filters ----
export interface PrcsFilters {
  app?: string;
  pi_category?: string;
  sink_type?: string;
  practice?: string;
  purpose?: string;
  label_source?: string;
  split?: string;
  q?: string;
  page?: number;
  page_size?: number;
}

export interface CaptionFilters {
  app?: string;
  provider?: "llm" | "mock";
  q?: string;
  page?: number;
  page_size?: number;
}

// ---- hooks ----
export const useOverview = () =>
  useQuery({ queryKey: ["overview"], queryFn: () => apiGet<Overview>("/api/overview") });

export const useApps = () =>
  useQuery({ queryKey: ["apps"], queryFn: () => apiGet<AppSummary[]>("/api/apps") });

export const useApp = (pkg: string | undefined) =>
  useQuery({
    queryKey: ["app", pkg],
    queryFn: () => apiGet<AppDetail>(`/api/apps/${pkg}`),
    enabled: !!pkg,
  });

export const usePrcsList = (filters: PrcsFilters) =>
  useQuery({
    queryKey: ["prcs", filters],
    queryFn: ({ signal }) =>
      apiGet<PrcsPage>("/api/prcs", filters as Record<string, unknown>, signal),
    placeholderData: (prev) => prev, // keep previous page visible while fetching next
  });

export const usePrcs = (id: string | undefined) =>
  useQuery({
    queryKey: ["prcs-detail", id],
    queryFn: () => apiGet<PrcsDetail>(`/api/prcs/${id}`),
    enabled: !!id,
  });

export const useCaptions = (filters: CaptionFilters) =>
  useQuery({
    queryKey: ["captions", filters],
    queryFn: ({ signal }) =>
      apiGet<CaptionPage>("/api/captions", filters as Record<string, unknown>, signal),
    placeholderData: (prev) => prev,
  });

export const useClassification = () =>
  useQuery({
    queryKey: ["results", "classification"],
    queryFn: () => apiGet<ClassificationResults>("/api/results/classification"),
  });

export const useCaptionResults = () =>
  useQuery({
    queryKey: ["results", "captions"],
    queryFn: () => apiGet<CaptionResults>("/api/results/captions"),
  });

export const useCompliance = () =>
  useQuery({
    queryKey: ["results", "compliance"],
    queryFn: () => apiGet<ComplianceResults>("/api/results/compliance"),
  });

export const useExperiments = () =>
  useQuery({
    queryKey: ["results", "experiments"],
    queryFn: () => apiGet<ExperimentsStatus>("/api/results/experiments"),
  });

export const useDocs = () =>
  useQuery({ queryKey: ["docs"], queryFn: () => apiGet<DocMeta[]>("/api/docs") });

export const useDoc = (slug: string | undefined) =>
  useQuery({
    queryKey: ["doc", slug],
    queryFn: () => apiGet<DocContent>(`/api/docs/${slug}`),
    enabled: !!slug,
  });

// Prefetch helpers for predictable navigation (hover on links).
export const prefetchApp = (pkg: string) =>
  queryClient.prefetchQuery({
    queryKey: ["app", pkg],
    queryFn: () => apiGet<AppDetail>(`/api/apps/${pkg}`),
  });

export const prefetchPrcs = (id: string) =>
  queryClient.prefetchQuery({
    queryKey: ["prcs-detail", id],
    queryFn: () => apiGet<PrcsDetail>(`/api/prcs/${id}`),
  });
