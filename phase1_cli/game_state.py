"""Mutable game state for one CLI play session."""

from dataclasses import dataclass, field
from typing import Optional, Set

from character import Character


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
            "player": self.player.to_dict(),
            "visited_locations": sorted(self.visited_locations),
            "event_log": self.event_log,
        }
