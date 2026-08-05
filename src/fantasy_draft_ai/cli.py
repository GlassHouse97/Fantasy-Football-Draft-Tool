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
from fantasy_draft_ai.data.audit import audit_project_data
from fantasy_draft_ai.data.identity_review import (
    apply_identity_overrides,
    refresh_identity_review_queue,
)
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
from fantasy_draft_ai.data.warehouse import Warehouse
from fantasy_draft_ai.features.player_seasons import build_player_season_features
from fantasy_draft_ai.logging import configure_logging
from fantasy_draft_ai.models.baselines.evaluate import evaluate_baselines
from fantasy_draft_ai.rules.models import LeagueRules
from fantasy_draft_ai.scoring.engine import PlayerStatLine, score_player
from fantasy_draft_ai.services.status import project_status

app = typer.Typer(no_args_is_help=True, help="Local fantasy football modeling and draft tools.")
data_app = typer.Typer(no_args_is_help=True, help="Acquire, import, and audit data.")
rules_app = typer.Typer(no_args_is_help=True, help="Inspect normalized league rules.")
features_app = typer.Typer(no_args_is_help=True, help="Build cutoff-safe modeling features.")
models_app = typer.Typer(no_args_is_help=True, help="Evaluate projection baselines and models.")
app.add_typer(data_app, name="data")
app.add_typer(rules_app, name="rules")
app.add_typer(features_app, name="features")
app.add_typer(models_app, name="models")


def _load_rules(path: Path) -> LeagueRules:
    with path.open(encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    return LeagueRules.model_validate(payload)


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
