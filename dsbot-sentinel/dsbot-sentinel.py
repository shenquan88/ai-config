#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dsbot-sentinel — a read-only health scanner for the DS Bot (dsh) data dir.

Ported, deliberately simplified, from OpenMausBot's Sentinel
(docs/sentinel.md in https://github.com/milind-soni/OpenMausBot):

- every source is opened read-only; the data dir it reads is never modified;
- failures group into issues by a normalized signature: paths, numbers,
  UUIDs, URLs and quoted values are replaced before hashing, so "MEMORY.md
  would have 4085/4000 characters" and "would have 4049/4000" are one issue
  (the same idea as OMB Sentinel's tool-error normalization);
- the issue store keeps references and a short normalized title only —
  never the raw diagnostic text (OMB Sentinel's privacy model);
- issues.jsonl is upserted by signature: count/firstAt/lastAt are updated
  in place, each sighting counted once (occurrence key), evidenceRef points
  back at the source so a person can look the raw line up there;
- the issue store lives OUTSIDE the data dir (XDG state home); the only
  file written inside the team workspace is SENTINEL.md — the daily brief
  the bots and the owner read.

Usage:
  dsbot-sentinel.py [--quiet] [--json] [--lookback-minutes N]
      [--home /home/dsh/.dsh/bot] [--workspace /home/dsh/.dsh/bot/workspace]
      [--out ~/.local/state/dsbot-sentinel]

Exit codes (in the spirit of OMB's CLI): 0 ok, 2 usage error, 1 scan error.
"""

import argparse
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

TITLE_CAP = 160
LOOKBACK_DEFAULT = 360  # minutes: trailing window reread from diagnostics.jsonl
DATA_DIR_NAME = "bot"

UUID_RE = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")
HEXID_RE = re.compile(r"\b[0-9a-f]{12,}\b")
URL_RE = re.compile(r"https?://\S+")
QUOTED_RE = re.compile(r"[\"“”'`][^\"“”'`]{4,}[\"“”]")
PATH_RE = re.compile(r"(?:/[A-Za-z0-9_.@\-+]+)+")


def normalize(text: str) -> str:
    t = URL_RE.sub("<url>", text)
    t = UUID_RE.sub("<id>", t)
    t = HEXID_RE.sub("<id>", t)
    t = QUOTED_RE.sub("<q>", t)
    t = PATH_RE.sub("<path>", t)
    t = re.sub(r"\d+(?:\.\d+)?", "<n>", t)
    t = re.sub(r"\s+", " ", t).strip().lower()
    if len(t) > TITLE_CAP:
        t = t[: TITLE_CAP - 1] + "…"
    return t


def sig_of(kind: str, norm: str) -> str:
    return f"{kind}:{hashlib.sha256(norm.encode()).hexdigest()[:16]}"


class Scan:
    def __init__(self, home: Path, out_dir: Path, workspace: Path, lookback_min: int):
        self.home = home
        self.out_dir = out_dir
        self.workspace = workspace
        self.lookback_min = lookback_min
        self.new_issues: dict[str, dict] = {}
        self.seen: set[str] = set()
        self.notes: list[str] = []
        self.usage = None
        self.machine = {}

    def add_issue(self, kind, origin, title, source, source_id, at_ms, severity):
        if not title:
            return
        sig = sig_of(kind, title)
        entry = self.new_issues.setdefault(
            sig,
            {
                "sig": sig,
                "kind": kind,
                "title": title,
                "origin": origin,
                "severity": severity,
                "tool": None,
                "firstAt": at_ms,
                "lastAt": at_ms,
                "count": 0,
                "evidenceRef": {"source": source, "id": str(source_id)},
            },
        )
        occ = f"{sig}|{at_ms // 30000}"
        if occ not in self.seen:
            self.seen.add(occ)
            entry["count"] += 1
            entry["lastAt"] = max(entry["lastAt"], at_ms)

    # ---------------- sources ----------------

    def read_diagnostics(self):
        log = self.home / "logs" / "diagnostics.jsonl"
        if not log.exists():
            self.notes.append("diagnostics.jsonl not found; skipped")
            return
        cutoff = (time.time() - self.lookback_min * 60) * 1000
        size = log.stat().st_size
        with log.open("rb") as f:
            f.seek(max(0, size - 1_500_000))
            buf = f.read().decode("utf-8", "replace")
        for line in buf.splitlines():
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            at = int(rec.get("time", 0)) or 0
            if at < cutoff or at > time.time() * 1000 + 5000:
                continue
            level = str(rec.get("level", "warn"))
            if level not in ("warn", "error"):
                continue
            text = str(rec.get("text", "")).strip()
            if not text:
                continue
            self.add_issue(
                kind=f"diag_{level}",
                origin="ds-bot",
                title=normalize(text.splitlines()[0]),
                source="diagnostics",
                source_id=f"at={at}",
                at_ms=at,
                severity="high" if level == "error" else "medium",
            )

    def read_usage(self):
        db = self.home / "usage.sqlite"
        if not db.exists():
            self.notes.append("usage.sqlite not found; skipped")
            return
        try:
            con = sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=2)
            con.execute("PRAGMA query_only=1")
            try:
                cutoff = time.time() * 1000 - 86400 * 1000
                bots: list[str] = []
                for (n,) in con.execute("SELECT name FROM owners"):
                    if n and n not in bots:
                        bots.append(n)
                calls24h, tin, tout = con.execute(
                    "SELECT COUNT(*), COALESCE(SUM(input),0), COALESCE(SUM(output),0) FROM calls WHERE time>?",
                    (cutoff,),
                ).fetchone()
                by_model = con.execute(
                    "SELECT model, COUNT(*) FROM calls WHERE time>? GROUP BY model ORDER BY 2 DESC LIMIT 8",
                    (cutoff,),
                ).fetchall()
            finally:
                con.close()
        except Exception as exc:
            self.notes.append(f"usage.sqlite unreadable: {exc}")
            return
        self.usage = {
            "calls24h": calls24h,
            "tokensIn24h": int(tin),
            "tokensOut24h": int(tout),
            "bots": bots,
            "byModel": [{"model": m, "calls": c} for m, c in by_model],
        }

    def machine_health(self):
        # The server's own heartbeat (state.lock, bumped as a live check by the
        # dsh holding the team lock) is the trustworthy liveness signal; the
        # process shows up as "node /usr/bin/dsh", so a name match would false-
        # alarm. A stale heartbeat of 3+ minutes means nobody is refreshing it.
        st = os.statvfs("/")
        self.machine["diskFreeGB"] = round((st.f_bavail * st.f_frsize) / 2**30, 1)
        if self.machine["diskFreeGB"] < 5:
            self.add_issue(
                "health_disk", "machine", "磁盘剩余不足 5 GB",
                "statvfs", f"free={self.machine['diskFreeGB']}GB", int(time.time() * 1000), "high",
            )
        lock = self.home / "state.lock"
        if lock.exists():
            age = round((time.time() - lock.stat().st_mtime) / 60, 1)
            self.machine["stateLockHeartbeatAgeMin"] = age
            if age > 3:
                self.add_issue(
                    "health_lock", "machine", "state.lock 心跳超过 3 分钟未更新",
                    "state.lock", f"age={age}min", int(time.time() * 1000), "high",
                )

    # ------------- issue store -------------

    def store_write(self):
        path = self.out_dir / "issues.jsonl"
        kept = []
        for line in path.read_text(encoding="utf-8").splitlines() if path.exists() else []:
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                kept.append(json.loads(line))
            except Exception:
                continue
        old = {rec["sig"]: rec for rec in kept}
        merged: list[dict] = []
        for sig, fresh in self.new_issues.items():
            popped = old.pop(sig, None)
            if popped:
                merged.append({**popped,
                               "count": fresh["count"],
                               "firstAt": max(popped["firstAt"], fresh["firstAt"]),
                               "lastAt": fresh["lastAt"],
                               "evidenceRef": fresh["evidenceRef"]})
            else:
                merged.append(fresh)
        merged.extend(rec for rec in old.values())  # not re-sighted: keep history
        rank = {"high": 0, "medium": 1, "low": 2}
        merged.sort(key=lambda r: (rank.get(r["severity"], 2), -r["count"], -r["lastAt"]))
        tmp = path.with_suffix(".jsonl.tmp")
        tmp.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in merged), encoding="utf-8")
        os.replace(tmp, path)
        os.chmod(path, 0o600)
        self.notes.append(f"issues.jsonl upserted: {len(merged)} issue(s), {len(self.new_issues)} seen this scan")

    def store_read(self):
        path = self.out_dir / "issues.jsonl"
        issues = []
        for line in path.read_text(encoding="utf-8").splitlines() if path.exists() else []:
            if line.strip().startswith("{"):
                try:
                    issues.append(json.loads(line))
                except Exception:
                    pass
        return issues

    # ------------- brief -------------

    def write_brief(self, issues):
        now_ms = time.time() * 1000
        findings = [i for i in issues if i["lastAt"] > now_ms - 6 * 3600 * 1000]
        rank = {"high": 0, "medium": 1, "low": 2}
        findings.sort(key=lambda r: (rank.get(r["severity"], 2), -r["count"]))

        def stamp(ms):
            return time.strftime("%-m-%d %H:%M", time.localtime(ms / 1000))

        lines = [
            "# 状态简报（dsbot-sentinel）",
            "",
            f"生成时间 {time.strftime('%F %T %z')}。本文件由定时任务整篇覆盖；"
            "只写次数与概况，不含会话内容、密钥或用户信息。问题明细在 "
            f"~/.local/state/dsbot-sentinel/issues.jsonl。",
            "",
            "## 近 6 小时的问题",
        ]
        if findings:
            for i in findings:
                lines.append(
                    f"- [{i['severity']}] {i['title']}（近 {i['count']} 次，最近 {stamp(i['lastAt'])}，"
                    f"来源 {i['evidenceRef']['source']}）"
                )
        else:
            lines.append("- 无新问题。")
        lines += ["", "## 24 小时用量（只计次数）"]
        if self.usage:
            bots = "、".join(self.usage["bots"][:14]) or "—"
            models = "、".join(f"{m['model']}×{m['calls']}" for m in self.usage["byModel"][:6]) or "—"
            lines += [
                f"- 模型调用 {self.usage['calls24h']} 次；输入 {self.usage['tokensIn24h']:,}，"
                f"输出 {self.usage['tokensOut24h']:,} tokens。",
                f"- 成员：{bots}",
                f"- 按模型：{models}",
            ]
        else:
            lines.append("- 用量数据暂不可读。")
        m = self.machine
        lock = m.get("stateLockHeartbeatAgeMin")
        machine_line = f"磁盘剩余 {m.get('diskFreeGB', '?')} GB"
        if lock is not None:
            machine_line += f"；state.lock 心跳 {lock} 分钟前"
        lines += ["", "## 机器", f"- {machine_line}"]
        lines += [
            "",
            "原始记录回看：",
            f"- 原始日志 ~/.dsh/bot/logs/diagnostics.jsonl（最近 {self.lookback_min} 分钟窗口）",
            "- 结构化问题表 ~/.local/state/dsbot-sentinel/issues.jsonl",
        ]
        tmp = self.workspace / ".SENTINEL.md.tmp"
        tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
        os.replace(tmp, self.workspace / "SENTINEL.md")


def refuse_out_inside_data(out: Path, home: Path):
    inside = out == home or str(out).startswith(str(home) + os.sep) or out.name == DATA_DIR_NAME
    if inside:
        raise ValueError(f"--out {out} 位于 ds-bot 数据目录内，拒绝写入（隐私模型）；请放在数据目录外")


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--lookback-minutes", type=int, default=LOOKBACK_DEFAULT)
    ap.add_argument("--home", default=os.environ.get("DSH_BOT_HOME", "/home/dsh/.dsh/bot"))
    ap.add_argument("--workspace", default="/home/dsh/.dsh/bot/workspace")
    ap.add_argument("--out", default=os.environ.get(
        "DSBSENTINEL_OUT",
        os.path.join(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local/state")), "dsbot-sentinel"),
    ))
    args = ap.parse_args()
    out_dir, home, workspace = Path(args.out).expanduser(), Path(args.home).expanduser(), Path(args.workspace).expanduser()
    state = None
    try:
        if args.lookback_minutes < 0:
            raise ValueError("--lookback-minutes 不能为负")
        refuse_out_inside_data(out_dir, home)
    except ValueError as exc:
        print(f"usage error: {exc}", file=sys.stderr)
        return 2
    scan = Scan(home, out_dir, workspace, int(args.lookback_minutes))
    ok = False
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        scan.read_diagnostics()
        scan.read_usage()
        scan.machine_health()
        scan.store_write()
        scan.write_brief(scan.store_read())
        ok = True
    except Exception as exc:
        scan.notes.append(f"scan error: {type(exc).__name__}: {exc}")
    summary = {
        "ok": ok,
        "sighted": len(scan.new_issues),
        "usage": scan.usage,
        "machine": scan.machine,
        "notes": scan.notes,
        "out": str(out_dir / "issues.jsonl"),
        "brief": str(workspace / "SENTINEL.md"),
    }
    if args.json:
        print(json.dumps(summary, ensure_ascii=False))
    elif not args.quiet:
        print(f"dsbot-sentinel: {'ok' if ok else 'FAILED'}; {summary['brief']}")
        for n in scan.notes:
            print(f"  - {n}")
    if not ok:
        print("\n".join(scan.notes), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
