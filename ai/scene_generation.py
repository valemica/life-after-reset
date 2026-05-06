from __future__ import annotations

import json
import re
from textwrap import dedent
from typing import Any

from ai.narration import (
    DEFAULT_MODEL,
    build_tom_context,
    mentions_tom_in_third_person,
    ollama,
    sanitize_narration_text,
    summarize_history,
)
from game.economy import build_food_menu, format_money


ACTION_TYPES = {
    "legal_work",
    "food",
    "food_menu",
    "housing",
    "transport",
    "rest",
    "social_support",
    "quick_cash",
    "street_information",
    "medical_followup",
    "budget_plan",
}


def build_ai_scene(state: dict[str, Any], fallback_narration: str) -> dict[str, Any]:
    if state.get("hunger", 100) <= 50:
        return build_food_priority_scene(state) if state["active_flags"].get("food_menu_open") else build_low_hunger_scene(state)

    if ollama is None:
        return build_fallback_ai_scene(state)

    system_prompt = dedent(
        """
        You generate the next moment of a life simulation as Tom, the player's government-assigned recovery support specialist.
        Return valid JSON only. No markdown, no prose outside JSON.

        The JSON shape must be:
        {
          "kicker": "short location or situation",
          "title": "short scene title",
          "narration": "Tom speaks directly to the player in first person, 1 or 2 compact paragraphs.",
          "options": [
            {"label": "player-facing action under 70 characters", "action_type": "one allowed action type", "evidence": "exact phrase from narration that makes this option available"}
          ]
        }

        Rules:
        - Produce exactly four options.
        - Start by reacting to what just happened if there is a last outcome. Tom should sound like he remembers the previous choice.
        - Do not repeat recent Tom wording. Reuse facts only by paraphrasing them in a natural conversational way.
        - Keep related ideas in the same paragraph. Avoid stacking many one-line paragraphs.
        - Every option must be grounded in player knowledge.
        - A choice is valid only if the narration directly mentions the opportunity in the evidence phrase, or the opportunity is already listed in known facts.
        - The evidence field must be an exact substring from the narration.
        - You may introduce a shady opportunity only by mentioning it in this narration first, such as a flyer, old hospital hallway number, or street contact Tom noticed. If you do, make Tom uneasy but loyal.
        - Hunger is a fed meter: 100 means full and 0 means a hospital-level hunger emergency.
        - If hunger is 10 or below, Tom must directly tell the player to eat something before they collapse.
        - When money, hunger, or health are getting bad, include one tempting shady option sometimes, even for a mostly legal player.
        - If the player keeps choosing legal_work, offer laddered legal progress like better shifts, supervisor training, certifications, delivery contracts, or small-business steps.
        - If the player keeps choosing quick_cash, offer laddered criminal progress toward larger, faster payouts while making the risk clear.
        - Do not offer vouchers, jobs, meals, vehicles, people, places, or phone numbers unless Tom mentions them in the narration first or known facts already include them.
        - Keep choices specific to the character's current money, health, hunger, housing, vehicle, job leads, inventory, history, and Tom's relationship with them.
        - Avoid repeating the same four options from previous scenes.
        - Do not offer an option with the same wording as a recently selected option unless it is a continuing ladder action with changed wording.
        - If a practical need returns, introduce it through a new concrete detail in the narration instead of repeating the same menu-style sentence.
        - Use only these action_type values: legal_work, food, food_menu, housing, transport, rest, social_support, quick_cash, street_information, medical_followup, budget_plan.
        """
    ).strip()

    user_prompt = build_user_prompt(state, fallback_narration)

    try:
        response = ollama.chat(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            format="json",
        )
        payload = parse_json_payload(response["message"]["content"])
        scene = validate_ai_scene(payload, state)
        if scene:
            return scene
    except Exception:
        pass

    return build_fallback_ai_scene(state)


