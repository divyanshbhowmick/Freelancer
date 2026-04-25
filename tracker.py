import json
import os
from datetime import datetime

TRACKER_FILE = "tracker.json"

WEEKLY_PLAN = {
    "week1": {
        "label": "Week 1 — Foundation",
        "tasks": [
            "Create Upwork profile with Cloud Cost Optimization headline",
            "Upload Java/DevOps portfolio samples (GitHub links)",
            "Write 3 niche-specific profile descriptions",
            "Set Upwork hourly rate to $40/hr minimum",
            "Identify 10 target companies on LinkedIn (50-500 employees, cloud-heavy)",
            "Send 5 LinkedIn connection requests with personalized notes",
            "Publish first LinkedIn post (K8s audit post template)",
            "Submit 4 Upwork proposals (Cloud Cost niche)",
        ],
    },
    "week2": {
        "label": "Week 2 — First Conversations",
        "tasks": [
            "Submit 4 more Upwork proposals (Elasticsearch/AI Search niche)",
            "Follow up on Week 1 LinkedIn connections (Day 4 DM)",
            "Publish second LinkedIn post (Elasticsearch/AI angle)",
            "Send 5 new LinkedIn connection requests",
            "Research Arc.dev — prepare profile content",
            "Aim for at least 1 discovery call booked",
            "Review and refine proposal win rate — adjust if needed",
            "Track response rates in tracker",
        ],
    },
    "week3": {
        "label": "Week 3 — First Client",
        "tasks": [
            "Submit 4 proposals (mix: Cloud Cost + Elasticsearch)",
            "Conduct discovery calls — use SPIN selling questions",
            "Send 5 new LinkedIn connections",
            "Publish third LinkedIn post (Terraform/IaC angle)",
            "Register on Arc.dev — complete profile",
            "Follow up on all pending proposals > 5 days old",
            "Aim to close first paid engagement (retainer or project)",
            "Draft SOW/contract template for signed clients",
        ],
    },
    "week4": {
        "label": "Week 4 — Close & Systemize",
        "tasks": [
            "Close first client — sign contract, collect deposit",
            "Begin Toptal application process",
            "Submit 4 Upwork proposals (maintain pipeline)",
            "Publish fourth LinkedIn post (success story / results-focused)",
            "Send 5 new LinkedIn connections",
            "Set up recurring weekly review cadence",
            "Calculate Month 1 actual income vs. ₹1.9L target",
            "Plan Month 2 — identify retainer expansion opportunities",
        ],
    },
}


def _load() -> dict:
    if not os.path.exists(TRACKER_FILE):
        return {"completed": {}, "notes": {}, "created_at": datetime.now().isoformat()}
    with open(TRACKER_FILE) as f:
        return json.load(f)


def _save(data: dict) -> None:
    with open(TRACKER_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_progress(week: str | None = None) -> dict:
    data = _load()
    completed = data.get("completed", {})

    if week and week in WEEKLY_PLAN:
        weeks_to_show = {week: WEEKLY_PLAN[week]}
    else:
        weeks_to_show = WEEKLY_PLAN

    result = {}
    for wk, info in weeks_to_show.items():
        tasks = info["tasks"]
        done_indices = completed.get(wk, [])
        done_tasks = [tasks[i] for i in done_indices if i < len(tasks)]
        pending_tasks = [tasks[i] for i in range(len(tasks)) if i not in done_indices]
        result[wk] = {
            "label": info["label"],
            "total": len(tasks),
            "done": len(done_tasks),
            "completed_tasks": done_tasks,
            "pending_tasks": pending_tasks,
        }

    return result


def update_progress(week: str, task_indices: list[int], note: str = "") -> dict:
    if week not in WEEKLY_PLAN:
        return {"error": f"Unknown week '{week}'. Valid: {list(WEEKLY_PLAN.keys())}"}

    data = _load()
    completed = data.setdefault("completed", {})
    existing = set(completed.get(week, []))
    max_idx = len(WEEKLY_PLAN[week]["tasks"]) - 1

    added = []
    for idx in task_indices:
        if 0 <= idx <= max_idx:
            existing.add(idx)
            added.append(WEEKLY_PLAN[week]["tasks"][idx])

    completed[week] = sorted(existing)

    if note:
        data.setdefault("notes", {})[f"{week}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"] = note

    _save(data)
    return {"updated": week, "newly_completed": added, "total_done": len(existing)}


def get_all_tasks_flat(week: str) -> list[dict]:
    if week not in WEEKLY_PLAN:
        return []
    return [{"index": i, "task": t} for i, t in enumerate(WEEKLY_PLAN[week]["tasks"])]
