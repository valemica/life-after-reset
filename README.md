# Life After Reset

AI-powered life simulation game built with Python, Streamlit, and Ollama.

## Overview
You wake up after a fifteen-year coma and have to rebuild your life in Las Playas with almost no support system. Tom, a slightly sarcastic but supportive recovery specialist, guides the player through high-impact choices while hidden morality and police heat shift quietly in the background.

## Features
- Choice-based gameplay (4 options every turn)
- Hidden law vs crime system
- Police heat and consequences
- Inventory and survival mechanics
- $100,000 financial independence goal and ending
- Persistent memory and storytelling
- Terminal-style UI

## Stack
- Python
- Streamlit
- Ollama (local LLM)

## Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Status
🚧 In development

## Current State
The current playable build starts in the hospital and completes a first end-to-end use case:

- `Start Game` with player name entry
- `Receive Narration` in a terminal-style Streamlit UI
- `View Choices` with exactly four clickable actions every turn
- `Select Choice` to update player state
- `Track Player Progress` through visible survival stats
- `Reach Financial Independence` by getting $100,000 in the player account
- `View Inventory`, `Save Game` (in progress), and `Quit Game`