"""Scenario helpers for tutorial and Phase 5 world mode."""

import os
from pathlib import Path

from .data import LOCATION_DESCRIPTIONS, LOCATIONS


GAME_MODE_ENV_VAR = "PANTHEON_GAME_MODE"
LOCAL_ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
_LOCAL_ENV_LOADED = False

TUTORIAL_GAME_MODE = "tutorial"
WORLD_GAME_MODE = "world"

TUTORIAL_SCENARIO_ID = "tutorial_mist_abbey"
WORLD_SCENARIO_ID = "agentic_world"

TUTORIAL_START_LOCATION = "修道院门口"
DEFAULT_ORIGIN_COUNTRY_ID = "albion"

WORLD_MODE_OBJECTIVE = (
    "在神座纪元世界中展开一次开放行动，让 Agent 生成临时场景、NPC、事件和物件；"
    "只有经过验证和提交的内容才会成为世界事实。"
)

COMMON_BACKGROUNDS = (
    {
        "background_id": "investigative_reporter",
        "name": "调查记者",
        "description": "为报社或独立刊物追查异常传闻，擅长采访、观察和记录。",
        "opening_hook": "你随身带着笔记本和一张尚未写完的采访提纲。",
    },
    {
        "background_id": "church_novice",
        "name": "教会见习",
        "description": "曾在教区、修会或小礼拜堂受训，熟悉仪式、祷告和教会规矩。",
        "opening_hook": "你知道正式神职人员说出口的话通常只是一半，另一半藏在规章里。",
    },
    {
        "background_id": "retired_officer",
        "name": "退役军官",
        "description": "离开军队或治安部队后卷入城市阴影，擅长判断危险和命令结构。",
        "opening_hook": "你仍保留着旧部队的站姿，也保留着对异常沉默的警觉。",
    },
    {
        "background_id": "railway_clerk",
        "name": "铁路职员",
        "description": "熟悉车站、货单、时刻表和人员流动，适合追查跨城线索。",
        "opening_hook": "你能从一张车票、一封行李标签和一段晚点记录里看出很多东西。",
    },
    {
        "background_id": "dock_scribe",
        "name": "港口书记员",
        "description": "接触码头账簿、船员传闻和海关手续，适合港口、走私和远洋案件。",
        "opening_hook": "你听过太多水手酒后的胡话，也知道其中少数并不是胡话。",
    },
    {
        "background_id": "fallen_noble",
        "name": "落魄贵族",
        "description": "出身旧家族但处境衰落，仍能进入某些宴会、沙龙和私人俱乐部。",
        "opening_hook": "你的姓氏还能打开一些门，也会让另一些人立刻戒备。",
    },
    {
        "background_id": "university_auditor",
        "name": "大学旁听生",
        "description": "游走在大学、图书馆和实验室边缘，擅长学术传闻和异常研究。",
        "opening_hook": "你没有所有证件，但你知道哪扇侧门不会在黄昏前上锁。",
    },
    {
        "background_id": "black_market_broker",
        "name": "黑市掮客",
        "description": "熟悉地下交易、假名、违禁品和消息买卖，适合灰色调查。",
        "opening_hook": "你明白很多秘密不是被发现的，而是被估价之后卖出来的。",
    },
)

