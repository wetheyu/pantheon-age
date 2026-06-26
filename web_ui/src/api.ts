import type {
  ApiBootData,
  ActionRequest,
  ActionResponse,
  ClassesResponse,
  GameCreateRequest,
  GameCreateResponse,
  GodsResponse,
  HealthResponse,
  OriginsResponse,
} from "./types";

const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") || DEFAULT_API_BASE_URL;

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`${path} failed with HTTP ${response.status}`);
  }
  return response.json() as Promise<T>;
}

async function postJson<TResponse, TBody>(path: string, body: TBody): Promise<TResponse> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`${path} failed with HTTP ${response.status}: ${detail}`);
  }
  return response.json() as Promise<TResponse>;
}

export async function loadBootData(): Promise<ApiBootData> {
  const [health, classes, gods, origins] = await Promise.all([
    fetchJson<HealthResponse>("/health"),
    fetchJson<ClassesResponse>("/classes"),
    fetchJson<GodsResponse>("/gods"),
    fetchJson<OriginsResponse>("/origins"),
  ]);

  return { health, classes, gods, origins };
}

export async function createWorldGame(request: GameCreateRequest): Promise<GameCreateResponse> {
  return postJson<GameCreateResponse, GameCreateRequest>("/games", request);
}

export async function submitGameAction(
  gameId: string,
  request: ActionRequest,
): Promise<ActionResponse> {
  return postJson<ActionResponse, ActionRequest>(`/games/${gameId}/actions`, request);
}
