"""League Setup page for normalized, fingerprinted local rules."""

from __future__ import annotations

from typing import Any

import duckdb
import streamlit as st
from pydantic import ValidationError

from fantasy_draft_ai.rules.models import DraftSettings, FlexSlot, LeagueRules
from fantasy_draft_ai.services.league_setup import (
    LeagueSetupIntegrityError,
    LeagueSetupRecord,
    PlayoffSettings,
    export_setup_yaml,
    import_setup_yaml,
)
from fantasy_draft_ai.ui.common import render_page_header
from fantasy_draft_ai.ui.context import load_app_context


def _rules_from_form(values: dict[str, Any], reference: LeagueRules) -> LeagueRules:
    flex_slots: list[FlexSlot] = []
    if int(values["flex_count"]):
        flex_slots.append(
            FlexSlot(
                name="FLEX",
                count=int(values["flex_count"]),
                eligible=("RB", "WR", "TE"),
            )
        )
    if int(values["superflex_count"]):
        flex_slots.append(
            FlexSlot(
                name="SUPERFLEX",
                count=int(values["superflex_count"]),
                eligible=("QB", "RB", "WR", "TE"),
            )
        )
    scoring = reference.scoring.model_copy(
        update={
            "reception": float(values["reception"]),
            "passing_td": float(values["passing_td"]),
            "interception": float(values["interception"]),
            "passing_yards_per_point": float(values["passing_yards_per_point"]),
            "rushing_yards_per_point": float(values["rushing_yards_per_point"]),
            "receiving_yards_per_point": float(values["receiving_yards_per_point"]),
        }
    )
    return LeagueRules(
        season=int(values["season"]),
        teams=int(values["teams"]),
        draft=DraftSettings(rounds=int(values["rounds"])),
        starters={
            "QB": int(values["qb"]),
            "RB": int(values["rb"]),
            "WR": int(values["wr"]),
            "TE": int(values["te"]),
        },
        flex_slots=tuple(flex_slots),
        bench=int(values["bench"]),
        ir=int(values["ir"]),
        scoring=scoring,
    )


def _setup_form(default: LeagueSetupRecord) -> LeagueSetupRecord | None:
    rules = default.rules
    flex_count = next((slot.count for slot in rules.flex_slots if slot.name == "FLEX"), 0)
    superflex_count = next((slot.count for slot in rules.flex_slots if slot.name == "SUPERFLEX"), 0)
    playoffs = default.playoff_settings or PlayoffSettings(
        playoff_teams=min(6, rules.teams),
        playoff_start_week=15,
        championship_week=17,
    )
    with st.form("league_setup_form"):
        st.subheader("League identity")
        identity_one, identity_two, identity_three = st.columns(3)
        league_id = identity_one.text_input("Setup name", value=default.league_season_id)
        platform = identity_two.text_input("Platform", value=default.platform)
        season = int(identity_three.number_input("Season", 2000, 2100, rules.season))

        st.subheader("Draft and roster")
        draft_one, draft_two, draft_three = st.columns(3)
        teams = int(draft_one.number_input("Teams", 4, 32, rules.teams))
        draft_slot = int(
            draft_two.number_input(
                "Your draft slot",
                1,
                teams,
                min(default.draft_slot, teams),
            )
        )
        rounds = int(draft_three.number_input("Draft rounds", 1, 40, rules.draft.rounds))

        starter_one, starter_two, starter_three, starter_four = st.columns(4)
        qb = int(starter_one.number_input("Starting QB", 0, 4, rules.starters.get("QB", 0)))
        rb = int(starter_two.number_input("Starting RB", 0, 6, rules.starters.get("RB", 0)))
        wr = int(starter_three.number_input("Starting WR", 0, 8, rules.starters.get("WR", 0)))
        te = int(starter_four.number_input("Starting TE", 0, 4, rules.starters.get("TE", 0)))
        roster_one, roster_two, roster_three, roster_four = st.columns(4)
        flex = int(roster_one.number_input("FLEX", 0, 4, flex_count))
        superflex = int(roster_two.number_input("SUPERFLEX", 0, 3, superflex_count))
        bench = int(roster_three.number_input("Bench", 0, 30, rules.bench))
        ir = int(roster_four.number_input("IR", 0, 20, rules.ir))
        expected_rounds = qb + rb + wr + te + flex + superflex + bench
        if expected_rounds != rounds:
            st.warning(
                f"Roster slots require {expected_rounds} rounds; the saved draft rounds must "
                "match exactly. IR does not consume a draft pick."
            )

        st.subheader("Scoring")
        scoring_one, scoring_two, scoring_three = st.columns(3)
        reception = float(
            scoring_one.number_input(
                "Points per reception",
                -2.0,
                3.0,
                float(rules.scoring.reception),
                0.5,
            )
        )
        passing_td = float(
            scoring_two.number_input("Passing TD", value=float(rules.scoring.passing_td))
        )
        interception = float(
            scoring_three.number_input("Interception", value=float(rules.scoring.interception))
        )
        yard_one, yard_two, yard_three = st.columns(3)
        passing_yards = float(
            yard_one.number_input(
                "Passing yards per point",
                min_value=1.0,
                value=float(rules.scoring.passing_yards_per_point),
            )
        )
        rushing_yards = float(
            yard_two.number_input(
                "Rushing yards per point",
                min_value=1.0,
                value=float(rules.scoring.rushing_yards_per_point),
            )
        )
        receiving_yards = float(
            yard_three.number_input(
                "Receiving yards per point",
                min_value=1.0,
                value=float(rules.scoring.receiving_yards_per_point),
            )
        )

        st.subheader("Playoffs")
        playoff_one, playoff_two, playoff_three = st.columns(3)
        playoff_teams = int(
            playoff_one.number_input("Playoff teams", 2, teams, min(playoffs.playoff_teams, teams))
        )
        playoff_start = int(
            playoff_two.number_input("Playoff start week", 1, 22, playoffs.playoff_start_week)
        )
        championship_week = int(
            playoff_three.number_input("Championship week", 1, 22, playoffs.championship_week)
        )
        submitted = st.form_submit_button("Save normalized setup", type="primary")
    if not submitted:
        return None
    values: dict[str, Any] = {
        "season": season,
        "teams": teams,
        "rounds": rounds,
        "qb": qb,
        "rb": rb,
        "wr": wr,
        "te": te,
        "flex_count": flex,
        "superflex_count": superflex,
        "bench": bench,
        "ir": ir,
        "reception": reception,
        "passing_td": passing_td,
        "interception": interception,
        "passing_yards_per_point": passing_yards,
        "rushing_yards_per_point": rushing_yards,
        "receiving_yards_per_point": receiving_yards,
    }
    rules = _rules_from_form(values, default.rules)
    return LeagueSetupRecord(
        league_season_id=league_id,
        platform=platform,
        rules=rules,
        draft_slot=draft_slot,
        playoff_settings=PlayoffSettings(
            playoff_teams=playoff_teams,
            playoff_start_week=playoff_start,
            championship_week=championship_week,
        ),
    )


