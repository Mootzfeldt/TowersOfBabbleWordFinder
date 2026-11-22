# A Word Finding program made especially for the game Towers of Babble made by Everybody House Games.
# units.json was taken directly from the game files, while cursed_words.json was decompiled by AI.
# Mostly written by AI, I (Levi) simply fixed formatting, functionality and other small things.

import json
import os
import sys
import base64
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import quote_plus


# Theme, Naming & Canonical Stat Ordering
KIND_META = {
    "TOWER": {
        "display": "tower",
        "color": "#FF5604",       # Orange
        "soft_bg": "#FFE7DA",
    },
    "MOD": {
        "display": "mod",
        "color": "#e858a8",       # Pink
        "soft_bg": "#F8DDF0",
    },
    "HARVESTER": {
        "display": "harvester",
        "color": "#1E7D32",       # Green
        "soft_bg": "#DCF0DF",
    },
    "CURSED": {
        "display": "cursed",
        "color": "#6e13be",       # Purple
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

# Short badge labels shown when sorting by a stat
STAT_SHORT_LABELS: Dict[str, str] = {
    "curse": "CURSE",
    "damage": "DMG",
    "dps": "DPS",
    "dmg_buff_aura": "DMG AURA",
    "attack_speed": "ATK SPD",
    "firerate_buff_aura": "SPD AURA",
    "toughness": "HP",
    "heal_aura": "HEAL",
    "armor": "ARM",
    "armor_buff_aura": "ARM AURA",
    "crit": "CRIT",
    "range": "RNG",
    "burn": "BURN",
    "burn_aura": "BURN",
    "poison": "PSN",
    "slow": "SLOW",
    "slow_aura": "SLOW AURA",
    "knockback": "KB",
    "stun": "STUN",
    "multishot": "MULTI",
    "pierce": "PRC",
    "armor_shred": "SHRED",
    "splash": "SPLASH",
    "chain": "CHAIN",
    "harvest_amount": "AMT",
    "harvest_speed": "H-SPD",
    "harvest_rate": "RATE",
    "harvest_types": "TYPES",
    "multi_harvest": "M-HARV",
    "harvest_aura": "H-AURA",
}

# Sort-by options per category (Points & Alphabetical on top, then canonical stat order)
SORT_KEYS_BY_KIND: Dict[str, List[str]] = {
    "ALL": [
        "points",
        "alphabetical",
        "damage",
        "dps",
        "dmg_buff_aura",
        "attack_speed",
        "firerate_buff_aura",
        "toughness",
        "heal_aura",
        "armor",
        "armor_buff_aura",
        "crit",
        "range",
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
        "harvest_amount",
        "harvest_speed",
        "harvest_rate",
        "multi_harvest",
        "harvest_aura",
    ],
    "TOWER": [
        "points",
        "alphabetical",
        "damage",
        "dps",
        "dmg_buff_aura",
        "attack_speed",
        "firerate_buff_aura",
        "toughness",
        "heal_aura",
        "armor",
        "armor_buff_aura",
        "crit",
        "range",
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
    ],
    "CURSED": [
        "points",
        "alphabetical",
        "damage",
        "dps",
        "dmg_buff_aura",
        "attack_speed",
        "firerate_buff_aura",
        "toughness",
        "heal_aura",
        "armor",
        "armor_buff_aura",
        "crit",
        "range",
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
    ],
    "HARVESTER": [
        "points",
        "alphabetical",
        "toughness",
        "armor",
        "range",
        "harvest_amount",
        "harvest_speed",
        "harvest_rate",
        "harvest_types",
        "multi_harvest",
        "harvest_aura",
    ],
    "MOD": [
        "points",
        "alphabetical",
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
        "burn_aura",
        "poison",
        "slow",
        "slow_aura",
        "knockback",
        "stun",
        "multishot",
        "pierce",
        "armor_shred",
        "splash",
        "chain",
        "harvest_amount",
        "harvest_speed",
        "multi_harvest",
        "harvest_aura",
    ],
}

SORT_LABELS: Dict[str, str] = {
    "points": "Points",
    "alphabetical": "Alphabetical",
    **DISPLAY_NAMES,
}


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


# Favorites Persistence (favorites.txt, one word per line)
def resolve_favorites_path() -> Path:
    if getattr(sys, "frozen", False):
        app_dir = Path(sys.executable).resolve().parent
    else:
        app_dir = Path(__file__).resolve().parent

    candidate = app_dir / "favorites.txt"
    if os.access(str(app_dir), os.W_OK):
        return candidate
    return Path.home() / "favorites.txt"


def load_favorites_txt(path: Path) -> Set[str]:
    if not path.is_file():
        return set()
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        return {line.strip().lower() for line in lines if line.strip()}
    except Exception:
        return set()


def save_favorites_txt(path: Path, favorites: Set[str]) -> None:
    try:
        ordered = sorted(w.strip().lower() for w in favorites if w.strip())
        content = ("\n".join(ordered) + "\n") if ordered else ""
        path.write_text(content, encoding="utf-8")
    except Exception:
        pass

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
    )

    def __init__(self, u: Dict[str, Any]):
        w = str(u.get("word", "")).strip().lower()
        self.word = w
        self.word_upper = w.upper()
        self.length = len(w)

        mask = 0
        for ch in w:
            o = ord(ch) - 97
            if 0 <= o < 26:
                mask |= 1 << o
        self.mask = mask

        self.raw_kind: str = str(u.get("kind", "TOWER"))
        self.kind: str = normalize_kind(self.raw_kind)
        self.scrabble: int = int(u.get("scrabble", 0))

        # Tower stats
        self.damage: Optional[float] = float(u["damage"]) if "damage" in u else None
        self.range: Optional[float] = float(u["range"]) if "range" in u else None
        self.attack_interval: Optional[float] = (
            float(u["attackInterval"]) if "attackInterval" in u else None
        )
        if self.attack_interval and self.attack_interval > 0:
            self.attack_speed: Optional[float] = 1.0 / self.attack_interval
            self.dps: Optional[float] = (
                self.damage / self.attack_interval if self.damage is not None else None
            )
        else:
            self.attack_speed = None
            self.dps = None

        self.health: Optional[float] = float(u["health"]) if "health" in u else None
        self.armor: Optional[float] = (
            float(u["armor"]) if "armor" in u else (0.0 if self.kind == "TOWER" else None)
        )
        self.targeting: str = str(u.get("targeting", ""))
        self.is_cursed: bool = bool(u.get("isCursed", False))
        self.curse_effects: Tuple[str, ...] = tuple(
            str(effect) for effect in u.get("curseEffects", [])
        )

        # Harvester stats
        self.harvest_amount: Optional[float] = (
            float(u["harvestAmount"]) if "harvestAmount" in u else None
        )
        self.harvest_interval: Optional[float] = (
            float(u["harvestInterval"]) if "harvestInterval" in u else None
        )
        if self.harvest_interval and self.harvest_interval > 0:
            self.harvest_speed: Optional[float] = 1.0 / self.harvest_interval
            self.harvest_rate: Optional[float] = (
                self.harvest_amount / self.harvest_interval
                if self.harvest_amount is not None
                else None
            )
        else:
            self.harvest_speed = None
            self.harvest_rate = None

        self.harvest_types: Optional[int] = (
            int(u["harvestTypes"]) if "harvestTypes" in u else None
        )
        self.harvest_range: Optional[float] = (
            float(u["harvestRange"]) if "harvestRange" in u else None
        )
        self.harvest_resources: Tuple[str, ...] = tuple(u.get("harvestResources", []))

        # Specials & Deltas
        self.specials: Tuple[Tuple[str, float], ...] = tuple(
            (str(s.get("name", "")), float(s.get("value", 0.0)))
            for s in u.get("specials", [])
        )
        self.deltas: Tuple[Tuple[str, str, float], ...] = tuple(
            (str(d.get("stat", "")), str(d.get("op", "")), float(d.get("value", 0.0)))
            for d in u.get("deltas", [])
        )

        # Searchable effect / boosted-stat / resource tags
        tags: Set[str] = set()
        for name, _ in self.specials:
            tags.add(name)
        for stat, _, _ in self.deltas:
            tags.add(stat)
        for res in self.harvest_resources:
            tags.add(f"res:{res}")
        if self.is_cursed:
            tags.add("curse")
            tags.update(self.curse_effects)

        # Also tag towers/harvesters with boosted base stats so filtering works intuitively
        if self.kind == "TOWER":
            if self.damage is not None and self.damage > TOWER_DEFAULTS["damage"] + 0.01:
                tags.add("damage")
            if self.attack_interval is not None and self.attack_interval < TOWER_DEFAULTS["attackInterval"] - 0.01:
                tags.add("attack_speed")
            if self.health is not None and self.health > TOWER_DEFAULTS["health"] + 0.1:
                tags.add("toughness")
            if self.armor is not None and self.armor > TOWER_DEFAULTS["armor"] + 0.01:
                tags.add("armor")
            if self.range is not None and self.range > TOWER_DEFAULTS["range"] + 0.01:
                tags.add("range")
        elif self.kind == "HARVESTER":
            if self.health is not None and self.health > HARVESTER_DEFAULTS["health"] + 0.1:
                tags.add("toughness")
            if self.armor is not None and self.armor > 0.01:
                tags.add("armor")
            if self.harvest_range is not None and self.harvest_range > HARVESTER_DEFAULTS["harvestRange"] + 0.01:
                tags.add("range")
            if self.harvest_amount is not None and self.harvest_amount > HARVESTER_DEFAULTS["harvestAmount"] + 0.01:
                tags.add("harvest_amount")
            if self.harvest_interval is not None and self.harvest_interval < HARVESTER_DEFAULTS["harvestInterval"] - 0.01:
                tags.add("harvest_speed")

        self.effect_tags = frozenset(tags)
        self._preview_stats: Optional[List[Tuple[str, str, str]]] = None

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
            tone = "pos" if val > 5.01 else ("neg" if val < 4.99 else "neutral")
            return (fmt_num(val, 1), "DPS", tone)
        if stat_key == "attack_speed":
            if self.kind == "TOWER":
                tone = "pos" if val > 1.01 else ("neg" if val < 0.99 else "neutral")
                return (f"{fmt_num(val, 2)}/s", "Attack Speed", tone)
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
            if self.attack_interval is not None and self.attack_interval < TOWER_DEFAULTS["attackInterval"] - 0.01:
                items.append((f"{fmt_num(self.attack_speed, 2)}/s", "Attack Speed", "pos"))
            if self.range is not None and self.range > TOWER_DEFAULTS["range"] + 0.01:
                items.append((fmt_num(self.range, 1), "Range", "pos"))
            if self.health is not None and self.health > TOWER_DEFAULTS["health"] + 0.1:
                items.append((fmt_num(self.health, 0), "HP", "pos"))
            if self.armor is not None and self.armor > TOWER_DEFAULTS["armor"] + 0.01:
                items.append((fmt_num(self.armor, 1), "Armor", "pos"))

            # 3. Drawbacks
            if self.damage is not None and self.damage < TOWER_DEFAULTS["damage"] - 0.01:
                items.append((fmt_num(self.damage, 1), "Damage", "neg"))
            if self.attack_interval is not None and self.attack_interval > TOWER_DEFAULTS["attackInterval"] + 0.01:
                items.append((f"{fmt_num(self.attack_speed, 2)}/s", "Attack Speed", "neg"))
            if self.range is not None and self.range < TOWER_DEFAULTS["range"] - 0.01:
                items.append((fmt_num(self.range, 1), "Range", "neg"))
            if self.health is not None and self.health < TOWER_DEFAULTS["health"] - 0.1:
                items.append((fmt_num(self.health, 0), "HP", "neg"))
            if self.armor is not None and self.armor < TOWER_DEFAULTS["armor"] - 0.01:
                items.append(("0", "Armor", "neg"))

            # 4. Fill up to 3 with core defaults
            existing = {x[1] for x in items}
            if len(items) < 3 and "Damage" not in existing and self.damage is not None:
                items.append((fmt_num(self.damage, 1), "Damage", "neutral"))
            if len(items) < 3 and "Range" not in existing and self.range is not None:
                items.append((fmt_num(self.range, 1), "Range", "neutral"))
            if len(items) < 3 and "HP" not in existing and self.health is not None:
                items.append((fmt_num(self.health, 0), "HP", "neutral"))

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
                tone = "pos" if boosted else ("neg" if reduced else "neutral")
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
            if len(items) < 3 and self.harvest_range is not None:
                items.append((fmt_num(self.harvest_range, 1), "Range", "neutral"))

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


class UnitDatabase:
    """Loads, indexes, filters, and sorts Towers of Babble units."""

    def __init__(self):
        self.units: List[UnitRecord] = []
        self.available_tags: Set[str] = set()
        self.max_len: int = 15
        self.source_path: str = ""

    def load_data(self, data: Any, source_label: str = "") -> int:
        raw_units = data.get("units", []) if isinstance(data, dict) else data
        records: List[UnitRecord] = []
        tags: Set[str] = set()
        max_l = 2

        for u in raw_units:
            if not isinstance(u, dict) or "word" not in u:
                continue
            rec = UnitRecord(u)
            if not rec.word:
                continue
            records.append(rec)
            if rec.length > max_l:
                max_l = rec.length
            tags.update(rec.effect_tags)

        self.units = records
        self.available_tags = tags
        self.max_len = max_l
        self.source_path = source_label
        return len(records)

    def load_file(self, filepath: str) -> int:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return self.load_data(data, source_label=filepath)

    def load_extra_file(self, filepath: str) -> int:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        raw_units = data.get("units", []) if isinstance(data, dict) else data
        existing_words = {record.word for record in self.units}
        added = 0
        for u in raw_units:
            if not isinstance(u, dict) or "word" not in u:
                continue
            rec = UnitRecord(u)
            if rec.word and rec.word not in existing_words:
                self.units.append(rec)
                existing_words.add(rec.word)
                added += 1
                self.available_tags.update(rec.effect_tags)
                self.max_len = max(self.max_len, rec.length)
        return added

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
        effect_filter: str = "",
        favorites_only: bool = False,
        favorites: Optional[Set[str]] = None,
        sort_by: str = "points",
        descending: bool = True,
        group_by_length: bool = True,
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
            if favorites_only and rec.word not in fav_set:
                continue

            if kind_filter != "ALL":
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

        def stat_sort_key(r: UnitRecord):
            v = r.get_stat_value(sort_by)
            missing = 1 if v is None else 0
            num = 0.0 if v is None else (val_sign * v)
            if group_by_length:
                return (len_sign * r.length, missing, num, -r.scrabble, r.word)
            return (missing, num, -r.scrabble, r.word)

        results.sort(key=stat_sort_key)


# ---------------------------------------------------------------------------
# Shared Database Loader
# ---------------------------------------------------------------------------
GLOBAL_DB = UnitDatabase()


def autoload_database() -> Optional[str]:
    if getattr(sys, "frozen", False):
        app_dir = Path(sys.executable).resolve().parent
    else:
        app_dir = Path(__file__).resolve().parent
    cwd = Path.cwd()
    candidates = [
        app_dir / "units.json",
        app_dir / "units_2.json",
        cwd / "units.json",
        cwd / "units_2.json",
    ]
    for path in candidates:
        if path.is_file():
            GLOBAL_DB.load_file(str(path))
            loaded_paths = [str(path)]
            for curse_name in ("cursed_words.json",):
                curse_path = path.with_name(curse_name)
                if curse_path.is_file():
                    GLOBAL_DB.load_extra_file(str(curse_path))
                    loaded_paths.append(str(curse_path))
            return " + ".join(loaded_paths)
    return None


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


CUSTOM_CSS = """
<style>
""" + build_font_css() + """
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
    background: #E4E4E4;
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
  .babble-uppercase input {
    text-transform: uppercase !important;
    font-weight: 700 !important;
    letter-spacing: 0.06em;
  }
  .babble-group-bar {
    background: #D4D4D4;
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
    background: #E2E2E2;
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
    background: #E0E0E0 !important;
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
  .babble-pts-tile {
    background: #E8DDAB;
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
  .babble-stat-chip {
    background: #DCDCDC;
    border: 1px solid #9A9A9A;
    border-radius: 4px;
    padding: 1px 7px;
    font-size: 11px;
    font-weight: 700;
    color: #111111;
    line-height: 1.35;
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


def build_nicegui_app():
    from nicegui import ui

    PAGE_SIZE = 200

    class FinderSession:
        def __init__(self):
            self.favorites_path = resolve_favorites_path()
            self.favorites: Set[str] = load_favorites_txt(self.favorites_path)

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
            self.kind_filter: str = "ALL"
            self.sort_by: str = "points"
            self.descending: bool = True
            self.group_by_length: bool = True
            self.favorites_only: bool = False

            # Current search results & pagination
            self.current_matches: List[UnitRecord] = []
            self.visible_limit: int = PAGE_SIZE
            self.collapsed_lengths: Set[int] = set()
            self._suppress_events: bool = False

            # UI widget references populated in build()
            self.inp_letters = None
            self.inp_contains = None
            self.inp_starts = None
            self.inp_ends = None
            self.sel_length = None
            self.sel_effect = None
            self.sel_category = None
            self.sel_sort = None
            self.sel_order = None
            self.btn_group = None
            self.btn_favorites = None
            self.btn_in_order = None
            self.btn_exact = None
            self.lbl_letter_count = None
            self.lbl_file_status = None
            self.lbl_pending = None
            self.lbl_fav_count = None
            self.lbl_result_count = None
            self.results_container = None
            self.load_dialog = None

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
            entered_letters = sum(
                1
                for ch in self.form_letters
                if ("a" <= ch.lower() <= "z") or ch in ("?", "*")
            )
            if entered_letters == 0:
                self.lbl_fav_count.set_text("")
                self.lbl_fav_count.set_visibility(False)
                return

            fav_in_list = sum(1 for r in self.current_matches if r.word in self.favorites)
            if fav_in_list > 0:
                noun = "favorite" if fav_in_list == 1 else "favorites"
                self.lbl_fav_count.set_text(f"♥ {fav_in_list:,} {noun} found")
                self.lbl_fav_count.set_visibility(True)
            else:
                self.lbl_fav_count.set_text("")
                self.lbl_fav_count.set_visibility(False)

        def _get_sort_options(self) -> Dict[str, str]:
            keys = SORT_KEYS_BY_KIND.get(self.kind_filter, SORT_KEYS_BY_KIND["ALL"])
            return {k: SORT_LABELS.get(k, pretty_name(k)) for k in keys}

        def _get_length_options(self) -> Dict[str, str]:
            # Reordered: All lengths, 15, 14, 13, ... down to 2
            max_l = max(GLOBAL_DB.max_len, 15)
            opts: Dict[str, str] = {"ALL": "All lengths"}
            for n in range(max_l, 1, -1):
                opts[str(n)] = f"{n} letters"
            return opts

        def _refresh_dynamic_dropdowns(self) -> None:
            self._suppress_events = True
            try:
                len_opts = self._get_length_options()
                self.sel_length.options = len_opts
                if self.form_length not in len_opts:
                    self.form_length = "ALL"
                    self.sel_length.value = "ALL"
                self.sel_length.update()

                eff_opts = GLOBAL_DB.get_ordered_effect_options()
                self.sel_effect.options = eff_opts
                if self.form_effect not in eff_opts:
                    self.form_effect = ""
                    self.sel_effect.value = ""
                self.sel_effect.update()

                sort_opts = self._get_sort_options()
                self.sel_sort.options = sort_opts
                if self.sort_by not in sort_opts:
                    self.sort_by = "points"
                    self.sel_sort.value = "points"
                self.sel_sort.update()
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
        def on_category_change(self, e) -> None:
            if self._suppress_events:
                return
            self.kind_filter = str(e.value or "ALL")
            self._suppress_events = True
            try:
                sort_opts = self._get_sort_options()
                self.sel_sort.options = sort_opts
                if self.sort_by not in sort_opts:
                    self.sort_by = "points"
                    self.sel_sort.value = "points"
                self.sel_sort.update()
            finally:
                self._suppress_events = False
            self.run_applied_search(reset_pagination=True)

        def on_sort_change(self, e) -> None:
            if self._suppress_events:
                return
            self.sort_by = str(e.value or "points")
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

        def on_find_words(self) -> None:
            self.applied_query = self._snapshot_form()
            self._update_pending_indicator()
            self.run_applied_search(reset_pagination=True)

        def on_clear(self) -> None:
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
                self.favorites_only = False

                self.inp_letters.value = ""
                self.inp_contains.value = ""
                self.inp_starts.value = ""
                self.inp_ends.value = ""
                self.sel_length.value = "ALL"
                self.sel_effect.value = ""
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
            save_favorites_txt(self.favorites_path, self.favorites)
            self._update_favorites_banner()

            if self.favorites_only:
                self.run_applied_search(reset_pagination=False)
            elif heart_btn is not None:
                heart_btn.set_text("♥" if is_fav else "♡")
                heart_btn.style(
                    f"color: {'#D93829' if is_fav else '#666666'}; min-width: 24px;"
                )

        # ---- Search & Render ----
        def run_applied_search(self, reset_pagination: bool = True) -> None:
            if not GLOBAL_DB.units:
                self.current_matches = []
                self.lbl_result_count.set_text("0 words loaded")
                self._update_favorites_banner()
                self._render_results()
                return

            q = self.applied_query
            matches = GLOBAL_DB.search(
                available_letters=q["available_letters"],
                starts_with=q["starts_with"],
                ends_with=q["ends_with"],
                contains=q["contains"],
                in_order=q["in_order"],
                exact_amount=q["exact_amount"],
                length_filter=q["length_filter"],
                kind_filter=self.kind_filter,
                effect_filter=q["effect_filter"],
                favorites_only=self.favorites_only,
                favorites=self.favorites,
                sort_by=self.sort_by,
                descending=self.descending,
                group_by_length=self.group_by_length,
            )

            self.current_matches = matches
            if reset_pagination:
                self.visible_limit = PAGE_SIZE
                self.collapsed_lengths.clear()

            n = len(matches)
            word_lbl = "word" if n == 1 else "words"
            self.lbl_result_count.set_text(f"{n:,} {word_lbl} found")
            self._update_favorites_banner()
            self._render_results()

        def _load_more(self, amount: int = PAGE_SIZE) -> None:
            ui.run_javascript(
                "const x = window.scrollX, y = window.scrollY; "
                "const restore = () => window.scrollTo(x, y); "
                "window.__babbleRestoreScroll = restore; "
                "restore(); "
                "setTimeout(restore, 50); "
                "setTimeout(restore, 150); "
                "setTimeout(restore, 350);"
            )
            self.visible_limit += amount
            self._render_results()
            ui.run_javascript(
                "requestAnimationFrame(() => window.__babbleRestoreScroll?.()); "
                "setTimeout(() => window.__babbleRestoreScroll?.(), 100); "
                "setTimeout(() => window.__babbleRestoreScroll?.(), 300);"
            )

        def _render_results(self) -> None:
            self.results_container.clear()
            matches = self.current_matches

            with self.results_container:
                if not matches:
                    with ui.column().classes("w-full items-center py-10"):
                        ui.label("No matching words found.").classes(
                            "text-base font-bold"
                        ).style("color: #595959;")
                        ui.label(
                            "Type letters above and click FIND WORDS, or adjust your filters."
                        ).classes("text-sm").style("color: #777777;")
                    return

                visible = matches[: self.visible_limit]
                active_stat = (
                    self.sort_by
                    if self.sort_by not in ("points", "alphabetical")
                    else None
                )

                if self.group_by_length:
                    # Precompute total count per length across ALL matches (not just visible slice)
                    total_per_len: Dict[int, int] = {}
                    for r in matches:
                        total_per_len[r.length] = total_per_len.get(r.length, 0) + 1

                    i = 0
                    n_vis = len(visible)
                    while i < n_vis:
                        length = visible[i].length
                        j = i + 1
                        while j < n_vis and visible[j].length == length:
                            j += 1
                        group_items = visible[i:j]
                        self._render_length_group(
                            length,
                            group_items,
                            total_per_len[length],
                            active_stat,
                        )
                        i = j
                else:
                    with ui.column().classes("w-full gap-1.5"):
                        for rec in visible:
                            self._render_unit_box(rec, active_stat)

                # Load-more footer when results exceed current page limit
                remaining = len(matches) - len(visible)
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

                def toggle_group(_e=None, L=length, b=body, a=arrow_lbl):
                    if L in self.collapsed_lengths:
                        self.collapsed_lengths.remove(L)
                        b.set_visibility(True)
                        a.set_text("▾")
                    else:
                        self.collapsed_lengths.add(L)
                        b.set_visibility(False)
                        a.set_text("▸")

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

                            def_url = f"https://onelook.com/?w={quote_plus(rec.word)}"
                            def_btn = (
                                ui.button("DEF")
                                .props(
                                    f'unelevated dense href="{def_url}" target="_blank"'
                                )
                                .classes("babble-mini-use")
                            )
                            def_btn.tooltip(f"Open OneLook definition for '{rec.word}'")
                            def_btn.on("click.stop", lambda _e: None)

                        # Rightmost stack: [optional active stat] + [PTS tile] on top, [X letters] directly below PTS
                        with ui.column().classes("items-end gap-1"):
                            with ui.row().classes("items-center gap-1.5 no-wrap"):
                                if active_stat:
                                    sv = rec.get_stat_value(active_stat)
                                    short_lbl = STAT_SHORT_LABELS.get(
                                        active_stat, pretty_name(active_stat).upper()
                                    )
                                    sv_txt = (
                                        f"{short_lbl}: {fmt_num(sv, 2) if sv is not None else '—'}"
                                    )
                                    ui.label(sv_txt).classes("babble-stat-chip")

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
                    dps_t = self._cmp_tone(rec.dps, 5.0)
                    spd_t = self._cmp_tone(rec.attack_speed, 1.0)
                    rng_t = self._cmp_tone(rec.range, TOWER_DEFAULTS["range"])
                    hp_t = self._cmp_tone(rec.health, TOWER_DEFAULTS["health"])
                    arm_t = self._cmp_tone(rec.armor, TOWER_DEFAULTS["armor"])

                    stats_grid = [
                        ("Damage", fmt_num(rec.damage, 2), dmg_t),
                        ("DPS", fmt_num(rec.dps, 2), dps_t),
                        (
                            "Attack Speed",
                            f"{fmt_num(rec.attack_speed, 2)}/s ({fmt_num(rec.attack_interval, 3)}s)",
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

        # ---- Load JSON Dialog ----
        def _build_load_dialog(self) -> None:
            self.load_dialog = ui.dialog()
            with self.load_dialog, ui.card().classes("w-[480px] max-w-full").style(
                "background: #E4E4E4; border: 1px solid #B7B7B7;"
            ):
                ui.label("LOAD UNITS JSON").classes("text-sm font-bold").style(
                    "color: #222222;"
                )
                ui.label(
                    "Enter a local path to units.json or upload a JSON file directly:"
                ).classes("text-xs").style("color: #595959;")

                path_input = (
                    ui.input(
                        value=GLOBAL_DB.source_path,
                        placeholder="Path to units.json…",
                    )
                    .props("outlined dense")
                    .classes("w-full babble-input")
                )

                def load_from_path():
                    p = str(path_input.value or "").strip().strip('"')
                    if not p or not os.path.isfile(p):
                        ui.notify(f"File not found: {p}", type="negative")
                        return
                    try:
                        count = GLOBAL_DB.load_file(p)
                        curse_path = Path(p).with_name("cursed_words.json")
                        if curse_path.is_file():
                            count += GLOBAL_DB.load_extra_file(str(curse_path))
                        self._on_new_db_loaded(os.path.basename(p), count)
                        self.load_dialog.close()
                    except Exception as exc:
                        ui.notify(f"Failed to load JSON: {exc}", type="negative")

                def handle_upload(e):
                    try:
                        raw_bytes = e.content.read()
                        data = json.loads(raw_bytes.decode("utf-8"))
                        count = GLOBAL_DB.load_data(data, source_label=e.name)
                        self._on_new_db_loaded(e.name, count)
                        self.load_dialog.close()
                    except Exception as exc:
                        ui.notify(f"Upload parse error: {exc}", type="negative")

                with ui.row().classes("w-full justify-end gap-2 mt-1"):
                    ui.button("LOAD PATH", on_click=load_from_path).props(
                        "unelevated dense"
                    ).classes("babble-pill-blue px-4")

                ui.separator().style("background-color: #C4C4C4;")
                ui.upload(
                    label="Or drop / select units.json here",
                    auto_upload=True,
                    max_file_size=100_000_000,
                    on_upload=handle_upload,
                ).props('accept=".json" flat bordered').classes("w-full")

                with ui.row().classes("w-full justify-end mt-2"):
                    ui.button("CLOSE", on_click=self.load_dialog.close).props(
                        "unelevated dense"
                    ).classes("babble-pill px-4")

        def _on_new_db_loaded(self, name: str, count: int) -> None:
            self.lbl_file_status.set_text(f"{name} ({count:,} units)")
            self._refresh_dynamic_dropdowns()
            self.applied_query = self._snapshot_form()
            self._update_pending_indicator()
            self.run_applied_search(reset_pagination=True)
            ui.notify(f"Loaded {count:,} units from {name}", type="positive")

        # ---- Main Page Layout ----
        def build(self) -> None:
            ui.add_head_html(CUSTOM_CSS)
            self._build_load_dialog()

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
                            "Enter available letters, then click find words! Made by Levi."
                        ).classes("text-xs").style("color: #595959;")

                    with ui.column().classes("items-end gap-1"):
                        ui.button("LOAD JSON", on_click=self.load_dialog.open).props(
                            "unelevated dense"
                        ).classes("babble-pill px-4")
                        status_txt = (
                            f"{os.path.basename(GLOBAL_DB.source_path)} ({len(GLOBAL_DB.units):,} units)"
                            if GLOBAL_DB.units
                            else "No units.json loaded — click LOAD JSON"
                        )
                        self.lbl_file_status = ui.label(status_txt).classes(
                            "text-xs"
                        ).style("color: #666666;")

                ui.separator().style("background-color: #B7B7B7; height: 2px;")

                # ---- CONTROLS PANEL ----
                with ui.column().classes("w-full babble-panel gap-3"):
                    # Row 1: Available Letters + Find Words + Clear
                    with ui.column().classes("w-full gap-1"):
                        with ui.row().classes("w-full items-center justify-between"):
                            ui.label("AVAILABLE LETTERS").classes("babble-field-lbl")
                            self.lbl_letter_count = ui.label(
                                "0 letters (browsing all)"
                            ).classes("text-xs").style("color: #666666;")

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

                            ui.button("CLEAR", on_click=self.on_clear).props(
                                "unelevated"
                            ).classes("babble-pill px-4 h-10")

                    # Row 2: Combined Show (Category) + Sort By + Order + Group Toggle + Favorites
                    with ui.row().classes(
                        "w-full items-center justify-between gap-2 flex-wrap"
                    ):
                        with ui.row().classes("items-center gap-2 flex-wrap"):
                            self.sel_category = (
                                ui.select(
                                    options={
                                        "ALL": "All Types",
                                        "TOWER": "Towers",
                                        "HARVESTER": "Harvesters",
                                        "MOD": "Mods",
                                        "CURSED": "Cursed",
                                    },
                                    value=self.kind_filter,
                                    label="Show",
                                    on_change=self.on_category_change,
                                )
                                .props("outlined dense options-dense")
                                .classes("babble-input w-32")
                            )

                            self.sel_sort = (
                                ui.select(
                                    options=self._get_sort_options(),
                                    value=self.sort_by,
                                    label="Sort by",
                                    on_change=self.on_sort_change,
                                )
                                .props("outlined dense options-dense")
                                .classes("babble-input w-48")
                            )

                            self.sel_order = (
                                ui.select(
                                    options=["Descending", "Ascending"],
                                    value="Descending",
                                    label="Order",
                                    on_change=self.on_order_change,
                                )
                                .props("outlined dense options-dense")
                                .classes("babble-input w-40")
                            )

                            self.btn_group = (
                                ui.button(
                                    "GROUP BY LENGTH", on_click=self.on_toggle_group
                                )
                                .props("unelevated dense")
                                .classes("babble-pill-blue px-3 h-9 text-xs")
                            )

                        self.btn_favorites = (
                            ui.button(
                                "♥ FAVORITES", on_click=self.on_toggle_favorites_only
                            )
                            .props("unelevated dense")
                            .classes("babble-pill px-4 h-9 text-xs")
                        )
                        self._sync_favorite_style(False)

                    ui.separator().style("background-color: #C8C8C8;")

                    # Row 3: CONTAINS + In Order + Exact Amount (deferred until Find Words)
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

                            self._sync_pill_style(self.btn_group, True)
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
                    # Results Header: RESULTS  |  ♥ X favorites (only when >0)  |  X words found
                    with ui.row().classes(
                        "w-full items-center justify-between gap-2 pb-1"
                    ):
                        ui.label("RESULTS").classes("babble-field-lbl")

                        self.lbl_fav_count = ui.label("").classes(
                            "text-xs font-bold"
                        ).style("color: #D93829;")
                        self.lbl_fav_count.set_visibility(False)

                        self.lbl_result_count = ui.label("0 words found").classes(
                            "text-xs font-bold"
                        ).style("color: #595959;")

                    ui.separator().style("background-color: #C8C8C8;")

                    self.results_container = ui.column().classes("w-full gap-1.5")

            # Perform initial render of loaded units
            self.run_applied_search(reset_pagination=True)

    @ui.page("/")
    def index_page():
        session = FinderSession()
        session.build()

    return ui


def main():
    from nicegui import app

    loaded = autoload_database()
    if loaded:
        print(f"Loaded {len(GLOBAL_DB.units):,} units from {loaded}")
    else:
        print("No units.json found automatically — use the LOAD JSON button in the UI.")

    ui = build_nicegui_app()
    app.native.window_args["min_size"] = (980, 860)
    ui.run(
        title="Towers of Babble — Word Finder",
        reload=False,
        native=True,
        window_size=(980, 860),
        port=8080,
    )


if __name__ == "__main__":
    main()
