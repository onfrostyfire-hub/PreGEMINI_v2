import json
import os
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

import poker_utils as utils


PRE_HU_MIGRATION_MAP = {
    "SB pfr": "HU @ SB pfr",
    "BB def vs PFR": "HU @ BB def vs PFR",
    "SB def vs 3bet BB": "HU @ SB def vs 3bet",
    "SB def vs 3bet": "HU @ SB def vs 3bet",
    "BB def vs 4bet": "HU @ BB def vs 4bet",
}

LEGACY_SPOT_RENAME_MAP = {
    "BUvsCO": "3bet BUvsCO",
    "SBvsCO": "3bet SBvsCO",
    "SBvsBU": "3bet SBvsBU",
    "BBvsCO": "3bet BBvsCO",
    "BBvsBU": "3bet BBvsBU",
    "BBvsSB": "3bet BBvsSB",
    **PRE_HU_MIGRATION_MAP,
}

PRE_SCENARIO_ORDER = [
    "Open Raise",
    "3bet",
    "BB def vs PFR",
    "Def vs 3bet",
    "Def vs 4bet",
    "Open 4bet",
    "HU",
]


def _normalize_text(value):
    return " ".join(str(value or "").replace("\xa0", " ").split()).strip()


def _slugify(value):
    cleaned = []
    for ch in _normalize_text(value).lower():
        if ch.isalnum():
            cleaned.append(ch)
        else:
            cleaned.append("_")
    return "".join(cleaned).strip("_") or "item"


def _scenario_sort_key(name):
    norm = _normalize_text(name)
    if norm in PRE_SCENARIO_ORDER:
        return (PRE_SCENARIO_ORDER.index(norm), norm.lower())
    return (len(PRE_SCENARIO_ORDER), norm.lower())


def _spot_sort_key(spot_name, catalog, is_postflop):
    meta = catalog.get(spot_name, {})
    if is_postflop:
        return (
            _normalize_text(meta.get("spot", "")),
            _normalize_text(meta.get("hero", "")),
            _normalize_text(meta.get("street", "")),
            _normalize_text(meta.get("branch", "")),
            _normalize_text(meta.get("display_name", spot_name)),
        )
    return (
        _scenario_sort_key(meta.get("scenario", "")),
        _normalize_text(meta.get("display_name", spot_name)),
    )


@st.cache_data(ttl=0)
def load_preflop_catalog():
    catalog = {}
    aliases = {}
    ranges_db = utils.load_ranges()

    for source, scenario_dict in ranges_db.items():
        for scenario, spots_dict in scenario_dict.items():
            for spot_name in spots_dict.keys():
                canonical_name = _normalize_text(spot_name)
                catalog[canonical_name] = {
                    "display_name": canonical_name,
                    "source": _normalize_text(source),
                    "scenario": _normalize_text(scenario),
                }
                aliases[canonical_name.lower()] = canonical_name

                if canonical_name.startswith("3bet "):
                    short_name = canonical_name.replace("3bet ", "", 1)
                    aliases[_normalize_text(short_name).lower()] = canonical_name

    for old_name, new_name in PRE_HU_MIGRATION_MAP.items():
        aliases[_normalize_text(old_name).lower()] = _normalize_text(new_name)

    return catalog, aliases


