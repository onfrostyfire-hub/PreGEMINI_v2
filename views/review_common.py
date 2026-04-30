from __future__ import annotations

from datetime import date, datetime, timedelta
import csv
import hashlib
import html
import os
import json
from typing import Dict, Iterable, List, Tuple

import streamlit as st

import poker_utils as utils


SECTIONS = ["Preflop", "Postflop", "Fish"]
PERIODS = ["Today", "Late", "Next 7 Days", "Active Spots"]
MIN_REVIEW_HANDS = 100
FISH_HISTORY_COLUMNS = [
    "Date",
    "Fish_Type",
    "Position",
    "Action_Line",
    "Texture",
    "Runout",
    "Hand",
    "UserAction",
    "CorrectAction",
    "Result",
    "XP",
]


def esc(value) -> str:
    return html.escape(str(value or ""))


def stable_key(prefix: str, value: str) -> str:
    digest = hashlib.md5(value.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


def spot_id(section: str, key: str) -> str:
    return f"{section}::{key}"


def parse_date(value: str):
    if not value:
        return None
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except Exception:
        return None


def _ensure_review_settings(raw: dict) -> dict:
    review = raw.get("review_settings", {})
    if not isinstance(review, dict):
        review = {}
    review.setdefault("hidden_sections", [])
    review.setdefault("hidden_spots", [])
    review.setdefault("min_hands", MIN_REVIEW_HANDS)
    return review


def load_review_settings() -> Tuple[dict, dict]:
    settings = utils.load_user_settings()
    review = _ensure_review_settings(settings)
    settings["review_settings"] = review
    return settings, review


def save_review_settings(review: dict) -> None:
    settings = utils.load_user_settings()
    settings["review_settings"] = _ensure_review_settings({"review_settings": review})
    utils.save_user_settings(settings)


def hide_spot(section: str, key: str) -> None:
    _, review = load_review_settings()
    hidden = set(review.get("hidden_spots", []))
    hidden.add(spot_id(section, key))
    review["hidden_spots"] = sorted(hidden)
    save_review_settings(review)


def unhide_all_spots() -> None:
    _, review = load_review_settings()
    review["hidden_spots"] = []
    save_review_settings(review)


def _load_postflop_flat() -> Dict[str, dict]:
    db = {}
    pf_dir = "postflop_data" if os.path.exists("postflop_data") else "spots_data"
    if not os.path.exists(pf_dir):
        return db
    for file_name in os.listdir(pf_dir):
        if not file_name.endswith(".json"):
            continue
        path = os.path.join(pf_dir, file_name)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and "spots" in data:
                db.update(data.get("spots", {}))
            elif isinstance(data, dict):
                db.update(data)
        except Exception:
            continue
    return db


@st.cache_data(ttl=0)
def load_catalogs() -> Dict[str, Dict[str, dict]]:
    catalogs = {"Preflop": {}, "Postflop": {}, "Fish": {}}

    try:
        ranges_db = utils.load_ranges()
        for source, scenarios in ranges_db.items():
            for scenario, spots in scenarios.items():
                for name, data in spots.items():
                    key = f"{source}|{scenario}|{name}"
                    catalogs["Preflop"][key] = {
                        "section": "Preflop",
                        "key": key,
                        "display": name,
                        "line": scenario,
                        "subline": source,
                        "detail": f"{source} | {scenario}",
                        "raw": data,
                    }
    except Exception:
        pass

    try:
        for key, data in _load_postflop_flat().items():
            parts = [p.strip() for p in key.split("|")]
            if len(parts) == 5:
                spot, hero, street, branch, board = parts
                display = board
                detail = f"{spot} | {hero} | {street} | {branch}"
                line = branch
                subline = spot
            else:
                display = key
                detail = "Postflop"
                line = "Postflop"
                subline = ""
            catalogs["Postflop"][key] = {
                "section": "Postflop",
                "key": key,
                "display": display,
                "line": line,
                "subline": subline,
                "detail": detail,
                "raw": data,
            }
    except Exception:
        pass

    try:
        fish_db = utils.load_fish_data()
        for fish_type, board_data in fish_db.items():
            for texture, pos_data in board_data.items():
                for position, line_data in pos_data.items():
                    for action_line, runouts in line_data.items():
                        for runout, data in runouts.items():
                            setup = data.get("setup", {}) if isinstance(data, dict) else {}
                            line_label = setup.get("spot_label", action_line)
                            key = f"{fish_type}|{texture}|{position}|{action_line}|{runout}"
                            catalogs["Fish"][key] = {
                                "section": "Fish",
                                "key": key,
                                "display": runout,
                                "line": line_label,
                                "subline": fish_type,
                                "detail": f"{fish_type} | {position} | {line_label}",
                                "raw": data,
                            }
    except Exception:
        pass

    return catalogs


def _merge_mastery(*stats_objects: dict) -> dict:
    merged = {}
    for stats in stats_objects:
        if not isinstance(stats, dict):
            continue
        mastery = stats.get("spot_mastery", {})
        if not isinstance(mastery, dict):
            continue
        for key, value in mastery.items():
            if not isinstance(value, dict):
                continue
            old = merged.get(key, {})
            old_total = int(old.get("t", 0) or 0)
            new_total = int(value.get("t", 0) or 0)
            if new_total >= old_total:
                merged[key] = dict(value)
    return merged


def _date_from_history_value(value: str):
    text = str(value or "").strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d.%m.%Y %H:%M:%S", "%d.%m.%Y"):
        try:
            return datetime.strptime(text[:19] if "%H" in fmt else text[:10], fmt).date()
        except Exception:
            pass
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except Exception:
        return None


def _result_bit(value) -> str:
    try:
        return "1" if int(float(str(value or "0").strip())) == 1 else "0"
    except Exception:
        return "0"


def _rows_from_values(values, default_headers):
    if not values:
        return []
    first = [str(v).strip() for v in values[0]]
    if first and first[0] == "Date":
        headers = first
        rows = values[1:]
    else:
        headers = default_headers
        rows = values
    width = len(headers)
    out = []
    for row in rows:
        normalized = list(row) + [""] * max(0, width - len(row))
        out.append(dict(zip(headers, normalized[:width])))
    return out


def _load_fish_history_rows():
    rows = []
    try:
        sheets = utils.get_worksheets()
        if "FishHistory" in sheets:
            rows.extend(_rows_from_values(sheets["FishHistory"].get_all_values(), FISH_HISTORY_COLUMNS))
    except Exception:
        pass
    if rows:
        return rows
    if os.path.exists("fish_history.csv"):
        try:
            with open("fish_history.csv", "r", encoding="utf-8-sig", newline="") as f:
                raw = list(csv.reader(f))
            rows.extend(_rows_from_values(raw, FISH_HISTORY_COLUMNS))
        except Exception:
            pass
    return rows


def _fish_key_from_history(row: dict) -> str:
    fish_type = row.get("Fish_Type", row.get("FishType", row.get("Fish Type", "")))
    action_line = row.get("Action_Line", row.get("Action Line", ""))
    return "|".join(
        str(value or "").strip()
        for value in (fish_type, row.get("Texture", ""), row.get("Position", ""), action_line, row.get("Runout", ""))
    )


def _mastery_from_fish_history() -> dict:
    mastery = {}
    for row in _load_fish_history_rows():
        key = _fish_key_from_history(row)
        if key.count("|") != 4 or not key.replace("|", "").strip():
            continue
        item = mastery.setdefault(key, {"t": 0, "h": "", "d": ""})
        item["t"] = int(item.get("t", 0) or 0) + 1
        item["h"] = str(item.get("h", "") or "") + _result_bit(row.get("Result", "0"))
        row_date = _date_from_history_value(row.get("Date", ""))
        if row_date:
            old_date = parse_date(item.get("d", ""))
            if not old_date or row_date >= old_date:
                item["d"] = row_date.strftime("%Y-%m-%d")
    return mastery


def load_section_mastery(section: str) -> dict:
    if section == "Preflop":
        return _merge_mastery(utils.load_user_stats())
    if section == "Postflop":
        from_file = utils.load_user_stats(is_postflop=True)
        from_settings = utils.load_user_settings(is_postflop=True).get("stats", {})
        return _merge_mastery(from_file, from_settings)
    if section == "Fish":
        from_file = utils.load_user_stats(is_fish=True)
        from_settings = utils.load_user_settings(is_fish=True).get("stats", {})
        from_history = {"spot_mastery": _mastery_from_fish_history()}
        return _merge_mastery(from_file, from_settings, from_history)
    return {}


def interval_days(section: str, mastery: dict) -> int:
    info = utils.get_spot_mastery_info(mastery, is_fish=(section == "Fish"))
    rank = int(info.get("rank", 0) or 0)
    total = int(info.get("total", 0) or 0)
    intervals = {0: 1, 1: 4, 2: 10, 3: 30, 4: 60, 5: 180}
    if rank >= 5:
        if section == "Fish" and total >= 1500:
            return 360
        if section != "Fish" and total >= 5000:
            return 360
    return intervals.get(rank, 1)


def accuracy_from_history(hist: str) -> float:
    if not hist:
        return 0.0
    return round((hist.count("1") / len(hist)) * 100, 1)


def build_review_spots() -> List[dict]:
    catalogs = load_catalogs()
    _, review = load_review_settings()
    hidden_sections = set(review.get("hidden_sections", []))
    hidden_spots = set(review.get("hidden_spots", []))
    min_hands = int(review.get("min_hands", MIN_REVIEW_HANDS) or MIN_REVIEW_HANDS)
    today = date.today()
    results = []

    for section in SECTIONS:
        if section in hidden_sections:
            continue
        mastery_map = load_section_mastery(section)
        for key, meta in catalogs.get(section, {}).items():
            if spot_id(section, key) in hidden_spots:
                continue
            mastery = mastery_map.get(key, {})
            total = int(mastery.get("t", 0) or 0)
            if total < min_hands:
                continue

            info = utils.get_spot_mastery_info(mastery, is_fish=(section == "Fish"))
            hist = str(mastery.get("h", "") or "")
            last = parse_date(mastery.get("d", ""))
            interval = interval_days(section, mastery)
            due = (last + timedelta(days=interval)) if last else today
            delta = (today - due).days
            late_days = max(0, delta)
            days_until = (due - today).days

            if due < today:
                bucket = "Late"
            elif due == today:
                bucket = "Today"
            elif due <= today + timedelta(days=7):
                bucket = "Next 7 Days"
            else:
                bucket = "Active Spots"

            acc = accuracy_from_history(hist)
            weak_boost = max(0.0, (94.0 - acc) / 12.0) if hist else 0.5
            priority = late_days * 10.0
            if due <= today:
                priority += 8.0
            priority += weak_boost
            if not last:
                priority += 20.0

            results.append({
                **meta,
                "mastery": mastery,
                "total": total,
                "accuracy": acc,
                "status": info.get("name", "Sandbox"),
                "status_icon": info.get("icon", ""),
                "rank": int(info.get("rank", 0) or 0),
                "next_target": int(info.get("next_target", 0) or 0),
                "last_date": last,
                "due_date": due,
                "interval_days": interval,
                "late_days": late_days,
                "days_until": days_until,
                "bucket": bucket,
                "priority": priority,
            })

    results.sort(key=lambda x: (-x["priority"], x["due_date"], x["section"], x["display"]))
    return results


def filter_spots(spots: List[dict], sections: Iterable[str], period: str, search: str = "") -> List[dict]:
    section_set = set(sections or SECTIONS)
    search_value = (search or "").lower().strip()
    filtered = []
    for spot in spots:
        if spot["section"] not in section_set:
            continue
        if period != "Active Spots" and spot["bucket"] != period:
            continue
        if search_value:
            hay = " ".join([spot["display"], spot["detail"], spot["line"], spot["section"]]).lower()
            if search_value not in hay:
                continue
        filtered.append(spot)
    return filtered


def bucket_counts(spots: List[dict]) -> dict:
    counts = {p: 0 for p in PERIODS}
    for spot in spots:
        if spot["bucket"] != "Active Spots":
            counts[spot["bucket"]] += 1
        counts["Active Spots"] += 1
    return counts


def section_counts(spots: List[dict]) -> dict:
    counts = {s: 0 for s in SECTIONS}
    for spot in spots:
        counts[spot["section"]] += 1
    return counts


def calendar_counts(spots: List[dict], days: int = 7) -> List[dict]:
    today = date.today()
    out = []
    for i in range(days):
        current = today + timedelta(days=i)
        due = [s for s in spots if s["due_date"] == current]
        by_section = section_counts(due)
        out.append({
            "date": current,
            "label": current.strftime("%a"),
            "count": len(due),
            "sections": by_section,
        })
    return out


def split_by_section(spots_or_keys) -> Dict[str, List[str]]:
    grouped = {s: [] for s in SECTIONS}
    for item in spots_or_keys:
        if isinstance(item, dict):
            grouped[item["section"]].append(item["key"])
        elif isinstance(item, (tuple, list)) and len(item) == 2:
            grouped[item[0]].append(item[1])
    return {section: keys for section, keys in grouped.items() if keys}


def _apply_preflop_filters(keys: List[str]) -> None:
    settings = utils.load_user_settings()
    scenarios = []
    for key in keys:
        parts = key.split("|")
        if len(parts) >= 3 and parts[1] not in scenarios:
            scenarios.append(parts[1])
    settings["scenarios"] = scenarios
    settings["spots"] = keys
    utils.save_user_settings(settings)


def _apply_postflop_filters(keys: List[str]) -> None:
    settings = utils.load_user_settings(is_postflop=True)
    spots, heroes, streets, branches = [], [], [], []
    for key in keys:
        parts = [p.strip() for p in key.split("|")]
        if len(parts) != 5:
            continue
        spot, hero, street, branch, _board = parts
        for target, value in [(spots, spot), (heroes, hero), (streets, street), (branches, branch)]:
            if value not in target:
                target.append(value)
    settings["pf_sel_spots"] = spots
    settings["pf_sel_heroes"] = heroes
    settings["pf_sel_streets"] = streets
    settings["pf_sel_branches"] = branches
    settings["pf_spots"] = keys
    utils.save_user_settings(settings, is_postflop=True)


def _apply_fish_filters(keys: List[str]) -> None:
    settings = utils.load_user_settings(is_fish=True)
    vpips, boards, positions, lines = [], [], [], []
    for key in keys:
        parts = key.split("|")
        if len(parts) != 5:
            continue
        vpip, board, pos, line, _runout = parts
        for target, value in [(vpips, vpip), (boards, board), (positions, pos), (lines, line)]:
            if value not in target:
                target.append(value)
    settings["fish_sel_vpips"] = vpips
    settings["fish_sel_boards"] = boards
    settings["fish_sel_pos"] = positions
    settings["fish_sel_lines"] = lines
    settings["fish_spots"] = keys
    settings["fish_due_mode"] = False
    utils.save_user_settings(settings, is_fish=True)


def start_review_training(section: str, keys: List[str], label: str = "Review") -> None:
    keys = [k for k in keys if k]
    if not keys:
        st.warning("No spots selected for Review training.")
        return

    if section == "Preflop":
        _apply_preflop_filters(keys)
        st.session_state.hand = None
        st.session_state.current_spot_key = None
    elif section == "Postflop":
        _apply_postflop_filters(keys)
        st.session_state.pf_hand = None
        st.session_state.pf_current_spot_key = None
    elif section == "Fish":
        _apply_fish_filters(keys)
        st.session_state.fish_hand = None
        st.session_state.fish_current_spot_key = None

    st.session_state.review_training = {
        "section": section,
        "spot_keys": keys,
        "label": label,
        "started_at": datetime.now().isoformat(timespec="seconds"),
    }
    st.session_state.actual_app_mode = section
    st.rerun()


def request_grouped_launch(label: str, spots: List[dict]) -> None:
    grouped = split_by_section(spots)
    if not grouped:
        st.warning("No eligible spots in this queue.")
        return
    if len(grouped) == 1:
        section, keys = next(iter(grouped.items()))
        start_review_training(section, keys, label)
        return
    st.session_state.review_launch_choice = {"label": label, "groups": grouped}
    st.rerun()


def clear_review_training() -> None:
    st.session_state.pop("review_training", None)


def review_context_for(section: str) -> dict:
    ctx = st.session_state.get("review_training", {})
    if isinstance(ctx, dict) and ctx.get("section") == section:
        return ctx
    return {}
