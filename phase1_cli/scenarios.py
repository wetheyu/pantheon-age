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
        "wealth_level": 1,
        "wealth_label": "拮据",
        "resource_note": "稿费、线人费和房租总在互相追赶；你能支付小额交通、酒钱和誊抄费，但买不起昂贵资产。",
    },
    {
        "background_id": "church_novice",
        "name": "教会见习",
        "description": "曾在教区、修会或小礼拜堂受训，熟悉仪式、祷告和教会规矩。",
        "opening_hook": "你知道正式神职人员说出口的话通常只是一半，另一半藏在规章里。",
        "wealth_level": 1,
        "wealth_label": "清贫",
        "resource_note": "你能借用少量教会物资，但个人财产有限；大额交易必须依赖教会许可或赞助人。",
    },
    {
        "background_id": "retired_officer",
        "name": "退役军官",
        "description": "离开军队或治安部队后卷入城市阴影，擅长判断危险和命令结构。",
        "opening_hook": "你仍保留着旧部队的站姿，也保留着对异常沉默的警觉。",
        "wealth_level": 2,
        "wealth_label": "体面但不宽裕",
        "resource_note": "退役津贴和旧人脉让你能维持体面，也能承担普通装备和短途旅行；地产、船只和大型投资仍远超能力。",
    },
    {
        "background_id": "railway_clerk",
        "name": "铁路职员",
        "description": "熟悉车站、货单、时刻表和人员流动，适合追查跨城线索。",
        "opening_hook": "你能从一张车票、一封行李标签和一段晚点记录里看出很多东西。",
        "wealth_level": 1,
        "wealth_label": "工薪",
        "resource_note": "你有稳定薪水和铁路便利，但现金有限；你能负担票据和小额打点，无法直接承担奢侈购买。",
    },
    {
        "background_id": "dock_scribe",
        "name": "港口书记员",
        "description": "接触码头账簿、船员传闻和海关手续，适合港口、走私和远洋案件。",
        "opening_hook": "你听过太多水手酒后的胡话，也知道其中少数并不是胡话。",
        "wealth_level": 1,
        "wealth_label": "工薪",
        "resource_note": "你熟悉账簿和人情债，但真正属于你的钱不多；码头消息比现金更值钱。",
    },
    {
        "background_id": "fallen_noble",
        "name": "落魄贵族",
        "description": "出身旧家族但处境衰落，仍能进入某些宴会、沙龙和私人俱乐部。",
        "opening_hook": "你的姓氏还能打开一些门，也会让另一些人立刻戒备。",
        "wealth_level": 2,
        "wealth_label": "有名无钱",
        "resource_note": "你的姓氏和信用还能敲开上流社会的门，但现金紧张；你可以谈抵押、借贷或婚约，不能随手买下庄园。",
    },
    {
        "background_id": "university_auditor",
        "name": "大学旁听生",
        "description": "游走在大学、图书馆和实验室边缘，擅长学术传闻和异常研究。",
        "opening_hook": "你没有所有证件，但你知道哪扇侧门不会在黄昏前上锁。",
        "wealth_level": 1,
        "wealth_label": "清贫",
        "resource_note": "你有知识入口和学生圈关系，但钱包很薄；大额资源只能通过导师、赞助或偷借设备获得。",
    },
    {
        "background_id": "black_market_broker",
        "name": "黑市掮客",
        "description": "熟悉地下交易、假名、违禁品和消息买卖，适合灰色调查。",
        "opening_hook": "你明白很多秘密不是被发现的，而是被估价之后卖出来的。",
        "wealth_level": 2,
        "wealth_label": "现金流不稳定",
        "resource_note": "你能调动小额黑钱、人情和赊账渠道，但大额资产会立刻引来债主、警察和帮派注意。",
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

GOD_CHURCHES = {
    "海洋之神": "潮汐圣会",
    "真理之神": "白塔院",
    "战争之神": "铁血教团",
    "审判之神": "审判庭",
    "丰饶之神": "蔷薇圣庭",
    "死亡之神": "安魂教团",
    "隐秘之神": "夜幕修会",
    "深渊之神": "密仪会",
}

GOD_OPENING_SIGNS = {
    "海洋之神": "远处像有潮声越过屋脊，提醒你所有航线都会留下回声。",
    "真理之神": "你下意识留意证词、印章和措辞，因为谎言通常先在细节上露出裂缝。",
    "战争之神": "街角的脚步和队列让你想起军令，秩序背后往往藏着真正的恐惧。",
    "审判之神": "你能感觉到契约、誓言和判决的阴影正在这座城里缓慢合拢。",
    "丰饶之神": "花香、药味和面包香混在一起，越是丰盛的地方，越可能藏着过度生长的东西。",
    "死亡之神": "蜡烛、墓碑和遗嘱的气味隔着人群传来，亡者的秩序从不真正沉默。",
    "隐秘之神": "窗帘后的视线、擦肩而过的暗号和空白档案提醒你：秘密也有自己的道路。",
    "深渊之神": "你听见梦境边缘传来几乎不可察觉的水声，像现实底部有黑暗正在翻身。",
}

CLASS_OPENING_LINES = {
    "warrior": "你习惯先确认出口、守卫和可用掩体，这让你在混乱开始前总能快半步。",
    "mage": "你会把异常当成结构来读：符号、材质、温度和重复出现的词，都可能是入口。",
    "rogue": "你知道正门通常是给别人看的，真正有用的信息藏在侧门、账本和低声交易里。",
    "hunter": "你先看足迹、气味和人群流向。城市也是荒野，只是猎物会穿礼服。",
    "priest": "你熟悉祷告、忏悔和禁忌仪式，也知道神职人员的沉默有时比布道更诚实。",
    "alchemist": "你会留意药味、金属粉尘、变色液体和不合常理的伤口，因为物质从不撒谎。",
}

COUNTRY_OPENING_PRESSURES = {
    "albion": "一份远洋保险赔付单被人匆匆藏进外套，旁边的报童正在叫卖一桩没有尸体的海难。",
    "lumiere": "新一期报纸被雨水打湿，标题提到一场被大学和博物馆同时否认的异常展览。",
    "wald": "军靴声从街口压过来，工厂烟囱却在同一时刻吐出不该有的苍白火星。",
    "ost": "一名宫廷乐师的死讯在低声传播，审判庭的马车已经先于讣告抵达街区。",
    "isteria": "一场慈善宴会的请柬被撕成两半，背面仍残留蔷薇香水和金融寡头的暗记。",
    "noctia": "假名登记处提前关门，山路信使留下的密封信却指向一个不存在的档案编号。",
    "selemia": "金门海峡的关税钟敲错了时辰，香料商和密仪会祭司同时停下了交谈。",
    "rosvia": "冻河上的送葬队伍没有棺木，安魂钟响过之后，秘密警察封住了一条小巷。",
}

BACKGROUND_ACTION_SUGGESTIONS = {
    "investigative_reporter": (
        "去本地报社、印刷所或咖啡馆核对这条传闻的来源",
        "采访第一个愿意开口的目击者",
    ),
    "church_novice": (
        "前往本地教会据点，询问最近是否有异常祷告或禁忌仪式",
        "观察神职人员是否在回避某个名字",
    ),
    "retired_officer": (
        "观察巡警、军人或守卫的调动，判断谁在控制现场",
        "用旧部队经验判断这里是否发生过暴力冲突",
    ),
    "railway_clerk": (
        "去车站、货运处或行李房查看最近的异常出入记录",
        "检查票据、货单或晚点记录里是否有重复出现的名字",
    ),
    "dock_scribe": (
        "前往码头或海关账房，寻找愿意低声说话的水手",
        "核对船名、货单和港口传闻是否互相矛盾",
    ),
    "fallen_noble": (
        "借姓氏进入沙龙、俱乐部或私人宴会，听听贵族们不敢公开说的话",
        "寻找一个认识旧家族纹章的人",
    ),
    "university_auditor": (
        "去大学、图书馆或博物馆寻找被撤下的讲义和展品记录",
        "找一名愿意冒险的学生或助教交换消息",
    ),
    "black_market_broker": (
        "联系黑市中间人，询问最近谁在高价收购异常物件",
        "用假名打听这条消息在地下渠道值多少钱",
    ),
}

WORLD_START_LOCATION = PLAYABLE_ORIGINS[DEFAULT_ORIGIN_COUNTRY_ID]["cities"][0]["name"]
CURRENT_SCENE_FOCUS_FLAG = "current_scene_focus"
SCENE_FOCUS_HISTORY_FLAG = "scene_focus_history"


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
        character.flags[CURRENT_SCENE_FOCUS_FLAG] = default_scene_focus(origin["origin_city"])
        character.flags[SCENE_FOCUS_HISTORY_FLAG] = [character.flags[CURRENT_SCENE_FOCUS_FLAG]]
        character.flags["opening_profile"] = build_world_opening_profile(character)
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


def world_city_names():
    names = []
    for country in PLAYABLE_ORIGINS.values():
        names.extend(city["name"] for city in country["cities"])
    return names


def find_world_city_in_text(text):
    source = str(text or "")
    for city_name in world_city_names():
        if city_name and city_name in source:
            return city_name
    return None


def is_world_city_name(value):
    candidate = str(value or "").strip()
    return candidate in set(world_city_names())


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
        "wealth_level": background["wealth_level"],
        "wealth_label": background["wealth_label"],
        "resource_note": background["resource_note"],
    }


