"""Shared, typed application dependencies for Streamlit pages."""

from __future__ import annotations

from dataclasses import dataclass

from fantasy_draft_ai.config import AppConfig, load_config
from fantasy_draft_ai.draft.repository import DraftRepository
from fantasy_draft_ai.recommendations.config import (
    DraftEngineConfig,
    ProjectionGuidanceConfig,
    load_draft_engine_config,
    load_projection_guidance_config,
)
from fantasy_draft_ai.rules.models import LeagueRules
from fantasy_draft_ai.services.adp_market import AdpMarketBoard, load_adp_market_board
from fantasy_draft_ai.services.draft_room import DraftRoomPreparation, prepare_draft_room
from fantasy_draft_ai.services.league_setup import (
    LeagueSetupRepository,
    load_reference_rules,
)
from fantasy_draft_ai.services.projections import ProjectionBoard, load_projection_board


@dataclass(frozen=True)
class AppContext:
    """Dependencies loaded for one Streamlit rerun."""

    config: AppConfig
    projection_board: ProjectionBoard
    adp_market_board: AdpMarketBoard
    reference_rules: LeagueRules
    engine_config: DraftEngineConfig
    guidance_config: ProjectionGuidanceConfig
    draft_repository: DraftRepository
    setup_repository: LeagueSetupRepository

    def prepare_draft(self, rules: LeagueRules) -> DraftRoomPreparation:
        """Validate a ruleset against current projection and market contracts."""

        return prepare_draft_room(
            self.projection_board,
            self.adp_market_board,
            rules=rules,
            projection_reference_rules=self.reference_rules,
            required_market_coverage=self.engine_config.market_coverage_required,
        )


def load_app_context() -> AppContext:
    """Load the current local artifacts without hiding unavailable states."""

    config = load_config()
    warehouse_path = config.resolve(config.paths.warehouse)
    return AppContext(
        config=config,
        projection_board=load_projection_board(config),
        adp_market_board=load_adp_market_board(config),
        reference_rules=load_reference_rules(
            config.project_root / "configs" / "example_ppr_12_team.yaml"
        ),
        engine_config=load_draft_engine_config(
            config.project_root / "configs" / "draft_engine.yaml"
        ),
        guidance_config=load_projection_guidance_config(
            config.project_root / "configs" / "projection_guidance.yaml"
        ),
        draft_repository=DraftRepository(warehouse_path),
        setup_repository=LeagueSetupRepository(warehouse_path),
    )