PLAYABLE_ORIGINS = {
    "albion": {
        "name": "阿尔比昂",
        "formal_name": "阿尔比昂联合王国",
        "identity": "阿尔比昂人",
        "summary": "海权、金融、议会、殖民航线与世界第一海军。",
        "cities": (
            {
                "name": "格兰威克",
                "title": "万都之都",
                "description": "世界最大城市，金融、议会、远洋港口和海军决策中心。",
            },
            {
                "name": "布莱摩尔",
                "title": "黑炉城",
                "description": "纺织工业城、工人运动中心和蒸汽机械试验地。",
            },
            {
                "name": "圣维兰",
                "title": "潮钟城",
                "description": "潮汐圣会总部，海洋之神教会最高圣座和远航祝圣中心。",
            },
        ),
    },
    "lumiere": {
        "name": "卢米埃",
        "formal_name": "卢米埃共和国",
        "identity": "卢米埃人",
        "summary": "共和国、白塔院、革命思想、博物馆和学术审查。",
        "cities": (
            {
                "name": "卢塞恩",
                "title": "白城",
                "description": "世界第二大城市，政治文化中心、大学、报社、博物馆和贵族宴会并存。",
            },
            {
                "name": "圣雷米尔",
                "title": "真理之城",
                "description": "白塔院总部，全世界最大的研究中心，靠近阿斯特拉山脉。",
            },
            {
                "name": "维拉尔",
                "title": "",
                "description": "卢米埃最大港口、亚特海门户、河海联运中心和蔚蓝海岸入口。",
            },
        ),
    },
    "wald": {
        "name": "瓦尔德",
        "formal_name": "瓦尔德铁血邦联",
        "identity": "瓦尔德人",
        "summary": "陆权、军政长老团、工业巨城、铁路和铁血教团。",
        "cities": (
            {
                "name": "格莱芬",
                "title": "铁都",
                "description": "首都、总参谋部、军政长老团和战争教会大礼堂所在地。",
            },
            {
                "name": "科伦海姆",
                "title": "",
                "description": "瓦尔德西部工业核心，全世界最大工业区和铁血教团总部所在地。",
            },
            {
                "name": "霍恩维克",
                "title": "",
                "description": "东南界河城市、军官学院、旧贵族艺术中心和瓦尔德唯一港口。",
            },
        ),
    },
    "ost": {
        "name": "奥斯特",
        "formal_name": "奥斯特帝国",
        "identity": "奥斯特人",
        "summary": "皇权、审判法统、宫廷音乐、多民族帝国和旧贵族秩序。",
        "ethnicities": (
            {
                "name": "奥斯特人",
                "description": "帝国主体民族，集中在维伦纳和中央官僚体系，强调皇权、审判法统和宫廷文化。",
            },
            {
                "name": "佩斯塔人",
                "description": "第二大民族，主要聚集在佩斯塔和界河入海口东岸，拥有自治传统、港口贸易网络和边境贵族势力。",
            },
            {
                "name": "波西恩人",
                "description": "第三大民族，主要聚集在卡洛维茨及周边工业区，重视工业、工程、城市自治和民族文化保存。",
            },
        ),
        "cities": (
            {
                "name": "维伦纳",
                "title": "皇都",
                "description": "首都、皇宫、音乐之都、审判之都和审判庭总部。",
            },
            {
                "name": "卡洛维茨",
                "title": "",
                "description": "工业区，波西恩人聚集地，旧城、工厂、大学和机械异常并存。",
            },
            {
                "name": "佩斯塔",
                "title": "",
                "description": "亚特海港口，佩斯塔人聚集地，界河入海口东岸核心城市。",
            },
        ),
    },
    "isteria": {
        "name": "伊斯特亚",
        "formal_name": "伊斯特亚王冠领",
        "identity": "伊斯特亚人",
        "summary": "商人寡头君主制、王室法统、金融寡头、海商舰队和丰饶教会。",
        "cities": (
            {
                "name": "阿尔卡萨",
                "title": "",
                "description": "首都、王宫所在地、王室权力中心和殖民帝国法统所在地。",
            },
            {
                "name": "贝拉诺",
                "title": "花港",
                "description": "界河入海口西岸港口、海军核心、贸易中心和丰饶教会总部。",
            },
            {
                "name": "米拉诺",
                "title": "",
                "description": "伊斯特亚艺术与经济中心，金融寡头、画院、工坊和炼金材料市场聚集地。",
            },
        ),
    },
    "noctia": {
        "name": "诺克提亚",
        "formal_name": "诺克提亚",
        "identity": "诺克提亚人",
        "summary": "中立宗教城国、夜幕修会总部、保密银行、秘密档案和山地通行。",
        "cities": (
            {
                "name": "诺克提亚城",
                "title": "",
                "description": "首都兼唯一城市，夜幕修会总部、公开大教堂、保密银行和假名登记处所在地。",
            },
        ),
    },
    "selemia": {
        "name": "塞勒米亚",
        "formal_name": "塞勒米亚苏丹国",
        "identity": "塞勒米亚人",
        "summary": "金门海峡守门人、苏丹宫廷、旧帝国残余、香料贸易和公开深渊国教。",
        "cities": (
            {
                "name": "萨莱姆",
                "title": "",
                "description": "首都，深渊教会总部、苏丹宫廷、香料市场、海峡关卡和密仪会圣殿所在地。",
            },
        ),
    },
    "rosvia": {
        "name": "罗斯维亚",
        "formal_name": "罗斯维亚大公国",
        "identity": "罗斯维亚人",
        "summary": "寒地内陆强国、大公专制、旧信仰、矿山、冻河和安魂教团总部。",
        "cities": (
            {
                "name": "维亚洛夫",
                "title": "",
                "description": "首都，安魂教团总部、大公宫廷、旧圣像教堂、秘密警察和寒地贵族政治中心。",
            },
        ),
    },
}

