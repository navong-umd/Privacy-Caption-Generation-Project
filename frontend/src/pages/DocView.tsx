import { Link, useParams } from "react-router-dom";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Container } from "@/components/layout/Container";
import { useDoc } from "@/api/queries";
import { ErrorState, LoadingRows } from "@/components/ui/states";

export default function DocView() {
  const { slug } = useParams();
  const { data, isLoading, isError, error, refetch } = useDoc(slug);

  return (
    <Container size="prose">
      <div className="mb-6 text-sm">
        <Link to="/research" className="text-muted hover:text-accent">
          ← Documentation
        </Link>
      </div>

      {isLoading ? (
        <LoadingRows rows={10} />
      ) : isError ? (
        <ErrorState error={error} onRetry={() => refetch()} />
      ) : data ? (
        <article className="markdown">
          <Markdown
            remarkPlugins={[remarkGfm]}
            components={{
              // Keep long identifiers from breaking the layout.
              code: ({ children }) => (
                <code style={{ overflowWrap: "anywhere" }}>{children}</code>
              ),
              a: ({ href, children }) => {
                // Internal repo links (relative .md) are not navigable here; render as plain text.
                if (href?.startsWith("http"))
                  return (
                    <a href={href} target="_blank" rel="noreferrer">
                      {children}
                    </a>
                  );
                return <span className="text-muted">{children}</span>;
              },
            }}
          >
            {data.markdown}
          </Markdown>
        </article>
      ) : null}
    </Container>
  );
}
