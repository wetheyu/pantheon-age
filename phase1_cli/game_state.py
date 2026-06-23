"""Mutable game state for one CLI play session."""

from dataclasses import dataclass, field
from typing import Optional, Set

from .character import Character
from .data import CORE_TRUTH_CLUES, LOCATIONS


@dataclass
class GameState:
    player: Character
    turn: int = 0
    is_game_over: bool = False
    ending_id: Optional[str] = None
    ending_text: str = ""
    event_log: list = field(default_factory=list)
    visited_locations: Set[str] = field(default_factory=lambda: {"修道院门口"})

    @property
    def current_location(self):
        return self.player.current_location

    def record_turn(self):
        self.turn += 1

    def move_to(self, location):
        self.player.current_location = location
        self.visited_locations.add(location)

    def add_event(self, message):
        self.event_log.append(message)

    def mark_game_over(self, ending_id, ending_text):
        self.is_game_over = True
        self.ending_id = ending_id
        self.ending_text = ending_text

    def to_dict(self):
        return {
            "turn": self.turn,
            "is_game_over": self.is_game_over,
            "ending_id": self.ending_id,
            "ending_text": self.ending_text,
            "player": self.player.to_dict(),
            "visited_locations": sorted(self.visited_locations),
            "event_log": self.event_log,
        }

    def to_public_dict(self):
        core_clues = CORE_TRUTH_CLUES.intersection(self.player.clues)
        return {
            "turn": self.turn,
            "current_location": self.current_location,
            "available_exits": list(LOCATIONS[self.current_location]),
            "is_game_over": self.is_game_over,
            "ending_id": self.ending_id,
            "ending_text": self.ending_text,
            "visited_locations": sorted(self.visited_locations),
            "event_log": list(self.event_log),
            "core_clue_count": len(core_clues),
            "core_clue_total": len(CORE_TRUTH_CLUES),
            "player": self.player.to_public_dict(),
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            player=Character.from_dict(data["player"]),
            turn=data.get("turn", 0),
            is_game_over=data.get("is_game_over", False),
            ending_id=data.get("ending_id"),
            ending_text=data.get("ending_text", ""),
            event_log=list(data.get("event_log", [])),
            visited_locations=set(data.get("visited_locations", ["修道院门口"])),
        )
