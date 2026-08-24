"""Command-line entry point for repeatable local workflows."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Annotated

import typer
import yaml

from fantasy_draft_ai.config import load_config
from fantasy_draft_ai.data.adp_loader import load_adp_to_warehouse
from fantasy_draft_ai.data.audit import audit_project_data
from fantasy_draft_ai.data.identity_review import (
    apply_identity_overrides,
    refresh_identity_review_queue,
)
from fantasy_draft_ai.data.league_history_loader import import_league_history_package
from fantasy_draft_ai.data.nflverse_loader import load_nflverse_to_warehouse
from fantasy_draft_ai.data.nflverse_participation import (
    load_nflverse_participation_to_warehouse,
)
from fantasy_draft_ai.data.sources.espn import import_espn_adp
from fantasy_draft_ai.data.sources.ffc_adp import snapshot_ffc_adp
from fantasy_draft_ai.data.sources.nflverse import (
    download_nflverse,
    download_nflverse_snap_counts,
)
from fantasy_draft_ai.data.sources.platform_adp import (
    import_manual_platform_adp,
    snapshot_nflverse_ff_playerids,
    snapshot_sleeper_adp,
)
from fantasy_draft_ai.data.warehouse import Warehouse
from fantasy_draft_ai.draft.repository import DraftRepository
from fantasy_draft_ai.draft.state import DraftStateError
from fantasy_draft_ai.features.player_seasons import build_player_season_features
from fantasy_draft_ai.features.roster_construction import build_roster_history
from fantasy_draft_ai.logging import configure_logging
from fantasy_draft_ai.models.baselines.evaluate import evaluate_baselines
from fantasy_draft_ai.recommendations.config import load_draft_engine_config
from fantasy_draft_ai.recommendations.engine import recommend_for_session
from fantasy_draft_ai.rules.models import LeagueRules
from fantasy_draft_ai.scoring.engine import PlayerStatLine, score_player
from fantasy_draft_ai.services.adp_market import load_adp_market_board
from fantasy_draft_ai.services.draft_room import (
    create_draft_session,
    load_draft_session,
    prepare_draft_room,
    record_draft_pick,
    replace_draft_pick,
    undo_draft_pick,
)
from fantasy_draft_ai.services.projections import load_projection_board
from fantasy_draft_ai.services.status import project_status

app = typer.Typer(no_args_is_help=True, help="Local fantasy football modeling and draft tools.")
data_app = typer.Typer(no_args_is_help=True, help="Acquire, import, and audit data.")
rules_app = typer.Typer(no_args_is_help=True, help="Inspect normalized league rules.")
features_app = typer.Typer(no_args_is_help=True, help="Build cutoff-safe modeling features.")
models_app = typer.Typer(no_args_is_help=True, help="Evaluate projection baselines and models.")
draft_app = typer.Typer(no_args_is_help=True, help="Run a persisted manual snake draft.")
app.add_typer(data_app, name="data")
app.add_typer(rules_app, name="rules")
app.add_typer(features_app, name="features")
app.add_typer(models_app, name="models")
app.add_typer(draft_app, name="draft")


def _load_rules(path: Path) -> LeagueRules:
    with path.open(encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    return LeagueRules.model_validate(payload)


def _draft_repository() -> DraftRepository:
    config = load_config()
    return DraftRepository(config.resolve(config.paths.warehouse))


def _draft_error(exc: Exception) -> None:
    typer.echo(f"Draft command failed: {exc}", err=True)
    raise typer.Exit(code=2)


@app.callback()
def main() -> None:
    """Configure shared logging before executing a subcommand."""

    configure_logging()


@app.command("status")
def status_command() -> None:
    """Show what is actually available without fabricating model status."""

    config = load_config()
    for item in project_status(config):
        marker = "[available]" if item.available else "[pending]"
        typer.echo(f"{marker} {item.name}: {item.status}")


@data_app.command("init-warehouse")
def init_warehouse() -> None:
    """Create canonical DuckDB tables idempotently."""

    config = load_config()
    path = config.resolve(config.paths.warehouse)
    Warehouse(path).initialize()
    typer.echo(f"Initialized warehouse: {path}")


@data_app.command("download-nflverse")
def download_nflverse_command(
    start_season: int = typer.Option(..., min=1999),
    end_season: int = typer.Option(..., min=1999),
    offline: bool = typer.Option(False, help="Reuse matching local captures only."),
) -> None:
    """Archive nflverse player identities and weekly stats."""

    result = download_nflverse(
        load_config(), start_season=start_season, end_season=end_season, offline=offline
    )
    typer.echo(f"Players: {result.player_path}")
    typer.echo(f"Weekly stats: {result.stats_path}")
    typer.echo(f"Manifest: {result.manifest_path}")
    typer.echo(f"Offline reuse: {result.reused_offline}")


@data_app.command("download-nflverse-snap-counts")
def download_nflverse_snap_counts_command(
    start_season: int = typer.Option(..., min=2012),
    end_season: int = typer.Option(..., min=2012),
    offline: bool = typer.Option(False, help="Reuse a matching local capture only."),
) -> None:
    """Archive PFR game-level snap counts distributed by nflverse."""

    result = download_nflverse_snap_counts(
        load_config(),
        start_season=start_season,
        end_season=end_season,
        offline=offline,
    )
    typer.echo(f"Snap counts: {result.snap_counts_path}")
    typer.echo(f"Manifest: {result.manifest_path}")
    typer.echo(f"Offline reuse: {result.reused_offline}")


@data_app.command("load-nflverse")
def load_nflverse_command(
    manifest: Annotated[
        Path | None,
        typer.Option(
            "--manifest",
            help="Specific source manifest. Defaults to the newest complete nflverse manifest.",
        ),
    ] = None,
) -> None:
    """Validate and transactionally load archived nflverse data into DuckDB."""

    result = load_nflverse_to_warehouse(load_config(), manifest_path=manifest)
    typer.echo(result.render())
    if not result.committed:
        raise typer.Exit(code=2)


@data_app.command("load-nflverse-participation")
def load_nflverse_participation_command(
    manifest: Annotated[
        Path | None,
        typer.Option(
            "--manifest",
            help="Specific snap-count manifest. Defaults to the newest complete capture.",
        ),
    ] = None,
) -> None:
    """Validate and load archived snap counts as game participation."""

    result = load_nflverse_participation_to_warehouse(load_config(), manifest_path=manifest)
    typer.echo(result.render())
    if not result.committed:
        raise typer.Exit(code=2)


@data_app.command("review-identities")
def review_identities_command(
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            help="Review worksheet path. Defaults to data/processed/identity/.",
        ),
    ] = None,
) -> None:
    """Refresh cross-source identity evidence and export a review worksheet."""

    result = refresh_identity_review_queue(load_config(), output_path=output)
    typer.echo(result.render())
    if not result.committed:
        raise typer.Exit(code=2)


@data_app.command("apply-identity-overrides")
def apply_identity_overrides_command(path: Path) -> None:
    """Validate, archive, and transactionally apply reviewed identity decisions."""

    result = apply_identity_overrides(load_config(), path)
    typer.echo(result.render())
    if result.quality.has_fatal_errors:
        raise typer.Exit(code=2)


@data_app.command("snapshot-ffc-adp")
def snapshot_ffc_adp_command(
    season: int = typer.Option(..., min=2007),
    scoring_format: str = typer.Option("ppr", "--format"),
    teams: int = typer.Option(12, min=4, max=32),
    position: str | None = typer.Option(None),
    offline: bool = typer.Option(False, help="Reuse a matching local snapshot only."),
) -> None:
    """Archive one documented FFC ADP response without overwriting history."""

    result = snapshot_ffc_adp(
        load_config(),
        season=season,
        scoring_format=scoring_format,
        teams=teams,
        position=position,
        offline=offline,
    )
    typer.echo(f"Rows: {len(result.normalized)}")
    typer.echo(f"Raw snapshot: {result.raw_path}")
    typer.echo(f"Manifest: {result.manifest_path}")
    typer.echo(f"Offline reuse: {result.reused_offline}")


@data_app.command("import-espn-adp")
def import_espn_adp_command(path: Path) -> None:
    """Validate and archive a user-supplied ESPN ADP CSV."""

    result = import_espn_adp(load_config(), path)
    typer.echo(result.report.render())
    if result.report.has_fatal_errors:
        raise typer.Exit(code=2)
    typer.echo(f"Raw snapshot: {result.raw_path}")
    typer.echo(f"Manifest: {result.manifest_path}")


@data_app.command("snapshot-sleeper-adp")
def snapshot_sleeper_adp_command(
    season: int = typer.Option(2026, min=2000, max=2100),
    offline: bool = typer.Option(False, help="Reuse the newest matching capture only."),
) -> None:
    """Archive the current Sleeper full-PPR redraft ADP response."""

    result = snapshot_sleeper_adp(load_config(), season=season, offline=offline)
    typer.echo(f"Usable rows: {result.usable_count}")
    typer.echo(f"Captured at: {result.captured_at.isoformat()}")
    typer.echo(f"Raw snapshot: {result.raw_path}")
    typer.echo(f"Manifest: {result.manifest_path}")
    typer.echo(f"Offline reuse: {result.reused_offline}")


@data_app.command("snapshot-platform-player-ids")
def snapshot_platform_player_ids_command(
    offline: bool = typer.Option(False, help="Reuse the newest local crosswalk only."),
) -> None:
    """Archive nflverse's ESPN/Yahoo/Sleeper-to-GSIS player-ID crosswalk."""

    result = snapshot_nflverse_ff_playerids(load_config(), offline=offline)
    typer.echo(f"Rows: {result.row_count}")
    typer.echo(f"Captured at: {result.captured_at.isoformat()}")
    typer.echo(f"Raw snapshot: {result.raw_path}")
    typer.echo(f"Manifest: {result.manifest_path}")
    typer.echo(f"Offline reuse: {result.reused_offline}")


