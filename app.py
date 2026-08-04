"""Streamlit foundation; all reusable logic remains in the package."""

import streamlit as st
import yaml

from fantasy_draft_ai.config import load_config
from fantasy_draft_ai.rules.models import LeagueRules
from fantasy_draft_ai.scoring.engine import PlayerStatLine, score_player
from fantasy_draft_ai.services.status import project_status

st.set_page_config(page_title="Fantasy Football Draft AI", page_icon="🏈", layout="wide")
st.title("🏈 Fantasy Football Draft AI")
st.caption("Local-first projections, ruleset-aware value, and explanations you can audit.")

config = load_config()

status_tab, scoring_tab, learning_tab = st.tabs(
    ["Project status", "Scoring sandbox", "Learning path"]
)

with status_tab:
    st.subheader("What is actually available")
    for item in project_status(config):
        icon = "✅" if item.available else "⏳"
        st.write(f"{icon} **{item.name}:** {item.status}")
    st.info(
        "Learned projections and recommendations stay disabled until their data and tests exist."
    )

with scoring_tab:
    rules_path = config.project_root / "configs" / "example_ppr_12_team.yaml"
    with rules_path.open(encoding="utf-8") as handle:
        rules = LeagueRules.model_validate(yaml.safe_load(handle))
    st.write(f"Example ruleset fingerprint: `{rules.fingerprint()}`")
    position = st.selectbox("Position", ["QB", "RB", "WR", "TE"], index=2)
    receptions = st.number_input("Receptions", min_value=0.0, value=7.0, step=1.0)
    receiving_yards = st.number_input("Receiving yards", value=100.0, step=5.0)
    receiving_tds = st.number_input("Receiving touchdowns", min_value=0.0, value=1.0, step=1.0)
    line = PlayerStatLine(
        position=position,
        receptions=receptions,
        receiving_yards=receiving_yards,
        receiving_tds=receiving_tds,
    )
    st.metric("Fantasy points", f"{score_player(line, rules.scoring):.2f}")

with learning_tab:
    st.markdown(
        """
        1. Archive source data without overwriting it.
        2. Validate and map players with visible confidence.
        3. Build features using only information available before the prediction season.
        4. Beat transparent baselines before accepting a more complex model.
        5. Apply the exact league scoring and roster rules.
        6. Estimate draft availability separately from player performance.
        7. Simulate the rest of the draft and explain the recommendation.
        """
    )
    st.markdown("See `docs/learning/SCORING_AND_REPLACEMENT_VALUE.md` in the repository.")
