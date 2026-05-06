# Life After Reset Project Report

## Project Overview

**Life After Reset** is an AI-powered life simulation game built with Python, Streamlit, and Ollama. The player wakes up in Las Playas General Hospital after being in a coma for fifteen years. The player is now twenty-eight years old and has to rebuild their life with limited money, almost no support system, an impounded 2001 Volvo S60, and a government-assigned recovery support specialist named Tom.

The game is designed around survival, financial recovery, morality, and consequence-based decision making. The player’s long-term goal is to reach $100,000 and become financially independent. Along the way, the player must manage basic needs such as hunger, health, and money. The player can choose a legal path, a risky criminal path, or a mixed path. These choices affect the player’s cash, morality, police heat, reputation, job progress, relationship with Tom, and final ending.

The project uses AI methods to generate dynamic interactive scenes. Instead of relying only on fixed scripted text, the game uses an LLM through Ollama to generate Tom’s narration and the player’s next possible choices based on the current game state. The AI is not just generating random story text. It receives structured information about the player’s current condition, recent actions, inventory, legal/criminal history, Tom’s memory, current risks, and available facts. The output is required to be valid JSON so the game can safely convert it into playable choices.

The main purpose of this project is to demonstrate how an AI system can be used inside a working interactive game. The project connects AI-generated storytelling with traditional game systems such as state management, resources, consequences, branching paths, and a user interface.

---

# 1. Base System Functionality

## 1.1 Description of the Working System

The base system runs as a Streamlit application. The player starts at a title screen, enters a player name, and begins the game from the hospital intro scene. The system creates a player state and stores it in Streamlit session state. From there, the game displays Tom’s narration, player stats, inventory, and exactly four clickable choices per turn.

The game follows this basic loop:

1. The player starts a new game by entering a name.
2. The game creates a new player state.
3. The engine loads the current scene.
4. If the scene is dynamic, the AI scene generator builds a new scene using the current state.
5. Tom’s narration and four choices are displayed in the Streamlit UI.
6. The player selects a choice.
7. The engine applies the consequence of that choice.
8. The player state updates.
9. The next scene is generated based on the updated state.
10. The loop continues until the player reaches the $100,000 goal or quits.

This demonstrates a working AI-based system because the game is not only showing static text. It uses the player’s changing state to influence future AI narration and choices.

## 1.2 Core Gameplay Features

The current playable system includes the following features:

- Player name entry
- Hospital intro scene
- Streamlit terminal-style interface
- Tom as an AI-guided support specialist
- AI-generated post-hospital scenes
- Exactly four player choices each turn
- Player state tracking
- Inventory tracking
- Save game support
- Quit game support
- Hunger system
- Health system
- Stress system
- Police heat system
- Morality system
- Legal work path
- Criminal quick-cash path
- Transportation system using the 2001 Volvo
- Housing support and motel voucher system
- Food menu and hunger emergency system
- Tom memory
- Choice history
- Major event history
- Legal and criminal history
- $100,000 financial independence goal
- Different ending tone depending on the player’s path

## 1.3 List of Scenarios the AI System Can Handle

The following are the main scenarios that the system is currently capable of handling.

### Scenario 1: Starting a New Game

The player enters a name on the start screen. The system validates that the name is not empty. Once submitted, the system creates a new player state with starting values such as age, cash, health, hunger, stress, housing, vehicle status, inventory, and current scene.

The starting conditions include:

- Age: 28
- Cash: $1,450
- Financial goal: $100,000
- Health: 85
- Energy: 70
- Hunger: 70
- Stress: 40
- Housing: discharge pending
- Vehicle: 2001 Volvo S60, impounded
- Starting inventory:
  - hospital discharge papers
  - late grandma's envelope
  - cheap smartphone
  - wallet and ID
  - basic clothes

This scenario shows basic system functionality because the player can begin a complete interactive run.

### Scenario 2: Receiving the Hospital Introduction

The first scene introduces the player to Tom, the recovery support specialist. Tom explains that the player has been in a coma for fifteen years, has very limited support, owns a bad car that is currently impounded, and must rebuild life in Las Playas.

The player is given four opening options:

1. Review the discharge plan with Tom
2. Ask for a motel voucher and basic support
3. Call the impound lot about the Volvo
4. Pocket a whispered easy-cash tip from the hallway

This scenario establishes the game world, the player’s situation, and the first meaningful moral choice.

### Scenario 3: Reviewing the Discharge Plan

If the player reviews the discharge plan, the system marks the plan as reviewed, reduces stress, slightly reduces energy, increases morality, increases Tom’s trust, adds a handwritten recovery checklist to inventory, and records the action in lawful history and major events.

This scenario demonstrates that choices have consequences beyond text. The game updates hidden and visible state values.

### Scenario 4: Asking for Support

If the player asks for support, the system gives the player formal support resources such as a motel voucher and city bus pass. This reduces stress and increases reputation. The player’s inventory and lawful history are updated.