@data_app.command("import-platform-adp")
def import_platform_adp_command(
    path: Path,
    source: str = typer.Option(..., help="Authorized source: espn, yahoo, or underdog."),
) -> None:
    """Validate and archive one authorized standardized platform ADP CSV."""

    result = import_manual_platform_adp(load_config(), path, source=source)
    typer.echo(f"Source: {result.source}")
    typer.echo(f"Usable rows: {result.usable_count}")
    typer.echo(f"Captured at: {result.captured_at.isoformat()}")
    typer.echo(f"Raw snapshot: {result.raw_path}")
    typer.echo(f"Manifest: {result.manifest_path}")


@data_app.command("load-adp")
def load_adp_command(
    manifest: Annotated[
        Path | None,
        typer.Option(
            "--manifest",
            help="One supported ADP manifest. Defaults to every archived ADP manifest.",
        ),
    ] = None,
    include_synthetic: Annotated[
        bool,
        typer.Option(
            "--include-synthetic",
            help="Permit clearly labeled fixture captures; disabled for production builds.",
        ),
    ] = False,
) -> None:
    """Verify and idempotently normalize immutable ADP captures into DuckDB."""

    manifest_paths = None if manifest is None else [manifest]
    result = load_adp_to_warehouse(
        load_config(),
        manifest_paths=manifest_paths,
        include_synthetic=include_synthetic,
    )
    typer.echo(result.render())
    if not result.committed or result.quality.has_fatal_errors:
        raise typer.Exit(code=2)


