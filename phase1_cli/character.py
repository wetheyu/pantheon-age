"""Character creation for 神座纪元 v1.0."""

from dataclasses import dataclass, field

from data import BASE_HP, BASE_SAN, BASE_STATS, CLASSES, GODS
from utils import numbered_choice, print_divider, safe_input


@dataclass
class Character:
    name: str
    class_id: str
    class_name: str
    god: str
    stats: dict
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
            "stats": self.stats,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "san": self.san,
            "max_san": self.max_san,
            "suspicion": self.suspicion,
            "corruption": self.corruption,
            "inventory": self.inventory,
            "skills": self.skills,
            "current_location": self.current_location,
            "clues": self.clues,
            "flags": self.flags,
        }


def build_character(name, class_id, god):
    class_config = CLASSES[class_id]

    stats = BASE_STATS.copy()
    for stat_name, bonus in class_config["stat_bonus"].items():
        stats[stat_name] += bonus

    max_hp = max(1, BASE_HP + class_config["hp_bonus"])
    max_san = max(1, BASE_SAN + class_config["san_bonus"])

    return Character(
        name=name,
        class_id=class_id,
        class_name=class_config["name"],
        god=god,
        stats=stats,
        hp=max_hp,
        max_hp=max_hp,
        san=max_san,
        max_san=max_san,
        inventory=list(class_config["starting_items"]),
        skills=list(class_config["skill_tags"]),
        rule_modifiers=dict(class_config["rule_modifiers"]),
    )


def choose_class():
    print("\n请选择职业：")
    class_ids = list(CLASSES.keys())
    for index, class_id in enumerate(class_ids, start=1):
        class_config = CLASSES[class_id]
        print(f"{index}. {class_config['name']} / {class_config['english_name']} - {class_config['description']}")

    while True:
        answer = safe_input("输入职业编号或 class_id：").strip().lower()
        if answer.isdigit():
            index = int(answer) - 1
            if 0 <= index < len(class_ids):
                return class_ids[index]

        for class_id, class_config in CLASSES.items():
            names = {class_id, class_config["name"], class_config["english_name"].lower()}
            if answer in names:
                return class_id

        print("没有找到这个职业，请重新输入。")


def choose_god():
    print("\n请选择信仰神明：")
    for index, god in enumerate(GODS, start=1):
        print(f"{index}. {god}")
    return numbered_choice(GODS, "输入神明编号或完整名称：")


def create_character_interactive():
    print_divider("=")
    print("创建角色")
    print_divider("=")
    name = safe_input("请输入角色名：").strip() or "无名冒险者"
    class_id = choose_class()
    god = choose_god()
    character = build_character(name, class_id, god)

    print("\n角色创建完成：")
    print(f"- 名字：{character.name}")
    print(f"- 职业：{character.class_name}")
    print(f"- 信仰：{character.god}")
    print(f"- 属性：{character.stats}")
    print(f"- HP/SAN：{character.hp}/{character.san}")
    print(f"- 初始道具：{', '.join(character.inventory)}")
    return character
