# A Word Finding program made especially for the game Towers of Babble made by Everybody House Games.
# units.json was taken directly from the game files, while cursed_words.json was decompiled by AI.
# Mostly written by AI, I (Levi) simply fixed formatting, functionality and other small things.

import asyncio
import json
import multiprocessing
import os
import socket
import sys
import base64
import threading
import time
from itertools import combinations_with_replacement, product
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import quote_plus


# Theme, Naming & Canonical Stat Ordering
KIND_META = {
    "TOWER": {
        "display": "tower",
        "color": "#FF5604",       # Orange
        "button_color": "#C84300",
        "soft_bg": "#FFE7DA",
    },
    "MOD": {
        "display": "mod",
        "color": "#e858a8",       # Pink
        "button_color": "#BE2F7F",
        "soft_bg": "#F8DDF0",
    },
    "HARVESTER": {
        "display": "harvester",
        "color": "#1E7D32",       # Green
        "button_color": "#1B702D",
        "soft_bg": "#DCF0DF",
    },
    "CURSED": {
        "display": "cursed",
        "color": "#6e13be",       # Purple
        "button_color": "#6e13be",
        "soft_bg": "#E7D5F5",
    },
}

RESOURCE_COLORS = {
    "ore": ("O", "#303030", "#AAAAAA"),
    "crystal": ("C", "#134B73", "#88C9FE"),
    "wood": ("W", "#1E5626", "#8BD094"),
}

TOWER_DEFAULTS = {
    "damage": 5.0,
    "range": 4.0,
    "attackInterval": 1.0,
    "attackSpeed": 2.0,
    "health": 100.0,
    "armor": 1.0,
}

HARVESTER_DEFAULTS = {
    "health": 120.0,
    "armor": 0.0,
    "harvestAmount": 2.0,
    "harvestInterval": 3.2,
    "harvestTypes": 1,
    "harvestRange": 3.0,
}

# Canonical order for Effect / Resource dropdown
EFFECT_RESOURCE_ORDER: List[str] = [
    "damage",
    "dmg_buff_aura",
    "attack_speed",
    "firerate_buff_aura",
    "toughness",
    "heal_aura",
    "armor",
    "armor_buff_aura",
    "crit",
    "range",
    "burn",
    "burn_aura",
    "poison",
    "curse",
    "slow",
    "slow_aura",
    "knockback",
    "stun",
    "multishot",
    "pierce",
    "armor_shred",
    "splash",
    "chain",
    "res:ore",
    "res:crystal",
    "res:wood",
    "harvest_amount",
    "harvest_speed",
    "multi_harvest",
    "harvest_aura",
    "base_range",
    "base_health",
    "no_healing",
    "one_mod_slot",
    "no_nearby_buildings",
    "no_nearby_resources",
]

# Canonical display names (incorporating all requested renames)
DISPLAY_NAMES: Dict[str, str] = {
    "curse": "Curse",
    "damage": "Damage",
    "dps": "DPS",
    "dmg_buff_aura": "Damage Aura",
    "attack_speed": "Attack Speed",
    "firerate_buff_aura": "Atk Spd Aura",
    "toughness": "HP",
    "health": "HP",
    "heal_aura": "Heal Aura",
    "armor": "Armor",
    "armor_buff_aura": "Armor Aura",
    "crit": "Crit",
    "range": "Range",
    "burn": "Burn",
    "burn_aura": "Burn Aura",
    "poison": "Poison",
    "slow": "Slow",
    "slow_aura": "Slow Aura",
    "knockback": "Knockback",
    "stun": "Stun",
    "multishot": "Multi Shot",
    "pierce": "Pierce",
    "armor_shred": "Shred",
    "splash": "Splash",
    "chain": "Chain",
    "res:ore": "Resource Ore",
    "res:crystal": "Resource Crystal",
    "res:wood": "Resource Wood",
    "harvest_amount": "Harvest Amount",
    "harvest_speed": "Harvest Speed",
    "harvest_rate": "Harvest Rate",
    "harvest_types": "Resource Types",
    "multi_harvest": "Multi Harvest",
    "harvest_aura": "Harvest Aura",
    "base_range": "Base Range",
    "base_health": "Base Health",
    "no_healing": "No Healing",
    "one_mod_slot": "One Mod Slot",
    "no_nearby_buildings": "No Nearby Buildings",
    "no_nearby_resources": "No Nearby Resources",
}

STAT_FILTERS: List[Tuple[str, str, str, str]] = [
    ("toughness", "HEALTH", "#2A732E", "#FFFFFF"),
    ("armor", "ARMOR", "#835C4F", "#FFFFFF"),
    ("damage", "DAMAGE", "#C22727", "#FFFFFF"),
    ("attack_speed", "ATTACK SPEED", "#9C2ACC", "#FFFFFF"),
    ("range", "RANGE", "#1564BE", "#FFFFFF"),
    ("multishot", "MULTISHOT", "#A44B07", "#FFFFFF"),
    ("splash", "SPLASH", "#155FD2", "#FFFFFF"),
    ("chain", "CHAIN", "#7D6100", "#FFFFFF"),
    ("pierce", "PIERCE", "#C21862", "#FFFFFF"),
    ("crit", "CRIT", "#AC4500", "#FFFFFF"),
    ("poison", "POISON", "#237429", "#FFFFFF"),
    ("slow", "SLOW", "#1564BE", "#FFFFFF"),
    ("stun", "STUN", "#676900", "#FFFFFF"),
    ("knockback", "KNOCKBACK", "#BF1871", "#FFFFFF"),
    ("armor_shred", "SHRED", "#A84800", "#FFFFFF"),
    ("dmg_buff_aura", "DAMAGE AURA", "#C51F1F", "#FFFFFF"),
    ("firerate_buff_aura", "ATTACK SPEED AURA", "#962AD7", "#FFFFFF"),
    ("armor_buff_aura", "ARMOR AURA", "#835C50", "#FFFFFF"),
    ("heal_aura", "HEAL AURA", "#2C732F", "#FFFFFF"),
    ("slow_aura", "SLOW AURA", "#155FD2", "#FFFFFF"),
    ("burn_aura", "BURN AURA", "#C22727", "#FFFFFF"),
    ("harvest_amount", "HARVEST AMOUNT", "#457024", "#FFFFFF"),
    ("harvest_speed", "HARVEST SPEED", "#4E6E2F", "#FFFFFF"),
    ("multi_harvest", "MULTI HARVEST", "#2A732E", "#FFFFFF"),
    ("harvest_aura", "HARVEST AURA", "#237429", "#FFFFFF"),
    ("curse", "CURSE", "#962AD7", "#FFFFFF"),
    ("dps", "DPS", "#B71C1C", "#FFFFFF"),
]
STAT_FILTER_TOOLTIPS: Dict[str, str] = {
    "dps": (
        "Not a stat found in the game — an approximation based on "
        "Damage, Attack Speed, and Crit."
    ),
}
STAT_FILTER_BITS: Dict[str, int] = {
    stat_key: 1 << index
    for index, (stat_key, _, _, _) in enumerate(STAT_FILTERS)
}
_CHAR_BITS: Dict[str, int] = {chr(97 + i): 1 << i for i in range(26)}
_KIND_LOOKUP: Dict[str, str] = {
    "TOWER": "TOWER",
    "HARVESTER": "HARVESTER",
    "MOD": "MOD",
    "MODIFIER_QUALITY": "MOD",
    "MODIFIER_ACTION": "MOD",
}
_BIT_DAMAGE = STAT_FILTER_BITS["damage"]
_BIT_DPS = STAT_FILTER_BITS["dps"]
_BIT_ATTACK_SPEED = STAT_FILTER_BITS["attack_speed"]
_BIT_TOUGHNESS = STAT_FILTER_BITS["toughness"]
_BIT_ARMOR = STAT_FILTER_BITS["armor"]
_BIT_RANGE = STAT_FILTER_BITS["range"]
_BIT_HARVEST_AMOUNT = STAT_FILTER_BITS["harvest_amount"]
_BIT_HARVEST_SPEED = STAT_FILTER_BITS["harvest_speed"]
_BIT_CURSE = STAT_FILTER_BITS["curse"]
_TOWER_DEFAULT_DPS = 5.5
_TOWER_DMG_POS = TOWER_DEFAULTS["damage"] + 0.01
_TOWER_DPS_POS = _TOWER_DEFAULT_DPS + 0.01
_TOWER_SPD_POS = TOWER_DEFAULTS["attackSpeed"] + 0.01
_TOWER_HP_TAG = TOWER_DEFAULTS["health"] + 0.1
_TOWER_HP_POS = TOWER_DEFAULTS["health"] + 0.01
_TOWER_ARM_POS = TOWER_DEFAULTS["armor"] + 0.01
_TOWER_RNG_POS = TOWER_DEFAULTS["range"] + 0.01
_HARV_HP_TAG = HARVESTER_DEFAULTS["health"] + 0.1
_HARV_HP_POS = HARVESTER_DEFAULTS["health"] + 0.01
_HARV_RNG_POS = HARVESTER_DEFAULTS["harvestRange"] + 0.01
_HARV_AMT_POS = HARVESTER_DEFAULTS["harvestAmount"] + 0.01
_HARV_INT_TAG = HARVESTER_DEFAULTS["harvestInterval"] - 0.01
_HARV_SPD_POS = (1.0 / HARVESTER_DEFAULTS["harvestInterval"]) + 0.01


def lighten_stat_filter_color(color: str, amount: float = 0.82) -> str:
    channels = [int(color[index : index + 2], 16) for index in (1, 3, 5)]
    light_channels = [
        round(channel + (255 - channel) * amount) for channel in channels
    ]
    return "#" + "".join(f"{channel:02X}" for channel in light_channels)


def normalize_kind(raw_kind: str) -> str:
    """Unify MODIFIER_QUALITY / MODIFIER_ACTION into 'MOD'."""
    k = str(raw_kind or "TOWER").upper()
    if k.startswith("MODIFIER") or k == "MOD":
        return "MOD"
    if k == "HARVESTER":
        return "HARVESTER"
    return "TOWER"


def pretty_name(key: str) -> str:
    """Convert internal stat/effect/resource key into the requested display label."""
    if key in DISPLAY_NAMES:
        return DISPLAY_NAMES[key]
    return key.replace("_", " ").title()


def fmt_num(val: Optional[float], decimals: int = 2) -> str:
    """Format a float cleanly without unnecessary trailing zeros."""
    if val is None:
        return "—"
    if abs(val - round(val)) < 1e-6:
        return str(int(round(val)))
    return f"{val:.{decimals}f}".rstrip("0").rstrip(".")


def attack_rate_from_stat(stat: float) -> float:
    """Convert game attack-speed points to attacks per second."""
    return (max(0.01, stat) / 2.0) ** 0.78


def crit_chance_from_stat(stat: float) -> float:
    """Return the game's critical-hit chance for the given crit points."""
    progress = min(1.0, max(0.0, stat / 1000.0))
    return 0.1 + 0.4 * progress


def crit_multiplier_from_stat(stat: float) -> float:
    """Return the game's critical damage multiplier for the given crit points."""
    chance = crit_chance_from_stat(stat)
    crit_damage = 1.1 + 7.0 * stat / 1000.0
    return 1.0 + (crit_damage - 1.0) / chance


def format_crit_summary(stat: float) -> str:
    chance = crit_chance_from_stat(stat)
    multiplier = crit_multiplier_from_stat(stat)
    return f"{fmt_num(chance * 100, 0)}% x{fmt_num(multiplier, 1)}"


def consume_word_letters(available_letters: str, word: str) -> Tuple[str, int]:
    """
    Remove the letters needed to spell `word` from `available_letters`.
    Exact letter matches are consumed first; wildcards (? or *) fill missing letters.
    Returns (remaining_letters_upper, letters_consumed_count).
    """
    chars = [
        ch.upper()
        for ch in available_letters
        if ("a" <= ch.lower() <= "z") or ch in ("?", "*")
    ]
    if not chars:
        return "", 0

    consumed = 0
    for needed in word.upper():
        if not ("A" <= needed <= "Z"):
            continue
        if needed in chars:
            chars.remove(needed)
            consumed += 1
        elif "?" in chars:
            chars.remove("?")
            consumed += 1
        elif "*" in chars:
            chars.remove("*")
            consumed += 1
    return "".join(chars), consumed


# User Data Persistence (user_data.json)
DEFAULT_DICTIONARY_URL = "https://onelook.com/?w="


def normalize_dictionary_url(raw_url: Any) -> str:
    if not isinstance(raw_url, str):
        return DEFAULT_DICTIONARY_URL
    cleaned = raw_url.strip().replace('"', "").replace("'", "")
    if not cleaned:
        return DEFAULT_DICTIONARY_URL
    lower = cleaned.lower()
    if lower.startswith(("http://", "https://")):
        return cleaned
    if "://" in cleaned or lower.startswith("javascript:"):
        return DEFAULT_DICTIONARY_URL
    return f"https://{cleaned}"


def build_definition_url(base_url: str, word: str) -> str:
    cleaned = normalize_dictionary_url(base_url)
    encoded = quote_plus(word)
    if "{word}" in cleaned:
        return cleaned.replace("{word}", encoded)
    return f"{cleaned}{encoded}"


def resolve_user_data_path() -> Path:
    if getattr(sys, "frozen", False):
        app_dir = Path(sys.executable).resolve().parent
    else:
        app_dir = Path(__file__).resolve().parent

    candidate = app_dir / "user_data.json"
    if os.access(str(app_dir), os.W_OK):
        return candidate
    return Path.home() / "user_data.json"


def resolve_legacy_favorites_path() -> Path:
    if getattr(sys, "frozen", False):
        app_dir = Path(sys.executable).resolve().parent
    else:
        app_dir = Path(__file__).resolve().parent

    candidate = app_dir / "favorites.txt"
    if candidate.is_file():
        return candidate
    return Path.home() / "favorites.txt"


def normalize_user_data(data: Any) -> Dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("User data must be a JSON object.")

    if "favorites" not in data:
        raise ValueError("User data must include a 'favorites' list.")
    favorites = data["favorites"]
    if not isinstance(favorites, list) or any(
        not isinstance(word, str) for word in favorites
    ):
        raise ValueError("'favorites' must be a list of words.")

    normalized = dict(data)
    normalized.setdefault("version", 1)
    normalized["favorites"] = sorted(
        {word.strip().lower() for word in favorites if word.strip()}
    )
    normalized["dictionary_url"] = normalize_dictionary_url(
        data.get("dictionary_url", DEFAULT_DICTIONARY_URL)
    )
    return normalized


def load_user_data_json(path: Path) -> Dict[str, Any]:
    return normalize_user_data(json.loads(path.read_text(encoding="utf-8")))