@data_app.command("import-league-history")
def import_league_history_command(path: Path) -> None:
    """Archive, validate, and transactionally load a league-history-v1 ZIP."""

    result = import_league_history_package(load_config(), path)
    typer.echo(result.render())
    if not result.committed or result.quality.has_fatal_errors:
        raise typer.Exit(code=2)


@data_app.command("audit")
def audit_command() -> None:
    """Verify raw hashes and report canonical table counts."""

    result = audit_project_data(load_config())
    typer.echo(f"Manifests: {result.manifest_count}")
    typer.echo(f"Verified raw files: {result.verified_files}")
    typer.echo("Canonical table rows:")
    for table, count in result.table_counts.items():
        typer.echo(f"  {table}: {count}")
    for failure in result.failures:
        typer.echo(f"FAIL: {failure}", err=True)
    if not result.passed:
        raise typer.Exit(code=2)


@rules_app.command("fingerprint")
def fingerprint_command(path: Path) -> None:
    """Print canonical JSON and its deterministic ruleset SHA-256."""

    rules = _load_rules(path)
    typer.echo(json.dumps(json.loads(rules.canonical_json()), indent=2, sort_keys=True))
    typer.echo(f"Fingerprint: {rules.fingerprint()}")


@rules_app.command("score-example")
def score_example_command(path: Path) -> None:
    """Score a documented example stat line under a YAML ruleset."""

    rules = _load_rules(path)
    example = PlayerStatLine(position="WR", receiving_yards=100, receptions=7, receiving_tds=1)
    typer.echo(f"Example WR points: {score_player(example, rules.scoring):.2f}")


