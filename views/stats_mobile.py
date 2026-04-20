import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import poker_utils as utils
import json
import os

def get_spot_metadata(is_postflop):
    directory = 'postflop_data' if is_postflop else 'spots_data'
    meta = {}
    categories = set()
    rename_map = {
        "SB pfr": "HU @ SB pfr",
        "BB def vs SB": "HU @ BB def vs SB",
        "BB def vs BU": "HU @ BB def vs BU",
        "CO pfr": "HU @ CO pfr",
        "BTN pfr": "HU @ BTN pfr"
    }
    
    if os.path.exists(directory):
        for file in os.listdir(directory):
            if file.endswith('.json'):
                try:
                    with open(os.path.join(directory, file), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if "spots" in data:
                            scen = data.get("scenario", "Other")
                            categories.add(scen)
                            for k in data["spots"].keys(): meta[k] = scen
                        else:
                            scen = data.get("scenario", "Postflop")
                            categories.add(scen)
                            for k in data.keys():
                                if k not in ["scenario", "source"]: meta[k] = scen
                except: pass
    return meta, sorted(list(categories)), rename_map

@st.cache_data(ttl=60)
def fetch_history(is_postflop):
    sheets = utils.get_worksheets()
    df = pd.DataFrame(columns=["Date", "Spot", "Hand", "Result", "CorrectAction", "UserAction"])
    ws_name = "PostflopHistory" if is_postflop else "History"
    
    if ws_name in sheets:
        try:
            vals = sheets[ws_name].get_all_values()
            if vals and len(vals) > 1:
                headers = vals[0]
                if "UserAction" not in headers:
                    headers.append("UserAction")
                    for r in vals[1:]: r.append("UNKNOWN")
                df = pd.DataFrame(vals[1:], columns=headers)
                df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
                df["Result"] = pd.to_numeric(df["Result"], errors='coerce')
        except: pass
    return df

def custom_delete_history(is_postflop, hours=None):
    sheets = utils.get_worksheets()
    ws_name = "PostflopHistory" if is_postflop else "History"
    if ws_name in sheets:
        try:
            if hours is None:
                sheets[ws_name].clear()
                sheets[ws_name].append_row(["Date", "Spot", "Hand", "Result", "CorrectAction", "UserAction"])
            else:
                df = fetch_history(is_postflop)
                if not df.empty:
                    cutoff = datetime.now() - timedelta(hours=hours)
                    df = df[df["Date"] < cutoff]
                    sheets[ws_name].clear()
                    headers = ["Date", "Spot", "Hand", "Result", "CorrectAction", "UserAction"]
                    sheets[ws_name].append_row(headers)
                    if not df.empty:
                        df["Date"] = df["Date"].dt.strftime("%Y-%m-%d %H:%M:%S")
                        sheets[ws_name].append_rows(df[headers].values.tolist())
            fetch_history.clear()
        except: pass

def show():
    is_postflop = st.session_state.get("actual_app_mode") == "Postflop"
    meta, available_cats, rename_map = get_spot_metadata(is_postflop)
    
    df_hist = fetch_history(is_postflop)
    if not df_hist.empty:
        df_hist["Spot"] = df_hist["Spot"].apply(lambda x: rename_map.get(x, x))
        df_hist["Category"] = df_hist["Spot"].apply(lambda x: meta.get(x, "Archived"))
        cats_in_data = sorted(list(df_hist["Category"].unique()))
    else:
        cats_in_data = []

    if f"active_cats_mob_{is_postflop}" not in st.session_state:
        st.session_state[f"active_cats_mob_{is_postflop}"] = cats_in_data.copy()

    st.markdown('### 🎯 Filters')
    st.markdown('<div class="filter-row-marker"></div>', unsafe_allow_html=True)
    st.markdown('''<style>
    div:has(> .filter-row-marker) + div[data-testid="stHorizontalBlock"] {
        display: flex !important; flex-wrap: wrap !important; gap: 6px !important; margin-bottom: 20px !important;
    }
    div:has(> .filter-row-marker) + div[data-testid="stHorizontalBlock"] > div {
        min-width: auto !important; width: auto !important; flex: 0 0 auto !important; padding: 0 !important;
    }
    div:has(> .filter-row-marker) + div[data-testid="stHorizontalBlock"] button {
        border-radius: 14px !important; padding: 2px 12px !important; min-height: 28px !important; font-size: 12px !important; font-weight: 800 !important; transition: 0.2s;
    }
    div:has(> .filter-row-marker) + div[data-testid="stHorizontalBlock"] button[kind="primary"] {
        background: #ffc107 !important; color: #000 !important; border: 1px solid #ffc107 !important; box-shadow: 0 0 8px rgba(255,193,7,0.4) !important;
    }
    div:has(> .filter-row-marker) + div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
        background: #1a1c20 !important; color: #777 !important; border: 1px solid #333 !important;
    }
    </style>''', unsafe_allow_html=True)

    if cats_in_data:
        cols = st.columns(len(cats_in_data))
        for i, cat in enumerate(cats_in_data):
            with cols[i]:
                is_act = cat in st.session_state[f"active_cats_mob_{is_postflop}"]
                if st.button(cat, key=f"fm_{cat}_{is_postflop}", type="primary" if is_act else "secondary"):
                    if is_act: st.session_state[f"active_cats_mob_{is_postflop}"].remove(cat)
                    else: st.session_state[f"active_cats_mob_{is_postflop}"].append(cat)
                    st.rerun()

    if not df_hist.empty and st.session_state[f"active_cats_mob_{is_postflop}"]:
        f_df = df_hist[df_hist["Category"].isin(st.session_state[f"active_cats_mob_{is_postflop}"])]
    else:
        f_df = pd.DataFrame(columns=df_hist.columns)

    st.markdown("### 🏆 Road to Mastery")
    total_hands = len(f_df)
    progress = min(total_hands / 5000.0, 1.0)
    st.progress(progress)
    st.caption(f"{total_hands} / 5000 hands processed (Filtered)")

    st.markdown("### 📊 Spot Mastery")
    st.markdown('<div class="spot-row-marker-mob"></div>', unsafe_allow_html=True)
    st.markdown('''<style>
    div:has(> .spot-row-marker-mob) + div[data-testid="stHorizontalBlock"] {
        display: flex !important; flex-direction: row !important; align-items: center !important; margin-bottom: 10px !important;
    }
    div:has(> .spot-row-marker-mob) + div[data-testid="stHorizontalBlock"] > div:nth-child(1) { width: 75% !important; flex: 1 1 75% !important; }
    div:has(> .spot-row-marker-mob) + div[data-testid="stHorizontalBlock"] > div:nth-child(2) { width: 25% !important; flex: 1 1 25% !important; padding-left: 5px !important; }
    div:has(> .spot-row-marker-mob) + div[data-testid="stHorizontalBlock"] button {
        height: 48px !important; border-radius: 8px !important; padding: 0 !important; font-size: 11px !important; font-weight: 900 !important;
    }
    </style>''', unsafe_allow_html=True)

    if f_df.empty:
        st.info("Глухо. Меняй фильтры.")
    else:
        for spot, group in f_df.groupby("Spot"):
            correct = group["Result"].sum()
            total = len(group)
            wr = int((correct / total) * 100) if total > 0 else 0
            
            color = "#dc3545" if wr < 70 else "#ffc107" if wr < 85 else "#28a745"
            
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f'''
                <div style="background:#1e2126; padding:8px 12px; border-radius:8px; border-left:3px solid {color}; box-shadow: 0 2px 4px rgba(0,0,0,0.4); height: 48px; display:flex; flex-direction:column; justify-content:center;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                        <strong style="color:#e0e0e0; font-size:12px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:70%;">{spot}</strong>
                        <span style="color:{color}; font-weight:900; font-size:12px;">{wr}%</span>
                    </div>
                    <div style="background:#000; height:6px; border-radius:3px; overflow:hidden;">
                        <div style="width:{wr}%; background:{color}; height:100%;"></div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            with c2:
                if st.button("TRAIN", key=f"tm_{spot}", use_container_width=True):
                    settings = utils.load_user_settings(is_postflop=is_postflop)
                    settings["selected_spots"] = [spot]
                    utils.save_user_settings(settings, is_postflop=is_postflop)
                    st.cache_data.clear()
                    st.success("✔️")

    st.markdown("---")
    st.markdown("### 🗑️ Danger Zone")
    with st.expander("Clear & Recover", expanded=False):
        if st.button("Recalculate Global XP", use_container_width=True):
            if not df_hist.empty:
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
                st.success("✅ Done.")

        d1, d2 = st.columns(2)
        if d1.button("Delete 24h", use_container_width=True): custom_delete_history(is_postflop, 24); st.rerun()
        if d2.button("NUKE ALL", type="primary", use_container_width=True): custom_delete_history(is_postflop, None); st.rerun()
