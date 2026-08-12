# InsightSearch

### Semantic search for knowledge bases, grounded by Gemini.

InsightSearch is a small full-stack retrieval-augmented generation (RAG) application. Users ask questions in natural language, the backend embeds the query, retrieves the most semantically similar documents using cosine similarity, and asks Gemini to produce a grounded answer with transparent source references.

## Features

- Natural-language semantic search
- Gemini embeddings for query and document vectors
- Cosine-similarity retrieval over a local JSON dataset
- Gemini-generated grounded answers
- Source cards with relevance scores
- Loading, empty, error, and success states
- Responsive recruiter-friendly UI
- No database, Docker, authentication, or vector database

## Architecture

```text
React + TypeScript
       |
       | POST /api/search
       v
FastAPI
       |
       +--> Gemini Embeddings
       |        |
       |        v
       |   Cosine Similarity
       |        |
       |        v
       |   Top-K Documents
       |
       +--> Gemini Generation
                |
                v
        Grounded Answer + Sources
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, TypeScript |
| Backend | Python, FastAPI |
| Embeddings | Gemini Embeddings |
| Generation | Gemini |
| Retrieval | Cosine similarity |
| Data | Local JSON |
| Icons | Lucide React |

## Local Setup

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your Gemini API key to `backend/.env`.

Start the API:

```bash
uvicorn app.main:app --reload --port 8000
```

Health check:

```text
http://127.0.0.1:8000/health
```

### 2. Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

Vite proxies `/api` requests to the FastAPI server on port 8000.

## Example Queries

Try:

- What is our remote work policy?
- How does the refund process work?
- What should I do if a customer reports a security issue?
- How much can employees spend on professional development?
- What are the requirements for a production release?
- How long are operational logs retained?

## Retrieval Pipeline

1. Documents are loaded from `backend/data/documents.json`.
2. Document text is embedded with Gemini.
3. A user query is embedded using the retrieval-query task type.
4. Cosine similarity ranks documents against the query.
5. The top documents are placed into a constrained generation prompt.
6. Gemini produces an answer using only the retrieved context.
7. The API returns the answer plus source titles, snippets, and similarity scores.

The MVP intentionally keeps vectors in memory. This makes the implementation easy to inspect while demonstrating the core semantic-search and RAG concepts without introducing a database or vector store.

## Environment Variables

`backend/.env`:

```env
GEMINI_API_KEY=your-gemini-api-key
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
GEMINI_MODEL=gemini-2.5-flash
```

Never commit API keys.

## Project Structure

```text
insight-search/
├── backend/
│   ├── app/
│   │   └── main.py
│   ├── data/
│   │   └── documents.json
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── styles.css
│   ├── package.json
│   └── vite.config.ts
├── .env.example
├── .gitignore
└── README.md
```

## Future Improvements

- Persist document embeddings between restarts
- Upload and index user-provided documents
- Incremental embedding instead of startup embedding
- Hybrid keyword + semantic retrieval
- Streaming answer generation
- Authentication and per-user knowledge bases
- Evaluation set for retrieval precision and answer faithfulness

## Portfolio

InsightSearch demonstrates a complete semantic-search and RAG pipeline while intentionally keeping the implementation small enough to understand end to end.
