/* Towers of Babble Word Finder — web version.
 * A browser port of TowersOfBabbleWordFinder.py: same data, search, sorting,
 * stat filters, clever mode and favorites, running entirely client-side. */
"use strict";

// ---------------------------------------------------------------------------
// Constants (mirrors the desktop app)
// ---------------------------------------------------------------------------
const PAGE_SIZE = 200;
const FAVORITES_KEY = "tob-word-finder:favorites";
const PREFS_KEY = "tob-word-finder:prefs";

const KIND_META = {
  TOWER: { display: "tower", cls: "tower" },
  MOD: { display: "mod", cls: "mod" },
  HARVESTER: { display: "harvester", cls: "harvester" },
  CURSED: { display: "cursed", cls: "cursed" },
};

const RESOURCE_COLORS = {
  ore: ["O", "#303030", "#AAAAAA"],
  crystal: ["C", "#134B73", "#88C9FE"],
  wood: ["W", "#1E5626", "#8BD094"],
};

const TOWER_DEFAULTS = { damage: 5, range: 4, attackInterval: 1, attackSpeed: 2, health: 100, armor: 1 };
const HARVESTER_DEFAULTS = { health: 120, armor: 0, harvestAmount: 2, harvestInterval: 3.2, harvestTypes: 1, harvestRange: 3 };

const EFFECT_RESOURCE_ORDER = [
  "damage", "dmg_buff_aura", "attack_speed", "firerate_buff_aura", "toughness", "heal_aura", "armor",
  "armor_buff_aura", "crit", "range", "burn", "burn_aura", "poison", "curse", "slow", "slow_aura",
  "knockback", "stun", "multishot", "pierce", "armor_shred", "splash", "chain", "res:ore", "res:crystal",
  "res:wood", "harvest_amount", "harvest_speed", "multi_harvest", "harvest_aura", "base_range",
  "base_health", "no_healing", "one_mod_slot", "no_nearby_buildings", "no_nearby_resources",
];

const DISPLAY_NAMES = {
  curse: "Curse", damage: "Damage", dps: "DPS", dmg_buff_aura: "Damage Aura", attack_speed: "Attack Speed",
  firerate_buff_aura: "Atk Spd Aura", toughness: "HP", health: "HP", heal_aura: "Heal Aura", armor: "Armor",
  armor_buff_aura: "Armor Aura", crit: "Crit", range: "Range", burn: "Burn", burn_aura: "Burn Aura",
  poison: "Poison", slow: "Slow", slow_aura: "Slow Aura", knockback: "Knockback", stun: "Stun",
  multishot: "Multi Shot", pierce: "Pierce", armor_shred: "Shred", splash: "Splash", chain: "Chain",
  "res:ore": "Resource Ore", "res:crystal": "Resource Crystal", "res:wood": "Resource Wood",
  harvest_amount: "Harvest Amount", harvest_speed: "Harvest Speed", harvest_rate: "Harvest Rate",
  harvest_types: "Resource Types", multi_harvest: "Multi Harvest", harvest_aura: "Harvest Aura",
  base_range: "Base Range", base_health: "Base Health", no_healing: "No Healing", one_mod_slot: "One Mod Slot",
  no_nearby_buildings: "No Nearby Buildings", no_nearby_resources: "No Nearby Resources",
};

// [key, label, active background]
const STAT_FILTERS = [
  ["toughness", "HEALTH", "#2A732E"], ["armor", "ARMOR", "#835C4F"], ["damage", "DAMAGE", "#C22727"],
  ["attack_speed", "ATTACK SPEED", "#9C2ACC"], ["range", "RANGE", "#1564BE"], ["multishot", "MULTISHOT", "#A44B07"],
  ["splash", "SPLASH", "#155FD2"], ["chain", "CHAIN", "#7D6100"], ["pierce", "PIERCE", "#C21862"],
  ["crit", "CRIT", "#AC4500"], ["poison", "POISON", "#237429"], ["slow", "SLOW", "#1564BE"],
  ["stun", "STUN", "#676900"], ["knockback", "KNOCKBACK", "#BF1871"], ["armor_shred", "ARMOR SHRED", "#A84800"],
  ["dmg_buff_aura", "DAMAGE AURA", "#C51F1F"], ["firerate_buff_aura", "ATTACK SPEED AURA", "#962AD7"],
  ["armor_buff_aura", "ARMOR AURA", "#835C50"], ["heal_aura", "HEAL AURA", "#2C732F"],
  ["slow_aura", "SLOW AURA", "#155FD2"], ["burn_aura", "BURN AURA", "#C22727"],
  ["harvest_amount", "HARVEST AMOUNT", "#457024"], ["harvest_speed", "HARVEST INTERVAL", "#4E6E2F"],
  ["multi_harvest", "MULTI HARVEST", "#2A732E"], ["harvest_aura", "HARVEST AURA", "#237429"],
  ["curse", "CURSE", "#962AD7"],
];
const STAT_FILTER_INDEX = Object.fromEntries(STAT_FILTERS.map(([k], i) => [k, i]));

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
const $ = (id) => document.getElementById(id);
const nf = new Intl.NumberFormat("en-US");
const fmtInt = (n) => nf.format(n);

function lighten(color, amount = 0.82) {
  const ch = [1, 3, 5].map((i) => parseInt(color.slice(i, i + 2), 16));
  return "#" + ch.map((c) => Math.round(c + (255 - c) * amount).toString(16).padStart(2, "0")).join("");
}

function prettyName(key) {
  if (key in DISPLAY_NAMES) return DISPLAY_NAMES[key];
  return key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()).replace(/\B\w+/g, (s) => s.toLowerCase());
}

function titleCase(s) { return s.charAt(0).toUpperCase() + s.slice(1).toLowerCase(); }

function fmtNum(val, decimals = 2) {
  if (val === null || val === undefined || Number.isNaN(val)) return "—";
  if (Math.abs(val - Math.round(val)) < 1e-6) return String(Math.round(val));
  let s = val.toFixed(decimals);
  if (s.includes(".")) s = s.replace(/0+$/, "").replace(/\.$/, "");
  return s === "-0" ? "0" : s;
}

const attackRateFromStat = (stat) => Math.pow(Math.max(0.01, stat) / 2, 0.78);
const critChanceFromStat = (stat) => 0.1 + 0.4 * Math.min(1, Math.max(0, stat / 1000));
function critMultiplierFromStat(stat) {
  const chance = critChanceFromStat(stat);
  const critDamage = 1.1 + (7 * stat) / 1000;
  return 1 + (critDamage - 1) / chance;
}
const formatCritSummary = (stat) => `${fmtNum(critChanceFromStat(stat) * 100, 0)}% x${fmtNum(critMultiplierFromStat(stat), 1)}`;

function normalizeKind(raw) {
  const k = String(raw || "TOWER").toUpperCase();
  if (k.startsWith("MODIFIER") || k === "MOD") return "MOD";
  if (k === "HARVESTER") return "HARVESTER";
  return "TOWER";
}

const isRackChar = (ch) => (ch >= "a" && ch <= "z") || ch === "?" || ch === "*";
const cleanRack = (s) => [...String(s).toLowerCase()].filter(isRackChar).join("");
const cleanLetters = (s) => [...String(s).toLowerCase()].filter((ch) => ch >= "a" && ch <= "z").join("");
const optNum = (v) => (v === undefined || v === null ? null : Number(v));

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function letterCounts(word) {
  const counts = new Uint8Array(26);
  for (let i = 0; i < word.length; i++) {
    const o = word.charCodeAt(i) - 97;
    if (o >= 0 && o < 26) counts[o]++;
  }
  return counts;
}

/** Remove the letters needed for `word` from the rack (exact letters first, then wildcards). */
function consumeWordLetters(available, word) {
  const chars = [...available].filter((ch) => isRackChar(ch.toLowerCase())).map((ch) => ch.toUpperCase());
  if (!chars.length) return ["", 0];
  let consumed = 0;
  for (const needed of word.toUpperCase()) {
    if (needed < "A" || needed > "Z") continue;
    let idx = chars.indexOf(needed);
    if (idx < 0) idx = chars.indexOf("?");
    if (idx < 0) idx = chars.indexOf("*");
    if (idx >= 0) { chars.splice(idx, 1); consumed++; }
  }
  return [chars.join(""), consumed];
}

