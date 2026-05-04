from __future__ import annotations

import json
from typing import Any

from game.state import FINANCIAL_INDEPENDENCE_GOAL, add_event, add_unique_item, normalize_state


def get_scene(state: dict[str, Any]) -> dict[str, Any]:
    normalize_state(state)
    builders = {
        "hospital_intro": build_hospital_intro,
        "discharge_hub": build_discharge_hub,
        "street_hub": build_street_hub,
        "financial_independence_ending": build_financial_independence_ending,
    }
    scene_id = state["current_scene"]
    if scene_id not in builders:
        raise ValueError(f"Unknown scene: {scene_id}")
    return builders[scene_id](state)


def get_scene_signature(state: dict[str, Any]) -> str:
    fingerprint = {
        "scene": state["current_scene"],
        "day_count": state["day_count"],
        "cash": state["cash"],
        "health": state["health"],
        "energy": state["energy"],
        "hunger": state["hunger"],
        "stress": state["stress"],
        "morality": state["morality"],
        "police_heat": state["police_heat"],
        "reputation": state["reputation"],
        "housing": state["housing"],
        "job": state["job"],
        "job_lead": state["job_lead"],
        "vehicle": state["vehicle"],
        "criminal_history": state["criminal_history"],
        "lawful_history": state["lawful_history"],
        "known_npcs": state["known_npcs"],
        "flags": state["active_flags"],
        "last_outcome": state["last_outcome"],
        "game_over": state.get("game_over"),
        "ending_type": state.get("ending_type"),
        "cash_goal": state.get("cash_goal"),
    }
    return json.dumps(fingerprint, sort_keys=True)


def get_tom_alignment(state: dict[str, Any]) -> str:
    lawful_moves = len(state["lawful_history"])
    criminal_moves = len(state["criminal_history"])

    if state["morality"] <= -2 or criminal_moves > lawful_moves:
        return "shady"
    if state["morality"] >= 2 or lawful_moves > criminal_moves:
        return "steady"
    return "mixed"


def get_tom_scene_lines(state: dict[str, Any]) -> tuple[str, str]:
    alignment = get_tom_alignment(state)

    if alignment == "shady":
        support_line = (
            "I get the appeal of fast money in a city like this. I am not going to keep giving you the same lecture, "
            "but I do need to say this once: if you go that way, the fallout can land on both of us."
        )
        next_step_line = (
            "If I cannot talk you out of every bad shortcut, then fine, I am still staying in your corner as your friend. "
            "Just let me help you keep your eyes open about what this could cost."
        )
        return support_line, next_step_line

    if alignment == "steady":
        support_line = (
            "I have to say, watching you lean toward the solid path makes me ridiculously proud. "
            "You are my first client, and somehow you are already making me feel competent."
        )
        next_step_line = (
            "Keep stacking choices like this and you are going to turn into the kind of comeback story I brag about for years."
        )
        return support_line, next_step_line

    support_line = (
        "You are still close enough to either future that I am not making speeches yet. "
        "What matters is that the next move leaves you steadier, safer, and a little harder for this city to knock over."
    )
    next_step_line = (
        "I am here as your coach, your witness, and increasingly the guy who is way too invested in whether you pull this off."
    )
    return support_line, next_step_line


def build_hospital_intro(state: dict[str, Any]) -> dict[str, Any]:
    narration = f"""
Hey. Easy, {state["name"]}. Do not try to sit up too fast unless your plan is to pass out and make this introduction needlessly dramatic. My name's Tom. I am your recovery support specialist, which is the state's painfully official way of saying I am the guy helping you build a life again. You're in Las Playas General Hospital, and you've been in a coma for fifteen years. You're twenty-eight now. 

The bad news? The world kept moving.
The worse news? You don't really have family coming to save you, no close friends on file, and your life is currently being held together by a discharge packet, a motel voucher, and my extremely professional guidance. 
The decent news? Your grandmother left you $1,450. Also a terrible 2001 Volvo, which the city is currently holding hostage for $500.

Las Playas has changed a lot since you've been gone. The streets are rougher, the people are more desperate, and crime is on the rise. If you want to rebuild something real here, you are going to need food, sleep, transport, cash, and better judgment than this city usually rewards. The state has a very official phrase for being "on your own," and because bureaucracy loves a number, Tom's target for you is $100,000 in your account. Get there, and nobody gets to call you a recovery case anymore. That is the situation. You are waking up after fifteen lost years with a little money, a bad car, almost no support, and one actual chance to decide what kind of life you build next.

So let's decide what to do first.
""".strip()

    return {
        "id": "hospital_intro",
        "kicker": "Las Playas General Hospital",
        "title": "Tom's First Briefing",
        "narration": narration,
        "options": [
            {"id": "review_discharge_plan", "label": "Review the discharge plan with Tom"},
            {"id": "ask_for_support", "label": "Ask for a motel voucher and basic support"},
            {"id": "call_impound_lot", "label": "Call the impound lot about the Volvo"},
            {"id": "follow_easy_cash_tip", "label": "Pocket a whispered easy-cash tip from the hallway"},
        ],
    }


