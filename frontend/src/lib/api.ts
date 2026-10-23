export type CaseRecord = {
  complaint_ref: string;
  customer_ref: string;
  account_ref: string | null;
  product_type: string | null;
  category: string;
  subcategory: string | null;
  priority: string;
  status: string;
  allegation_status: string;
  customer_summary: string;
  opened_at: string;
  target_resolution_at: string | null;
};

export type ProfileSnapshot = {
  customer_ref: string;
  system_name: string;
  field_name: string;
  field_value: string | null;
  source_version: string | null;
  last_synced_at: string | null;
  sync_status: string;
  observed_at: string;
};

export type SourceDocument = {
  document_ref: string;
  filename: string;
  title: string;
  related_refs: string[];
  content: string;
};

type ListResponse<T> = {
  items: T[];
  total: number;
};

const API_BASE = (
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1"
).replace(/\/$/, "");

async function request<T>(path: string, signal?: AbortSignal): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, { signal, cache: "no-store" });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") throw error;
    throw new Error("Cannot reach the API. Check that FastAPI is running.");
  }

  if (!response.ok) {
    throw new Error(`API request failed (${response.status} ${response.statusText}).`);
  }
  return response.json() as Promise<T>;
}

function searchQuery(search: string): string {
  const query = new URLSearchParams();
  if (search.trim()) query.set("search", search.trim());
  const serialized = query.toString();
  return serialized ? `?${serialized}` : "";
}

export function getCases(search: string, signal?: AbortSignal) {
  const params = new URLSearchParams(searchQuery(search).slice(1));
  params.set("limit", "100");
  return request<ListResponse<CaseRecord>>(`/cases?${params.toString()}`, signal);
}

export function getProfiles(search: string, signal?: AbortSignal) {
  return request<ListResponse<ProfileSnapshot>>(
    `/profiles/snapshots${searchQuery(search)}`,
    signal,
  );
}

export function getDocuments(search: string, signal?: AbortSignal) {
  return request<ListResponse<SourceDocument>>(
    `/documents${searchQuery(search)}`,
    signal,
  );
}

export function getReadiness(signal?: AbortSignal) {
  return request<{ status: string; database: string }>("/health/ready", signal);
}