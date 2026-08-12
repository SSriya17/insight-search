import { useState } from "react";
import {
  ArrowUpRight,
  BrainCircuit,
  CheckCircle2,
  ChevronDown,
  Clock3,
  FileText,
  Search,
  Sparkles,
  TriangleAlert,
} from "lucide-react";

type Source = {
  id: string;
  title: string;
  category: string;
  snippet: string;
  score: number;
};

type SearchResponse = {
  answer: string;
  sources: Source[];
  query: string;
  took_ms: number;
};

const examples = [
  "What is our remote work policy?",
  "How does the refund process work?",
  "What should I do if a customer reports a security issue?",
];

function scoreLabel(score: number) {
  if (score >= 0.85) return "Highly relevant";
  if (score >= 0.7) return "Relevant";
  return "Related";
}

function App() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showSources, setShowSources] = useState(true);

  async function search() {
    const trimmed = query.trim();
    if (!trimmed || loading) return;

    setLoading(true);
    setError("");
    try {
      const apiBaseUrl = import.meta.env.VITE_API_URL || "";
    
      const response = await fetch(`${apiBaseUrl}/api/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: trimmed, top_k: 4 }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Search failed.");
      setResult(data);
    } catch (err) {
      setResult(null);
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark"><Sparkles size={16} /></div>
          <span>InsightSearch</span>
        </div>
        <div className="status-pill">
          <span className="status-dot" />
          AI knowledge search
        </div>
      </header>

      <main className="main">
        <section className="hero">
          <div className="eyebrow"><BrainCircuit size={15} /> Semantic retrieval, grounded answers</div>
          <h1>Find the insight,<br /><span>not just the keyword.</span></h1>
          <p>
            Ask questions in plain language. InsightSearch finds the most relevant
            documents, then uses Gemini to synthesize an answer with transparent sources.
          </p>
        </section>

        <section className="search-card">
          <div className="search-row">
            <Search size={21} className="search-icon" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && search()}
              placeholder="Ask anything about your knowledge base..."
              aria-label="Search your knowledge base"
            />
            <button onClick={search} disabled={!query.trim() || loading}>
              {loading ? "Searching..." : "Search"}
              {!loading && <ArrowUpRight size={17} />}
            </button>
          </div>
          <div className="examples">
            <span>Try</span>
            {examples.map((example) => (
              <button key={example} onClick={() => setQuery(example)}>
                {example}
              </button>
            ))}
          </div>
        </section>

        {error && (
          <div className="notice error">
            <TriangleAlert size={18} />
            <div>
              <strong>Search unavailable</strong>
              <span>{error}</span>
            </div>
          </div>
        )}

        {loading && (
          <section className="results">
            <div className="result-heading">
              <div className="skeleton title-skeleton" />
              <div className="skeleton meta-skeleton" />
            </div>
            <div className="answer-card loading-card">
              <div className="skeleton line wide" />
              <div className="skeleton line" />
              <div className="skeleton line medium" />
            </div>
          </section>
        )}

        {!loading && result && (
          <section className="results">
            <div className="result-heading">
              <div>
                <span className="section-label">ANSWER</span>
                <h2>Here’s what I found</h2>
              </div>
              <div className="timing"><Clock3 size={14} /> {result.took_ms}ms</div>
            </div>

            <article className="answer-card">
              <div className="answer-badge"><CheckCircle2 size={15} /> Grounded in your documents</div>
              <p>{result.answer}</p>
            </article>

            <div className="sources-header">
              <div>
                <span className="section-label">SOURCES</span>
                <h2>{result.sources.length} relevant documents</h2>
              </div>
              <button className="collapse" onClick={() => setShowSources(!showSources)}>
                {showSources ? "Hide" : "Show"} sources <ChevronDown size={16} className={showSources ? "rotated" : ""} />
              </button>
            </div>

            {showSources && (
              <div className="source-grid">
                {result.sources.map((source, index) => (
                  <article className="source-card" key={source.id}>
                    <div className="source-top">
                      <div className="source-icon"><FileText size={17} /></div>
                      <span className="source-number">0{index + 1}</span>
                    </div>
                    <span className="category">{source.category}</span>
                    <h3>{source.title}</h3>
                    <p>{source.snippet}</p>
                    <div className="source-bottom">
                      <div>
                        <strong>{Math.round(source.score * 100)}%</strong>
                        <span>{scoreLabel(source.score)}</span>
                      </div>
                      <div className="score-track">
                        <span style={{ width: `${Math.min(source.score * 100, 100)}%` }} />
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </section>
        )}

        {!loading && !result && !error && (
          <section className="empty-state">
            <div className="empty-icon"><Search size={22} /></div>
            <h2>Your knowledge base is ready.</h2>
            <p>Ask a question above to retrieve relevant context and generate a grounded answer.</p>
          </section>
        )}
      </main>

      <footer>
        <span>InsightSearch</span>
        <span>Semantic search · Gemini · FastAPI</span>
      </footer>
    </div>
  );
}

export default App;
