export const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const TOKEN_STORAGE_KEY = "aniai_token";

export function getStoredToken() {
  return localStorage.getItem(TOKEN_STORAGE_KEY) || "";
}

export function setStoredToken(token) {
  localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

export function clearStoredToken() {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
}

export class UnauthorizedError extends Error {
  constructor() {
    super("Unauthorized");
    this.name = "UnauthorizedError";
  }
}

// Wraps fetch with the stored bearer token attached, if any -- public endpoints (discover, anime
// detail, recommend) work fine with no token. Clears the token on a 401 so callers can fall back
// to a logged-out state instead of silently failing every subsequent authenticated request.
export async function apiFetch(path, options = {}) {
  const token = getStoredToken();
  const headers = { ...options.headers };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (res.status === 401) {
    clearStoredToken();
    throw new UnauthorizedError();
  }
  return res;
}

async function _errorDetail(res, fallback) {
  const body = await res.json().catch(() => ({}));
  return body.detail || fallback;
}

// signup/login intentionally use plain fetch, not apiFetch -- they're pre-auth by definition (no
// token to attach), and a wrong-password 401 here is a normal expected error, not a sign the
// caller's session expired, so it must not trip apiFetch's blanket 401 -> clear-token-and-throw.
async function _authFetch(path, email, password) {
  return fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
}

export async function signup(email, password) {
  const res = await _authFetch("/auth/signup", email, password);
  if (!res.ok) throw new Error(await _errorDetail(res, "Signup failed"));
  return res.json();
}

export async function login(email, password) {
  const res = await _authFetch("/auth/login", email, password);
  if (!res.ok) throw new Error(await _errorDetail(res, "Login failed"));
  return res.json();
}

export async function fetchMe() {
  const res = await apiFetch("/auth/me");
  if (!res.ok) throw new UnauthorizedError();
  return res.json();
}

export async function fetchConversations() {
  const res = await apiFetch("/conversations");
  if (!res.ok) throw new Error("Failed to load conversation history");
  return res.json();
}
