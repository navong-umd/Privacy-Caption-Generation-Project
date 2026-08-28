import { Suspense } from "react";
import { Outlet, useLocation } from "react-router-dom";
import { Nav } from "./Nav";
import { Footer } from "./Footer";
import { Container } from "./Container";
import { LoadingRows } from "@/components/ui/states";

export function RootLayout() {
  const location = useLocation();
  return (
    <div className="flex min-h-screen flex-col bg-paper">
      <Nav />
      <main className="flex-1">
        {/* key on pathname so route content re-mounts with a subtle fade */}
        <div key={location.pathname} className="fade-in py-10">
          <Suspense
            fallback={
              <Container>
                <LoadingRows rows={5} />
              </Container>
            }
          >
            <Outlet />
          </Suspense>
        </div>
      </main>
      <Footer />
    </div>
  );
}
