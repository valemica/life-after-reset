from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from pathlib import Path
import json
import re
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
SAVE_DIR = ROOT_DIR / "saves"

STARTING_INVENTORY = [
    "hospital discharge papers",
    "late grandma's envelope",
    "cheap smartphone",
    "wallet and ID",
    "basic clothes",
]

FINANCIAL_INDEPENDENCE_GOAL = 100_000


def clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(value, maximum))


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return cleaned or "player"


def add_unique_item(items: list[str], item: str) -> None:
    if item not in items:
        items.append(item)


def add_event(history: list[str], event: str) -> None:
    history.append(event)
    if len(history) > 14:
        del history[0]


def create_player_state(name: str) -> dict[str, Any]:
    return {
        "name": name,
        "age": 28,
        "cash": 1450,
        "cash_goal": FINANCIAL_INDEPENDENCE_GOAL,
        "game_over": False,
        "ending_type": None,
        "health": 85,
        "energy": 70,
        "hunger": 30,
        "stress": 40,
        "morality": 0,
        "police_heat": 0,
        "reputation": 0,
        "job": None,
        "job_lead": None,
        "housing": "discharge pending",
        "alive": True,
        "day_count": 1,
        "turn_count": 0,
        "current_phase": "intro",
        "current_scene": "hospital_intro",
        "last_outcome": "",
        "vehicle": {
            "name": "2001 Volvo S60",
            "status": "impounded",
            "recovery_cost": 500,
            "condition": "poor",
            "fuel": 10,
        },
        "inventory": deepcopy(STARTING_INVENTORY),
        "major_events": [
            "Woke up at Las Playas General Hospital after a fifteen-year coma.",
            "Met Tom, the state's assigned recovery support specialist.",
        ],
        "criminal_history": [],
        "lawful_history": [],
        "known_npcs": {
            "Tom": {
                "trust": 1,
                "notes": ["met at hospital"],
            }
        },
        "active_flags": {
            "met_tom": True,
            "gave_name": True,
            "reviewed_plan": False,
            "has_voucher": False,
            "called_impound_lot": False,
            "quick_cash_contact": False,
            "car_recovered": False,
            "checked_into_motel": False,
            "job_center_visited": False,
            "worked_shift": False,
        },
    }


def normalize_state(state: dict[str, Any]) -> None:
    state.setdefault("cash_goal", FINANCIAL_INDEPENDENCE_GOAL)
    state.setdefault("game_over", False)
    state.setdefault("ending_type", None)

    state["cash"] = max(0, int(state["cash"]))
    state["health"] = clamp(int(state["health"]), 0, 100)
    state["energy"] = clamp(int(state["energy"]), 0, 100)
    state["hunger"] = clamp(int(state["hunger"]), 0, 100)
    state["stress"] = clamp(int(state["stress"]), 0, 100)
    state["police_heat"] = clamp(int(state["police_heat"]), 0, 100)
    state["vehicle"]["fuel"] = clamp(int(state["vehicle"]["fuel"]), 0, 100)

    if state["hunger"] >= 85:
        state["health"] = clamp(state["health"] - 3, 0, 100)
    if state["energy"] <= 15:
        state["stress"] = clamp(state["stress"] + 4, 0, 100)


def save_game(state: dict[str, Any]) -> Path:
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    payload = deepcopy(state)
    payload["last_saved_at"] = datetime.now().isoformat(timespec="seconds")
    save_path = SAVE_DIR / f"{slugify(state['name'])}_latest.json"
    with save_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    return save_path


def get_progress_snapshot(state: dict[str, Any]) -> dict[str, str]:
    normalize_state(state)
    job_text = state["job"] or state["job_lead"] or "Unemployed"
    goal_progress = min(100, round((state["cash"] / state["cash_goal"]) * 100))
    vehicle_status = state["vehicle"]["status"]
    if state["active_flags"]["car_recovered"]:
        vehicle_text = f"{state['vehicle']['name']} ({vehicle_status}, {state['vehicle']['fuel']} fuel)"
    else:
        vehicle_text = f"{state['vehicle']['name']} ({vehicle_status})"

    return {
        "day": str(state["day_count"]),
        "cash": f"${state['cash']}",
        "goal_progress": f"{goal_progress}%",
        "health": str(state["health"]),
        "energy": str(state["energy"]),
        "hunger": str(state["hunger"]),
        "housing": state["housing"],
        "vehicle": vehicle_text,
        "job": job_text,
    }
