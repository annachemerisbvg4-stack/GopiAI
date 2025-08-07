/**
 * DeerFlow UI logger + fetch interceptor for Next.js apps.
 * - Generates X-Request-ID per API call (uuid v4)
 * - Logs ui_action, ui_component, api_url, api_method, api_status, payload_keys, ui_latency_ms, request_id
 * - In dev: logs to console; in prod: optionally POSTs to a backend endpoint (e.g., /logs/ui)
 */

type UILogLevel = "DEBUG" | "INFO" | "WARN" | "ERROR";

export interface UILogEvent {
  timestamp?: string;
  level?: UILogLevel;
  service?: string;
  env?: string;
  event?: string;
  request_id?: string;

  // UI-specific fields
  ui_component?: string;
  ui_action?: string;

  // API call info
  api_url?: string;
  api_method?: string;
  api_status?: number;
  payload_keys?: string[];
  ui_latency_ms?: number;
}

const SERVICE_NAME = "gopiai-ui";
// Avoid relying on Node's "process" types to keep this file portable for browsers/Next.js.
// Safe access to env without referencing 'process' identifier directly (prevents TS error without @types/node).
const _envObj: Record<string, string | undefined> =
  (typeof globalThis !== "undefined" &&
    (globalThis as any).process &&
    (globalThis as any).process.env) ||
  (typeof (globalThis as any) !== "undefined" &&
    (globalThis as any).window &&
    (globalThis as any).window.process &&
    (globalThis as any).window.process.env) ||
  {};
const ENV: string = _envObj.NEXT_PUBLIC_ENV ?? "dev";
const API_URL: string = _envObj.NEXT_PUBLIC_API_URL ?? "";

function isoNow(): string {
  try {
    return new Date().toISOString();
  } catch {
    return "";
  }
}

function uuidv4(): string {
  // RFC4122 v4 (simple implementation sufficient for correlation ID)
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    try {
      return (crypto as any).randomUUID();
    } catch {
      // fall back
    }
  }
  // Fallback
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

function toOneLineJson(event: UILogEvent): string {
  const payload = {
    timestamp: event.timestamp || isoNow(),
    level: event.level || "INFO",
    service: SERVICE_NAME,
    env: ENV,
    event: event.event || "ui_log",
    request_id: event.request_id,
    ui_component: event.ui_component,
    ui_action: event.ui_action,
    api_url: event.api_url,
    api_method: event.api_method,
    api_status: event.api_status,
    payload_keys: event.payload_keys,
    ui_latency_ms: event.ui_latency_ms,
  };
  try {
    return JSON.stringify(payload);
  } catch {
    return `{"level":"INFO","service":"${SERVICE_NAME}","env":"${ENV}","event":"ui_log"}`;
  }
}

export function uiLog(event: UILogEvent): void {
  const line = toOneLineJson(event);
  if (ENV === "dev") {
    // Local console logging in dev
    // eslint-disable-next-line no-console
    console.log(line);
    return;
  }
  // Optional: forward to backend collector in prod (disabled by default)
  // fetch(`${API_URL || ""}/logs/ui`, { method: "POST", headers: {"Content-Type": "application/json"}, body: line }).catch(() => {});
}

/**
 * Wrap fetch to:
 * - inject X-Request-ID
 * - measure latency
 * - log basic request/response info (without sensitive payload data)
 */
export async function loggedFetch(
  input: RequestInfo | URL,
  init?: RequestInit & { ui_component?: string; ui_action?: string }
): Promise<Response> {
  const reqId = uuidv4();
  const start = Date.now();

  const url = typeof input === "string" ? input : (input as URL).toString();
  const method = (init?.method || "GET").toUpperCase();

  // derive payload keys safely
  let payloadKeys: string[] | undefined;
  try {
    if (init?.body && typeof init.body === "string") {
      const parsed = JSON.parse(init.body);
      if (parsed && typeof parsed === "object") {
        payloadKeys = Object.keys(parsed).slice(0, 50);
      }
    }
  } catch {
    payloadKeys = undefined;
  }

  const headers: HeadersInit = {
    ...(init?.headers || {}),
    "X-Request-ID": reqId,
  };

  // request_out for UI will be logged after response; here record "request_in" (UI sending API)
  uiLog({
    level: "INFO",
    event: "ui_request_out",
    request_id: reqId,
    ui_component: init?.ui_component,
    ui_action: init?.ui_action,
    api_url: url,
    api_method: method,
    payload_keys: payloadKeys,
  });

  let resp: Response;
  try {
    resp = await fetch(input, { ...init, headers });
  } catch (e) {
    uiLog({
      level: "ERROR",
      event: "ui_request_error",
      request_id: reqId,
      ui_component: init?.ui_component,
      ui_action: init?.ui_action,
      api_url: url,
      api_method: method,
      ui_latency_ms: Date.now() - start,
    });
    throw e;
  }

  uiLog({
    level: "INFO",
    event: "ui_request_in",
    request_id: reqId,
    ui_component: init?.ui_component,
    ui_action: init?.ui_action,
    api_url: url,
    api_method: method,
    api_status: resp.status,
    ui_latency_ms: Date.now() - start,
  });

  return resp;
}