def build_user_prompt(state: dict[str, Any], fallback_narration: str) -> str:
    tom_context = build_tom_context(state)
    known_facts = build_known_facts(state)

    return dedent(
        f"""
        Client name: {state["name"]}
        Day: {state["day_count"]}
        Money: {format_money(state["cash"])}
        Goal: {format_money(state["cash_goal"])}
        Health: {state["health"]}
        Hunger/fed meter: {state["hunger"]} out of 100. 0 means hospital emergency; 10 or below means Tom must warn them to eat.
        Police attention: {state["police_heat"]}
        Morality read: {state["morality"]}
        Housing: {state["housing"]}
        Vehicle: {state["vehicle"]["name"]}, status {state["vehicle"]["status"]}, fuel {state["vehicle"]["fuel"]}
        Job: {state["job"] or "None"}
        Job lead: {state["job_lead"] or "None"}
        Legal progress level: {state.get("legal_level", 0)}
        Shady progress level: {state.get("shady_level", 0)}
        Last selected option: {state.get("last_choice_label") or "None"}
        Last selected action type: {state.get("last_choice_type") or "None"}
        Inventory: {", ".join(state.get("inventory", [])) or "None"}
        Tom's read: {tom_context["path_read"]}
        Tom relationship: {tom_context["relationship_mode"]}
        Voice brief: {tom_context["voice_brief"]}
        Risk read: {tom_context["risk_read"]}
        Known facts and available continuity:
        {known_facts}

        Recent lawful moves: {summarize_history(state.get("lawful_history", []), 5)}
        Recent risky moves: {summarize_history(state.get("criminal_history", []), 5)}
        Recent major events: {summarize_history(state.get("major_events", []), 5)}
        Recently selected option labels to avoid repeating exactly:
        {summarize_recent_choices(state)}
        Recently shown option labels to vary or replace:
        {summarize_recent_offered_options(state)}
        Last outcome: {state.get("last_outcome") or "None"}
        Recent Tom narration memory to avoid repeating:
        {summarize_tom_memory(state)}

        Current scripted scene notes, for continuity only:
        {fallback_narration}
        """
    ).strip()


def build_known_facts(state: dict[str, Any]) -> str:
    flags = state["active_flags"]
    facts = [
        "The player woke from a fifteen-year coma in Las Playas.",
        "Tom is their assigned recovery support specialist and is becoming a friend.",
        "The player's financial independence goal is $100,000.",
        f"The player has ${state['cash']} available.",
        f"The current housing situation is: {state['housing']}.",
        f"The 2001 Volvo status is: {state['vehicle']['status']}.",
    ]

    if flags.get("has_voucher"):
        facts.append("The player has formal support paperwork or a motel voucher.")
    if flags.get("called_impound_lot"):
        facts.append("The impound lot confirmed the Volvo can be released for $500.")
    if flags.get("car_recovered"):
        facts.append("The player has recovered the Volvo and can use it if it has fuel.")
    if flags.get("quick_cash_contact"):
        facts.append("The player has a suspicious easy-money contact from a folded flyer.")
    else:
        facts.append("The player has not committed to the easy-money contact, but Tom can still mention seeing shady hospital flyers or street pressure if the current narration introduces it.")
    if flags.get("job_center_visited") or state.get("job_lead"):
        facts.append(f"The player has a legitimate job lead: {state.get('job_lead') or state.get('job')}.")
    if flags.get("checked_into_motel"):
        facts.append("The player checked into a motel room and has a key.")

    return "\n".join(f"- {fact}" for fact in facts)


def summarize_tom_memory(state: dict[str, Any]) -> str:
    memories = state.get("tom_memory", [])[-3:]
    if not memories:
        return "None"

    summaries = []
    for memory in memories:
        narration = sanitize_narration_text(str(memory.get("narration", "")))
        narration = narration[:320]
        summaries.append(
            f"Day {memory.get('day')}: Tom said roughly '{narration}' Player chose: {memory.get('chosen_label') or 'unknown'}."
        )
    return "\n".join(f"- {summary}" for summary in summaries)


def parse_json_payload(raw_content: str) -> dict[str, Any]:
    stripped = raw_content.strip()
    if stripped.startswith("{"):
        return json.loads(stripped)

    match = re.search(r"\{.*\}", stripped, flags=re.DOTALL)
    if not match:
        raise ValueError("No JSON object found")
    return json.loads(match.group(0))


