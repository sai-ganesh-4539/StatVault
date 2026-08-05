const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchAPI<T>(path: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json", ...opts?.headers },
    ...opts,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

// Typed API calls
export const getHealth = () => fetchAPI<any>("/health");

export const predictMatch = (data: any) =>
  fetchAPI<any>("/predict/match", { method: "POST", body: JSON.stringify(data) });

export const predictMarketValue = (data: any) =>
  fetchAPI<any>("/predict/market-value", { method: "POST", body: JSON.stringify(data) });

export const scoutAnomaly = (data: any) =>
  fetchAPI<any>("/scout/anomaly", { method: "POST", body: JSON.stringify(data) });

export const getClusters = () => fetchAPI<any>("/scout/clusters");

export const askQuestion = (question: string) =>
  fetchAPI<any>("/ask", { method: "POST", body: JSON.stringify({ question }) });

export const getLiveScores = () => fetchAPI<any>("/matches/live");

export const getFixtures = (comp = "PL") =>
  fetchAPI<any>(`/matches/fixtures?competition=${comp}`);

export const getStandings = (comp = "PL") =>
  fetchAPI<any>(`/matches/standings?competition=${comp}`);

export const getScorers = (comp = "PL") =>
  fetchAPI<any>(`/matches/scorers?competition=${comp}`);