def build_world_opening_profile(character):
    flags = character.flags
    country_id = normalize_origin_country_id(flags.get("origin_country_id"))
    city_name = flags.get("origin_city") or WORLD_START_LOCATION
    background_id = flags.get("background_id")
    scene_focus = flags.get(CURRENT_SCENE_FOCUS_FLAG) or default_scene_focus(city_name)
    church_name = GOD_CHURCHES.get(character.god, "未知教会")
    faith_status = faith_status_for_origin(country_id, church_name)
    background_actions = BACKGROUND_ACTION_SUGGESTIONS.get(background_id, ())
    suggested_actions = list(background_actions[:2])
    suggested_actions.append(f"留在{scene_focus}，观察谁最先对异常作出反应")
    suggested_actions.append(faith_action_suggestion(church_name, faith_status))

    return {
        "scene_focus": scene_focus,
        "identity_summary": (
            f"{character.name}，{flags.get('origin_country_formal_name', '未知国家')}的"
            f"{flags.get('origin_identity', '未知身份')}，"
            f"{flags.get('origin_ethnicity', flags.get('origin_identity', '未知民族'))}，"
            f"{flags.get('background_name', '无名旅人')}。"
        ),
        "class_context": CLASS_OPENING_LINES.get(
            character.class_id,
            "你没有显赫的头衔，但足够清醒，知道异常从不会自己解释自己。",
        ),
        "faith_context": faith_context_line(character.god, church_name, faith_status),
        "faith_sign": GOD_OPENING_SIGNS.get(character.god, ""),
        "city_context": describe_origin_city(country_id, city_name),
        "resource_context": (
            f"资源处境：{flags.get('wealth_label', '普通')}。"
            f"{flags.get('resource_note', '你能承担日常开销，但大额行动需要额外来源。')}"
        ),
        "opening_incident": COUNTRY_OPENING_PRESSURES.get(
            country_id,
            "一条没有来源的传闻穿过人群，像火星落进干草。",
        ),
        "first_hook": first_hook_for_background(background_id),
        "suggested_actions": suggested_actions[:4],
    }