def validate_ai_scene(payload: dict[str, Any], state: dict[str, Any]) -> dict[str, Any] | None:
    narration = sanitize_narration_text(str(payload.get("narration", "")))
    options = payload.get("options")
    if not narration or mentions_tom_in_third_person(narration) or not isinstance(options, list) or len(options) != 4:
        return None

    clean_options = []
    used_labels = set()
    recent_labels = get_recent_option_labels(state, limit=8)
    for index, option in enumerate(options):
        label = sanitize_label(str(option.get("label", "")))
        action_type = str(option.get("action_type", "")).strip()
        evidence = sanitize_narration_text(str(option.get("evidence", "")))

        if not label or label in used_labels or action_type not in ACTION_TYPES:
            return None
        if action_type == "food_menu" and state.get("hunger", 100) > 50:
            return None
        if label.lower() in recent_labels:
            return None
        if not evidence or evidence.lower() not in narration.lower():
            return None

        used_labels.add(label)
        clean_options.append(
            {
                "id": f"ai_choice_{index}",
                "label": label,
                "action_type": action_type,
                "evidence": evidence,
            }
        )

    kicker = sanitize_label(str(payload.get("kicker", "Las Playas")) or "Las Playas")
    title = sanitize_label(str(payload.get("title", "The Next Move")) or "The Next Move")
    if mentions_tom_in_third_person(kicker):
        kicker = "Las Playas"
    if mentions_tom_in_third_person(title):
        title = "The Next Move"

    return {
        "kicker": kicker,
        "title": title,
        "narration": narration,
        "options": clean_options,
        "ai_generated": True,
    }


def sanitize_label(value: str) -> str:
    cleaned = sanitize_narration_text(value)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:90]


def get_recent_choice_labels(state: dict[str, Any], limit: int = 6) -> set[str]:
    labels = set()
    for item in state.get("choice_history", [])[-limit:]:
        label = sanitize_label(str(item.get("label", ""))).lower()
        if label:
            labels.add(label)
    last_label = sanitize_label(str(state.get("last_choice_label", ""))).lower()
    if last_label:
        labels.add(last_label)
    return labels


def get_recent_offered_labels(state: dict[str, Any], limit: int = 2) -> set[str]:
    labels = set()
    for memory in state.get("tom_memory", [])[-limit:]:
        for label in memory.get("offered_labels", []):
            cleaned = sanitize_label(str(label)).lower()
            if cleaned:
                labels.add(cleaned)
    return labels


def get_recent_option_labels(state: dict[str, Any], limit: int = 6) -> set[str]:
    return get_recent_choice_labels(state, limit=limit) | get_recent_offered_labels(state)


def summarize_recent_choices(state: dict[str, Any]) -> str:
    choices = state.get("choice_history", [])[-6:]
    if not choices and not state.get("last_choice_label"):
        return "None"

    lines = []
    for choice in choices:
        label = sanitize_label(str(choice.get("label", "")))
        action_type = str(choice.get("action_type", "")).strip() or "unknown"
        if label:
            lines.append(f"- {label} ({action_type})")
    if not lines and state.get("last_choice_label"):
        lines.append(f"- {sanitize_label(str(state['last_choice_label']))} ({state.get('last_choice_type') or 'unknown'})")
    return "\n".join(lines)


def summarize_recent_offered_options(state: dict[str, Any]) -> str:
    labels = sorted(get_recent_offered_labels(state, limit=1))
    if not labels:
        return "None"
    return "\n".join(f"- {label}" for label in labels)