@features_app.command("build-roster-history")
def build_roster_history_command() -> None:
    """Build idempotent roster-construction and drafted-only historical reports."""

    result = build_roster_history(load_config())
    typer.echo(result.render())
    if not result.committed:
        raise typer.Exit(code=2)


@features_app.command("build-player-seasons")
def build_player_seasons_command(
    prediction_season: Annotated[
        int | None,
        typer.Option(
            "--prediction-season",
            min=2000,
            help="Final live prediction season. Defaults to the project configuration.",
        ),
    ] = None,
    rules_path: Annotated[
        Path,
        typer.Option(
            "--rules",
            help="League rules whose scoring definition produces fantasy-point targets.",
        ),
    ] = Path("configs/example_ppr_12_team.yaml"),
) -> None:
    """Build validated t-to-t+1 player-season features and separate targets."""

    result = build_player_season_features(
        load_config(),
        _load_rules(rules_path),
        prediction_season=prediction_season,
    )
    typer.echo(result.render())
    if not result.committed:
        raise typer.Exit(code=2)


@models_app.command("evaluate-baselines")
def evaluate_baselines_command(
    rules_path: Annotated[
        Path,
        typer.Option("--rules", help="Rules used by the validated feature build."),
    ] = Path("configs/example_ppr_12_team.yaml"),
    first_evaluation_season: Annotated[
        int | None,
        typer.Option("--first-evaluation-season", min=2000),
    ] = None,
    last_evaluation_season: Annotated[
        int | None,
        typer.Option("--last-evaluation-season", min=2000),
    ] = None,
    output: Annotated[
        Path | None,
        typer.Option("--output", help="JSON or Markdown report path."),
    ] = None,
) -> None:
    """Evaluate transparent baselines on expanding future-season folds."""

    result = evaluate_baselines(
        load_config(),
        _load_rules(rules_path),
        first_evaluation_season=first_evaluation_season,
        last_evaluation_season=last_evaluation_season,
        output_path=output,
    )
    typer.echo(result.render())
    if not result.committed:
        raise typer.Exit(code=2)


@models_app.command("train-player-models")
def train_player_models_command(
    rules_path: Annotated[
        Path,
        typer.Option("--rules", help="Rules used by the frozen Phase 3 feature build."),
    ] = Path("configs/example_ppr_12_team.yaml"),
    validation_start_season: Annotated[
        int,
        typer.Option("--validation-start-season", min=2000),
    ] = 2020,
    test_season: Annotated[
        int,
        typer.Option("--test-season", min=2000),
    ] = 2025,
    output: Annotated[
        Path,
        typer.Option("--output", help="Tracked Markdown evaluation report path."),
    ] = Path("docs/PHASE_4_MODEL_EVALUATION.md"),
    force: Annotated[
        bool,
        typer.Option("--force", help="Retrain an otherwise current deterministic run."),
    ] = False,
) -> None:
    """Train Ridge/HGB models, select champions, and build the live board."""

    # Keep optional pandas/scikit-learn imports out of non-model CLI commands.
    from fantasy_draft_ai.models.player_projection.train import (
        train_player_projection_models,
    )

    result = train_player_projection_models(
        load_config(),
        _load_rules(rules_path),
        validation_start_season=validation_start_season,
        test_season=test_season,
        report_markdown_path=output,
        report_json_path=output.with_suffix(".json"),
        force=force,
    )
    typer.echo(result.render())
    if not result.committed and not result.reused:
        raise typer.Exit(code=2)


