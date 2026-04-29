/**
 * Typed API client.
 *
 * All requests are routed through Vite's /api proxy (configured in vite.config.ts),
 * which forwards to the FastAPI backend at VITE_API_URL (default: http://localhost:8000).
 *
 * In dev mode the backend runs with AUTH_BYPASS_DEV=true so no bearer token is sent.
 */

import type { DemandRecord, MatchResultsResponse } from "../types/api";

const BASE = "/api";

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { Accept: "application/json" },
  });
  if (!res.ok) {
    throw new Error(`API ${res.status}: ${await res.text()}`);
  }
  return res.json() as Promise<T>;
}

/** Fetch all open demand records. */
export function getDemands(): Promise<DemandRecord[]> {
  return fetchJson<DemandRecord[]>("/demands");
}

/** Fetch paginated match results for a demand. */
export function getMatches(
  demandId: number,
  page = 1
): Promise<MatchResultsResponse> {
  return fetchJson<MatchResultsResponse>(
    `/demands/${demandId}/matches?page=${page}`
  );
}