This scenario handles a social support path where the player accepts help instead of trying to survive alone.

### Scenario 5: Calling the Impound Lot

The player can contact the impound lot to learn that the Volvo can be released for $500. This updates the active flag showing that the impound lot has been called and gives the player information needed for a future transportation decision.

This scenario demonstrates continuity because the system remembers that the player already confirmed the vehicle release cost.

### Scenario 6: Recovering the Volvo

If the player has enough money, the player can spend $500 to recover the 2001 Volvo S60. The car status changes from impounded to recovered, the player receives Volvo keys, and the game updates the car recovery flag.

This scenario demonstrates a transportation system, money management, and long-term consequences. Having a car affects future AI-generated options because the prompt tells the model whether the car is recovered and how much fuel it has.

### Scenario 7: Securing Housing

If the player has a voucher or support paperwork, the player can secure a motel room. The game updates housing to a motel room, adds a motel room key to inventory, reduces stress, increases energy, and records the event.

If the player does not already have a voucher, the system can still create a housing support path by adding a housing intake slip and making future housing more possible.

This scenario handles shelter and stability as part of the survival simulation.

### Scenario 8: Eating Food and Managing Hunger

The game includes a hunger system. Hunger is treated as a “fed meter,” where 100 means full and 0 means a medical emergency. Food choices can restore hunger and energy, but cost money.

The game includes several food tiers:

- Cheap snack
- Deli meal
- Full hot meal
- Recovery feast

Each food option has a hunger gain and price range. Food prices are calculated based on the player’s progress toward the $100,000 goal. This means the economy can scale as the player becomes more financially stable.

This scenario demonstrates a resource management mechanic connected to AI-generated choices.

### Scenario 9: Low Hunger Priority

If hunger drops to 50 or below, the AI scene generator does not continue with normal scene generation. Instead, it prioritizes food. If the food menu is open, the game shows actual food options. If not, Tom pushes the player to eat before the situation becomes dangerous.

If hunger drops to 10 or below, Tom directly warns the player that eating is urgent. If hunger reaches 0, the player collapses and is sent back to the hospital. The system charges the player 10% of current cash, reduces health, increases stress, resets hunger to 25, and records the hospital event.

This scenario is important because it shows that the game has rule-based safety checks around AI generation. The AI does not get to ignore a medical emergency.

### Scenario 10: Legal Work Path

The player can pursue legal work through the workforce office. The legal work path starts with an entry-level shift lead and can progress through several stages:

1. Entry-level shift screening
2. Warehouse temp shift
3. Reliable shift lead track
4. Assistant supervisor training
5. Operations supervisor role
6. Small logistics contract

Legal work pays less than crime but lowers police heat, improves morality, improves reputation, and can lead to bonuses. Every three legal work actions, the player can receive a legal reliability bonus.

This scenario demonstrates laddered progression and long-term planning. The more the player chooses legal work, the more the AI is instructed to offer legal promotions and stability-based choices.

### Scenario 11: Quick Cash / Criminal Path

The player can pursue shady quick-cash choices through an easy-money contact. The criminal path pays four times more than comparable legal work, but it increases stress, lowers morality, raises police heat, and can eventually trigger arrest consequences.

The criminal path also has progression levels:

1. Easy-money callback
2. Cash handoff runner
3. Package route regular
4. Crew dispatcher
5. High-risk stash movement
6. Five-grand criminal score

This scenario demonstrates risk and reward. The criminal path creates faster progress toward the money goal but increases danger and can lead to losing money through police release fees.

### Scenario 12: Police Heat and Arrest

The system tracks police heat. Each criminal action increases police heat. If police heat reaches the arrest threshold, the player gets caught, sent to jail for processing, and charged a 30% release fee from current cash. After arrest, police heat is reduced but not fully cleared.

This creates meaningful consequences for repeated crime. The game does not simply punish one bad choice instantly. It allows risk to build over time, which makes the system feel more realistic.

### Scenario 13: Rest and Medical Follow-Up

The player can rest or seek medical follow-up. Rest increases energy, improves health, and lowers stress, but it costs a day and reduces hunger. Medical follow-up improves health and reduces stress while adding a clinic follow-up card to inventory.

These scenarios show that not every useful action is about earning money. Survival and recovery also matter.

### Scenario 14: Social Support

The player can ask support services or the county benefits desk for help. This lowers stress, increases reputation, increases Tom’s trust, and can create support resources such as vouchers or service contacts.

This scenario helps the game support a realistic recovery path where the player uses community resources instead of only working or committing crime.

### Scenario 15: Budget Planning

The player can make a budget with Tom. This lowers stress, increases morality, increases Tom’s trust, adds a rough budget plan to inventory, and records progress toward the $100,000 goal.

This scenario demonstrates planning behavior inside the game world. The action itself does not create money immediately, but it improves stability and supports long-term decision making.

### Scenario 16: Dynamic AI Scene Generation

After the fixed intro and hub scenes, the AI system generates new scenes based on the current player state. The generated scene includes:

- A short kicker/location
- A title
- Tom’s narration
- Exactly four options
- Each option’s action type
- Evidence showing that the option is grounded in the narration

This scenario is the main AI-driven feature of the project.

### Scenario 17: Save Game

The player can save the game. The system writes the current state to a JSON file in a saves folder. The save file includes the player’s current state and a timestamp.

This scenario supports persistence and shows that the game state is serializable.

### Scenario 18: Quit Game

The player can quit the game from the sidebar. The system closes the current session and returns the player to the start screen.

This scenario supports complete gameplay flow from start to exit.

### Scenario 19: Financial Independence Ending

If the player reaches $100,000, the game ends. The ending depends on the player’s alignment. If the player mostly followed a steady legal path, Tom gives a proud and positive goodbye. If the player reached the goal through a more questionable path, Tom still acknowledges the achievement but with concern.

This scenario demonstrates branching endings based on accumulated player behavior.

---

# 2. Prompt Engineering and Model Parameter Choice

## 2.1 How Prompt Engineering Is Used

Prompt engineering is one of the most important AI methods in this project. The system does not simply ask the model to “continue the story.” Instead, it gives the model a detailed system prompt that defines the model’s role, output format, tone, rules, constraints, and allowed action types.

The AI is prompted to act as Tom, the player’s government-assigned recovery support specialist. This role-based prompt keeps the narration consistent. Tom is not just a narrator. He is part of the game world, and his voice changes depending on the player’s choices.

The system prompt tells the model to return valid JSON only. This is important because the output must be used by the game engine. If the model returned unstructured prose, the game would not know how to create buttons or apply consequences. By requiring JSON, the system turns the LLM into a structured scene generator.

The expected JSON shape is:

```json
{
  "kicker": "short location or situation",
  "title": "short scene title",
  "narration": "Tom speaks directly to the player in first person, 1 or 2 compact paragraphs.",
  "options": [
    {
      "label": "player-facing action under 70 characters",
      "action_type": "one allowed action type",
      "evidence": "exact phrase from narration that makes this option available"
    }
  ]
}
```

This prompt is effective because it gives the model clear rules:

- Generate exactly four options.
- Keep Tom speaking in first person.
- React to the last outcome.
- Avoid repeating recent wording.
- Ground every choice in the narration.
- Use only allowed action types.
- Mention risky choices before offering them.
- Prioritize food when hunger is dangerous.
- Offer more legal choices if the player keeps choosing legal work.
- Offer more criminal choices if the player keeps choosing quick cash.
- Make police heat risk obvious when crime is involved.

This is strong prompt engineering because it controls both creative style and game logic.

## 2.2 Role-Based Prompting

The system prompt uses role-based prompting by telling the LLM:

"You generate the next moment of a life simulation as Tom, the player's government-assigned recovery support specialist."

This helps the model maintain a consistent identity. Tom’s role is important because he provides emotional continuity. He sounds supportive, sarcastic, worried, proud, or disappointed depending on the player’s decisions.

Role-based prompting improves the game because the player does not feel like they are receiving generic AI text. They feel like they are interacting with a specific NPC who remembers them.

## 2.3 Structured Output Prompting

The prompt requires valid JSON and uses Ollama’s JSON format mode:

```python
response = ollama.chat(
    model=DEFAULT_MODEL,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ],
    format="json",
)
```

This is a model parameter choice because `format="json"` forces the model toward structured output. This is especially important in a game because the response has to be machine-readable. The game engine must be able to parse the narration, choices, action types, and evidence fields.

The system also validates the JSON after receiving it. If the response is invalid, unsafe, missing fields, repeated, or not grounded, the system uses a fallback scene instead of crashing.

## 2.4 Context Prompting

The user prompt is built from the current player state. It includes:

- Player name
- Day count
- Money
- Financial goal
- Health
- Hunger
- Police attention
- Morality
- Housing
- Vehicle status
- Job
- Job lead
- Legal progress level
- Shady progress level
- Legal streak
- Crime streak
- Arrest count
- Last selected option
- Last selected action type
- Inventory
- Tom’s read on the player
- Tom relationship mode
- Risk read
- Known facts
- Recent lawful moves
- Recent risky moves
- Recent major events
- Recently selected choices
- Recently shown options
- Last outcome
- Recent Tom narration memory
- Scripted fallback narration for continuity

This is important because the AI does not have true memory on its own. The game gives the AI the memory it needs through the prompt. This makes the system more coherent because the model can respond to what just happened instead of generating disconnected scenes.

## 2.5 Prompt Used for Scenario Handling

The most important prompt is the dynamic scene generation prompt. The following is a simplified version of the prompt used by the system:

```markdown
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
- Start by reacting to what just happened if there is a last outcome.
- Tom should sound like he remembers the previous choice.
- Do not repeat recent Tom wording.
- Every option must be grounded in player knowledge.
- A choice is valid only if the narration directly mentions the opportunity in the evidence phrase, or the opportunity is already listed in known facts.
- The evidence field must be an exact substring from the narration.
- Hunger is a fed meter: 100 means full and 0 means a hospital-level hunger emergency.
- If hunger is 10 or below, Tom must directly tell the player to eat something before they collapse.
- If the player keeps choosing legal_work, offer laddered legal progress.
- If the player keeps choosing quick_cash, offer laddered criminal progress while making the risk clear.
- Use only the allowed action_type values.
```

This prompt directly supports multiple scenarios, including:

- Legal work progression
- Criminal quick-cash escalation
- Hunger emergencies
- Transportation decisions
- Housing decisions
- Social support
- Budget planning
- Medical follow-up
- Rest and recovery

## 2.6 Model Parameter Choices

The current project uses Ollama as the local LLM provider. The visible scene generation code uses:

- `model=DEFAULT_MODEL`
- `format="json"`

The most important parameter choice in the current implementation is `format="json"`. This is used because the game needs predictable structured output. The model must return a JSON object instead of free-form text so the system can validate it and convert it into playable buttons.

The project also uses fallback scenes when the model is unavailable or returns invalid output. This design choice improves reliability because the game can continue even if the AI call fails.

For future tuning, I would use the following parameter values:

```python
options={
    "temperature": 0.7,
    "num_predict": 500
}
```

The reason for a medium temperature such as `0.7` is that the game needs creativity, but not complete randomness. A temperature that is too low could make the scenes repetitive. A temperature that is too high could make the model ignore rules, invent unsupported facts, or create inconsistent choices.

The reason for a moderate output limit such as `num_predict=500` is that Tom's narration should be detailed enough to feel like storytelling, but short enough to fit the Streamlit interface and avoid overly long turns.

The current implementation already controls output length through the prompt by asking for "1 or 2 compact paragraphs” and “player-facing action under 70 characters." This means the prompt itself is also acting as a parameter-like control over output size.

---

# 3. Tools Usage

## 3.1 Tool Usage in the Project

The project demonstrates tool usage by connecting the AI system to several Python-based tools and game systems. The LLM does not directly change the player state. Instead, it produces a structured action type, and the game engine routes that action type to the correct Python function.

This is similar to tool calling because the model selects from allowed action types, and the engine executes the matching function. The allowed action types are:

```python
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
```

The AI chooses what kind of action is appropriate, but the actual game logic is handled by deterministic Python functions. This is a safer design than letting the model directly edit the game state.

## 3.2 Python Functions as Tools

Each action type maps to a game function. For example:

- `legal_work` maps to `apply_legal_work_choice`
- `quick_cash` maps to `apply_quick_cash_choice`
- `food` maps to `apply_food_choice`
- `housing` maps to `apply_housing_choice`
- `transport` maps to `apply_transport_choice`
- `rest` maps to `apply_rest_choice`
- `social_support` maps to `apply_social_support_choice`
- `medical_followup` maps to `apply_medical_followup_choice`
- `budget_plan` maps to `apply_budget_plan_choice`

The AI does not decide exact cash changes, hunger changes, or police heat changes. It only chooses the category of action. The Python engine applies the real consequence.

This is important because it keeps the game fair and consistent. The LLM can be creative with narration, but the rules are controlled by code.

## 3.3 Economy Tool

The `economy.py` file works like a support tool for food and money formatting. It includes functions such as:

- `normalize_money`
- `format_money`
- `get_goal_progress_ratio`
- `get_food_price_factor`
- `calculate_food_price`
- `build_food_menu`

The food menu system creates food options dynamically. The prices are based on the player’s financial progress, which means the game economy changes as the player becomes wealthier.

For example, the food tiers include:

```python
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
```

This counts as tool usage because the AI scene generator can trigger food-related choices, and the game uses a separate economy module to calculate valid food options.

## 3.4 Save System Tool

The save system writes the current player state to a JSON file. This gives the project persistence. The game can serialize complex state, including inventory, current scene, last outcome, major events, legal history, criminal history, and Tom memory.

The save function creates a save directory if needed and writes a file using the player’s name:

```python
save_path = SAVE_DIR / f"{slugify(state['name'])}_latest.json"
```

This supports the rubric because it shows integration with file system tools and environment management.

## 3.5 Streamlit as a UI Tool

Streamlit is used as the user interface framework. It handles:

- Page configuration
- Start screen
- Text input
- Buttons
- Sidebar
- Stats display
- Inventory display
- Save and quit buttons
- Scene rendering
- Choice layout

The project uses custom CSS to create a terminal-style interface. This makes the game feel more polished and gives it a stronger identity.

## 3.6 Ollama as the AI Tool

Ollama is used to run the local LLM. This is important because the project does not depend on a cloud API for its core AI generation. The game can call a local model through Ollama and receive structured JSON output.

This supports LO2 because the project integrates Python with an AI ecosystem tool.

---

# 4. Planning and Reasoning

## 4.1 Multi-Step Reasoning in the Game