ORIGIN_CHURCH_RELATIONS = {
    "albion": {
        "dominant": ["潮汐圣会"],
        "friendly": ["审判庭", "蔷薇圣庭", "夜幕修会"],
        "restricted": ["铁血教团", "白塔院", "安魂教团"],
        "hostile": ["密仪会", "欲望母神邪教"],
    },
    "lumiere": {
        "dominant": ["白塔院"],
        "friendly": ["潮汐圣会", "蔷薇圣庭", "安魂教团"],
        "restricted": ["审判庭", "铁血教团", "夜幕修会"],
        "hostile": ["密仪会", "欲望母神邪教"],
    },
    "wald": {
        "dominant": ["铁血教团"],
        "friendly": ["审判庭", "安魂教团", "白塔院"],
        "restricted": ["潮汐圣会", "蔷薇圣庭", "夜幕修会"],
        "hostile": ["密仪会", "欲望母神邪教"],
    },
    "ost": {
        "dominant": ["审判庭"],
        "friendly": ["铁血教团", "安魂教团", "白塔院"],
        "restricted": ["潮汐圣会", "蔷薇圣庭", "夜幕修会"],
        "hostile": ["密仪会", "欲望母神邪教"],
    },
    "isteria": {
        "dominant": ["蔷薇圣庭"],
        "friendly": ["潮汐圣会", "白塔院", "审判庭"],
        "restricted": ["铁血教团", "安魂教团", "夜幕修会"],
        "hostile": ["密仪会", "欲望母神邪教"],
    },
    "noctia": {
        "dominant": ["夜幕修会"],
        "friendly": ["潮汐圣会", "白塔院", "铁血教团", "审判庭", "蔷薇圣庭", "安魂教团"],
        "restricted": ["各国教会不得干涉诺克提亚档案和假名制度"],
        "hostile": ["密仪会", "欲望母神邪教"],
    },
    "selemia": {
        "dominant": ["密仪会"],
        "friendly": ["潮汐圣会", "白塔院", "铁血教团", "审判庭", "蔷薇圣庭", "安魂教团", "夜幕修会"],
        "restricted": ["未登记七神地下教派", "反苏丹武装化七神教派", "列强情报化教区"],
        "hostile": ["欲望母神邪教"],
    },
    "rosvia": {
        "dominant": ["安魂教团"],
        "friendly": ["铁血教团", "蔷薇圣庭", "夜幕修会"],
        "restricted": ["审判庭", "白塔院", "潮汐圣会"],
        "hostile": ["密仪会", "欲望母神邪教"],
    },
}

WORLD_START_LOCATION = PLAYABLE_ORIGINS[DEFAULT_ORIGIN_COUNTRY_ID]["cities"][0]["name"]


def game_mode_from_env():
    load_local_env()
    return normalize_game_mode(os.getenv(GAME_MODE_ENV_VAR, TUTORIAL_GAME_MODE))


def load_local_env():
    global _LOCAL_ENV_LOADED
    if _LOCAL_ENV_LOADED or not LOCAL_ENV_PATH.exists():
        _LOCAL_ENV_LOADED = True
        return

    for raw_line in LOCAL_ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)
    _LOCAL_ENV_LOADED = True


def normalize_game_mode(value):
    mode = (value or TUTORIAL_GAME_MODE).strip().lower()
    if mode in {"world", "agentic", "open_world", "open-world"}:
        return WORLD_GAME_MODE
    return TUTORIAL_GAME_MODE


def configure_character_for_game_mode(
    character,
    game_mode=None,
    origin_country_id=None,
    origin_city=None,
    origin_ethnicity=None,
    background_id=None,
):
    mode = normalize_game_mode(game_mode or TUTORIAL_GAME_MODE)
    character.flags["game_mode"] = mode
    character.flags["scenario_id"] = scenario_id_for_mode(mode)
    if mode == WORLD_GAME_MODE:
        origin = resolve_origin(origin_country_id, origin_city, origin_ethnicity)
        character.flags.update(origin)
        character.flags.update(resolve_background(background_id))
        character.current_location = origin["origin_city"]
    else:
        character.current_location = character.current_location or TUTORIAL_START_LOCATION
    return character


def scenario_id_for_mode(game_mode):
    if normalize_game_mode(game_mode) == WORLD_GAME_MODE:
        return WORLD_SCENARIO_ID
    return TUTORIAL_SCENARIO_ID


