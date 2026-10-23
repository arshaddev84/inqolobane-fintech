"use client";

import { useEffect, useState } from "react";
import {
  getCases,
  getDocuments,
  getProfiles,
  getReadiness,
  type CaseRecord,
  type ProfileSnapshot,
  type SourceDocument,
} from "@/lib/api";

type View = "cases" | "profiles" | "documents";

function displayStatus(status: string): string {
  return status.replaceAll("_", " ").toLowerCase();
}

function formatDate(value: string | null): string {
  if (!value) return "Not set";
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? "Not set"
    : new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(date);
}

function shortDate(value: string): string {
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? "Unknown"
    : new Intl.DateTimeFormat("en", { month: "short", day: "numeric" }).format(date);
}

function RequestNotice({ message }: { message: string }) {
  return (
    <div className="request-notice" role="status">
      <span className="notice-mark" aria-hidden="true">!</span>
      <span>{message}</span>
    </div>
  );
}

export default function OperationsWorkbench() {
  const [view, setView] = useState<View>("cases");
  const [searchInput, setSearchInput] = useState("");
  const [search, setSearch] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);
  const [cases, setCases] = useState<CaseRecord[]>([]);
  const [caseTotal, setCaseTotal] = useState(0);
  const [profiles, setProfiles] = useState<ProfileSnapshot[]>([]);
  const [profileTotal, setProfileTotal] = useState(0);
  const [documents, setDocuments] = useState<SourceDocument[]>([]);
  const [documentTotal, setDocumentTotal] = useState(0);
  const [selectedCaseRef, setSelectedCaseRef] = useState("");
  const [selectedDocumentRef, setSelectedDocumentRef] = useState("");
  const [apiReady, setApiReady] = useState<boolean | null>(null);
  const [errors, setErrors] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();

    Promise.allSettled([
      getReadiness(controller.signal),
      getCases(search, controller.signal),
      getProfiles(search, controller.signal),
      getDocuments(search, controller.signal),
    ]).then(([healthResult, casesResult, profilesResult, documentsResult]) => {
      if (controller.signal.aborted) return;

      const nextErrors: string[] = [];
      if (healthResult.status === "fulfilled") {
        setApiReady(healthResult.value.database === "ok");
      } else {
        setApiReady(false);
        nextErrors.push(`API status: ${healthResult.reason.message ?? "Request failed."}`);
      }

      if (casesResult.status === "fulfilled") {
        setCases(casesResult.value.items);
        setCaseTotal(casesResult.value.total);
      } else {
        setCases([]);
        setCaseTotal(0);
        nextErrors.push(`Cases: ${casesResult.reason.message ?? "Request failed."}`);
      }

      if (profilesResult.status === "fulfilled") {
        setProfiles(profilesResult.value.items);
        setProfileTotal(profilesResult.value.total);
      } else {
        setProfiles([]);
        setProfileTotal(0);
        nextErrors.push(`Profiles: ${profilesResult.reason.message ?? "Request failed."}`);
      }

      if (documentsResult.status === "fulfilled") {
        setDocuments(documentsResult.value.items);
        setDocumentTotal(documentsResult.value.total);
      } else {
        setDocuments([]);
        setDocumentTotal(0);
        nextErrors.push(`Documents: ${documentsResult.reason.message ?? "Request failed."}`);
      }

      setErrors(nextErrors);
      setLoading(false);
    });

    return () => controller.abort();
  }, [search, refreshKey]);

  const selectedCase = cases.find((item) => item.complaint_ref === selectedCaseRef) ?? cases[0];
  const selectedDocument =
    documents.find((item) => item.document_ref === selectedDocumentRef) ?? documents[0];
  const attentionCount = profiles.filter((item) => item.sync_status !== "CURRENT").length;

  function submitSearch(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setSearch(searchInput.trim());
    setRefreshKey((key) => key + 1);
  }

  return (
    <main className="workbench-shell">
      <header className="topbar">
        <a className="brand" href="#home" aria-label="Inqolobane home">
          <span className="brand-mark">I</span>
          <span>inqolobane<span className="brand-period">.</span></span>
        </a>
        <span className="workspace-label">OPERATIONS WORKSPACE</span>
        <div className="connection-state" aria-live="polite">
          <span className={`connection-dot ${apiReady ? "is-online" : apiReady === false ? "is-offline" : ""}`} />
          {apiReady === true ? "API connected" : apiReady === false ? "API unavailable" : "Connecting"}
        </div>
      </header>

      <div className="workspace-grid" id="home">
        <aside className="sidebar">
          <div className="sidebar-label">WORKSPACE</div>
          <nav className="primary-nav" aria-label="Workspace views">
            <button className={view === "cases" ? "nav-item active" : "nav-item"} onClick={() => setView("cases")}>
              <span className="nav-glyph" aria-hidden="true">▤</span> Case queue
              <span className="nav-count">{caseTotal}</span>
            </button>
            <button className={view === "profiles" ? "nav-item active" : "nav-item"} onClick={() => setView("profiles")}>
              <span className="nav-glyph" aria-hidden="true">◫</span> Profile review
              {attentionCount > 0 && <span className="nav-count alert-count">{attentionCount}</span>}
            </button>
            <button className={view === "documents" ? "nav-item active" : "nav-item"} onClick={() => setView("documents")}>
              <span className="nav-glyph" aria-hidden="true">▧</span> Source documents
              <span className="nav-count">{documentTotal}</span>
            </button>
          </nav>

          <div className="sidebar-bottom">
            <div className="sidebar-label">DATA SOURCE</div>
            <div className="source-indicator"><span className="connection-dot is-online" /> FastAPI · PostgreSQL</div>
            <div className="sidebar-footnote">Read-only review environment</div>
          </div>
        </aside>

        <section className="main-panel">
          <div className="page-heading">
            <div>
              <div className="eyebrow">CUSTOMER OPERATIONS <span>/</span> {view.toUpperCase()}</div>
              <h1>{view === "cases" ? "Case queue" : view === "profiles" ? "Profile review" : "Source library"}</h1>
              <p className="page-subtitle">
                {view === "cases" && "Review incoming complaints and supporting details."}
                {view === "profiles" && "Compare source-system snapshots for human review."}
                {view === "documents" && "Search the local source documents linked to cases."}
              </p>
            </div>
            <button className="refresh-button" onClick={() => { setLoading(true); setRefreshKey((key) => key + 1); }} disabled={loading}>
              <span aria-hidden="true">↻</span> Refresh
            </button>
          </div>

          <div className="metrics-row" aria-label="Workspace totals">
            <div className="metric"><span className="metric-label">CASES</span><strong>{caseTotal}</strong><span className="metric-note">matching records</span></div>
            <div className="metric"><span className="metric-label">IN REVIEW</span><strong>{attentionCount}</strong><span className="metric-note">profile exceptions</span></div>
            <div className="metric"><span className="metric-label">DOCUMENTS</span><strong>{documentTotal}</strong><span className="metric-note">available sources</span></div>
            <div className="metric metric-health"><span className="metric-label">DATABASE</span><strong className={apiReady ? "health-ok" : "health-waiting"}>{apiReady === null ? "Checking" : apiReady ? "Connected" : "Offline"}</strong><span className="metric-note">readiness endpoint</span></div>
          </div>

          <div className="content-toolbar">
            <div className="view-tabs" role="tablist" aria-label="Operations views">
              {(["cases", "profiles", "documents"] as const).map((tab) => (
                <button key={tab} role="tab" aria-selected={view === tab} className={view === tab ? "view-tab selected" : "view-tab"} onClick={() => setView(tab)}>
                  {tab === "cases" ? "Cases" : tab === "profiles" ? "Profiles" : "Documents"}
                </button>
              ))}
            </div>
            <form className="search-form" onSubmit={submitSearch}>
              <label className="search-box">
                <span className="search-icon" aria-hidden="true">⌕</span>
                <input value={searchInput} onChange={(event) => setSearchInput(event.target.value)} placeholder="Search records or references" aria-label="Search records or references" />
              </label>
              <button className="search-button" type="submit">Search</button>
            </form>
          </div>

          {errors.length > 0 && (
            <div className="notice-stack">
              {errors.map((error) => <RequestNotice key={error} message={error} />)}
            </div>
          )}

          {view === "cases" && (
            <section className="case-workspace" aria-label="Case queue">
              <div className="section-bar"><span>COMPLAINTS</span><span>{loading ? "Loading…" : `${caseTotal} results`}</span></div>
              <div className="case-layout">
                <div className="case-list">
                  {cases.map((item) => (
                    <button key={item.complaint_ref} className={`case-row ${selectedCase?.complaint_ref === item.complaint_ref ? "case-selected" : ""}`} onClick={() => setSelectedCaseRef(item.complaint_ref)}>
                      <span className="case-row-top"><strong>{item.complaint_ref}</strong><span className={`priority priority-${item.priority.toLowerCase()}`}>{item.priority}</span></span>
                      <span className="case-row-summary">{item.customer_summary}</span>
                      <span className="case-row-bottom"><span>{item.category}</span><span>{shortDate(item.opened_at)}</span></span>
                    </button>
                  ))}
                  {!loading && cases.length === 0 && <div className="empty-state">No cases match this search.</div>}
                  {loading && cases.length === 0 && <div className="empty-state">Loading cases from the API…</div>}
                </div>

                {selectedCase ? (
                  <article className="case-detail">
                    <div className="detail-kicker">CASE DETAIL <span>·</span> {selectedCase.complaint_ref}</div>
                    <div className="detail-title-row"><h2>{selectedCase.category}</h2><span className={`status-pill status-${selectedCase.status.toLowerCase()}`}>{displayStatus(selectedCase.status)}</span></div>
                    <p className="case-summary">{selectedCase.customer_summary}</p>
                    <div className="detail-rule" />
                    <div className="detail-grid">
                      <div><span className="detail-label">CUSTOMER REF</span><strong>{selectedCase.customer_ref}</strong></div>
                      <div><span className="detail-label">ACCOUNT REF</span><strong>{selectedCase.account_ref ?? "Not linked"}</strong></div>
                      <div><span className="detail-label">PRODUCT</span><strong>{selectedCase.product_type ?? "Not specified"}</strong></div>
                      <div><span className="detail-label">SUBCATEGORY</span><strong>{selectedCase.subcategory ?? "Not specified"}</strong></div>
                      <div><span className="detail-label">ALLEGATION</span><strong>{displayStatus(selectedCase.allegation_status)}</strong></div>
                      <div><span className="detail-label">OPENED</span><strong>{formatDate(selectedCase.opened_at)}</strong></div>
                      <div><span className="detail-label">TARGET RESOLUTION</span><strong>{formatDate(selectedCase.target_resolution_at)}</strong></div>
                      <div><span className="detail-label">PRIORITY</span><strong>{selectedCase.priority}</strong></div>
                    </div>
                    <div className="detail-footer">Customer-reported information · Human review required</div>
                  </article>
                ) : (
                  <article className="case-detail detail-empty"><span className="empty-mark">—</span><p>Select a case to inspect its details.</p></article>
                )}
              </div>
            </section>
          )}

          {view === "profiles" && (
            <section className="data-section" aria-label="Profile snapshots">
              <div className="section-bar"><span>SOURCE SNAPSHOTS</span><span>{loading ? "Loading…" : `${profileTotal} records`}</span></div>
              <div className="table-wrap">
                <table><thead><tr><th>Customer</th><th>Field</th><th>Observed value</th><th>Source system</th><th>Sync status</th><th>Observed</th></tr></thead>
                  <tbody>{profiles.map((item, index) => <tr key={`${item.customer_ref}-${item.system_name}-${item.field_name}-${index}`}>
                    <td className="table-ref">{item.customer_ref}</td><td>{item.field_name.replaceAll("_", " ")}</td><td className="field-value">{item.field_value ?? "No value"}</td><td>{item.system_name}</td><td><span className={`status-pill status-${item.sync_status.toLowerCase()}`}>{displayStatus(item.sync_status)}</span></td><td>{shortDate(item.observed_at)}</td>
                  </tr>)}</tbody>
                </table>
                {!loading && profiles.length === 0 && <div className="empty-state">No profile snapshots match this search.</div>}
              </div>
            </section>
          )}

          {view === "documents" && (
            <section className="document-workspace" aria-label="Source documents">
              <div className="section-bar"><span>LOCAL SOURCES</span><span>{loading ? "Loading…" : `${documentTotal} documents`}</span></div>
              <div className="document-layout">
                <div className="document-list">
                  {documents.map((document) => <button key={document.document_ref} className={`document-row ${selectedDocument?.document_ref === document.document_ref ? "document-selected" : ""}`} onClick={() => setSelectedDocumentRef(document.document_ref)}>
                    <span className="document-type">SOURCE DOCUMENT</span><strong>{document.title}</strong><span className="document-ref">{document.document_ref}</span>
                  </button>)}
                  {!loading && documents.length === 0 && <div className="empty-state">No documents match this search.</div>}
                </div>
                {selectedDocument ? <article className="document-detail">
                  <div className="detail-kicker">{selectedDocument.filename}</div><h2>{selectedDocument.title}</h2>
                  <div className="related-refs"><span>LINKED REFERENCES</span>{selectedDocument.related_refs.length ? selectedDocument.related_refs.map((ref) => <span className="reference-chip" key={ref}>{ref}</span>) : <span className="muted">No linked references</span>}</div>
                  <pre className="document-content">{selectedDocument.content}</pre>
                </article> : <article className="document-detail detail-empty"><span className="empty-mark">—</span><p>No source document selected.</p></article>}
              </div>
            </section>
          )}

          <footer className="page-footer"><span>Inqolobane Operations</span><span>Read-only workspace <i /> Synthetic records</span></footer>
        </section>
      </div>
    </main>
  );
}