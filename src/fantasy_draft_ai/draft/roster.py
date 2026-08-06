"""Ruleset-aware roster legality and best-lineup assignment."""

from __future__ import annotations

from dataclasses import dataclass

from fantasy_draft_ai.rules.models import LeagueRules


@dataclass(frozen=True)
class RosterPlayer:
    """The minimum player information needed to assign a legal roster."""

    player_id: str
    position: str
    projected_points: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "position", self.position.strip().upper())
        if not self.player_id.strip():
            raise ValueError("player_id cannot be blank.")


@dataclass(frozen=True)
class StarterAssignment:
    slot: str
    player: RosterPlayer


@dataclass(frozen=True)
class RosterAssignment:
    """A maximum-value legal starting lineup plus bench overflow details."""

    starters: tuple[StarterAssignment, ...]
    bench: tuple[RosterPlayer, ...]
    unassigned: tuple[RosterPlayer, ...]
    starter_slot_count: int
    bench_capacity: int

    @property
    def legal(self) -> bool:
        return not self.unassigned

    @property
    def starter_coverage(self) -> float:
        if not self.starter_slot_count:
            return 1.0
        return len(self.starters) / self.starter_slot_count

    @property
    def starter_value(self) -> float:
        return float(sum(item.player.projected_points for item in self.starters))

    @property
    def bench_value(self) -> float:
        return float(sum(player.projected_points for player in self.bench))

    def slot_for_player(self, player_id: str) -> str | None:
        for assignment in self.starters:
            if assignment.player.player_id == player_id:
                return assignment.slot
        if any(player.player_id == player_id for player in self.bench):
            return "BENCH"
        return None


@dataclass(frozen=True)
class _ConcreteSlot:
    key: str
    eligible: tuple[str, ...]


def _starter_slots(rules: LeagueRules) -> tuple[_ConcreteSlot, ...]:
    slots: list[_ConcreteSlot] = []
    for position, count in rules.starters.items():
        slots.extend(
            _ConcreteSlot(f"{position}:{index}", (position,)) for index in range(1, count + 1)
        )
    for flex in rules.flex_slots:
        slots.extend(
            _ConcreteSlot(f"{flex.name}:{index}", flex.eligible)
            for index in range(1, flex.count + 1)
        )
    return tuple(slots)


def _maximum_matching(
    players: tuple[RosterPlayer, ...],
    slots: tuple[_ConcreteSlot, ...],
) -> dict[int, int]:
    """Return player-index to slot-index matches using deterministic augmenting paths."""

    slot_to_player: dict[int, int] = {}

    def assign(player_index: int, visited: set[int]) -> bool:
        player = players[player_index]
        for slot_index, slot in enumerate(slots):
            if slot_index in visited or player.position not in slot.eligible:
                continue
            visited.add(slot_index)
            incumbent = slot_to_player.get(slot_index)
            if incumbent is None or assign(incumbent, visited):
                slot_to_player[slot_index] = player_index
                return True
        return False

    for player_index in range(len(players)):
        assign(player_index, set())
    return {player_index: slot_index for slot_index, player_index in slot_to_player.items()}


def _is_matchable(
    players: tuple[RosterPlayer, ...],
    slots: tuple[_ConcreteSlot, ...],
) -> bool:
    return len(_maximum_matching(players, slots)) == len(players)


def assign_roster(
    players: tuple[RosterPlayer, ...] | list[RosterPlayer],
    rules: LeagueRules,
) -> RosterAssignment:
    """Assign the highest-value matchable players to starters and the rest to bench.

    Explicit slot eligibility is honored for every direct, FLEX, and SUPERFLEX slot.
    Weighted greedy selection is exact here because matchable player sets form a
    transversal matroid. Players that cannot fit the remaining universal bench capacity
    are returned as unassigned, making roster legality visible to callers.
    """

    roster = tuple(players)
    if len({player.player_id for player in roster}) != len(roster):
        raise ValueError("A roster cannot contain the same player more than once.")
    slots = _starter_slots(rules)
    ranked = sorted(
        roster,
        key=lambda player: (-player.projected_points, player.player_id),
    )
    selected: list[RosterPlayer] = []
    for player in ranked:
        if len(selected) == len(slots):
            break
        candidate = tuple([*selected, player])
        if _is_matchable(candidate, slots):
            selected.append(player)

    selected_tuple = tuple(selected)
    matching = _maximum_matching(selected_tuple, slots)
    starters = tuple(
        sorted(
            (
                StarterAssignment(slots[slot_index].key, selected_tuple[player_index])
                for player_index, slot_index in matching.items()
            ),
            key=lambda item: item.slot,
        )
    )
    starter_ids = {assignment.player.player_id for assignment in starters}
    nonstarters = tuple(player for player in ranked if player.player_id not in starter_ids)
    bench = nonstarters[: rules.bench]
    unassigned = nonstarters[rules.bench :]
    return RosterAssignment(
        starters=starters,
        bench=bench,
        unassigned=unassigned,
        starter_slot_count=len(slots),
        bench_capacity=rules.bench,
    )