The project demonstrates planning and reasoning through the way it manages long-term consequences. Each player choice affects the next state, and the next state affects future AI-generated scenes.

The system does not treat each turn as isolated. It uses memory and state values to reason about what should happen next. For example:

- If the player chooses legal work repeatedly, the system increases legal progress.
- If the player chooses quick cash repeatedly, the system increases shady progress and police heat.
- If the player ignores hunger, the system pushes food options.
- If hunger reaches 0, the system triggers a hospital consequence.
- If police heat gets too high, the system triggers arrest and a release fee.
- If the player reaches $100,000, the system ends the game.
- If the player’s morality is higher, Tom reacts more proudly.
- If the player’s morality is lower, Tom becomes more concerned.

This creates a cause-and-effect structure that feels like planning.

## 4.2 The Player State as the Reasoning Base

The player state is the central reasoning structure. It stores the current facts of the game world. Important fields include:

```python
"name"
"age"
"cash"
"cash_goal"
"health"
"energy"
"hunger"
"stress"
"morality"
"police_heat"
"reputation"
"job"
"job_lead"
"housing"
"day_count"
"turn_count"
"current_phase"
"current_scene"
"last_outcome"
"vehicle"
"inventory"
"major_events"
"criminal_history"
"lawful_history"
"known_npcs"
"active_flags"
```

The game uses this information to decide what scenes are valid, what options should appear, and what consequences should happen.

## 4.3 Legal Path Planning

The legal path is planned as a ladder. The player does not immediately become financially independent. Instead, the system moves the player through increasingly better legal opportunities.

The legal titles are:

```python
LEGAL_TITLES = [
    "entry-level shift screening this week",
    "warehouse temp shift",
    "reliable shift lead track",
    "assistant supervisor training",
    "operations supervisor role",
    "small logistics contract",
]
```

The legal payouts are:

```python
LEGAL_PAYOUTS = [100, 250, 600, 1200, 2400, 4500]
```

This shows planning because the player’s current legal level determines the next legal opportunity. The system also rewards consistency with legal bonuses every three legal actions.

## 4.4 Criminal Path Planning

The criminal path is also planned as a ladder. The player starts with smaller shady actions and can move toward larger criminal opportunities.

The shady titles are:

```python
SHADY_TITLES = [
    "easy-money callback",
    "cash handoff runner",
    "package route regular",
    "crew dispatcher",
    "high-risk stash movement",
    "five-grand criminal score",
]
```

Crime pays four times more than legal work:

```python
def get_crime_payout(level: int) -> int:
    return get_legal_payout(level) * 4
```

However, repeated crime increases police heat and can trigger a 30% release fee. This creates a planning tradeoff. The player can earn money faster but risks losing a large amount of money and increasing stress.

## 4.5 Planning Around Hunger

Hunger creates short-term planning pressure. Legal work and crime can help the player earn money, but they also reduce hunger and energy. If the player focuses only on money, hunger can become dangerous.

The game uses special logic when hunger gets low:

- Hunger at 50 or below creates a food-priority scene.
- Hunger at 10 or below makes Tom directly warn the player.
- Hunger at 0 triggers collapse, hospital treatment, a cash penalty, health loss, and stress gain.

This improves gameplay because the player must balance long-term money goals with short-term survival.

## 4.6 Planning Around Police Heat

Police heat creates delayed consequences. The player is not punished immediately for one risky choice. Instead, repeated criminal choices increase heat. The arrest threshold depends on the current crime level and arrest count. If the threshold is reached, the player pays a release fee equal to 30% of current cash.

This creates a realistic planning problem because the player must decide whether fast money is worth long-term risk.

## 4.7 AI Reasoning Through Prompt Context

The AI receives a context-rich user prompt every time a dynamic scene is generated. This allows the model to reason about the player’s situation before generating options.

For example, the AI sees:

```markdown
Money: $...
Goal: $100,000
Health: ...
Hunger/fed meter: ...
Police attention: ...
Morality read: ...
Housing: ...
Vehicle: ...
Job lead: ...
Legal progress level: ...
Shady progress level: ...
Legal streak: ...
Crime streak: ...
Last selected option: ...
Last outcome: ...
Recent lawful moves: ...
Recent risky moves: ...
Recent major events: ...
Recent Tom narration memory: ...
```

This is not hidden chain-of-thought output, but it is a form of structured reasoning support. The AI is given the information needed to make a better next-scene decision.

## 4.8 Conversation Coherence

The project improves conversation coherence in several ways:

1. It stores the last outcome.
2. It stores recent choices.
3. It stores recently offered options.
4. It stores Tom memory.
5. It includes known facts in the prompt.
6. It validates that generated options are grounded in the narration.
7. It rejects repeated labels.
8. It uses fallback scenes if the AI output is invalid.

This helps prevent common AI issues such as:

- Forgetting what just happened
- Repeating the same options
- Inventing unsupported locations or items
- Offering choices that are not connected to the narration
- Generating unplayable output

---

# 5. RAG Implementation

## 5.1 How RAG Is Used in This Project