def save_user_data_json(path: Path, user_data: Dict[str, Any]) -> None:
    path.write_text(
        json.dumps(user_data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def resolve_blacklist_path() -> Path:
    if getattr(sys, "frozen", False):
        app_dir = Path(sys.executable).resolve().parent
    else:
        app_dir = Path(__file__).resolve().parent
    return app_dir / "blacklist.txt"


def parse_word_list(contents: str) -> Set[str]:
    return {
        line.strip().lower()
        for line in contents.splitlines()
        if line.strip()
    }


def validate_units_json(data: Any, *, require_cursed: bool = False) -> int:
    raw_units = data.get("units") if isinstance(data, dict) else data
    if not isinstance(raw_units, list):
        raise ValueError("JSON must contain a list of units.")

    count = 0
    has_cursed = False
    for unit in raw_units:
        if not isinstance(unit, dict):
            continue
        word = unit.get("word")
        if isinstance(word, str):
            if not word or (word[0].isspace() and not word.strip()):
                continue
        elif not str(word or "").strip():
            continue
        count += 1
        if require_cursed and not has_cursed and unit.get("isCursed"):
            has_cursed = True

    if count == 0:
        raise ValueError("No word records were found.")
    if require_cursed and not has_cursed:
        raise ValueError("No cursed towers were found.")
    return count


def format_file_size(size_bytes: int) -> str:
    size = float(size_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"

# Unit Data Model & Fast Search Engine
class UnitRecord:
    """Pre-indexed representation of a single Towers of Babble unit (no budget stat)."""

    __slots__ = (
        "word",
        "word_upper",
        "length",
        "mask",
        "kind",
        "raw_kind",
        "scrabble",
        "damage",
        "range",
        "attack_interval",
        "attack_speed",
        "attacks_per_second",
        "dps",
        "health",
        "armor",
        "targeting",
        "harvest_amount",
        "harvest_interval",
        "harvest_speed",
        "harvest_rate",
        "harvest_types",
        "harvest_range",
        "harvest_resources",
        "specials",
        "deltas",
        "effect_tags",
        "is_cursed",
        "curse_effects",
        "_preview_stats",
        "_positive_stat_mask",
    )

    def __init__(self, u: Dict[str, Any]):
        get = u.get
        raw_word = get("word", "")
        w = (
            raw_word.strip().lower()
            if type(raw_word) is str
            else str(raw_word).strip().lower()
        )
        self.word = w
        self.word_upper = w.upper()
        self.length = len(w)

        mask = 0
        char_bits = _CHAR_BITS
        for ch in w:
            bit = char_bits.get(ch)
            if bit is not None:
                mask |= bit
        self.mask = mask

        raw_kind = get("kind", "TOWER")
        if type(raw_kind) is not str:
            raw_kind = str(raw_kind)
        self.raw_kind: str = raw_kind
        kind = _KIND_LOOKUP.get(raw_kind)
        if kind is None:
            kind = normalize_kind(raw_kind)
        self.kind: str = kind

        raw_scrabble = get("scrabble", 0)
        self.scrabble: int = (
            raw_scrabble if type(raw_scrabble) is int else int(raw_scrabble)
        )

        is_cursed = bool(get("isCursed", False))
        self.is_cursed: bool = is_cursed
        raw_curse_effects = get("curseEffects") if is_cursed else None
        curse_effects: Tuple[str, ...] = (
            tuple([str(effect) for effect in raw_curse_effects])
            if raw_curse_effects
            else ()
        )
        self.curse_effects = curse_effects

        damage: Optional[float] = None
        rng: Optional[float] = None
        attack_interval: Optional[float] = None
        attack_speed: Optional[float] = None
        attacks_per_second: Optional[float] = None
        dps: Optional[float] = None
        health: Optional[float] = None
        armor: Optional[float] = None
        targeting = ""
        harvest_amount: Optional[float] = None
        harvest_interval: Optional[float] = None
        harvest_speed: Optional[float] = None
        harvest_rate: Optional[float] = None
        harvest_types: Optional[int] = None
        harvest_range: Optional[float] = None
        harvest_resources: Tuple[str, ...] = ()
        specials: Tuple[Tuple[str, float], ...] = ()
        deltas: Tuple[Tuple[str, str, float], ...] = ()

        tags: Set[str] = set()
        pos_mask = 0
        base_covered_mask = _BIT_CURSE

        if is_cursed:
            tags.add("curse")
            if curse_effects:
                tags.update(curse_effects)
            pos_mask |= _BIT_CURSE

        if kind == "TOWER":
            raw_damage = get("damage")
            if raw_damage is not None:
                damage = float(raw_damage)
                base_covered_mask |= _BIT_DAMAGE
                if damage > _TOWER_DMG_POS:
                    tags.add("damage")
                    pos_mask |= _BIT_DAMAGE

            raw_range = get("range")
            if raw_range is not None:
                rng = float(raw_range)
                base_covered_mask |= _BIT_RANGE
                if rng > _TOWER_RNG_POS:
                    tags.add("range")
                    pos_mask |= _BIT_RANGE

            raw_atk_int = get("attackInterval")
            if raw_atk_int is not None:
                attack_interval = float(raw_atk_int)
                if attack_interval > 0:
                    attack_speed = 1.0 / attack_interval + 1.0
                    attacks_per_second = (
                        (attack_speed if attack_speed > 0.01 else 0.01) / 2.0
                    ) ** 0.78
                    base_covered_mask |= _BIT_ATTACK_SPEED
                    if attack_speed > _TOWER_SPD_POS:
                        tags.add("attack_speed")
                        pos_mask |= _BIT_ATTACK_SPEED

            raw_health = get("health")
            if raw_health is not None:
                health = float(raw_health)
                base_covered_mask |= _BIT_TOUGHNESS
                if health > _TOWER_HP_POS:
                    pos_mask |= _BIT_TOUGHNESS
                    if health > _TOWER_HP_TAG:
                        tags.add("toughness")

            raw_armor = get("armor")
            armor = float(raw_armor) if raw_armor is not None else 0.0
            base_covered_mask |= _BIT_ARMOR
            if armor > _TOWER_ARM_POS:
                tags.add("armor")
                pos_mask |= _BIT_ARMOR

            raw_targeting = get("targeting", "")
            targeting = (
                raw_targeting
                if type(raw_targeting) is str
                else str(raw_targeting)
            )

            raw_specials = get("specials")
            if raw_specials:
                specials = tuple(
                    [
                        (str(s.get("name", "")), float(s.get("value", 0.0)))
                        for s in raw_specials
                    ]
                )

            if damage is not None and attacks_per_second is not None:
                crit_stat = 0.0
                for sp_name, val in specials:
                    if sp_name == "crit":
                        crit_stat = val
                        break
                dps = damage * attacks_per_second * (1.1 + 0.007 * crit_stat)
                base_covered_mask |= _BIT_DPS
                if dps > _TOWER_DPS_POS:
                    pos_mask |= _BIT_DPS

            raw_deltas = get("deltas")
            if raw_deltas:
                deltas = tuple(
                    [
                        (
                            str(d.get("stat", "")),
                            str(d.get("op", "")),
                            float(d.get("value", 0.0)),
                        )
                        for d in raw_deltas
                    ]
                )
        elif kind == "HARVESTER":
            raw_health = get("health")
            if raw_health is not None:
                health = float(raw_health)
                base_covered_mask |= _BIT_TOUGHNESS
                if health > _HARV_HP_POS:
                    pos_mask |= _BIT_TOUGHNESS
                    if health > _HARV_HP_TAG:
                        tags.add("toughness")

            raw_armor = get("armor")
            if raw_armor is not None:
                armor = float(raw_armor)
                base_covered_mask |= _BIT_ARMOR
                if armor > 0.01:
                    tags.add("armor")
                    pos_mask |= _BIT_ARMOR

            raw_h_amt = get("harvestAmount")
            if raw_h_amt is not None:
                harvest_amount = float(raw_h_amt)
                base_covered_mask |= _BIT_HARVEST_AMOUNT
                if harvest_amount > _HARV_AMT_POS:
                    tags.add("harvest_amount")
                    pos_mask |= _BIT_HARVEST_AMOUNT

            raw_h_int = get("harvestInterval")
            if raw_h_int is not None:
                harvest_interval = float(raw_h_int)
                if harvest_interval > 0:
                    harvest_speed = 1.0 / harvest_interval
                    if harvest_amount is not None:
                        harvest_rate = harvest_amount / harvest_interval
                    base_covered_mask |= _BIT_HARVEST_SPEED
                    if harvest_speed > _HARV_SPD_POS:
                        pos_mask |= _BIT_HARVEST_SPEED
                if harvest_interval < _HARV_INT_TAG:
                    tags.add("harvest_speed")

            raw_h_types = get("harvestTypes")
            if raw_h_types is not None:
                harvest_types = int(raw_h_types)

            raw_h_rng = get("harvestRange")
            if raw_h_rng is not None:
                harvest_range = float(raw_h_rng)
                base_covered_mask |= _BIT_RANGE
                if harvest_range > _HARV_RNG_POS:
                    tags.add("range")
                    pos_mask |= _BIT_RANGE

            raw_h_res = get("harvestResources")
            if raw_h_res:
                harvest_resources = tuple(raw_h_res)
                for res in harvest_resources:
                    tags.add(f"res:{res}")

            raw_specials = get("specials")
            if raw_specials:
                specials = tuple(
                    [
                        (str(s.get("name", "")), float(s.get("value", 0.0)))
                        for s in raw_specials
                    ]
                )

            raw_deltas = get("deltas")
            if raw_deltas:
                deltas = tuple(
                    [
                        (
                            str(d.get("stat", "")),
                            str(d.get("op", "")),
                            float(d.get("value", 0.0)),
                        )
                        for d in raw_deltas
                    ]
                )
        else:  # MOD
            raw_deltas = get("deltas")
            if raw_deltas:
                deltas = tuple(
                    [
                        (
                            str(d.get("stat", "")),
                            str(d.get("op", "")),
                            float(d.get("value", 0.0)),
                        )
                        for d in raw_deltas
                    ]
                )
            raw_specials = get("specials")
            if raw_specials:
                specials = tuple(
                    [
                        (str(s.get("name", "")), float(s.get("value", 0.0)))
                        for s in raw_specials
                    ]
                )

        if deltas or specials:
            seen_ds_mask = base_covered_mask
            filter_bits = STAT_FILTER_BITS
            for stat, op, value in deltas:
                tags.add(stat)
                bit = filter_bits.get(stat)
                if bit is not None and not (seen_ds_mask & bit):
                    seen_ds_mask |= bit
                    change = (
                        value - 1.0
                        if (op == "mult" or op.lower() == "mult")
                        else value
                    )
                    if change > 0.01:
                        pos_mask |= bit
            for name, value in specials:
                tags.add(name)
                bit = filter_bits.get(name)
                if bit is not None and not (seen_ds_mask & bit):
                    seen_ds_mask |= bit
                    if value > 0.01:
                        pos_mask |= bit

        self.damage = damage
        self.range = rng
        self.attack_interval = attack_interval
        self.attack_speed = attack_speed
        self.attacks_per_second = attacks_per_second
        self.dps = dps
        self.health = health
        self.armor = armor
        self.targeting = targeting
        self.harvest_amount = harvest_amount
        self.harvest_interval = harvest_interval
        self.harvest_speed = harvest_speed
        self.harvest_rate = harvest_rate
        self.harvest_types = harvest_types
        self.harvest_range = harvest_range
        self.harvest_resources = harvest_resources
        self.specials = specials
        self.deltas = deltas
        self.effect_tags = frozenset(tags)
        self._preview_stats: Optional[List[Tuple[str, str, str]]] = None
        self._positive_stat_mask = pos_mask

    def _special_val(self, name: str) -> Optional[float]:
        for sp_name, val in self.specials:
            if sp_name == name:
                return val
        return None

    def _delta_val(self, stat_name: str) -> Optional[float]:
        for stat, _, val in self.deltas:
            if stat == stat_name:
                return val
        return None

    def _base_stat_change(self, stat_key: str) -> Optional[float]:
        if stat_key == "damage" and self.kind == "TOWER" and self.damage is not None:
            return self.damage - TOWER_DEFAULTS["damage"]
        if stat_key == "dps" and self.kind == "TOWER" and self.dps is not None:
            return self.dps - _TOWER_DEFAULT_DPS
        if stat_key == "attack_speed" and self.kind == "TOWER" and self.attack_speed is not None:
            return self.attack_speed - TOWER_DEFAULTS["attackSpeed"]
        if stat_key in ("toughness", "health") and self.kind in ("TOWER", "HARVESTER") and self.health is not None:
            default_health = (
                TOWER_DEFAULTS["health"]
                if self.kind == "TOWER"
                else HARVESTER_DEFAULTS["health"]
            )
            return self.health - default_health
        if stat_key == "armor" and self.kind in ("TOWER", "HARVESTER") and self.armor is not None:
            default_armor = (
                TOWER_DEFAULTS["armor"] if self.kind == "TOWER" else 0.0
            )
            return self.armor - default_armor
        if stat_key == "range" and self.kind == "TOWER" and self.range is not None:
            return self.range - TOWER_DEFAULTS["range"]
        if stat_key == "range" and self.kind == "HARVESTER" and self.harvest_range is not None:
            return self.harvest_range - HARVESTER_DEFAULTS["harvestRange"]
        if stat_key == "harvest_amount" and self.kind == "HARVESTER" and self.harvest_amount is not None:
            return self.harvest_amount - HARVESTER_DEFAULTS["harvestAmount"]
        if stat_key == "harvest_speed" and self.kind == "HARVESTER" and self.harvest_speed is not None:
            return self.harvest_speed - (
                1.0 / HARVESTER_DEFAULTS["harvestInterval"]
            )
        return None

    def _build_positive_stat_mask(self) -> int:
        positive_by_stat: Dict[str, bool] = {}
        for stat, op, value in self.deltas:
            if stat not in positive_by_stat:
                change = value - 1.0 if op.lower() == "mult" else value
                positive_by_stat[stat] = change > 0.01
        for name, value in self.specials:
            if name not in positive_by_stat:
                positive_by_stat[name] = value > 0.01

        mask = 0
        for stat_key, bit in STAT_FILTER_BITS.items():
            if stat_key == "curse":
                is_positive = self.is_cursed
            else:
                base_change = self._base_stat_change(stat_key)
                is_positive = (
                    base_change > 0.01
                    if base_change is not None
                    else positive_by_stat.get(stat_key, False)
                )

            if is_positive:
                mask |= bit
        return mask

    def has_positive_stat_change(self, stat_key: str) -> bool:
        bit = STAT_FILTER_BITS.get(stat_key)
        return bit is not None and bool(self._positive_stat_mask & bit)

    def get_positive_stat_change(self, stat_key: str) -> Optional[float]:
        """Return a positive stat improvement for the filter chips, if present."""
        if stat_key == "curse":
            return 1.0 if self.is_cursed else None

        base_change = self._base_stat_change(stat_key)

        if base_change is not None:
            return base_change if base_change > 0.01 else None

        for stat, op, value in self.deltas:
            if stat == stat_key:
                change = value - 1.0 if op.lower() == "mult" else value
                return change if change > 0.01 else None

        special_value = self._special_val(stat_key)
        if special_value is not None and special_value > 0.01:
            return special_value
        return None

    def get_stat_value(self, stat_key: str) -> Optional[float]:
        """Return the numeric value for stat/effect sorting, or None if not applicable."""
        if stat_key == "damage":
            return self.damage if self.damage is not None else self._delta_val("damage")
        if stat_key == "dps":
            return self.dps
        if stat_key == "attack_speed":
            return self.attack_speed if self.attack_speed is not None else self._delta_val("attack_speed")
        if stat_key in ("toughness", "health"):
            return self.health if self.health is not None else self._delta_val("toughness")
        if stat_key == "armor":
            if self.armor is not None and (self.armor > 0 or self.kind == "TOWER"):
                return self.armor
            return self._delta_val("armor")
        if stat_key == "range":
            if self.range is not None:
                return self.range
            if self.harvest_range is not None:
                return self.harvest_range
            return self._delta_val("range")
        if stat_key == "harvest_amount":
            return self.harvest_amount if self.harvest_amount is not None else self._delta_val("harvest_amount")
        if stat_key == "harvest_speed":
            return self.harvest_speed if self.harvest_speed is not None else self._delta_val("harvest_speed")
        if stat_key == "harvest_rate":
            return self.harvest_rate
        if stat_key == "harvest_types":
            return float(self.harvest_types) if self.harvest_types is not None else None

        # Any special ability or modifier effect (crit, burn_aura, slow, armor_shred, etc.)
        sp = self._special_val(stat_key)
        if sp is not None:
            return sp
        return self._delta_val(stat_key)

    def get_preview_stats(
        self, priority_stat_key: Optional[str] = None
    ) -> List[Tuple[str, str, str]]:
        """
        Return up to 3 important stats for the unopened box as (val_text, label_text, tone),
        where tone is 'pos' (green), 'neg' (red), or 'neutral' (black).
        """
        if self._preview_stats is None:
            self._preview_stats = self._compute_default_preview()

        if priority_stat_key and priority_stat_key not in ("points", "alphabetical"):
            val = self.get_stat_value(priority_stat_key)
            if val is not None:
                item = self._format_priority_stat(priority_stat_key, val)
                if item:
                    base = [x for x in self._preview_stats if x[1] != item[1]]
                    return ([item] + base)[:3]

        return self._preview_stats[:3]

    def _format_priority_stat(
        self, stat_key: str, val: float
    ) -> Optional[Tuple[str, str, str]]:
        lbl = pretty_name(stat_key)
        if stat_key == "damage":
            tone = "pos" if (self.kind == "MOD" or val > 5.01) else ("neg" if val < 4.99 else "neutral")
            return (f"{'+' if self.kind == 'MOD' else ''}{fmt_num(val, 1)}", "Damage", tone)
        if stat_key == "dps":
            tone = "pos" if val > _TOWER_DPS_POS else ("neg" if val < _TOWER_DEFAULT_DPS - 0.01 else "neutral")
            return (fmt_num(val, 1), "DPS", tone)
        if stat_key == "attack_speed":
            if self.kind == "TOWER":
                delta = val - TOWER_DEFAULTS["attackSpeed"]
                tone = "pos" if delta > 0.01 else ("neg" if delta < -0.01 else "neutral")
                value = f"+{fmt_num(delta, 2)}" if delta > 0 else fmt_num(delta, 2)
                return (value, "Attack Speed", tone)
            return (f"+{fmt_num(val, 2)}", "Attack Speed", "pos")
        if stat_key in ("toughness", "health"):
            if self.kind == "MOD":
                return (f"+{fmt_num(val, 1)}", "HP", "pos")
            dflt = 100.0 if self.kind == "TOWER" else 120.0
            tone = "pos" if val > dflt + 0.1 else ("neg" if val < dflt - 0.1 else "neutral")
            return (fmt_num(val, 0), "HP", tone)
        if stat_key == "armor":
            tone = "pos" if (self.kind == "MOD" or val > 1.01) else ("neg" if self.kind == "TOWER" and val < 0.99 else "neutral")
            return (f"{'+' if self.kind == 'MOD' else ''}{fmt_num(val, 1)}", "Armor", tone)
        if stat_key == "range":
            if self.kind == "MOD":
                return (f"+{fmt_num(val, 2)}", "Range", "pos")
            dflt = 4.0 if self.kind == "TOWER" else 3.0
            tone = "pos" if val > dflt + 0.01 else ("neg" if val < dflt - 0.01 else "neutral")
            return (fmt_num(val, 1), "Range", tone)
        if stat_key == "harvest_amount":
            tone = "pos" if (self.kind == "MOD" or val > 2.01) else ("neg" if val < 1.99 else "neutral")
            return (f"{'+' if self.kind == 'MOD' else ''}{fmt_num(val, 1)}", "Harvest Amount", tone)
        if stat_key == "harvest_speed":
            if self.kind == "HARVESTER":
                tone = "pos" if val > (1.0 / 3.2) + 0.01 else ("neg" if val < (1.0 / 3.2) - 0.01 else "neutral")
                return (f"{fmt_num(val, 2)}/s", "Harvest Speed", tone)
            return (f"+{fmt_num(val, 2)}", "Harvest Speed", "pos")
        if stat_key == "harvest_rate":
            tone = "pos" if val > (2.0 / 3.2) + 0.01 else ("neg" if val < (2.0 / 3.2) - 0.01 else "neutral")
            return (f"{fmt_num(val, 2)}/s", "Harvest Rate", tone)
        if stat_key == "harvest_types":
            return (fmt_num(val, 0), "Resource Types", "pos" if val > 1 else "neutral")
        return (f"+{fmt_num(val, 2)}", lbl, "pos")

    def _compute_default_preview(self) -> List[Tuple[str, str, str]]:
        """Pick up to 3 most important stats for the unopened unit box."""
        items: List[Tuple[str, str, str]] = []

        if self.kind == "TOWER":
            # 1. Special abilities first (e.g., +40.32 Burn Aura)
            for name, val in self.specials:
                items.append((f"+{fmt_num(val, 2)}", pretty_name(name), "pos"))

            # 2. Boosted base stats
            if self.damage is not None and self.damage > TOWER_DEFAULTS["damage"] + 0.01:
                items.append((fmt_num(self.damage, 1), "Damage", "pos"))
            if self.attack_speed is not None and self.attack_speed > TOWER_DEFAULTS["attackSpeed"] + 0.01:
                items.append(
                    (
                        f"+{fmt_num(self.attack_speed - TOWER_DEFAULTS['attackSpeed'], 2)}",
                        "Attack Speed",
                        "pos",
                    )
                )
            if self.range is not None and self.range > TOWER_DEFAULTS["range"] + 0.01:
                items.append((fmt_num(self.range, 1), "Range", "pos"))
            if self.health is not None and self.health > TOWER_DEFAULTS["health"] + 0.1:
                items.append((fmt_num(self.health, 0), "HP", "pos"))
            if self.armor is not None and self.armor > TOWER_DEFAULTS["armor"] + 0.01:
                items.append((fmt_num(self.armor, 1), "Armor", "pos"))

            # 3. Drawbacks
            if self.damage is not None and self.damage < TOWER_DEFAULTS["damage"] - 0.01:
                items.append((fmt_num(self.damage, 1), "Damage", "neg"))
            if self.attack_speed is not None and self.attack_speed < TOWER_DEFAULTS["attackSpeed"] - 0.01:
                delta = self.attack_speed - TOWER_DEFAULTS["attackSpeed"]
                items.append((fmt_num(delta, 2), "Attack Speed", "neg"))
            if self.range is not None and self.range < TOWER_DEFAULTS["range"] - 0.01:
                items.append((fmt_num(self.range, 1), "Range", "neg"))
            if self.health is not None and self.health < TOWER_DEFAULTS["health"] - 0.1:
                items.append((fmt_num(self.health, 0), "HP", "neg"))
            if self.armor is not None and self.armor < TOWER_DEFAULTS["armor"] - 0.01:
                items.append(("0", "Armor", "neg"))

            return items[:3]

        if self.kind == "HARVESTER":
            if self.harvest_resources:
                res_txt = "/".join(r.title() for r in self.harvest_resources)
                tone = "pos" if len(self.harvest_resources) > 1 else "neutral"
                items.append((res_txt, "", tone))

            for name, val in self.specials:
                items.append((f"+{fmt_num(val, 2)}", pretty_name(name), "pos"))

            if self.harvest_amount is not None and self.harvest_interval is not None:
                boosted = (
                    self.harvest_amount > HARVESTER_DEFAULTS["harvestAmount"] + 0.01
                    or self.harvest_interval < HARVESTER_DEFAULTS["harvestInterval"] - 0.01
                )
                reduced = (
                    self.harvest_amount < HARVESTER_DEFAULTS["harvestAmount"] - 0.01
                    or self.harvest_interval > HARVESTER_DEFAULTS["harvestInterval"] + 0.01
                )
                if boosted or reduced:
                    tone = "pos" if boosted else "neg"
                    items.append(
                        (f"{fmt_num(self.harvest_amount, 1)}/{fmt_num(self.harvest_interval, 2)}s", "Harvest", tone)
                    )

            if len(items) < 3 and self.harvest_range is not None and abs(self.harvest_range - 3.0) > 0.01:
                tone = "pos" if self.harvest_range > 3.0 else "neg"
                items.append((fmt_num(self.harvest_range, 1), "Range", tone))
            if len(items) < 3 and self.health is not None and abs(self.health - 120.0) > 0.1:
                tone = "pos" if self.health > 120.0 else "neg"
                items.append((fmt_num(self.health, 0), "HP", tone))
            if len(items) < 3 and self.armor is not None and self.armor > 0.01:
                items.append((fmt_num(self.armor, 1), "Armor", "pos"))
            return items[:3]

        # MOD
        if not self.deltas:
            return [("—", "No effects", "neutral")]
        for stat, op, val in self.deltas[:3]:
            lbl = pretty_name(stat)
            if op == "mult":
                items.append((f"×{fmt_num(val, 3)}", lbl, "pos"))
            else:
                items.append((f"+{fmt_num(val, 2)}", lbl, "pos"))
        return items


CLEVER_MAX_COMBINATIONS = 5000
CLEVER_TIME_LIMIT_SECONDS = 2.0


def find_exact_word_combinations(
    records: List[UnitRecord],
    available_letters: str,
    include_two_letter_words: bool,
    *,
    max_combinations: int = CLEVER_MAX_COMBINATIONS,
    time_limit_seconds: float = CLEVER_TIME_LIMIT_SECONDS,
    cancel_event: Optional[threading.Event] = None,
) -> Tuple[List[Tuple[UnitRecord, ...]], bool]:
    if cancel_event is not None and cancel_event.is_set():
        return [], False
    rack = [
        ch.lower()
        for ch in available_letters
        if ("a" <= ch.lower() <= "z") or ch in ("?", "*")
    ]
    if not rack:
        return [], False

    rack_counts = [0] * 26
    wildcards = 0
    for ch in rack:
        if ch in ("?", "*"):
            wildcards += 1
        else:
            rack_counts[ord(ch) - ord("a")] += 1

    rack_length = len(rack)
    min_word_length = 2 if include_two_letter_words else 3
    if rack_length < min_word_length:
        return [], False

    rack_mask = 0
    for letter_index, count in enumerate(rack_counts):
        if count:
            rack_mask |= 1 << letter_index
    not_rack_mask = ~rack_mask

    # Group candidate words by exact letter-count signature (anagram buckets).
    groups_by_sig: Dict[Tuple[int, ...], List[UnitRecord]] = {}
    for rec in sorted(records, key=lambda item: item.word):
        if rec.length < min_word_length or rec.length > rack_length:
            continue
        if wildcards == 0 and (rec.mask & not_rack_mask):
            continue
        counts = [0] * 26
        valid_word = True
        for ch in rec.word:
            if not ("a" <= ch <= "z"):
                valid_word = False
                break
            counts[ord(ch) - ord("a")] += 1
        if not valid_word:
            continue
        wildcards_needed = 0
        for i in range(26):
            if counts[i] > rack_counts[i]:
                wildcards_needed += counts[i] - rack_counts[i]
                if wildcards_needed > wildcards:
                    break
        if wildcards_needed > wildcards:
            continue
        groups_by_sig.setdefault(tuple(counts), []).append(rec)

    if not groups_by_sig:
        return [], False

    ordered_sigs = sorted(
        groups_by_sig.keys(), key=lambda sig: groups_by_sig[sig][0].word
    )
    group_words: List[Tuple[UnitRecord, ...]] = []
    group_sigs: List[Tuple[int, ...]] = []
    group_sparse: List[Tuple[Tuple[int, int], ...]] = []
    group_masks: List[int] = []
    group_lens: List[int] = []
    sig_to_group: Dict[Tuple[int, ...], int] = {}
    groups_by_len: Dict[int, List[int]] = {}
    groups_by_letter: List[List[int]] = [[] for _ in range(26)]
    groups_by_letter_and_len: Dict[Tuple[int, int], List[int]] = {}

    for gi, sig in enumerate(ordered_sigs):
        words = tuple(groups_by_sig[sig])
        word_len = words[0].length
        sparse = tuple((i, c) for i, c in enumerate(sig) if c)
        mask = 0
        for i, _ in sparse:
            mask |= 1 << i
            groups_by_letter[i].append(gi)
            groups_by_letter_and_len.setdefault((i, word_len), []).append(gi)

        group_words.append(words)
        group_sigs.append(sig)
        group_sparse.append(sparse)
        group_masks.append(mask)
        group_lens.append(word_len)
        sig_to_group[sig] = gi
        groups_by_len.setdefault(word_len, []).append(gi)

    max_group_len = max(group_lens)
    max_words = rack_length // min_word_length
    deadline = time.monotonic() + time_limit_seconds

    results: List[Tuple[UnitRecord, ...]] = []
    seen_sig_combos: Set[Tuple[int, ...]] = set()
    failed_states: Set[Tuple[Tuple[int, ...], int, int]] = set()
    truncated = False
    stopped = False
    steps = 0

    def check_stop() -> bool:
        nonlocal steps, stopped, truncated
        if stopped:
            return True
        steps += 1
        if (steps & 255) == 0:
            if cancel_event is not None and cancel_event.is_set():
                stopped = True
                return True
            if time.monotonic() >= deadline:
                truncated = True
                stopped = True
                return True
        return False

    def emit_sig_combo(sig_combo: Tuple[int, ...]) -> None:
        nonlocal truncated, stopped
        if sig_combo in seen_sig_combos:
            return
        seen_sig_combos.add(sig_combo)

        factor_lists: List[Tuple[Tuple[UnitRecord, ...], ...]] = []
        idx = 0
        n_sig = len(sig_combo)
        while idx < n_sig:
            gi = sig_combo[idx]
            end = idx + 1
            while end < n_sig and sig_combo[end] == gi:
                end += 1
            mult = end - idx
            if mult == 1:
                factor_lists.append(tuple((w,) for w in group_words[gi]))
            else:
                factor_lists.append(
                    tuple(combinations_with_replacement(group_words[gi], mult))
                )
            idx = end

        for chunks in product(*factor_lists):
            flat = tuple(
                sorted(
                    (rec for chunk in chunks for rec in chunk),
                    key=lambda item: item.word,
                )
            )
            results.append(flat)
            if len(results) >= max_combinations:
                truncated = True
                stopped = True
                return

    def consume_group(
        remaining: Tuple[int, ...],
        rem_mask: int,
        wildcards_left: int,
        gi: int,
    ) -> Optional[Tuple[Tuple[int, ...], int, int]]:
        if wildcards_left == 0:
            if group_masks[gi] & ~rem_mask:
                return None
            for letter_idx, need in group_sparse[gi]:
                if need > remaining[letter_idx]:
                    return None
            updated = list(remaining)
            new_mask = rem_mask
            for letter_idx, need in group_sparse[gi]:
                left = updated[letter_idx] - need
                updated[letter_idx] = left
                if left == 0:
                    new_mask &= ~(1 << letter_idx)
            return tuple(updated), new_mask, 0

        wildcards_needed = 0
        for letter_idx, need in group_sparse[gi]:
            avail = remaining[letter_idx]
            if need > avail:
                wildcards_needed += need - avail
                if wildcards_needed > wildcards_left:
                    return None
        updated = list(remaining)
        new_mask = rem_mask
        for letter_idx, need in group_sparse[gi]:
            avail = updated[letter_idx]
            if need < avail:
                updated[letter_idx] = avail - need
            elif avail:
                updated[letter_idx] = 0
                new_mask &= ~(1 << letter_idx)
        return tuple(updated), new_mask, wildcards_left - wildcards_needed

    def dfs(
        remaining: Tuple[int, ...],
        rem_mask: int,
        rem_len: int,
        wildcards_left: int,
        words_left: int,
        path: Tuple[int, ...],
    ) -> bool:
        if check_stop():
            return False
        if (
            rem_len < words_left * min_word_length
            or rem_len > words_left * max_group_len
        ):
            return False

        if words_left == 1:
            if wildcards_left == 0:
                gi = sig_to_group.get(remaining)
                if gi is None:
                    return False
                emit_sig_combo(tuple(sorted(path + (gi,))))
                return True

            if rem_mask == 0:
                cands = groups_by_len.get(rem_len)
                if not cands:
                    return False
                for gi in cands:
                    emit_sig_combo(tuple(sorted(path + (gi,))))
                    if stopped or check_stop():
                        return True
                return True

            pivot = -1
            best_count = 1 << 30
            rem_pairs: List[Tuple[int, int]] = []
            mask_iter = rem_mask
            while mask_iter:
                bit = mask_iter & -mask_iter
                letter_idx = bit.bit_length() - 1
                mask_iter ^= bit
                rem_pairs.append((letter_idx, remaining[letter_idx]))
                bucket = groups_by_letter_and_len.get((letter_idx, rem_len))
                if not bucket:
                    return False
                if len(bucket) < best_count:
                    best_count = len(bucket)
                    pivot = letter_idx

            found_any = False
            for gi in groups_by_letter_and_len[(pivot, rem_len)]:
                if (group_masks[gi] & rem_mask) != rem_mask:
                    continue
                sig = group_sigs[gi]
                ok = True
                for letter_idx, need_avail in rem_pairs:
                    if sig[letter_idx] < need_avail:
                        ok = False
                        break
                if ok:
                    found_any = True
                    emit_sig_combo(tuple(sorted(path + (gi,))))
                    if stopped or check_stop():
                        return True
            return found_any

        state_key = (remaining, wildcards_left, words_left)
        if state_key in failed_states:
            return False

        if rem_mask != 0:
            pivot = -1
            best_count = 1 << 30
            mask_iter = rem_mask
            while mask_iter:
                bit = mask_iter & -mask_iter
                letter_idx = bit.bit_length() - 1
                mask_iter ^= bit
                bucket = groups_by_letter[letter_idx]
                if not bucket:
                    failed_states.add(state_key)
                    return False
                if len(bucket) < best_count:
                    best_count = len(bucket)
                    pivot = letter_idx
            candidate_groups = groups_by_letter[pivot]
        else:
            candidate_groups = range(len(group_words))

        max_next_len = rem_len - (words_left - 1) * min_word_length
        min_next_len = max(
            min_word_length, rem_len - (words_left - 1) * max_group_len
        )
        found_any = False
        for gi in candidate_groups:
            glen = group_lens[gi]
            if glen < min_next_len or glen > max_next_len:
                continue
            next_state = consume_group(remaining, rem_mask, wildcards_left, gi)
            if next_state is None:
                continue
            next_rem, next_mask, next_wild = next_state
            if dfs(
                next_rem,
                next_mask,
                rem_len - glen,
                next_wild,
                words_left - 1,
                path + (gi,),
            ):
                found_any = True
            if stopped:
                return found_any

        if not found_any and not stopped:
            failed_states.add(state_key)
        return found_any

    initial_remaining = tuple(rack_counts)
    # Iterative deepening by word count finds shortest combinations first.
    for target_words in range(1, max_words + 1):
        if stopped:
            break
        dfs(
            initial_remaining,
            rack_mask,
            rack_length,
            wildcards,
            target_words,
            (),
        )

    results.sort(key=lambda combo: (len(combo), tuple(rec.word for rec in combo)))
    return results, truncated


class UnitDatabase:
    """Loads, indexes, filters, and sorts Towers of Babble units."""

    def __init__(self):
        self.units: List[UnitRecord] = []
        self.available_tags: Set[str] = set()
        self.revision: int = 0
        self._base_records: List[UnitRecord] = []
        self._extra_records: List[UnitRecord] = []
        self.blacklist_path = resolve_blacklist_path()
        self.blacklisted_words: Set[str] = set()
        self.blacklist_source_label = ""
        self.blacklist_size_bytes: Optional[int] = None
        self.blacklist_loaded = False
        self._blacklist_checked = False
        self.extra_source_path: str = ""
        self.extra_source_size_bytes: Optional[int] = None
        self.max_len: int = 15
        self.source_path: str = ""
        self.source_size_bytes: Optional[int] = None

    def ensure_blacklist_loaded(self) -> None:
        if self._blacklist_checked:
            return
        self._blacklist_checked = True
        try:
            if self.blacklist_path.is_file():
                contents = self.blacklist_path.read_bytes()
                self.blacklisted_words = parse_word_list(
                    contents.decode("utf-8")
                )
                self.blacklist_source_label = self.blacklist_path.name
                self.blacklist_size_bytes = len(contents)
                self.blacklist_loaded = True
        except (OSError, UnicodeDecodeError) as exc:
            print(f"Could not load {self.blacklist_path.name}: {exc}")

    def load_data(
        self,
        data: Any,
        source_label: str = "",
        source_size_bytes: Optional[int] = None,
        *,
        refresh: bool = True,
    ) -> int:
        self.ensure_blacklist_loaded()
        raw_units = data.get("units", []) if isinstance(data, dict) else data
        unit_record = UnitRecord
        records: List[UnitRecord] = []
        append = records.append

        for u in raw_units:
            if type(u) is not dict and not isinstance(u, dict):
                continue
            if "word" not in u:
                continue
            rec = unit_record(u)
            if rec.word:
                append(rec)

        self._base_records = records
        self.source_path = source_label
        self.source_size_bytes = source_size_bytes
        if refresh:
            self._refresh_records()
        return len(self.units) if refresh else len(records)

    def load_file(self, filepath: str) -> int:
        raw_bytes = Path(filepath).read_bytes()
        data = json.loads(raw_bytes.decode("utf-8"))
        return self.load_data(
            data,
            source_label=filepath,
            source_size_bytes=len(raw_bytes),
        )

    def load_extra_data(
        self,
        data: Any,
        source_label: str = "",
        source_size_bytes: Optional[int] = None,
        *,
        refresh: bool = True,
    ) -> int:
        self.ensure_blacklist_loaded()
        raw_units = data.get("units", []) if isinstance(data, dict) else data
        unit_record = UnitRecord
        records: List[UnitRecord] = []
        append = records.append
        for u in raw_units:
            if type(u) is not dict and not isinstance(u, dict):
                continue
            if "word" not in u:
                continue
            rec = unit_record(u)
            if rec.word:
                append(rec)

        self._extra_records = records
        self.extra_source_path = source_label
        self.extra_source_size_bytes = source_size_bytes
        if not refresh:
            return len(records)
        self._refresh_records()
        base_ids = {id(record) for record in self._base_records}
        return sum(1 for record in self.units if id(record) not in base_ids)

    def load_extra_file(self, filepath: str) -> int:
        raw_bytes = Path(filepath).read_bytes()
        data = json.loads(raw_bytes.decode("utf-8"))
        return self.load_extra_data(
            data,
            source_label=filepath,
            source_size_bytes=len(raw_bytes),
        )

    def load_blacklist_data(
        self,
        contents: str,
        source_label: str = "",
        source_size_bytes: Optional[int] = None,
    ) -> int:
        self._blacklist_checked = True
        self.blacklisted_words = parse_word_list(contents)
        if source_label:
            self.blacklist_source_label = source_label
        self.blacklist_size_bytes = (
            source_size_bytes
            if source_size_bytes is not None
            else len(contents.encode("utf-8"))
        )
        self.blacklist_loaded = True
        self._refresh_records()
        return len(self.units)

    def _refresh_records(self) -> None:
        self.ensure_blacklist_loaded()
        records: List[UnitRecord] = []
        append = records.append
        tags: Set[str] = set()
        tags_update = tags.update
        max_len = 2
        blacklisted = self.blacklisted_words
        base_words: Set[str] = set()
        base_add = base_words.add

        for record in self._base_records:
            word = record.word
            base_add(word)
            if word in blacklisted:
                continue
            append(record)
            tags_update(record.effect_tags)
            if record.length > max_len:
                max_len = record.length

        if self._extra_records:
            extra_words: Set[str] = set()
            extra_add = extra_words.add
            for record in self._extra_records:
                word = record.word
                if word in base_words or word in extra_words:
                    continue
                extra_add(word)
                if word in blacklisted:
                    continue
                append(record)
                tags_update(record.effect_tags)
                if record.length > max_len:
                    max_len = record.length

        self.units = records
        self.available_tags = tags
        self.max_len = max_len
        self.revision += 1

    def get_ordered_effect_options(self) -> Dict[str, str]:
        """Build the Effect / Resource select options in the exact requested order."""
        opts: Dict[str, str] = {"": "Any effect / resource"}
        seen: Set[str] = set()
        for key in EFFECT_RESOURCE_ORDER:
            if key in self.available_tags:
                opts[key] = pretty_name(key)
                seen.add(key)
        # Include any extra tags present in future JSON updates
        for key in sorted(self.available_tags - seen):
            opts[key] = pretty_name(key)
        return opts

    def search(
        self,
        available_letters: str = "",
        starts_with: str = "",
        ends_with: str = "",
        contains: str = "",
        in_order: bool = False,
        exact_amount: bool = False,
        length_filter: Optional[int] = None,
        kind_filter: str = "ALL",
        kind_filters: Optional[Set[str]] = None,
        effect_filter: str = "",
        favorites_only: bool = False,
        favorites: Optional[Set[str]] = None,
        sort_by: str = "points",
        descending: bool = True,
        group_by_length: bool = False,
        include_two_letter_words: bool = False,
        sort_results: bool = True,
    ) -> List[UnitRecord]:
        avail_clean = "".join(
            ch for ch in available_letters.lower() if ("a" <= ch <= "z") or ch in ("?", "*")
        )
        starts = "".join(ch for ch in starts_with.lower() if "a" <= ch <= "z")
        ends = "".join(ch for ch in ends_with.lower() if "a" <= ch <= "z")
        cont = "".join(ch for ch in contains.lower() if "a" <= ch <= "z")

        use_rack = len(avail_clean) > 0
        wildcards = avail_clean.count("?") + avail_clean.count("*")
        rack_letters = [ch for ch in avail_clean if "a" <= ch <= "z"]
        rack_len = len(rack_letters) + wildcards
        rack_counts: Dict[str, int] = {}
        rack_mask = 0
        for ch in rack_letters:
            rack_counts[ch] = rack_counts.get(ch, 0) + 1
            rack_mask |= 1 << (ord(ch) - 97)
        not_rack_mask = ~rack_mask

        cont_counts: Dict[str, int] = {}
        for ch in cont:
            cont_counts[ch] = cont_counts.get(ch, 0) + 1

        fav_set = favorites or set()

        results: List[UnitRecord] = []
        for rec in self.units:
            if not include_two_letter_words and rec.length == 2:
                continue

            if favorites_only and rec.word not in fav_set:
                continue

            if kind_filters is not None:
                if rec.kind not in kind_filters:
                    continue
            elif kind_filter != "ALL":
                if kind_filter == "CURSED":
                    if not rec.is_cursed:
                        continue
                elif rec.kind != kind_filter:
                    continue

            if length_filter is not None and rec.length != length_filter:
                continue

            if use_rack:
                if rec.length > rack_len:
                    continue
                if wildcards == 0:
                    if rec.mask & not_rack_mask:
                        continue
                    w = rec.word
                    ok = True
                    for ch in set(w):
                        if w.count(ch) > rack_counts[ch]:
                            ok = False
                            break
                    if not ok:
                        continue
                else:
                    w = rec.word
                    needed = 0
                    for ch in set(w):
                        diff = w.count(ch) - rack_counts.get(ch, 0)
                        if diff > 0:
                            needed += diff
                            if needed > wildcards:
                                break
                    if needed > wildcards:
                        continue

            if effect_filter and effect_filter not in rec.effect_tags:
                continue

            w = rec.word
            if starts and not w.startswith(starts):
                continue
            if ends and not w.endswith(ends):
                continue

            if cont:
                if in_order and cont not in w:
                    continue
                if exact_amount:
                    ok = True
                    for ch, cnt in cont_counts.items():
                        if w.count(ch) != cnt:
                            ok = False
                            break
                    if not ok:
                        continue
                elif not in_order:
                    ok = True
                    for ch, cnt in cont_counts.items():
                        if w.count(ch) < cnt:
                            ok = False
                            break
                    if not ok:
                        continue

            results.append(rec)

        if sort_results:
            self._sort_results(
                results,
                sort_by=sort_by,
                descending=descending,
                group_by_length=group_by_length,
            )
        return results

    def _sort_results(
        self,
        results: List[UnitRecord],
        sort_by: str,
        descending: bool,
        group_by_length: bool,
    ) -> None:
        if sort_by == "alphabetical":
            # Descending starts at A (A -> Z); Ascending starts at Z (Z -> A)
            if group_by_length:
                if descending:
                    results.sort(key=lambda r: (-r.length, r.word))
                else:
                    results.sort(key=lambda r: r.word, reverse=True)
                    results.sort(key=lambda r: r.length)
            else:
                results.sort(key=lambda r: r.word, reverse=(not descending))
            return

        if sort_by == "points":
            if group_by_length:
                if descending:
                    results.sort(key=lambda r: (-r.length, -r.scrabble, r.word))
                else:
                    results.sort(key=lambda r: (r.length, r.scrabble, r.word))
            else:
                if descending:
                    results.sort(key=lambda r: (-r.scrabble, -r.length, r.word))
                else:
                    results.sort(key=lambda r: (r.scrabble, r.length, r.word))
            return

        # Stat / Effect sort (units WITH the stat always appear before units lacking it)
        val_sign = -1 if descending else 1
        len_sign = -1 if descending else 1

        if sort_by == "damage":
            get_val = lambda r: r.damage if r.damage is not None else r._delta_val("damage")
        elif sort_by == "dps":
            get_val = lambda r: r.dps
        elif sort_by == "attack_speed":
            get_val = lambda r: r.attack_speed if r.attack_speed is not None else r._delta_val("attack_speed")
        elif sort_by in ("toughness", "health"):
            get_val = lambda r: r.health if r.health is not None else r._delta_val("toughness")
        elif sort_by == "armor":
            get_val = lambda r: r.armor if (r.armor is not None and (r.armor > 0 or r.kind == "TOWER")) else r._delta_val("armor")
        elif sort_by == "range":
            get_val = lambda r: r.range if r.range is not None else (r.harvest_range if r.harvest_range is not None else r._delta_val("range"))
        elif sort_by == "harvest_amount":
            get_val = lambda r: r.harvest_amount if r.harvest_amount is not None else r._delta_val("harvest_amount")
        elif sort_by == "harvest_speed":
            get_val = lambda r: r.harvest_speed if r.harvest_speed is not None else r._delta_val("harvest_speed")
        elif sort_by == "harvest_rate":
            get_val = lambda r: r.harvest_rate
        elif sort_by == "harvest_types":
            get_val = lambda r: float(r.harvest_types) if r.harvest_types is not None else None
        else:
            def get_val(r: UnitRecord):
                sp = r._special_val(sort_by)
                return sp if sp is not None else r._delta_val(sort_by)

        if group_by_length:
            def stat_sort_key(r: UnitRecord):
                v = get_val(r)
                if v is None:
                    return (len_sign * r.length, 1, 0.0, -r.scrabble, r.word)
                return (len_sign * r.length, 0, val_sign * v, -r.scrabble, r.word)
        else:
            def stat_sort_key(r: UnitRecord):
                v = get_val(r)
                if v is None:
                    return (1, 0.0, -r.scrabble, r.word)
                return (0, val_sign * v, -r.scrabble, r.word)

        results.sort(key=stat_sort_key)


# ---------------------------------------------------------------------------
# Shared Database Loader
# ---------------------------------------------------------------------------
GLOBAL_DB = UnitDatabase()
DB_LOAD_EVENT = threading.Event()
_DB_AUTOLOAD_STARTED = False


def autoload_database() -> Optional[str]:
    try:
        GLOBAL_DB.ensure_blacklist_loaded()
        if getattr(sys, "frozen", False):
            app_dir = Path(sys.executable).resolve().parent
        else:
            app_dir = Path(__file__).resolve().parent
        cwd = Path.cwd()
        roots = list(dict.fromkeys((app_dir, cwd)))
        unit_paths = [
            root / name
            for root in roots
            for name in ("units.json", "units_2.json")
        ]
        loaded_paths: List[str] = []

        for path in unit_paths:
            if path.is_file():
                try:
                    raw_bytes = path.read_bytes()
                    data = json.loads(raw_bytes)
                    raw_units = data.get("units") if isinstance(data, dict) else data
                    if not isinstance(raw_units, list):
                        raise ValueError("JSON must contain a list of units.")
                    count = GLOBAL_DB.load_data(
                        data,
                        source_label=str(path),
                        source_size_bytes=len(raw_bytes),
                        refresh=False,
                    )
                    if count == 0:
                        raise ValueError("No word records were found.")
                    loaded_paths.append(str(path))
                    break
                except (
                    OSError,
                    UnicodeDecodeError,
                    json.JSONDecodeError,
                    KeyError,
                    TypeError,
                    ValueError,
                ) as exc:
                    print(f"Could not load {path.name}: {exc}")

        curse_paths = [root / "cursed_words.json" for root in roots]
        for path in curse_paths:
            if path.is_file():
                try:
                    raw_bytes = path.read_bytes()
                    data = json.loads(raw_bytes)
                    raw_units = data.get("units") if isinstance(data, dict) else data
                    if not isinstance(raw_units, list):
                        raise ValueError("JSON must contain a list of units.")
                    count = GLOBAL_DB.load_extra_data(
                        data,
                        source_label=str(path),
                        source_size_bytes=len(raw_bytes),
                        refresh=False,
                    )
                    if count == 0 or not any(
                        rec.is_cursed for rec in GLOBAL_DB._extra_records
                    ):
                        GLOBAL_DB._extra_records = []
                        GLOBAL_DB.extra_source_path = ""
                        GLOBAL_DB.extra_source_size_bytes = None
                        raise ValueError("No cursed towers were found.")
                    loaded_paths.append(str(path))
                    break
                except (
                    OSError,
                    UnicodeDecodeError,
                    json.JSONDecodeError,
                    KeyError,
                    TypeError,
                    ValueError,
                ) as exc:
                    print(f"Could not load {path.name}: {exc}")

        if loaded_paths:
            GLOBAL_DB._refresh_records()

        return " + ".join(loaded_paths) if loaded_paths else None
    finally:
        DB_LOAD_EVENT.set()


def start_autoload_in_background() -> threading.Thread:
    global _DB_AUTOLOAD_STARTED
    _DB_AUTOLOAD_STARTED = True
    DB_LOAD_EVENT.clear()

    def _loader() -> None:
        loaded = autoload_database()
        if loaded:
            print(f"Loaded {len(GLOBAL_DB.units):,} units from {loaded}")
        else:
            print(
                "No units.json found automatically — use the settings menu to load files."
            )

    thread = threading.Thread(
        target=_loader, name="babble-db-autoload", daemon=True
    )
    thread.start()
    return thread


# ---------------------------------------------------------------------------
# Modern NiceGUI Application
# ---------------------------------------------------------------------------
def resolve_app_directory() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def find_outfit_font() -> Optional[Path]:
    app_dir = resolve_app_directory()
    candidates = [app_dir / "outfit_font.ttf"]

    if getattr(sys, "frozen", False):
        bundled_dir = getattr(sys, "_MEIPASS", None)
        if bundled_dir:
            candidates.append(Path(bundled_dir) / "outfit_font.ttf")

    candidates.append(Path.cwd() / "outfit_font.ttf")

    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def build_font_css() -> str:
    font_css = [
        '@import url("https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@700&display=swap");'
    ]

    outfit_font = find_outfit_font()
    if outfit_font is not None:
        try:
            encoded_font = base64.b64encode(outfit_font.read_bytes()).decode("ascii")
            font_css.append(
                "@font-face {"
                'font-family: "Outfit";'
                "font-style: normal;"
                "font-weight: 700;"
                "font-display: swap;"
                f'src: url("data:font/ttf;base64,{encoded_font}") format("truetype");'
                "}"
            )
        except (OSError, PermissionError):
            pass

    return "\n".join(font_css)


_CUSTOM_CSS_BODY = """
  body {
    background-color: #DDDDDD !important;
    font-family: "Plus Jakarta Sans", "Outfit", Arial, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
    color: #111111;
    margin: 0;
  }
  .babble-shell {
    max-width: 920px;
    margin: 0 auto;
    padding: 16px 18px 28px 18px;
  }
  .babble-panel {
    background: #F4F4F4;
    border: 1px solid #B7B7B7;
    border-radius: 10px;
    padding: 14px 16px;
  }
  .babble-pill {
    border-radius: 9999px !important;
    border: 2px solid #939393 !important;
    background: #DCDCDC !important;
    color: #111111 !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em;
    box-shadow: none !important;
    transition: background-color 0.14s ease, border-color 0.14s ease;
  }
  .babble-pill-blue-border {
    border: 2px solid #6BA3D1 !important;
  }
  .babble-pill:hover {
    background: #CECECE !important;
  }
  .babble-pill-blue {
    border-radius: 9999px !important;
    border: 2px solid #6BA3D1 !important;
    background: #88C9FE !important;
    color: #111111 !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em;
    box-shadow: none !important;
    transition: background-color 0.14s ease, border-color 0.14s ease;
  }
  .babble-pill-blue:hover {
    background: #72BDFB !important;
  }
  .babble-favorite-btn {
    border-radius: 9999px !important;
    border: 2px solid #FF5604 !important;
    background: #FF5604 !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    box-shadow: none !important;
  }
  .babble-favorite-btn:hover {
    background: #E64D00 !important;
  }
  .babble-mini-btn {
    border-radius: 9999px !important;
    border: 1.5px solid #939393 !important;
    background: #DCDCDC !important;
    color: #111111 !important;
    font-weight: 700 !important;
    font-size: 11px !important;
    min-height: 24px !important;
    padding: 0 10px !important;
    box-shadow: none !important;
  }
  .babble-mini-btn:hover {
    background: #CECECE !important;
  }
  .babble-mini-use {
    border-radius: 9999px !important;
    border: 1.5px solid #6BA3D1 !important;
    background: #88C9FE !important;
    color: #111111 !important;
    font-weight: 700 !important;
    font-size: 11px !important;
    min-height: 24px !important;
    padding: 0 11px !important;
    box-shadow: none !important;
  }
  .babble-mini-use:hover {
    background: #72BDFB !important;
  }
  .babble-input .q-field__control {
    background: #F4F4F4 !important;
    border-radius: 7px !important;
  }
  .babble-file-status {
    display: inline-flex;
    min-width: 108px;
    justify-content: center;
    border-radius: 5px;
    padding: 5px 8px;
    color: #FFFFFF !important;
    font-weight: 700;
    white-space: nowrap;
  }
  .babble-file-upload .q-uploader__subtitle,
  .babble-file-upload .q-uploader__list,
  .babble-file-upload .q-uploader .q-linear-progress {
    display: none !important;
  }
  .babble-file-upload .q-uploader__header {
    min-height: 42px !important;
  }
  .babble-file-upload.babble-file-loaded .q-uploader__header {
    background: #2E7D32 !important;
    color: #FFFFFF !important;
  }
  .babble-file-upload.babble-file-not-loaded .q-uploader__header {
    background: #B71C1C !important;
    color: #FFFFFF !important;
  }
  .babble-uppercase input {
    text-transform: uppercase !important;
    font-weight: 700 !important;
    letter-spacing: 0.06em;
  }
  .babble-group-bar {
    background: #F4F4F4;
    border: 1px solid #B0B0B0;
    border-radius: 7px;
    padding: 6px 12px;
    cursor: pointer;
    user-select: none;
    transition: background-color 0.12s ease;
  }
  .babble-group-bar:hover {
    background: #C9C9C9;
  }
  .babble-unit-box {
    background: #F4F4F4;
    border: 1px solid #BDBDBD;
    border-radius: 8px;
    padding: 9px 12px;
    cursor: pointer;
    transition: background-color 0.12s ease, border-color 0.12s ease;
  }
  .babble-unit-box-tower {
    border: 1px solid #FF5604 !important;
  }
  .babble-unit-box-mod {
    border: 1px solid #e858a8 !important;
  }
  .babble-unit-box-cursed {
    border: 1px solid #6e13be !important;
  }
  .babble-unit-box-harvester {
    border: 1px solid #1E7D32 !important;
  }
  .babble-unit-box:hover {
    background: #EAEAEA;
  }
  .babble-unit-box-tower:hover {
    border-color: #FF5604 !important;
  }
  .babble-unit-box-mod:hover {
    border-color: #e858a8 !important;
  }
  .babble-unit-box-cursed:hover {
    border-color: #6e13be !important;
  }
  .babble-unit-box-harvester:hover {
    border-color: #1E7D32 !important;
  }
  .babble-unit-box-open {
    background: #F4F4F4 !important;
    border: 1.5px solid #8A8A8A !important;
  }
  .babble-unit-box-open.babble-unit-box-tower {
    border: 1.5px solid #FF5604 !important;
  }
  .babble-unit-box-open.babble-unit-box-mod {
    border: 1.5px solid #e858a8 !important;
  }
  .babble-unit-box-open.babble-unit-box-cursed {
    border: 1.5px solid #6e13be !important;
  }
  .babble-unit-box-open.babble-unit-box-harvester {
    border: 1.5px solid #1E7D32 !important;
  }
  .babble-combo-box {
    background: #F4F4F4;
    border: 1px solid #BDBDBD;
    border-radius: 8px;
    padding: 9px 12px;
    cursor: pointer;
    transition: background-color 0.12s ease, border-color 0.12s ease;
  }
  .babble-combo-box:hover {
    background: #EAEAEA;
  }
  .babble-combo-box-open {
    background: #F4F4F4 !important;
    border: 1.5px solid #8A8A8A !important;
  }
  .babble-combo-unit {
    background: #F4F4F4;
    border: 1px solid #BDBDBD;
    border-radius: 8px;
    padding: 9px 12px;
  }
  .babble-pts-tile {
    background: #F4F4F4;
    border: 1px solid #B8AD7E;
    border-radius: 4px;
    padding: 1px 7px;
    font-size: 11px;
    font-weight: 700;
    color: #111111;
    line-height: 1.35;
    box-shadow: 0 1px 0 rgba(0, 0, 0, 0.12);
    white-space: nowrap;
  }
  .q-btn.babble-stat-filter {
    border: 2px solid transparent !important;
    border-radius: 4px !important;
    box-shadow: none !important;
    font-size: 10px !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em;
    min-height: 24px !important;
    padding: 0 6px !important;
  }
  .q-btn.babble-stat-filter .babble-stat-filter-count {
    background: #FFFFFF !important;
    color: #222222 !important;
    border-radius: 3px;
    font-size: 9px;
    font-weight: 800;
    line-height: 1.2;
    margin-right: 4px;
    padding: 1px 4px;
  }
  .q-btn.babble-stat-filter .babble-stat-filter-label {
    white-space: nowrap;
  }
  .babble-field-lbl {
    font-size: 11px;
    font-weight: 700;
    color: #595959;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }
  .stat-pos { color: #087007; font-weight: 700; }
  .stat-neg { color: #B83227; font-weight: 700; }
  .stat-neutral { color: #111111; font-weight: 700; }
  .babble-res-dot {
    width: 18px;
    height: 18px;
    border-radius: 9999px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    font-weight: 700;
  }
  ::-webkit-scrollbar { width: 10px; height: 10px; }
  ::-webkit-scrollbar-track { background: #D2D2D2; border-radius: 5px; }
  ::-webkit-scrollbar-thumb { background: #9A9A9A; border-radius: 5px; }
  ::-webkit-scrollbar-thumb:hover { background: #7D7D7D; }
</style>
"""

_CUSTOM_CSS_CACHE: Optional[str] = None


def get_custom_css() -> str:
    global _CUSTOM_CSS_CACHE
    if _CUSTOM_CSS_CACHE is None:
        _CUSTOM_CSS_CACHE = "<style>\n" + build_font_css() + _CUSTOM_CSS_BODY
    return _CUSTOM_CSS_CACHE


def build_nicegui_app():
    from nicegui import background_tasks, ui
    from nicegui.translations import translations as nicegui_translations

    for entry in nicegui_translations.values():
        entry["connection_lost"] = "Please wait."
        entry["trying_to_reconnect"] = "The program is loading..."

    PAGE_SIZE = 200

    class FinderSession:
        def __init__(self):
            self.user_data_path = resolve_user_data_path()
            self.user_data: Dict[str, Any] = {
                "version": 1,
                "favorites": [],
                "dictionary_url": DEFAULT_DICTIONARY_URL,
            }
            self.user_data_source = ""
            self.user_data_size_bytes: Optional[int] = None
            self.user_data_loaded = False

            if self.user_data_path.is_file():
                try:
                    self.user_data = load_user_data_json(self.user_data_path)
                    self.user_data_source = self.user_data_path.name
                    self.user_data_size_bytes = self.user_data_path.stat().st_size
                    self.user_data_loaded = True
                except (
                    OSError,
                    UnicodeDecodeError,
                    json.JSONDecodeError,
                    ValueError,
                ) as exc:
                    print(f"Could not load {self.user_data_path.name}: {exc}")
            else:
                legacy_path = resolve_legacy_favorites_path()
                if legacy_path.is_file():
                    try:
                        legacy_favorites = parse_word_list(
                            legacy_path.read_text(encoding="utf-8")
                        )
                        self.user_data["favorites"] = sorted(legacy_favorites)
                        save_user_data_json(self.user_data_path, self.user_data)
                        self.user_data_source = self.user_data_path.name
                        self.user_data_size_bytes = self.user_data_path.stat().st_size
                        self.user_data_loaded = True
                    except (OSError, UnicodeDecodeError) as exc:
                        print(f"Could not migrate {legacy_path.name}: {exc}")

            self.favorites: Set[str] = set(self.user_data["favorites"])
            self.dictionary_url: str = normalize_dictionary_url(
                self.user_data.get("dictionary_url", DEFAULT_DICTIONARY_URL)
            )

            # Deferred form state (only applied when Find Words / Clear / Use is pressed)
            self.form_letters: str = ""
            self.form_contains: str = ""
            self.form_in_order: bool = False
            self.form_exact_amount: bool = False
            self.form_starts: str = ""
            self.form_ends: str = ""
            self.form_length: str = "ALL"
            self.form_effect: str = ""

            # Last committed query
            self.applied_query: Dict[str, Any] = self._snapshot_form()

            # Immediate-update controls
            self.selected_kinds: Set[str] = {"TOWER", "HARVESTER", "MOD"}
            self.sort_by: str = "points"
            self.sort_mode: str = "value"
            self.descending: bool = True
            self.group_by_length: bool = False
            self.show_two_letter_words: bool = False
            self.clever_mode: bool = False
            self.favorites_only: bool = False
            self.selected_stat_filters: Set[str] = set()
            self.stat_filter_counts: Dict[str, int] = {}

            # Current search results & pagination
            self.current_matches: List[UnitRecord] = []
            self.current_combinations: List[Tuple[UnitRecord, ...]] = []
            self.combinations_by_word_count: Dict[
                int, List[Tuple[UnitRecord, ...]]
            ] = {}
            self.combinations_truncated: bool = False
            self.clever_searching: bool = False
            self._clever_search_generation: int = 0
            self._clever_cancel_event: Optional[threading.Event] = None
            self._clever_task: Optional[asyncio.Task] = None
            self._stat_filter_generation: int = 0
            self._stat_filter_task: Optional[asyncio.Task] = None
            self._cached_base_key: Optional[Tuple[Any, ...]] = None
            self._cached_base_matches: List[UnitRecord] = []
            self._cached_stat_counts: Dict[str, int] = {}
            self._cached_max_changes: Dict[str, float] = {}
            self._cached_sorted_key: Optional[Tuple[Any, ...]] = None
            self._cached_sorted_matches: List[UnitRecord] = []
            self._cached_clever_key: Optional[Tuple[Any, ...]] = None
            self._cached_clever_result: Optional[
                Tuple[
                    List[Tuple[UnitRecord, ...]],
                    Dict[int, List[Tuple[UnitRecord, ...]]],
                    bool,
                ]
            ] = None
            self.stat_filter_widgets: Dict[str, Tuple[Any, Any]] = {}
            self._rendered_stat_filter_state: Dict[str, Tuple[int, bool]] = {}
            self.visible_limit: int = PAGE_SIZE
            self.collapsed_lengths: Set[int] = set()
            self.collapsed_clever_groups: Set[int] = set()
            self.group_visible_limits: Dict[Tuple[str, int], int] = {}
            self._suppress_events: bool = False

            # UI widget references populated in build()
            self.inp_letters = None
            self.inp_contains = None
            self.inp_starts = None
            self.inp_ends = None
            self.sel_length = None
            self.sel_effect = None
            self.sel_order = None
            self.kind_buttons: Dict[str, Any] = {}
            self.btn_sort_mode = None
            self.btn_group = None
            self.btn_two_letter_words = None
            self.btn_clever_mode = None
            self.btn_collapse_groups = None
            self.btn_favorites = None
            self.btn_in_order = None
            self.btn_exact = None
            self.lbl_letter_count = None
            self.lbl_file_status = None
            self.lbl_pending = None
            self.lbl_fav_count = None
            self.lbl_curse_count = None
            self.lbl_result_count = None
            self.stat_filter_container = None
            self.results_container = None
            self.settings_dialog = None
            self.inp_dictionary_url = None
            self.settings_file_labels: Dict[str, Any] = {}
            self.settings_upload_boxes: Dict[str, Any] = {}
            def file_status(loaded: bool, size_bytes: Optional[int]):
                if loaded and size_bytes is not None:
                    return format_file_size(size_bytes), True
                return "File not loaded", False

            self.settings_file_status: Dict[str, Tuple[str, bool]] = {
                "units": file_status(
                    bool(GLOBAL_DB.source_path and GLOBAL_DB._base_records),
                    GLOBAL_DB.source_size_bytes,
                ),
                "cursed": file_status(
                    bool(
                        GLOBAL_DB.extra_source_path
                        and any(record.is_cursed for record in GLOBAL_DB._extra_records)
                    ),
                    GLOBAL_DB.extra_source_size_bytes,
                ),
                "blacklist": file_status(
                    GLOBAL_DB.blacklist_loaded,
                    GLOBAL_DB.blacklist_size_bytes,
                ),
                "user_data": file_status(
                    self.user_data_loaded,
                    self.user_data_size_bytes,
                ),
            }

        def _snapshot_form(self) -> Dict[str, Any]:
            length_val: Optional[int] = None
            if self.form_length != "ALL":
                try:
                    length_val = int(self.form_length)
                except ValueError:
                    length_val = None
            return {
                "available_letters": self.form_letters,
                "contains": self.form_contains,
                "in_order": self.form_in_order,
                "exact_amount": self.form_exact_amount,
                "starts_with": self.form_starts,
                "ends_with": self.form_ends,
                "length_filter": length_val,
                "effect_filter": self.form_effect,
            }

        def _sync_pill_style(self, btn, active: bool) -> None:
            btn.classes(
                remove="babble-pill babble-pill-blue babble-favorite-btn",
                add="babble-pill",
            )
            if active:
                btn.style(
                    "background: #FF5604 !important; "
                    "border: 2px solid #FF5604 !important; "
                    "color: #FFFFFF !important;"
                )
            else:
                btn.style(
                    "background: #DCDCDC !important; "
                    "border: 2px solid #939393 !important; "
                    "color: #111111 !important;"
                )

        def _sync_favorite_style(self, active: bool) -> None:
            if active:
                self.btn_favorites.classes(
                    remove="babble-pill babble-favorite-btn",
                    add="babble-favorite-btn",
                )
                self.btn_favorites.style(
                    "background: #FF5604 !important; "
                    "border: 2px solid #FF5604 !important; "
                    "color: #FFFFFF !important;"
                )
            else:
                self.btn_favorites.classes(
                    remove="babble-pill babble-favorite-btn",
                    add="babble-pill",
                )
                self.btn_favorites.style(
                    "background: #DCDCDC !important; "
                    "border: 2px solid #939393 !important; "
                    "color: #111111 !important;"
                )

        def _update_letter_count_label(self) -> None:
            clean_len = sum(
                1
                for ch in self.form_letters
                if ("a" <= ch.lower() <= "z") or ch in ("?", "*")
            )
            if clean_len == 0:
                self.lbl_letter_count.set_text("0 letters (browsing all)")
            elif clean_len == 1:
                self.lbl_letter_count.set_text("1 letter")
            else:
                self.lbl_letter_count.set_text(f"{clean_len} letters")

        def _update_pending_indicator(self) -> None:
            dirty = self._snapshot_form() != self.applied_query
            if dirty and GLOBAL_DB.units:
                self.lbl_pending.set_text("• Click FIND WORDS to apply filter changes")
                self.lbl_pending.set_visibility(True)
            else:
                self.lbl_pending.set_text("")
                self.lbl_pending.set_visibility(False)

        def _update_favorites_banner(self) -> None:
            fav_count_label = self.lbl_fav_count
            curse_count_label = self.lbl_curse_count
            if fav_count_label is None or curse_count_label is None:
                return
            entered_letters = sum(
                1
                for ch in self.applied_query["available_letters"]
                if ("a" <= ch.lower() <= "z") or ch in ("?", "*")
            )
            if entered_letters == 0:
                fav_count_label.set_text("")
                fav_count_label.set_visibility(False)
                curse_count_label.set_text("")
                curse_count_label.set_visibility(False)
                return

            fav_in_list = sum(1 for r in self.current_matches if r.word in self.favorites)
            if fav_in_list > 0:
                noun = "favorite" if fav_in_list == 1 else "favorites"
                fav_count_label.set_text(f"♥ {fav_in_list:,} {noun} found")
                fav_count_label.set_visibility(True)
            else:
                fav_count_label.set_text("")
                fav_count_label.set_visibility(False)

            cursed_in_list = sum(1 for r in self.current_matches if r.is_cursed)
            if cursed_in_list > 0:
                noun = "cursed word" if cursed_in_list == 1 else "cursed words"
                curse_count_label.set_text(f"☠ {cursed_in_list:,} {noun}")
                curse_count_label.set_visibility(True)
            else:
                curse_count_label.set_text("")
                curse_count_label.set_visibility(False)

        def _build_stat_filter_controls(self) -> None:
            filter_container = self.stat_filter_container
            if filter_container is None:
                return
            filter_container.clear()
            self.stat_filter_widgets.clear()
            self._rendered_stat_filter_state.clear()
            with filter_container:
                for stat_key, label, active_bg, _active_fg in STAT_FILTERS:
                    bg = lighten_stat_filter_color(active_bg)
                    button = (
                        ui.button(
                            on_click=lambda _e, key=stat_key: self.on_toggle_stat_filter(
                                key
                            ),
                        )
                        .props("unelevated dense no-caps")
                        .classes("babble-stat-filter")
                        .style(
                            f"background-color: {bg} !important; "
                            "color: #263238 !important;"
                        )
                    )
                    with button:
                        count_label = ui.label("0").classes(
                            "babble-stat-filter-count"
                        )
                        ui.label(label).classes("babble-stat-filter-label")
                    tooltip_text = STAT_FILTER_TOOLTIPS.get(stat_key)
                    if tooltip_text:
                        button.tooltip(tooltip_text)
                    self.stat_filter_widgets[stat_key] = (button, count_label)
                    self._rendered_stat_filter_state[stat_key] = (0, False)

        def _update_stat_filter_controls(self) -> None:
            if not self.stat_filter_widgets:
                self._build_stat_filter_controls()
                if not self.stat_filter_widgets:
                    return
            for stat_key, _label, active_bg, active_fg in STAT_FILTERS:
                count = self.stat_filter_counts.get(stat_key, 0)
                is_selected = stat_key in self.selected_stat_filters
                new_state = (count, is_selected)
                if self._rendered_stat_filter_state.get(stat_key) == new_state:
                    continue
                self._rendered_stat_filter_state[stat_key] = new_state
                button, count_label = self.stat_filter_widgets[stat_key]
                bg = (
                    active_bg
                    if is_selected
                    else lighten_stat_filter_color(active_bg)
                )
                fg = active_fg if is_selected else "#263238"
                button.style(
                    f"background-color: {bg} !important; "
                    f"color: {fg} !important;"
                )
                count_label.set_text(f"{count:,}")

        def _sync_kind_filter_controls(self) -> None:
            for kind, button in self.kind_buttons.items():
                color = KIND_META[kind]["button_color"]
                selected = kind in self.selected_kinds
                background = color if selected else "#DCDCDC"
                border = color
                foreground = "#FFFFFF" if selected else "#263238"
                button.style(
                    f"background-color: {background} !important; "
                    f"border-color: {border} !important; "
                    f"color: {foreground} !important;"
                )

        def _sync_sort_mode_button(self) -> None:
            if self.btn_sort_mode is None:
                return
            if self.sort_mode == "alphabetical":
                self.btn_sort_mode.set_text("ALPHABETICAL")
                color = "#6A1B9A"
            else:
                self.btn_sort_mode.set_text("VALUE")
                color = "#1565C0"
            self.btn_sort_mode.style(
                f"background-color: {color} !important; "
                f"border-color: {color} !important; color: #FFFFFF !important;"
            )

        def _sync_clever_mode_button(self) -> None:
            button = self.btn_clever_mode
            if button is None:
                return
            background = "#795548" if self.clever_mode else "#DCDCDC"
            border = "#795548" if self.clever_mode else "#939393"
            foreground = "#FFFFFF" if self.clever_mode else "#111111"
            button.style(
                f"background-color: {background} !important; "
                f"border-color: {border} !important; "
                f"color: {foreground} !important;"
            )

        def _get_max_positive_stat_change(
            self, base_results: List[UnitRecord], stat_key: str
        ) -> float:
            cached = self._cached_max_changes.get(stat_key)
            if cached is not None:
                return cached
            if stat_key == "curse":
                max_val = (
                    1.0 if self.stat_filter_counts.get("curse", 0) > 0 else 0.0
                )
                self._cached_max_changes[stat_key] = max_val
                return max_val
            bit = STAT_FILTER_BITS.get(stat_key, 0)
            max_val = 0.0
            for rec in base_results:
                if rec._positive_stat_mask & bit:
                    val = rec.get_positive_stat_change(stat_key)
                    if val is not None and val > max_val:
                        max_val = val
            self._cached_max_changes[stat_key] = max_val
            return max_val

        def _sort_combined_results(
            self,
            results: List[UnitRecord],
            base_results: List[UnitRecord],
            stat_keys: List[str],
        ) -> None:
            inv_scales: List[Tuple[str, float]] = []
            for key in stat_keys:
                max_val = self._get_max_positive_stat_change(base_results, key)
                if max_val > 0.0:
                    inv_scales.append((key, 1.0 / max_val))

            order_sign = -1 if self.descending else 1
            length_sign = -1 if self.descending else 1
            if self.group_by_length:
                def sort_key(rec: UnitRecord):
                    score = 0.0
                    for key, inv_max in inv_scales:
                        val = rec.get_positive_stat_change(key)
                        if val is not None:
                            score += val * inv_max
                    return (
                        length_sign * rec.length,
                        order_sign * score,
                        -rec.scrabble,
                        rec.word,
                    )
            else:
                def sort_key(rec: UnitRecord):
                    score = 0.0
                    for key, inv_max in inv_scales:
                        val = rec.get_positive_stat_change(key)
                        if val is not None:
                            score += val * inv_max
                    return (order_sign * score, -rec.scrabble, rec.word)

            results.sort(key=sort_key)

        def _get_active_group_totals(self) -> Dict[Tuple[str, int], int]:
            totals: Dict[Tuple[str, int], int] = {}
            if self.clever_mode:
                return {
                    ("clever", word_count): len(items)
                    for word_count, items in self.combinations_by_word_count.items()
                }

            if not self.group_by_length:
                return totals

            exact_letters = "".join(
                ch
                for ch in self.applied_query["available_letters"].lower()
                if ("a" <= ch <= "z") or ch in ("?", "*")
            )
            valid_word = None
            if exact_letters and "?" not in exact_letters and "*" not in exact_letters:
                valid_word = next(
                    (rec for rec in self.current_matches if rec.word == exact_letters),
                    None,
                )
            for record in self.current_matches:
                if record is not valid_word:
                    key = ("length", record.length)
                    totals[key] = totals.get(key, 0) + 1
            return totals

        def _group_visible_count(
            self,
            key: Tuple[str, int],
            total_count: int,
            group_count: int,
        ) -> int:
            default_limit = max(1, PAGE_SIZE // max(group_count, 1))
            return min(
                total_count,
                self.group_visible_limits.get(key, default_limit),
            )

        def _sync_group_collapse_button(self) -> None:
            button = self.btn_collapse_groups
            if button is None:
                return
            group_totals = self._get_active_group_totals()
            if not group_totals:
                button.set_visibility(False)
                return

            collapsed = all(
                key[1]
                in (
                    self.collapsed_clever_groups
                    if key[0] == "clever"
                    else self.collapsed_lengths
                )
                for key in group_totals
            )
            button.set_text("EXPAND GROUPS" if collapsed else "COLLAPSE GROUPS")
            button.set_visibility(True)
            color = "#1565C0" if collapsed else "#6A1B9A"
            button.style(
                f"background-color: {color} !important; "
                f"border-color: {color} !important; "
                "color: #FFFFFF !important;"
            )

        def on_toggle_all_groups(self) -> None:
            group_totals = self._get_active_group_totals()
            if not group_totals:
                return

            collapsed = all(
                key[1]
                in (
                    self.collapsed_clever_groups
                    if key[0] == "clever"
                    else self.collapsed_lengths
                )
                for key in group_totals
            )
            for mode, group_key in group_totals:
                group_set = (
                    self.collapsed_clever_groups
                    if mode == "clever"
                    else self.collapsed_lengths
                )
                if collapsed:
                    group_set.discard(group_key)
                else:
                    group_set.add(group_key)
            self._sync_group_collapse_button()
            self._render_results()

        def _load_more_group(
            self, key: Tuple[str, int], total_count: int
        ) -> None:
            group_count = len(self._get_active_group_totals())
            current = self._group_visible_count(key, total_count, group_count)
            self.group_visible_limits[key] = min(
                total_count, current + PAGE_SIZE
            )
            self._render_results_preserving_scroll()

        def _load_more_grouped_results(self) -> None:
            totals = self._get_active_group_totals()
            if not totals:
                return
            group_count = len(totals)
            step = max(1, PAGE_SIZE // group_count)
            for key, total_count in totals.items():
                current = self._group_visible_count(
                    key, total_count, group_count
                )
                self.group_visible_limits[key] = min(
                    total_count, current + step
                )
            self._render_results_preserving_scroll()

        def _show_all_grouped_results(self) -> None:
            self.group_visible_limits.update(self._get_active_group_totals())
            self._render_results_preserving_scroll()

        def _render_grouped_pagination_footer(self) -> None:
            totals = self._get_active_group_totals()
            if not totals:
                return
            group_count = len(totals)
            visible_count = sum(
                self._group_visible_count(key, total_count, group_count)
                for key, total_count in totals.items()
            )
            total_count = sum(totals.values())
            remaining = total_count - visible_count
            if remaining <= 0:
                return

            step = max(1, PAGE_SIZE // group_count)
            next_batch = sum(
                min(
                    step,
                    total - self._group_visible_count(key, total, group_count),
                )
                for key, total in totals.items()
            )
            noun = "combinations" if self.clever_mode else "words"
            with ui.row().classes(
                "w-full items-center justify-center gap-3 pt-3 pb-1"
            ):
                ui.label(
                    f"Showing {visible_count:,} of {total_count:,} {noun}"
                ).classes("text-xs font-bold").style("color: #595959;")
                ui.button(
                    f"SHOW {next_batch:,} MORE",
                    on_click=self._load_more_grouped_results,
                ).props("unelevated dense").classes("babble-pill px-4")
                if remaining <= 600:
                    ui.button(
                        f"SHOW ALL ({total_count:,})",
                        on_click=self._show_all_grouped_results,
                    ).props("unelevated dense").classes("babble-pill-blue px-4")

        def _get_length_options(self) -> Dict[str, str]:
            # Reordered: All lengths, 15, 14, 13, ... down to 3 (or 2 when enabled)
            max_l = max(GLOBAL_DB.max_len, 15)
            min_l = 2 if self.show_two_letter_words else 3
            opts: Dict[str, str] = {"ALL": "All lengths"}
            for n in range(max_l, min_l - 1, -1):
                opts[str(n)] = f"{n} letters"
            return opts

        def _sync_length_options(self) -> None:
            if self.sel_length is None:
                return
            len_opts = self._get_length_options()
            prev_suppress = self._suppress_events
            self._suppress_events = True
            try:
                self.sel_length.options = len_opts
                if self.form_length not in len_opts:
                    self.form_length = "ALL"
                    self.sel_length.value = "ALL"
                    self.applied_query["length_filter"] = None
                self.sel_length.update()
            finally:
                self._suppress_events = prev_suppress

        def _refresh_dynamic_dropdowns(self) -> None:
            self._sync_length_options()
            self._suppress_events = True
            try:
                eff_opts = GLOBAL_DB.get_ordered_effect_options()
                self.sel_effect.options = eff_opts
                if self.form_effect not in eff_opts:
                    self.form_effect = ""
                    self.sel_effect.value = ""
                self.sel_effect.update()
            finally:
                self._suppress_events = False

        # ---- Deferred Input Handlers (NEVER trigger search) ----
        def on_letters_change(self, e) -> None:
            self.form_letters = str(e.value or "")
            self._update_letter_count_label()
            if not self._suppress_events:
                self._update_pending_indicator()

        def on_contains_change(self, e) -> None:
            self.form_contains = str(e.value or "")
            if not self._suppress_events:
                self._update_pending_indicator()

        def on_starts_change(self, e) -> None:
            self.form_starts = str(e.value or "")
            if not self._suppress_events:
                self._update_pending_indicator()

        def on_ends_change(self, e) -> None:
            self.form_ends = str(e.value or "")
            if not self._suppress_events:
                self._update_pending_indicator()

        def on_length_change(self, e) -> None:
            self.form_length = str(e.value or "ALL")
            if not self._suppress_events:
                length_val: Optional[int] = None
                if self.form_length != "ALL":
                    try:
                        length_val = int(self.form_length)
                    except ValueError:
                        length_val = None
                self.applied_query["length_filter"] = length_val
                self._update_pending_indicator()
                self.run_applied_search(reset_pagination=True)

        def on_effect_change(self, e) -> None:
            self.form_effect = str(e.value or "")
            if not self._suppress_events:
                self._update_pending_indicator()

        def on_toggle_in_order(self) -> None:
            self.form_in_order = not self.form_in_order
            self._sync_pill_style(self.btn_in_order, self.form_in_order)
            self._update_pending_indicator()

        def on_toggle_exact_amount(self) -> None:
            self.form_exact_amount = not self.form_exact_amount
            self._sync_pill_style(self.btn_exact, self.form_exact_amount)
            self._update_pending_indicator()

        # ---- Immediate-Update Triggers ----
        def on_toggle_kind(self, kind: str) -> None:
            if kind in self.selected_kinds:
                self.selected_kinds.remove(kind)
            else:
                self.selected_kinds.add(kind)
            self._sync_kind_filter_controls()
            self.run_applied_search(reset_pagination=True)

        def on_toggle_two_letter_words(self) -> None:
            self.show_two_letter_words = not self.show_two_letter_words
            self._sync_pill_style(
                self.btn_two_letter_words, self.show_two_letter_words
            )
            self._sync_length_options()
            self._update_pending_indicator()
            self.run_applied_search(reset_pagination=True)

        def on_toggle_clever_mode(self) -> None:
            self.clever_mode = not self.clever_mode
            self._sync_clever_mode_button()
            self.run_applied_search(reset_pagination=True)

        def on_toggle_sort_mode(self) -> None:
            self.sort_mode = (
                "alphabetical" if self.sort_mode == "value" else "value"
            )
            self._sync_sort_mode_button()
            self.run_applied_search(reset_pagination=True)

        def on_order_change(self, e) -> None:
            if self._suppress_events:
                return
            self.descending = str(e.value or "Descending") == "Descending"
            self.run_applied_search(reset_pagination=True)

        def on_toggle_group(self) -> None:
            self.group_by_length = not self.group_by_length
            self._sync_pill_style(self.btn_group, self.group_by_length)
            self.run_applied_search(reset_pagination=True)

        def on_toggle_favorites_only(self) -> None:
            self.favorites_only = not self.favorites_only
            self._sync_favorite_style(self.favorites_only)
            self.run_applied_search(reset_pagination=True)

        def _cancel_pending_stat_filter_search(self) -> None:
            self._stat_filter_generation += 1
            if (
                self._stat_filter_task is not None
                and not self._stat_filter_task.done()
            ):
                self._stat_filter_task.cancel()
            self._stat_filter_task = None

        def on_toggle_stat_filter(self, stat_key: str) -> None:
            if stat_key in self.selected_stat_filters:
                self.selected_stat_filters.remove(stat_key)
            else:
                self.selected_stat_filters.add(stat_key)

            self.sort_mode = "value"
            selected = [
                key for key, _, _, _ in STAT_FILTERS
                if key in self.selected_stat_filters
            ]
            if len(selected) > 1:
                self.sort_by = "combined_stats"
            elif selected:
                self.sort_by = selected[0]
            else:
                self.sort_by = "points"

            self._sync_sort_mode_button()
            self._update_stat_filter_controls()
            self._cancel_pending_stat_filter_search()

            try:
                asyncio.get_running_loop()
            except RuntimeError:
                self.run_applied_search(reset_pagination=True)
                return

            generation = self._stat_filter_generation

            async def _debounced_search() -> None:
                try:
                    await asyncio.sleep(0.08)
                except asyncio.CancelledError:
                    return
                if (
                    generation != self._stat_filter_generation
                    or self.results_container is None
                    or self.results_container.is_deleted
                    or self.results_container.client.is_deleted
                ):
                    return
                self._stat_filter_task = None
                self.run_applied_search(reset_pagination=True)

            self._stat_filter_task = background_tasks.create(
                _debounced_search(), name="stat-filter-search"
            )

        def on_find_words(self) -> None:
            self.applied_query = self._snapshot_form()
            self._update_pending_indicator()
            self.run_applied_search(reset_pagination=True)

        def on_reset(self) -> None:
            self._suppress_events = True
            try:
                self.form_letters = ""
                self.form_contains = ""
                self.form_starts = ""
                self.form_ends = ""
                self.form_length = "ALL"
                self.form_effect = ""
                self.form_in_order = False
                self.form_exact_amount = False

                self.selected_kinds = {"TOWER", "HARVESTER", "MOD"}
                self.sort_by = "points"
                self.sort_mode = "value"
                self.descending = True
                self.group_by_length = False
                self.show_two_letter_words = False
                self.clever_mode = False
                self.favorites_only = False
                self.selected_stat_filters.clear()

                self.inp_letters.value = ""
                self.inp_contains.value = ""
                self.inp_starts.value = ""
                self.inp_ends.value = ""
                self.sel_length.value = "ALL"
                self._sync_length_options()
                self.sel_effect.value = ""
                self.sel_order.value = "Descending"
                self._sync_kind_filter_controls()
                self._sync_sort_mode_button()
                self._sync_pill_style(self.btn_group, False)
                self._sync_pill_style(self.btn_two_letter_words, False)
                self._sync_clever_mode_button()
                self._sync_pill_style(self.btn_in_order, False)
                self._sync_pill_style(self.btn_exact, False)
                self._sync_favorite_style(False)
                self._update_letter_count_label()
            finally:
                self._suppress_events = False

            self.applied_query = self._snapshot_form()
            self._update_pending_indicator()
            self.run_applied_search(reset_pagination=True)

        def on_use_word(self, word: str) -> None:
            """Copy word to clipboard, remove its letters from Available Letters, and refresh."""
            js_word = json.dumps(word)
            ui.run_javascript(
                f"""
                (function() {{
                  const txt = {js_word};
                  if (navigator.clipboard && navigator.clipboard.writeText) {{
                    navigator.clipboard.writeText(txt).catch(() => {{}});
                  }} else {{
                    const ta = document.createElement('textarea');
                    ta.value = txt;
                    document.body.appendChild(ta);
                    ta.select();
                    document.execCommand('copy');
                    document.body.removeChild(ta);
                  }}
                }})();
                """
            )

            source_rack = self.form_letters or self.applied_query["available_letters"]
            remaining, removed = consume_word_letters(source_rack, word)

            self._suppress_events = True
            try:
                self.form_letters = remaining
                self.inp_letters.value = remaining
                self._update_letter_count_label()
            finally:
                self._suppress_events = False

            self.applied_query["available_letters"] = remaining
            self._update_pending_indicator()

            if removed > 0:
                ui.notify(
                    f"Used {word.upper()} — copied & removed {removed} letters ({len(remaining)} left)",
                    type="positive",
                    position="bottom-right",
                    timeout=2200,
                )
            else:
                ui.notify(
                    f"Copied {word.upper()} to clipboard",
                    type="info",
                    position="bottom-right",
                    timeout=1800,
                )

            self.run_applied_search(reset_pagination=True)

        def on_toggle_word_favorite(self, word: str, heart_btn=None) -> None:
            if word in self.favorites:
                self.favorites.remove(word)
                is_fav = False
            else:
                self.favorites.add(word)
                is_fav = True
            self.user_data["favorites"] = sorted(self.favorites)
            try:
                save_user_data_json(self.user_data_path, self.user_data)
                self.user_data_source = self.user_data_path.name
                self.user_data_size_bytes = self.user_data_path.stat().st_size
                self.user_data_loaded = True
                self._set_settings_file_status(
                    "user_data",
                    self.user_data_size_bytes,
                    self.user_data_loaded,
                )
            except (OSError, TypeError, ValueError) as exc:
                self.user_data_loaded = False
                self._set_settings_file_status("user_data", None, False)
                ui.notify(f"Could not save user data: {exc}", type="negative")
            self._update_favorites_banner()

            if self.favorites_only:
                self.run_applied_search(reset_pagination=False)
            elif heart_btn is not None:
                heart_btn.set_text("♥" if is_fav else "♡")
                heart_btn.style(
                    f"color: {'#D93829' if is_fav else '#666666'}; min-width: 24px;"
                )

        # ---- Search & Render ----
        def _cancel_pending_clever_search(self) -> None:
            self._clever_search_generation += 1
            if self._clever_cancel_event is not None:
                self._clever_cancel_event.set()
                self._clever_cancel_event = None
            if self._clever_task is not None and not self._clever_task.done():
                self._clever_task.cancel()
            self._clever_task = None
            self.clever_searching = False

        def _set_combinations(
            self,
            combinations: List[Tuple[UnitRecord, ...]],
            truncated: bool,
        ) -> Dict[int, List[Tuple[UnitRecord, ...]]]:
            grouped: Dict[int, List[Tuple[UnitRecord, ...]]] = {}
            for combination in combinations:
                grouped.setdefault(len(combination), []).append(combination)
            self.current_combinations = combinations
            self.combinations_by_word_count = grouped
            self.combinations_truncated = truncated
            return grouped

        def _update_clever_result_count_label(self) -> None:
            if self.lbl_result_count is None:
                return
            n = len(self.current_combinations)
            noun = "combination" if n == 1 else "combinations"
            if self.combinations_truncated:
                self.lbl_result_count.set_text(
                    f"{n:,}+ {noun} found (limit reached)"
                )
            else:
                self.lbl_result_count.set_text(f"{n:,} {noun} found")

        def _start_clever_search(
            self,
            matches: List[UnitRecord],
            available_letters: str,
            include_two_letter_words: bool,
            clever_key: Tuple[Any, ...],
        ) -> None:
            generation = self._clever_search_generation
            cancel_event = threading.Event()
            self._clever_cancel_event = cancel_event
            match_snapshot = list(matches)

            try:
                asyncio.get_running_loop()
            except RuntimeError:
                combinations, truncated = find_exact_word_combinations(
                    match_snapshot,
                    available_letters,
                    include_two_letter_words,
                    cancel_event=cancel_event,
                )
                grouped = self._set_combinations(combinations, truncated)
                self._cached_clever_key = clever_key
                self._cached_clever_result = (combinations, grouped, truncated)
                self._update_clever_result_count_label()
                self._sync_group_collapse_button()
                self._update_favorites_banner()
                self._render_results()
                return

            self.clever_searching = True
            self.current_combinations = []
            self.combinations_by_word_count = {}
            self.combinations_truncated = False

            if self.lbl_result_count is not None:
                self.lbl_result_count.set_text("Searching combinations...")
            self._sync_group_collapse_button()
            self._update_favorites_banner()
            self._render_results()

            async def worker() -> None:
                try:
                    combinations, truncated = await asyncio.to_thread(
                        find_exact_word_combinations,
                        match_snapshot,
                        available_letters,
                        include_two_letter_words,
                        cancel_event=cancel_event,
                    )
                except asyncio.CancelledError:
                    cancel_event.set()
                    return

                if (
                    generation != self._clever_search_generation
                    or not self.clever_mode
                    or self.results_container is None
                    or self.results_container.is_deleted
                    or self.results_container.client.is_deleted
                ):
                    return

                self.clever_searching = False
                self._clever_cancel_event = None
                self._clever_task = None
                grouped = self._set_combinations(combinations, truncated)
                self._cached_clever_key = clever_key
                self._cached_clever_result = (combinations, grouped, truncated)
                self._update_clever_result_count_label()
                self._sync_group_collapse_button()
                self._update_favorites_banner()
                self._render_results()

            self._clever_task = background_tasks.create(
                worker(), name="clever-mode-search"
            )

        def run_applied_search(self, reset_pagination: bool = True) -> None:
            self._cancel_pending_stat_filter_search()
            self._cancel_pending_clever_search()
            q = self.applied_query
            if not GLOBAL_DB.units:
                self.current_matches = []
                self._set_combinations([], False)
                self.stat_filter_counts = {}
                self.group_visible_limits.clear()
                self._update_stat_filter_controls()
                self.lbl_result_count.set_text(
                    "0 combinations found"
                    if self.clever_mode
                    else "0 words loaded"
                )
                self._sync_group_collapse_button()
                self._update_favorites_banner()
                self._render_results()
                return

            clean_rack = any(
                ("a" <= ch.lower() <= "z") or ch in ("?", "*")
                for ch in q["available_letters"]
            )
            if self.clever_mode and not clean_rack:
                self.current_matches = []
                self._set_combinations([], False)
                self.stat_filter_counts = {}
                self._update_stat_filter_controls()
                if reset_pagination:
                    self.visible_limit = PAGE_SIZE
                    self.collapsed_lengths.clear()
                    self.collapsed_clever_groups.clear()
                    self.group_visible_limits.clear()
                if self.lbl_result_count is not None:
                    self.lbl_result_count.set_text("0 combinations found")
                self._sync_group_collapse_button()
                self._update_favorites_banner()
                self._render_results()
                return

            base_sort_by = (
                "alphabetical"
                if self.sort_mode == "alphabetical"
                else (
                    "points"
                    if self.sort_by == "combined_stats"
                    else self.sort_by
                )
            )
            favorites_key = (
                frozenset(self.favorites) if self.favorites_only else None
            )
            base_key = (
                GLOBAL_DB.revision,
                q["available_letters"],
                q["starts_with"],
                q["ends_with"],
                q["contains"],
                q["in_order"],
                q["exact_amount"],
                q["length_filter"],
                q["effect_filter"],
                self.favorites_only,
                favorites_key,
                frozenset(self.selected_kinds),
                self.show_two_letter_words,
            )
            if base_key == self._cached_base_key:
                base_matches = self._cached_base_matches
                self.stat_filter_counts = dict(self._cached_stat_counts)
            else:
                base_matches = GLOBAL_DB.search(
                    available_letters=q["available_letters"],
                    starts_with=q["starts_with"],
                    ends_with=q["ends_with"],
                    contains=q["contains"],
                    in_order=q["in_order"],
                    exact_amount=q["exact_amount"],
                    length_filter=q["length_filter"],
                    effect_filter=q["effect_filter"],
                    favorites_only=self.favorites_only,
                    favorites=self.favorites,
                    kind_filters=self.selected_kinds,
                    include_two_letter_words=self.show_two_letter_words,
                    sort_results=False,
                )

                stat_counts = [0] * len(STAT_FILTERS)
                for rec in base_matches:
                    mask = rec._positive_stat_mask
                    while mask:
                        bit = mask & -mask
                        stat_counts[bit.bit_length() - 1] += 1
                        mask ^= bit
                self.stat_filter_counts = {
                    stat_key: stat_counts[index]
                    for index, (stat_key, _, _, _) in enumerate(STAT_FILTERS)
                }
                self._cached_base_key = base_key
                self._cached_base_matches = base_matches
                self._cached_stat_counts = dict(self.stat_filter_counts)
                self._cached_max_changes.clear()
                self._cached_sorted_key = None
                self._cached_sorted_matches = []
            self._update_stat_filter_controls()

            selected_stats = [
                key
                for key, _, _, _ in STAT_FILTERS
                if key in self.selected_stat_filters
            ]
            if selected_stats:
                required_mask = 0
                for key in selected_stats:
                    required_mask |= STAT_FILTER_BITS[key]
                matches = [
                    rec
                    for rec in base_matches
                    if (rec._positive_stat_mask & required_mask) == required_mask
                ]
                if not self.clever_mode:
                    if (
                        len(selected_stats) > 1
                        and self.sort_by == "combined_stats"
                        and self.sort_mode == "value"
                    ):
                        self._sort_combined_results(
                            matches, base_matches, selected_stats
                        )
                    else:
                        GLOBAL_DB._sort_results(
                            matches,
                            sort_by=base_sort_by,
                            descending=self.descending,
                            group_by_length=self.group_by_length,
                        )
            elif self.clever_mode:
                matches = base_matches
            else:
                sorted_key = (
                    base_key,
                    base_sort_by,
                    self.descending,
                    self.group_by_length,
                )
                if sorted_key == self._cached_sorted_key:
                    matches = self._cached_sorted_matches
                else:
                    matches = list(base_matches)
                    GLOBAL_DB._sort_results(
                        matches,
                        sort_by=base_sort_by,
                        descending=self.descending,
                        group_by_length=self.group_by_length,
                    )
                    self._cached_sorted_key = sorted_key
                    self._cached_sorted_matches = matches

            self.current_matches = matches
            if reset_pagination:
                self.visible_limit = PAGE_SIZE
                self.collapsed_lengths.clear()
                self.collapsed_clever_groups.clear()
                self.group_visible_limits.clear()

            if self.clever_mode:
                clever_key = (
                    GLOBAL_DB.revision,
                    q["available_letters"],
                    q["starts_with"],
                    q["ends_with"],
                    q["contains"],
                    q["in_order"],
                    q["exact_amount"],
                    q["length_filter"],
                    q["effect_filter"],
                    self.favorites_only,
                    favorites_key,
                    frozenset(self.selected_kinds),
                    frozenset(self.selected_stat_filters),
                    self.show_two_letter_words,
                )
                if (
                    clever_key == self._cached_clever_key
                    and self._cached_clever_result is not None
                ):
                    combos, grouped, truncated = self._cached_clever_result
                    self.current_combinations = combos
                    self.combinations_by_word_count = grouped
                    self.combinations_truncated = truncated
                    self._update_clever_result_count_label()
                    self._sync_group_collapse_button()
                    self._update_favorites_banner()
                    self._render_results()
                    return

                self._start_clever_search(
                    matches,
                    q["available_letters"],
                    self.show_two_letter_words,
                    clever_key,
                )
                return

            self._set_combinations([], False)
            n = len(matches)
            word_lbl = "word" if n == 1 else "words"
            self.lbl_result_count.set_text(f"{n:,} {word_lbl} found")
            self._sync_group_collapse_button()
            self._update_favorites_banner()
            self._render_results()

        def _load_more(self, amount: int = PAGE_SIZE) -> None:
            self.visible_limit += amount
            self._render_results_preserving_scroll()

        def _render_results_preserving_scroll(self) -> None:
            ui.run_javascript(
                "const x = window.scrollX, y = window.scrollY; "
                "const restore = () => window.scrollTo(x, y); "
                "window.__babbleRestoreScroll = restore; "
                "restore(); "
                "setTimeout(restore, 50); "
                "setTimeout(restore, 150); "
                "setTimeout(restore, 350);"
            )
            self._render_results()

        def _render_results(self) -> None:
            self.results_container.clear()
            matches = self.current_matches

            with self.results_container:
                if self.clever_mode:
                    if self.clever_searching:
                        with ui.row().classes(
                            "w-full items-center justify-center gap-2 py-10"
                        ):
                            ui.spinner(size="sm", color="#795548")
                            ui.label("Searching combinations...").classes(
                                "text-sm font-bold"
                            ).style("color: #595959;")
                        return
                    if not self.current_combinations:
                        with ui.column().classes("w-full items-center py-10"):
                            ui.label("No combinations found.").classes(
                                "text-base font-bold"
                            ).style("color: #595959;")
                            clean_rack = any(
                                ("a" <= ch.lower() <= "z") or ch in ("?", "*")
                                for ch in self.applied_query["available_letters"]
                            )
                            message = (
                                "No combination uses every available letter."
                                if clean_rack
                                else "Enter available letters and click FIND WORDS."
                            )
                            ui.label(message).classes("text-sm").style(
                                "color: #777777;"
                            )
                        return
                    self._render_clever_results()
                    return

                if not matches:
                    with ui.column().classes("w-full items-center py-10"):
                        ui.label("No matching words found.").classes(
                            "text-base font-bold"
                        ).style("color: #595959;")
                        ui.label(
                            "Type letters above and click FIND WORDS, or adjust your filters."
                        ).classes("text-sm").style("color: #777777;")
                    return

                active_stat = (
                    self.sort_by
                    if self.sort_mode == "value"
                    and self.sort_by not in (
                        "points",
                        "combined_stats",
                    )
                    else None
                )
                exact_letters = "".join(
                    ch
                    for ch in self.applied_query["available_letters"].lower()
                    if ("a" <= ch <= "z") or ch in ("?", "*")
                )
                valid_word = None
                if exact_letters and "?" not in exact_letters and "*" not in exact_letters:
                    valid_word = next(
                        (rec for rec in matches if rec.word == exact_letters), None
                    )

                if valid_word is not None:
                    ui.label(f"{valid_word.word_upper} is a valid word").classes(
                        "text-sm font-bold"
                    ).style("color: #087007;")
                    self._render_unit_box(valid_word, active_stat)

                remaining_matches = [
                    rec for rec in matches if rec is not valid_word
                ]

                if self.group_by_length:
                    grouped_matches: Dict[int, List[UnitRecord]] = {}
                    for record in remaining_matches:
                        grouped_matches.setdefault(record.length, []).append(record)

                    group_count = len(grouped_matches)
                    for length, group_items in grouped_matches.items():
                        group_key = ("length", length)
                        visible_count = self._group_visible_count(
                            group_key, len(group_items), group_count
                        )
                        self._render_length_group(
                            length,
                            group_items[:visible_count],
                            len(group_items),
                            active_stat,
                        )
                    self._render_grouped_pagination_footer()
                    return

                visible_limit = self.visible_limit - (
                    1 if valid_word is not None else 0
                )
                visible = remaining_matches[:visible_limit]
                with ui.column().classes("w-full gap-1.5"):
                    for rec in visible:
                        self._render_unit_box(rec, active_stat)

                # Load-more footer when results exceed current page limit
                remaining = len(matches) - len(visible) - (
                    1 if valid_word is not None else 0
                )
                if remaining > 0:
                    with ui.row().classes(
                        "w-full items-center justify-center gap-3 pt-3 pb-1"
                    ):
                        ui.label(
                            f"Showing {len(visible):,} of {len(matches):,} words"
                        ).classes("text-xs font-bold").style("color: #595959;")
                        ui.button(
                            f"SHOW {min(PAGE_SIZE, remaining)} MORE",
                            on_click=lambda: self._load_more(PAGE_SIZE),
                        ).props("unelevated dense").classes("babble-pill px-4")
                        if remaining <= 600:
                            ui.button(
                                f"SHOW ALL ({len(matches):,})",
                                on_click=lambda: self._load_more(remaining),
                            ).props("unelevated dense").classes("babble-pill-blue px-4")

        def _render_clever_results(self) -> None:
            if self.combinations_truncated:
                ui.label(
                    f"Showing the first {len(self.current_combinations):,} combinations "
                    "(shortest word counts first). Add more filters to narrow results."
                ).classes("text-xs font-bold pb-1").style("color: #795548;")

            combinations_by_word_count = self.combinations_by_word_count
            group_count = len(combinations_by_word_count)
            for word_count in sorted(combinations_by_word_count):
                group_key = ("clever", word_count)
                combinations = combinations_by_word_count[word_count]
                visible_count = self._group_visible_count(
                    group_key, len(combinations), group_count
                )
                self._render_clever_group(
                    word_count,
                    combinations[:visible_count],
                    len(combinations),
                )
            self._render_grouped_pagination_footer()

        def _render_clever_group(
            self,
            word_count: int,
            combinations: List[Tuple[UnitRecord, ...]],
            total_count: int,
        ) -> None:
            is_collapsed = word_count in self.collapsed_clever_groups
            with ui.column().classes("w-full gap-1.5 mb-2"):
                header = ui.row().classes(
                    "w-full items-center justify-between babble-group-bar"
                )
                with header:
                    with ui.row().classes("items-center gap-2"):
                        arrow_lbl = ui.label("▸" if is_collapsed else "▾").classes(
                            "text-sm font-bold"
                        ).style("color: #222222; width: 12px;")
                        label = "WORD" if word_count == 1 else "WORDS"
                        ui.label(
                            f"{word_count} {label} PER COMBINATION"
                        ).classes("text-xs font-bold tracking-wide").style(
                            "color: #222222;"
                        )
                    count_txt = (
                        f"{len(combinations):,} / {total_count:,}"
                        if len(combinations) < total_count
                        else f"{total_count:,}"
                    )
                    ui.label(count_txt).classes("text-xs font-bold").style(
                        "color: #595959;"
                    )

                body = ui.column().classes("w-full gap-1.5")
                body.set_visibility(not is_collapsed)
                with body:
                    for combination in combinations:
                        self._render_combination_box(combination)

                    if len(combinations) < total_count:
                        remaining = total_count - len(combinations)
                        ui.button(
                            f"SHOW {min(PAGE_SIZE, remaining)} MORE",
                            on_click=lambda _=None, key=("clever", word_count), total=total_count: self._load_more_group(
                                key, total
                            ),
                        ).props("unelevated dense").classes(
                            "babble-pill px-4 self-center"
                        )

                def toggle_group(
                    _=None,
                    count=word_count,
                    group_body=body,
                    arrow=arrow_lbl,
                ):
                    if count in self.collapsed_clever_groups:
                        self.collapsed_clever_groups.remove(count)
                        group_body.set_visibility(True)
                        arrow.set_text("▾")
                    else:
                        self.collapsed_clever_groups.add(count)
                        group_body.set_visibility(False)
                        arrow.set_text("▸")
                    self._sync_group_collapse_button()

                header.on("click", toggle_group)

        def _render_combination_box(
            self, combination: Tuple[UnitRecord, ...]
        ) -> None:
            state = {"open": False, "built": False}
            box = ui.column().classes("w-full babble-combo-box gap-0")

            with box:
                with ui.row().classes(
                    "w-full items-center justify-between no-wrap gap-2"
                ):
                    with ui.row().classes(
                        "items-center gap-2 flex-wrap min-w-0"
                    ):
                        for index, rec in enumerate(combination):
                            if index:
                                ui.label("+").classes(
                                    "text-sm font-bold"
                                ).style("color: #777777;")
                            meta = (
                                KIND_META["CURSED"]
                                if rec.is_cursed
                                else KIND_META.get(
                                    rec.kind, KIND_META["TOWER"]
                                )
                            )
                            with ui.row().classes("items-baseline gap-1"):
                                ui.label(rec.word_upper).classes(
                                    "text-sm font-bold"
                                ).style(f"color: {meta['color']};")
                                ui.label(f"({meta['display']})").classes(
                                    "text-xs font-bold"
                                ).style(f"color: {meta['color']};")

                    with ui.row().classes(
                        "items-center gap-1.5 no-wrap shrink-0"
                    ):
                        total_pts = sum(rec.scrabble for rec in combination)
                        ui.label(f"{total_pts} PTS").classes("babble-pts-tile")
                        chevron_lbl = ui.label("▸").classes(
                            "text-xs font-bold"
                        ).style(
                            "color: #595959; width: 10px; text-align: right;"
                        )

                details_col = ui.column().classes("w-full gap-2 pt-2.5")
                details_col.set_visibility(False)

            def toggle_open(_e=None):
                state["open"] = not state["open"]
                is_open = state["open"]
                if is_open and not state["built"]:
                    state["built"] = True
                    self._populate_combination_details(details_col, combination)

                details_col.set_visibility(is_open)
                chevron_lbl.set_text("▾" if is_open else "▸")
                if is_open:
                    box.classes(add="babble-combo-box-open")
                else:
                    box.classes(remove="babble-combo-box-open")

            box.on("click", toggle_open)

        def _populate_combination_details(
            self, container, combination: Tuple[UnitRecord, ...]
        ) -> None:
            with container:
                for rec in combination:
                    meta = (
                        KIND_META["CURSED"]
                        if rec.is_cursed
                        else KIND_META.get(rec.kind, KIND_META["TOWER"])
                    )
                    is_fav = rec.word in self.favorites
                    kind_class = (
                        "babble-unit-box-cursed"
                        if rec.is_cursed
                        else f"babble-unit-box-{rec.kind.lower()}"
                    )
                    with ui.column().classes(
                        f"w-full babble-combo-unit {kind_class} gap-1.5"
                    ):
                        with ui.row().classes(
                            "w-full items-start justify-between no-wrap gap-2"
                        ):
                            with ui.row().classes(
                                "items-center gap-1.5 flex-wrap min-w-0"
                            ):
                                heart_btn = (
                                    ui.button("♥" if is_fav else "♡")
                                    .props("flat dense round size=sm")
                                    .style(
                                        f"color: {'#FF5604' if is_fav else '#666666'}; "
                                        "min-width: 24px; min-height: 24px; font-size: 15px; padding: 0;"
                                    )
                                )
                                heart_btn.on(
                                    "click.stop",
                                    lambda _e, w=rec.word, hb=heart_btn: self.on_toggle_word_favorite(
                                        w, hb
                                    ),
                                )
                                ui.label(rec.word_upper).classes(
                                    "text-base font-bold leading-tight"
                                ).style(f"color: {meta['color']};")
                                ui.label(f"({meta['display']})").classes(
                                    "text-sm font-bold leading-tight"
                                ).style(f"color: {meta['color']};")

                            with ui.row().classes("items-start gap-2 shrink-0"):
                                with ui.row().classes(
                                    "items-center gap-1.5 pt-0.5"
                                ):
                                    use_btn = (
                                        ui.button("USE")
                                        .props("unelevated dense")
                                        .classes("babble-mini-use")
                                    )
                                    use_btn.tooltip(
                                        "Copy word, remove its letters from Available Letters, and refresh"
                                    )
                                    use_btn.on(
                                        "click.stop",
                                        lambda _e, w=rec.word: self.on_use_word(
                                            w
                                        ),
                                    )

                                    def_url = build_definition_url(
                                        self.dictionary_url, rec.word
                                    )
                                    def_btn = (
                                        ui.button("DEFINITION")
                                        .props(
                                            f'unelevated dense href="{def_url}" target="_blank"'
                                        )
                                        .classes("babble-mini-use")
                                    )
                                    def_btn.tooltip(
                                        f"Open definition for '{rec.word}'"
                                    )
                                    def_btn.on("click.stop", lambda _e: None)

                                with ui.column().classes("items-end gap-1"):
                                    ui.label(f"{rec.scrabble} PTS").classes(
                                        "babble-pts-tile"
                                    )
                                    ui.label(f"{rec.length} letters").classes(
                                        "text-xs font-medium"
                                    ).style("color: #666666; line-height: 1;")

                        unit_details = ui.column().classes(
                            "w-full gap-1.5 pl-7 pr-2"
                        )
                        self._populate_expanded_details(unit_details, rec)

        def _render_length_group(
            self,
            length: int,
            items: List[UnitRecord],
            total_count: int,
            active_stat: Optional[str],
        ) -> None:
            is_collapsed = length in self.collapsed_lengths
            with ui.column().classes("w-full gap-1.5 mb-2"):
                header = ui.row().classes(
                    "w-full items-center justify-between babble-group-bar"
                )
                with header:
                    with ui.row().classes("items-center gap-2"):
                        arrow_lbl = ui.label("▸" if is_collapsed else "▾").classes(
                            "text-sm font-bold"
                        ).style("color: #222222; width: 12px;")
                        ui.label(f"{length} LETTER WORDS").classes(
                            "text-xs font-bold tracking-wide"
                        ).style("color: #222222;")
                    count_txt = (
                        f"{len(items):,} / {total_count:,}"
                        if len(items) < total_count
                        else f"{total_count:,}"
                    )
                    ui.label(count_txt).classes("text-xs font-bold").style(
                        "color: #595959;"
                    )

                body = ui.column().classes("w-full gap-1.5")
                body.set_visibility(not is_collapsed)
                with body:
                    for rec in items:
                        self._render_unit_box(rec, active_stat)
                    if len(items) < total_count:
                        remaining = total_count - len(items)
                        ui.button(
                            f"SHOW {min(PAGE_SIZE, remaining)} MORE",
                            on_click=lambda _=None, key=("length", length), total=total_count: self._load_more_group(
                                key, total
                            ),
                        ).props("unelevated dense").classes(
                            "babble-pill px-4 self-center"
                        )

                def toggle_group(_=None, L=length, b=body, a=arrow_lbl):
                    if L in self.collapsed_lengths:
                        self.collapsed_lengths.remove(L)
                        b.set_visibility(True)
                        a.set_text("▾")
                    else:
                        self.collapsed_lengths.add(L)
                        b.set_visibility(False)
                        a.set_text("▸")
                    self._sync_group_collapse_button()

                header.on("click", toggle_group)

        def _render_unit_box(
            self, rec: UnitRecord, active_stat: Optional[str]
        ) -> None:
            meta = KIND_META["CURSED"] if rec.is_cursed else KIND_META.get(
                rec.kind, KIND_META["TOWER"]
            )
            is_fav = rec.word in self.favorites
            state = {"open": False, "built": False}

            kind_class = (
                "babble-unit-box-cursed"
                if rec.is_cursed
                else f"babble-unit-box-{rec.kind.lower()}"
            )
            box = ui.column().classes(
                f"w-full babble-unit-box {kind_class} gap-0"
            )

            with box:
                # ---- TOP ROW: Left (Heart + WORD (kind) + unopened preview), Right (Actions + PTS + letter count) ----
                with ui.row().classes(
                    "w-full items-start justify-between no-wrap gap-2"
                ):
                    # Left column: title + unopened 3-stat preview
                    with ui.column().classes("gap-1 flex-grow min-w-0"):
                        with ui.row().classes("items-center gap-1.5 flex-wrap"):
                            heart_btn = (
                                ui.button("♥" if is_fav else "♡")
                                .props("flat dense round size=sm")
                                .style(
                                    f"color: {'#FF5604' if is_fav else '#666666'}; "
                                    "min-width: 24px; min-height: 24px; font-size: 15px; padding: 0;"
                                )
                            )
                            heart_btn.on(
                                "click.stop",
                                lambda _e, w=rec.word, hb=heart_btn: self.on_toggle_word_favorite(
                                    w, hb
                                ),
                            )

                            # Colored WORD + colored (tower) / (mod) / (harvester)
                            ui.label(rec.word_upper).classes(
                                "text-base font-bold leading-tight"
                            ).style(f"color: {meta['color']};")
                            ui.label(f"({meta['display']})").classes(
                                "text-sm font-bold leading-tight"
                            ).style(f"color: {meta['color']};")

                        # Unopened 3-stat preview row (hidden when unfolded)
                        preview_row = ui.row().classes(
                            "items-center gap-x-2 gap-y-0.5 flex-wrap pl-7"
                        )
                        with preview_row:
                            preview_stats = rec.get_preview_stats(active_stat)
                            for idx_s, (val_str, lbl_str, tone) in enumerate(
                                preview_stats
                            ):
                                if idx_s > 0:
                                    ui.label("·").classes("text-xs").style(
                                        "color: #777777;"
                                    )
                                with ui.row().classes("items-baseline gap-1"):
                                    ui.label(val_str).classes(
                                        f"text-xs stat-{tone}"
                                    )
                                    if lbl_str:
                                        ui.label(lbl_str).classes("text-xs").style(
                                            "color: #111111;"
                                        )

                    # Right column: Action buttons + PTS tile + Letter count (bottom right below PTS)
                    with ui.row().classes("items-start gap-2 shrink-0"):
                        # Action buttons (USE + DEF)
                        with ui.row().classes("items-center gap-1.5 pt-0.5"):
                            use_btn = (
                                ui.button("USE")
                                .props("unelevated dense")
                                .classes("babble-mini-use")
                            )
                            use_btn.tooltip(
                                "Copy word, remove its letters from Available Letters, and refresh"
                            )
                            use_btn.on(
                                "click.stop",
                                lambda _e, w=rec.word: self.on_use_word(w),
                            )

                            def_url = build_definition_url(
                                self.dictionary_url, rec.word
                            )
                            def_btn = (
                                ui.button("DEFINITION")
                                .props(
                                    f'unelevated dense href="{def_url}" target="_blank"'
                                )
                                .classes("babble-mini-use")
                            )
                            def_btn.tooltip(f"Open definition for '{rec.word}'")
                            def_btn.on("click.stop", lambda _e: None)

                        # Rightmost stack: [PTS tile] on top, [X letters] directly below PTS
                        with ui.column().classes("items-end gap-1"):
                            with ui.row().classes("items-center gap-1.5 no-wrap"):
                                ui.label(f"{rec.scrabble} PTS").classes(
                                    "babble-pts-tile"
                                )
                                chevron_lbl = ui.label("▸").classes(
                                    "text-xs font-bold"
                                ).style("color: #595959; width: 10px; text-align: right;")

                            # Letter count displayed in bottom right corner when unopened, below PTS
                            letter_lbl = ui.label(f"{rec.length} letters").classes(
                                "text-xs font-medium pr-3.5"
                            ).style("color: #666666; line-height: 1;")

                # ---- UNFOLDED DETAILS CONTAINER (built lazily on first click) ----
                details_col = ui.column().classes("w-full gap-1.5 pt-2 pl-7 pr-2")
                details_col.set_visibility(False)

            def toggle_open(_e=None):
                state["open"] = not state["open"]
                is_open = state["open"]
                if is_open and not state["built"]:
                    state["built"] = True
                    self._populate_expanded_details(details_col, rec)

                preview_row.set_visibility(not is_open)
                details_col.set_visibility(is_open)
                chevron_lbl.set_text("▾" if is_open else "▸")
                if is_open:
                    box.classes(add="babble-unit-box-open")
                else:
                    box.classes(remove="babble-unit-box-open")

            box.on("click", toggle_open)

        def _populate_expanded_details(self, container, rec: UnitRecord) -> None:
            """Render full Towers of Babble tooltip-style breakdown inside unfolded box."""
            with container:
                if rec.kind == "TOWER":
                    # Specials right below title (just like +40.32 Burn Aura)
                    for name, val in rec.specials:
                        with ui.row().classes("items-baseline gap-1.5"):
                            ui.label(f"+{fmt_num(val, 2)}").classes(
                                "text-sm stat-pos"
                            )
                            ui.label(pretty_name(name)).classes("text-sm").style(
                                "color: #000000;"
                            )
                            if name == "crit":
                                ui.label(f"({format_crit_summary(val)})").classes(
                                    "text-sm"
                                ).style("color: #000000;")

                    if rec.is_cursed and rec.curse_effects:
                        ui.separator().style("background-color: #C4C4C4; margin: 4px 0;")
                        ui.label("Possible Curse Effects").classes("babble-field-lbl")
                        with ui.column().classes("gap-0.5"):
                            for effect in rec.curse_effects:
                                ui.label(pretty_name(effect)).classes("text-sm").style(
                                    "color: #000000;"
                                )

                    ui.separator().style("background-color: #C4C4C4; margin: 4px 0;")
                    ui.label("TOWER STATS").classes("babble-field-lbl")

                    dmg_t = self._cmp_tone(rec.damage, TOWER_DEFAULTS["damage"])
                    dps_t = self._cmp_tone(rec.dps, 5.5)
                    spd_t = self._cmp_tone(
                        rec.attack_speed, TOWER_DEFAULTS["attackSpeed"]
                    )
                    rng_t = self._cmp_tone(rec.range, TOWER_DEFAULTS["range"])
                    hp_t = self._cmp_tone(rec.health, TOWER_DEFAULTS["health"])
                    arm_t = self._cmp_tone(rec.armor, TOWER_DEFAULTS["armor"])

                    stats_grid = [
                        ("Damage", fmt_num(rec.damage, 2), dmg_t),
                        ("DPS", fmt_num(rec.dps, 2), dps_t),
                        (
                            "Attack Speed",
                            f"{fmt_num(rec.attack_speed, 2)} ({fmt_num(rec.attacks_per_second, 2)}/sec)",
                            spd_t,
                        ),
                        ("Range", fmt_num(rec.range, 2), rng_t),
                        ("HP", fmt_num(rec.health, 1), hp_t),
                        ("Armor", fmt_num(rec.armor, 2), arm_t),
                    ]
                    self._render_stat_grid(stats_grid)

                elif rec.kind == "HARVESTER":
                    if rec.harvest_resources:
                        with ui.row().classes("items-center gap-4 flex-wrap pb-1"):
                            for res in rec.harvest_resources:
                                letter, fg, rbg = RESOURCE_COLORS.get(
                                    res, ("?", "#111111", "#CCCCCC")
                                )
                                with ui.row().classes("items-center gap-1.5"):
                                    ui.label(letter).classes("babble-res-dot").style(
                                        f"background-color: {rbg}; color: {fg};"
                                    )
                                    ui.label(f"Resource {res.title()}").classes(
                                        "text-sm font-bold"
                                    ).style("color: #111111;")

                    for name, val in rec.specials:
                        with ui.row().classes("items-baseline gap-1.5"):
                            ui.label(f"+{fmt_num(val, 2)}").classes("text-sm stat-pos")
                            ui.label(pretty_name(name)).classes("text-sm").style(
                                "color: #000000;"
                            )

                    ui.separator().style("background-color: #C4C4C4; margin: 4px 0;")
                    ui.label("HARVESTER STATS").classes("babble-field-lbl")

                    amt_t = self._cmp_tone(
                        rec.harvest_amount, HARVESTER_DEFAULTS["harvestAmount"]
                    )
                    spd_t = self._cmp_tone(rec.harvest_speed, 1.0 / 3.2)
                    rate_t = self._cmp_tone(rec.harvest_rate, 2.0 / 3.2)
                    rng_t = self._cmp_tone(
                        rec.harvest_range, HARVESTER_DEFAULTS["harvestRange"]
                    )
                    hp_t = self._cmp_tone(rec.health, HARVESTER_DEFAULTS["health"])
                    arm_val = rec.armor if rec.armor is not None else 0.0
                    arm_t = "pos" if arm_val > 0.01 else "neutral"

                    stats_grid = [
                        ("Harvest Amount", fmt_num(rec.harvest_amount, 2), amt_t),
                        (
                            "Harvest Speed",
                            f"{fmt_num(rec.harvest_speed, 2)}/s ({fmt_num(rec.harvest_interval, 3)}s)",
                            spd_t,
                        ),
                        ("Harvest Rate", f"{fmt_num(rec.harvest_rate, 2)}/s", rate_t),
                        ("Range", fmt_num(rec.harvest_range, 2), rng_t),
                        (
                            "Resource Types",
                            str(rec.harvest_types or 0),
                            "pos" if (rec.harvest_types or 0) > 1 else "neutral",
                        ),
                        ("HP", fmt_num(rec.health, 1), hp_t),
                        ("Armor", fmt_num(arm_val, 2), arm_t),
                    ]
                    self._render_stat_grid(stats_grid)

                else:  # MOD
                    if not rec.deltas:
                        ui.label("No modifier effects defined.").classes(
                            "text-sm"
                        ).style("color: #666666;")
                    else:
                        for stat, op, val in rec.deltas:
                            v_txt = (
                                f"×{fmt_num(val, 3)}"
                                if op == "mult"
                                else f"+{fmt_num(val, 2)}"
                            )
                            with ui.row().classes("items-baseline gap-1.5"):
                                ui.label(v_txt).classes("text-sm stat-pos")
                                ui.label(pretty_name(stat)).classes("text-sm").style(
                                    "color: #000000;"
                                )
                                if op:
                                    display_op = "add" if op.lower() == "grant" else op
                                    ui.label(f"({display_op})").classes("text-xs").style(
                                        "color: #666666;"
                                    )
                                if stat == "crit":
                                    ui.label(f"({format_crit_summary(val)})").classes(
                                        "text-sm"
                                    ).style("color: #000000;")

        def _render_stat_grid(self, items: List[Tuple[str, str, str]]) -> None:
            with ui.element("div").classes(
                "w-full grid grid-cols-2 gap-x-6 gap-y-1 pt-0.5"
            ):
                for lbl, val, tone in items:
                    with ui.row().classes("items-baseline gap-1.5 no-wrap"):
                        ui.label(f"{lbl}:").classes("text-xs").style("color: #595959;")
                        ui.label(val).classes(f"text-xs stat-{tone}")

        def _cmp_tone(self, val: Optional[float], default: float) -> str:
            if val is None:
                return "neutral"
            if val > default + 0.01:
                return "pos"
            if val < default - 0.01:
                return "neg"
            return "neutral"

        # ---- Settings Dialog ----
        def _set_settings_file_status(
            self, key: str, size_bytes: Optional[int], loaded: bool
        ) -> None:
            if loaded and size_bytes is not None:
                text = format_file_size(size_bytes)
            else:
                loaded = False
                text = "File not loaded"
            self.settings_file_status[key] = (text, loaded)
            label = self.settings_file_labels.get(key)
            if label is not None:
                label.set_text(text)
                color = "#2E7D32" if loaded else "#B71C1C"
                label.style(f"background-color: {color} !important;")
            upload = self.settings_upload_boxes.get(key)
            if upload is not None:
                upload.classes(
                    remove="babble-file-loaded babble-file-not-loaded",
                    add="babble-file-loaded" if loaded else "babble-file-not-loaded",
                )

            self._update_main_file_status()

        def _file_load_summary(self) -> Tuple[str, bool]:
            labels = {
                "units": "UNITS JSON",
                "cursed": "CURSED WORDS JSON",
                "blacklist": "BLACKLIST TXT",
                "user_data": "USER DATA JSON",
            }
            missing = [
                labels[key]
                for key, (_, loaded) in self.settings_file_status.items()
                if not loaded
            ]
            if not missing:
                return "All files loaded", True
            return f"Missing: {', '.join(missing)}", False

        def _build_settings_dialog(self) -> None:
            self.settings_dialog = ui.dialog()
            with self.settings_dialog, ui.card().classes(
                "w-[760px] max-w-full"
            ).style("background: #F4F4F4; border: 1px solid #B7B7B7;"):
                ui.label("OPTIONS").classes("text-sm font-bold").style(
                    "color: #222222;"
                )
                ui.label(
                    "All files are required to have a complete wordlist."
                ).classes("text-xs").style("color: #595959;")

                def add_file_loader(
                    key: str,
                    title: str,
                    description: str,
                    accept: str,
                    handler,
                ) -> None:
                    with ui.column().classes("w-full gap-1"):
                        ui.label(title).classes("text-xs font-bold").style(
                            "color: #222222;"
                        )
                        ui.label(description).classes("text-xs leading-relaxed").style(
                            "color: #595959;"
                        )
                        with ui.row().classes(
                            "w-full items-center justify-between gap-2 flex-wrap"
                        ):
                            status_text, loaded = self.settings_file_status[key]
                            status_label = ui.label(status_text).classes(
                                "babble-file-status text-xs"
                            )
                            status_label.style(
                                "background-color: "
                                f"{'#2E7D32' if loaded else '#B71C1C'} !important;"
                            )
                            self.settings_file_labels[key] = status_label
                            upload = ui.upload(
                                label="LOAD",
                                auto_upload=True,
                                max_file_size=100_000_000,
                                on_upload=handler,
                            ).props(f'accept="{accept}" flat bordered').classes(
                                "w-40 babble-file-upload"
                            )
                            self.settings_upload_boxes[key] = upload
                            size_by_key = {
                                "units": GLOBAL_DB.source_size_bytes,
                                "cursed": GLOBAL_DB.extra_source_size_bytes,
                                "blacklist": GLOBAL_DB.blacklist_size_bytes,
                                "user_data": self.user_data_size_bytes,
                            }
                            self._set_settings_file_status(
                                key,
                                size_by_key[key],
                                loaded,
                            )
                    ui.separator().style("background-color: #C4C4C4;")

                add_file_loader(
                    "units",
                    "UNITS JSON",
                    r"The file that contains most of the games words and their stats. This is found inside the game files in Towers of Babble\TowersOfBabble_Data\StreamingAssets.",
                    ".json",
                    self._handle_units_upload,
                )
                add_file_loader(
                    "cursed",
                    "CURSED WORDS JSON",
                    "A file that was made by extracting data from the game containing the stats for Cursed Towers. This file does not exist implicitly inside the game files. (optional)",
                    ".json",
                    self._handle_cursed_upload,
                )
                add_file_loader(
                    "blacklist",
                    "BLACKLIST TXT",
                    r"The file that contains the words the developer has blacklisted and therefore do not exist inside the game. This is found inside the game files in Towers of Babble\TowersOfBabble_Data\StreamingAssets. (optional, but will show invalid words in search result)",
                    ".txt",
                    self._handle_blacklist_upload,
                )
                add_file_loader(
                    "user_data",
                    "USER DATA JSON",
                    "A file for storing your favorite words and custom settings (such as your dictionary link). Should be missing if this is the first time you have opened the program, will be made when you favorite a word or save settings.",
                    ".json",
                    self._handle_user_data_upload,
                )

                with ui.column().classes("w-full gap-1"):
                    ui.label("DICTIONARY LINK").classes(
                        "text-xs font-bold"
                    ).style("color: #222222;")
                    ui.label(
                        "Paste the query link of any dictionary website you want the DEFINITION button to use. "
                        "The searched word is added to the end of the link (or replaces {word} if included). "
                        "Leave blank or click DEFAULT to use OneLook (https://onelook.com/?w=). "
                        "Other examples: https://www.google.com/search?q= or https://en.wiktionary.org/wiki/."
                    ).classes("text-xs leading-relaxed").style(
                        "color: #595959;"
                    )
                    with ui.row().classes(
                        "w-full items-center gap-2 no-wrap"
                    ):
                        self.inp_dictionary_url = (
                            ui.input(
                                value=self.dictionary_url,
                                placeholder=DEFAULT_DICTIONARY_URL,
                            )
                            .props("outlined dense")
                            .classes("flex-grow babble-input")
                        )
                        self.inp_dictionary_url.on(
                            "keydown.enter",
                            lambda _e: self._save_dictionary_url(),
                        )
                        ui.button(
                            "SAVE", on_click=self._save_dictionary_url
                        ).props("unelevated dense").classes(
                            "babble-pill-blue px-4 h-9 text-xs"
                        )
                        ui.button(
                            "DEFAULT", on_click=self._reset_dictionary_url
                        ).props("unelevated dense").classes(
                            "babble-pill px-3 h-9 text-xs"
                        )
                ui.separator().style("background-color: #C4C4C4;")

                with ui.row().classes("w-full justify-end mt-2"):
                    ui.button("CLOSE", on_click=self.settings_dialog.close).props(
                        "unelevated dense"
                    ).classes("babble-pill px-4")

        def _persist_dictionary_url(self, raw_url: str, notify_msg: str) -> None:
            normalized = normalize_dictionary_url(raw_url)
            self.dictionary_url = normalized
            self.user_data["dictionary_url"] = normalized
            if self.inp_dictionary_url is not None:
                self.inp_dictionary_url.value = normalized
            try:
                save_user_data_json(self.user_data_path, self.user_data)
                self.user_data_source = self.user_data_path.name
                self.user_data_size_bytes = self.user_data_path.stat().st_size
                self.user_data_loaded = True
                self._set_settings_file_status(
                    "user_data",
                    self.user_data_size_bytes,
                    self.user_data_loaded,
                )
            except (OSError, TypeError, ValueError) as exc:
                ui.notify(f"Could not save dictionary link: {exc}", type="negative")
            self._render_results()
            ui.notify(notify_msg, type="positive", position="bottom-right", timeout=2200)

        def _save_dictionary_url(self) -> None:
            raw = (
                str(self.inp_dictionary_url.value or "")
                if self.inp_dictionary_url is not None
                else DEFAULT_DICTIONARY_URL
            )
            normalized = normalize_dictionary_url(raw)
            self._persist_dictionary_url(
                normalized, f"Dictionary link saved: {normalized}"
            )

        def _reset_dictionary_url(self) -> None:
            self._persist_dictionary_url(
                DEFAULT_DICTIONARY_URL,
                f"Dictionary link reset to default ({DEFAULT_DICTIONARY_URL})",
            )

        def _refresh_after_file_change(self) -> None:
            self._refresh_dynamic_dropdowns()
            self.applied_query = self._snapshot_form()
            self._update_pending_indicator()
            self.run_applied_search(reset_pagination=True)

        def _update_main_file_status(self) -> None:
            if self.lbl_file_status is None:
                return
            text, loaded = self._file_load_summary()
            self.lbl_file_status.set_text(text)
            self.lbl_file_status.style(
                f"color: {'#2E7D32' if loaded else '#B71C1C'} !important;"
            )

        def _handle_units_upload(self, e) -> None:
            try:
                raw_bytes = e.content.read()
                data = json.loads(raw_bytes.decode("utf-8"))
                validate_units_json(data)
                count = GLOBAL_DB.load_data(
                    data,
                    source_label=e.name,
                    source_size_bytes=len(raw_bytes),
                )
            except (
                OSError,
                UnicodeDecodeError,
                json.JSONDecodeError,
                KeyError,
                TypeError,
                ValueError,
            ) as exc:
                self._set_settings_file_status("units", None, False)
                e.sender.reset()
                ui.notify(f"Could not load units JSON: {exc}", type="negative")
                return

            loaded = bool(GLOBAL_DB._base_records)
            self._set_settings_file_status(
                "units", len(raw_bytes), loaded
            )
            e.sender.reset()
            self._refresh_after_file_change()
            ui.notify(f"Loaded {count:,} units from {e.name}", type="positive")

        def _handle_cursed_upload(self, e) -> None:
            try:
                raw_bytes = e.content.read()
                data = json.loads(raw_bytes.decode("utf-8"))
                validate_units_json(data, require_cursed=True)
                count = GLOBAL_DB.load_extra_data(
                    data,
                    source_label=e.name,
                    source_size_bytes=len(raw_bytes),
                )
            except (
                OSError,
                UnicodeDecodeError,
                json.JSONDecodeError,
                KeyError,
                TypeError,
                ValueError,
            ) as exc:
                self._set_settings_file_status("cursed", None, False)
                e.sender.reset()
                ui.notify(f"Could not load cursed words JSON: {exc}", type="negative")
                return

            loaded = any(record.is_cursed for record in GLOBAL_DB._extra_records)
            self._set_settings_file_status(
                "cursed", len(raw_bytes), loaded
            )
            e.sender.reset()
            self._refresh_after_file_change()
            ui.notify(f"Loaded {count:,} cursed words from {e.name}", type="positive")

        def _handle_blacklist_upload(self, e) -> None:
            try:
                raw_bytes = e.content.read()
                contents = raw_bytes.decode("utf-8")
                count = GLOBAL_DB.load_blacklist_data(
                    contents,
                    source_label=e.name,
                    source_size_bytes=len(raw_bytes),
                )
            except (UnicodeDecodeError, OSError, TypeError, ValueError) as exc:
                self._set_settings_file_status("blacklist", None, False)
                e.sender.reset()
                ui.notify(f"Could not load blacklist: {exc}", type="negative")
                return

            self._set_settings_file_status(
                "blacklist", len(raw_bytes), GLOBAL_DB.blacklist_loaded
            )
            e.sender.reset()
            self._refresh_after_file_change()
            ui.notify(
                f"Loaded blacklist with {len(GLOBAL_DB.blacklisted_words):,} "
                f"entries; {count:,} units remain",
                type="positive",
            )

        def _handle_user_data_upload(self, e) -> None:
            try:
                raw_bytes = e.content.read()
                data = normalize_user_data(
                    json.loads(raw_bytes.decode("utf-8"))
                )
            except (
                OSError,
                UnicodeDecodeError,
                json.JSONDecodeError,
                TypeError,
                ValueError,
            ) as exc:
                self._set_settings_file_status("user_data", None, False)
                e.sender.reset()
                ui.notify(f"Could not load user data JSON: {exc}", type="negative")
                return

            self.user_data = data
            self.favorites = set(data["favorites"])
            self.dictionary_url = data["dictionary_url"]
            if self.inp_dictionary_url is not None:
                self.inp_dictionary_url.value = self.dictionary_url
            self.user_data_source = e.name
            self.user_data_size_bytes = len(raw_bytes)
            self.user_data_loaded = True
            self._set_settings_file_status(
                "user_data", len(raw_bytes), self.user_data_loaded
            )
            e.sender.reset()
            self._refresh_after_file_change()
            ui.notify(
                f"Loaded user data with {len(self.favorites):,} favorites from {e.name}",
                type="positive",
            )

        # ---- Main Page Layout ----
        def _sync_db_file_statuses(self) -> None:
            self._set_settings_file_status(
                "units",
                GLOBAL_DB.source_size_bytes,
                bool(GLOBAL_DB.source_path and GLOBAL_DB._base_records),
            )
            self._set_settings_file_status(
                "cursed",
                GLOBAL_DB.extra_source_size_bytes,
                bool(
                    GLOBAL_DB.extra_source_path
                    and any(
                        record.is_cursed for record in GLOBAL_DB._extra_records
                    )
                ),
            )
            self._set_settings_file_status(
                "blacklist",
                GLOBAL_DB.blacklist_size_bytes,
                GLOBAL_DB.blacklist_loaded,
            )

        def build(self) -> None:
            ui.add_head_html(get_custom_css())
            self._build_settings_dialog()
            assert self.settings_dialog is not None

            with ui.column().classes("w-full babble-shell gap-3"):
                # ---- HEADER ----
                with ui.row().classes("w-full items-center justify-between gap-2"):
                    with ui.column().classes("gap-0.5"):
                        with ui.row().classes("items-baseline gap-2"):
                            ui.label("TOWERS OF BABBLE").classes(
                                "text-2xl font-bold tracking-tight"
                            ).style("color: #FF5604;")
                            ui.label("WORD FINDER").classes(
                                "text-xl font-bold tracking-tight"
                            ).style("color: #595959;")
                        ui.label(
                            "Enter available letters, then click FIND WORDS! Made by Levi. Version 2."
                        ).classes("text-xs").style("color: #595959;")

                    with ui.column().classes("items-end gap-1"):
                        ui.button(
                            icon="settings",
                            on_click=self.settings_dialog.open,
                        ).props("flat round dense").style(
                            "width: 36px; height: 36px; color: #595959;"
                        ).tooltip("Options and data files")
                        status_txt, files_loaded = self._file_load_summary()
                        self.lbl_file_status = ui.label(status_txt).classes(
                            "text-xs text-right"
                        ).style(
                            f"color: {'#2E7D32' if files_loaded else '#B71C1C'};"
                        )

                ui.separator().style("background-color: #B7B7B7; height: 2px;")

                # ---- CONTROLS PANEL ----
                with ui.column().classes("w-full babble-panel gap-3"):
                    # Row 1: Available Letters + Find Words + Reset
                    with ui.column().classes("w-full gap-1"):
                        with ui.row().classes("w-full items-center gap-2 flex-wrap"):
                            ui.label("AVAILABLE LETTERS").classes("babble-field-lbl")
                            self.lbl_fav_count = ui.label("").classes(
                                "text-xs font-bold"
                            ).style("color: #D93829;")
                            self.lbl_fav_count.set_visibility(False)
                            self.lbl_curse_count = ui.label("").classes(
                                "text-xs font-bold"
                            ).style("color: #6E13BE;")
                            self.lbl_curse_count.set_visibility(False)
                            self.lbl_letter_count = ui.label(
                                "0 letters (browsing all)"
                            ).classes("text-xs ml-auto").style("color: #666666;")

                        with ui.row().classes("w-full items-center gap-2 no-wrap"):
                            self.inp_letters = (
                                ui.input(
                                    placeholder="e.g. ABCDEFGHIJKLMNOPQRSTUVWXYZ  (? for wildcard)",
                                    on_change=self.on_letters_change,
                                )
                                .props("outlined dense")
                                .classes("flex-grow babble-input babble-uppercase")
                            )
                            self.inp_letters.on(
                                "keydown.enter", lambda _e: self.on_find_words()
                            )

                            ui.button(
                                "FIND WORDS", on_click=self.on_find_words
                            ).props("unelevated").classes("babble-pill-blue px-5 h-10")

                            ui.button("RESET", on_click=self.on_reset).props(
                                "unelevated"
                            ).classes("babble-pill babble-pill-blue-border px-4 h-10")

                    # Row 2: Category, sort, and order controls.
                    with ui.row().classes(
                        "w-full items-center justify-between gap-2 flex-wrap"
                    ):
                        with ui.row().classes("items-center gap-2 flex-wrap"):
                            with ui.column().classes("gap-1"):
                                ui.label("SHOW").classes("babble-field-lbl")
                                with ui.row().classes("items-center gap-1"):
                                    for kind, label in (
                                        ("TOWER", "TOWERS"),
                                        ("HARVESTER", "HARVESTERS"),
                                        ("MOD", "MODS"),
                                    ):
                                        self.kind_buttons[kind] = (
                                            ui.button(
                                                label,
                                                on_click=lambda _e, selected_kind=kind: self.on_toggle_kind(
                                                    selected_kind
                                                ),
                                            )
                                            .props("unelevated dense no-caps")
                                            .classes("babble-pill px-3 h-9 text-xs")
                                        )
                            self._sync_kind_filter_controls()

                            with ui.column().classes("gap-1"):
                                ui.label("SORT BY").classes("babble-field-lbl")
                                self.btn_sort_mode = (
                                    ui.button(
                                        "VALUE", on_click=self.on_toggle_sort_mode
                                    )
                                    .props("unelevated dense no-caps")
                                    .classes("babble-pill px-3 h-9 text-xs")
                                )
                            self._sync_sort_mode_button()

                            with ui.column().classes("gap-1"):
                                ui.label("ORDER").classes("babble-field-lbl")
                                self.sel_order = (
                                    ui.select(
                                        options=["Descending", "Ascending"],
                                        value="Descending",
                                        on_change=self.on_order_change,
                                    )
                                    .props("outlined dense options-dense")
                                    .classes("babble-input w-40")
                                )

                    # Row 3: Result toggles.
                    with ui.row().classes(
                        "w-full items-center justify-between gap-2 flex-wrap"
                    ):
                        with ui.row().classes("items-center gap-2 flex-wrap"):
                            self.btn_group = (
                                ui.button(
                                    "GROUP BY LENGTH", on_click=self.on_toggle_group
                                )
                                .props("unelevated dense")
                                .classes("babble-pill px-3 h-9 text-xs")
                            )
                            self.btn_collapse_groups = (
                                ui.button(
                                    "COLLAPSE GROUPS",
                                    on_click=self.on_toggle_all_groups,
                                )
                                .props("unelevated dense no-caps")
                                .classes("babble-pill px-3 h-9 text-xs")
                            )
                            self.btn_collapse_groups.tooltip(
                                "Collapse or expand all grouped results"
                            )
                            self.btn_collapse_groups.set_visibility(False)
                            self._sync_pill_style(
                                self.btn_collapse_groups, False
                            )

                            self.btn_two_letter_words = (
                                ui.button(
                                    "2-LETTER WORDS",
                                    on_click=self.on_toggle_two_letter_words,
                                )
                                .props("unelevated dense no-caps")
                                .classes("babble-pill px-3 h-9 text-xs")
                            )
                            self.btn_two_letter_words.tooltip(
                                "Toggle whether 2-letter words appear in results"
                            )
                            self.btn_clever_mode = (
                                ui.button(
                                    "CLEVER MODE",
                                    on_click=self.on_toggle_clever_mode,
                                )
                                .props("unelevated dense no-caps")
                                .classes("babble-pill px-3 h-9 text-xs")
                            )
                            self.btn_clever_mode.tooltip(
                                "Show word combinations that use every available letter exactly."
                            )
                            self._sync_pill_style(self.btn_group, False)
                            self._sync_pill_style(
                                self.btn_two_letter_words,
                                self.show_two_letter_words,
                            )
                            self._sync_clever_mode_button()

                        self.btn_favorites = (
                            ui.button(
                                "♥ FAVORITES", on_click=self.on_toggle_favorites_only
                            )
                            .props("unelevated dense")
                            .classes("babble-pill px-4 h-9 text-xs")
                        )
                        self._sync_favorite_style(False)

                    ui.separator().style("background-color: #C8C8C8;")

                    # Row 4: CONTAINS + In Order + Exact Amount (deferred until Find Words)
                    with ui.column().classes("w-full gap-1"):
                        ui.label("CONTAINS").classes("babble-field-lbl")
                        with ui.row().classes("w-full items-center gap-2 no-wrap"):
                            self.inp_contains = (
                                ui.input(
                                    placeholder="Letters that must appear in the word…",
                                    on_change=self.on_contains_change,
                                )
                                .props("outlined dense")
                                .classes("flex-grow babble-input babble-uppercase")
                            )
                            self.inp_contains.on(
                                "keydown.enter", lambda _e: self.on_find_words()
                            )

                            self.btn_in_order = (
                                ui.button(
                                    "IN ORDER", on_click=self.on_toggle_in_order
                                )
                                .props("unelevated dense")
                                .classes("babble-pill px-3 h-9 text-xs")
                            )
                            self.btn_exact = (
                                ui.button(
                                    "EXACT AMOUNT",
                                    on_click=self.on_toggle_exact_amount,
                                )
                                .props("unelevated dense")
                                .classes("babble-pill px-3 h-9 text-xs")
                            )

                            self._sync_pill_style(self.btn_in_order, False)
                            self._sync_pill_style(self.btn_exact, False)

                    # Row 4: STARTS / ENDS / LENGTH / EFFECT & RESOURCE (deferred until Find Words)
                    with ui.element("div").classes(
                        "w-full grid grid-cols-1 sm:grid-cols-4 gap-2"
                    ):
                        with ui.column().classes("gap-1"):
                            ui.label("STARTS").classes("babble-field-lbl")
                            self.inp_starts = (
                                ui.input(
                                    placeholder="Prefix…",
                                    on_change=self.on_starts_change,
                                )
                                .props("outlined dense")
                                .classes("w-full babble-input babble-uppercase")
                            )
                            self.inp_starts.on(
                                "keydown.enter", lambda _e: self.on_find_words()
                            )

                        with ui.column().classes("gap-1"):
                            ui.label("ENDS").classes("babble-field-lbl")
                            self.inp_ends = (
                                ui.input(
                                    placeholder="Suffix…",
                                    on_change=self.on_ends_change,
                                )
                                .props("outlined dense")
                                .classes("w-full babble-input babble-uppercase")
                            )
                            self.inp_ends.on(
                                "keydown.enter", lambda _e: self.on_find_words()
                            )

                        with ui.column().classes("gap-1"):
                            ui.label("LENGTH").classes("babble-field-lbl")
                            self.sel_length = (
                                ui.select(
                                    options=self._get_length_options(),
                                    value="ALL",
                                    on_change=self.on_length_change,
                                )
                                .props("outlined dense options-dense")
                                .classes("w-full babble-input")
                            )

                        with ui.column().classes("gap-1"):
                            ui.label("EFFECT / RESOURCE").classes("babble-field-lbl")
                            self.sel_effect = (
                                ui.select(
                                    options=GLOBAL_DB.get_ordered_effect_options(),
                                    value="",
                                    on_change=self.on_effect_change,
                                )
                                .props("outlined dense options-dense")
                                .classes("w-full babble-input")
                            )

                    # Pending-changes hint banner (hidden unless unapplied filter edits exist)
                    self.lbl_pending = ui.label("").classes(
                        "text-xs font-bold"
                    ).style("color: #FF5604;")
                    self.lbl_pending.set_visibility(False)

                # ---- RESULTS PANEL ----
                with ui.column().classes("w-full babble-panel gap-2"):
                    # Results title/count row followed by stat filter buttons.
                    with ui.row().classes(
                        "w-full items-center justify-between gap-2 pb-1"
                    ):
                        ui.label("RESULTS").classes("babble-field-lbl")
                        self.lbl_result_count = ui.label("0 words found").classes(
                            "ml-auto text-xs font-bold whitespace-nowrap"
                        ).style("color: #595959;")

                    self.stat_filter_container = ui.row().classes(
                        "w-full items-center gap-1 flex-wrap"
                    )
                    self._build_stat_filter_controls()

                    ui.separator().style("background-color: #C8C8C8;")

                    self.results_container = ui.column().classes("w-full gap-1.5")

            def _cleanup_tasks() -> None:
                self._cancel_pending_stat_filter_search()
                self._cancel_pending_clever_search()

            ui.context.client.on_delete(_cleanup_tasks)

            # Perform initial render immediately if loaded, otherwise wait asynchronously.
            if not _DB_AUTOLOAD_STARTED or DB_LOAD_EVENT.is_set():
                self.run_applied_search(reset_pagination=True)
            else:
                if self.lbl_result_count is not None:
                    self.lbl_result_count.set_text("Loading word database...")
                with self.results_container:
                    with ui.row().classes(
                        "w-full items-center justify-center gap-2 py-10"
                    ):
                        ui.spinner(size="sm", color="#FF5604")
                        ui.label("Loading word database...").classes(
                            "text-sm font-bold"
                        ).style("color: #595959;")

                async def _finish_initial_load() -> None:
                    await asyncio.to_thread(DB_LOAD_EVENT.wait)
                    if (
                        self.results_container is None
                        or self.results_container.is_deleted
                        or self.results_container.client.is_deleted
                    ):
                        return
                    self._sync_db_file_statuses()
                    self._refresh_dynamic_dropdowns()
                    self.run_applied_search(reset_pagination=True)

                background_tasks.create(
                    _finish_initial_load(), name="babble-finish-initial-load"
                )

    @ui.page("/")
    def index_page():
        session = FinderSession()
        session.build()

    return ui


_TITLEBAR_BG_HEX = "#DDDDDD"
_TITLEBAR_TEXT_HEX = "#111111"
_TITLEBAR_SUBCLASS_REFS: List[Any] = []


def _hex_to_colorref(hex_color: str) -> int:
    """Convert #RRGGBB to Win32 COLORREF (0x00BBGGRR)."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (b << 16) | (g << 8) | r


def _init_native_titlebar() -> None:
    """Run inside the pywebview subprocess to lock the Win11 title bar color synchronously."""
    if sys.platform != "win32":
        return

    import ctypes
    from ctypes import wintypes
    import time
    import webview

    # Wait briefly for pywebview's WinForms window handle to be created
    deadline = time.monotonic() + 15.0
    form = None
    while time.monotonic() < deadline:
        if webview.windows:
            win = webview.windows[0]
            candidate = getattr(win, "native", None)
            if candidate is None:
                try:
                    from webview.platforms.winforms import BrowserView
                    candidate = BrowserView.instances.get(win.uid)
                except Exception:
                    candidate = None
            if candidate is not None and getattr(candidate, "IsHandleCreated", False):
                form = candidate
                break
        time.sleep(0.02)

    if form is None:
        return

    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    DWMWA_CAPTION_COLOR = 35
    DWMWA_TEXT_COLOR = 36

    WM_ACTIVATE = 0x0006
    WM_SETTINGCHANGE = 0x001A
    WM_NCDESTROY = 0x0082
    WM_NCACTIVATE = 0x0086
    WM_THEMECHANGED = 0x031A

    SWP_NOSIZE = 0x0001
    SWP_NOMOVE = 0x0002
    SWP_NOZORDER = 0x0004
    SWP_NOACTIVATE = 0x0010
    SWP_FRAMECHANGED = 0x0020
    SUBCLASS_ID = 1

    LRESULT = ctypes.c_ssize_t
    UINT_PTR = ctypes.c_size_t
    DWORD_PTR = ctypes.c_size_t

    SUBCLASSPROC = ctypes.WINFUNCTYPE(
        LRESULT,
        wintypes.HWND,
        wintypes.UINT,
        wintypes.WPARAM,
        wintypes.LPARAM,
        UINT_PTR,
        DWORD_PTR,
    )

    dwmapi = ctypes.WinDLL("dwmapi", use_last_error=True)
    comctl32 = ctypes.WinDLL("comctl32", use_last_error=True)
    user32 = ctypes.WinDLL("user32", use_last_error=True)

    dwmapi.DwmSetWindowAttribute.argtypes = [
        wintypes.HWND,
        wintypes.DWORD,
        ctypes.c_void_p,
        wintypes.DWORD,
    ]
    dwmapi.DwmSetWindowAttribute.restype = ctypes.c_long

    comctl32.SetWindowSubclass.argtypes = [
        wintypes.HWND,
        SUBCLASSPROC,
        UINT_PTR,
        DWORD_PTR,
    ]
    comctl32.SetWindowSubclass.restype = wintypes.BOOL

    comctl32.DefSubclassProc.argtypes = [
        wintypes.HWND,
        wintypes.UINT,
        wintypes.WPARAM,
        wintypes.LPARAM,
    ]
    comctl32.DefSubclassProc.restype = LRESULT

    comctl32.RemoveWindowSubclass.argtypes = [
        wintypes.HWND,
        SUBCLASSPROC,
        UINT_PTR,
    ]
    comctl32.RemoveWindowSubclass.restype = wintypes.BOOL

    user32.SetWindowPos.argtypes = [
        wintypes.HWND,
        wintypes.HWND,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        wintypes.UINT,
    ]
    user32.SetWindowPos.restype = wintypes.BOOL

    bg_colorref = _hex_to_colorref(_TITLEBAR_BG_HEX)
    text_colorref = _hex_to_colorref(_TITLEBAR_TEXT_HEX)
    sync_messages = (WM_NCACTIVATE, WM_ACTIVATE, WM_THEMECHANGED, WM_SETTINGCHANGE)

    def apply_dwm(hwnd: int) -> None:
        use_dark = ctypes.c_int(0)
        dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(use_dark),
            ctypes.sizeof(use_dark),
        )
        caption_color = wintypes.DWORD(bg_colorref)
        dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_CAPTION_COLOR,
            ctypes.byref(caption_color),
            ctypes.sizeof(caption_color),
        )
        text_color = wintypes.DWORD(text_colorref)
        dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_TEXT_COLOR,
            ctypes.byref(text_color),
            ctypes.sizeof(text_color),
        )

    @SUBCLASSPROC
    def subclass_proc(hwnd, msg, wparam, lparam, uid, ref_data):
        if msg in sync_messages:
            apply_dwm(hwnd)
            res = comctl32.DefSubclassProc(hwnd, msg, wparam, lparam)
            apply_dwm(hwnd)
            return res
        if msg == WM_NCDESTROY:
            comctl32.RemoveWindowSubclass(hwnd, subclass_proc, uid)
            res = comctl32.DefSubclassProc(hwnd, msg, wparam, lparam)
            if subclass_proc in _TITLEBAR_SUBCLASS_REFS:
                _TITLEBAR_SUBCLASS_REFS.remove(subclass_proc)
            return res
        return comctl32.DefSubclassProc(hwnd, msg, wparam, lparam)

    def attach_subclass() -> None:
        hwnd = int(form.Handle.ToInt64())
        _TITLEBAR_SUBCLASS_REFS.append(subclass_proc)
        if not comctl32.SetWindowSubclass(hwnd, subclass_proc, SUBCLASS_ID, 0):
            _TITLEBAR_SUBCLASS_REFS.remove(subclass_proc)
        apply_dwm(hwnd)
        # Force a single initial frame repaint at startup only
        user32.SetWindowPos(
            hwnd,
            None,
            0,
            0,
            0,
            0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE | SWP_FRAMECHANGED,
        )

    if getattr(form, "InvokeRequired", False):
        from System import Action
        form.Invoke(Action(attach_subclass))
    else:
        attach_subclass()


def _is_address_available(host: str, port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            sock.bind((host, port))
            return True
    except OSError:
        return False


def find_available_server_address(
    preferred_hosts: Tuple[str, ...] = ("127.0.0.1", "127.0.0.2", "127.0.0.3"),
    start_port: int = 8080,
    end_port: int = 8999,
) -> Tuple[str, int]:
    """Return an unused local (host, port) pair so multiple windows can run simultaneously."""
    for host in preferred_hosts:
        for port in range(start_port, end_port + 1):
            if _is_address_available(host, port):
                return host, port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((preferred_hosts[0], 0))
        return preferred_hosts[0], int(sock.getsockname()[1])


def main():
    from nicegui import app

    ui = build_nicegui_app()
    app.on_startup(start_autoload_in_background)
    app.native.window_args["min_size"] = (980, 860)
    app.native.window_args["background_color"] = _TITLEBAR_BG_HEX
    app.native.start_args["func"] = _init_native_titlebar

    host, port = find_available_server_address()
    ui.run(
        title="Towers of Babble — Word Finder",
        host=host,
        port=port,
        reload=False,
        native=True,
        window_size=(980, 860),
        show_welcome_message=False,
    )


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()