def render() -> None:
    """Render normalized setup creation, selection, backup, and restore."""

    context = load_app_context()
    repository = context.setup_repository
    try:
        setups = repository.list()
    except (duckdb.Error, OSError, TypeError, ValueError, LeagueSetupIntegrityError) as exc:
        setups = ()
        st.error(f"Saved league setups could not be verified: {exc}")
    render_page_header(
        "League Setup",
        "Rules before rankings",
        "Save the exact roster, scoring, draft slot, and playoff settings that shape value.",
    )
    if setups:
        options = {item.league_season_id: item for item in setups}
        prior_value = st.session_state.get("selected_league_setup")
        prior = prior_value if isinstance(prior_value, str) else None
        selected_id = st.selectbox(
            "Active setup",
            list(options),
            index=list(options).index(prior) if prior in options else 0,
            format_func=lambda value: (
                f"{options[value].league_season_id} - slot {options[value].draft_slot} - "
                f"{options[value].fingerprint_label}"
            ),
        )
        selected = options[selected_id]
        st.session_state["selected_league_setup"] = selected_id
    else:
        selected = LeagueSetupRecord(
            league_season_id=f"my-{context.config.project.prediction_season}-league",
            rules=context.reference_rules,
            draft_slot=1,
            playoff_settings=PlayoffSettings(
                playoff_teams=6,
                playoff_start_week=15,
                championship_week=17,
            ),
        )
        st.info("No setup is saved yet. The checked-in 12-team PPR rules are prefilled below.")

    status_one, status_two, status_three = st.columns(3)
    status_one.metric("Teams", selected.rules.teams)
    status_two.metric("Draft slot", selected.draft_slot)
    status_three.metric("Roster rounds", selected.rules.draft.rounds)
    st.caption(
        f"Normalized fingerprint `{selected.rules.fingerprint()}` - "
        "draft sessions freeze this exact ruleset."
    )

    try:
        saved = _setup_form(selected)
        if saved is not None:
            persisted = repository.upsert(saved)
            st.session_state["selected_league_setup"] = persisted.league_season_id
            st.success(f"Saved {persisted.fingerprint_label}.")
            st.rerun()
    except (OSError, ValueError, ValidationError, LeagueSetupIntegrityError) as exc:
        st.error(f"Setup was not saved: {exc}")

    st.divider()
    st.subheader("Backup and restore")
    backup_one, backup_two = st.columns(2)
    backup_one.download_button(
        "Download setup YAML",
        data=export_setup_yaml(selected),
        file_name=f"{selected.league_season_id}.yaml",
        mime="application/x-yaml",
        width="stretch",
    )
    uploaded = backup_two.file_uploader("Import setup YAML", type=("yaml", "yml"))
    if uploaded is not None and backup_two.button("Validate and import", width="stretch"):
        try:
            imported = import_setup_yaml(uploaded.getvalue().decode("utf-8"))
            repository.upsert(imported)
            st.session_state["selected_league_setup"] = imported.league_season_id
            st.success("The fingerprint-verified setup was imported.")
            st.rerun()
        except (UnicodeDecodeError, OSError, ValueError, ValidationError) as exc:
            st.error(f"Import failed: {exc}")

    if setups:
        with st.expander("Delete a saved local setup"):
            delete_id = st.selectbox("Setup to delete", [item.league_season_id for item in setups])
            st.caption("Draft sessions already frozen with these rules are not deleted.")
            if st.button("Delete selected setup"):
                repository.delete(delete_id)
                if st.session_state.get("selected_league_setup") == delete_id:
                    st.session_state.pop("selected_league_setup", None)
                st.rerun()
