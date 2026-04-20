import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import poker_utils as utils
import json
import os

def get_spot_categories(is_postflop):
    cat_map = {}
    all_spots = set()
    directory = 'postflop_data' if is_postflop else 'spots_data'
    if os.path.exists(directory):
        for file in os.listdir(directory):
            if file.endswith('.json'):
                try:
                    with open(os.path.join(directory, file), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        scen = data.get("scenario", "Postflop" if is_postflop else "Other")
                        if "spots" in data:
                            for k in data["spots"].keys():
                                cat_map[k] = scen
                                all_spots.add(k)
                        else:
                            for k in data.keys():
                                if k not in ["scenario", "source"]:
                                    cat_map[k] = scen
                                    all_spots.add(k)
                except: pass
    return cat_map, all_spots

@st.cache_data(ttl=60)
def fetch_history(is_postflop):
    sheets = utils.get_worksheets()
    ws_name = "PostflopHistory" if is_postflop else "History"
    df = pd.DataFrame(columns=["Date", "Spot", "Hand", "Result", "CorrectAction", "UserAction"])
    if ws_name in sheets:
        try:
            vals = sheets[ws_name].get_all_values()
            if vals and len(vals) > 1:
                headers = vals[0]
                if "UserAction" not in headers:
                    headers.append("UserAction")
                    for r in vals[1:]: r.append("UNKNOWN")
                df = pd.DataFrame(vals[1:], columns=headers)
        except: pass
    return df

def custom_delete_history(days=None):
    try:
        sheets = utils.get_worksheets()
        headers = ["Date", "Spot", "Hand", "Result", "CorrectAction", "UserAction"]
        for ws_name in ["History", "PostflopHistory"]:
            if ws_name in sheets:
                if days is None:
                    sheets[ws_name].clear()
                    sheets[ws_name].append_row(headers)
                else:
                    vals = sheets[ws_name].get_all_values()
                    if vals and len(vals) > 1:
                        df = pd.DataFrame(vals[1:], columns=vals[0])
                        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
                        cutoff = datetime.now() - timedelta(days=days)
                        df_new = df[df["Date"] >= cutoff]
                        sheets[ws_name].clear()
                        rows = [headers] + df_new.astype(str).values.tolist()
                        sheets[ws_name].update(values=rows, range_name="A1")
    except: pass
    fetch_history.clear()

def start_training(selected_spots, is_postflop):
    if not selected_spots:
        st.warning("Select spots first, Boss.")
        return

    for k in list(st.session_state.keys()):
        if k.startswith("chk_") or k.startswith("pf_chk_") or k.startswith("sel_") or k.startswith("pf_sel_"):
            del st.session_state[k]

    if is_postflop:
        settings = utils.load_user_settings(is_postflop=True)
        pf_spots, pf_heroes, pf_streets, pf_branches = set(), set(), set(), set()
        for key in selected_spots:
            parts = [p.strip() for p in key.split('|')]
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
        sel_src, sel_sc = set(), set()
        for sp in selected_spots:
            for src, sc_dict in ranges_db.items():
                for sc, sp_dict in sc_dict.items():
                    if sp in sp_dict:
                        sel_src.add(src)
                        sel_sc.add(sc)
                        
        settings["selected_sources"] = list(sel_src)
        settings["selected_scenarios"] = list(sel_sc)
        settings["selected_spots"] = selected_spots
        utils.save_user_settings(settings, is_postflop=False)
        st.session_state.actual_app_mode = "Preflop"
        st.session_state.hand = None
        st.session_state.current_spot = None

    if hasattr(utils, "force_sync"): utils.force_sync()
    st.rerun()

def show():
    st.markdown("""
        <style>
        /* ГЛОБАЛЬНЫЙ ХАК ПРОТИВ СЛОМА КОЛОНОК НА МОБИЛЕ */
        div[data-testid="stHorizontalBlock"]:not(:has(.filter-marker-mob)) {
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
            width: 100% !important;
            overflow: hidden !important;
            gap: 4px !important;
        }
        div[data-testid="stHorizontalBlock"]:not(:has(.filter-marker-mob)) > div[data-testid="column"], 
        div[data-testid="stHorizontalBlock"]:not(:has(.filter-marker-mob)) > div[data-testid="stColumn"] {
            min-width: 0 !important;
            padding-left: 2px !important;
            padding-right: 2px !important;
        }
        
        /* КНОПКА МИШЕНИ */
        .target-btn div[data-testid="stButton"] button {
            width: 32px !important;
            height: 32px !important;
            min-height: 32px !important;
            padding: 0 !important;
            border-radius: 8px !important;
            background: transparent !important;
            border: 1px solid rgba(255,255,255,0.2) !important;
            font-size: 15px !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            margin: 0 auto !important;
        }
        .target-btn div[data-testid="stButton"] button:hover, 
        .target-btn div[data-testid="stButton"] button:active {
            border-color: #ffc107 !important;
            background: rgba(255,193,7,0.1) !important;
        }

        /* ЧЕКБОКС */
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

        /* КНОПКА TRAIN SELECTED */
        .train-btn div[data-testid="stButton"] button {
            height: 44px !important;
            background: linear-gradient(180deg, #1c3a55 0%, #102436 100%) !important;
            border: none !important;
            font-weight: 900 !important;
            letter-spacing: 1px !important;
            color: #fff !important;
            border-radius: 10px !important;
            width: 100% !important;
        }

        /* FILTERS CSS */
        div[data-testid="stHorizontalBlock"]:has(.filter-marker-mob) {
            display: flex !important; flex-wrap: wrap !important; gap: 6px !important; margin-bottom: 20px !important;
            flex-direction: row !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.filter-marker-mob) > div {
            min-width: auto !important; width: auto !important; flex: 0 0 auto !important; padding: 0 !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.filter-marker-mob) button {
            border-radius: 10px !important; padding: 2px 10px !important; min-height: 28px !important; font-size: 11px !important; font-weight: bold !important; transition: 0.2s;
        }
        div[data-testid="stHorizontalBlock"]:has(.filter-marker-mob) button[kind="primary"] {
            background: #ffc107 !important; color: #000 !important; border: 1px solid #ffc107 !important; box-shadow: 0 0 8px rgba(255,193,7,0.3) !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.filter-marker-mob) button[kind="secondary"] {
            background: #1a1c20 !important; color: #777 !important; border: 1px solid #333 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("## 📊 Statistics Hub")
    
    mode = st.radio("Section:", ["🔥 Preflop", "🌊 Postflop"], horizontal=True, label_visibility="collapsed")
    is_postflop = (mode == "🌊 Postflop")
    
    cat_map, all_spots_names = get_spot_categories(is_postflop)
    df = fetch_history(is_postflop)
    
    hu_migration_map = {
        "SB pfr": "HU @ SB pfr",
        "BB def vs PFR": "HU @ BB def vs PFR",
        "SB def vs 3bet BB": "HU @ SB def vs 3bet",
        "SB def vs 3bet": "HU @ SB def vs 3bet",
        "BB def vs 4bet": "HU @ BB def vs 4bet"
    }

    if not df.empty and "Spot" in df.columns:
        df["Spot"] = df["Spot"].replace(hu_migration_map)
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
        df = df.dropna(subset=["Date"])
        df["Result"] = pd.to_numeric(df["Result"], errors='coerce').fillna(0).astype(int)
        df["Category"] = df["Spot"].apply(lambda x: cat_map.get(x, "Other"))
        available_cats = sorted(list(df["Category"].unique()))
    else:
        available_cats = []

    st.markdown("### 🎯 Filters")
    filter_key = f"active_filters_mob_{is_postflop}"
    if filter_key not in st.session_state:
        st.session_state[filter_key] = available_cats.copy()

    if available_cats:
        st.markdown("<div class='filter-marker-mob'></div>", unsafe_allow_html=True)
        cols = st.columns(len(available_cats))
        for i, cat in enumerate(available_cats):
            with cols[i]:
                is_active = cat in st.session_state[filter_key]
                if st.button(cat, key=f"f_mob_{cat}", type="primary" if is_active else "secondary"):
                    if is_active: st.session_state[filter_key].remove(cat)
                    else: st.session_state[filter_key].append(cat)
                    st.rerun()

    active_cats = st.session_state.get(filter_key, available_cats)
    filtered_df = df[df["Category"].isin(active_cats)] if not df.empty else pd.DataFrame()
    filtered_all_spots = [sp for sp in all_spots_names if cat_map.get(sp, "Other") in active_cats]

    if filtered_df.empty:
        st.info("No data for selected filters or history is empty. Go train, Boss.")
        return

    st.markdown(f"### 📈 Performance ({mode.split()[1]})")
    total_hands = len(filtered_df)
    total_correct = filtered_df["Result"].sum()
    winrate = (total_correct / total_hands * 100) if total_hands > 0 else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Hands", total_hands)
    c2.metric("Correct", total_correct)
    c3.metric("Accuracy", f"{winrate:.1f}%")

    st.markdown("### 🎯 Spots Mastery")
    stats = filtered_df.groupby("Spot")["Result"].agg(["count", "sum", "mean"]).reset_index()
    stats["Errors"] = stats["count"] - stats["sum"]
    stats["Accuracy"] = (stats["mean"] * 100).astype(int).astype(str) + "%"
    
    display_rename_map = {
        "BUvsCO": "3bet BUvsCO", "SBvsCO": "3bet SBvsCO", "SBvsBU": "3bet SBvsBU",
        "BBvsCO": "3bet BBvsCO", "BBvsBU": "3bet BBvsBU", "BBvsSB": "3bet BBvsSB"
    }

    display_df = stats.copy()
    if not is_postflop:
        display_df["Spot"] = display_df["Spot"].replace(display_rename_map)
        
    all_spots_sorted = display_df.sort_values(by="count", ascending=False)
    st.dataframe(all_spots_sorted[["Spot", "Errors", "Accuracy", "count"]].rename(columns={"count": "Total"}), use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("### 🚀 Road to Mastery (5k Hands)")
    st.caption("Check spots and click TRAIN SELECTED, or hit 🎯 for quick launch.")

    spot_counts = filtered_df["Spot"].value_counts().to_dict()
    merged_counts = {sp: 0 for sp in filtered_all_spots}
    for sp, cnt in spot_counts.items():
        if sp in merged_counts:
            merged_counts[sp] = cnt
        
    sorted_spots = sorted(merged_counts.items(), key=lambda x: x[1], reverse=True)

    col_btn, _ = st.columns([1, 1])
    with col_btn:
        st.markdown('<div class="train-btn">', unsafe_allow_html=True)
        if st.button("🚀 TRAIN SELECTED", use_container_width=True):
            selected = [sp for sp in filtered_all_spots if st.session_state.get(f"sel_{sp}", False)]
            start_training(selected, is_postflop)
        st.markdown('</div>', unsafe_allow_html=True)

    for sp, cnt in sorted_spots:
        pct = min(100, (cnt / 5000) * 100)
        
        if cnt < 100: grad, glow = "linear-gradient(90deg, #6c757d, #495057)", "rgba(108, 117, 125, 0.3)"
        elif cnt < 500: grad, glow = "linear-gradient(90deg, #198754, #20c997)", "rgba(32, 201, 151, 0.4)"
        elif cnt < 1500: grad, glow = "linear-gradient(90deg, #0dcaf0, #0d6efd)", "rgba(13, 202, 240, 0.5)"
        elif cnt < 3000: grad, glow = "linear-gradient(90deg, #6f42c1, #d63384)", "rgba(214, 51, 132, 0.5)"
        elif cnt < 5000: grad, glow = "linear-gradient(90deg, #dc3545, #fd7e14)", "rgba(253, 126, 20, 0.6)"
        else: grad, glow = "linear-gradient(90deg, #ffc107, #ffef96)", "rgba(255, 193, 7, 0.8)"

        disp_name = display_rename_map.get(sp, sp) if not is_postflop else sp

        c1, c2, c3 = st.columns([0.1, 0.12, 0.78], vertical_alignment="center")
        
        with c1:
            st.markdown('<div class="hide-checkbox-label">', unsafe_allow_html=True)
            st.checkbox(" ", key=f"sel_{sp}")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with c2:
            st.markdown('<div class="target-btn">', unsafe_allow_html=True)
            if st.button("🎯", key=f"go_{sp}"):
                start_training([sp], is_postflop)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with c3:
            html_out = f"<div style='display:flex; align-items:center; gap:8px; background:#16181c; padding:8px 12px; border-radius:10px; border:1px solid #2d3139; box-shadow:0 2px 4px rgba(0,0,0,0.2); width:100%; box-sizing:border-box;'><div style='flex:1 1 35%; min-width:0; color:#e9ecef; font-weight:800; font-size:11px; letter-spacing:0.02em; text-transform:uppercase; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;' title='{sp}'>{disp_name}</div><div style='flex:0 0 auto; color:#fff; font-weight:900; font-size:13px; text-align:right; font-variant-numeric:tabular-nums;'>{cnt}</div><div style='flex:1 1 45%; background:rgba(0,0,0,0.6); height:6px; border-radius:3px; box-shadow:inset 0 1px 3px rgba(0,0,0,0.8); position:relative; overflow:hidden;'><div style='width:{pct}%; height:100%; background:{grad}; border-radius:3px; box-shadow:0 0 10px {glow}; transition:width 0.5s ease-out;'></div></div><div style='flex:0 0 auto; color:#6c757d; font-weight:700; font-size:10px;'>5k</div></div>"
            st.markdown(html_out, unsafe_allow_html=True)

    st.divider()
    with st.expander("📜 Raw History Log"):
        d = df.copy()
        d["Result"] = d["Result"].apply(lambda x: "✅" if x==1 else "❌")
        d = d.sort_values("Date", ascending=False)
        d["Date"] = d["Date"].dt.strftime("%Y-%m-%d %H:%M:%S")
        cols_to_show = ["Date", "Spot", "Hand", "CorrectAction", "UserAction", "Result"] if "UserAction" in d.columns else ["Date", "Spot", "Hand", "CorrectAction", "Result"]
        st.dataframe(d[cols_to_show], use_container_width=True, hide_index=True)

    st.markdown("### 🚑 Data Recovery")
    with st.expander("Recover Spot Mastery from History", expanded=False):
        st.markdown("If your progress got reset, this will recalculate your experience, streak, and Spot Mastery from raw history.")
        if st.button("🔧 RECOVER SPOT MASTERY", use_container_width=True):
            df_hist = df.copy().sort_values("Date")
            new_mastery = {}
            total_correct = df_hist["Result"].sum()
            
            for _, row in df_hist.iterrows():
                sp = row["Spot"]
                if sp not in new_mastery: new_mastery[sp] = {"t": 0, "h": "", "d": ""}
                new_mastery[sp]["t"] += 1
                new_mastery[sp]["h"] += "1" if row["Result"] == 1 else "0"
                if len(new_mastery[sp]["h"]) > 100: new_mastery[sp]["h"] = new_mastery[sp]["h"][-100:]
                new_mastery[sp]["d"] = row["Date"].strftime("%Y-%m-%d")

            stats_dict = utils.load_user_stats(is_postflop=is_postflop)
            stats_dict["xp"] = int(total_correct * 10)
            stats_dict["total_hands"] = len(df_hist)
            stats_dict["spot_mastery"] = new_mastery
            
            utils.save_user_stats(stats_dict, is_postflop=is_postflop)
            st.success("✅ Recovery complete! Refresh the page.")
            st.rerun()

    st.markdown("### 🗑️ Danger Zone")
    with st.expander("Clear History", expanded=False):
        st.warning("⚠️ Warning: Clears ALL history globally (Preflop & Postflop).")
        d1, d2, d3, d4 = st.columns(4)
        if d1.button("Delete: 24 Hours", use_container_width=True): custom_delete_history(days=1); st.rerun()
        if d2.button("Delete: 7 Days", use_container_width=True): custom_delete_history(days=7); st.rerun()
        if d3.button("Delete: 30 Days", use_container_width=True): custom_delete_history(days=30); st.rerun()
        if d4.button("NUKE ALL", use_container_width=True): custom_delete_history(); st.rerun()