// ---------------------------------------------------------------------------
// Unit record
// ---------------------------------------------------------------------------
class UnitRecord {
  constructor(u) {
    const w = String(u.word || "").trim().toLowerCase();
    this.word = w;
    this.upper = w.toUpperCase();
    this.length = w.length;
    this.counts = letterCounts(w);
    let mask = 0;
    for (let i = 0; i < 26; i++) if (this.counts[i]) mask |= 1 << i;
    this.mask = mask;
    this.kind = normalizeKind(u.kind);
    this.scrabble = parseInt(u.scrabble || 0, 10) || 0;

    this.damage = optNum(u.damage);
    this.range = optNum(u.range);
    this.attackInterval = optNum(u.attackInterval);
    if (this.attackInterval && this.attackInterval > 0) {
      this.attackSpeed = 1 / this.attackInterval + 1;
      this.attacksPerSecond = attackRateFromStat(this.attackSpeed);
    } else {
      this.attackSpeed = null;
      this.attacksPerSecond = null;
    }
    this.dps = null;
    this.health = optNum(u.health);
    this.armor = u.armor !== undefined && u.armor !== null ? Number(u.armor) : this.kind === "TOWER" ? 0 : null;
    this.isCursed = !!u.isCursed;
    this.curseEffects = (u.curseEffects || []).map(String);

    this.harvestAmount = optNum(u.harvestAmount);
    this.harvestInterval = optNum(u.harvestInterval);
    if (this.harvestInterval && this.harvestInterval > 0) {
      this.harvestSpeed = 1 / this.harvestInterval;
      this.harvestRate = this.harvestAmount !== null ? this.harvestAmount / this.harvestInterval : null;
    } else {
      this.harvestSpeed = null;
      this.harvestRate = null;
    }
    this.harvestTypes = u.harvestTypes !== undefined && u.harvestTypes !== null ? parseInt(u.harvestTypes, 10) : null;
    this.harvestRange = optNum(u.harvestRange);
    this.harvestResources = (u.harvestResources || []).map(String);

    this.specials = (u.specials || []).map((s) => [String(s.name || ""), Number(s.value || 0)]);
    if (this.damage !== null && this.attacksPerSecond !== null) {
      const crit = this.specialVal("crit") ?? 0;
      const chance = critChanceFromStat(crit);
      const mult = critMultiplierFromStat(crit);
      this.dps = this.damage * this.attacksPerSecond * (1 + chance * (mult - 1));
    }
    this.deltas = (u.deltas || []).map((d) => [String(d.stat || ""), String(d.op || ""), Number(d.value || 0)]);

    const tags = new Set();
    for (const [name] of this.specials) tags.add(name);
    for (const [stat] of this.deltas) tags.add(stat);
    for (const r of this.harvestResources) tags.add("res:" + r);
    if (this.isCursed) { tags.add("curse"); this.curseEffects.forEach((e) => tags.add(e)); }
    if (this.kind === "TOWER") {
      if (this.damage !== null && this.damage > TOWER_DEFAULTS.damage + 0.01) tags.add("damage");
      if (this.attackSpeed !== null && this.attackSpeed > TOWER_DEFAULTS.attackSpeed + 0.01) tags.add("attack_speed");
      if (this.health !== null && this.health > TOWER_DEFAULTS.health + 0.1) tags.add("toughness");
      if (this.armor !== null && this.armor > TOWER_DEFAULTS.armor + 0.01) tags.add("armor");
      if (this.range !== null && this.range > TOWER_DEFAULTS.range + 0.01) tags.add("range");
    } else if (this.kind === "HARVESTER") {
      if (this.health !== null && this.health > HARVESTER_DEFAULTS.health + 0.1) tags.add("toughness");
      if (this.armor !== null && this.armor > 0.01) tags.add("armor");
      if (this.harvestRange !== null && this.harvestRange > HARVESTER_DEFAULTS.harvestRange + 0.01) tags.add("range");
      if (this.harvestAmount !== null && this.harvestAmount > HARVESTER_DEFAULTS.harvestAmount + 0.01) tags.add("harvest_amount");
      if (this.harvestInterval !== null && this.harvestInterval < HARVESTER_DEFAULTS.harvestInterval - 0.01) tags.add("harvest_speed");
    }
    this.tags = tags;
    this._preview = null;
    this.positiveMask = this.buildPositiveMask();
  }

  specialVal(name) {
    for (const [n, v] of this.specials) if (n === name) return v;
    return null;
  }

  deltaVal(stat) {
    for (const [s, , v] of this.deltas) if (s === stat) return v;
    return null;
  }

  baseStatChange(key) {
    const k = this.kind;
    if (key === "damage" && k === "TOWER" && this.damage !== null) return this.damage - TOWER_DEFAULTS.damage;
    if (key === "attack_speed" && k === "TOWER" && this.attackSpeed !== null) return this.attackSpeed - TOWER_DEFAULTS.attackSpeed;
    if ((key === "toughness" || key === "health") && (k === "TOWER" || k === "HARVESTER") && this.health !== null)
      return this.health - (k === "TOWER" ? TOWER_DEFAULTS.health : HARVESTER_DEFAULTS.health);
    if (key === "armor" && (k === "TOWER" || k === "HARVESTER") && this.armor !== null)
      return this.armor - (k === "TOWER" ? TOWER_DEFAULTS.armor : 0);
    if (key === "range" && k === "TOWER" && this.range !== null) return this.range - TOWER_DEFAULTS.range;
    if (key === "range" && k === "HARVESTER" && this.harvestRange !== null) return this.harvestRange - HARVESTER_DEFAULTS.harvestRange;
    if (key === "harvest_amount" && k === "HARVESTER" && this.harvestAmount !== null) return this.harvestAmount - HARVESTER_DEFAULTS.harvestAmount;
    if (key === "harvest_speed" && k === "HARVESTER" && this.harvestSpeed !== null) return this.harvestSpeed - 1 / HARVESTER_DEFAULTS.harvestInterval;
    return null;
  }

  buildPositiveMask() {
    const positive = {};
    for (const [stat, op, value] of this.deltas) {
      if (!(stat in positive)) positive[stat] = (op.toLowerCase() === "mult" ? value - 1 : value) > 0.01;
    }
    for (const [name, value] of this.specials) if (!(name in positive)) positive[name] = value > 0.01;
    let mask = 0;
    STAT_FILTERS.forEach(([key], i) => {
      let on;
      if (key === "curse") on = this.isCursed;
      else {
        const base = this.baseStatChange(key);
        on = base !== null ? base > 0.01 : !!positive[key];
      }
      if (on) mask |= 1 << i;
    });
    return mask;
  }

  hasPositive(key) {
    const i = STAT_FILTER_INDEX[key];
    return i !== undefined && (this.positiveMask & (1 << i)) !== 0;
  }

  positiveChange(key) {
    if (key === "curse") return this.isCursed ? 1 : null;
    const base = this.baseStatChange(key);
    if (base !== null) return base > 0.01 ? base : null;
    for (const [stat, op, value] of this.deltas) {
      if (stat === key) {
        const change = op.toLowerCase() === "mult" ? value - 1 : value;
        return change > 0.01 ? change : null;
      }
    }
    const sp = this.specialVal(key);
    return sp !== null && sp > 0.01 ? sp : null;
  }

  statValue(key) {
    switch (key) {
      case "damage": return this.damage ?? this.deltaVal("damage");
      case "dps": return this.dps;
      case "attack_speed": return this.attackSpeed ?? this.deltaVal("attack_speed");
      case "toughness": case "health": return this.health ?? this.deltaVal("toughness");
      case "armor":
        if (this.armor !== null && (this.armor > 0 || this.kind === "TOWER")) return this.armor;
        return this.deltaVal("armor");
      case "range": return this.range ?? this.harvestRange ?? this.deltaVal("range");
      case "harvest_amount": return this.harvestAmount ?? this.deltaVal("harvest_amount");
      case "harvest_speed": return this.harvestSpeed ?? this.deltaVal("harvest_speed");
      case "harvest_rate": return this.harvestRate;
      case "harvest_types": return this.harvestTypes;
      default: {
        const sp = this.specialVal(key);
        return sp !== null ? sp : this.deltaVal(key);
      }
    }
  }

  previewStats(priorityKey) {
    if (this._preview === null) this._preview = this.defaultPreview();
    if (priorityKey && priorityKey !== "points" && priorityKey !== "alphabetical") {
      const val = this.statValue(priorityKey);
      if (val !== null && val !== undefined) {
        const item = this.formatPriority(priorityKey, val);
        if (item) return [item, ...this._preview.filter((x) => x[1] !== item[1])].slice(0, 3);
      }
    }
    return this._preview.slice(0, 3);
  }

