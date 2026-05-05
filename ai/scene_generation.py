from __future__ import annotations

import json
import re
from textwrap import dedent
from typing import Any

from ai.narration import DEFAULT_MODEL, build_tom_context, ollama, sanitize_narration_text, summarize_history


ACTION_TYPES = {
    "legal_work",
    "food",
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
        - When money, hunger, health, or energy are getting bad, include one tempting shady option sometimes, even for a mostly legal player.
        - If the player keeps choosing legal_work, offer laddered legal progress like better shifts, supervisor training, certifications, delivery contracts, or small-business steps.
        - If the player keeps choosing quick_cash, offer laddered criminal progress toward larger, faster payouts while making the risk clear.
        - Do not offer vouchers, jobs, meals, vehicles, people, places, or phone numbers unless Tom mentions them in the narration first or known facts already include them.
        - Keep choices specific to the character's current money, health, energy, hunger, housing, vehicle, job leads, inventory, history, and Tom's relationship with them.
        - Avoid repeating the same four options from previous scenes.
        - Use only these action_type values: legal_work, food, housing, transport, rest, social_support, quick_cash, street_information, medical_followup, budget_plan.
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
        Money: ${state["cash"]}
        Goal: ${state["cash_goal"]}
        Health: {state["health"]}
        Energy: {state["energy"]}
        Hunger: {state["hunger"]}
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
    if not narration or not isinstance(options, list) or len(options) != 4:
        return None

    clean_options = []
    used_labels = set()
    for index, option in enumerate(options):
        label = sanitize_label(str(option.get("label", "")))
        action_type = str(option.get("action_type", "")).strip()
        evidence = sanitize_narration_text(str(option.get("evidence", "")))

        if not label or label in used_labels or action_type not in ACTION_TYPES:
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

    return {
        "kicker": sanitize_label(str(payload.get("kicker", "Las Playas")) or "Las Playas"),
        "title": sanitize_label(str(payload.get("title", "The Next Move")) or "The Next Move"),
        "narration": narration,
        "options": clean_options,
        "ai_generated": True,
    }


def sanitize_label(value: str) -> str:
    cleaned = sanitize_narration_text(value)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:90]


def build_fallback_ai_scene(state: dict[str, Any]) -> dict[str, Any]:
    flags = state["active_flags"]
    last_label = state.get("last_choice_label") or ""
    pressure_is_high = state["cash"] < 300 or state["hunger"] > 70 or state["energy"] < 25 or state["health"] < 45

    if last_label:
        opener = (
            f"Okay, so after {last_label.lower()}, here is what we actually learned: "
            f"{state.get('last_outcome') or 'the city answered us, even if it did not make anything simple.'}"
        )
    else:
        opener = (
            f"All right, {state['name']}. I am going from what you actually know now, not handing you a perfect little menu like the city suddenly got polite."
        )

    option_specs = [
        ("Buy soup at the corner deli", "food", "corner deli"),
        ("Ask the county benefits desk for help", "social_support", "county benefits desk"),
        ("Check in at the clinic desk", "medical_followup", "clinic desk"),
        ("Rest on the quiet bench", "rest", "quiet bench"),
        ("Make a budget with Tom", "budget_plan", "actual budget"),
    ]

    if flags.get("car_recovered"):
        transport_line = "the Volvo is outside if you want to keep transportation from becoming tomorrow's emergency"
        option_specs.append(("Check the Volvo and plan the next drive", "transport", "the Volvo is outside"))
    elif flags.get("called_impound_lot") or state["cash"] >= state["vehicle"]["recovery_cost"]:
        transport_line = "the impound lot already confirmed the Volvo can be released for five hundred dollars"
        option_specs.append(("Go to the impound lot for the Volvo", "transport", "impound lot already confirmed"))
    else:
        transport_line = "we can call the impound lot again before you spend money you cannot afford to lose"
        option_specs.append(("Call the impound lot for details", "transport", "call the impound lot again"))

    if state.get("job_lead"):
        legal_line = f"the legal ladder is still there through {state['job_lead']}"
        option_specs[1] = (get_legal_fallback_label(state), "legal_work", "legal ladder")
    elif flags.get("job_center_visited"):
        legal_line = "the workforce office is still the least glamorous legal door in the city"
        option_specs[1] = (get_legal_fallback_label(state), "legal_work", "workforce office")
    else:
        legal_line = "the workforce office opens today, and boring legal money is still money"
        option_specs[1] = ("Visit the workforce office", "legal_work", "workforce office opens today")

    shady_line = ""
    if flags.get("quick_cash_contact"):
        shady_line = "the easy-money contact is still there, looking like trouble with a phone number"
        option_specs.append((get_shady_fallback_label(state), "quick_cash", "easy-money contact"))
    elif pressure_is_high or state.get("legal_level", 0) >= 2:
        shady_line = "I also remember the easy-money flyer from the hospital hallway, and I hate that it is starting to sound useful"
        option_specs.append((get_shady_fallback_label(state), "quick_cash", "easy-money flyer from the hospital hallway"))

    first_option = state.get("turn_count", 0) % len(option_specs)
    rotated_options = option_specs[first_option:] + option_specs[:first_option]
    selected_options = rotated_options[:4]
    required_evidence = {evidence.lower() for _, _, evidence in selected_options}

    option_lines = [
        "food is still possible at the corner deli",
        "paperwork help is still sitting behind the county benefits desk",
        "the clinic desk can keep your recovery from becoming a preventable problem",
        "a quiet bench is not a life plan, but it is ten minutes of not collapsing",
        "an actual budget can keep the $100,000 goal from turning into a fantasy",
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
            for index, (label, action_type, evidence) in enumerate(selected_options)
        ],
        "ai_generated": False,
    }


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