def build_discharge_hub(state: dict[str, Any]) -> dict[str, Any]:
    opener_parts = []
    flags = state["active_flags"]
    support_line, next_step_line = get_tom_scene_lines(state)
    alignment = get_tom_alignment(state)

    if flags["reviewed_plan"]:
        opener_parts.append(
            "I've already sketched a recovery checklist on the back of your discharge packet, because apparently I care about structure now."
        )
    if flags["has_voucher"]:
        opener_parts.append(
            "You've got a motel voucher clipped to your paperwork, which is more kindness than Las Playas usually offers in one sitting."
        )
    if flags["called_impound_lot"]:
        opener_parts.append(
            "The impound clerk confirmed the Volvo exists, which is not the comforting sentence it sounds like."
        )
    if flags["quick_cash_contact"]:
        if alignment == "shady":
            opener_parts.append(
                "That folded flyer in your pocket still looks like the kind of shortcut that pays fast and asks questions later, and I can tell you feel the pull."
            )
        else:
            opener_parts.append(
                "That folded flyer in your pocket still looks like the kind of number I would love to keep in the category of bad idea instead of active plan."
            )

    opener = " ".join(opener_parts) or "The room has gone quiet in the way hospitals do when the paperwork starts winning."
    narration = f"""
{opener}

{support_line}

All right. You are being discharged into a city that will not slow down for you, so whatever happens next needs to help with food, shelter, transport, or cash flow. Preferably more than one of those if we can manage it without setting anything on fire. {next_step_line}
""".strip()

    return {
        "id": "discharge_hub",
        "kicker": "Discharge Window",
        "title": "The First Practical Decision",
        "narration": narration,
        "options": [
            {"id": "eat_hospital_meal", "label": "Use the hospital meal voucher before heading out"},
            {"id": "secure_motel_room", "label": "Lock in a motel room for tonight"},
            {"id": "recover_volvo", "label": "Pay $500 to recover the Volvo"},
            {"id": "skip_to_street_hustle", "label": "Ignore the plan and chase money immediately"},
        ],
    }


def build_street_hub(state: dict[str, Any]) -> dict[str, Any]:
    support_line, next_step_line = get_tom_scene_lines(state)

    if state["active_flags"]["car_recovered"]:
        vehicle_line = "Good news. I saw you got your Volvo back. I am using the word 'good' generously, but it does mean you have wheels."
    else:
        vehicle_line = "Bad news first: your Volvo is still in impound, which means the city is charging you for the luxury of being stranded."

    housing_line = f"Right now your housing situation is {state['housing']}."
    lead_line = (
        f"Your best lead is {state['job_lead']}."
        if state["job_lead"]
        else "You still do not have a stable job lead, which I would prefer we fix before Las Playas gets any ideas."
    )

    pressure_line = (
        "And that patrol car drifting by is a useful reminder that trouble is already close enough to smell."
        if state["police_heat"] > 0
        else "For the moment, nobody in this city is watching you too closely, and I would love to keep it that way."
    )

    narration = f"""
You made it out into Las Playas. {vehicle_line}

{housing_line} {lead_line}

{support_line} {next_step_line} {pressure_line}
""".strip()

    transport_label = "Put gas in the Volvo and keep moving" if state["active_flags"]["car_recovered"] else "Pay to recover the Volvo now"
    work_label = "Visit the workforce office for a job lead" if not state["job_lead"] else "Show up for the warehouse screening"
    hustle_label = "Run a shady delivery for quick cash" if state["active_flags"]["quick_cash_contact"] else "Text the easy-cash number"

    return {
        "id": "street_hub",
        "kicker": "Day-to-Day Survival",
        "title": "Las Playas, Day One and Beyond",
        "narration": narration,
        "options": [
            {"id": "visit_job_center", "label": work_label},
            {"id": "buy_hot_meal", "label": "Buy a hot meal from the corner deli for $14"},
            {"id": "manage_transport", "label": transport_label},
            {"id": "quick_cash_move", "label": hustle_label},
        ],
    }