  formatPriority(key, val) {
    const mod = this.kind === "MOD";
    if (key === "damage") {
      const tone = mod || val > 5.01 ? "pos" : val < 4.99 ? "neg" : "neutral";
      return [`${mod ? "+" : ""}${fmtNum(val, 1)}`, "Damage", tone];
    }
    if (key === "dps") return [fmtNum(val, 1), "DPS", val > 5.01 ? "pos" : val < 4.99 ? "neg" : "neutral"];
    if (key === "attack_speed") {
      if (this.kind === "TOWER") {
        const d = val - TOWER_DEFAULTS.attackSpeed;
        return [d > 0 ? `+${fmtNum(d, 2)}` : fmtNum(d, 2), "Attack Speed", d > 0.01 ? "pos" : d < -0.01 ? "neg" : "neutral"];
      }
      return [`+${fmtNum(val, 2)}`, "Attack Speed", "pos"];
    }
    if (key === "toughness" || key === "health") {
      if (mod) return [`+${fmtNum(val, 1)}`, "HP", "pos"];
      const d = this.kind === "TOWER" ? 100 : 120;
      return [fmtNum(val, 0), "HP", val > d + 0.1 ? "pos" : val < d - 0.1 ? "neg" : "neutral"];
    }
    if (key === "armor") {
      const tone = mod || val > 1.01 ? "pos" : this.kind === "TOWER" && val < 0.99 ? "neg" : "neutral";
      return [`${mod ? "+" : ""}${fmtNum(val, 1)}`, "Armor", tone];
    }
    if (key === "range") {
      if (mod) return [`+${fmtNum(val, 2)}`, "Range", "pos"];
      const d = this.kind === "TOWER" ? 4 : 3;
      return [fmtNum(val, 1), "Range", val > d + 0.01 ? "pos" : val < d - 0.01 ? "neg" : "neutral"];
    }
    if (key === "harvest_amount") {
      const tone = mod || val > 2.01 ? "pos" : val < 1.99 ? "neg" : "neutral";
      return [`${mod ? "+" : ""}${fmtNum(val, 1)}`, "Harvest Amount", tone];
    }
    if (key === "harvest_speed") {
      if (this.kind === "HARVESTER") {
        const d = 1 / 3.2;
        return [`${fmtNum(val, 2)}/s`, "Harvest Speed", val > d + 0.01 ? "pos" : val < d - 0.01 ? "neg" : "neutral"];
      }
      return [`+${fmtNum(val, 2)}`, "Harvest Speed", "pos"];
    }
    if (key === "harvest_rate") {
      const d = 2 / 3.2;
      return [`${fmtNum(val, 2)}/s`, "Harvest Rate", val > d + 0.01 ? "pos" : val < d - 0.01 ? "neg" : "neutral"];
    }
    if (key === "harvest_types") return [fmtNum(val, 0), "Resource Types", val > 1 ? "pos" : "neutral"];
    return [`+${fmtNum(val, 2)}`, prettyName(key), "pos"];
  }

  defaultPreview() {
    const items = [];
    const T = TOWER_DEFAULTS;
    if (this.kind === "TOWER") {
      for (const [name, val] of this.specials) items.push([`+${fmtNum(val, 2)}`, prettyName(name), "pos"]);
      if (this.damage !== null && this.damage > T.damage + 0.01) items.push([fmtNum(this.damage, 1), "Damage", "pos"]);
      if (this.attackSpeed !== null && this.attackSpeed > T.attackSpeed + 0.01)
        items.push([`+${fmtNum(this.attackSpeed - T.attackSpeed, 2)}`, "Attack Speed", "pos"]);
      if (this.range !== null && this.range > T.range + 0.01) items.push([fmtNum(this.range, 1), "Range", "pos"]);
      if (this.health !== null && this.health > T.health + 0.1) items.push([fmtNum(this.health, 0), "HP", "pos"]);
      if (this.armor !== null && this.armor > T.armor + 0.01) items.push([fmtNum(this.armor, 1), "Armor", "pos"]);
      if (this.damage !== null && this.damage < T.damage - 0.01) items.push([fmtNum(this.damage, 1), "Damage", "neg"]);
      if (this.attackSpeed !== null && this.attackSpeed < T.attackSpeed - 0.01)
        items.push([fmtNum(this.attackSpeed - T.attackSpeed, 2), "Attack Speed", "neg"]);
      if (this.range !== null && this.range < T.range - 0.01) items.push([fmtNum(this.range, 1), "Range", "neg"]);
      if (this.health !== null && this.health < T.health - 0.1) items.push([fmtNum(this.health, 0), "HP", "neg"]);
      if (this.armor !== null && this.armor < T.armor - 0.01) items.push(["0", "Armor", "neg"]);
      return items.slice(0, 3);
    }
    if (this.kind === "HARVESTER") {
      const H = HARVESTER_DEFAULTS;
      if (this.harvestResources.length)
        items.push([this.harvestResources.map(titleCase).join("/"), "", this.harvestResources.length > 1 ? "pos" : "neutral"]);
      for (const [name, val] of this.specials) items.push([`+${fmtNum(val, 2)}`, prettyName(name), "pos"]);
      if (this.harvestAmount !== null && this.harvestInterval !== null) {
        const boosted = this.harvestAmount > H.harvestAmount + 0.01 || this.harvestInterval < H.harvestInterval - 0.01;
        const reduced = this.harvestAmount < H.harvestAmount - 0.01 || this.harvestInterval > H.harvestInterval + 0.01;
        if (boosted || reduced)
          items.push([`${fmtNum(this.harvestAmount, 1)}/${fmtNum(this.harvestInterval, 2)}s`, "Harvest", boosted ? "pos" : "neg"]);
      }
      if (items.length < 3 && this.harvestRange !== null && Math.abs(this.harvestRange - 3) > 0.01)
        items.push([fmtNum(this.harvestRange, 1), "Range", this.harvestRange > 3 ? "pos" : "neg"]);
      if (items.length < 3 && this.health !== null && Math.abs(this.health - 120) > 0.1)
        items.push([fmtNum(this.health, 0), "HP", this.health > 120 ? "pos" : "neg"]);
      if (items.length < 3 && this.armor !== null && this.armor > 0.01) items.push([fmtNum(this.armor, 1), "Armor", "pos"]);
      return items.slice(0, 3);
    }
    if (!this.deltas.length) return [["—", "No effects", "neutral"]];
    for (const [stat, op, val] of this.deltas.slice(0, 3))
      items.push([op === "mult" ? `×${fmtNum(val, 3)}` : `+${fmtNum(val, 2)}`, prettyName(stat), "pos"]);
    return items;
  }

  get meta() { return this.isCursed ? KIND_META.CURSED : KIND_META[this.kind] || KIND_META.TOWER; }
}

// ---------------------------------------------------------------------------
// Database
// ---------------------------------------------------------------------------
const KIND_CODES = ["TOWER", "HARVESTER", "MODIFIER"];

/** Expand a compact row from data/words.json into the raw units.json shape. */
function unpackRow(row, names) {
  const [word, kind, scrabble] = row;
  const u = { word, kind: KIND_CODES[kind], scrabble };
  let i = 3;
  if (kind === 0) {
    [u.damage, u.range, u.attackInterval, u.health, u.armor] = row.slice(3, 8);
    i = 8;
  } else if (kind === 1) {
    [u.health, u.armor, u.harvestAmount, u.harvestInterval, u.harvestTypes, u.harvestRange] = row.slice(3, 9);
    u.harvestResources = row[9].map((n) => names[n]);
    i = 10;
  }
  for (const k of Object.keys(u)) if (u[k] === null) delete u[k];
  const sp = row[i] || [];
  u.specials = [];
  for (let j = 0; j < sp.length; j += 2) u.specials.push({ name: names[sp[j]], value: sp[j + 1] });
  const de = row[i + 1] || [];
  u.deltas = [];
  for (let j = 0; j < de.length; j += 3) u.deltas.push({ stat: names[de[j]], op: names[de[j + 1]], value: de[j + 2] });
  if (row.length > i + 2) {
    u.isCursed = true;
    u.curseEffects = row[i + 2].map((n) => names[n]);
  }
  return u;
}

function recordsFromRaw(data) {
  const raw = Array.isArray(data) ? data : data && data.units;
  if (!Array.isArray(raw)) throw new Error("JSON must contain a list of units.");
  const out = [];
  for (const u of raw) {
    if (!u || typeof u !== "object" || !String(u.word || "").trim()) continue;
    out.push(new UnitRecord(u));
  }
  if (!out.length) throw new Error("No word records were found.");
  return out;
}

const parseWordList = (text) => new Set(text.split(/\r?\n/).map((l) => l.trim().toLowerCase()).filter(Boolean));