The current project uses a lightweight retrieval-augmented generation approach. It does not use a vector database yet, but it does retrieve relevant game context and inject it into the model prompt before generation.

This works like RAG because the model is not generating only from its general training knowledge. It is augmented with retrieved facts from the current game state, recent history, known facts, inventory, previous choices, and Tom memory.

The retrieval source is the game state instead of an external document database.

## 5.2 Retrieved Data Sources

The AI scene generator retrieves and uses the following data sources:

### Player State

The current player state provides the most important facts. This includes money, hunger, health, stress, housing, vehicle status, job status, and police heat.

### Known Facts

The `build_known_facts` function creates a list of facts that the AI is allowed to use. Examples include:

- The player woke from a fifteen-year coma in Las Playas.
- Tom is the assigned recovery support specialist.
- The player’s goal is $100,000.
- The player has a specific amount of cash.
- The player’s housing situation.
- The 2001 Volvo status.
- Whether the player has a motel voucher.
- Whether the impound lot has confirmed the Volvo release cost.
- Whether the player has recovered the Volvo.
- Whether the player has a quick-cash contact.
- Whether the player has a job lead.
- Whether the player has checked into a motel.

This is important because the AI is instructed not to invent new vouchers, jobs, vehicles, people, places, or phone numbers unless they are mentioned in the narration or already listed in known facts.

### Major Events

The game stores recent major events. This allows the AI to remember important story developments, such as waking from the coma, meeting Tom, recovering the Volvo, getting a motel room, getting arrested, or collapsing from hunger.

### Lawful History

The game stores lawful actions, such as reviewing the discharge plan, accepting support, getting housing help, working legally, or making a budget.

### Criminal History

The game stores risky or criminal actions, such as using the easy-money contact or running shady deliveries.

### Tom Memory

Tom memory stores previous AI narration, offered choices, chosen labels, and chosen action types. This gives the AI a short-term memory of how Tom has been speaking and what the player recently selected.

### Recent Choices

The system tracks recent player choices and recently offered options. The AI is told to avoid repeating exact option labels.

## 5.3 Why This Counts as Retrieval-Augmented Generation

Traditional RAG often retrieves text chunks from a vector database. This project uses a smaller but still meaningful version of the same idea. Before generation, the system gathers the most relevant context from structured game memory and inserts it into the prompt.

The generation is augmented by retrieved context such as:

- Player condition
- Current resources
- Current risks
- Recent decisions
- Previous consequences
- Inventory
- Available support
- Tom’s relationship with the player

This improves the AI output because the model can generate scenes that match the actual game state.

## 5.4 Example of RAG-Style Context Injection

The user prompt includes a section like this:

```markdown
Known facts and available continuity:
- The player woke from a fifteen-year coma in Las Playas.
- Tom is their assigned recovery support specialist and is becoming a friend.
- The player's financial independence goal is $100,000.
- The player has $... available.
- The current housing situation is: ...
- The 2001 Volvo status is: ...
```

It also includes recent histories:

```markdown
Recent lawful moves: ...
Recent risky moves: ...
Recent major events: ...
Recently selected option labels to avoid repeating exactly: ...
Recently shown option labels to vary or replace: ...
Recent Tom narration memory to avoid repeating: ...
```

This gives the LLM a grounded context window for each new scene.

## 5.5 Benefits of the RAG-Style Design

This approach improves the game in several ways:

1. **Better continuity:** The AI can refer to recent choices and consequences.
2. **More grounded choices:** The AI is less likely to invent unsupported options.
3. **Personalized gameplay:** The AI can adapt based on the player’s legal or criminal behavior.
4. **Reduced repetition:** The AI receives recent option labels and narration memory.
5. **Dynamic difficulty:** Hunger, money, health, and police heat affect generated scenes.
6. **More believable NPC behavior:** Tom sounds like he remembers the player.

## 5.6 Future RAG Improvements

A future version could use a full vector database to store and retrieve larger lore documents. For example, the game could have files for:

- Las Playas locations
- NPC profiles
- Criminal organizations
- Job systems
- Medical recovery details
- Tom’s personality guide
- City history
- Side quests
- Dialogue examples

Then the AI could retrieve only the most relevant lore for each scene. This would make the world deeper while keeping prompts efficient.

---

# 6. Additional Tools / Innovation

## 6.1 Terminal-Style Streamlit Interface

One creative add-on in the project is the terminal-style user interface. The game uses custom CSS to create a dark green, computer-terminal aesthetic. This fits the title **Life After Reset** because the player is rebuilding life almost like restarting a system.

The UI includes:

- A title panel
- Scene header panel
- Dialogue panel
- Sidebar stats
- Inventory panel
- Save and quit buttons
- Choice buttons
- Latest consequence panel

This gives the project a stronger identity than a default Streamlit app.

## 6.2 Tom as a Persistent AI Companion

Another innovative feature is Tom. Tom is not just a narrator. He acts as:

