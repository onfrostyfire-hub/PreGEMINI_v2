import json
import os
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

import poker_utils as utils


PRE_RENAME_MAP = {
    "BUvsCO": "3bet BUvsCO",
    "SBvsCO": "3bet SBvsCO",
    "SBvsBU": "3bet SBvsBU",
    "BBvsCO": "3bet BBvsCO",
    "BBvsBU": "3bet BBvsBU",
    "BBvsSB": "3bet BBvsSB",
    "SB pfr": "HU @ SB pfr",
    "BB def vs PFR": "HU @ BB def vs PFR",
    "SB def vs 3bet BB": "HU @ SB def vs 3bet",
    "SB def vs 3bet": "HU @ SB def vs 3bet",
    "BB def vs 4bet": "HU @ BB def vs 4bet",
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


def normalize_text(value):
    return " ".join(str(value or "").replace("\xa0", " ").split()).strip()


def normalize_postflop_key(value):
    parts = [part.strip() for part in str(value or "").split("|")]
    return " | ".join([part for part in parts if part])


def slugify(value):
    chars = []
    for ch in normalize_text(value).lower():
        chars.append(ch if ch.isalnum() else "_")
    return "".join(chars).strip("_") or "item"


def scenario_sort_key(name):
    clean_name = normalize_text(name)
    if clean_name in PRE_SCENARIO_ORDER:
        return (PRE_SCENARIO_ORDER.index(clean_name), clean_name.lower())
    return (len(PRE_SCENARIO_ORDER), clean_name.lower())


@st.cache_data(ttl=0)
def load_preflop_category_map():
    category_map = {}
    try:
        ranges_db = utils.load_ranges()
        for _, scenario_dict in ranges_db.items():
            for scenario_name, spots_dict in scenario_dict.items():
                for spot_name in spots_dict.keys():
                    category_map[normalize_text(spot_name)] = normalize_text(scenario_name)
    except Exception:
        pass
    return category_map


@st.cache_data(ttl=0)
def load_postflop_meta_map():
    meta_map = {}
    pf_dir = "postflop_data" if os.path.exists("postflop_data") else "spots_data"
    if not os.path.exists(pf_dir):
        return meta_map

    for file_name in os.listdir(pf_dir):
        if not file_name.endswith(".json"):
            continue
        try:
            with open(os.path.join(pf_dir, file_name), "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except Exception:
            continue

        raw_spots = data.get("spots", data) if isinstance(data, dict) else {}
        if not isinstance(raw_spots, dict):
            continue

        for spot_name in raw_spots.keys():
            clean_name = normalize_postflop_key(spot_name)
            parts = [part.strip() for part in clean_name.split("|")]
            meta_map[clean_name] = {
                "spot": parts[0] if len(parts) > 0 else clean_name,
                "hero": parts[1] if len(parts) > 1 else "Unknown",
                "street": parts[2] if len(parts) > 2 else "Unknown",
                "branch": parts[3] if len(parts) > 3 else "General",
            }
    return meta_map


def fetch_history_direct(is_postflop):
    sheets = utils.get_worksheets()
    ws_name = "PostflopHistory" if is_postflop else "History"
    df_hist = pd.DataFrame(columns=["Date", "Spot", "Hand", "Result", "CorrectAction", "UserAction"])

    if ws_name in sheets:
        try:
            vals = sheets[ws_name].get_all_values()
            if vals and len(vals) > 1:
                headers = vals[0]
                if "UserAction" not in headers:
                    headers.append("UserAction")
                    for row in vals[1:]:
                        row.append("UNKNOWN")
                df_hist = pd.DataFrame(vals[1:], columns=headers)
        except Exception:
            pass

    return df_hist


def custom_delete_history(days=None):
    try:
        sheets = utils.get_worksheets()
        headers = ["Date", "Spot", "Hand", "Result", "CorrectAction", "UserAction"]

        for ws_name in ["History", "PostflopHistory"]:
            if ws_name not in sheets:
                continue

            if days is None:
                sheets[ws_name].clear()
                sheets[ws_name].append_row(headers)
            else:
                vals = sheets[ws_name].get_all_values()
                if vals and len(vals) > 1:
                    df_hist = pd.DataFrame(vals[1:], columns=vals[0])
                    df_hist["Date"] = pd.to_datetime(df_hist["Date"], errors="coerce")
                    cutoff = datetime.now() - timedelta(days=days)
                    df_new = df_hist[df_hist["Date"] >= cutoff]
                    sheets[ws_name].clear()
                    rows = [headers] + df_new.astype(str).values.tolist()
                    sheets[ws_name].update(values=rows, range_name="A1")
    except Exception:
        pass


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
            for source_name, scenario_dict in ranges_db.items():
                for scenario_name, spots_dict in scenario_dict.items():
                    if spot_name in spots_dict:
                        selected_sources.add(source_name)
                        selected_scenarios.add(scenario_name)

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


def toggle_filter_value(state_key, value, sorter=None):
    current_values = set(st.session_state.get(state_key, []))
    if value in current_values:
        current_values.remove(value)
    else:
        current_values.add(value)

    if sorter is not None:
        st.session_state[state_key] = sorted(current_values, key=sorter)
    else:
        st.session_state[state_key] = sorted(current_values, key=lambda item: item.lower())


def render_chip_group(title, items, state_key, key_prefix, columns_per_row, sorter=None):
    if not items:
        return

    st.markdown(f"<div class='filter-group-title'>{title}</div>", unsafe_allow_html=True)
    selected_values = set(st.session_state.get(state_key, []))

    for start_idx in range(0, len(items), columns_per_row):
        row_items = items[start_idx:start_idx + columns_per_row]
        row_cols = st.columns(len(row_items))
        for idx, (col, item) in enumerate(zip(row_cols, row_items)):
            with col:
                if idx == 0:
                    st.markdown("<div class='filter-marker'></div>", unsafe_allow_html=True)
                is_active = item in selected_values
                if st.button(
                    item,
                    key=f"{key_prefix}_{slugify(item)}",
                    type="primary" if is_active else "secondary",
                    use_container_width=True,
                ):
                    toggle_filter_value(state_key, item, sorter=sorter)
                    st.rerun()


def prepare_history_dataframe(is_postflop):
    df_hist = fetch_history_direct(is_postflop)
    if df_hist.empty or "Spot" not in df_hist.columns:
        return df_hist

    df_hist = df_hist.copy()
    if is_postflop:
        df_hist["Spot"] = df_hist["Spot"].apply(normalize_postflop_key)
    else:
        df_hist["Spot"] = df_hist["Spot"].replace(PRE_RENAME_MAP).apply(normalize_text)

    df_hist["Date"] = pd.to_datetime(df_hist["Date"], errors="coerce")
    df_hist = df_hist.dropna(subset=["Date"])
    df_hist["Result"] = pd.to_numeric(df_hist["Result"], errors="coerce").fillna(0).astype(int)
    return df_hist


def apply_preflop_filters(df_hist):
    category_map = load_preflop_category_map()
    df_hist = df_hist.copy()
    df_hist["Category"] = df_hist["Spot"].apply(lambda value: category_map.get(value, "Other"))

    available_categories = sorted(
        [value for value in df_hist["Category"].dropna().unique() if value != "Other"],
        key=scenario_sort_key,
    )
    if "Other" in df_hist["Category"].values:
        available_categories.append("Other")

    render_chip_group(
        title="Scenario",
        items=available_categories,
        state_key="stats_filters_mob_pre_scenario",
        key_prefix="mob_pre_scenario",
        columns_per_row=2,
        sorter=scenario_sort_key,
    )

    active_categories = set(st.session_state.get("stats_filters_mob_pre_scenario", []))
    if active_categories:
        return df_hist[df_hist["Category"].isin(active_categories)].copy()
    return df_hist


def apply_postflop_filters(df_hist):
    meta_map = load_postflop_meta_map()
    df_hist = df_hist.copy()

    df_hist["PF_Spot"] = df_hist["Spot"].apply(lambda value: meta_map.get(value, {}).get("spot", value.split("|")[0].strip()))
    df_hist["PF_Hero"] = df_hist["Spot"].apply(
        lambda value: meta_map.get(value, {}).get("hero", value.split("|")[1].strip() if "|" in value else "Unknown")
    )
    df_hist["PF_Street"] = df_hist["Spot"].apply(
        lambda value: meta_map.get(value, {}).get("street", value.split("|")[2].strip() if value.count("|") >= 2 else "Unknown")
    )
    df_hist["PF_Branch"] = df_hist["Spot"].apply(
        lambda value: meta_map.get(value, {}).get("branch", value.split("|")[3].strip() if value.count("|") >= 3 else "General")
    )

    render_chip_group(
        title="Spot",
        items=sorted(df_hist["PF_Spot"].dropna().unique(), key=lambda item: item.lower()),
        state_key="stats_filters_mob_pf_spot",
        key_prefix="mob_pf_spot",
        columns_per_row=2,
    )
    render_chip_group(
        title="Hero",
        items=sorted(df_hist["PF_Hero"].dropna().unique(), key=lambda item: item.lower()),
        state_key="stats_filters_mob_pf_hero",
        key_prefix="mob_pf_hero",
        columns_per_row=2,
    )
    render_chip_group(
        title="Street",
        items=sorted(df_hist["PF_Street"].dropna().unique(), key=lambda item: item.lower()),
        state_key="stats_filters_mob_pf_street",
        key_prefix="mob_pf_street",
        columns_per_row=2,
    )
    render_chip_group(
        title="Branch",
        items=sorted(df_hist["PF_Branch"].dropna().unique(), key=lambda item: item.lower()),
        state_key="stats_filters_mob_pf_branch",
        key_prefix="mob_pf_branch",
        columns_per_row=2,
    )

    active_spots = set(st.session_state.get("stats_filters_mob_pf_spot", []))
    active_heroes = set(st.session_state.get("stats_filters_mob_pf_hero", []))
    active_streets = set(st.session_state.get("stats_filters_mob_pf_street", []))
    active_branches = set(st.session_state.get("stats_filters_mob_pf_branch", []))

    filtered_df = df_hist.copy()
    if active_spots:
        filtered_df = filtered_df[filtered_df["PF_Spot"].isin(active_spots)]
    if active_heroes:
        filtered_df = filtered_df[filtered_df["PF_Hero"].isin(active_heroes)]
    if active_streets:
        filtered_df = filtered_df[filtered_df["PF_Street"].isin(active_streets)]
    if active_branches:
        filtered_df = filtered_df[filtered_df["PF_Branch"].isin(active_branches)]
    return filtered_df


def clear_filter_state(is_postflop):
    if is_postflop:
        for key in [
            "stats_filters_mob_pf_spot",
            "stats_filters_mob_pf_hero",
            "stats_filters_mob_pf_street",
            "stats_filters_mob_pf_branch",
        ]:
            st.session_state[key] = []
    else:
        st.session_state["stats_filters_mob_pre_scenario"] = []


def show():
    st.markdown(
        """
        <style>
        .block-container { padding-top: 1.2rem !important; }

        .filter-panel {
            padding: 12px 12px 14px 12px;
            background: transparent;
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 16px;
            margin: 18px 0 18px 0;
        }

        .filter-panel-title {
            font-size: 12px;
            font-weight: 900;
            letter-spacing: 0.16em;
            color: #ffffff;
            text-transform: uppercase;
            margin-bottom: 4px;
        }

        .filter-panel-note {
            font-size: 11px;
            color: #8ea4c0;
            margin-bottom: 12px;
            line-height: 1.35;
        }

        .filter-group-title {
            font-size: 10px;
            font-weight: 800;
            color: #d0d7df;
            text-transform: uppercase;
            letter-spacing: 0.10em;
            margin: 10px 0 8px 0;
        }

        div[data-testid="stHorizontalBlock"]:has(.filter-marker) {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 6px !important;
            margin-bottom: 6px !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.filter-marker) > div[data-testid="column"] {
            min-width: 0 !important;
            padding: 0 !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.filter-marker) div[data-testid="stButton"] button {
            border-radius: 999px !important;
            padding: 4px 10px !important;
            height: 34px !important;
            min-height: 34px !important;
            font-size: 11px !important;
            font-weight: 700 !important;
            border: 1px solid rgba(255,255,255,0.10) !important;
            background: rgba(44,44,46,0.60) !important;
            color: #d6d8dd !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.filter-marker) div[data-testid="stButton"] button[kind="primary"] {
            background: #ffcc00 !important;
            border-color: #ffcc00 !important;
            color: #1c1c1e !important;
            box-shadow: 0 4px 12px rgba(255, 204, 0, 0.35) !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.spot-row-marker-mob) {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
            background: rgba(28,28,30,0.60) !important;
            padding: 12px 12px !important;
            border-radius: 14px !important;
            border: 1px solid rgba(255,255,255,0.05) !important;
            margin-bottom: 8px !important;
            gap: 10px !important;
            width: 100% !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.spot-row-marker-mob) > div[data-testid="column"] {
            margin: 0 !important;
            padding: 0 !important;
            min-width: 0 !important;
            width: auto !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.spot-row-marker-mob) > div[data-testid="column"]:nth-child(1) { flex: 0 0 24px !important; }
        div[data-testid="stHorizontalBlock"]:has(.spot-row-marker-mob) > div[data-testid="column"]:nth-child(2) { flex: 0 0 44px !important; }
        div[data-testid="stHorizontalBlock"]:has(.spot-row-marker-mob) > div[data-testid="column"]:nth-child(3) { flex: 1 1 auto !important; }

        .hide-checkbox-label div[data-testid="stCheckbox"] {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            margin: 0 !important;
        }

        .hide-checkbox-label div[data-testid="stCheckbox"] label {
            padding: 0 !important;
            min-height: 0 !important;
        }

        .hide-checkbox-label div[data-testid="stCheckbox"] p { display: none !important; }

        .target-btn-wrap div[data-testid="stButton"] button {
            width: 42px !important;
            height: 32px !important;
            min-height: 32px !important;
            padding: 0 !important;
            margin: 0 !important;
            border-radius: 10px !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
            background: rgba(255,255,255,0.04) !important;
            font-size: 11px !important;
            font-weight: 800 !important;
        }

        .spot-card {
            display: flex;
            flex-direction: column;
            width: 100%;
            gap: 6px;
            justify-content: center;
        }

        .spot-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
            gap: 8px;
        }

        .spot-title {
            color: #f2f2f7;
            font-weight: 600;
            font-size: 12px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            flex: 1 1 auto;
            min-width: 0;
        }

        .spot-count {
            color: #ffffff;
            font-weight: 800;
            font-size: 12px;
            font-variant-numeric: tabular-nums;
            flex: 0 0 auto;
            text-align: right;
        }

        .spot-bar-bg {
            width: 100%;
            background: rgba(0,0,0,0.5);
            height: 8px;
            border-radius: 4px;
            overflow: hidden;
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.8);
        }

        .spot-bar-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.5s ease-out;
        }

        .train-btn div[data-testid="stButton"] button {
            border-radius: 14px !important;
            background: linear-gradient(180deg, #ffcc00 0%, #e6b800 100%) !important;
            color: #1c1c1e !important;
            font-weight: 800 !important;
            border: none !important;
            height: 46px !important;
            min-height: 46px !important;
            box-shadow: 0 4px 14px rgba(255, 204, 0, 0.4) !important;
            letter-spacing: 0.5px !important;
            text-transform: uppercase !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## Statistics Hub")

    mode = st.radio("Section:", ["Preflop", "Postflop"], horizontal=True, label_visibility="collapsed")
    is_postflop = mode == "Postflop"

    df = prepare_history_dataframe(is_postflop)
    if df.empty:
        st.info("No history data to show. Go train.")
        return

    st.markdown(f"### Performance ({mode})")
    total_hands = len(df)
    total_correct = int(df["Result"].sum())
    accuracy = (total_correct / total_hands * 100) if total_hands > 0 else 0

    col_1, col_2, col_3 = st.columns(3)
    col_1.metric("Hands", total_hands)
    col_2.metric("Correct", total_correct)
    col_3.metric("Accuracy", f"{accuracy:.1f}%")

    st.markdown("<div class='filter-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='filter-panel-title'>Spot Filters</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='filter-panel-note'>Active chips filter both Spot Mastery and Road to Mastery.</div>",
        unsafe_allow_html=True,
    )

    reset_col_1, reset_col_2 = st.columns([1.8, 1])
    with reset_col_2:
        if st.button("RESET", key=f"mob_reset_{mode.lower()}", use_container_width=True):
            clear_filter_state(is_postflop)
            st.rerun()

    filtered_df = apply_postflop_filters(df) if is_postflop else apply_preflop_filters(df)
    st.markdown("</div>", unsafe_allow_html=True)

    if filtered_df.empty:
        st.info("No history data matches the active filters.")
        return

    st.markdown("### Spot Mastery")
    stats = filtered_df.groupby("Spot")["Result"].agg(["count", "sum", "mean"]).reset_index()
    stats["Errors"] = stats["count"] - stats["sum"]
    stats["Accuracy"] = (stats["mean"] * 100).astype(int).astype(str) + "%"
    stats = stats.sort_values(by=["count", "Spot"], ascending=[False, True])

    st.dataframe(
        stats[["Spot", "Errors", "Accuracy", "count"]].rename(columns={"count": "Total"}),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    st.markdown("### Road to Mastery (5k Hands)")
    st.caption("Select spots and launch training right from here.")

    spot_counts = filtered_df["Spot"].value_counts().to_dict()
    sorted_spots = sorted(spot_counts.items(), key=lambda item: (-item[1], item[0]))

    st.markdown('<div class="train-btn">', unsafe_allow_html=True)
    if st.button("TRAIN SELECTED", key=f"mob_train_selected_{mode.lower()}", use_container_width=True):
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

        row_col_1, row_col_2, row_col_3 = st.columns([0.12, 0.18, 0.70])

        with row_col_1:
            st.markdown("<div class='spot-row-marker-mob'></div><div class='hide-checkbox-label'>", unsafe_allow_html=True)
            st.checkbox(" ", key=f"sel_{spot_name}")
            st.markdown("</div>", unsafe_allow_html=True)

        with row_col_2:
            st.markdown("<div class='target-btn-wrap'>", unsafe_allow_html=True)
            if st.button("GO", key=f"go_{spot_name}", use_container_width=True):
                start_training([spot_name], is_postflop)
            st.markdown("</div>", unsafe_allow_html=True)

        with row_col_3:
            html_output = (
                "<div class='spot-card'>"
                "<div class='spot-header'>"
                f"<div class='spot-title' title='{spot_name}'>{spot_name}</div>"
                f"<div class='spot-count'>{count}</div>"
                "</div>"
                "<div class='spot-bar-bg'>"
                f"<div class='spot-bar-fill' style='width:{pct}%; background:{gradient}; box-shadow:0 0 10px {glow};'></div>"
                "</div>"
                "</div>"
            )
            st.markdown(html_output, unsafe_allow_html=True)

    st.divider()
    with st.expander("Raw History Log"):
        history_view = filtered_df.copy()
        history_view["Result"] = history_view["Result"].apply(lambda value: "OK" if value == 1 else "MISS")
        history_view = history_view.sort_values("Date", ascending=False)
        history_view["Date"] = history_view["Date"].dt.strftime("%Y-%m-%d %H:%M:%S")
        cols_to_show = (
            ["Date", "Spot", "Hand", "CorrectAction", "UserAction", "Result"]
            if "UserAction" in history_view.columns
            else ["Date", "Spot", "Hand", "CorrectAction", "Result"]
        )
        st.dataframe(history_view[cols_to_show], use_container_width=True, hide_index=True)

    st.markdown("### Data Recovery")
    with st.expander("Recover Spot Mastery from History", expanded=False):
        st.markdown("If your progress got reset, this will recalculate your experience, streak, and Spot Mastery from raw history.")
        if st.button("RECOVER SPOT MASTERY", key=f"mob_recover_{mode.lower()}", use_container_width=True):
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
            st.success("Recovery complete.")
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