const DB = {
  base: [],
  extra: [],
  blacklist: new Set(),
  useBlacklist: true,
  units: [],
  tags: new Set(),
  maxLen: 15,

  refresh() {
    const records = [];
    const baseWords = new Set();
    const bl = this.useBlacklist ? this.blacklist : new Set();
    for (const r of this.base) {
      baseWords.add(r.word);
      if (!bl.has(r.word)) records.push(r);
    }
    const extraWords = new Set();
    for (const r of this.extra) {
      if (baseWords.has(r.word) || extraWords.has(r.word)) continue;
      extraWords.add(r.word);
      if (!bl.has(r.word)) records.push(r);
    }
    const tags = new Set();
    let maxLen = 2;
    for (const r of records) {
      r.tags.forEach((t) => tags.add(t));
      if (r.length > maxLen) maxLen = r.length;
    }
    this.units = records;
    this.tags = tags;
    this.maxLen = maxLen;
  },

  effectOptions() {
    const opts = [["", "Any effect / resource"]];
    const seen = new Set();
    for (const key of EFFECT_RESOURCE_ORDER) if (this.tags.has(key)) { opts.push([key, prettyName(key)]); seen.add(key); }
    for (const key of [...this.tags].filter((t) => !seen.has(t)).sort()) opts.push([key, prettyName(key)]);
    return opts;
  },

  search(q) {
    const avail = cleanRack(q.letters);
    const starts = cleanLetters(q.starts);
    const ends = cleanLetters(q.ends);
    const cont = cleanLetters(q.contains);
    const useRack = avail.length > 0;
    let wildcards = 0;
    const rackCounts = new Uint8Array(26);
    let rackMask = 0;
    for (const ch of avail) {
      if (ch === "?" || ch === "*") wildcards++;
      else { const o = ch.charCodeAt(0) - 97; rackCounts[o]++; rackMask |= 1 << o; }
    }
    const rackLen = avail.length;
    const contCounts = letterCounts(cont);
    const contIdx = [];
    for (let i = 0; i < 26; i++) if (contCounts[i]) contIdx.push(i);
    const favs = q.favorites || new Set();

    const results = [];
    for (const rec of this.units) {
      if (!q.includeTwo && rec.length === 2) continue;
      if (q.favoritesOnly && !favs.has(rec.word)) continue;
      if (!q.kinds.has(rec.kind)) continue;
      if (q.length !== null && rec.length !== q.length) continue;
      if (useRack) {
        if (rec.length > rackLen) continue;
        if (wildcards === 0 && rec.mask & ~rackMask) continue;
        let needed = 0;
        const c = rec.counts;
        for (let i = 0; i < 26; i++) {
          const diff = c[i] - rackCounts[i];
          if (diff > 0 && (needed += diff) > wildcards) break;
        }
        if (needed > wildcards) continue;
      }
      if (q.effect && !rec.tags.has(q.effect)) continue;
      const w = rec.word;
      if (starts && !w.startsWith(starts)) continue;
      if (ends && !w.endsWith(ends)) continue;
      if (cont) {
        if (q.inOrder && !w.includes(cont)) continue;
        if (q.exact) {
          if (contIdx.some((i) => rec.counts[i] !== contCounts[i])) continue;
        } else if (!q.inOrder) {
          if (contIdx.some((i) => rec.counts[i] < contCounts[i])) continue;
        }
      }
      results.push(rec);
    }
    sortResults(results, q.sortBy, q.descending, q.groupByLength);
    return results;
  },
};

const cmpStr = (a, b) => (a < b ? -1 : a > b ? 1 : 0);

function sortResults(results, sortBy, desc, grouped) {
  if (sortBy === "alphabetical") {
    if (grouped) {
      results.sort(desc ? (a, b) => b.length - a.length || cmpStr(a.word, b.word) : (a, b) => a.length - b.length || cmpStr(b.word, a.word));
    } else {
      results.sort(desc ? (a, b) => cmpStr(a.word, b.word) : (a, b) => cmpStr(b.word, a.word));
    }
    return;
  }
  if (sortBy === "points") {
    if (grouped) {
      results.sort(desc
        ? (a, b) => b.length - a.length || b.scrabble - a.scrabble || cmpStr(a.word, b.word)
        : (a, b) => a.length - b.length || a.scrabble - b.scrabble || cmpStr(a.word, b.word));
    } else {
      results.sort(desc
        ? (a, b) => b.scrabble - a.scrabble || b.length - a.length || cmpStr(a.word, b.word)
        : (a, b) => a.scrabble - b.scrabble || a.length - b.length || cmpStr(a.word, b.word));
    }
    return;
  }
  // Stat sort: units WITH the stat always come before units lacking it.
  const sign = desc ? -1 : 1;
  const vals = new Map(results.map((r) => [r, r.statValue(sortBy)]));
  results.sort((a, b) => {
    if (grouped) { const d = sign * (a.length - b.length); if (d) return d; }
    const va = vals.get(a), vb = vals.get(b);
    const ma = va === null || va === undefined ? 1 : 0, mb = vb === null || vb === undefined ? 1 : 0;
    if (ma !== mb) return ma - mb;
    const na = ma ? 0 : sign * va, nb = mb ? 0 : sign * vb;
    return na - nb || b.scrabble - a.scrabble || cmpStr(a.word, b.word);
  });
}

function sortCombined(results, baseResults, keys, desc, grouped) {
  const maxChanges = {};
  for (const key of keys) {
    let m = 0;
    for (const r of baseResults) { const v = r.positiveChange(key) || 0; if (v > m) m = v; }
    maxChanges[key] = m;
  }
  const score = new Map(results.map((r) => [r, keys.reduce((s, k) => (maxChanges[k] > 0 ? s + (r.positiveChange(k) || 0) / maxChanges[k] : s), 0)]));
  const sign = desc ? -1 : 1;
  results.sort((a, b) => {
    if (grouped) { const d = sign * (a.length - b.length); if (d) return d; }
    return sign * (score.get(a) - score.get(b)) || b.scrabble - a.scrabble || cmpStr(a.word, b.word);
  });
}

// ---------------------------------------------------------------------------
// Clever mode: combinations of words that use every available letter exactly
// ---------------------------------------------------------------------------
const CLEVER_LIMIT = 50000;

function findExactWordCombinations(records, available, includeTwo) {
  const rack = cleanRack(available);
  if (!rack) return { combos: [], truncated: false };
  const rackCounts = new Array(26).fill(0);
  let wildcards = 0;
  for (const ch of rack) {
    if (ch === "?" || ch === "*") wildcards++;
    else rackCounts[ch.charCodeAt(0) - 97]++;
  }
  const rackLen = rack.length;
  const minLen = includeTwo ? 2 : 3;
  const candidates = [];
  const byLetter = Array.from({ length: 26 }, () => []);
  const sorted = [...records].sort((a, b) => cmpStr(a.word, b.word));
  for (const rec of sorted) {
    if (rec.length < minLen || rec.length > rackLen || !/^[a-z]+$/.test(rec.word)) continue;
    let over = 0;
    for (let i = 0; i < 26; i++) over += Math.max(0, rec.counts[i] - rackCounts[i]);
    if (over > wildcards) continue;
    const idx = candidates.length;
    candidates.push(rec);
    for (let i = 0; i < 26; i++) if (rec.counts[i]) byLetter[i].push(idx);
  }
  if (!candidates.length) return { combos: [], truncated: false };

  const memo = new Map();
  let work = 0;
  const ABORT = {};

  function solve(remaining, wildLeft) {
    const key = remaining.join(",") + "|" + wildLeft;
    const cached = memo.get(key);
    if (cached) return cached;
    let remLen = wildLeft;
    for (const c of remaining) remLen += c;
    if (remLen === 0) return [[]];
    if (remLen < minLen) return [];

    let pivot = -1;
    for (let i = 0; i < 26; i++) {
      if (remaining[i] && (pivot < 0 || byLetter[i].length < byLetter[pivot].length)) pivot = i;
    }
    const indexes = pivot >= 0 ? byLetter[pivot] : candidates.map((_, i) => i);
    const found = new Map();
    for (const ci of indexes) {
      const rec = candidates[ci];
      if (rec.length > remLen) continue;
      const next = new Array(26);
      let need = 0;
      for (let i = 0; i < 26; i++) {
        const used = Math.min(remaining[i], rec.counts[i]);
        next[i] = remaining[i] - used;
        need += rec.counts[i] - used;
      }
      if (need > wildLeft) continue;
      for (const suffix of solve(next, wildLeft - need)) {
        const combo = [ci, ...suffix].sort((a, b) => a - b);
        found.set(combo.join(","), combo);
        if (++work > CLEVER_LIMIT * 20) throw ABORT;
      }
    }
    const result = [...found.values()].sort(cmpIntArrays);
    memo.set(key, result);
    return result;
  }

  try {
    let combos = solve(rackCounts, wildcards);
    const truncated = combos.length > CLEVER_LIMIT;
    if (truncated) combos = combos.slice(0, CLEVER_LIMIT);
    return { combos: combos.map((c) => c.map((i) => candidates[i])), truncated };
  } catch (e) {
    if (e === ABORT) return { combos: [], truncated: true };
    throw e;
  }
}

function cmpIntArrays(a, b) {
  const n = Math.min(a.length, b.length);
  for (let i = 0; i < n; i++) if (a[i] !== b[i]) return a[i] - b[i];
  return a.length - b.length;
}

// ---------------------------------------------------------------------------
// Persistence
// ---------------------------------------------------------------------------
function loadFavorites() {
  try {
    const list = JSON.parse(localStorage.getItem(FAVORITES_KEY) || "[]");
    return new Set(Array.isArray(list) ? list.filter((w) => typeof w === "string") : []);
  } catch { return new Set(); }
}

function saveFavorites() {
  try { localStorage.setItem(FAVORITES_KEY, JSON.stringify([...state.favorites].sort())); }
  catch { toast("Could not save favorites in this browser.", "err"); }
}

