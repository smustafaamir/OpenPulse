import { apiRequest } from "@/api/client";
import type {
  LoginRequest,
  RefreshRequest,
  RegisterRequest,
  TokenResponse,
} from "@/types/auth";

export function register(data: RegisterRequest): Promise<TokenResponse> {
  return apiRequest<TokenResponse>("/auth/register", {
    method: "POST",
    body: data,
    skipAuth: true,
  });
}

export function login(data: LoginRequest): Promise<TokenResponse> {
  return apiRequest<TokenResponse>("/auth/login", {
    method: "POST",
    body: data,
    skipAuth: true,
  });
}

export function refresh(data: RefreshRequest): Promise<TokenResponse> {
  return apiRequest<TokenResponse>("/auth/refresh", {
    method: "POST",
    body: data,
    skipAuth: true,
  });
}
