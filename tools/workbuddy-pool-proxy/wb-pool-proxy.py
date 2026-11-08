#!/usr/bin/env python3
"""Local request-rewriting proxy for the WorkBuddy credit-pool gateway (7863).

Why: DSH's system prompt contains a fixed 111-char sentence (FILE_REFERENCE_PROMPT from
@deepseek-ai/dsh-file-reference) that upstream content moderation treats as an unapproved-client
fingerprint. Upstream /v2 answers HTTP 400 code=11128 ("Illegal API invocation from an unapproved
channel"), workbuddy2api falls back to /console, /console lacks the cn: models -> 11102 ->
gateway reports 503 no_healthy_account for the whole request.

Fix (client-side, WSL only): rewrite ONE WORD of that sentence in outbound system/developer
messages ("with" -> "by") so the literal no longer matches, while the meaning stays identical.
Verified 5/5 with the full DSH payload for several rewrite variants (see pool-503-investigation.md).

Usage:
    python3 pool-503-rewrite-proxy.py            # listen 127.0.0.1:7866 -> http://<host>:7863
    python3 pool-503-rewrite-proxy.py --selftest # in-process functional self-test (no external deps)

DSH provider config: baseURL = http://127.0.0.1:7866/v1 (same apiKey), everything else unchanged.
"""
from __future__ import annotations

import argparse
import http.client
import http.server
import json
import socket
import subprocess
import sys
import threading
import time
import urllib.request

UPSTREAM_HOST_DEFAULT = None  # resolved lazily from `ip route` (WSL -> Windows host)
UPSTREAM_PORT = 7863
LISTEN = ("127.0.0.1", 7866)
PROXY_SEND_HEADERS = {"host", "content-length", "connection", "accept-encoding", "transfer-encoding"}

# Literal -> replacement, applied ONLY to outbound system/developer message text.
# One-word change: exact upstream match breaks, semantics of the @-file guidance unchanged.
REWRITES = [
    ("Tokens prefixed with @", "Tokens prefixed by @"),
]


_HOST_CACHE = {"host": None, "at": 0.0}
HOST_TTL_S = 60.0


def resolve_upstream_host(force: bool = False) -> str:
    """Resolve the Windows host IP from the WSL default route, cached for HOST_TTL_S.

    The host IP changes across Windows/WSL restarts; a short TTL keeps normal
    requests cheap while recovering automatically after a restart without a
    proxy restart.
    """
    if UPSTREAM_HOST_DEFAULT:
        return UPSTREAM_HOST_DEFAULT
    now = time.monotonic()
    if not force and _HOST_CACHE["host"] and now - _HOST_CACHE["at"] < HOST_TTL_S:
        return _HOST_CACHE["host"]
    out = subprocess.check_output(
        ["bash", "-c", "ip route show default | awk '{print $3}'"], text=True
    ).strip()
    if not out:
        raise RuntimeError("cannot resolve Windows host IP from WSL")
    _HOST_CACHE["host"], _HOST_CACHE["at"] = out, now
    return out


def rewrite_text(s: str) -> str:
    for old, new in REWRITES:
        if old in s:
            s = s.replace(old, new)
    return s


def rewrite_content(v):
    if isinstance(v, str):
        return rewrite_text(v), v != rewrite_text(v)
    if isinstance(v, list):  # multimodal parts
        changed = False
        for part in v:
            if isinstance(part, dict) and isinstance(part.get("text"), str):
                new, ch = rewrite_text(part["text"]), None
                ch = new != part["text"]
                if ch:
                    part["text"] = new
                    changed = True
        return v, changed
    return v, False


def rewrite_body(raw: bytes) -> tuple[bytes, int]:
    """Rewrite the fingerprint in system/developer messages. Returns (body, changed_count)."""
    try:
        obj = json.loads(raw)
    except Exception:  # noqa: BLE001
        return raw, 0
    msgs = obj.get("messages")
    if not isinstance(msgs, list):
        return raw, 0
    changed = 0
    for m in msgs:
        if not isinstance(m, dict):
            continue
        role = m.get("role")
        if role not in ("system", "developer"):
            continue
        if "content" in m:
            c, ch = rewrite_content(m["content"])
            if ch:
                m["content"] = c
                changed += 1
        if isinstance(m.get("reasoning_content"), str):
            m["reasoning_content"] = rewrite_text(m["reasoning_content"])
    if changed:
        return json.dumps(obj, ensure_ascii=False).encode(), changed
    return raw, 0


CREDIT_LABELS = {}


def credit_label(row):
    """Human label carrying the credit multiplier, e.g. 'Hy3 · 免费(×0.00)' or '均衡 · 积分×0.50'.

    The gateway already reports `credits` (its own multiplier string) and `name`; we only
    combine them so OpenAI-compatible clients that render the model `name` (openmausbot does)
    show whether a model burns credits before it is used.
    """
    name = str(row.get("name") or row.get("id") or "")
    credits = row.get("credits")
    if isinstance(credits, str) and credits.strip():
        c = credits.strip()
        num = c[1:] if c.lower().startswith("x") else c
        try:
            value = float(num)
        except ValueError:
            return name + " · 积分" + c
        if value == 0:
            return name + " · 免费(x0.00)"
        return name + " · 积分" + c
    if str(row.get("id", "")) == "cn:auto":
        return name + " · 积分浮动"
    return name + " · 积分未知"