function loadPrefs() {
  try { return JSON.parse(localStorage.getItem(PREFS_KEY) || "{}") || {}; } catch { return {}; }
}

function savePrefs() {
  const p = {
    kinds: [...state.kinds], sortMode: state.sortMode, descending: state.descending,
    groupByLength: state.groupByLength, includeTwo: state.includeTwo, useBlacklist: DB.useBlacklist,
  };
  try { localStorage.setItem(PREFS_KEY, JSON.stringify(p)); } catch { /* ignore */ }
}

// ---------------------------------------------------------------------------
// UI state
// ---------------------------------------------------------------------------
const prefs = loadPrefs();
const state = {
  favorites: loadFavorites(),
  applied: { letters: "", contains: "", inOrder: false, exact: false, starts: "", ends: "", length: null, effect: "" },
  form: { inOrder: false, exact: false },
  kinds: new Set(Array.isArray(prefs.kinds) ? prefs.kinds : ["TOWER", "HARVESTER", "MOD"]),
  sortBy: "points",
  sortMode: prefs.sortMode === "alphabetical" ? "alphabetical" : "value",
  descending: prefs.descending !== false,
  groupByLength: !!prefs.groupByLength,
  includeTwo: !!prefs.includeTwo,
  clever: false,
  favoritesOnly: false,
  statFilters: new Set(),
  statCounts: new Array(STAT_FILTERS.length).fill(0),
  matches: [],
  combos: [],
  combosTruncated: false,
  visibleLimit: PAGE_SIZE,
  collapsed: new Set(), // "length:7" or "clever:2"
  groupLimits: new Map(),
  open: new Set(), // words whose detail panel is open
};
DB.useBlacklist = prefs.useBlacklist !== false;

function formSnapshot() {
  const len = $("sel-length").value;
  return {
    letters: $("inp-letters").value,
    contains: $("inp-contains").value,
    inOrder: state.form.inOrder,
    exact: state.form.exact,
    starts: $("inp-starts").value,
    ends: $("inp-ends").value,
    length: len === "ALL" ? null : parseInt(len, 10),
    effect: $("sel-effect").value,
  };
}

const sameQuery = (a, b) => Object.keys(a).every((k) => a[k] === b[k]);

// ---------------------------------------------------------------------------
// Search + render
// ---------------------------------------------------------------------------
function runSearch(resetPagination = true) {
  const q = state.applied;
  if (resetPagination) {
    state.visibleLimit = PAGE_SIZE;
    state.collapsed.clear();
    state.groupLimits.clear();
    state.open.clear();
  }
  const hasRack = cleanRack(q.letters).length > 0;
  if (!DB.units.length || (state.clever && !hasRack)) {
    state.matches = [];
    state.combos = [];
    state.combosTruncated = false;
    state.statCounts.fill(0);
    finishRender();
    return;
  }

  const baseSort = state.sortMode === "alphabetical" ? "alphabetical" : state.sortBy === "combined_stats" ? "points" : state.sortBy;
  const base = DB.search({
    ...q, favoritesOnly: state.favoritesOnly, favorites: state.favorites, kinds: state.kinds,
    sortBy: baseSort, descending: state.descending, groupByLength: state.groupByLength, includeTwo: state.includeTwo,
  });

  const counts = new Array(STAT_FILTERS.length).fill(0);
  for (const rec of base) {
    let m = rec.positiveMask;
    while (m) { const bit = m & -m; counts[31 - Math.clz32(bit)]++; m ^= bit; }
  }
  state.statCounts = counts;

  const selected = STAT_FILTERS.map(([k]) => k).filter((k) => state.statFilters.has(k));
  let matches = base;
  if (selected.length) {
    matches = base.filter((r) => selected.every((k) => r.hasPositive(k)));
    if (selected.length > 1 && state.sortBy === "combined_stats" && state.sortMode === "value") {
      sortCombined(matches, base, selected, state.descending, state.groupByLength);
    }
  }
  state.matches = matches;
  if (state.clever) {
    const { combos, truncated } = findExactWordCombinations(matches, q.letters, state.includeTwo);
    state.combos = combos;
    state.combosTruncated = truncated;
  } else {
    state.combos = [];
    state.combosTruncated = false;
  }
  finishRender();
}

function finishRender() {
  const n = state.clever ? state.combos.length : state.matches.length;
  const noun = state.clever ? (n === 1 ? "combination" : "combinations") : n === 1 ? "word" : "words";
  $("lbl-result-count").textContent = `${fmtInt(n)}${state.combosTruncated ? "+" : ""} ${noun} found`;
  renderStatFilters();
  renderBanner();
  renderResults();
  syncCollapseButton();
}

function renderStatFilters() {
  const el = $("stat-filters");
  el.innerHTML = STAT_FILTERS.map(([key, label, color], i) => {
    const on = state.statFilters.has(key);
    const count = state.statCounts[i];
    const bg = on ? color : lighten(color);
    return `<button type="button" class="chip${on ? " on" : ""}${count || on ? "" : " zero"}" data-stat="${key}" style="background:${bg}" aria-pressed="${on}"><span class="count">${fmtInt(count)}</span>${label}</button>`;
  }).join("");
}

function renderBanner() {
  const fav = $("lbl-fav-count"), cur = $("lbl-curse-count");
  if (!cleanRack($("inp-letters").value).length) { fav.hidden = cur.hidden = true; return; }
  const f = state.matches.filter((r) => state.favorites.has(r.word)).length;
  const c = state.matches.filter((r) => r.isCursed).length;
  fav.hidden = f === 0;
  fav.textContent = `♥ ${fmtInt(f)} ${f === 1 ? "favorite" : "favorites"} found`;
  cur.hidden = c === 0;
  cur.textContent = `☠ ${fmtInt(c)} ${c === 1 ? "cursed word" : "cursed words"}`;
}

function validWordFor(matches) {
  const exact = cleanRack(state.applied.letters);
  if (!exact || exact.includes("?") || exact.includes("*")) return null;
  return matches.find((r) => r.word === exact) || null;
}

function activeStat() {
  return state.sortMode === "value" && !["points", "combined_stats"].includes(state.sortBy) ? state.sortBy : null;
}

function groupTotals() {
  const totals = new Map();
  if (state.clever) {
    for (const c of state.combos) totals.set(`clever:${c.length}`, (totals.get(`clever:${c.length}`) || 0) + 1);
    return totals;
  }
  if (!state.groupByLength) return totals;
  const valid = validWordFor(state.matches);
  for (const r of state.matches) if (r !== valid) totals.set(`length:${r.length}`, (totals.get(`length:${r.length}`) || 0) + 1);
  return totals;
}

function groupVisible(key, total, groupCount) {
  const def = Math.max(1, Math.floor(PAGE_SIZE / Math.max(groupCount, 1)));
  return Math.min(total, state.groupLimits.has(key) ? state.groupLimits.get(key) : def);
}

function syncCollapseButton() {
  const btn = $("btn-collapse");
  const totals = groupTotals();
  if (!totals.size) { btn.hidden = true; return; }
  const allCollapsed = [...totals.keys()].every((k) => state.collapsed.has(k));
  btn.hidden = false;
  btn.textContent = allCollapsed ? "EXPAND GROUPS" : "COLLAPSE GROUPS";
  btn.classList.toggle("collapsed", allCollapsed);
}

