import json
import logging
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class OneLineJsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "service": getattr(record, "service", os.getenv("SERVICE_NAME", "gopiai-backend")),
            "env": getattr(record, "env", os.getenv("ENV", "dev")),
            "message": record.getMessage(),
        }
        # Merge extra dict if present
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            payload.update(record.extra)
        # Also merge any known structured fields set via logger.bind-style (if any)
        for key in (
            "event", "request_id", "route", "method", "status_code", "latency_ms",
            "provider", "model", "endpoint", "headers_masked", "params",
            "tool_names", "tool_call_count", "tool_results_summary",
            "provider_latency_ms", "tool_latency_ms", "success", "error_code",
            "error_message", "retry_count", "effective_config_hash", "ui_component",
            "ui_action", "api_url", "api_method", "api_status", "payload_keys",
            "start_ms", "finish_reason", "tool_calls", "tool_name", "tool_args_keys",
        ):
            val = getattr(record, key, None)
            if val is not None:
                payload[key] = val
        # Ensure one-line JSON
        return json.dumps(payload, ensure_ascii=False)


def build_logger(name: str = "gopiai") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO))
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(OneLineJsonFormatter())
        logger.addHandler(handler)
        logger.propagate = False
    return logger


_logger = build_logger()


def mask_headers(headers: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
    if not headers:
        return None
    masked = {}
    for k, v in headers.items():
        lk = k.lower()
        if any(s in lk for s in ("authorization", "api-key", "apikey", "x-api-key", "cookie", "set-cookie", "token")):
            masked[k] = "***"
        else:
            # avoid overly long header values in logs
            masked[k] = v if len(v) <= 512 else (v[:256] + "...(truncated)")
    return masked


def now_ms() -> int:
    return int(time.time() * 1000)


def jlog(level: str = "INFO", **fields: Any) -> None:
    """
    Structured JSON log helper aligned with DeerFlow standard.
    Defaults: service/env/timestamp handled by formatter; request_id encouraged.
    """
    lvl = getattr(logging, level.upper(), logging.INFO)
    # move fields into record's attributes so formatter can merge them
    _logger.log(lvl, fields.get("message", ""), extra=fields)


def ensure_request_id(existing: Optional[str] = None) -> str:
    try:
        if existing and isinstance(existing, str) and existing.strip():
            return existing.strip()
    except Exception:
        pass
    return str(uuid.uuid4())