- Recovery support specialist
- Guide
- Moral witness
- Friend
- Warning system
- Emotional anchor

Tom reacts differently depending on whether the player is leaning legal, criminal, or mixed. This gives the AI system a personality and makes the game feel more like an interactive story than a basic menu system.

## 6.3 Adaptive Legal and Criminal Progression

The game has two progression systems:

- Legal progression
- Shady progression

The legal route is slower but safer. The shady route is faster but more dangerous. This creates a meaningful gameplay innovation because the AI-generated narrative is connected to mechanical consequences.

The AI is instructed to offer more legal options when the player repeatedly chooses legal work and more criminal options when the player repeatedly chooses quick cash. This makes the world respond to the player’s behavior.

## 6.4 Dynamic Food Economy

The food system is also a creative add-on. Food prices are not just fixed values. They are calculated using the player’s progress toward the financial goal. The system builds a food menu with different hunger gains and prices.

This adds strategy because the player has to decide how much money to spend on survival.

## 6.5 Save System

The save system is another useful add-on. It allows the player state to be written to a JSON file. This supports future expansion because a saved state could later be loaded back into the game.

## 6.6 Future Innovation: Text-to-Speech and NPC Images

The current project does not yet include text-to-speech or NPC image generation. However, the design is ready for those features. For example:

- Tom’s narration could be sent to a text-to-speech library.
- Tom’s expression could change based on player morality.
- Important NPCs could have generated portraits.
- The city of Las Playas could have generated location images.
- Crime, work, hospital, and motel scenes could use generated visual cards.

These would be good future additions, but the current project already includes creative AI-driven storytelling, a custom UI, state-based memory, and adaptive survival systems.

---

# 7. Code Quality and Modular Design

## 7.1 Modular Structure

The project is organized into separate modules with clear responsibilities. This supports maintainability and makes the system easier to expand.

The main files include:

### `app.py`

This file handles the Streamlit application and user interface. It is responsible for:

- Page configuration
- Styling
- Start screen
- Sidebar
- Stats display
- Inventory display
- Scene rendering
- Buttons
- Save and quit controls
- Session state management

### `engine.py`

This file controls the main game logic. It is responsible for:

- Loading scenes
- Applying choices
- Managing scripted scenes
- Managing dynamic scene routing
- Updating state consequences
- Handling legal work
- Handling quick cash
- Handling food
- Handling housing
- Handling transportation
- Handling rest
- Handling social support
- Handling medical follow-up
- Handling budget planning
- Checking for hunger emergencies
- Checking for the financial independence ending

### `scene_generation.py`

This file handles AI scene generation. It is responsible for:

- Building the AI system prompt
- Building the user prompt
- Sending prompts to Ollama
- Parsing JSON responses
- Validating AI-generated scenes
- Building fallback scenes
- Handling low-hunger scenes
- Avoiding repeated choices
- Grounding options in narration
- Controlling allowed action types

### `state.py`

This file defines and manages player state. It is responsible for:

- Creating the starting player state
- Normalizing state values
- Clamping stats to valid ranges
- Saving the game
- Formatting progress snapshots
- Managing inventory items
- Managing event history
- Managing Tom memory

### `economy.py`

This file handles economy-related helper functions. It is responsible for:

- Normalizing money
- Formatting money
- Calculating progress toward the financial goal
- Calculating food prices
- Building the food menu

This separation is good design because the UI, AI generation, game logic, state, and economy are not all mixed together in one file.

## 7.2 Clean State Management

The game uses a dictionary-based player state. This makes it easy to pass the state between modules and update it based on choices.

The state includes both visible and hidden values. Visible values include cash, health, hunger, housing, vehicle, and job. Hidden values include morality, police heat, reputation, legal level, shady level, legal streak, crime streak, and Tom trust.

This design supports complex gameplay while keeping the UI simple.

## 7.3 Validation and Error Handling

The AI output is validated before being used. The validation checks include:

- Narration must exist.
- Tom should not be mentioned incorrectly in third person.
- Options must be a list.
- There must be exactly four options.
- Labels must not be empty.
- Labels must not repeat.
- Action types must be allowed.
- Food menu cannot appear when hunger is not low enough.
- Recent option labels cannot repeat.
- Evidence must appear in the narration.
- Legal-focused players must receive enough legal options.
- Criminal-focused players must receive enough quick-cash options.

If the AI response fails validation, the game uses a fallback scene. This is strong design because it prevents bad AI output from breaking the game.

## 7.4 Fallback System

The fallback system is important because LLMs are not fully predictable. Even with a strong prompt, the model might sometimes produce invalid JSON, repeat choices, invent unsupported details, or ignore format instructions.

The project handles this by using fallback scene generation when needed. This means the game can continue running even when the AI does not behave perfectly.

## 7.5 Version Control and Environment Management

The project is designed to be committed to a Git repository. The README includes local run instructions:

```bash
pip install -r requirements.txtstreamlit run app.py
```

This shows environment awareness because the project expects dependencies to be installed through `requirements.txt`.

