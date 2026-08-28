import { lazy, useEffect } from "react";
import { Route, Routes, useLocation } from "react-router-dom";
import { RootLayout } from "@/components/layout/RootLayout";
import { Home } from "@/pages/Home";

// Route-level code splitting: the heavier pages (markdown, tables) load on demand.
const Research = lazy(() => import("@/pages/Research"));
const DocView = lazy(() => import("@/pages/DocView"));
const Pipeline = lazy(() => import("@/pages/Pipeline"));
const Results = lazy(() => import("@/pages/Results"));
const Analysis = lazy(() => import("@/pages/Analysis"));
const AppDetail = lazy(() => import("@/pages/AppDetail"));
const PrcsDetail = lazy(() => import("@/pages/PrcsDetail"));
const About = lazy(() => import("@/pages/About"));
const NotFound = lazy(() => import("@/pages/NotFound"));

function ScrollToTop() {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);
  return null;
}

export function App() {
  return (
    <>
      <ScrollToTop />
      <Routes>
        <Route element={<RootLayout />}>
          <Route index element={<Home />} />
          <Route path="research" element={<Research />} />
          <Route path="research/:slug" element={<DocView />} />
          <Route path="pipeline" element={<Pipeline />} />
          <Route path="results" element={<Results />} />
          <Route path="analysis" element={<Analysis />} />
          <Route path="analysis/apps/:package" element={<AppDetail />} />
          <Route path="analysis/prcs/:id" element={<PrcsDetail />} />
          <Route path="about" element={<About />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </>
  );
}