@st.cache_data(ttl=0)
def load_postflop_catalog():
    catalog = {}
    aliases = {}
    pf_dir = "postflop_data" if os.path.exists("postflop_data") else "spots_data"

    if not os.path.exists(pf_dir):
        return catalog, aliases

    for file_name in sorted(os.listdir(pf_dir)):
        if not file_name.endswith(".json"):
            continue

        file_path = os.path.join(pf_dir, file_name)
        try:
            with open(file_path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except Exception:
            continue

        raw_spots = data.get("spots", data) if isinstance(data, dict) else {}
        if not isinstance(raw_spots, dict):
            continue

        source_name = _normalize_text(
            data.get("source", os.path.splitext(file_name)[0].replace("_", " "))
            if isinstance(data, dict)
            else os.path.splitext(file_name)[0].replace("_", " ")
        )
        scenario_name = _normalize_text(data.get("scenario", "Postflop")) if isinstance(data, dict) else "Postflop"

        for spot_name in raw_spots.keys():
            canonical_name = _normalize_text(spot_name)
            parts = [part.strip() for part in canonical_name.split("|")]
            catalog[canonical_name] = {
                "display_name": canonical_name,
                "source": source_name,
                "scenario": scenario_name,
                "spot": parts[0] if len(parts) > 0 else canonical_name,
                "hero": parts[1] if len(parts) > 1 else "Unknown",
                "street": parts[2] if len(parts) > 2 else "Unknown",
                "branch": parts[3] if len(parts) > 3 else "General",
            }
            aliases[canonical_name.lower()] = canonical_name

    return catalog, aliases


def get_spot_catalog(is_postflop):
    if is_postflop:
        return load_postflop_catalog()
    return load_preflop_catalog()


def canonicalize_history_spots(df, is_postflop):
    if df.empty or "Spot" not in df.columns:
        return df

    _, aliases = get_spot_catalog(is_postflop)
    mapped_df = df.copy()

    def _to_canonical(value):
        clean_value = _normalize_text(value)
        return aliases.get(clean_value.lower(), clean_value)

    mapped_df["Spot"] = mapped_df["Spot"].apply(_to_canonical)
    if not is_postflop:
        mapped_df["Spot"] = mapped_df["Spot"].replace(LEGACY_SPOT_RENAME_MAP)
    else:
        mapped_df["Spot"] = mapped_df["Spot"].apply(_normalize_text)
    return mapped_df


def get_filter_state_keys(is_postflop):
    if is_postflop:
        return {
            "spot": "stats_pf_filter_spot",
            "hero": "stats_pf_filter_hero",
            "street": "stats_pf_filter_street",
            "branch": "stats_pf_filter_branch",
        }
    return {"scenario": "stats_pre_filter_scenario"}


def get_active_filters(is_postflop):
    return {
        key: set(st.session_state.get(state_key, []))
        for key, state_key in get_filter_state_keys(is_postflop).items()
    }


def has_active_filters(active_filters):
    return any(values for values in active_filters.values())


def clear_active_filters(is_postflop):
    for state_key in get_filter_state_keys(is_postflop).values():
        st.session_state[state_key] = []


def _sorted_unique(values, sorter=None):
    clean_values = [_normalize_text(value) for value in values if _normalize_text(value)]
    unique_values = list(dict.fromkeys(clean_values))
    if sorter:
        return sorted(unique_values, key=sorter)
    return sorted(unique_values, key=lambda item: item.lower())


def build_filter_groups(catalog, is_postflop):
    if is_postflop:
        return [
            {
                "title": "Spot",
                "state_key": "stats_pf_filter_spot",
                "items": _sorted_unique([meta.get("spot", "") for meta in catalog.values()]),
            },
            {
                "title": "Hero",
                "state_key": "stats_pf_filter_hero",
                "items": _sorted_unique([meta.get("hero", "") for meta in catalog.values()]),
            },
            {
                "title": "Street",
                "state_key": "stats_pf_filter_street",
                "items": _sorted_unique([meta.get("street", "") for meta in catalog.values()]),
            },
            {
                "title": "Branch",
                "state_key": "stats_pf_filter_branch",
                "items": _sorted_unique([meta.get("branch", "") for meta in catalog.values()]),
            },
        ]

    return [
        {
            "title": "Scenario",
            "state_key": "stats_pre_filter_scenario",
            "items": _sorted_unique([meta.get("scenario", "") for meta in catalog.values()], sorter=_scenario_sort_key),
        }
    ]


def spot_matches_filters(spot_name, catalog, active_filters, is_postflop):
    if not has_active_filters(active_filters):
        return True

    meta = catalog.get(spot_name, {})
    if is_postflop:
        return (
            (not active_filters.get("spot") or meta.get("spot") in active_filters["spot"])
            and (not active_filters.get("hero") or meta.get("hero") in active_filters["hero"])
            and (not active_filters.get("street") or meta.get("street") in active_filters["street"])
            and (not active_filters.get("branch") or meta.get("branch") in active_filters["branch"])
        )

    return not active_filters.get("scenario") or meta.get("scenario") in active_filters["scenario"]


def render_filter_chip_group(title, items, state_key, key_prefix, columns_per_row=2):
    if not items:
        return

    st.markdown(f"<div class='filter-group-title'>{title}</div>", unsafe_allow_html=True)
    selected = set(st.session_state.get(state_key, []))
    ordered_items = list(items)

    for start_idx in range(0, len(ordered_items), columns_per_row):
        row_items = ordered_items[start_idx:start_idx + columns_per_row]
        row_cols = st.columns(len(row_items))
        for item_idx, (col, item) in enumerate(zip(row_cols, row_items)):
            with col:
                if item_idx == 0:
                    st.markdown("<div class='filter-row-marker-mob'></div>", unsafe_allow_html=True)
                is_active = item in selected
                if st.button(
                    item,
                    key=f"{key_prefix}_{_slugify(item)}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                ):
                    new_values = set(selected)
                    if item in new_values:
                        new_values.remove(item)
                    else:
                        new_values.add(item)

                    if state_key == "stats_pre_filter_scenario":
                        st.session_state[state_key] = sorted(new_values, key=_scenario_sort_key)
                    else:
                        st.session_state[state_key] = sorted(new_values, key=lambda value: value.lower())
                    st.rerun()


def fetch_history(is_postflop):
    sheets = utils.get_worksheets()
    if is_postflop:
        df_pf = pd.DataFrame(columns=["Date", "Spot", "Hand", "Result", "CorrectAction", "UserAction"])
        if "PostflopHistory" in sheets:
            try:
                vals = sheets["PostflopHistory"].get_all_values()
                if vals and len(vals) > 1:
                    headers = vals[0]
                    if "UserAction" not in headers:
                        headers.append("UserAction")
                        for row in vals[1:]:
                            row.append("UNKNOWN")
                    df_pf = pd.DataFrame(vals[1:], columns=headers)
            except Exception:
                pass
        elif os.path.exists("postflop_history.csv"):
            try:
                df_pf = pd.read_csv("postflop_history.csv", header=None)
                if df_pf.iloc[0, 0] == "Date":
                    df_pf.columns = df_pf.iloc[0]
                    df_pf = df_pf[1:]
                else:
                    df_pf.columns = ["Date", "Spot", "Hand", "Result", "CorrectAction", "UserAction"]
            except Exception:
                pass
        return df_pf

    df_pr = utils.load_history()
    if df_pr.empty:
        return df_pr
    return df_pr[~df_pr["Spot"].astype(str).str.contains("|", regex=False, na=False)].copy()


def custom_delete_history(days=None):
    utils.delete_history(days)
    try:
        sheets = utils.get_worksheets()
        headers = ["Date", "Spot", "Hand", "Result", "CorrectAction", "UserAction"]

        if "PostflopHistory" in sheets:
            if days is None:
                sheets["PostflopHistory"].clear()
                sheets["PostflopHistory"].append_row(headers)
            else:
                vals = sheets["PostflopHistory"].get_all_values()
                if vals and len(vals) > 1:
                    df = pd.DataFrame(vals[1:], columns=vals[0])
                    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
                    cutoff = datetime.now() - timedelta(days=days)
                    df_new = df[df["Date"] >= cutoff]
                    sheets["PostflopHistory"].clear()
                    rows = [headers] + df_new.astype(str).values.tolist()
                    sheets["PostflopHistory"].update(values=rows, range_name="A1")

        if os.path.exists("postflop_history.csv"):
            if days is None:
                os.remove("postflop_history.csv")
            else:
                df = pd.read_csv("postflop_history.csv", names=headers)
                if df.iloc[0]["Date"] == "Date":
                    df = df[1:]
                df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
                cutoff = datetime.now() - timedelta(days=days)
                df_new = df[df["Date"] >= cutoff]
                df_new.to_csv("postflop_history.csv", index=False, header=True)
    except Exception:
        pass

    utils.load_history.clear()


def start_training(selected_spots, is_postflop):
    if not selected_spots:
        st.warning("Select spots first.")
        return

    for key in list(st.session_state.keys()):
        if key.startswith("chk_") or key.startswith("pf_chk_") or key.startswith("sel_") or key.startswith("pf_sel_"):
            del st.session_state[key]

    if is_postflop:
        settings = utils.load_user_settings(is_postflop=True)
        pf_spots, pf_heroes, pf_streets, pf_branches = set(), set(), set(), set()

        for key in selected_spots:
            parts = [part.strip() for part in key.split("|")]
            if len(parts) >= 4:
                pf_spots.add(parts[0])
                pf_heroes.add(parts[1])
                pf_streets.add(parts[2])
                pf_branches.add(parts[3])

        settings["pf_sel_spots"] = list(pf_spots)
        settings["pf_sel_heroes"] = list(pf_heroes)
        settings["pf_sel_streets"] = list(pf_streets)
        settings["pf_sel_branches"] = list(pf_branches)
        settings["pf_spots"] = selected_spots

        utils.save_user_settings(settings, is_postflop=True)
        st.session_state.actual_app_mode = "Postflop"
        st.session_state.pf_hand = None
        st.session_state.pf_current_spot_key = None
    else:
        settings = utils.load_user_settings(is_postflop=False)
        ranges_db = utils.load_ranges()
        selected_sources, selected_scenarios = set(), set()

        for spot_name in selected_spots:
            for source, scenario_dict in ranges_db.items():
                for scenario, spot_dict in scenario_dict.items():
                    if spot_name in spot_dict:
                        selected_sources.add(source)
                        selected_scenarios.add(scenario)

        settings["selected_sources"] = list(selected_sources)
        settings["selected_scenarios"] = list(selected_scenarios)
        settings["selected_spots"] = selected_spots

        utils.save_user_settings(settings, is_postflop=False)
        st.session_state.actual_app_mode = "Preflop"
        st.session_state.hand = None
        st.session_state.current_spot = None

    if hasattr(utils, "force_sync"):
        utils.force_sync()
    st.rerun()


def show():
    st.markdown(
        """
        <style>
        div[data-testid="stHorizontalBlock"] {
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
            width: 100% !important;
            overflow: hidden !important;
            gap: 4px !important;
        }

        div[data-testid="column"], div[data-testid="stColumn"] {
            min-width: 0 !important;
            padding-left: 2px !important;
            padding-right: 2px !important;
        }

        .filter-panel {
            padding: 12px 12px 10px 12px;
            background: linear-gradient(180deg, rgba(18, 21, 26, 0.92) 0%, rgba(14, 17, 21, 0.98) 100%);
            border: 1px solid #2d3139;
            border-radius: 14px;
            margin-bottom: 14px;
        }

        .filter-panel-title {
            font-size: 12px;
            font-weight: 900;
            letter-spacing: 0.14em;
            color: #f8f9fa;
            text-transform: uppercase;
            margin-bottom: 4px;
        }

        .filter-panel-note {
            font-size: 11px;
            color: #89929b;
            margin-bottom: 10px;
            line-height: 1.35;
        }

        .filter-group-title {
            font-size: 10px;
            font-weight: 800;
            color: #adb5bd;
            text-transform: uppercase;
            letter-spacing: 0.10em;
            margin: 10px 0 8px 0;
        }

        .filter-row-marker-mob { display: none; }

        div[data-testid="stHorizontalBlock"]:has(.filter-row-marker-mob) {
            gap: 6px !important;
            margin-bottom: 6px !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.filter-row-marker-mob) > div[data-testid="column"] {
            min-width: 0 !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.filter-row-marker-mob) div[data-testid="stButton"] button {
            width: 100% !important;
            height: 34px !important;
            min-height: 34px !important;
            padding: 0 10px !important;
            border-radius: 999px !important;
            font-size: 10px !important;
            font-weight: 800 !important;
            line-height: 1 !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.filter-row-marker-mob) div[data-testid="stButton"] button[kind="secondary"] {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            color: #cfd6dd !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.filter-row-marker-mob) div[data-testid="stButton"] button[kind="primary"] {
            background: linear-gradient(180deg, #2b5876 0%, #1f3447 100%) !important;
            border: 1px solid rgba(255, 193, 7, 0.55) !important;
            box-shadow: 0 0 0 1px rgba(255, 193, 7, 0.15), 0 0 12px rgba(255, 193, 7, 0.12) !important;
            color: #ffffff !important;
        }

        .train-btn div[data-testid="stButton"] button {
            height: 42px !important;
            background: linear-gradient(180deg, #1c3a55 0%, #102436 100%) !important;
            border: none !important;
            font-weight: 900 !important;
            letter-spacing: 0.04em !important;
            color: #ffffff !important;
            border-radius: 10px !important;
            width: 100% !important;
        }

        .target-btn div[data-testid="stButton"] button {
            width: 44px !important;
            height: 32px !important;
            min-height: 32px !important;
            padding: 0 !important;
            border-radius: 8px !important;
            background: transparent !important;
            border: 1px solid rgba(255,255,255,0.18) !important;
            font-size: 10px !important;
            font-weight: 800 !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            margin: 0 auto !important;
            color: #ffffff !important;
        }

        .hide-checkbox-label div[data-testid="stCheckbox"] {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }

        .hide-checkbox-label div[data-testid="stCheckbox"] label {
            padding: 0 !important;
            min-height: 0 !important;
        }

        .hide-checkbox-label div[data-testid="stCheckbox"] p {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## Statistics Hub")

    mode = st.radio("Section:", ["Preflop", "Postflop"], horizontal=True, label_visibility="collapsed")
    is_postflop = mode == "Postflop"

    raw_df = fetch_history(is_postflop)
    if raw_df.empty or "Date" not in raw_df.columns or "Result" not in raw_df.columns:
        st.info(f"History for {mode} is empty. Go train.")
        return

    catalog, _ = get_spot_catalog(is_postflop)
    df = canonicalize_history_spots(raw_df, is_postflop)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])
    df["Result"] = pd.to_numeric(df["Result"], errors="coerce").fillna(0).astype(int)

    st.markdown(f"### Performance ({mode})")
    total_hands = len(df)
    total_correct = int(df["Result"].sum())
    accuracy = (total_correct / total_hands * 100) if total_hands > 0 else 0

    metric_col_1, metric_col_2, metric_col_3 = st.columns(3)
    metric_col_1.metric("Hands", total_hands)
    metric_col_2.metric("Correct", total_correct)
    metric_col_3.metric("Accuracy", f"{accuracy:.1f}%")

    st.markdown("<div class='filter-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='filter-panel-title'>Spot Filters</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='filter-panel-note'>Tap chips to filter both Spot Mastery and Road to Mastery.</div>",
        unsafe_allow_html=True,
    )

    reset_col_1, reset_col_2 = st.columns([1.8, 1])
    with reset_col_2:
        if st.button("RESET", key=f"reset_filters_mobile_{mode.lower()}", use_container_width=True):
            clear_active_filters(is_postflop)
            st.rerun()

    filter_groups = build_filter_groups(catalog, is_postflop)
    for group in filter_groups:
        render_filter_chip_group(
            title=group["title"],
            items=group["items"],
            state_key=group["state_key"],
            key_prefix=f"mob_{mode.lower()}_{group['title'].lower()}",
            columns_per_row=2,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    active_filters = get_active_filters(is_postflop)
    filtered_catalog_spots = {
        spot_name
        for spot_name in catalog.keys()
        if spot_matches_filters(spot_name, catalog, active_filters, is_postflop)
    }
    filtered_df = df[df["Spot"].apply(lambda spot_name: spot_matches_filters(spot_name, catalog, active_filters, is_postflop))].copy()

    st.markdown("### Spot Mastery")
    stats = filtered_df.groupby("Spot")["Result"].agg(["count", "sum", "mean"]).reset_index()
    stats["Errors"] = stats["count"] - stats["sum"]
    stats["Accuracy"] = (stats["mean"] * 100).round().astype(int).astype(str) + "%"
    stats["DisplaySpot"] = stats["Spot"].apply(lambda name: catalog.get(name, {}).get("display_name", name))
    stats_view = stats.sort_values(by=["count", "DisplaySpot"], ascending=[False, True])

    if stats_view.empty:
        st.info("No spots match the active filters in Spot Mastery.")
    else:
        st.dataframe(
            stats_view[["DisplaySpot", "Errors", "Accuracy", "count"]].rename(
                columns={"DisplaySpot": "Spot", "count": "Total"}
            ),
            use_container_width=True,
            hide_index=True,
        )

    st.divider()
    st.markdown("### Road to Mastery (5k Hands)")
    st.caption("Select spots and launch training right from here.")

    spot_counts = filtered_df["Spot"].value_counts().to_dict()
    sorted_spots = sorted(spot_counts.items(), key=lambda item: (-item[1], _spot_sort_key(item[0], catalog, is_postflop)))

    if not sorted_spots:
        st.info("No spots match the active filters in Road to Mastery.")
    else:
        st.markdown('<div class="train-btn">', unsafe_allow_html=True)
        if st.button("TRAIN SELECTED", key=f"train_selected_mobile_{mode.lower()}", use_container_width=True):
            selected_spots = [spot_name for spot_name, _ in sorted_spots if st.session_state.get(f"sel_{spot_name}", False)]
            start_training(selected_spots, is_postflop)
        st.markdown("</div>", unsafe_allow_html=True)

        for spot_name, count in sorted_spots:
            pct = min(100, (count / 5000) * 100)
            if count < 100:
                gradient, glow = "linear-gradient(90deg, #6c757d, #495057)", "rgba(108, 117, 125, 0.3)"
            elif count < 500:
                gradient, glow = "linear-gradient(90deg, #198754, #20c997)", "rgba(32, 201, 151, 0.4)"
            elif count < 1500:
                gradient, glow = "linear-gradient(90deg, #0dcaf0, #0d6efd)", "rgba(13, 202, 240, 0.5)"
            elif count < 3000:
                gradient, glow = "linear-gradient(90deg, #6f42c1, #d63384)", "rgba(214, 51, 132, 0.5)"
            elif count < 5000:
                gradient, glow = "linear-gradient(90deg, #dc3545, #fd7e14)", "rgba(253, 126, 20, 0.6)"
            else:
                gradient, glow = "linear-gradient(90deg, #ffc107, #ffef96)", "rgba(255, 193, 7, 0.8)"

            left_col, action_col, card_col = st.columns([0.12, 0.18, 0.70], vertical_alignment="center")

            with left_col:
                st.markdown('<div class="hide-checkbox-label">', unsafe_allow_html=True)
                st.checkbox(" ", key=f"sel_{spot_name}")
                st.markdown("</div>", unsafe_allow_html=True)

            with action_col:
                st.markdown('<div class="target-btn">', unsafe_allow_html=True)
                if st.button("GO", key=f"go_{spot_name}", use_container_width=True):
                    start_training([spot_name], is_postflop)
                st.markdown("</div>", unsafe_allow_html=True)

            with card_col:
                display_name = catalog.get(spot_name, {}).get("display_name", spot_name)
                html_output = (
                    "<div style='display:flex; align-items:center; gap:8px; background:#16181c; padding:8px 10px; "
                    "border-radius:10px; border:1px solid #2d3139; box-shadow:0 2px 4px rgba(0,0,0,0.2); "
                    "width:100%; box-sizing:border-box;'>"
                    f"<div style='flex:1 1 38%; min-width:0; color:#e9ecef; font-weight:800; font-size:10px; "
                    f"letter-spacing:0.02em; text-transform:uppercase; overflow:hidden; text-overflow:ellipsis; "
                    f"white-space:nowrap;' title='{display_name}'>{display_name}</div>"
                    f"<div style='flex:0 0 auto; color:#ffffff; font-weight:900; font-size:12px; text-align:right; "
                    f"font-variant-numeric:tabular-nums;'>{count}</div>"
                    f"<div style='flex:1 1 42%; background:rgba(0,0,0,0.6); height:6px; border-radius:3px; "
                    f"box-shadow:inset 0 1px 3px rgba(0,0,0,0.8); position:relative; overflow:hidden;'>"
                    f"<div style='width:{pct}%; height:100%; background:{gradient}; border-radius:3px; "
                    f"box-shadow:0 0 10px {glow}; transition:width 0.5s ease-out;'></div></div>"
                    "<div style='flex:0 0 auto; color:#6c757d; font-weight:700; font-size:10px;'>5k</div>"
                    "</div>"
                )
                st.markdown(html_output, unsafe_allow_html=True)

    st.divider()
    with st.expander("Raw History Log"):
        history_view = df.copy().sort_values("Date", ascending=False)
        history_view["Date"] = history_view["Date"].dt.strftime("%Y-%m-%d %H:%M:%S")
        history_view["Result"] = history_view["Result"].apply(lambda value: "WIN" if value == 1 else "MISS")
        cols_to_show = (
            ["Date", "Spot", "Hand", "CorrectAction", "UserAction", "Result"]
            if "UserAction" in history_view.columns
            else ["Date", "Spot", "Hand", "CorrectAction", "Result"]
        )
        st.dataframe(history_view[cols_to_show], use_container_width=True, hide_index=True)

    st.markdown("### Data Recovery")
    with st.expander("Recover Spot Mastery from History", expanded=False):
        st.markdown("Recalculate XP, streak, and Spot Mastery directly from raw history.")
        if st.button("RECOVER SPOT MASTERY", key=f"recover_mobile_{mode.lower()}", use_container_width=True):
            df_hist = df.copy().sort_values("Date")
            new_mastery = {}
            total_correct_hist = int(df_hist["Result"].sum())

            for _, row in df_hist.iterrows():
                spot_name = row["Spot"]
                if spot_name not in new_mastery:
                    new_mastery[spot_name] = {"t": 0, "h": "", "d": ""}
                new_mastery[spot_name]["t"] += 1
                new_mastery[spot_name]["h"] += "1" if row["Result"] == 1 else "0"
                if len(new_mastery[spot_name]["h"]) > 100:
                    new_mastery[spot_name]["h"] = new_mastery[spot_name]["h"][-100:]
                new_mastery[spot_name]["d"] = row["Date"].strftime("%Y-%m-%d")

            stats_dict = utils.load_user_stats(is_postflop=is_postflop)
            stats_dict["xp"] = int(total_correct_hist * 10)
            stats_dict["total_hands"] = len(df_hist)
            stats_dict["spot_mastery"] = new_mastery

            utils.save_user_stats(stats_dict, is_postflop=is_postflop)
            st.success("Recovery complete. Refresh applied.")
            st.rerun()

    st.markdown("### Danger Zone")
    with st.expander("Clear History", expanded=False):
        st.warning("Warning: clears ALL history globally (Preflop and Postflop).")
        del_col_1, del_col_2 = st.columns(2)
        del_col_3, del_col_4 = st.columns(2)
        if del_col_1.button("Delete: 24 Hours", use_container_width=True):
            custom_delete_history(days=1)
            st.rerun()
        if del_col_2.button("Delete: 7 Days", use_container_width=True):
            custom_delete_history(days=7)
            st.rerun()
        if del_col_3.button("Delete: 30 Days", use_container_width=True):
            custom_delete_history(days=30)
            st.rerun()
        if del_col_4.button("NUKE ALL", use_container_width=True):
            custom_delete_history()
            st.rerun()