function renderResults() {
  const el = $("results");
  const html = [];
  if (state.clever) {
    if (!state.combos.length) {
      const hasRack = cleanRack(state.applied.letters).length > 0;
      const msg = state.combosTruncated
        ? "Too many possible combinations. Add more filters or use fewer letters."
        : hasRack ? "No combination uses every available letter." : "Enter available letters and press FIND WORDS.";
      html.push(emptyHtml("No combinations found.", msg));
    } else {
      const byCount = new Map();
      for (const c of state.combos) {
        if (!byCount.has(c.length)) byCount.set(c.length, []);
        byCount.get(c.length).push(c);
      }
      const keys = [...byCount.keys()].sort((a, b) => a - b);
      for (const wc of keys) {
        const list = byCount.get(wc);
        const key = `clever:${wc}`;
        const vis = groupVisible(key, list.length, keys.length);
        const body = list.slice(0, vis).map((combo) =>
          `<div class="combo">${combo.map((r, i) => `${i ? '<span class="plus">+</span>' : ""}<span class="w c-${r.meta.cls}">${r.upper}</span><span class="k c-${r.meta.cls}">(${r.meta.display})</span>`).join("")}</div>`
        ).join("");
        html.push(groupHtml(key, `${wc} ${wc === 1 ? "WORD" : "WORDS"} PER COMBINATION`, vis, list.length, body));
      }
      if (state.combosTruncated) html.push(`<p class="small muted center">Showing the first ${fmtInt(CLEVER_LIMIT)} combinations.</p>`);
      html.push(groupedFooter("combinations"));
    }
    el.innerHTML = html.join("");
    return;
  }

  const matches = state.matches;
  if (!matches.length) {
    el.innerHTML = emptyHtml("No matching words found.", "Type letters above and press FIND WORDS, or adjust your filters.");
    return;
  }
  const stat = activeStat();
  const valid = validWordFor(matches);
  if (valid) html.push(`<div class="valid-word">${valid.upper} is a valid word</div>`, unitHtml(valid, stat));
  const rest = valid ? matches.filter((r) => r !== valid) : matches;

  if (state.groupByLength) {
    const groups = new Map();
    for (const r of rest) {
      if (!groups.has(r.length)) groups.set(r.length, []);
      groups.get(r.length).push(r);
    }
    for (const [len, items] of groups) {
      const key = `length:${len}`;
      const vis = groupVisible(key, items.length, groups.size);
      html.push(groupHtml(key, `${len} LETTER WORDS`, vis, items.length, items.slice(0, vis).map((r) => unitHtml(r, stat)).join("")));
    }
    html.push(groupedFooter("words"));
    el.innerHTML = html.join("");
    return;
  }

  const limit = state.visibleLimit - (valid ? 1 : 0);
  const visible = rest.slice(0, limit);
  for (const r of visible) html.push(unitHtml(r, stat));
  const remaining = rest.length - visible.length;
  if (remaining > 0) {
    html.push(`<div class="more-row"><span class="small bold muted">Showing ${fmtInt(visible.length + (valid ? 1 : 0))} of ${fmtInt(matches.length)} words</span>
      <button type="button" class="pill" data-action="more">SHOW ${fmtInt(Math.min(PAGE_SIZE, remaining))} MORE</button>
      ${remaining <= 600 ? `<button type="button" class="pill pill-blue" data-action="all">SHOW ALL (${fmtInt(matches.length)})</button>` : ""}</div>`);
  }
  el.innerHTML = html.join("");
}

function emptyHtml(title, msg) {
  return `<div class="empty"><div class="bold">${escapeHtml(title)}</div><div class="small muted">${escapeHtml(msg)}</div></div>`;
}

function groupHtml(key, title, visible, total, bodyHtml) {
  const collapsed = state.collapsed.has(key);
  const more = visible < total
    ? `<button type="button" class="pill center" data-action="group-more" data-group="${key}">SHOW ${fmtInt(Math.min(PAGE_SIZE, total - visible))} MORE</button>`
    : "";
  return `<div class="group"><button type="button" class="group-bar" data-group-toggle="${key}" aria-expanded="${!collapsed}">
    <span>${collapsed ? "▸" : "▾"}&nbsp; ${title}</span><span class="count">${visible < total ? `${fmtInt(visible)} / ` : ""}${fmtInt(total)}</span></button>
    <div class="group-body"${collapsed ? " hidden" : ""}>${bodyHtml}${more}</div></div>`;
}

function groupedFooter(noun) {
  const totals = groupTotals();
  if (!totals.size) return "";
  const gc = totals.size;
  let visible = 0, total = 0, next = 0;
  const step = Math.max(1, Math.floor(PAGE_SIZE / gc));
  for (const [k, t] of totals) {
    const v = groupVisible(k, t, gc);
    visible += v; total += t; next += Math.min(step, t - v);
  }
  if (total - visible <= 0) return "";
  return `<div class="more-row"><span class="small bold muted">Showing ${fmtInt(visible)} of ${fmtInt(total)} ${noun}</span>
    <button type="button" class="pill" data-action="groups-more">SHOW ${fmtInt(next)} MORE</button>
    ${total - visible <= 600 ? `<button type="button" class="pill pill-blue" data-action="groups-all">SHOW ALL (${fmtInt(total)})</button>` : ""}</div>`;
}

function unitHtml(rec, stat) {
  const m = rec.meta;
  const fav = state.favorites.has(rec.word);
  const open = state.open.has(rec.word);
  const preview = rec.previewStats(stat).map(([v, l, t], i) =>
    `${i ? '<span class="dot">·</span>' : ""}<span><span class="${t}">${escapeHtml(v)}</span>${l ? ` ${escapeHtml(l)}` : ""}</span>`).join("");
  return `<div class="unit k-${m.cls}${open ? " open" : ""}" data-word="${rec.word}" tabindex="0" role="button" aria-expanded="${open}">
    <div class="unit-top">
      <div class="unit-left">
        <div class="unit-title">
          <button type="button" class="heart${fav ? " on" : ""}" data-action="fav" title="${fav ? "Remove from" : "Add to"} favorites" aria-label="Favorite ${rec.word}">${fav ? "♥" : "♡"}</button>
          <span class="unit-word c-${m.cls}">${rec.upper}</span><span class="unit-kind c-${m.cls}">(${m.display})</span>
        </div>
        <div class="preview"${open ? " hidden" : ""}>${preview}</div>
      </div>
      <div class="unit-right">
        <div class="actions">
          <button type="button" class="mini" data-action="use" title="Copy word and remove its letters from Available Letters">USE</button>
          <a class="mini" href="https://onelook.com/?w=${encodeURIComponent(rec.word)}" target="_blank" rel="noopener" title="Look up the definition on OneLook" data-action="def">DEF</a>
        </div>
        <div class="pts-col">
          <div class="pts-row"><span class="pts">${rec.scrabble} PTS</span><span class="chev">${open ? "▾" : "▸"}</span></div>
          <span class="letters">${rec.length} letters</span>
        </div>
      </div>
    </div>
    ${open ? detailsHtml(rec) : ""}
  </div>`;
}

function cmpTone(val, def) {
  if (val === null || val === undefined) return "neutral";
  return val > def + 0.01 ? "pos" : val < def - 0.01 ? "neg" : "neutral";
}

function line(valHtml, label, extra = "") {
  return `<div class="line"><span class="pos">${escapeHtml(valHtml)}</span><span>${escapeHtml(label)}</span>${extra}</div>`;
}

function grid(items) {
  return `<div class="stat-grid">${items.map(([l, v, t]) => `<div><span class="lbl">${l}:</span> <span class="${t}">${escapeHtml(v)}</span></div>`).join("")}</div>`;
}

function detailsHtml(rec) {
  const h = [];
  if (rec.kind === "TOWER") {
    for (const [name, val] of rec.specials)
      h.push(line(`+${fmtNum(val, 2)}`, prettyName(name), name === "crit" ? `<span>(${formatCritSummary(val)})</span>` : ""));
    if (rec.isCursed && rec.curseEffects.length) {
      h.push(`<hr><span class="field-lbl">Possible curse effects</span>`);
      h.push(rec.curseEffects.map((e) => `<div class="line">${escapeHtml(prettyName(e))}</div>`).join(""));
    }
    h.push(`<hr><span class="field-lbl">Tower stats</span>`);
    const T = TOWER_DEFAULTS;
    h.push(grid([
      ["Damage", fmtNum(rec.damage, 2), cmpTone(rec.damage, T.damage)],
      ["DPS", fmtNum(rec.dps, 2), cmpTone(rec.dps, 5.5)],
      ["Attack Speed", `${fmtNum(rec.attackSpeed, 2)} (${fmtNum(rec.attacksPerSecond, 2)}/sec)`, cmpTone(rec.attackSpeed, T.attackSpeed)],
      ["Range", fmtNum(rec.range, 2), cmpTone(rec.range, T.range)],
      ["HP", fmtNum(rec.health, 1), cmpTone(rec.health, T.health)],
      ["Armor", fmtNum(rec.armor, 2), cmpTone(rec.armor, T.armor)],
    ]));
  } else if (rec.kind === "HARVESTER") {
    if (rec.harvestResources.length) {
      h.push(`<div class="row wrap" style="gap:16px">${rec.harvestResources.map((res) => {
        const [letter, fg, bg] = RESOURCE_COLORS[res] || ["?", "#111", "#ccc"];
        return `<span class="row gap-sm"><span class="res-dot" style="background:${bg};color:${fg}">${letter}</span><span class="bold small">Resource ${escapeHtml(titleCase(res))}</span></span>`;
      }).join("")}</div>`);
    }
    for (const [name, val] of rec.specials) h.push(line(`+${fmtNum(val, 2)}`, prettyName(name)));
    h.push(`<hr><span class="field-lbl">Harvester stats</span>`);
    const H = HARVESTER_DEFAULTS;
    const arm = rec.armor ?? 0;
    h.push(grid([
      ["Harvest Amount", fmtNum(rec.harvestAmount, 2), cmpTone(rec.harvestAmount, H.harvestAmount)],
      ["Harvest Speed", `${fmtNum(rec.harvestSpeed, 2)}/s (${fmtNum(rec.harvestInterval, 3)}s)`, cmpTone(rec.harvestSpeed, 1 / 3.2)],
      ["Harvest Rate", `${fmtNum(rec.harvestRate, 2)}/s`, cmpTone(rec.harvestRate, 2 / 3.2)],
      ["Range", fmtNum(rec.harvestRange, 2), cmpTone(rec.harvestRange, H.harvestRange)],
      ["Resource Types", String(rec.harvestTypes || 0), (rec.harvestTypes || 0) > 1 ? "pos" : "neutral"],
      ["HP", fmtNum(rec.health, 1), cmpTone(rec.health, H.health)],
      ["Armor", fmtNum(arm, 2), arm > 0.01 ? "pos" : "neutral"],
    ]));
  } else if (!rec.deltas.length) {
    h.push(`<div class="small muted">No modifier effects defined.</div>`);
  } else {
    for (const [stat, op, val] of rec.deltas) {
      const v = op === "mult" ? `×${fmtNum(val, 3)}` : `+${fmtNum(val, 2)}`;
      let extra = op ? `<span class="tiny muted">(${escapeHtml(op.toLowerCase() === "grant" ? "add" : op)})</span>` : "";
      if (stat === "crit") extra += `<span>(${formatCritSummary(val)})</span>`;
      h.push(line(v, prettyName(stat), extra));
    }
  }
  return `<div class="details">${h.join("")}</div>`;
}

