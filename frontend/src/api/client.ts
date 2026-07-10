import { API_BASE } from "@/config";
import { useAuthStore } from "@/stores/authStore";
import { ApiError, type ApiErrorBody } from "@/types/api";
import type { TokenResponse } from "@/types/auth";

type RequestOptions = Omit<RequestInit, "body"> & {
  body?: unknown;
  skipAuth?: boolean;
};

let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const { refreshToken, setTokens, clearTokens } = useAuthStore.getState();
  if (!refreshToken) {
    clearTokens();
    return null;
  }

  const response = await fetch(`${API_BASE}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  if (!response.ok) {
    clearTokens();
    return null;
  }

  const data = (await response.json()) as TokenResponse;
  setTokens(data.access_token);
  return data.access_token;
}

async function getValidAccessToken(): Promise<string | null> {
  const { accessToken } = useAuthStore.getState();
  return accessToken;
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { body, skipAuth = false, headers, ...rest } = options;

  const send = async (token: string | null): Promise<Response> => {
    const requestHeaders = new Headers(headers);
    if (body !== undefined) {
      requestHeaders.set("Content-Type", "application/json");
    }
    if (!skipAuth && token) {
      requestHeaders.set("Authorization", `Bearer ${token}`);
    }

    return fetch(`${API_BASE}${path}`, {
      ...rest,
      headers: requestHeaders,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    }).catch(() => {
      throw new Error(
        "Cannot reach the API. Make sure the backend is running on port 8000.",
      );
    });
  };

  let token = skipAuth ? null : await getValidAccessToken();
  let response = await send(token);

  if (response.status === 401 && !skipAuth) {
    if (!refreshPromise) {
      refreshPromise = refreshAccessToken().finally(() => {
        refreshPromise = null;
      });
    }
    token = await refreshPromise;
    if (token) {
      response = await send(token);
    }
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const text = await response.text();
  let data: unknown = null;
  if (text) {
    try {
      data = JSON.parse(text) as unknown;
    } catch {
      throw new Error(
        response.ok
          ? "Received an invalid response from the server."
          : `Request failed (${response.status}). Is the API running on port 8000?`,
      );
    }
  }

  if (!response.ok) {
    if (
      data &&
      typeof data === "object" &&
      "error" in data &&
      typeof (data as ApiErrorBody).error?.message === "string"
    ) {
      throw new ApiError(response.status, data as ApiErrorBody);
    }
    throw new Error(`Request failed (${response.status}).`);
  }

  return data as T;
}
