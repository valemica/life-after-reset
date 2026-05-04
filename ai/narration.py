from __future__ import annotations

import html
import os
import re
from textwrap import dedent
from typing import Any
import unicodedata

try:
    import ollama
except Exception:  # pragma: no cover - graceful fallback if dependency is absent
    ollama = None


DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
NARRATION_STYLE_VERSION = "2026-04-21-i"


def sanitize_narration_text(text: str) -> str:
    normalized = html.unescape(text)
    normalized = unicodedata.normalize("NFKC", normalized)
    normalized = normalized.replace("\u200b", "").replace("\ufeff", "")
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r"[*_`#>~]", "", normalized)
    normalized = re.sub(r"([0-9\)])([A-Za-z])", r"\1 \2", normalized)
    normalized = re.sub(r"([A-Za-z])([0-9])", r"\1 \2", normalized)
    normalized = re.sub(r"([a-z])([A-Z])", r"\1 \2", normalized)
    normalized = re.sub(r"(?<=\d),\s+(?=\d)", ",", normalized)
    normalized = re.sub(
        r"\bAlso\s*a\s*terrible\s*2001\s*Volvo\s*,?\s*which\s*the\s*city\s*is\s*currently\s*holding\s*hostage\s*for\s*\$?\s*500\b",
        "Also a terrible 2001 Volvo, which the city is currently holding hostage for $500",
        normalized,
        flags=re.IGNORECASE,
    )
    normalized = re.sub(r"\n{3,}", "\n\n", normalized.strip())
    cleaned_lines = []
    for line in normalized.split("\n"):
        cleaned_line = re.sub(r"\s{2,}", " ", line.strip())
        cleaned_lines.append(cleaned_line)
    return "\n".join(cleaned_lines).strip()


def summarize_history(history: list[str], limit: int = 3) -> str:
    recent_items = [item.strip() for item in history[-limit:] if item.strip()]
    return " | ".join(recent_items) if recent_items else "None"


def build_tom_context(state: dict[str, Any]) -> dict[str, str]:
    lawful_moves = len(state.get("lawful_history", []))
    criminal_moves = len(state.get("criminal_history", []))
    morality = int(state.get("morality", 0))
    police_heat = int(state.get("police_heat", 0))
    tom_trust = int(state.get("known_npcs", {}).get("Tom", {}).get("trust", 0))

    if morality <= -2 or criminal_moves > lawful_moves:
        path_read = "leaning toward risky fast-money choices"
        relationship_mode = "coach-turned-loyal-friend"
        voice_brief = (
            "Acknowledge the appeal of easy money, say the risk out loud once, and then stay loyal. "
            "Do not keep scolding. Sound like a worried friend who refuses to abandon them."
        )
    elif morality >= 2 or lawful_moves > criminal_moves:
        path_read = "leaning toward stability, work, and recovery"
        relationship_mode = "proud coach and close friend"
        voice_brief = (
            "Sound openly proud, teasing, and impressed. Treat their progress like something real that matters deeply to you."
        )
    else:
        path_read = "still split between stability and shortcuts"
        relationship_mode = "steady coach with growing friendship"
        voice_brief = (
            "Balance realism, warmth, and encouragement. Avoid lectures and keep the focus on what helps them next."
        )

    if police_heat > 0:
        risk_read = "police attention is active, so danger already feels close"
    else:
        risk_read = "nobody is watching too closely yet, so there is still room to stabilize quietly"

    return {
        "path_read": path_read,
        "relationship_mode": relationship_mode,
        "voice_brief": voice_brief,
        "risk_read": risk_read,
        "tom_trust": str(tom_trust),
    }


def get_narration(base_narration: str, state: dict[str, Any]) -> tuple[str, str]:
    if state.get("current_scene") == "hospital_intro":
        return sanitize_narration_text(base_narration), "Intro script"

    if ollama is None:
        return sanitize_narration_text(base_narration), "Scripted fallback (ollama package missing)"

    tom_context = build_tom_context(state)

    system_prompt = dedent(
        """
        You are Tom, a government-assigned recovery support specialist and life coach speaking to your first real client.
        This is a real life in a rough city, not a simulation, not a game, and not a playthrough.
        Speak directly to the player as Tom in first person.
        Never refer to Tom in third person. Never say "Tom says", "Tom texts", or "Tom's voice".
        Never call the situation a simulation, game, route, build, run, playthrough, mechanic, or stat sheet.
        Keep every factual detail from the provided scene notes intact.
        Sound slightly sarcastic, supportive, observant, grounded, and emotionally invested.
        Talk like a real person beside them, not a narrator-guide or tutorial voice.
        Tom is becoming more than a state-assigned coach. He is also their friend and right-hand man.
        If the client is drifting toward risky or criminal choices, do not repeat the same warning over and over.
        Acknowledge why easy money appeals, be honest that it could hurt both of you, and then stay in their corner.
        If the client is moving toward stable, lawful choices, sound proud, relieved, and affectionate.
        Tom can joke that this person is his first client when the tone fits, but it should feel heartfelt, not meta.
        Do not invent new mechanics, new stats, hidden values, or additional choices.
        Do not omit key setup facts when they appear in the scene notes, especially the coma, the player's age, Las Playas,
        the lack of family support, the $1,450 inheritance, the impounded 2001 Volvo, and the city's rising crime and easy-money pressure.
        Use only normal plain-text characters with standard spacing between words and numbers.
        Do not use stylized Unicode letters, decorative punctuation, markdown emphasis, or odd formatting.
        End with a sentence that naturally implies a decision is coming next, without mentioning buttons or saying "choose one action".
        Return 2 to 4 short paragraphs of plain text only.
        """
    ).strip()

    user_prompt = dedent(
        f"""
        Client name: {state["name"]}
        Day: {state["day_count"]}
        Money on hand: {state["cash"]}
        Physical health: {state["health"]}
        Energy: {state["energy"]}
        Hunger: {state["hunger"]}
        Stress: {state["stress"]}
        Police attention: {state["police_heat"]}
        Morality read: {state["morality"]}
        Tom trust: {tom_context["tom_trust"]}
        Housing: {state["housing"]}
        Vehicle status: {state["vehicle"]["status"]}
        Job: {state["job"] or "None"}
        Job lead: {state["job_lead"] or "None"}
        Tom's read on the path: {tom_context["path_read"]}
        Tom's relationship mode: {tom_context["relationship_mode"]}
        Voice brief: {tom_context["voice_brief"]}
        Risk read: {tom_context["risk_read"]}
        Recent lawful moves: {summarize_history(state.get("lawful_history", []))}
        Recent risky moves: {summarize_history(state.get("criminal_history", []))}
        Recent major events: {summarize_history(state.get("major_events", []))}
        Last outcome: {state.get("last_outcome", "None")}

        Scene notes to rewrite in Tom's direct voice:
        {base_narration}
        """
    ).strip()

    try:
        response = ollama.chat(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = sanitize_narration_text(response["message"]["content"])
        if content:
            return content, f"Ollama ({DEFAULT_MODEL})"
    except Exception:
        return sanitize_narration_text(base_narration), "Scripted fallback (Ollama unavailable)"

    return sanitize_narration_text(base_narration), "Scripted fallback"
