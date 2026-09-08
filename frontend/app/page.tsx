"use client";

import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

type Source = {
  document_id: string;
  filename: string;
  page: number;
};

type Evidence = {
  text: string;
  verified: boolean;
};

type Fact = {
  id: number;
  subject: string;
  predicate: string;
  value: string;
  value_type: string;
  unit?: string | null;
  period?: string | null;
  scope?: string | null;
  confidence: number;
  extraction_method: string;
  evidence: Evidence;
  source: Source;
};

type RelationshipFact = {
  fact_id: number;
  role: string;
  subject: string;
  predicate: string;
  value: string;
  value_type: string;
  unit?: string | null;
  period?: string | null;
  scope?: string | null;
  confidence: number;
  evidence: Evidence;
  source: Source;
};

type Relationship = {
  id: number;
  relationship_type: string;
  confidence: number;
  explanation: string;
  facts: RelationshipFact[];
};

type Document = {
  id: number;
  document_id: string;
  filename: string;
  uploaded_at: string;
};

function formatValue(fact: { value: string; unit?: string | null }) {
  const value = Number(fact.value);

  if (Number.isNaN(value)) {
    return `${fact.value}${fact.unit ? ` ${fact.unit}` : ""}`;
  }

  const formatted = new Intl.NumberFormat("en-IN", {
    maximumFractionDigits: 2,
  }).format(value);

  return `${formatted}${fact.unit ? ` ${fact.unit}` : ""}`;
}

function relationshipLabel(type: string) {
  switch (type) {
    case "CORROBORATES":
      return "Corroborated";
    case "RECONCILED":
      return "Reconciled";
    case "LIKELY_DISAGREEMENT":
      return "Likely disagreement";
    case "CONTRADICTS":
      return "Contradiction";
    case "CONTEXTUAL_DIFFERENCE":
      return "Contextual difference";
    case "UNRESOLVED":
      return "Unresolved";
    default:
      return type.replaceAll("_", " ");
  }
}

function relationshipIcon(type: string) {
  switch (type) {
    case "CORROBORATES":
      return "✓";
    case "RECONCILED":
      return "=";
    case "LIKELY_DISAGREEMENT":
      return "!";
    case "CONTRADICTS":
      return "×";
    case "UNRESOLVED":
      return "?";
    default:
      return "•";
  }
}

