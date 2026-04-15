import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import poker_utils as utils
import json
import os

def show():
    st.markdown("## 📊 Statistics Hub")
    
    st.markdown("""
    <style>
    div[data-testid="stRadio"] > div {
        background: #141518;
        padding: 6px;
        border-radius: 10px;
        border: 1px solid #3a3d42;
        display: flex;
        gap: 6px;
    }
    div[data-testid="stRadio"] label {
        background: #1c1e22;
        padding: 12px 20px;
        border-radius: 6px;
        cursor: pointer;
        flex: 1;
        text-align: center;
        justify-content: center;
        border: 1px solid transparent;
        transition: all 0.2s ease;
    }
    div[data-testid="stRadio"] label[data-checked="true"] {
        background: #2a2d32 !important;
        border-color: #ffc107 !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5), inset 0 2px 4px rgba(255,255,255,0.05);
    }
    div[data-testid="stRadio"] p {
        font-size: 15px;
        font-weight: 900;
        margin: 0;
        color: #888;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    div[data-testid="stRadio"] label[data-checked="true"] p {
        color: #ffc107 !important;
        text-shadow: 0 0 10px rgba(255,193,7,0.3);
    }
    </style>
    """, unsafe_allow_html=True)
    
    mode = st.radio("Category", ["🔥 Preflop", "🌊 Postflop"], horizontal=True, label_visibility="collapsed")
    is_postflop = (mode == "🌊 Postflop")
    
    df_all = utils.load_history()
    
    if df_all.empty or "Date" not in df_all.columns or "Result" not in df_all.columns:
        st.info("History is empty. Go train, Boss!")
        return

    # Подмена старых названий префлоп-спотов на новые
    rename_map = {
        "BUvsCO": "3bet BUvsCO",
        "SBvsCO": "3bet SBvsCO",
        "SBvsBU": "3bet SBvsBU",
        "BBvsCO": "3bet BBvsCO",
        "BBvsBU": "3bet BBvsBU",
        "BBvsSB": "3bet BBvsSB"
    }
    df_all["Spot"] = df_all["Spot"].replace(rename_map)

    df_all["Date"] = pd.to_datetime(df_all["Date"], errors='coerce')
    df_all = df_all.dropna(subset=["Date"])
    df_all["Result"] = pd.to_numeric(df_all["Result"], errors='coerce').fillna(0).astype(int)
    
    # Жесткое разделение потоков (Постфлоп споты содержат символ "|")
    if is_postflop:
        df = df_all[df_all["Spot"].str.contains(r'\|', regex=False, na=False)]
        try:
            with open("postflop_stats.json", "r") as f: stats_dict = json.load(f)
        except:
            stats_dict = {"xp": 0, "combo": 0, "shields": 0, "spot_mastery": {}}
    else:
        df = df_all[~df_all["Spot"].str.contains(r'\|', regex=False, na=False)]
        stats_dict = utils.load_user_stats()

    if df.empty:
        st.info(f"No {mode.replace('🔥 ', '').replace('🌊 ', '')} history yet. Hit the tables!")
        return

    st.markdown(f"### 📈 Performance ({mode.replace('🔥 ', '').replace('🌊 ', '')})")
    
    total_hands = len(df)
    total_correct = df["Result"].sum()
    winrate = (total_correct / total_hands * 100) if total_hands > 0 else 0
    
    rank_name, next_xp = utils.get_rank_info(stats_dict.get("xp", 0))
    xp = stats_dict.get("xp", 0)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Hands Played", f"{total_hands}")
    c2.metric("Winrate", f"{winrate:.1f}%")
    c3.metric("Current Rank", rank_name)
    c4.metric("XP Bank", f"${xp}")
    
    if next_xp != "MAX":
        prog = int(xp / next_xp * 100)
        st.markdown(f"<div style='font-size:12px; color:#aaa; margin-bottom:5px;'>Progress to next rank ({next_xp} XP): <b>{prog}%</b></div>", unsafe_allow_html=True)
        st.progress(prog / 100.0)
    else:
        st.markdown("<div style='font-size:12px; color:#ffc107; margin-bottom:5px; font-weight:bold;'>MAX RANK ACHIEVED</div>", unsafe_allow_html=True)
        st.progress(1.0)
        
    st.markdown("---")
    st.markdown("### 🎯 Spot Mastery (Road to 5000)")
    
    mastery = stats_dict.get("spot_mastery", {})
    if not mastery:
        st.write("No mastery data yet. Play more hands.")
    else:
        # Сортируем споты по количеству сыгранных раздач
        sorted_mastery = sorted(mastery.items(), key=lambda item: item[1].get("t", 0), reverse=True)
        for spot_name, data in sorted_mastery:
            info = utils.get_spot_mastery_info(data)
            
            t = info["total"]
            pct = info["prog_pct"]
            c = info["color"]
            i = info["icon"]
            n = info["name"]
            
            st.markdown(f"<div style='font-size:14px; font-weight:bold; margin-bottom:5px; color:#ddd;'>{spot_name}</div>", unsafe_allow_html=True)
            
            cols = st.columns([1.5, 4, 1])
            with cols[0]:
                st.markdown(f"<div style='color:{c}; font-weight:900; font-size:13px; text-transform:uppercase;'>{i} {n}</div>", unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f"""
                    <div style="width:100%; height:14px; background:#1a1c20; border-radius:7px; overflow:hidden; border:1px solid #3a3d42; margin-top:4px; box-shadow: inset 0 1px 3px rgba(0,0,0,0.5);">
                        <div style="width:{pct}%; height:100%; background:{c}; box-shadow: 0 0 10px {c}aa;"></div>
                    </div>
                """, unsafe_allow_html=True)
            with cols[2]:
                st.markdown(f"<div style='text-align:right; font-size:13px; color:#888; margin-top:2px; font-weight:bold;'>{t} / {info['next']}</div>", unsafe_allow_html=True)
            
            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🛠️ Danger Zone")
    with st.expander("History & Recovery", expanded=False):
        st.warning("⚠️ Warning: Deleting history removes data for ALL modes (Preflop & Postflop) globally.")
        d1, d2, d3 = st.columns(3)
        if d1.button("Delete 24h", use_container_width=True):
            utils.delete_history(days=1); st.success("Done!"); st.rerun()
        if d2.button("Delete 7 Days", use_container_width=True):
            utils.delete_history(days=7); st.success("Done!"); st.rerun()
        if d3.button("Wipe ALL", use_container_width=True):
            utils.delete_history(); st.success("Wiped!"); st.rerun()
            
        st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
        st.markdown(f"**Recalculate {mode.replace('🔥 ', '').replace('🌊 ', '')} Mastery & XP (From History)**")
        
        if st.button(f"Recover {mode.replace('🔥 ', '').replace('🌊 ', '')} Stats", use_container_width=True):
            new_mastery = {}
            df_sorted = df.sort_values("Date")
            total_c = 0
            streak = 1
            unique_dates = []
            
            for _, row in df_sorted.iterrows():
                full_key = row["Spot"]
                if full_key not in new_mastery:
                    new_mastery[full_key] = {"t": 0, "h": "", "d": ""}
                
                new_mastery[full_key]["t"] += 1
                res = row["Result"]
                total_c += res
                new_mastery[full_key]["h"] += "1" if res == 1 else "0"
                if len(new_mastery[full_key]["h"]) > 100:
                    new_mastery[full_key]["h"] = new_mastery[full_key]["h"][-100:]
                
                d_str = row["Date"].strftime("%Y-%m-%d")
                new_mastery[full_key]["d"] = d_str
                
                d_obj = row["Date"].date()
                if not unique_dates or unique_dates[-1] != d_obj:
                    if unique_dates and (d_obj - unique_dates[-1]).days == 1:
                        streak += 1
                    elif unique_dates and (d_obj - unique_dates[-1]).days > 1:
                        streak = 1
                    unique_dates.append(d_obj)

            stats_dict["xp"] = int(total_c * 10)
            stats_dict["total_hands"] = len(df)
            stats_dict["streak"] = streak
            stats_dict["spot_mastery"] = new_mastery
            if unique_dates:
                stats_dict["last_date"] = unique_dates[-1].strftime("%Y-%m-%d")
            
            if is_postflop:
                with open("postflop_stats.json", "w") as f: json.dump(stats_dict, f)
            else:
                utils.save_user_stats(stats_dict)
                
            st.success("✅ Recovery complete! Refresh the page.")
            st.rerun()