/** Re-render while keeping the page from jumping. */
function rerenderKeepScroll() {
  const y = window.scrollY;
  renderResults();
  syncCollapseButton();
  window.scrollTo(0, y);
}

// ---------------------------------------------------------------------------
// Control syncing
// ---------------------------------------------------------------------------
function syncControls() {
  document.querySelectorAll("#kind-buttons .kind").forEach((b) => {
    const on = state.kinds.has(b.dataset.kind);
    b.classList.toggle("on", on);
    b.setAttribute("aria-pressed", on);
  });
  const sm = $("btn-sort-mode");
  sm.textContent = state.sortMode === "alphabetical" ? "ALPHABETICAL" : "VALUE";
  sm.classList.toggle("alpha", state.sortMode === "alphabetical");
  $("sel-order").value = state.descending ? "desc" : "asc";
  setToggle($("btn-group"), state.groupByLength);
  setToggle($("btn-two"), state.includeTwo);
  setToggle($("btn-clever"), state.clever);
  setToggle($("btn-favorites"), state.favoritesOnly);
  setToggle($("btn-in-order"), state.form.inOrder);
  setToggle($("btn-exact"), state.form.exact);
  $("chk-blacklist").checked = DB.useBlacklist;
  $("fav-total").textContent = `${fmtInt(state.favorites.size)} ${state.favorites.size === 1 ? "favorite" : "favorites"}`;
}

function setToggle(btn, on) {
  btn.classList.toggle("on", on);
  btn.setAttribute("aria-pressed", on);
}

function updateLetterCount() {
  const n = cleanRack($("inp-letters").value).length;
  $("lbl-letter-count").textContent = n === 0 ? "0 letters (browsing all)" : n === 1 ? "1 letter" : `${n} letters`;
}

function updatePending() {
  $("lbl-pending").hidden = sameQuery(formSnapshot(), state.applied) || !DB.units.length;
}

function fillDropdowns() {
  const lenSel = $("sel-length");
  const cur = lenSel.value || "ALL";
  const maxL = Math.max(DB.maxLen, 15);
  let opts = `<option value="ALL">All lengths</option>`;
  for (let n = maxL; n >= 2; n--) opts += `<option value="${n}">${n} letters</option>`;
  lenSel.innerHTML = opts;
  lenSel.value = [...lenSel.options].some((o) => o.value === cur) ? cur : "ALL";

  const effSel = $("sel-effect");
  const curE = effSel.value || "";
  effSel.innerHTML = DB.effectOptions().map(([v, l]) => `<option value="${escapeHtml(v)}">${escapeHtml(l)}</option>`).join("");
  effSel.value = [...effSel.options].some((o) => o.value === curE) ? curE : "";
}

function toast(msg, type = "") {
  const t = document.createElement("div");
  t.className = `toast ${type}`;
  t.textContent = msg;
  $("toasts").appendChild(t);
  setTimeout(() => t.remove(), 2400);
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    let ok = false;
    try { ok = document.execCommand("copy"); } catch { /* ignore */ }
    ta.remove();
    return ok;
  }
}

// ---------------------------------------------------------------------------
// Actions
// ---------------------------------------------------------------------------
function applyForm() {
  state.applied = formSnapshot();
  updatePending();
  runSearch(true);
}

function clearAll() {
  for (const id of ["inp-letters", "inp-contains", "inp-starts", "inp-ends"]) $(id).value = "";
  $("sel-length").value = "ALL";
  $("sel-effect").value = "";
  state.form.inOrder = state.form.exact = false;
  state.favoritesOnly = false;
  state.statFilters.clear();
  state.sortBy = "points";
  syncControls();
  updateLetterCount();
  applyForm();
  $("inp-letters").focus();
}

async function useWord(word) {
  const copied = await copyText(word);
  const source = $("inp-letters").value || state.applied.letters;
  const [remaining, removed] = consumeWordLetters(source, word);
  $("inp-letters").value = remaining;
  state.applied.letters = remaining;
  updateLetterCount();
  updatePending();
  if (removed > 0) toast(`Used ${word.toUpperCase()}${copied ? " — copied" : ""} & removed ${removed} letters (${remaining.length} left)`, "ok");
  else toast(copied ? `Copied ${word.toUpperCase()} to clipboard` : `${word.toUpperCase()}`);
  runSearch(true);
}

function toggleFavorite(word, btn) {
  const on = !state.favorites.has(word);
  if (on) state.favorites.add(word); else state.favorites.delete(word);
  saveFavorites();
  syncControls();
  renderBanner();
  if (state.favoritesOnly) {
    runSearch(false);
  } else if (btn) {
    btn.classList.toggle("on", on);
    btn.textContent = on ? "♥" : "♡";
    btn.title = `${on ? "Remove from" : "Add to"} favorites`;
  }
}

function toggleStatFilter(key) {
  if (state.statFilters.has(key)) state.statFilters.delete(key); else state.statFilters.add(key);
  state.sortMode = "value";
  const selected = STAT_FILTERS.map(([k]) => k).filter((k) => state.statFilters.has(k));
  state.sortBy = selected.length > 1 ? "combined_stats" : selected[0] || "points";
  syncControls();
  savePrefs();
  runSearch(true);
}

function toggleUnit(unitEl) {
  const word = unitEl.dataset.word;
  if (state.open.has(word)) state.open.delete(word); else state.open.add(word);
  const rec = state.matches.find((r) => r.word === word);
  if (!rec) return;
  const tmp = document.createElement("div");
  tmp.innerHTML = unitHtml(rec, activeStat());
  const fresh = tmp.firstElementChild;
  unitEl.replaceWith(fresh);
  fresh.focus({ preventScroll: true });
}

function toggleGroup(key) {
  if (state.collapsed.has(key)) state.collapsed.delete(key); else state.collapsed.add(key);
  rerenderKeepScroll();
}

function toggleAllGroups() {
  const totals = groupTotals();
  const all = [...totals.keys()].every((k) => state.collapsed.has(k));
  for (const k of totals.keys()) if (all) state.collapsed.delete(k); else state.collapsed.add(k);
  rerenderKeepScroll();
}

function groupsMore(showAll) {
  const totals = groupTotals();
  const gc = totals.size;
  const step = Math.max(1, Math.floor(PAGE_SIZE / gc));
  for (const [k, t] of totals) state.groupLimits.set(k, showAll ? t : Math.min(t, groupVisible(k, t, gc) + step));
  rerenderKeepScroll();
}

function groupMore(key) {
  const t = groupTotals().get(key) || 0;
  const gc = groupTotals().size;
  state.groupLimits.set(key, Math.min(t, groupVisible(key, t, gc) + PAGE_SIZE));
  rerenderKeepScroll();
}

// ---------------------------------------------------------------------------
// Files (import/export)
// ---------------------------------------------------------------------------
function readFile(input) {
  return new Promise((resolve, reject) => {
    const f = input.files && input.files[0];
    if (!f) return reject(new Error("No file selected"));
    const r = new FileReader();
    r.onload = () => resolve({ text: String(r.result), file: f });
    r.onerror = () => reject(r.error);
    r.readAsText(f);
  });
}

function formatSize(bytes) {
  let size = bytes;
  for (const u of ["B", "KB", "MB", "GB"]) {
    if (size < 1024 || u === "GB") return u === "B" ? `${size} B` : `${size.toFixed(1)} ${u}`;
    size /= 1024;
  }
  return "";
}

function setStatus(id, text, cls) {
  const el = $(id);
  el.textContent = text;
  el.className = `status ${cls || ""}`;
}

function afterDataChange() {
  DB.refresh();
  fillDropdowns();
  state.applied = formSnapshot();
  updatePending();
  runSearch(true);
}

