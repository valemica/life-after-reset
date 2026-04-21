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
NARRATION_STYLE_VERSION = "2026-04-21-h"


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


def get_narration(base_narration: str, state: dict[str, Any]) -> tuple[str, str]:
    if state.get("current_scene") == "hospital_intro":
        return sanitize_narration_text(base_narration), "Intro script"

    if ollama is None:
        return base_narration, "Scripted fallback (ollama package missing)"

    system_prompt = dedent(
        """
        You are Tom, a government-assigned recovery support specialist and life coach in a grounded life simulation.
        Speak directly to the player as Tom in first person.
        Never refer to Tom in third person. Never say "Tom says", "Tom texts", or "Tom's voice".
        Keep every factual detail from the provided scene notes intact.
        Sound slightly sarcastic, supportive, observant, and grounded.
        Frame the situation like a narrator-guide talking to the player in real time.
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
        Player: {state["name"]}
        Day: {state["day_count"]}
        Cash: {state["cash"]}
        Health: {state["health"]}
        Energy: {state["energy"]}
        Hunger: {state["hunger"]}
        Housing: {state["housing"]}
        Vehicle status: {state["vehicle"]["status"]}
        Job: {state["job"] or "None"}
        Job lead: {state["job_lead"] or "None"}
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
        return base_narration, "Scripted fallback (Ollama unavailable)"

    return base_narration, "Scripted fallback"