def build_financial_independence_ending(state: dict[str, Any]) -> dict[str, Any]:
    alignment = get_tom_alignment(state)

    if alignment == "steady":
        narration = f"""
Look at that account balance, {state["name"]}. One hundred thousand dollars. The state can call it financial independence, the forms can call it a successful recovery outcome, and I can call it what it is: you becoming a good citizen in a city that did not make that easy.

I am proud of you. Really proud. You woke up with almost nothing but a hospital bracelet, a bad car, and me talking too much, and you built enough stability to stand on your own. This is where I say goodbye as your assigned support specialist. As your friend, I am still rooting for you.
""".strip()
        title = "Tom's Proud Goodbye"
    else:
        narration = f"""
Well. This is not exactly the path I would have planned for you, {state["name"]}, and I am choosing my words carefully because I know you can see my face right now.

But you got one hundred thousand dollars in your account, my friend. That was the line Tom, the state, and all the paperwork treated as proof that you could be on your own. So this is where I say goodbye. You got this. Just try to stay alive, enjoy the life you fought your way back into, and maybe do not make me regret believing in you.
""".strip()
        title = "Tom Lets You Go"

    return {
        "id": "financial_independence_ending",
        "kicker": "Financial Independence",
        "title": title,
        "narration": narration,
        "options": [],
    }


def apply_choice(state: dict[str, Any], choice_id: str) -> None:
    handlers = {
        "review_discharge_plan": handle_review_discharge_plan,
        "ask_for_support": handle_ask_for_support,
        "call_impound_lot": handle_call_impound_lot,
        "follow_easy_cash_tip": handle_follow_easy_cash_tip,
        "eat_hospital_meal": handle_eat_hospital_meal,
        "secure_motel_room": handle_secure_motel_room,
        "recover_volvo": handle_recover_volvo,
        "skip_to_street_hustle": handle_skip_to_street_hustle,
        "visit_job_center": handle_visit_job_center,
        "buy_hot_meal": handle_buy_hot_meal,
        "manage_transport": handle_manage_transport,
        "quick_cash_move": handle_quick_cash_move,
    }

    if choice_id not in handlers:
        raise ValueError(f"Unsupported choice: {choice_id}")

    handlers[choice_id](state)
    state["turn_count"] += 1
    normalize_state(state)
    maybe_finish_game(state)


def maybe_finish_game(state: dict[str, Any]) -> None:
    if state.get("game_over"):
        return

    goal = int(state.get("cash_goal", FINANCIAL_INDEPENDENCE_GOAL))
    if state["cash"] < goal:
        return

    alignment = get_tom_alignment(state)
    state["game_over"] = True
    state["ending_type"] = "good_citizen" if alignment == "steady" else "unexpected_independence"
    state["current_scene"] = "financial_independence_ending"
    state["current_phase"] = "ending"
    add_event(state["major_events"], f"Reached ${goal:,} and earned financial independence.")
    state["last_outcome"] = (
        f"You reached ${goal:,}. Tom's official job is done, and your life is finally yours to keep."
    )


def handle_review_discharge_plan(state: dict[str, Any]) -> None:
    state["active_flags"]["reviewed_plan"] = True
    state["current_scene"] = "discharge_hub"
    state["current_phase"] = "discharge"
    state["stress"] -= 8
    state["energy"] -= 2
    state["morality"] += 1
    state["known_npcs"]["Tom"]["trust"] += 1
    add_unique_item(state["inventory"], "Tom's handwritten recovery checklist")
    add_event(state["lawful_history"], "Reviewed the hospital discharge plan instead of winging it.")
    add_event(state["major_events"], "Sat down with Tom and mapped out the first steps after discharge.")
    state["last_outcome"] = (
        "You let Tom walk you through the practical reality: food, shelter, transport, and how not to blow your first day."
    )


def handle_ask_for_support(state: dict[str, Any]) -> None:
    state["active_flags"]["has_voucher"] = True
    state["current_scene"] = "discharge_hub"
    state["current_phase"] = "discharge"
    state["stress"] -= 6
    state["reputation"] += 1
    add_unique_item(state["inventory"], "state motel voucher")
    add_unique_item(state["inventory"], "city bus pass")
    add_event(state["lawful_history"], "Accepted formal support services on day one.")
    add_event(state["major_events"], "Asked the hospital for discharge support and got a voucher packet.")
    state["last_outcome"] = (
        "Tom gets a social worker moving, and within minutes you have a motel voucher and a bus pass instead of just anxiety."
    )


