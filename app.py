from __future__ import annotations

import html
import re

import streamlit as st

from ai.narration import NARRATION_STYLE_VERSION, get_narration
from game.engine import apply_choice, get_scene, get_scene_signature
from game.state import create_player_state, get_progress_snapshot, save_game


st.set_page_config(
    page_title="Life After Reset",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            :root {
                --bg-main: #020702;
                --bg-panel: #07140a;
                --bg-panel-soft: rgba(7, 20, 10, 0.88);
                --text-main: #b4ffcb;
                --text-bright: #e3ffee;
                --text-dim: #7ed69d;
                --line: rgba(93, 240, 145, 0.35);
                --accent: #5df091;
            }

            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(37, 125, 61, 0.18), transparent 34%),
                    radial-gradient(circle at top right, rgba(24, 86, 44, 0.12), transparent 28%),
                    linear-gradient(180deg, #020702 0%, #010401 100%);
                color: var(--text-main);
            }

            [data-testid="stAppViewContainer"],
            [data-testid="stMain"],
            [data-testid="stMainBlockContainer"],
            [data-testid="stHeader"] {
                background:
                    radial-gradient(circle at top left, rgba(37, 125, 61, 0.18), transparent 34%),
                    radial-gradient(circle at top right, rgba(24, 86, 44, 0.12), transparent 28%),
                    linear-gradient(180deg, #020702 0%, #010401 100%) !important;
            }

            [data-testid="stHeader"] {
                border-bottom: 1px solid rgba(93, 240, 145, 0.15);
            }

            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #031006 0%, #020702 100%) !important;
                border-right: 1px solid rgba(93, 240, 145, 0.18);
            }

            [data-testid="stSidebar"] > div:first-child,
            [data-testid="stSidebarContent"] {
                background: transparent !important;
            }

            [data-testid="collapsedControl"] button {
                color: #ffffff !important;
                background: transparent !important;
                border: none !important;
                box-shadow: none !important;
                outline: none !important;
                padding: 0 !important;
            }

            [data-testid="stSidebarCollapseButton"] button {
                color: var(--accent) !important;
            }

            [data-testid="collapsedControl"] svg {
                fill: #ffffff !important;
                color: #ffffff !important;
                stroke: #ffffff !important;
            }

            [data-testid="collapsedControl"] button:hover,
            [data-testid="collapsedControl"] button:focus,
            [data-testid="collapsedControl"] button:active {
                background: transparent !important;
                border: none !important;
                box-shadow: none !important;
                outline: none !important;
            }

            [data-testid="stSidebarCollapseButton"] svg {
                fill: var(--accent) !important;
                color: var(--accent) !important;
                stroke: var(--accent) !important;
            }

            html, body, [class*="css"]  {
                font-family: "SFMono-Regular", "Menlo", "Consolas", "Liberation Mono", monospace;
            }

            .block-container {
                padding-top: 5.4rem;
                padding-bottom: 2rem;
            }

            .hero-panel,
            .terminal-panel,
            .dialogue-panel,
            .scene-header-panel,
            .status-panel,
            .inventory-panel,
            .info-panel,
            .sidebar-panel,
            .start-form-panel {
                border: 1px solid var(--line);
                background: var(--bg-panel-soft);
                border-radius: 18px;
                box-shadow: 0 0 0 1px rgba(14, 50, 25, 0.2), 0 24px 60px rgba(0, 0, 0, 0.35);
            }

            .hero-panel {
                padding: 1.6rem 1.6rem 1.3rem;
                margin-bottom: 1rem;
            }

            .start-shell {
                max-width: 54rem;
                margin: 2rem auto 0;
                text-align: center;
            }

            .hero-kicker {
                color: var(--text-dim);
                font-size: 0.82rem;
                letter-spacing: 0.18rem;
                text-transform: uppercase;
                margin-bottom: 0.55rem;
            }

            .hero-title {
                color: var(--text-bright);
                font-family: "Impact", "Haettenschweiler", "Arial Narrow Bold", sans-serif;
                font-size: clamp(4.2rem, 8vw, 6.2rem);
                letter-spacing: 0.03em;
                margin: 0;
                line-height: 0.96;
                text-align: center;
            }

            .hero-copy {
                color: var(--text-main);
                font-size: 1rem;
                line-height: 1.7;
                margin: 0;
                max-width: 58rem;
            }

            .start-field-title {
                color: #f4fff8;
                font-size: 1.4rem;
                font-weight: 700;
                margin: 0.4rem 0 0.9rem;
                text-align: center;
            }

            .start-field-copy {
                color: var(--text-main);
                font-size: 1rem;
                line-height: 1.7;
                margin-bottom: 1.15rem;
            }

            .status-panel,
            .terminal-panel,
            .dialogue-panel,
            .scene-header-panel,
            .inventory-panel,
            .info-panel,
            .sidebar-panel,
            .start-form-panel {
                padding: 1rem 1.15rem;
                margin-bottom: 1rem;
            }

            .start-form-panel {
                padding: 1.6rem;
            }

            .compact-title-panel {
                max-width: 38rem;
                margin: 0 auto 1.2rem;
                padding: 2rem 1.5rem 1.8rem;
            }

            .compact-form-panel {
                max-width: 44rem;
                margin: 0 auto;
                padding: 1.5rem 1.5rem 1.8rem;
            }

            .start-label-only {
                text-align: center;
                margin: 0 auto 0.35rem;
            }

            .panel-title {
                color: var(--text-dim);
                font-size: 0.82rem;
                letter-spacing: 0.15rem;
                text-transform: uppercase;
                margin-bottom: 0.65rem;
            }

            .scene-title {
                color: var(--text-bright);
                font-size: 1.35rem;
                margin-bottom: 0.45rem;
            }

            .dialogue-speaker {
                color: var(--accent);
                font-size: 1rem;
                letter-spacing: 0.14rem;
                text-transform: uppercase;
                margin-bottom: 0.75rem;
            }

            .narration-copy {
                color: var(--text-main);
                white-space: normal;
                width: 100%;
                max-width: none;
                line-height: 1.8;
                min-height: 12rem;
                border-left: 3px solid rgba(93, 240, 145, 0.28);
                padding-left: 1rem;
                animation: fadeIn 260ms ease-out;
            }

            .narration-copy p {
                width: 100%;
                max-width: none;
                margin: 0 0 1rem 0;
            }

            .narration-copy p:last-child {
                margin-bottom: 0;
            }

            .hint-line {
                color: var(--text-dim);
                font-size: 0.92rem;
                margin-top: 0.75rem;
            }

            .inventory-copy,
            .info-copy {
                color: var(--text-main);
                line-height: 1.7;
            }

            .inventory-copy {
                margin: 0;
                padding-left: 1.1rem;
                white-space: pre-wrap;
            }

            .info-copy {
                white-space: normal;
                text-align: left;
            }

            .free-hint {
                color: #f4fff8;
                text-align: center;
                font-size: 1rem;
                line-height: 1.7;
                margin: 1.25rem auto 0;
            }

            .sidebar-block-title {
                color: var(--text-bright);
                font-size: 1rem;
                margin-bottom: 0.65rem;
            }

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(4px); }
                to { opacity: 1; transform: translateY(0); }
            }

            div.stButton > button {
                width: 100%;
                min-height: 4.2rem;
                border-radius: 14px;
                border: 1px solid rgba(93, 240, 145, 0.42);
                background: linear-gradient(180deg, rgba(8, 25, 12, 0.98), rgba(3, 12, 5, 0.98));
                color: var(--text-bright);
                font-weight: 600;
                line-height: 1.45;
                transition: transform 120ms ease, border-color 120ms ease, box-shadow 120ms ease;
            }

            div.stButton > button:hover {
                transform: translateY(-1px);
                border-color: rgba(93, 240, 145, 0.8);
                box-shadow: 0 0 0 1px rgba(93, 240, 145, 0.22), 0 10px 22px rgba(0, 0, 0, 0.28);
            }

            .stTextInput input,
            .stTextInput > div > div > input,
            div[data-baseweb="base-input"] input {
                background: rgba(5, 18, 8, 0.96);
                color: #f3fff8;
                border: 1px solid rgba(93, 240, 145, 0.32);
                height: 4.1rem;
                line-height: 4.1rem;
                font-size: 1.15rem;
                border-radius: 14px;
                box-shadow: inset 0 0 0 1px rgba(93, 240, 145, 0.08);
                text-align: center;
                box-sizing: border-box;
                padding: 0 1.15rem !important;
                margin: 0 !important;
                vertical-align: middle;
            }

            .stTextInput > div > div,
            .stTextInput div[data-baseweb="base-input"] {
                display: flex;
                align-items: center;
            }

            .stTextInput input::placeholder,
            .stTextInput > div > div > input::placeholder,
            div[data-baseweb="base-input"] input::placeholder {
                color: rgba(227, 255, 238, 0.62);
                opacity: 1;
                text-align: center;
                font-style: italic;
            }

            div[data-testid="InputInstructions"] {
                display: none;
            }

            .stTextInput label,
            .st-emotion-cache-10trblm,
            .st-emotion-cache-16idsys p,
            .stMarkdown,
            .stCaption,
            .stAlert {
                color: var(--text-main);
            }

            div[data-testid="stMetric"] {
                background: rgba(4, 17, 7, 0.92);
                border: 1px solid rgba(93, 240, 145, 0.22);
                border-radius: 16px;
                padding: 0.55rem 0.85rem;
            }

            div[data-testid="stMetricLabel"] {
                color: var(--text-bright) !important;
                opacity: 1 !important;
            }

            div[data-testid="stMetricLabel"] p {
                color: var(--text-bright) !important;
                -webkit-text-fill-color: var(--text-bright) !important;
            }

            div[data-testid="stMetricLabel"] * {
                color: var(--text-bright) !important;
                fill: var(--text-bright) !important;
                stroke: var(--text-bright) !important;
                -webkit-text-fill-color: var(--text-bright) !important;
                opacity: 1 !important;
            }

            div[data-testid="stMetricValue"] {
                color: var(--text-bright);
            }

            div[data-testid="stMetricValue"] > div {
                color: var(--text-bright) !important;
            }

            div[data-baseweb="notification"] {
                background: rgba(5, 18, 8, 0.95);
                color: var(--text-bright);
                border: 1px solid rgba(93, 240, 145, 0.25);
            }

            div[data-testid="stFormSubmitButton"] > button {
                width: min(22rem, 100%);
                min-height: 5.4rem;
                border-radius: 16px;
                border: 1px solid rgba(125, 255, 170, 0.95);
                background:
                    radial-gradient(circle at top, rgba(182, 255, 206, 0.98) 0%, rgba(98, 255, 149, 0.96) 18%, rgba(25, 150, 69, 0.94) 46%, rgba(5, 38, 16, 0.98) 100%);
                color: #021008;
                font-size: 1.35rem;
                font-weight: 800;
                letter-spacing: 0.08rem;
                text-transform: uppercase;
                box-shadow:
                    0 0 0 1px rgba(125, 255, 170, 0.25),
                    0 0 18px rgba(93, 240, 145, 0.55),
                    0 0 44px rgba(50, 184, 96, 0.38),
                    inset 0 1px 0 rgba(255, 255, 255, 0.35);
                transition: transform 120ms ease, box-shadow 120ms ease, filter 120ms ease;
            }

            div[data-testid="stFormSubmitButton"] > button:hover {
                transform: translateY(-2px);
                filter: saturate(1.08);
                box-shadow:
                    0 0 0 1px rgba(125, 255, 170, 0.28),
                    0 0 24px rgba(93, 240, 145, 0.72),
                    0 0 58px rgba(50, 184, 96, 0.46),
                    inset 0 1px 0 rgba(255, 255, 255, 0.42);
            }

            div[data-testid="stFormSubmitButton"] {
                display: flex;
                justify-content: center;
                margin-top: 1.5rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def bootstrap_session() -> None:
    defaults = {
        "game_active": False,
        "player_state": None,
        "show_inventory": False,
        "save_message": "",
        "quit_message": "",
        "rendered_narration": "",
        "rendered_signature": "",
        "narration_status": "Ollama narration",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_render_cache() -> None:
    st.session_state.rendered_narration = ""
    st.session_state.rendered_signature = ""


def escape_copy(value: str) -> str:
    return escape_rich_text(value)


def sanitize_text(value: str) -> str:
    compact = re.sub(r"\s+", " ", value).strip()
    return escape_rich_text(compact)


def escape_rich_text(value: str) -> str:
    escaped = html.escape(value, quote=True)
    return escaped.replace("$", "&#36;")


def format_narration_html(value: str) -> str:
    if not value.strip():
        return ""
    return escape_rich_text(value).replace("\n", "<br>")


def start_new_game(name: str) -> None:
    st.session_state.player_state = create_player_state(name)
    st.session_state.game_active = True
    st.session_state.show_inventory = False
    st.session_state.save_message = ""
    st.session_state.quit_message = ""
    clear_render_cache()
    st.rerun()


def render_start_screen() -> None:
    left_col, center_col, right_col = st.columns([1.2, 1.6, 1.2])

    with center_col:
        st.markdown(
            """
            <div class="start-shell">
                <div class="hero-panel compact-title-panel">
                    <div class="hero-title">Life After Reset</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.session_state.quit_message:
            st.info(st.session_state.quit_message)

        inner_left, form_col, inner_right = st.columns([0.2, 1.6, 0.2])
        with form_col:
            st.markdown(
                """
                <div class="start-label-only">
                    <div class="start-field-title">Enter Player Name</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.form("start_game_form", clear_on_submit=False):
                player_name = st.text_input(
                    "Enter Player Name",
                    max_chars=30,
                    placeholder="Enter the name you want your player to be named",
                    label_visibility="collapsed",
                )
                submitted = st.form_submit_button("Start Game", use_container_width=True)

                if submitted:
                    cleaned_name = player_name.strip()
                    if not cleaned_name:
                        st.error("Enter a player name to begin the hospital intro.")
                    else:
                        start_new_game(cleaned_name)


def render_sidebar(player_state: dict) -> None:
    progress = get_progress_snapshot(player_state)
    housing = escape_copy(progress["housing"])
    vehicle = escape_copy(progress["vehicle"])
    job = escape_copy(progress["job"])

    with st.sidebar:
        if st.button("Inventory", use_container_width=True):
            st.session_state.show_inventory = not st.session_state.show_inventory

        if st.button("Save Game", use_container_width=True):
            save_path = save_game(player_state)
            st.session_state.save_message = f"Manual save written to {save_path.name}"

        if st.button("Quit Game", use_container_width=True):
            player_name = player_state["name"]
            st.session_state.quit_message = (
                f"{player_name}'s session was closed. Start a new run from the hospital when you're ready."
            )
            st.session_state.game_active = False
            st.session_state.player_state = None
            st.session_state.show_inventory = False
            clear_render_cache()
            st.rerun()

        if st.session_state.save_message:
            st.success(st.session_state.save_message)

        top_row = st.columns(2)
        top_row[0].metric("Day", progress["day"])
        top_row[1].metric("Cash", progress["cash"])

        middle_row = st.columns(2)
        middle_row[0].metric("Health", progress["health"])
        middle_row[1].metric("Energy", progress["energy"])

        bottom_row = st.columns(2)
        bottom_row[0].metric("Hunger", progress["hunger"])
        bottom_row[1].metric("Stress", str(player_state["stress"]))

        st.markdown(
            f"""
            <div class="sidebar-panel">
                <div class="panel-title">Current Position</div>
                <div class="info-copy">
                    <strong>Housing:</strong> {housing}<br>
                    <strong>Vehicle:</strong> {vehicle}<br>
                    <strong>Work:</strong> {job}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.session_state.show_inventory:
            render_inventory(player_state)


def render_inventory(player_state: dict) -> None:
    inventory_lines = "".join(f"<li>{escape_copy(item)}</li>" for item in player_state["inventory"])
    st.markdown(
        f"""
        <div class="sidebar-panel">
            <div class="panel-title">Inventory</div>
            <ul class="inventory-copy">{inventory_lines}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_scene(player_state: dict) -> None:
    scene = get_scene(player_state)
    signature = f"{get_scene_signature(player_state)}::{NARRATION_STYLE_VERSION}"

    if signature != st.session_state.rendered_signature:
        narration, status = get_narration(
            base_narration=scene["narration"],
            state=player_state,
        )
        st.session_state.rendered_narration = narration
        st.session_state.rendered_signature = signature
        st.session_state.narration_status = status

    safe_kicker = sanitize_text(scene["kicker"])
    safe_title = sanitize_text(scene["title"])
    safe_narration = format_narration_html(st.session_state.rendered_narration)

    st.markdown(
        f"""
        <div class="scene-header-panel">
            <div class="panel-title">{safe_kicker}</div>
            <div class="scene-title">{safe_title}</div>
        </div>
        <div class="dialogue-panel">
            <div class="dialogue-speaker">Tom</div>
            <div class="narration-copy">{safe_narration}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if player_state.get("last_outcome"):
        safe_outcome = escape_copy(player_state["last_outcome"])
        st.markdown(
            f"""
            <div class="info-panel">
                <div class="panel-title">Latest Consequence</div>
                <div class="info-copy">{safe_outcome}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    options = scene["options"]
    if len(options) != 4:
        st.error("Each turn must present exactly four choices.")
        return

    columns = st.columns(2, gap="large")
    for index, option in enumerate(options):
        with columns[index % 2]:
            if st.button(option["label"], key=f'{scene["id"]}_{option["id"]}', use_container_width=True):
                apply_choice(player_state, option["id"])
                st.session_state.save_message = ""
                clear_render_cache()
                st.rerun()

    if scene["id"] == "hospital_intro":
        st.markdown(
            """
            <div class="free-hint">
                Click the top-left arrow anytime to open inventory, save the game, quit, or check your stats.
            </div>
            """,
            unsafe_allow_html=True,
        )


def main() -> None:
    inject_styles()
    bootstrap_session()

    if not st.session_state.game_active or st.session_state.player_state is None:
        render_start_screen()
        return

    player_state = st.session_state.player_state
    render_sidebar(player_state)
    render_scene(player_state)


if __name__ == "__main__":
    main()
