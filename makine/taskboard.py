"""MAKİNE's unattended, bounded, deterministic task board and issue notifier.

Only posts to MAKİNE issue #1, and only on meaningful task state changes.
No dispatch to external repo, coding agent, trading endpoint, or LLM.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import pathlib
import urllib.error
import urllib.request

from .cli import write_json
from .source import stamp, utcnow

ROOT = pathlib.Path(__file__).resolve().parents[1]
TASKBOARD = ROOT / "site/data/task-board.json"
MASTER_ISSUE = "https://github.com/onurqlp/makine-core/issues/1"
POST_URL = "https://api.github.com/repos/onurqlp/makine-core/issues/1/comments"
ALLOWED_REPO = "onurqlp/makine-core"
SUPPORTED_STATES = {"FRESH", "PARTIAL", "STALE", "UNAVAILABLE", "INVALID", "INVALID_TIME"}
TASK_DEFINITIONS = {
    "COIN_SOURCE_FRESHNESS": {
        "owner": "COIN.LIVE", "severity": "HIGH",
        "title": "COIN.LIVE kaynak tazeliği / bütünlüğü kontrolü",
        "next_step": "Kaynağın gerçek zaman damgasını, health ve manifest bütünlüğünü kendi deposunda incele.",
    },
    "ALTI_SOURCE_FRESHNESS": {
        "owner": "ALTI", "severity": "HIGH",
        "title": "ALTI verisi zamanında yenilenmiyor",
        "next_step": "ALTI Actions cron/success loglarını ve son gerçek piyasa kaydı zamanını kontrol et.",
    },
    "ALTI_PROVIDER_ACCESS": {
        "owner": "ALTI", "severity": "MEDIUM",
        "title": "ALTI sağlayıcı erişimi kısmen başarısız",
        "next_step": "Sağlayıcı hata durumlarını ve alternatif kamuya açık veri erişimini araştır; işlem yapma.",
    },
    "ALTI_SOURCE_QUALITY": {
        "owner": "ALTI", "severity": "MEDIUM",
        "title": "ALTI kaynak verisi kısmi, veri kalitesini incele",
        "next_step": "Kısmi verinin gerçek gerekçesini kontrol et; kaynaktaki eksikleri tamamlanmış gibi işaretleme.",
    },
}


def _issue_codes(snapshot):
    result = []
    coin = (snapshot.get("sources") or {}).get("coinlive") or {}
    alti = (snapshot.get("sources") or {}).get("alti") or {}
    if coin.get("state") != "FRESH":
        result.append("COIN_SOURCE_FRESHNESS")
    if alti.get("state") in ("STALE", "UNAVAILABLE", "INVALID", "INVALID_TIME", None):
        result.append("ALTI_SOURCE_FRESHNESS")
    if alti.get("state") == "PARTIAL" and "PARTIAL_PROVIDER_ACCESS" not in (alti.get("warnings") or []):
        result.append("ALTI_SOURCE_QUALITY")
    if "PARTIAL_PROVIDER_ACCESS" in (alti.get("warnings") or []):
        result.append("ALTI_PROVIDER_ACCESS")
    return sorted(result)


def _safe_source_evidence(snapshot, code):
    src = (snapshot.get("sources") or {}).get(
        "coinlive" if code.startswith("COIN_") else "alti"
    ) or {}
    state = src.get("state")
    if state not in SUPPORTED_STATES:
        state = "UNAVAILABLE"
    # Only allow verified literals into public notifications; raw source text
    # is deliberately excluded, since sources are outside this repository.
    return {
        "source_repo": ("onurqlp/coin-live-pro" if code.startswith("COIN_")
                        else "onurqlp/alti-quant-lab"),
        "source_state": state,
        "observed_at_utc": src.get("observed_at_utc")
        if isinstance(src.get("observed_at_utc"), str) else None,
        "scan_id": src.get("scan_id") if isinstance(src.get("scan_id"), str) else None,
    }


def build_board(snapshot, previous=None, now=None):
    """Preserve open tasks and resolved history; alert only on state transitions."""
    now = now or utcnow()
    previous = previous or {}
    active_before = {x.get("id"): x for x in previous.get("active", [])
                     if isinstance(x, dict) and x.get("id") in TASK_DEFINITIONS}
    codes = _issue_codes(snapshot)
    active = []
    for code in codes:
        spec = TASK_DEFINITIONS[code]
        past = active_before.get(code) or {}
        active.append({
            "id": code, "owner": spec["owner"], "severity": spec["severity"],
            "title": spec["title"], "next_step": spec["next_step"],
            "status": "RESEARCH_REQUIRED", "approval_required": True,
            "source": _safe_source_evidence(snapshot, code),
            "first_seen_utc": past.get("first_seen_utc") or stamp(now),
            "last_seen_utc": stamp(now),
            "issue": MASTER_ISSUE,
            "autonomous_code_execution": False,
        })
    before_codes = set(active_before)
    after_codes = set(codes)
    started = sorted(after_codes - before_codes)
    resolved = sorted(before_codes - after_codes)
    resolved_events = list(previous.get("resolved_recent") or [])[-29:]
    for code in resolved:
        resolved_events.append({"id": code, "resolved_at_utc": stamp(now)})
    signature = hashlib.sha256("|".join(codes).encode("ascii")).hexdigest()[:16]
    old_notified = previous.get("last_notified_signature")
    changed = bool(started or resolved) or not previous.get("schema")
    return {
        "schema": "makine-task-board-v1", "generated_at_utc": stamp(now),
        "from_coordination_utc": snapshot.get("generated_at_utc"),
        "status": "ATTENTION_REQUIRED" if active else "CLEAR",
        "active": active, "resolved_recent": resolved_events[-30:],
        "transition": {"started": started, "resolved": resolved,
                       "changed": changed, "signature": signature},
        "last_notified_signature": old_notified,
        "issue_delivery": {"state": "NOT_ATTEMPTED"},
        "notification_required": signature != old_notified,
        "master_issue": MASTER_ISSUE,
        "automation": {
            "issue_updates": "ON_TRANSITIONS_ONLY",
            "cross_repository_writes": False,
            "auto_assign_coding_agent": False,
            "allow_trading": False,
            "allow_releases": False,
            "ai_proposals_not_executable": True,
        },
    }


def _comment(board):
    trans = board["transition"]
    lines = [
        "<!-- MAKINE-READONLY-COORDINATION: " + trans["signature"] + " -->",
        "## MAKİNE otomatik durum değişikliği",
        "Kaynak kontrol zamanı: " + board["generated_at_utc"],
        "",
        "Bu yorum bir **otomatik araştırma görev devridir**, çalışan ChatGPT/Codex ajanı kanıtı değildir.",
        "Diğer GitHub depolarının koduna, sinyaline veya kasasına dokunulmadı.",
        "",
    ]
    if trans["started"]:
        lines.append("**Yeni/açık problemler:**")
        for code in trans["started"]:
            spec = TASK_DEFINITIONS[code]
            lines.append("- **" + spec["owner"] + "**: " + spec["title"]
                         + " (kod " + code + ").")
    if trans["resolved"]:
        lines.append("**Kaynak durumuna göre düzelen problemler:** "
                     + ", ".join(trans["resolved"]))
    lines.extend(["", "**Şu an takip edilen görevler:** " +
                  (", ".join(x["id"] for x in board["active"]) or "yok"),
                  "Rapor: [MAKİNE görev listesi](https://github.com/onurqlp/makine-core/blob/main/site/data/task-board.json)",
                  "Bunlar öneri/inceleme kayıtlarıdır. Sürüm veya işlem yetkisi verilmez."])
    return "\n".join(lines)


def post_update(board, token, *, sender=None):
    if not board["notification_required"]:
        board["issue_delivery"] = {"state": "UNCHANGED", "posted": False}
        board["notification_required"] = False
        return board
    if not token:
        board["issue_delivery"] = {"state": "TOKEN_UNAVAILABLE", "posted": False}
        return board
    # GitHub's per-repository GITHUB_TOKEN is only allowed to write the hub repo.
    if os.getenv("GITHUB_REPOSITORY", ALLOWED_REPO) != ALLOWED_REPO:
        board["issue_delivery"] = {"state": "REPO_SCOPE_REJECTED", "posted": False}
        return board
    payload = {"body": _comment(board)}
    if sender is None:
        def sender(body):
            request = urllib.request.Request(
                POST_URL, json.dumps(body).encode("utf-8"),
                headers={"Authorization": "Bearer " + token,
                         "Accept": "application/vnd.github+json",
                         "Content-Type": "application/json",
                         "User-Agent": "MakineTaskBoard/1.0"},
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=20) as response:
                if response.status != 201:
                    raise ValueError("Issue comment not accepted")
                raw = response.read(150_000)
            return json.loads(raw)
    try:
        result = sender(payload)
        if not isinstance(result, dict) or not result.get("id"):
            raise ValueError("Issue comment confirmation absent")
    except (OSError, ValueError, TypeError, TimeoutError):
        board["issue_delivery"] = {"state": "FAILED_RETRY_NEXT_RUN", "posted": False}
        return board
    board["last_notified_signature"] = board["transition"]["signature"]
    board["issue_delivery"] = {"state": "POSTED", "posted": True}
    board["notification_required"] = False
    return board


def main():
    current = json.loads((ROOT / "site/data/coordination.json").read_text("utf-8"))
    try:
        previous = json.loads(TASKBOARD.read_text("utf-8"))
    except (OSError, ValueError):
        previous = {}
    board = build_board(current, previous)
    board = post_update(board, os.getenv("GITHUB_TOKEN", ""))
    write_json(TASKBOARD, board)
    print(json.dumps({"active": len(board["active"]), "status": board["status"],
                      "notification": board["issue_delivery"]["state"],
                      "cross_repo_writes": False, "no_orders": True},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