def handle_call_impound_lot(state: dict[str, Any]) -> None:
    state["active_flags"]["called_impound_lot"] = True
    state["current_scene"] = "discharge_hub"
    state["current_phase"] = "discharge"
    state["stress"] += 2
    add_unique_item(state["inventory"], "impound release form")
    add_event(state["major_events"], "Called the impound lot and confirmed the Volvo can be released for $500.")
    state["last_outcome"] = (
        "The clerk confirms the Volvo is real, ugly, and available the second you hand over five hundred dollars."
    )


def handle_follow_easy_cash_tip(state: dict[str, Any]) -> None:
    state["active_flags"]["quick_cash_contact"] = True
    state["current_scene"] = "discharge_hub"
    state["current_phase"] = "discharge"
    state["stress"] += 4
    state["morality"] -= 2
    state["police_heat"] += 1
    add_unique_item(state["inventory"], "folded easy-cash flyer")
    add_event(state["criminal_history"], "Took contact information for a suspicious fast-cash opportunity.")
    add_event(state["major_events"], "Left the room with a number Tom would absolutely hate.")
    state["last_outcome"] = (
        "A hallway whisper turns into a folded flyer in your hand, and Tom notices just enough to look worried."
    )


def handle_eat_hospital_meal(state: dict[str, Any]) -> None:
    state["current_scene"] = "street_hub"
    state["current_phase"] = "survival"
    state["hunger"] -= 20
    state["energy"] += 8
    state["stress"] -= 3
    state["housing"] = "voucher packet in hand"
    add_event(state["major_events"], "Ate before discharge and left the hospital less desperate.")
    state["last_outcome"] = (
        "You eat something warm before leaving, which is not glamorous but does make the world feel slightly less hostile."
    )


def handle_secure_motel_room(state: dict[str, Any]) -> None:
    state["current_scene"] = "street_hub"
    state["current_phase"] = "survival"
    state["housing"] = "motel room on Grand Avenue"
    state["stress"] -= 10
    state["energy"] += 6
    state["active_flags"]["has_voucher"] = True
    state["active_flags"]["checked_into_motel"] = True
    add_unique_item(state["inventory"], "motel room key")
    add_event(state["lawful_history"], "Secured housing before wandering into the city.")
    add_event(state["major_events"], "Checked into a motel room for the first night out of the hospital.")
    state["last_outcome"] = (
        "Tom helps you turn paperwork into an actual room, which means tonight you have a door that locks."
    )


def handle_recover_volvo(state: dict[str, Any]) -> None:
    state["current_scene"] = "street_hub"
    state["current_phase"] = "survival"
    if state["cash"] >= state["vehicle"]["recovery_cost"] and not state["active_flags"]["car_recovered"]:
        state["cash"] -= state["vehicle"]["recovery_cost"]
        state["vehicle"]["status"] = "recovered"
        state["active_flags"]["car_recovered"] = True
        state["stress"] -= 4
        add_unique_item(state["inventory"], "Volvo keys")
        add_event(state["lawful_history"], "Paid the impound fee and legally recovered the car.")
        add_event(state["major_events"], "Recovered the 2001 Volvo from impound.")
        state["last_outcome"] = (
            "Five hundred dollars hurts, but the Volvo is yours again, which is more freedom than you had an hour ago."
        )
    elif state["active_flags"]["car_recovered"]:
        state["last_outcome"] = "The Volvo is already back in your possession, along with all of its personality defects."
    else:
        state["stress"] += 5
        state["last_outcome"] = "You cannot recover the car yet. Las Playas remains committed to charging people for being stranded."


def handle_skip_to_street_hustle(state: dict[str, Any]) -> None:
    state["current_scene"] = "street_hub"
    state["current_phase"] = "survival"
    state["cash"] += 80
    state["stress"] += 10
    state["morality"] -= 2
    state["police_heat"] += 1
    add_event(state["criminal_history"], "Skipped safe planning to chase immediate money.")
    add_event(state["major_events"], "Walked out of the hospital ready to hustle before stabilizing.")
    state["last_outcome"] = (
        "You move before the plan is ready, pick up quick cash, and immediately feel how thin the line is between momentum and trouble."
    )


