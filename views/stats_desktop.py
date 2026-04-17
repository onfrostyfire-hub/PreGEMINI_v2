import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import poker_utils as utils
import json
import os

def load_postflop_keys():
    db = {}
    pf_dir = 'postflop_data' if os.path.exists('postflop_data') else 'spots_data'
    if not os.path.exists(pf_dir): return db
    for file in os.listdir(pf_dir):
        if file.endswith('.json'):
            with open(os.path.join(pf_dir, file), 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    if "spots" in data:
                        db.update(data["spots"])
                    else:
                        db.update(data)
                except: pass
    return db

@st.cache_data(ttl=60)
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
                        for r in vals[1:]: r.append("UNKNOWN")
                    df_pf = pd.DataFrame(vals[1:], columns=headers)
            except: pass
        elif os.path.exists("postflop_history.csv"):
            try:
                df_pf = pd.read_csv("postflop_history.csv", header=None)
                if df_pf.iloc[0, 0] == "Date":
                    df_pf.columns = df_pf.iloc[0]
                    df_pf = df_pf[1:]
                else:
                    df_pf.columns = ["Date", "Spot", "Hand", "Result", "CorrectAction", "UserAction"]
            except: pass
        return df_pf
    else:
        df_pr = utils.load_history()
        if df_pr.empty: return df_pr
        return df_pr[~df_pr["Spot"].astype(str).str.contains('|', regex=False, na=False)].copy()

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
                    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
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
                if df.iloc[0]["Date"] == "Date": df = df[1:]
                df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
                cutoff = datetime.now() - timedelta(days=days)
                df_new = df[df["Date"] >= cutoff]
                df_new.to_csv("postflop_history.csv", index=False, header=True)
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
        div[data-testid="stButton"] button[kind="primary"] {
            height: 44px !important; background: linear-gradient(180deg, #1c3a55 0%, #102436 100%) !important;
            border: none !important; font-weight: 900 !important; letter-spacing: 1px !important;
        }
        
        .spot-row-marker { display: none; }
        
        div[data-testid="stHorizontalBlock"]:has(.spot-row-marker) {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
            background: #16181c !important;
            padding: 8px 12px !important;
            border-radius: 12px !important;
            border: 1px solid #2d3139 !important;
            margin-bottom: 8px !important;
            gap: 8px !important;
            width: 100% !important;
            grid-template-columns: none !important;
        }
        
        div[data-testid="stHorizontalBlock"]:has(.spot-row-marker) > div[data-testid="column"] {
            width: auto !important; min-width: 0 !important; margin: 0 !important; padding: 0 !important;
        }
        
        div[data-testid="stHorizontalBlock"]:has(.spot-row-marker) > div[data-testid="column"]:nth-child(1) { flex: 0 0 20px !important; }
        div[data-testid="stHorizontalBlock"]:has(.spot-row-marker) > div[data-testid="column"]:nth-child(2) { flex: 0 0 32px !important; }
        div[data-testid="stHorizontalBlock"]:has(.spot-row-marker) > div[data-testid="column"]:nth-child(3) { flex: 1 1 35% !important; overflow: hidden; }
        div[data-testid="stHorizontalBlock"]:has(.spot-row-marker) > div[data-testid="column"]:nth-child(4) { flex: 0 0 30px !important; text-align: right; }
        div[data-testid="stHorizontalBlock"]:has(.spot-row-marker) > div[data-testid="column"]:nth-child(5) { flex: 1 1 35% !important; }
        div[data-testid="stHorizontalBlock"]:has(.spot-row-marker) > div[data-testid="column"]:nth-child(6) { flex: 0 0 25px !important; text-align: right; }
        
        div[data-testid="stHorizontalBlock"]:has(.spot-row-marker) div[data-testid="stButton"] button {
            height: 28px !important; width: 28px !important; min-height: 28px !important; padding: 0 !important;
            border-radius: 6px !important; font-size: 14px !important; line-height: 1 !important;
            background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.1) !important;
            display: flex; justify-content: center; align-items: center;
        }
        div[data-testid="stHorizontalBlock"]:has(.spot-row-marker) div[data-testid="stButton"] button:hover {
            border-color: #ffc107 !important; background: rgba(255,193,7,0.1) !important;
        }
        
        div[data-testid="stHorizontalBlock"]:has(.spot-row-marker) div[data-testid="stCheckbox"] {
            margin: 0 !important; padding: 0 !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.spot-row-marker) div[data-testid="stCheckbox"] label {
            padding: 0 !important; min-height: 0 !important;
        }

        .mastery-name {
            color: #e9ecef; font-weight: 800; font-size: 11px;
            text-transform: uppercase; white-space: nowrap;
            overflow: hidden; text-overflow: ellipsis; line-height: 1.2; margin: 0;
        }
        .mastery-count {
            color: #fff; font-weight: 900; font-size: 12px;
            font-variant-numeric: tabular-nums; line-height: 1.2; margin: 0;
        }
        .mastery-max {
            color: #6c757d; font-size: 10px; font-weight: 700; line-height: 1.2; margin: 0;
        }
        .mastery-bar-container {
            width: 100%; background: rgba(0,0,0,0.6); height: 6px; border-radius: 3px; overflow: hidden; box-shadow: inset 0 1px 3px rgba(0,0,0,0.8); margin-top: 1px;
        }
        .mastery-bar-fill { height: 100%; border-radius: 3px; transition: width 0.5s ease-out; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("## 📊 Statistics Hub")
    
    mode = st.radio("Section:", ["🔥 Preflop", "🌊 Postflop"], horizontal=True, label_visibility="collapsed")
    is_postflop = (mode == "🌊 Postflop")
    
    df = fetch_history(is_postflop)
    
    # ЖЕСТКАЯ ПОДМЕНА ИМЕН ДЛЯ HU И СТАРЫХ СПОТОВ В ИСТОРИИ
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

    if df.empty or "Date" not in df.columns or "Result" not in df.columns:
        st.info(f"History for {mode.split()[1]} is empty. Go train, Boss.")
        return
    
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
    df = df.dropna(subset=["Date"])
    df["Result"] = pd.to_numeric(df["Result"], errors='coerce').fillna(0).astype(int)

    st.markdown(f"### 📈 Performance ({mode.split()[1]})")
    total_hands = len(df)
    total_correct = df["Result"].sum()
    winrate = (total_correct / total_hands * 100) if total_hands > 0 else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Hands", total_hands)
    c2.metric("Correct", total_correct)
    c3.metric("Accuracy", f"{winrate:.1f}%")

    st.markdown("### 🎯 Spots Mastery")
    stats = df.groupby("Spot")["Result"].agg(["count", "sum", "mean"]).reset_index()
    stats["Errors"] = stats["count"] - stats["sum"]
    stats["Accuracy"] = (stats["mean"] * 100).astype(int).astype(str) + "%"
    
    all_spots_sorted = stats.sort_values(by="count", ascending=False)
    st.dataframe(all_spots_sorted[["Spot", "Errors", "Accuracy", "count"]].rename(columns={"count": "Total"}), use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("### 🚀 Road to Mastery (5k Hands)")
    st.caption("Check spots and click TRAIN SELECTED, or hit 🎯 for quick launch.")

    all_spots_names = set()
    if is_postflop:
        pf_db = load_postflop_keys()
        for sp in pf_db.keys(): all_spots_names.add(sp)
    else:
        ranges_db = utils.load_ranges()
        for src, sc_dict in ranges_db.items():
            for sc, sp_dict in sc_dict.items():
                for sp in sp_dict.keys(): all_spots_names.add(sp)
                
    spot_counts = df["Spot"].value_counts().to_dict()
    merged_counts = {sp: 0 for sp in all_spots_names}
    for sp, cnt in spot_counts.items(): merged_counts[sp] = cnt
        
    sorted_spots = sorted(merged_counts.items(), key=lambda x: x[1], reverse=True)

    col_btn, col_info = st.columns([1, 2])
    with col_btn:
        if st.button("🚀 TRAIN SELECTED", use_container_width=True, type="primary"):
            selected = [sp for sp in all_spots_names if st.session_state.get(f"sel_{sp}", False)]
            start_training(selected, is_postflop)

    for sp, cnt in sorted_spots:
        pct = min(100, (cnt / 5000) * 100)
        
        if cnt < 100: grad, glow = "linear-gradient(90deg, #6c757d, #495057)", "rgba(108, 117, 125, 0.3)"
        elif cnt < 500: grad, glow = "linear-gradient(90deg, #198754, #20c997)", "rgba(32, 201, 151, 0.4)"
        elif cnt < 1500: grad, glow = "linear-gradient(90deg, #0dcaf0, #0d6efd)", "rgba(13, 202, 240, 0.5)"
        elif cnt < 3000: grad, glow = "linear-gradient(90deg, #6f42c1, #d63384)", "rgba(214, 51, 132, 0.5)"
        elif cnt < 5000: grad, glow = "linear-gradient(90deg, #dc3545, #fd7e14)", "rgba(253, 126, 20, 0.6)"
        else: grad, glow = "linear-gradient(90deg, #ffc107, #ffef96)", "rgba(255, 193, 7, 0.8)"

        c1, c2, c3, c4, c5, c6 = st.columns(6, vertical_alignment="center")
        
        with c1:
            st.markdown("<div class='spot-row-marker'></div>", unsafe_allow_html=True)
            st.checkbox("", key=f"sel_{sp}", label_visibility="collapsed")
        with c2:
            if st.button("🎯", key=f"go_{sp}", help=f"Train {sp}"): start_training([sp], is_postflop)
        with c3:
            st.markdown(f"<div class='mastery-name' title='{sp}'>{sp}</div>", unsafe_allow_html=True)
        with c4:
            st.markdown(f"<div class='mastery-count'>{cnt}</div>", unsafe_allow_html=True)
        with c5:
            st.markdown(f"""
                <div class='mastery-bar-container'>
                    <div class='mastery-bar-fill' style='width:{pct}%; background:{grad}; box-shadow:0 0 10px {glow};'></div>
                </div>
            """, unsafe_allow_html=True)
        with c6:
            st.markdown("<div class='mastery-max'>5k</div>", unsafe_allow_html=True)

    st.divider()
    with st.expander("📜 Raw History Log"):
        d = df.copy()
        d["Result"] = d["Result"].apply(lambda x: "✅" if x==1 else "❌")
        d = d.sort_values("Date", ascending=False)
        d["Date"] = d["Date"].dt.strftime("%Y-%m-%d %H:%M:%S")
        cols_to_show = ["Date", "Spot", "Hand", "CorrectAction", "UserAction", "Result"] if "UserAction" in d.columns else ["Date", "Spot", "Hand", "CorrectAction", "Result"]
        st.dataframe(d[cols_to_show], use_container_width=True, hide_index=True)

    st.markdown("### 🚑 Data Recovery")
    with st.expander(f"Recover Spot Mastery from History", expanded=False):
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
