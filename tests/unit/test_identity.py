import pytest
from pydantic import ValidationError

from fantasy_draft_ai.schemas.identity import MappingConfidence, PlayerIdentity


def test_exact_identity_requires_source_identifier() -> None:
    with pytest.raises(ValidationError, match="source identifier"):
        PlayerIdentity(
            player_id="internal-1",
            display_name="Same Name",
            mapping_confidence=MappingConfidence.EXACT,
            mapping_source="display-name-only",
        )


def test_unresolved_name_only_identity_is_explicit() -> None:
    identity = PlayerIdentity(
        player_id="internal-1",
        display_name="Same Name",
        mapping_confidence=MappingConfidence.UNRESOLVED,
        mapping_source="manual-upload-name-only",
    )
    assert identity.mapping_confidence == "unresolved"
