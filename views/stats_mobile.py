import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import poker_utils as utils
import json
import os

def fetch_history_direct(is_postflop):
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
        /* APPLE-TIER GLOBAL FIXES */
        .block-container { padding-top: 1.5rem !important; }
        
        /* FILTERS UI - APPLE GLASSMORPHISM */
        div[data-testid="stHorizontalBlock"]:has(.filter-marker) {
            display: flex !important; flex-direction: row !important; flex-wrap: wrap !important; gap: 8px !important;
            background: transparent !important; border: none !important; padding: 0 0 16px 0 !important; margin: 0 !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.filter-marker) > div[data-testid="column"] {
            flex: 0 0 auto !important; width: auto !important; min-width: 0 !important; padding: 0 !important; margin: 0 !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.filter-marker) div[data-testid="stButton"] button {
            border-radius: 20px !important; padding: 4px 16px !important; height: 32px !important; min-height: 32px !important;
            font-size: 13px !important; font-weight: 600 !important; letter-spacing: -0.2px !important;
            border: 1px solid rgba(255,255,255,0.08) !important; background: rgba(44,44,46,0.6) !important; color: #98989d !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important; transition: all 0.2s cubic-bezier(0.25, 1, 0.5, 1) !important;
            display: inline-flex !important; align-items: center !important; justify-content: center !important; margin: 0 !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.filter-marker) div[data-testid="stButton"] button:active { transform: scale(0.95) !important; }
        div[data-testid="stHorizontalBlock"]:has(.filter-marker) div[data-testid="stButton"] button[kind="primary"] {
            background: #ffcc00 !important; border-color: #ffcc00 !important; color: #1c1c1e !important; font-weight: 800 !important; 
            box-shadow: 0 4px 12px rgba(255, 204, 0, 0.4) !important;
        }

        /* MOBILE SPOTS ROW MASTERY - ELITE CARD UI */
        div[data-testid="stHorizontalBlock"]:has(.spot-row-marker-mob) {
            display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; align-items: center !important;
            background: rgba(28,28,30,0.6) !important; padding: 12px 14px !important; border-radius: 16px !important;
            border: 1px solid rgba(255,255,255,0.04) !important; margin-bottom: 8px !important; gap: 10px !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.15) !important; width: 100% !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.spot-row-marker-mob) > div[data-testid="column"] { margin: 0 !important; padding: 0 !important; min-width: 0 !important; width: auto !important; }
        div[data-testid="stHorizontalBlock"]:has(.spot-row-marker-mob) > div[data-testid="column"]:nth-child(1) { flex: 0 0 24px !important; }
        div[data-testid="stHorizontalBlock"]:has(.spot-row-marker-mob) > div[data-testid="column"]:nth-child(2) { flex: 0 0 36px !important; }
        div[data-testid="stHorizontalBlock"]:has(.spot-row-marker-mob) > div[data-testid="column"]:nth-child(3) { flex: 1 1 auto !important; }

        /* CHECKBOX FIX */
        .hide-checkbox-label div[data-testid="stCheckbox"] { display: flex !important; justify-content: center !important; align-items: center !important; margin: 0 !important; }
        .hide-checkbox-label div[data-testid="stCheckbox"] label { padding: 0 !important; min-height: 0 !important; }
        .hide-checkbox-label div[data-testid="stCheckbox"] p { display: none !important; }

        /* TARGET BUTTON FIX */
        .target-btn-wrap div[data-testid="stButton"] button {
            width: 36px !important; height: 36px !important; min-height: 36px !important; padding: 0 !important; margin: 0 !important;
            border-radius: 12px !important; border: 1px solid rgba(255,255,255,0.08) !important; background: rgba(255,255,255,0.04) !important;
            display: flex !important; justify-content: center !important; align-items: center !important; font-size: 16px !important;
            transition: all 0.2s ease !important;
        }
        .target-btn-wrap div[data-testid="stButton"] button:hover,
        .target-btn-wrap div[data-testid="stButton"] button:active {
            background: rgba(255,204,0,0.15) !important; border-color: rgba(255,204,0,0.5) !important; transform: scale(0.95) !important;
        }

        /* SPOT CARD HTML */
        .spot-card { display: flex; flex-direction: column; width: 100%; gap: 6px; justify-content: center; }
        .spot-header { display: flex; justify-content: space-between; align-items: center; width: 100%; }
        .spot-title { color: #f2f2f7; font-weight: 600; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; letter-spacing: -0.2px; flex: 1 1 auto; min-width: 0; padding-right: 10px; }
        .spot-count { color: #8e8e93; font-weight: 700; font-size: 13px; font-variant-numeric: tabular-nums; flex: 0 0 auto; text-align: right; }
        .spot-bar-bg { width: 100%; background: rgba(0,0,0,0.5); height: 8px; border-radius: 4px; overflow: hidden; box-shadow: inset 0 1px 3px rgba(0,0,0,0.8); }
        .spot-bar-fill { height: 100%; border-radius: 4px; transition: width 0.5s cubic-bezier(0.25, 1, 0.5, 1); }

        /* TRAIN BTN */
        .train-btn div[data-testid="stButton"] button {
            border-radius: 14px !important; background: linear-gradient(180deg, #ffcc00 0%, #e6b800 100%) !important;
            color: #1c1c1e !important; font-weight: 800 !important; border: none !important; height: 48px !important; min-height: 48px !important;
            box-shadow: 0 4px 14px rgba(255, 204, 0, 0.4) !important; letter-spacing: 0.5px !important; text-transform: uppercase !important;
        }
        .train-btn div[data-testid="stButton"] button:active { transform: scale(0.98) !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("## 📊 Statistics Hub")
    
    mode = st.radio("Section:", ["🔥 Preflop", "🌊 Postflop"], horizontal=True, label_visibility="collapsed")
    is_postflop = (mode == "🌊 Postflop")
    
    df = fetch_history_direct(is_postflop)

    cat_map = {}
    if is_postflop:
        pf_dir = 'postflop_data' if os.path.exists('postflop_data') else 'spots_data'
        if os.path.exists(pf_dir):
            for file in os.listdir(pf_dir):
                if file.endswith('.json'):
                    try:
                        with open(os.path.join(pf_dir, file), 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            scen = data.get("scenario", "Postflop")
                            if "spots" in data:
                                for k in data["spots"].keys(): cat_map[k] = scen
                            else:
                                for k in data.keys():
                                    if k not in ["scenario", "source"]: cat_map[k] = scen
                    except: pass
    else:
        try:
            ranges_db = utils.load_ranges()
            for src, sc_dict in ranges_db.items():
                for sc, sp_dict in sc_dict.items():
                    for sp in sp_dict.keys(): cat_map[sp] = sc
        except: pass
    
    # ЖЕСТКАЯ СКЛЕЙКА СТАРОЙ БАЗЫ С НОВЫМ JSON
    rename_map = {
        "BUvsCO": "3bet BUvsCO", "SBvsCO": "3bet SBvsCO", "SBvsBU": "3bet SBvsBU",
        "BBvsCO": "3bet BBvsCO", "BBvsBU": "3bet BBvsBU", "BBvsSB": "3bet BBvsSB",
        "SB pfr": "HU @ SB pfr",
        "BB def vs PFR": "HU @ BB def vs PFR",
        "SB def vs 3bet BB": "HU @ SB def vs 3bet",
        "SB def vs 3bet": "HU @ SB def vs 3bet",
        "BB def vs 4bet": "HU @ BB def vs 4bet"
    }

    if not df.empty and "Spot" in df.columns:
        df["Spot"] = df["Spot"].replace(rename_map)
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
        df = df.dropna(subset=["Date"])
        df["Result"] = pd.to_numeric(df["Result"], errors='coerce').fillna(0).astype(int)
        df["Category"] = df["Spot"].apply(lambda x: cat_map.get(x, "Other"))
        
        available_cats = sorted([c for c in df["Category"].unique() if c != "Other"])
        if "Other" in df["Category"].unique():
            available_cats.append("Other")
    else:
        available_cats = []

    st.markdown("### 🎯 Filters")
    filter_key = f"active_filters_v7_mob_{is_postflop}"
    if filter_key not in st.session_state:
        st.session_state[filter_key] = [] 

    if available_cats:
        st.markdown("<div class='filter-marker'></div>", unsafe_allow_html=True)
        cols = st.columns(len(available_cats))
        for i, cat in enumerate(available_cats):
            with cols[i]:
                is_active = cat in st.session_state[filter_key]
                if st.button(cat, key=f"f_mob_{cat}", type="primary" if is_active else "secondary"):
                    if is_active: st.session_state[filter_key].remove(cat)
                    else: st.session_state[filter_key].append(cat)
                    st.rerun()

    active_cats = st.session_state[filter_key]
    
    if active_cats:
        filtered_df = df[df["Category"].isin(active_cats)]
    else:
        filtered_df = df

    if filtered_df.empty:
        st.info("No history data to show. Go train, Boss.")
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
    
    all_spots_sorted = stats.sort_values(by="count", ascending=False)
    st.dataframe(all_spots_sorted[["Spot", "Errors", "Accuracy", "count"]].rename(columns={"count": "Total"}), use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("### 🚀 Road to Mastery (5k Hands)")
    st.caption("Check spots and click TRAIN SELECTED, or hit 🎯 for quick launch.")

    spot_counts = filtered_df["Spot"].value_counts().to_dict()
    sorted_spots = sorted(spot_counts.items(), key=lambda x: x[1], reverse=True)

    col_btn, _ = st.columns([1, 1])
    with col_btn:
        st.markdown('<div class="train-btn">', unsafe_allow_html=True)
        if st.button("🚀 TRAIN SELECTED", use_container_width=True):
            selected = [sp for sp, _ in sorted_spots if st.session_state.get(f"sel_{sp}", False)]
            start_training(selected, is_postflop)
        st.markdown('</div>', unsafe_allow_html=True)

    for sp, cnt in sorted_spots:
        pct = min(100, (cnt / 5000) * 100)
        
        # ВОЗВРАЩЕНЫ ОРИГИНАЛЬНЫЕ ЦВЕТА
        if cnt < 100: grad, glow = "linear-gradient(90deg, #6c757d, #495057)", "rgba(108, 117, 125, 0.3)"
        elif cnt < 500: grad, glow = "linear-gradient(90deg, #198754, #20c997)", "rgba(32, 201, 151, 0.4)"
        elif cnt < 1500: grad, glow = "linear-gradient(90deg, #0dcaf0, #0d6efd)", "rgba(13, 202, 240, 0.5)"
        elif cnt < 3000: grad, glow = "linear-gradient(90deg, #6f42c1, #d63384)", "rgba(214, 51, 132, 0.5)"
        elif cnt < 5000: grad, glow = "linear-gradient(90deg, #dc3545, #fd7e14)", "rgba(253, 126, 20, 0.6)"
        else: grad, glow = "linear-gradient(90deg, #ffc107, #ffef96)", "rgba(255, 193, 7, 0.8)"

        c1, c2, c3 = st.columns(3) 
        
        with c1:
            st.markdown("<div class='spot-row-marker-mob'></div><div class='hide-checkbox-label'>", unsafe_allow_html=True)
            st.checkbox(" ", key=f"sel_{sp}")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with c2:
            st.markdown("<div class='target-btn-wrap'>", unsafe_allow_html=True)
            if st.button("🎯", key=f"go_{sp}"): start_training([sp], is_postflop)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with c3:
            html = f"""
            <div class='spot-card'>
                <div class='spot-header'>
                    <div class='spot-title' title='{sp}'>{sp}</div>
                    <div class='spot-count'>{cnt}</div>
                </div>
                <div class='spot-bar-bg'>
                    <div class='spot-bar-fill' style='width:{pct}%; background:{grad}; box-shadow: 0 0 10px {glow};'></div>
                </div>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)

    st.divider()
    with st.expander("📜 Raw History Log"):
        if not filtered_df.empty:
            d = filtered_df.copy()
            d["Result"] = d["Result"].apply(lambda x: "✅" if x==1 else "❌")
            d = d.sort_values("Date", ascending=False)
            d["Date"] = d["Date"].dt.strftime("%Y-%m-%d %H:%M:%S")
            cols_to_show = ["Date", "Spot", "Hand", "CorrectAction", "UserAction", "Result"] if "UserAction" in d.columns else ["Date", "Spot", "Hand", "CorrectAction", "Result"]
            st.dataframe(d[cols_to_show], use_container_width=True, hide_index=True)

    st.markdown("### 🚑 Data Recovery")
    with st.expander("Recover Spot Mastery from History", expanded=False):
        st.markdown("If your progress got reset, this will recalculate your experience, streak, and Spot Mastery from raw history.")
        if st.button("🔧 RECOVER SPOT MASTERY", use_container_width=True):
            if not df.empty:
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