def build_fallback_ai_scene(state: dict[str, Any]) -> dict[str, Any]:
    if state.get("hunger", 100) <= 50:
        return build_food_priority_scene(state) if state["active_flags"].get("food_menu_open") else build_low_hunger_scene(state)

    flags = state["active_flags"]
    last_label = state.get("last_choice_label") or ""
    pressure_is_high = state["cash"] < 300 or state["hunger"] < 25 or state["health"] < 45
    recent_labels = get_recent_option_labels(state)
    turn_variant = int(state.get("turn_count", 0))

    if last_label:
        opener = (
            f"Okay, so after you chose to {format_choice_as_action(last_label)}, here is what we actually learned: "
            f"{state.get('last_outcome') or 'the city answered us, even if it did not make anything simple.'}"
        )
    else:
        opener = (
            f"All right, {state['name']}. I am going from what you actually know now, not handing you a perfect little menu like the city suddenly got polite."
        )

    option_specs = [
        build_option_spec("food", turn_variant),
        build_option_spec("social_support", turn_variant),
        build_option_spec("medical_followup", turn_variant),
        build_option_spec("rest", turn_variant),
        build_option_spec("budget_plan", turn_variant),
    ]

    if flags.get("car_recovered"):
        transport_line = "the Volvo is outside if you want to keep transportation from becoming tomorrow's emergency"
        option_specs.append(build_option_spec("transport_recovered", turn_variant))
    elif flags.get("called_impound_lot") or state["cash"] >= state["vehicle"]["recovery_cost"]:
        transport_line = "the impound lot already confirmed the Volvo can be released for five hundred dollars"
        option_specs.append(build_option_spec("transport_release", turn_variant))
    else:
        transport_line = "we can call the impound lot again before you spend money you cannot afford to lose"
        option_specs.append(build_option_spec("transport_call", turn_variant))

    if state.get("job_lead"):
        legal_line = f"the legal ladder is still there through {state['job_lead']}"
        option_specs[1] = (get_legal_fallback_label(state), "legal_work", "legal ladder", "ladder")
    elif flags.get("job_center_visited"):
        legal_line = "the workforce office is still the least glamorous legal door in the city"
        option_specs[1] = (get_legal_fallback_label(state), "legal_work", "workforce office", "ladder")
    else:
        legal_line = "the workforce office opens today, and boring legal money is still money"
        option_specs[1] = ("Visit the workforce office", "legal_work", "workforce office opens today", "single")

    shady_line = ""
    if flags.get("quick_cash_contact"):
        shady_line = "the easy-money contact is still there, looking like trouble with a phone number"
        option_specs.append((get_shady_fallback_label(state), "quick_cash", "easy-money contact", "ladder"))
    elif pressure_is_high or state.get("legal_level", 0) >= 2:
        shady_line = "I also remember the easy-money flyer from the hospital hallway, and I hate that it is starting to sound useful"
        option_specs.append((get_shady_fallback_label(state), "quick_cash", "easy-money flyer from the hospital hallway", "single"))

    option_specs = filter_recent_options(option_specs, recent_labels, turn_variant)

    first_option = state.get("turn_count", 0) % len(option_specs)
    rotated_options = option_specs[first_option:] + option_specs[:first_option]
    selected_options = rotated_options[:4]
    required_evidence = {evidence.lower() for _, _, evidence, _ in selected_options}

    option_lines = [
        *get_all_option_lines("food"),
        *get_all_option_lines("social_support"),
        *get_all_option_lines("medical_followup"),
        *get_all_option_lines("rest"),
        *get_all_option_lines("budget_plan"),
        transport_line,
        legal_line,
    ]
    if shady_line:
        option_lines.append(shady_line)

    grounded_lines = [
        line for line in option_lines if any(evidence in line.lower() for evidence in required_evidence)
    ]
    if len(grounded_lines) > 1:
        closing = ", ".join(grounded_lines[:-1]) + f", or {grounded_lines[-1]}"
    else:
        closing = grounded_lines[0] if grounded_lines else "we still have a few grounded moves that fit what you know"

    narration = f"{opener} With that said, {closing}."
    return {
        "kicker": "Las Playas",
        "title": "What Actually Changed",
        "narration": narration,
        "options": [
            {
                "id": f"ai_choice_{index}",
                "label": label,
                "action_type": action_type,
                "evidence": evidence,
            }
            for index, (label, action_type, evidence, _) in enumerate(selected_options)
        ],
        "ai_generated": False,
    }


def build_food_priority_scene(state: dict[str, Any]) -> dict[str, Any]:
    menu = build_food_menu(state["cash"], state.get("cash_goal", 100_000))
    hunger = int(state.get("hunger", 0))
    last_outcome = state.get("last_outcome") or "Your body is making the decision louder than either of us."
    meal_lines = [
        f"the {option['evidence']} adds {option['hunger_gain']} hunger for {format_money(option['food_price'])}"
        for option in menu
    ]

    if hunger <= 10:
        warning = (
            f"Your hunger is down to {hunger}. Eat something now. "
            "That is not me being dramatic; that is me trying to keep you out of Las Playas General Hospital."
        )
        title = "Eat Before The Hospital"
    else:
        warning = (
            f"Your hunger is at {hunger}, which is low enough that food stops being optional. "
            "We are handling calories before we get clever."
        )
        title = "Food Comes First"

    narration = (
        f"Okay, here is the immediate problem: {last_outcome} {warning} "
        f"Right now, {', '.join(meal_lines[:-1])}, or {meal_lines[-1]}."
    )

    return {
        "kicker": "Hunger Check",
        "title": title,
        "narration": narration,
        "options": menu,
        "ai_generated": False,
    }