function bindFileInputs() {
  $("file-units").addEventListener("change", async (e) => {
    try {
      const { text, file } = await readFile(e.target);
      DB.base = recordsFromRaw(JSON.parse(text));
      setStatus("status-units", `${file.name} · ${formatSize(file.size)}`, "custom");
      afterDataChange();
      toast(`Loaded ${fmtInt(DB.base.length)} units`, "ok");
    } catch (err) { setStatus("status-units", "failed to load", "err"); toast(`Could not load units: ${err.message}`, "err"); }
    e.target.value = "";
  });
  $("file-cursed").addEventListener("change", async (e) => {
    try {
      const { text, file } = await readFile(e.target);
      const recs = recordsFromRaw(JSON.parse(text));
      if (!recs.some((r) => r.isCursed)) throw new Error("No cursed towers were found.");
      DB.extra = recs;
      setStatus("status-cursed", `${file.name} · ${formatSize(file.size)}`, "custom");
      afterDataChange();
      toast(`Loaded ${fmtInt(recs.length)} cursed words`, "ok");
    } catch (err) { setStatus("status-cursed", "failed to load", "err"); toast(`Could not load cursed words: ${err.message}`, "err"); }
    e.target.value = "";
  });
  $("file-blacklist").addEventListener("change", async (e) => {
    try {
      const { text, file } = await readFile(e.target);
      DB.blacklist = parseWordList(text);
      setStatus("status-blacklist", `${file.name} · ${formatSize(file.size)}`, "custom");
      afterDataChange();
      toast(`Blacklist has ${fmtInt(DB.blacklist.size)} words`, "ok");
    } catch (err) { toast(`Could not load blacklist: ${err.message}`, "err"); }
    e.target.value = "";
  });
  $("file-user-data").addEventListener("change", async (e) => {
    try {
      const { text } = await readFile(e.target);
      let words;
      try {
        const data = JSON.parse(text);
        const list = Array.isArray(data) ? data : data && data.favorites;
        if (!Array.isArray(list) || list.some((w) => typeof w !== "string")) throw new Error("'favorites' must be a list of words.");
        words = list;
      } catch (jsonErr) {
        if (text.trim().startsWith("{") || text.trim().startsWith("[")) throw jsonErr;
        words = [...parseWordList(text)]; // legacy favorites.txt
      }
      let added = 0;
      for (const w of words) {
        const clean = w.trim().toLowerCase();
        if (clean && !state.favorites.has(clean)) { state.favorites.add(clean); added++; }
      }
      saveFavorites();
      syncControls();
      runSearch(false);
      toast(`Imported ${fmtInt(added)} new favorites`, "ok");
    } catch (err) { toast(`Could not import favorites: ${err.message}`, "err"); }
    e.target.value = "";
  });
  $("btn-export").addEventListener("click", () => {
    const data = { version: 1, favorites: [...state.favorites].sort() };
    const blob = new Blob([JSON.stringify(data, null, 2) + "\n"], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "user_data.json";
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  });
  $("btn-clear-favs").addEventListener("click", () => {
    if (!state.favorites.size || !confirm(`Remove all ${state.favorites.size} favorites?`)) return;
    state.favorites.clear();
    saveFavorites();
    syncControls();
    runSearch(false);
  });
  $("chk-blacklist").addEventListener("change", (e) => {
    DB.useBlacklist = e.target.checked;
    savePrefs();
    afterDataChange();
  });
}

// ---------------------------------------------------------------------------
// Event wiring
// ---------------------------------------------------------------------------
function bindEvents() {
  $("search-form").addEventListener("submit", (e) => { e.preventDefault(); applyForm(); });
  $("btn-clear").addEventListener("click", clearAll);

  $("inp-letters").addEventListener("input", () => { updateLetterCount(); updatePending(); });
  for (const id of ["inp-contains", "inp-starts", "inp-ends", "sel-effect"]) {
    $(id).addEventListener("input", updatePending);
    $(id).addEventListener("change", updatePending);
  }
  $("sel-length").addEventListener("change", () => {
    const v = $("sel-length").value;
    state.applied.length = v === "ALL" ? null : parseInt(v, 10);
    updatePending();
    runSearch(true);
  });
  $("btn-in-order").addEventListener("click", () => { state.form.inOrder = !state.form.inOrder; syncControls(); updatePending(); });
  $("btn-exact").addEventListener("click", () => { state.form.exact = !state.form.exact; syncControls(); updatePending(); });

  $("kind-buttons").addEventListener("click", (e) => {
    const b = e.target.closest("[data-kind]");
    if (!b) return;
    const k = b.dataset.kind;
    if (state.kinds.has(k)) state.kinds.delete(k); else state.kinds.add(k);
    syncControls(); savePrefs(); runSearch(true);
  });
  $("btn-sort-mode").addEventListener("click", () => {
    state.sortMode = state.sortMode === "value" ? "alphabetical" : "value";
    syncControls(); savePrefs(); runSearch(true);
  });
  $("sel-order").addEventListener("change", (e) => { state.descending = e.target.value === "desc"; savePrefs(); runSearch(true); });
  $("btn-group").addEventListener("click", () => { state.groupByLength = !state.groupByLength; syncControls(); savePrefs(); runSearch(true); });
  $("btn-collapse").addEventListener("click", toggleAllGroups);
  $("btn-two").addEventListener("click", () => { state.includeTwo = !state.includeTwo; syncControls(); savePrefs(); runSearch(true); });
  $("btn-clever").addEventListener("click", () => {
    state.clever = !state.clever;
    syncControls();
    // Clever mode can take a moment on big racks; let the button repaint first.
    $("lbl-result-count").textContent = state.clever ? "Searching combinations…" : $("lbl-result-count").textContent;
    setTimeout(() => runSearch(true), 10);
  });
  $("btn-favorites").addEventListener("click", () => { state.favoritesOnly = !state.favoritesOnly; syncControls(); runSearch(true); });

  $("stat-filters").addEventListener("click", (e) => {
    const b = e.target.closest("[data-stat]");
    if (b) toggleStatFilter(b.dataset.stat);
  });

  const results = $("results");
  results.addEventListener("click", (e) => {
    const action = e.target.closest("[data-action]");
    if (action) {
      const a = action.dataset.action;
      const unit = action.closest(".unit");
      if (a === "def") return; // plain link
      e.preventDefault();
      if (a === "fav" && unit) return toggleFavorite(unit.dataset.word, action);
      if (a === "use" && unit) return useWord(unit.dataset.word);
      if (a === "more") { state.visibleLimit += PAGE_SIZE; return rerenderKeepScroll(); }
      if (a === "all") { state.visibleLimit = state.matches.length + 1; return rerenderKeepScroll(); }
      if (a === "groups-more") return groupsMore(false);
      if (a === "groups-all") return groupsMore(true);
      if (a === "group-more") return groupMore(action.dataset.group);
      return;
    }
    const gt = e.target.closest("[data-group-toggle]");
    if (gt) return toggleGroup(gt.dataset.groupToggle);
    if (e.target.closest(".details")) return; // allow selecting text in details
    const unit = e.target.closest(".unit");
    if (unit) toggleUnit(unit);
  });
  results.addEventListener("keydown", (e) => {
    if ((e.key === "Enter" || e.key === " ") && e.target.classList.contains("unit")) {
      e.preventDefault();
      toggleUnit(e.target);
    }
  });

  $("btn-settings").addEventListener("click", () => { syncControls(); $("dlg-settings").showModal(); });
  $("btn-help").addEventListener("click", () => $("dlg-help").showModal());
  for (const d of document.querySelectorAll("dialog")) {
    d.addEventListener("click", (e) => { if (e.target === d) d.close(); });
  }
  bindFileInputs();
}

// ---------------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------------
async function boot() {
  bindEvents();
  syncControls();
  try {
    const [wordsRes, blRes] = await Promise.all([fetch("data/words.json"), fetch("data/blacklist.txt")]);
    if (!wordsRes.ok) throw new Error(`HTTP ${wordsRes.status} while loading data/words.json`);
    $("loading-detail").textContent = "Preparing words…";
    const data = await wordsRes.json();
    if (blRes.ok) DB.blacklist = parseWordList(await blRes.text());
    await new Promise((r) => setTimeout(r, 0));
    DB.base = data.units.map((row) => new UnitRecord(unpackRow(row, data.names)));
    DB.extra = data.cursed.map((row) => new UnitRecord(unpackRow(row, data.names)));
    DB.refresh();
  } catch (err) {
    const box = $("loading");
    box.classList.add("error");
    box.innerHTML = `<div><div class="bold">Could not load the word list.</div><div class="small">${escapeHtml(err.message)}. If you opened index.html directly from disk, serve the folder with a local web server instead (see README).</div></div>`;
    return;
  }
  fillDropdowns();
  $("loading").hidden = true;
  $("controls").hidden = false;
  $("results-panel").hidden = false;
  state.applied = formSnapshot();
  runSearch(true);
  $("inp-letters").focus();
}

boot();