def faith_status_for_origin(country_id, church_name):
    context = church_context_for_origin(country_id)
    if church_name in context["dominant"]:
        return "dominant"
    if church_name in context["friendly"]:
        return "friendly"
    if church_name in context["restricted"]:
        return "restricted"
    if church_name in context["hostile"]:
        return "hostile"
    return "unknown"


def faith_context_line(god_name, church_name, faith_status):
    if faith_status == "dominant":
        return f"你信仰{god_name}。{church_name}在这里拥有公开权威，你的信仰会带来入口，也会带来责任。"
    if faith_status == "friendly":
        return f"你信仰{god_name}。{church_name}在这里可以公开活动，但仍要看地方势力的脸色。"
    if faith_status == "restricted":
        return f"你信仰{god_name}。{church_name}在这里受限存在，公开求助可能引来盘问。"
    if faith_status == "hostile":
        return f"你信仰{god_name}。{church_name}在这里被视为敌对异教或危险结社，你最好谨慎暴露身份。"
    return f"你信仰{god_name}。这份信仰在当地的处境并不清晰，最好先观察。"


def faith_action_suggestion(church_name, faith_status):
    if faith_status in {"dominant", "friendly"}:
        return f"去{church_name}的公开据点，询问最近是否有人求助或失踪"
    if faith_status == "restricted":
        return f"谨慎寻找{church_name}的私人联络点，不要直接暴露目的"
    if faith_status == "hostile":
        return f"隐藏与{church_name}有关的痕迹，先从旁人的恐惧里判断局势"
    return "先观察本地宗教和治安气氛，再决定向谁开口"


def first_hook_for_background(background_id):
    hooks = {
        "investigative_reporter": "你的采访提纲上只写着一句话：有人在说真话，但报纸不敢刊登。",
        "church_novice": "你记得导师说过：异常最先污染的不是街道，而是祷词。",
        "retired_officer": "你一眼看出现场的安静不正常，那是有人提前清过场的安静。",
        "railway_clerk": "你口袋里那张误送的车票，目的地栏被墨水涂黑，却没有完全干透。",
        "dock_scribe": "一名水手昨天把一枚湿透的硬币塞给你，只说不要相信今早第一班船。",
        "fallen_noble": "一封没有署名的请柬把你带到这里，封蜡上却压着你家族早已废弃的纹章。",
        "university_auditor": "你听说一份被撤下的讲义里，出现了本不该被公开的神名旁注。",
        "black_market_broker": "昨夜有人开出过高价格，想买一件连名字都不愿说清的东西。",
    }
    return hooks.get(background_id, "你来到这里并非偶然。某个细节正在等待你先开口。")


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


def default_scene_focus(city_name):
    return f"{city_name}的开放街区"


def current_scene_focus_for_state(state):
    if not is_world_mode_state(state):
        return state.current_location
    focus = state.player.flags.get(CURRENT_SCENE_FOCUS_FLAG)
    if focus:
        return focus
    return default_scene_focus(state.current_location)


def set_current_scene_focus(state, scene_focus):
    focus = str(scene_focus or "").strip()
    if not focus:
        focus = default_scene_focus(state.current_location)
    state.player.flags[CURRENT_SCENE_FOCUS_FLAG] = focus
    history = list(state.player.flags.get(SCENE_FOCUS_HISTORY_FLAG, []))
    if not history or history[-1] != focus:
        history.append(focus)
    state.player.flags[SCENE_FOCUS_HISTORY_FLAG] = history[-12:]
    return focus


def objective_for_state(state, tutorial_objective):
    if is_world_mode_state(state):
        return WORLD_MODE_OBJECTIVE
    return tutorial_objective