@models_app.command("build-adp-baselines")
def build_adp_baselines_command(
    availability_config: Annotated[
        Path,
        typer.Option(
            "--availability-config",
            help="Versioned fallbacks used only when source-reported spread is absent.",
        ),
    ] = Path("configs/adp_availability.yaml"),
    output: Annotated[
        Path,
        typer.Option("--output", help="Markdown evaluation report path."),
    ] = Path("docs/PHASE_5_ADP_AVAILABILITY_EVALUATION.md"),
) -> None:
    """Build cutoff-safe ADP movement and empirical availability baselines."""

    from fantasy_draft_ai.models.adp.build import build_adp_market_baselines

    result = build_adp_market_baselines(
        load_config(),
        availability_config_path=availability_config,
        output_path=output,
    )
    typer.echo(result.render())
    if not result.committed and not result.reused:
        raise typer.Exit(code=2)


@draft_app.command("create")
def create_draft_command(
    rules_path: Annotated[
        Path,
        typer.Option("--rules", help="League rules for this session."),
    ] = Path("configs/example_ppr_12_team.yaml"),
    draft_slot: Annotated[int, typer.Option("--draft-slot", min=1, max=32)] = 1,
    name: Annotated[str, typer.Option("--name", help="Local session label.")] = "My draft",
    simulations: Annotated[
        int | None,
        typer.Option("--simulations", min=1, max=1000),
    ] = None,
    seed: Annotated[int | None, typer.Option("--seed")] = None,
) -> None:
    """Create a session with frozen projections and reviewed market mappings."""

    try:
        config = load_config()
        rules = _load_rules(rules_path)
        reference_rules = _load_rules(
            config.project_root / "configs" / "example_ppr_12_team.yaml"
        )
        engine_config = load_draft_engine_config(
            config.project_root / "configs" / "draft_engine.yaml"
        )
        preparation = prepare_draft_room(
            load_projection_board(config),
            load_adp_market_board(config),
            rules=rules,
            projection_reference_rules=reference_rules,
            required_market_coverage=engine_config.market_coverage_required,
        )
        session = create_draft_session(
            _draft_repository(),
            preparation,
            session_name=name,
            rules=rules,
            user_draft_slot=draft_slot,
            engine_config=engine_config,
            random_seed=config.project.random_seed if seed is None else seed,
            simulation_count=simulations,
        )
    except (OSError, KeyError, TypeError, ValueError, DraftStateError) as exc:
        _draft_error(exc)
        return
    typer.echo(f"Created draft session: {session.state.session_id}")
    typer.echo(f"Current pick: {session.state.current_overall_pick}")
    typer.echo(
        f"Recommendation status: {session.info.recommendation_status} - "
        f"{session.info.recommendation_message}"
    )


@draft_app.command("list")
def list_drafts_command() -> None:
    """List locally persisted draft sessions."""

    try:
        sessions = _draft_repository().list_sessions()
    except (OSError, TypeError, ValueError, DraftStateError) as exc:
        _draft_error(exc)
        return
    if not sessions:
        typer.echo("No draft sessions have been created.")
        return
    for session in sessions:
        typer.echo(
            f"{session.session_id} | {session.session_name} | {session.status} | "
            f"version {session.current_version} | {session.recommendation_status}"
        )


