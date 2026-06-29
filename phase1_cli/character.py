"""Character creation for 神座纪元 v8.7.0."""

from dataclasses import dataclass, field

from .data import BASE_HP, BASE_SAN, BASE_STATS, CLASSES
from .items import item_affordances_for
from .progression import (
    initial_attributes_for,
    initial_progression_for,
    normalize_attributes_payload,
    normalize_progression_payload,
    progression_to_dict,
)


@dataclass
class Character:
    name: str
    class_id: str
    class_name: str
    god: str
    stats: dict
    attributes: dict
    hp: int
    max_hp: int
    san: int
    max_san: int
    suspicion: int = 0
    corruption: int = 0
    inventory: list = field(default_factory=list)
    skills: list = field(default_factory=list)
    rule_modifiers: dict = field(default_factory=dict)
    current_location: str = "修道院门口"
    clues: list = field(default_factory=list)
    flags: dict = field(default_factory=dict)
    class_level: int = 1
    faith_level: int = 1
    ascension_rank: int = 0
    revelation: int = 0
    favor: int = 0
    devotion: int = 0
    progression_skills: list = field(default_factory=list)
    talents: list = field(default_factory=list)
    prayers: list = field(default_factory=list)
    burdens: list = field(default_factory=list)
    progression_flags: dict = field(default_factory=dict)

    def has_item(self, item_name):
        return item_name in self.inventory

    def add_item(self, item_name):
        self.inventory.append(item_name)

    def remove_item(self, item_name):
        if item_name in self.inventory:
            self.inventory.remove(item_name)
            return True
        return False

    def add_clue(self, clue_name):
        if clue_name not in self.clues:
            self.clues.append(clue_name)
            return True
        return False

    def to_dict(self):
        """A JSON-like shape that mirrors the future database save format."""
        return {
            "name": self.name,
            "class_id": self.class_id,
            "class_name": self.class_name,
            "god": self.god,
            "attributes": self.attributes,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "san": self.san,
            "max_san": self.max_san,
            "suspicion": self.suspicion,
            "corruption": self.corruption,
            "inventory": self.inventory,
            "skills": self.skills,
            "rule_modifiers": self.rule_modifiers,
            "current_location": self.current_location,
            "clues": self.clues,
            "flags": self.flags,
            "progression": progression_to_dict(self),
        }

    def to_public_dict(self):
        """A player-facing shape for CLI service responses and future API JSON."""
        return {
            "name": self.name,
            "class_id": self.class_id,
            "class_name": self.class_name,
            "god": self.god,
            "attributes": dict(self.attributes),
            "hp": self.hp,
            "max_hp": self.max_hp,
            "san": self.san,
            "max_san": self.max_san,
            "suspicion": self.suspicion,
            "corruption": self.corruption,
            "inventory": list(self.inventory),
            "item_affordances": item_affordances_for(self),
            "skills": list(self.skills),
            "current_location": self.current_location,
            "clues": list(self.clues),
            "origin": {
                "country_id": self.flags.get("origin_country_id"),
                "country": self.flags.get("origin_country"),
                "formal_name": self.flags.get("origin_country_formal_name"),
                "identity": self.flags.get("origin_identity"),
                "ethnicity": self.flags.get("origin_ethnicity"),
                "city": self.flags.get("origin_city"),
                "city_title": self.flags.get("origin_city_title"),
                "background_id": self.flags.get("background_id"),
                "background_name": self.flags.get("background_name"),
                "background_description": self.flags.get("background_description"),
                "wealth_level": self.flags.get("wealth_level"),
                "wealth_label": self.flags.get("wealth_label"),
                "resource_note": self.flags.get("resource_note"),
                "church_context": self.flags.get("origin_church_context"),
                "current_scene_focus": self.flags.get("current_scene_focus"),
                "opening_profile": self.flags.get("opening_profile"),
            },
            "progression": progression_to_dict(self),
        }

    @classmethod
    def from_dict(cls, data):
        """Rebuild a Character from saved JSON-like data."""
        progression = normalize_progression_payload(
            data.get("progression"),
            data["class_id"],
            data["god"],
        )
        attributes = normalize_attributes_payload(
            data.get("attributes"),
            data["class_id"],
        )
        return cls(
            name=data["name"],
            class_id=data["class_id"],
            class_name=data["class_name"],
            god=data["god"],
            stats=dict(data.get("stats") or BASE_STATS),
            attributes=attributes,
            hp=data["hp"],
            max_hp=data["max_hp"],
            san=data["san"],
            max_san=data["max_san"],
            suspicion=data.get("suspicion", 0),
            corruption=data.get("corruption", 0),
            inventory=list(data.get("inventory", [])),
            skills=list(data.get("skills", [])),
            rule_modifiers=dict(data.get("rule_modifiers", {})),
            current_location=data.get("current_location", "修道院门口"),
            clues=list(data.get("clues", [])),
            flags=dict(data.get("flags", {})),
            class_level=progression["class_level"],
            faith_level=progression["faith_level"],
            ascension_rank=progression["ascension_rank"],
            revelation=progression["revelation"],
            favor=progression["favor"],
            devotion=progression["devotion"],
            progression_skills=progression["progression_skills"],
            talents=progression["talents"],
            prayers=progression["prayers"],
            burdens=progression["burdens"],
            progression_flags=progression["progression_flags"],
        )


def build_character(name, class_id, god):
    class_config = CLASSES[class_id]
    progression = initial_progression_for(class_id, god)
    attributes = initial_attributes_for(class_id)

    max_hp = max(1, BASE_HP + class_config["hp_bonus"])
    max_san = max(1, BASE_SAN + class_config["san_bonus"])

    return Character(
        name=name,
        class_id=class_id,
        class_name=class_config["name"],
        god=god,
        stats=dict(BASE_STATS),
        attributes=attributes,
        hp=max_hp,
        max_hp=max_hp,
        san=max_san,
        max_san=max_san,
        inventory=list(class_config["starting_items"]),
        skills=list(class_config["skill_tags"]),
        rule_modifiers=dict(class_config["rule_modifiers"]),
        class_level=progression["class_level"],
        faith_level=progression["faith_level"],
        ascension_rank=progression["ascension_rank"],
        revelation=progression["revelation"],
        favor=progression["favor"],
        devotion=progression["devotion"],
        progression_skills=progression["progression_skills"],
        talents=progression["talents"],
        prayers=progression["prayers"],
        burdens=progression["burdens"],
        progression_flags=progression["progression_flags"],
    )