export default function Home() {
  const [facts, setFacts] = useState<Fact[]>([]);
  const [relationships, setRelationships] = useState<Relationship[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);

  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [pagesInput, setPagesInput] = useState("");

  async function loadData() {
    try {
      setLoading(true);

      const [factsResponse, relationshipsResponse, documentsResponse] =
        await Promise.all([
          fetch(`${API_URL}/facts/`),
          fetch(`${API_URL}/relationships/`),
          fetch(`${API_URL}/documents/`),
        ]);

      if (!factsResponse.ok || !relationshipsResponse.ok) {
        throw new Error("Backend request failed");
      }

      const factsData = await factsResponse.json();
      const relationshipsData = await relationshipsResponse.json();
      const documentsData = await documentsResponse.json();

      setFacts(factsData);
      setRelationships(relationshipsData);
      setDocuments(documentsData);
    } catch (error) {
      console.error(error);
      setUploadMessage(
        "Unable to connect to FactLens API. Make sure FastAPI is running."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  async function handleUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setUploadMessage("Please upload a PDF file.");
      return;
    }

    const formData = new FormData();

    formData.append("file", file);

    if (pagesInput.trim()) {
      formData.append("pages", pagesInput.trim());
    }

    setUploading(true);
    setUploadMessage(`Processing ${file.name}...`);

    try {
      const response = await fetch(`${API_URL}/documents/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed");
      }

      if (data.status === "duplicate") {
        setUploadMessage("This document has already been processed.");
      } else {
        setUploadMessage(
          pagesInput.trim()
            ? `Processed ${file.name} — page(s) ${pagesInput.trim()}.`
            : `Processed ${file.name}.`
        );
      }

      await loadData();
    } catch (error) {
      console.error(error);

      setUploadMessage(
        error instanceof Error ? error.message : "Upload failed."
      );
    } finally {
      setUploading(false);
      event.target.value = "";
      setPagesInput("");
    }
  }

  const relationshipCounts = {
    corroborated: relationships.filter(
      (r) => r.relationship_type === "CORROBORATES"
    ).length,

    reconciled: relationships.filter(
      (r) => r.relationship_type === "RECONCILED"
    ).length,

    disagreement: relationships.filter(
      (r) => r.relationship_type === "LIKELY_DISAGREEMENT"
    ).length,

    unresolved: relationships.filter(
      (r) => r.relationship_type === "UNRESOLVED"
    ).length,
  };

  return (
    <main className="min-h-screen bg-[#f6f7f9] text-[#17181a]">
      {/* Header */}
      <header className="border-b border-black/10 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
          <div>
            <div className="text-xl font-semibold tracking-tight">FACTLENS</div>

            <div className="mt-0.5 text-xs uppercase tracking-[0.2em] text-black/45">
              Fact Knowledge Layer
            </div>
          </div>

          <div className="flex items-center gap-2 rounded-full border border-black/10 px-3 py-1.5 text-xs font-medium">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            SYSTEM ONLINE
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-6 py-10">
        {/* Hero */}
        <section className="mb-10">
          <div className="max-w-3xl">
            <div className="mb-4 text-xs font-semibold uppercase tracking-[0.22em] text-black/45">
              Financial document intelligence
            </div>

            <h1 className="text-4xl font-semibold leading-tight tracking-tight md:text-5xl">
              Extract facts.
              <br />
              Ground evidence.
              <br />
              Reconcile meaning.
            </h1>

            <p className="mt-5 max-w-2xl text-base leading-7 text-black/55">
              FactLens transforms financial documents into grounded facts and
              identifies corroboration, reconciliation, disagreement, and
              unresolved evidence across sources.
            </p>
          </div>
        </section>

        {/* Upload */}
        <section className="mb-8">
          <div className="grid gap-4 md:grid-cols-[1fr_220px]">
            {/* PDF upload */}
            <label
              htmlFor="pdf-upload"
              className={`group block cursor-pointer rounded-2xl border-2 border-dashed border-black/15 bg-white p-8 transition hover:border-black/30 hover:bg-black/[0.015] ${
                uploading ? "pointer-events-none opacity-60" : ""
              }`}
            >
              <div className="flex flex-col items-center justify-center text-center">
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-black text-xl text-white">
                  ↑
                </div>

                <h2 className="text-lg font-semibold">
                  {uploading
                    ? "Processing document..."
                    : "Upload a financial PDF"}
                </h2>

                <p className="mt-2 text-sm text-black/45">
                  Drop a document here or click to browse
                </p>

                <div className="mt-5 rounded-lg border border-black/10 px-4 py-2 text-sm font-medium">
                  {uploading ? "Processing..." : "Choose PDF"}
                </div>
              </div>

              <input
                id="pdf-upload"
                type="file"
                accept=".pdf,application/pdf"
                className="hidden"
                onChange={handleUpload}
                disabled={uploading}
              />
            </label>

            {/* Page selector */}
            <div className="rounded-2xl border border-black/10 bg-white p-6">
              <div className="text-xs font-semibold uppercase tracking-[0.15em] text-black/40">
                Processing scope
              </div>

              <label htmlFor="pages" className="mt-4 block text-sm font-medium">
                Pages
              </label>

              <input
                id="pages"
                type="text"
                value={pagesInput}
                onChange={(event) => setPagesInput(event.target.value)}
                placeholder="e.g. 6 or 6,9"
                disabled={uploading}
                className="mt-2 w-full rounded-lg border border-black/10 bg-[#f6f7f9] px-3 py-2.5 text-sm outline-none transition focus:border-black/30"
              />

              <p className="mt-3 text-xs leading-5 text-black/40">
                Specify pages to process. Leave blank to process the entire
                document.
              </p>

              <div className="mt-4 rounded-lg bg-black/[0.03] p-3 text-xs leading-5 text-black/50">
                For large PDFs, selective processing reduces unnecessary LLM
                calls.
              </div>
            </div>
          </div>

          {uploadMessage && (
            <div className="mt-3 rounded-xl border border-black/10 bg-white px-4 py-3 text-sm text-black/60">
              {uploadMessage}
            </div>
          )}
        </section>

        {/* Stats */}
        <section className="mb-10 grid grid-cols-2 gap-3 md:grid-cols-5">
          <StatCard label="Documents" value={documents.length} />

          <StatCard label="Facts" value={facts.length} />

          <StatCard label="Relationships" value={relationships.length} />

          <StatCard
            label="Corroborated"
            value={relationshipCounts.corroborated}
          />

          <StatCard label="Reconciled" value={relationshipCounts.reconciled} />
        </section>

        {/* Main content */}
        {loading ? (
          <div className="rounded-2xl border border-black/10 bg-white p-12 text-center">
            <div className="text-sm text-black/45">
              Loading knowledge layer...
            </div>
          </div>
        ) : (
          <>
            {/* Facts */}
            <section className="mb-12">
              <SectionHeading
                title="Extracted facts"
                subtitle="Structured numerical and semantic facts grounded in source evidence."
              />

              {facts.length === 0 ? (
                <EmptyState text="No facts extracted yet." />
              ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {facts.map((fact) => (
                    <FactCard key={fact.id} fact={fact} />
                  ))}
                </div>
              )}
            </section>

            {/* Relationships */}
            <section>
              <SectionHeading
                title="Reasoning & relationships"
                subtitle="How facts from different sources relate to one another."
              />

              {relationships.length === 0 ? (
                <EmptyState text="No relationships detected yet." />
              ) : (
                <div className="space-y-4">
                  {relationships.map((relationship) => (
                    <RelationshipCard
                      key={relationship.id}
                      relationship={relationship}
                    />
                  ))}
                </div>
              )}
            </section>
          </>
        )}
      </div>

      {/* Footer */}
      <footer className="border-t border-black/10 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6 text-xs text-black/40">
          <span>FactLens · Superjoin assignment</span>
          <span>Grounded AI · Evidence first</span>
        </div>
      </footer>
    </main>
  );
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-xl border border-black/10 bg-white p-5">
      <div className="text-2xl font-semibold">{value}</div>

      <div className="mt-1 text-xs uppercase tracking-[0.12em] text-black/40">
        {label}
      </div>
    </div>
  );
}

function SectionHeading({
  title,
  subtitle,
}: {
  title: string;
  subtitle: string;
}) {
  return (
    <div className="mb-5">
      <h2 className="text-2xl font-semibold tracking-tight">{title}</h2>

      <p className="mt-1 text-sm text-black/45">{subtitle}</p>
    </div>
  );
}

function FactCard({ fact }: { fact: Fact }) {
  const confidence = Math.round(fact.confidence * 100);

  return (
    <article className="rounded-2xl border border-black/10 bg-white p-5 transition hover:-translate-y-0.5 hover:shadow-lg">
      <div className="flex items-start justify-between gap-3">
        <div className="text-xs font-semibold uppercase tracking-[0.12em] text-black/40">
          {fact.subject}
        </div>

        <div className="rounded-full bg-black/[0.04] px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wide text-black/50">
          {fact.extraction_method === "llm"
            ? "LLM extracted"
            : fact.extraction_method === "seed"
            ? "Demo fact"
            : fact.extraction_method}
        </div>
      </div>

      <h3 className="mt-4 text-base font-medium">{fact.predicate}</h3>

      <div className="mt-2 text-2xl font-semibold tracking-tight">
        {formatValue(fact)}
      </div>

      {fact.period && (
        <div className="mt-1 text-sm text-black/45">{fact.period}</div>
      )}

      <div className="mt-5 border-t border-black/8 pt-4">
        <div className="flex items-center justify-between text-xs">
          <span
            className={
              fact.evidence.verified
                ? "font-medium text-emerald-700"
                : "font-medium text-amber-700"
            }
          >
            {fact.evidence.verified
              ? "✓ Evidence verified"
              : "⚠ Evidence unverified"}
          </span>

          <span className="text-black/40">{confidence}% confidence</span>
        </div>

        <p className="mt-3 line-clamp-3 text-xs leading-5 text-black/50">
          “{fact.evidence.text}”
        </p>

        <div className="mt-4 text-xs text-black/40">
          {fact.source.filename}
          <span className="mx-1">·</span>
          Page {fact.source.page}
        </div>
      </div>
    </article>
  );
}

function RelationshipCard({ relationship }: { relationship: Relationship }) {
  const type = relationship.relationship_type;

  const isWarning =
    type === "LIKELY_DISAGREEMENT" ||
    type === "CONTRADICTS" ||
    type === "UNRESOLVED";

  return (
    <article className="rounded-2xl border border-black/10 bg-white p-6">
      <div className="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
        <div className="flex items-start gap-4">
          <div
            className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-bold ${
              isWarning
                ? "bg-amber-100 text-amber-800"
                : "bg-emerald-100 text-emerald-800"
            }`}
          >
            {relationshipIcon(type)}
          </div>

          <div>
            <div
              className={`text-xs font-bold uppercase tracking-[0.15em] ${
                isWarning ? "text-amber-700" : "text-emerald-700"
              }`}
            >
              {relationshipLabel(type)}
            </div>

            <div className="mt-1 text-xs text-black/35">
              {Math.round(relationship.confidence * 100)}% confidence
            </div>
          </div>
        </div>
      </div>

      {/* Facts involved */}
      <div className="mt-6 grid gap-3 md:grid-cols-3">
        {relationship.facts.map((fact) => (
          <div key={fact.fact_id} className="rounded-xl bg-[#f6f7f9] p-4">
            <div className="text-[10px] font-semibold uppercase tracking-[0.12em] text-black/35">
              {fact.role}
            </div>

            <div className="mt-2 text-sm font-medium">{fact.predicate}</div>

            <div className="mt-1 text-lg font-semibold">
              {formatValue(fact)}
            </div>

            <div className="mt-1 text-xs text-black/40">{fact.period}</div>
          </div>
        ))}
      </div>

      {/* Explanation */}
      <div className="mt-5 rounded-xl border border-black/8 bg-black/[0.015] p-4">
        <div className="text-[10px] font-semibold uppercase tracking-[0.12em] text-black/35">
          Reasoning
        </div>

        <p className="mt-2 text-sm leading-6 text-black/60">
          {relationship.explanation}
        </p>
      </div>
    </article>
  );
}

function EmptyState({ text }: { text: string }) {
  return (
    <div className="rounded-2xl border border-dashed border-black/15 bg-white p-10 text-center text-sm text-black/40">
      {text}
    </div>
  );
}