@draft_app.command("show")
def show_draft_command(session_id: Annotated[str, typer.Option("--session-id")]) -> None:
    """Verify and print the current state derived from the event stream."""

    try:
        session = load_draft_session(_draft_repository(), session_id)
    except (OSError, KeyError, TypeError, ValueError, DraftStateError) as exc:
        _draft_error(exc)
        return
    payload = session.state.as_dict()
    payload["recommendation_status"] = session.info.recommendation_status
    payload["recommendation_message"] = session.info.recommendation_message
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


@draft_app.command("pick")
def draft_pick_command(
    session_id: Annotated[str, typer.Option("--session-id")],
    player_id: Annotated[str, typer.Option("--player-id")],
    expected_version: Annotated[int, typer.Option("--expected-version", min=0)],
) -> None:
    """Record the on-clock team's next canonical player selection."""

    try:
        session = record_draft_pick(
            _draft_repository(),
            session_id,
            player_id,
            expected_version=expected_version,
        )
    except (OSError, KeyError, TypeError, ValueError, DraftStateError) as exc:
        _draft_error(exc)
        return
    typer.echo(
        f"Recorded pick {len(session.state.picks)}; next pick "
        f"{session.state.current_overall_pick}; version {session.state.version}."
    )


@draft_app.command("undo")
def draft_undo_command(
    session_id: Annotated[str, typer.Option("--session-id")],
    expected_version: Annotated[int, typer.Option("--expected-version", min=0)],
) -> None:
    """Append an undo event for the latest active pick."""

    try:
        session = undo_draft_pick(
            _draft_repository(),
            session_id,
            expected_version=expected_version,
        )
    except (OSError, KeyError, TypeError, ValueError, DraftStateError) as exc:
        _draft_error(exc)
        return
    typer.echo(
        f"Undid the latest pick; current pick {session.state.current_overall_pick}; "
        f"version {session.state.version}."
    )


@draft_app.command("replace")
def draft_replace_command(
    session_id: Annotated[str, typer.Option("--session-id")],
    overall_pick: Annotated[int, typer.Option("--overall-pick", min=1)],
    player_id: Annotated[str, typer.Option("--player-id")],
    expected_version: Annotated[int, typer.Option("--expected-version", min=0)],
) -> None:
    """Append a replacement event without deleting the original pick."""

    try:
        session = replace_draft_pick(
            _draft_repository(),
            session_id,
            overall_pick,
            player_id,
            expected_version=expected_version,
        )
    except (OSError, KeyError, TypeError, ValueError, DraftStateError) as exc:
        _draft_error(exc)
        return
    typer.echo(f"Replaced pick {overall_pick}; version {session.state.version}.")


@draft_app.command("verify")
def verify_draft_command(session_id: Annotated[str, typer.Option("--session-id")]) -> None:
    """Verify event hashes, replay, metadata, and the frozen player pool."""

    try:
        state = _draft_repository().verify_session(session_id)
    except (OSError, KeyError, TypeError, ValueError, DraftStateError) as exc:
        _draft_error(exc)
        return
    typer.echo(
        f"PASSED: {session_id} version {state.version} replayed to {state.fingerprint()}."
    )


@draft_app.command("recommend")
def recommend_draft_command(
    session_id: Annotated[str, typer.Option("--session-id")],
) -> None:
    """Run the frozen, reproducible recommendation baseline when market mappings permit."""

    try:
        config = load_config()
        engine_config = load_draft_engine_config(
            config.project_root / "configs" / "draft_engine.yaml"
        )
        result = recommend_for_session(_draft_repository(), session_id, engine_config)
    except (OSError, KeyError, TypeError, ValueError, DraftStateError) as exc:
        _draft_error(exc)
        return
    typer.echo(json.dumps(result.as_dict(), indent=2, sort_keys=True))
    if not result.available:
        raise typer.Exit(code=2)


@app.command("app")
def app_command() -> None:
    """Start the local Streamlit application."""

    config = load_config()
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(config.project_root / "app.py")],
        check=True,
    )


if __name__ == "__main__":
    app()