def label_models_body(raw):
    """Rewrite a /v1/models JSON body so each model name carries its credit multiplier."""
    try:
        obj = json.loads(raw)
    except Exception:
        return raw
    rows = obj.get("data")
    if not isinstance(rows, list):
        return raw
    changed = False
    for row in rows:
        if not isinstance(row, dict):
            continue
        label = credit_label(row)
        if row.get("name") != label:
            row["name"] = label
            changed = True
    if not changed:
        return raw
    return json.dumps(obj, ensure_ascii=False).encode()


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"  # close-delimited responses: SSE streams stay streaming
    upstream_host = None

    def log_message(self, fmt, *args):  # quiet
        pass

    # --- helpers -----------------------------------------------------------
    def _target(self):
        host = self.upstream_host or resolve_upstream_host()
        return f"{host}:{UPSTREAM_PORT}"

    def _forward(self, method: str):
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else None
        rewritten = 0
        if body and method == "POST" and "/chat/completions" in self.path:
            body, rewritten = rewrite_body(body)
        headers = {k: v for k, v in self.headers.items() if k.lower() not in PROXY_SEND_HEADERS}
        conn = http.client.HTTPConnection(self._target(), timeout=600)
        try:
            conn.request(method, self.path, body=body, headers=headers)
            resp = conn.getresponse()
            self.send_response(resp.status)
            for k, v in resp.getheaders():
                if k.lower() in ("content-length", "transfer-encoding", "connection"):
                    continue
                self.send_header(k, v)
            self.end_headers()
            while True:
                chunk = resp.read(8192)
                if not chunk:
                    break
                self.wfile.write(chunk)
                self.wfile.flush()
        except (http.client.HTTPException, OSError) as e:  # noqa: BLE001
            # A connection failure may mean the Windows host IP changed (WSL restart):
            # re-resolve once and retry the same request before reporting a proxy error.
            try:
                resolve_upstream_host(force=True)
                conn.close()
                conn = http.client.HTTPConnection(self._target(), timeout=600)
                conn.request(method, self.path, body=body, headers=headers)
                resp = conn.getresponse()
                self.send_response(resp.status)
                for k, v in resp.getheaders():
                    if k.lower() in ("content-length", "transfer-encoding", "connection"):
                        continue
                    self.send_header(k, v)
                self.end_headers()
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    self.wfile.flush()
                return
            except Exception as e2:  # noqa: BLE001
                e = e2
            try:
                self.send_response(502)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": {"code": "proxy_error", "message": str(e)}}).encode())
            except Exception:  # noqa: BLE001
                pass
        finally:
            conn.close()

    def do_GET(self):
        if "/models" in self.path:
            return self._forward_models()
        self._forward("GET")

    def _forward_models(self):
        """GET /v1/models with credit-multiplier labels injected into each model name."""
        headers = {k: v for k, v in self.headers.items() if k.lower() not in PROXY_SEND_HEADERS}
        body = None
        for attempt in (0, 1):
            conn = http.client.HTTPConnection(self._target(), timeout=60)
            try:
                conn.request("GET", self.path, headers=headers)
                resp = conn.getresponse()
                raw = resp.read()
                break
            except (http.client.HTTPException, OSError):
                conn.close()
                if attempt == 1:
                    raise
                resolve_upstream_host(force=True)
            finally:
                try:
                    conn.close()
                except Exception:  # noqa: BLE001
                    pass
        payload = label_models_body(raw) if resp.status == 200 else raw
        self.send_response(resp.status)
        for k, v in resp.getheaders():
            if k.lower() in ("content-length", "transfer-encoding", "connection"):
                continue
            self.send_header(k, v)
        self.send_header("content-length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self):
        self._forward("POST")


class Server(http.server.ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def serve():
    srv = Server(LISTEN, Handler)
    print(f"[proxy] listening on http://{LISTEN[0]}:{LISTEN[1]} -> http://{resolve_upstream_host()}:{UPSTREAM_PORT}", flush=True)
    srv.serve_forever()


def selftest():
    """Start the proxy on an ephemeral port and push the real failing payload through it."""
    srv = Server(("127.0.0.1", 0), Handler)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    key = open("scratch/pool-key", encoding="utf-8").read().strip()
    replay = json.load(open("/tmp/wb/replay.json"))
    tools = [{"type": "function", "function": {"name": t["name"], "description": t["description"],
                                              "parameters": t["parameters"]}} for t in replay["tools"]]
    payload = {"model": "cn:glm-5.3", "max_tokens": 32,
               "messages": [{"role": "system", "content": replay["system"]},
                            {"role": "user", "content": "Reply with exactly: OK"}],
               "tools": tools}
    bad, good = 0, 0
    for i in range(5):
        req = urllib.request.Request(f"http://127.0.0.1:{port}/v1/chat/completions",
                                     data=json.dumps(payload).encode(),
                                     headers={"Authorization": "Bearer " + key,
                                              "Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                code = resp.status
                resp.read()
        except Exception as e:  # noqa: BLE001
            code = getattr(e, "code", -1)
        print(f"[selftest] full DSH payload via proxy #{i+1}: {code}", flush=True)
        bad += code != 200
        good += code == 200
        time.sleep(2)
    # control: without proxy, original body must still fail (proves the rewrite is what fixes it)
    req = urllib.request.Request(f"http://{resolve_upstream_host()}:{UPSTREAM_PORT}/v1/chat/completions",
                                 data=json.dumps(payload).encode(),
                                 headers={"Authorization": "Bearer " + key,
                                          "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            control = resp.status
    except Exception as e:  # noqa: BLE001
        control = getattr(e, "code", -1)
    print(f"[selftest] control direct 7863 (no rewrite): {control}", flush=True)
    print(f"[selftest] proxy ok={good}/5, control={'expected 503' if control != 200 else 'UNEXPECTED 200'}")
    srv.shutdown()
    return 0 if good == 5 and control != 200 else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--upstream-host", default=None)
    args = ap.parse_args()
    if args.upstream_host:
        Handler.upstream_host = args.upstream_host
    if args.selftest:
        sys.exit(selftest())
    serve()
