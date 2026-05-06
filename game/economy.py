from __future__ import annotations

from typing import Any


FOOD_TIERS = [
    {
        "name": "cheap snack",
        "label": "Buy a cheap snack",
        "hunger_gain": 10,
        "price_range": (10.0, 10.0),
    },
    {
        "name": "deli meal",
        "label": "Buy a deli meal",
        "hunger_gain": 20,
        "price_range": (10.0, 25.0),
    },
    {
        "name": "full hot meal",
        "label": "Buy a full hot meal",
        "hunger_gain": 40,
        "price_range": (25.0, 50.0),
    },
    {
        "name": "recovery feast",
        "label": "Buy a recovery feast",
        "hunger_gain": 100,
        "price_range": (50.0, 150.0),
    },
]


def normalize_money(value: Any) -> float:
    return round(max(0.0, float(value)), 2)


def format_money(value: Any) -> str:
    amount = normalize_money(value)
    if amount.is_integer():
        return f"${int(amount):,}"
    return f"${amount:,.2f}"


def get_goal_progress_ratio(cash: float, goal: float) -> float:
    if goal <= 0:
        return 0.0
    return max(0.0, min(float(cash) / float(goal), 1.0))


def get_food_price_factor(cash: float, goal: float) -> float:
    progress = get_goal_progress_ratio(cash, goal)
    if progress <= 0.25:
        return 0.0
    if progress >= 0.75:
        return 1.0
    return (progress - 0.25) / 0.5


def calculate_food_price(tier: dict[str, Any], cash: float, goal: float) -> float:
    low, high = tier["price_range"]
    factor = get_food_price_factor(cash, goal)
    return round(low + ((high - low) * factor), 2)


def build_food_menu(cash: float, goal: float) -> list[dict[str, Any]]:
    menu = []
    previous_price = 0.0
    for index, tier in enumerate(FOOD_TIERS):
        price = calculate_food_price(tier, cash, goal)
        low, high = tier["price_range"]
        if index > 0 and price <= previous_price:
            price = min(high, previous_price + 5)
        price = max(low, min(high, price))
        previous_price = price
        hunger_gain = tier["hunger_gain"]
        name = tier["name"]
        menu.append(
            {
                "id": f"ai_choice_{index}",
                "label": f"{tier['label']} (+{hunger_gain} hunger) - {format_money(price)}",
                "action_type": "food",
                "evidence": name,
                "food_price": price,
                "hunger_gain": hunger_gain,
                "food_name": name,
            }
        )
    return menu