def handle_visit_job_center(state: dict[str, Any]) -> None:
    state["current_scene"] = "street_hub"
    state["current_phase"] = "survival"
    state["day_count"] += 1
    state["energy"] -= 6
    state["hunger"] += 8

    if not state["active_flags"]["job_center_visited"]:
        state["active_flags"]["job_center_visited"] = True
        state["job_lead"] = "warehouse screening tomorrow at 8:00 AM"
        state["morality"] += 1
        state["stress"] -= 4
        add_unique_item(state["inventory"], "warehouse referral slip")
        add_event(state["lawful_history"], "Visited the workforce office for legitimate work.")
        add_event(state["major_events"], "Picked up a warehouse screening lead from the workforce office.")
        state["last_outcome"] = (
            "The workforce office is fluorescent and deeply depressing, but you leave with a real lead and a time to show up."
        )
        return

    state["job"] = "warehouse temp shift"
    state["cash"] += 90
    state["reputation"] += 2
    state["morality"] += 1
    state["energy"] -= 9
    state["hunger"] += 6
    state["active_flags"]["worked_shift"] = True
    add_event(state["lawful_history"], "Worked a legal shift to stabilize income.")
    add_event(state["major_events"], "Completed a warehouse temp shift and got paid.")
    state["last_outcome"] = (
        "You drag yourself through a warehouse shift, earn honest money, and feel the strange dignity of surviving the boring way."
    )


def handle_buy_hot_meal(state: dict[str, Any]) -> None:
    state["current_scene"] = "street_hub"
    state["current_phase"] = "survival"
    state["day_count"] += 1

    if state["cash"] >= 14:
        state["cash"] -= 14
        state["hunger"] -= 25
        state["energy"] += 5
        state["stress"] -= 2
        add_event(state["major_events"], "Spent money on a hot meal instead of pushing through hunger.")
        state["last_outcome"] = (
            "The deli coffee is dangerous and the soup tastes like survival, but the meal steadies you."
        )
    else:
        state["stress"] += 5
        state["hunger"] += 6
        state["last_outcome"] = (
            "You count your money twice, come up short on confidence both times, and leave the deli still hungry."
        )


def handle_manage_transport(state: dict[str, Any]) -> None:
    state["current_scene"] = "street_hub"
    state["current_phase"] = "survival"
    state["day_count"] += 1

    if not state["active_flags"]["car_recovered"]:
        if state["cash"] >= state["vehicle"]["recovery_cost"]:
            state["cash"] -= state["vehicle"]["recovery_cost"]
            state["vehicle"]["status"] = "recovered"
            state["active_flags"]["car_recovered"] = True
            state["stress"] -= 4
            add_unique_item(state["inventory"], "Volvo keys")
            add_event(state["lawful_history"], "Recovered the car as part of getting stable.")
            add_event(state["major_events"], "Recovered the Volvo during the first week out of the hospital.")
            state["last_outcome"] = (
                "You bite the bullet, pay the impound fee, and reclaim a car that looks exhausted but still gives you options."
            )
        else:
            state["stress"] += 4
            state["last_outcome"] = "The Volvo stays behind the fence another day because the money just is not there."
        return

    if state["cash"] >= 8:
        state["cash"] -= 8
        state["vehicle"]["fuel"] += 18
        state["energy"] += 2
        add_event(state["major_events"], "Kept the Volvo alive with a little gas money.")
        state["last_outcome"] = (
            "Eight dollars of gas buys you a little range, a little confidence, and one more day of pretending the Volvo is reliable."
        )
    else:
        state["stress"] += 3
        state["last_outcome"] = "You tap the dashboard like encouragement counts as fuel. The Volvo remains unconvinced."


def handle_quick_cash_move(state: dict[str, Any]) -> None:
    state["current_scene"] = "street_hub"
    state["current_phase"] = "survival"
    state["day_count"] += 1
    state["cash"] += 110
    state["stress"] += 7
    state["morality"] -= 2
    state["police_heat"] += 2
    state["hunger"] += 4
    state["active_flags"]["quick_cash_contact"] = True
    add_event(state["criminal_history"], "Took a shady delivery for fast money.")
    add_event(state["major_events"], "Ran a quick-cash errand that paid immediately and felt worse afterward.")
    state["last_outcome"] = (
        "The cash is real, the instructions are vague, and the whole job leaves you with the kind of nerves Tom warned you about."
    )