def game_mode_for_state(state):
    return normalize_game_mode(state.player.flags.get("game_mode", TUTORIAL_GAME_MODE))


def scenario_id_for_state(state):
    return state.player.flags.get("scenario_id", scenario_id_for_mode(game_mode_for_state(state)))


def is_world_mode_state(state):
    return game_mode_for_state(state) == WORLD_GAME_MODE


def origin_country_ids():
    return list(PLAYABLE_ORIGINS.keys())


def get_origin_country(country_id):
    return PLAYABLE_ORIGINS[country_id]


def city_names_for_origin(country_id):
    return [city["name"] for city in get_origin_country(country_id)["cities"]]


def ethnicity_options_for_origin(country_id):
    return tuple(get_origin_country(country_id).get("ethnicities", ()))


def ethnicity_names_for_origin(country_id):
    return [ethnicity["name"] for ethnicity in ethnicity_options_for_origin(country_id)]


def background_options():
    return COMMON_BACKGROUNDS


def background_names():
    return [background["name"] for background in COMMON_BACKGROUNDS]


def church_context_for_origin(country_id):
    country_id = normalize_origin_country_id(country_id)
    context = ORIGIN_CHURCH_RELATIONS[country_id]
    return {key: list(value) for key, value in context.items()}


def resolve_origin(country_id=None, city_name=None, ethnicity_name=None):
    country_id = normalize_origin_country_id(country_id)
    country = get_origin_country(country_id)
    city = find_origin_city(country, city_name)
    ethnicity = find_origin_ethnicity(country, ethnicity_name)
    return {
        "origin_country_id": country_id,
        "origin_country": country["name"],
        "origin_country_formal_name": country["formal_name"],
        "origin_identity": country["identity"],
        "origin_ethnicity": ethnicity,
        "origin_city": city["name"],
        "origin_city_title": city["title"],
        "origin_church_context": church_context_for_origin(country_id),
    }


def resolve_background(background_id=None):
    background = find_background(background_id)
    return {
        "background_id": background["background_id"],
        "background_name": background["name"],
        "background_description": background["description"],
        "background_opening_hook": background["opening_hook"],
    }


def find_background(value=None):
    if not value:
        return COMMON_BACKGROUNDS[0]
    candidate = str(value).strip()
    candidate_lower = candidate.lower()
    for background in COMMON_BACKGROUNDS:
        aliases = {
            background["background_id"],
            background["name"],
            background["background_id"].lower(),
        }
        if candidate in aliases or candidate_lower in aliases:
            return background
    return COMMON_BACKGROUNDS[0]


def normalize_origin_country_id(value):
    if not value:
        return DEFAULT_ORIGIN_COUNTRY_ID
    candidate = str(value).strip().lower()
    if candidate in PLAYABLE_ORIGINS:
        return candidate
    for country_id, country in PLAYABLE_ORIGINS.items():
        aliases = {
            country["name"],
            country["formal_name"],
            country["identity"],
            country_id,
        }
        if str(value).strip() in aliases:
            return country_id
    return DEFAULT_ORIGIN_COUNTRY_ID


def find_origin_city(country, city_name=None):
    cities = country["cities"]
    if not city_name:
        return cities[0]
    for city in cities:
        if city["name"] == city_name:
            return city
    return cities[0]


def find_origin_ethnicity(country, ethnicity_name=None):
    ethnicities = country.get("ethnicities", ())
    if not ethnicities:
        return country["identity"]
    if not ethnicity_name:
        return ethnicities[0]["name"]
    for ethnicity in ethnicities:
        if ethnicity["name"] == ethnicity_name:
            return ethnicity["name"]
    return ethnicities[0]["name"]


def describe_origin_city(country_id, city_name):
    country = get_origin_country(normalize_origin_country_id(country_id))
    city = find_origin_city(country, city_name)
    title_text = f"，常用称号：{city['title']}" if city["title"] else ""
    return f"{city['name']}{title_text}。{city['description']}"


def available_exits_for_state(state):
    if is_world_mode_state(state):
        return []
    return list(LOCATIONS.get(state.current_location, []))


def location_description_for_state(state):
    if is_world_mode_state(state):
        return describe_origin_city(
            state.player.flags.get("origin_country_id"),
            state.current_location,
        )
    return LOCATION_DESCRIPTIONS.get(state.current_location, "当前位置暂无固定描述。")


def objective_for_state(state, tutorial_objective):
    if is_world_mode_state(state):
        return WORLD_MODE_OBJECTIVE
    return tutorial_objective