def build_low_hunger_scene(state: dict[str, Any]) -> dict[str, Any]:
    hunger = int(state.get("hunger", 0))
    last_outcome = state.get("last_outcome") or "Your body is starting to make hunger the loudest fact in the room."
    if hunger <= 10:
        warning = (
            f"Your hunger is down to {hunger}. Eat something now, because the hospital is what happens when this hits zero."
        )
        title = "I Push Food"
    else:
        warning = (
            f"Your hunger is at {hunger}. You can keep moving if you insist, but I am putting food on the table as the obvious move."
        )
        title = "Food Is The Obvious Move"

    support_label, support_evidence = get_support_option_for_low_hunger(state)
    risky_label, risky_evidence = get_risky_option_for_low_hunger(state)
    options = [
        {
            "id": "ai_choice_0",
            "label": "Eat something before this gets worse",
            "action_type": "food_menu",
            "evidence": "Eat something",
        },
        {
            "id": "ai_choice_1",
            "label": get_legal_fallback_label(state),
            "action_type": "legal_work",
            "evidence": "legal work",
        },
        {
            "id": "ai_choice_2",
            "label": support_label,
            "action_type": "social_support",
            "evidence": support_evidence,
        },
        {
            "id": "ai_choice_3",
            "label": risky_label,
            "action_type": "quick_cash",
            "evidence": risky_evidence,
        },
    ]

    narration = (
        f"Okay, here is the immediate problem: {last_outcome} {warning} "
        f"Eat something is the choice I want you to make. If you ignore me, legal work is still there, "
        f"{support_evidence} might steady the day, and {risky_evidence} is still hanging around like a bad shortcut."
    )

    return {
        "kicker": "Hunger Check",
        "title": title,
        "narration": narration,
        "options": options,
        "ai_generated": False,
    }


def get_support_option_for_low_hunger(state: dict[str, Any]) -> tuple[str, str]:
    if state["active_flags"].get("has_voucher"):
        return "Ask support services for practical help", "support services"
    return "Ask the county benefits desk for help", "county benefits desk"


def get_risky_option_for_low_hunger(state: dict[str, Any]) -> tuple[str, str]:
    if state["active_flags"].get("quick_cash_contact"):
        return get_shady_fallback_label(state), "easy-money contact"
    return "Text the easy-cash number", "easy-cash number"


def build_option_spec(kind: str, turn_variant: int) -> tuple[str, str, str, str]:
    variants = {
        "food": [
            ("Buy soup at the corner deli", "food", "corner deli"),
            ("Grab rice and coffee from the deli counter", "food", "deli counter"),
            ("Spend a few dollars on something hot", "food", "something hot"),
        ],
        "social_support": [
            ("Ask the county benefits desk for help", "social_support", "county benefits desk"),
            ("Use the support-services contact", "social_support", "support-services contact"),
            ("Let me push the paperwork line", "social_support", "paperwork line"),
        ],
        "medical_followup": [
            ("Check in at the clinic desk", "medical_followup", "clinic desk"),
            ("Book the follow-up before symptoms snowball", "medical_followup", "follow-up"),
            ("Get the nurse to look you over", "medical_followup", "nurse"),
        ],
        "rest": [
            ("Rest on the quiet bench", "rest", "quiet bench"),
            ("Take ten minutes in the shade", "rest", "ten minutes"),
            ("Sit down before your body votes no", "rest", "sit down"),
        ],
        "budget_plan": [
            ("Make a budget with me", "budget_plan", "actual budget"),
            ("Sort the cash plan with me", "budget_plan", "cash plan"),
            ("Map the next bills before moving", "budget_plan", "next bills"),
        ],
        "transport_recovered": [
            ("Check the Volvo and plan the next drive", "transport", "the Volvo is outside"),
            ("Put the Volvo to practical use", "transport", "the Volvo is outside"),
            ("Use the car before the day boxes you in", "transport", "the Volvo is outside"),
        ],
        "transport_release": [
            ("Go to the impound lot for the Volvo", "transport", "impound lot already confirmed"),
            ("Pay the release fee and recover the car", "transport", "impound lot already confirmed"),
            ("Turn the impound form into keys", "transport", "impound lot already confirmed"),
        ],
        "transport_call": [
            ("Call the impound lot for details", "transport", "call the impound lot again"),
            ("Confirm the Volvo release cost", "transport", "call the impound lot again"),
            ("Get the impound clerk on the phone", "transport", "call the impound lot again"),
        ],
    }
    label, action_type, evidence = variants[kind][turn_variant % len(variants[kind])]
    return label, action_type, evidence, "repeatable"


