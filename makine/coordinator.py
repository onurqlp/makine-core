"""MAKİNE unattended, read-only, cross-project coordination snapshots.

This is deterministic orchestration, NOT an LLM or autonomous code-writing agent.
It does not send orders or change source repositories.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import urllib.request

from .cli import write_json
from .source import parse_time, stamp, utcnow

ROOT = pathlib.Path(__file__).resolve().parents[1]
TARGET = ROOT / "site" / "data" / "coordination.json"
HISTORY = ROOT / "data" / "coordination-history.json"
REPOS = {
    "coinlive": {"repo": "onurqlp/coin-live-pro", "max_age_minutes": 30},
    "alti": {"repo": "onurqlp/alti-quant-lab", "max_age_minutes": 90},
}
ALTI_IDS = ("A1", "A2", "A3", "B1", "B2", "T0")
LINKS = {
    "master": "https://github.com/onurqlp/makine-core/issues/1",
    "alti": "https://github.com/onurqlp/alti-quant-lab/issues/1",
    "coinlive": "https://github.com/onurqlp/coin-live-pro/issues/28",
}
OVERLAPS = ((31, "B1"), (36, "B2"), (43, "A1"), (45, "A2"),
            (54, "A3"), (55, "T0"))
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
MAX_FILE = 2_000_000
MAX_HISTORY = 336  # 14 days at the nominal hourly cadence


def fetch_bytes(url):
    """Only fixed, explicitly approved GitHub sources; never remote code."""
    host_api = "https://api.github.com/repos/"
    host_raw = "https://raw.githubusercontent.com/"
    if not (url.startswith(host_api) or url.startswith(host_raw)):
        raise ValueError("Non-GitHub data source denied")
    headers = {"User-Agent": "MakineSafeCoordinator/1.0",
               "Accept": "application/vnd.github+json" if url.startswith(host_api) else "application/json"}
    key = os.getenv("GITHUB_TOKEN", "")
    if key and url.startswith(host_api):
        headers["Authorization"] = "Bearer " + key
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=18) as resp:
        b = resp.read(MAX_FILE + 1)
    if len(b) > MAX_FILE:
        raise ValueError("Source size limit exceeded")
    return b


def read_pinned(repo, paths, fetch=fetch_bytes):
    """Resolve one immutable commit per repo; never mix files from moving main."""
    if repo not in [v["repo"] for v in REPOS.values()]:
        raise ValueError("Repository not allowlisted")
    ref_url = "https://api.github.com/repos/" + repo + "/git/ref/heads/main"
    ref = json.loads(fetch(ref_url))
    sha = (ref.get("object") or {}).get("sha")
    if not isinstance(sha, str) or not SHA_RE.fullmatch(sha):
        raise ValueError("No verified source SHA")
    docs, hashes = {}, {}
    for path in paths:
        if not re.fullmatch(r"[a-z0-9_./-]+\.json", path) or ".." in path:
            raise ValueError("Unsafe source path")
        raw = fetch("https://raw.githubusercontent.com/" + repo + "/" + sha + "/" + path)
        if len(raw) > MAX_FILE:
            raise ValueError("Oversized JSON")
        docs[path] = json.loads(raw)
        hashes[path] = hashlib.sha256(raw).hexdigest()
    return sha, docs, hashes


def age_minutes(ts, now):
    t = parse_time(ts)
    if t is None:
        return None
    return round((now - t).total_seconds() / 60, 2)


def fresh_status(age, maximum):
    if age is None or age < -5:
        return "INVALID_TIME"
    if age > maximum:
        return "STALE"
    return "FRESH"


def coinlive(now, fetch=fetch_bytes):
    repo = REPOS["coinlive"]["repo"]
    paths = ("web/data/v4-manifest.json", "web/data/health.json",
             "web/data/v4-radar.json", "web/data/v4-paper.json")
    sha, docs, hashes = read_pinned(repo, paths, fetch)
    man, health = docs[paths[0]], docs[paths[1]]
    checks = []
    for path, label in ((paths[2], "v4-radar"), (paths[3], "v4-paper")):
        expected = (man.get("sources", {}).get(label) or {}).get("sha256")
        if not expected or expected != hashes[path]:
            checks.append("HASH_MISMATCH_" + label.upper().replace("-", "_"))
        if docs[path].get("scan_id") != man.get("scan_id"):
            checks.append("SCAN_ID_MISMATCH_" + label.upper().replace("-", "_"))
    if not man.get("publication_valid") or man.get("no_real_orders") is not True:
        checks.append("MANIFEST_NOT_VALID_OR_ORDERS_ALLOWED")
    if not man.get("scan_id"):
        checks.append("MISSING_SCAN_ID")
    age = age_minutes(man.get("finished_at_utc"), now)
    status = fresh_status(age, REPOS["coinlive"]["max_age_minutes"])
    if status == "FRESH" and checks:
        status = "INVALID"
    health_age = age_minutes(health.get("updated_at"), now)
    if health_age is None or health_age < -5 or health_age > REPOS["coinlive"]["max_age_minutes"]:
        checks.append("HEALTH_TIMESTAMP_STALE_OR_INVALID")
        if status == "FRESH":
            status = "PARTIAL"
    if health.get("status") != "OK":
        checks.append("HEALTH_NOT_OK")
        if status == "FRESH":
            status = "PARTIAL"
    return {
        "repo": repo, "commit_sha": sha, "scan_id": man.get("scan_id"),
        "observed_at_utc": man.get("finished_at_utc"),
        "age_minutes": age, "freshness_limit_minutes": REPOS["coinlive"]["max_age_minutes"],
        "state": status, "source_health": health.get("status"),
        "real_scheduled_runs_seen": health.get("observed_real_scheduled_runs", 0),
        "schedule_proven_in_source": health.get("schedule_proven") is True,
        "partial_hash_verified": len([x for x in checks if x.startswith("HASH_MISMATCH")]) == 0,
        "hash_scope": ["v4-radar", "v4-paper"], "warnings": checks,
        "market_context_only": True, "can_place_orders": False,
    }


def alti(now, fetch=fetch_bytes):
    repo = REPOS["alti"]["repo"]
    sha, docs, hashes = read_pinned(repo, ("site/report.json",), fetch)
    report = docs["site/report.json"]
    strategies = {s.get("id"): s for s in report.get("strategies", [])
                  if isinstance(s, dict) and s.get("id") in ALTI_IDS}
    warnings = []
    if set(strategies) != set(ALTI_IDS):
        warnings.append("SIX_STRATEGY_CATALOG_INCOMPLETE")
    if report.get("live_orders_enabled") is not False:
        warnings.append("LIVE_ORDER_GUARD_NOT_VERIFIED")
    if report.get("synthetic_data_in_report") is True:
        warnings.append("SYNTHETIC_DATA_PRESENT")
    provider_states = sorted({p.get("status", "UNKNOWN") for p in report.get("provider_health", [])
                              if isinstance(p, dict)})
    if report.get("errors") or any(x in provider_states for x in ("ACCESS_BLOCKED", "SOURCE_ERROR")):
        warnings.append("PARTIAL_PROVIDER_ACCESS")
    age = age_minutes(report.get("generated_at_utc"), now)
    status = fresh_status(age, REPOS["alti"]["max_age_minutes"])
    if status == "FRESH" and any(x in warnings for x in
                                 ("SIX_STRATEGY_CATALOG_INCOMPLETE",
                                  "LIVE_ORDER_GUARD_NOT_VERIFIED")):
        status = "INVALID"
    elif status == "FRESH" and warnings:
        status = "PARTIAL"
    return {
        "repo": repo, "commit_sha": sha, "scan_id": report.get("scan_id"),
        "observed_at_utc": report.get("generated_at_utc"),
        "last_successful_scan_utc": report.get("last_successful_scan_utc"),
        "age_minutes": age, "freshness_limit_minutes": REPOS["alti"]["max_age_minutes"],
        "state": status, "scan_status": report.get("scan_status"),
        "strategies": {k: {"state": strategies[k].get("status"),
                            "data_label": strategies[k].get("data_label"),
                            "actionable": False} for k in ALTI_IDS if k in strategies},
        "provider_states": provider_states, "source_hash_sha256": hashes["site/report.json"],
        "warnings": warnings, "can_place_orders": False, "verified_real_pnl": None,
    }


def unavailable(repo, exc):
    # Never put raw HTTP responses or auth tokens into public JSON.
    return {"repo": repo, "state": "UNAVAILABLE", "commit_sha": None,
            "scan_id": None, "observed_at_utc": None, "age_minutes": None,
            "warnings": ["SOURCE_FETCH_FAILED_" + type(exc).__name__],
            "can_place_orders": False}


def build_snapshot(now=None, fetch=fetch_bytes):
    now = now or utcnow()
    sources = {}
    for key, fn in (("coinlive", coinlive), ("alti", alti)):
        try:
            sources[key] = fn(now, fetch)
        except (OSError, ValueError, TypeError, KeyError, TimeoutError) as exc:
            sources[key] = unavailable(REPOS[key]["repo"], exc)
    complete = all(s["state"] == "FRESH" for s in sources.values())
    mappings = []
    for idea, strategy in OVERLAPS:
        state = (sources["alti"].get("strategies") or {}).get(strategy, {})
        mappings.append({
            "makine_model_id": idea, "alti_strategy_id": strategy,
            "alti_status": state.get("state", "NOT_VERIFIED"),
            "owner": "ALTI", "handoff_status": "RESEARCH_ONLY",
            "automatic_signal_promotion": False,
        })
    report = {
        "schema": "makine-coordination-v1", "generated_at_utc": stamp(now),
        "mode": "AUTOMATED_READ_ONLY", "system_state": "FRESH" if complete else "ATTENTION_REQUIRED",
        "sources": sources, "overlaps": mappings, "coordination_issues": LINKS,
        "next_tasks": [
            {"owner": "MAKİNE", "task": "Track freshness and schema of public research snapshots",
             "mode": "AUTOMATIC_CHECK"},
            {"owner": "ALTI", "task": "Validate mapped six strategies independently",
             "mode": "PROPOSED_NOT_DISPATCHED", "issue": LINKS["alti"]},
            {"owner": "COIN.LIVE", "task": "Expose read-only market research evidence",
             "mode": "PROPOSED_NOT_DISPATCHED", "issue": LINKS["coinlive"]},
        ],
        "agent_runtime": {"state": "NOT_CONNECTED", "reason": "No approved AI API credential or agent runner",
                          "unattended_deterministic_coordinator": True,
                          "autonomous_llm_agents_running": False},
        "controls": {"source_repo_writes": False, "place_real_orders": False,
                     "place_paper_orders": False, "promote_live_signals": False,
                     "change_release_version": False, "merge_virtual_portfolios": False,
                     "verified_revenue_try": None},
        "notes": [
            "GitHub Actions scheduler is best-effort; verify actual workflow runs.",
            "A current immutable commit does not mean market observations are fresh.",
            "Coin.Live hash checks here cover v4-radar and v4-paper; the separate full research refresh has wider checks.",
            "No parallel ChatGPT/Codex agents are remotely started by this job.",
        ],
    }
    return report


def persist(report, output=TARGET, history_path=HISTORY):
    write_json(output, report)
    try:
        index = json.loads(history_path.read_text(encoding="utf-8"))
        if not isinstance(index, dict) or not isinstance(index.get("entries"), list):
            index = {"schema": "makine-coordination-history-v1", "entries": []}
    except (ValueError, OSError):
        index = {"schema": "makine-coordination-history-v1", "entries": []}
    event = {
        "hour_utc": report["generated_at_utc"][:13],
        "generated_at_utc": report["generated_at_utc"],
        "system_state": report["system_state"],
        "trigger_type": report.get("runtime_event", "LOCAL_OR_UNKNOWN"),
        "source_states": {k: v["state"] for k, v in report["sources"].items()},
        "source_shas": {k: v.get("commit_sha") for k, v in report["sources"].items()},
        "source_scan_ids": {k: v.get("scan_id") for k, v in report["sources"].items()},
        "no_orders": True,
    }
    rows = [x for x in index["entries"] if x.get("hour_utc") != event["hour_utc"]]
    rows.append(event)
    index["entries"] = sorted(rows, key=lambda x: x.get("hour_utc", ""))[-MAX_HISTORY:]
    write_json(history_path, index)


def main():
    snapshot = build_snapshot()
    event = os.getenv("GITHUB_EVENT_NAME", "LOCAL_OR_UNKNOWN")
    snapshot["runtime_event"] = event if event in ("push", "schedule", "workflow_dispatch") else "LOCAL_OR_UNKNOWN"
    snapshot["schedule_proven_this_run"] = snapshot["runtime_event"] == "schedule"
    persist(snapshot)
    print(json.dumps({"state": snapshot["system_state"],
                      "sources": {k: v["state"] for k, v in snapshot["sources"].items()},
                      "agent_runtime": snapshot["agent_runtime"]["state"],
                      "no_orders": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