The project also separates files clearly, which works well with version control. Changes to UI, game logic, economy, state, and AI prompting can be tracked separately.

## 7.6 Maintainability

The code is maintainable because most systems are broken into focused functions. For example:

- `apply_legal_work_choice`
- `apply_quick_cash_choice`
- `apply_food_choice`
- `apply_housing_choice`
- `apply_transport_choice`
- `apply_rest_choice`
- `apply_social_support_choice`
- `apply_medical_followup_choice`
- `apply_budget_plan_choice`

Each function handles one kind of action. This makes the game easier to debug and expand.

For example, if I wanted to add a new action type called `education`, I could:

1. Add `"education"` to the allowed action types.
2. Add a new handler called `apply_education_choice`.
3. Add it to the dynamic handler dictionary.
4. Update the prompt so the AI can offer education-related choices.
5. Add state changes such as increased reputation or future job opportunities.

This shows that the system is modular and expandable.

---

# Additional sections not part of the rubric that I added for better documentation

# 8. Connection to Learning Outcomes

## LO1: Demonstrate Fundamental AI Concepts in a Working System

The project demonstrates LO1 by using an LLM to generate interactive game scenes. It uses AI concepts such as:

- Prompt engineering
- Role prompting
- Structured output
- Context injection
- Memory
- Planning
- State-based reasoning
- Retrieval-augmented generation style context
- Validation of AI output
- Dynamic response generation

The AI system is part of a working game, not just a standalone chatbot.

## LO2: Demonstrate Use of AI Libraries and Packages

The project demonstrates LO2 by using:

- Python
- Streamlit
- Ollama
- JSON parsing
- File system saving
- Modular Python packages
- Custom AI scene generation logic

The project integrates an AI model into a Python application and connects it to other modules that manage game state, economy, and UI.

## LO3: Create a Modular and Well-Designed Working System

The project demonstrates LO3 through its modular design. The system separates:

- UI code
- Game engine code
- AI scene generation
- State management
- Economy logic
- Save logic

This makes the system easier to maintain, test, and expand.

---

# 9. Limitations and Future Work

Although the current project is playable and demonstrates the rubric requirements, there are still areas that could be improved.

## 9.1 Full Load Game Feature

The current system can save the game, but loading a saved game could be expanded. A future version should include a “Load Game” button that reads the latest save file and restores the previous player state.

## 9.2 Full Vector Database RAG

The current RAG implementation is state-based. A future version could use a vector database to retrieve lore, NPC information, location descriptions, and previous events.

Possible tools include:

- ChromaDB
- FAISS
- SQLite with embeddings
- LangChain retrievers

## 9.3 Text-to-Speech

Tom’s dialogue could be converted into speech using a text-to-speech library. This would make the game feel more cinematic.

## 9.4 NPC Image Generation

Tom and other characters could have generated portraits. The image could change depending on the scene mood, player morality, or danger level.

## 9.5 More Endings

The current ending changes based on whether the player is steady or more questionable. Future endings could include:

- Good citizen ending
- Criminal empire ending
- Burnout ending
- Hospital relapse ending
- Redemption ending
- Tom friendship ending
- Fugitive ending

## 9.6 More Locations

The current game includes the hospital, discharge hub, street hub, motel, impound lot, workforce office, deli, clinic, and city support systems. Future versions could add:

- Apartment search
- Community college
- Courthouse
- Bank
- Shelter
- Mechanic shop
- Police station
- Warehouse job site
- Criminal meeting spots
- Tom’s office

## 9.7 More NPCs

Tom is the main NPC. Future versions could add:

- Social worker
- Impound clerk
- Warehouse supervisor
- Motel manager
- Nurse
- Police officer
- Criminal contact
- Neighbor
- Old family friend

These NPCs could have their own memory and relationship systems.

---

# 10. Conclusion

**Life After Reset** is a working AI-powered life simulation game that combines interactive storytelling with state-based game mechanics. The player wakes up after a fifteen-year coma and must rebuild life in Las Playas while managing money, hunger, health, stress, housing, transportation, morality, and police heat.

The project demonstrates base system functionality through a playable Streamlit game loop. It demonstrates prompt engineering through a detailed role-based JSON prompt for Tom. It demonstrates tool usage through Python action handlers, economy functions, save files, and Ollama integration. It demonstrates planning and reasoning through legal and criminal progression systems, hunger emergencies, police heat, and financial independence goals. It demonstrates a RAG-style approach by retrieving current game state, history, known facts, and Tom memory before generating scenes. It demonstrates innovation through the terminal-style UI, adaptive AI narration, Tom’s persistent personality, dynamic food economy, and branching moral paths. Finally, it demonstrates modular design through separate files for the UI, engine, scene generation, state, and economy.

Overall, this project successfully creates a useful and creative AI system that applies AI methods inside a working game. It is not only a chatbot and not only a static text adventure. It is a modular AI-driven simulation where the player’s choices affect future narration, available actions, survival conditions, and final outcome.