def format_choice_as_action(label: str) -> str:
    cleaned = sanitize_label(label).strip()
    if not cleaned:
        return "make that move"

    lowered = cleaned[:1].lower() + cleaned[1:]
    if lowered.startswith(("ask ", "call ", "check ", "go ", "pay ", "put ", "run ", "text ", "use ", "visit ")):
        return lowered
    if lowered.startswith(("buy ", "grab ", "spend ", "take ", "rest ", "book ", "get ", "make ", "sort ", "map ", "let ")):
        return lowered
    return f"pick {lowered}"


def get_option_line(kind: str, turn_variant: int) -> str:
    lines = {
        "food": [
            "food is still possible at the corner deli, but this time I am counting it as medicine with steam on it",
            "the deli counter has rice, coffee, and the kind of fluorescent lighting that makes survival feel official",
            "something hot would do more for your hands than another heroic speech from me",
        ],
        "social_support": [
            "paperwork help is still sitting behind the county benefits desk",
            "that support-services contact can turn humiliation into a phone call that actually helps",
            "the paperwork line is slow, but slow beats stranded",
        ],
        "medical_followup": [
            "the clinic desk can keep your recovery from becoming a preventable problem",
            "a follow-up now is less dramatic than your body staging a protest later",
            "the nurse can look you over before pride turns into a medical bill",
        ],
        "rest": [
            "a quiet bench is not a life plan, but it is ten minutes of not collapsing",
            "ten minutes in the shade would give your nervous system a vote",
            "you can sit down before your body votes no on this whole comeback",
        ],
        "budget_plan": [
            "an actual budget can keep the $100,000 goal from turning into a fantasy",
            "a cash plan with me would make the next hour less blurry",
            "the next bills need a map before they start ambushing you",
        ],
    }
    return lines[kind][turn_variant % len(lines[kind])]


def get_all_option_lines(kind: str) -> list[str]:
    return [get_option_line(kind, index) for index in range(3)]


def filter_recent_options(
    option_specs: list[tuple[str, str, str, str]],
    recent_labels: set[str],
    turn_variant: int,
) -> list[tuple[str, str, str, str]]:
    filtered = [spec for spec in option_specs if spec[0].lower() not in recent_labels]
    if len(filtered) >= 4:
        return filtered

    for kind in ["food", "rest", "medical_followup", "budget_plan", "social_support"]:
        replacement = build_option_spec(kind, turn_variant + 1)
        if replacement[0].lower() not in recent_labels and replacement[0] not in {spec[0] for spec in filtered}:
            filtered.append(replacement)
        if len(filtered) >= 4:
            break
    return filtered or option_specs


def get_legal_fallback_label(state: dict[str, Any]) -> str:
    level = int(state.get("legal_level", 0))
    labels = [
        "Visit the workforce office",
        "Work the next legal shift",
        "Ask about shift lead training",
        "Apply for supervisor training",
        "Take the operations role",
        "Bid on a small logistics contract",
    ]
    return labels[min(level + 1, len(labels) - 1)]


def get_shady_fallback_label(state: dict[str, Any]) -> str:
    level = int(state.get("shady_level", 0))
    labels = [
        "Call the easy-money number",
        "Take the cash handoff",
        "Run the package route",
        "Meet the crew dispatcher",
        "Move the high-risk stash",
        "Take the five-grand score",
    ]
    return labels[min(level, len(labels) - 1)]
