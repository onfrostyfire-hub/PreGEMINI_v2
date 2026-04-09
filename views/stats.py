import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import poker_utils as utils

def show():
    st.markdown("## 📊 Statistics Hub")
    
    df = utils.load_history()
    
    if df.empty or "Date" not in df.columns or "Result" not in df.columns:
        st.info("History is empty. Go train, Boss!")
        return

    # Подмена старых названий спотов на новые (на лету, без насилия над базой данных)
    rename_map = {
        "BUvsCO": "3bet BUvsCO",
        "SBvsCO": "3bet SBvsCO",
        "SBvsBU": "3bet SBvsBU",
        "BBvsCO": "3bet BBvsCO",
        "BBvsBU": "3bet BBvsBU",
        "BBvsSB": "3bet BBvsSB"
    }
    df["Spot"] = df["Spot"].replace(rename_map)

    # Очистка и форматирование
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
    df = df.dropna(subset=["Date"])
    df["Result"] = pd.to_numeric(df["Result"], errors='coerce').fillna(0).astype(int)
    
    if df.empty:
        st.info("History is empty. Go train, Boss!")
        return

    st.markdown("### 📈 Performance")
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
    all_spots = stats.sort_values(by="count", ascending=False)
    st.dataframe(all_spots[["Spot", "Errors", "Accuracy", "count"]].rename(columns={"count": "Total"}), use_container_width=True, hide_index=True)

    # ==========================================
    # НОВЫЙ РАЗДЕЛ: GRIND PROGRESS (ROAD TO 5K)
    # ==========================================
    st.markdown("### 🚀 Road to Mastery (5k Hands)")
    
    # 1. Достаем все возможные споты из JSON файлов
    ranges_db = utils.load_ranges()
    all_spots_names = set()
    for src, sc_dict in ranges_db.items():
        for sc, sp_dict in sc_dict.items():
            for sp in sp_dict.keys():
                all_spots_names.add(sp)
                
    # 2. Берем количество сыгранных рук из истории
    spot_counts = df["Spot"].value_counts().to_dict()
    
    # 3. Скрещиваем базы
    merged_counts = {sp: 0 for sp in all_spots_names}
    for sp, cnt in spot_counts.items():
        merged_counts[sp] = cnt
        
    # 4. Сортируем по убыванию
    sorted_spots = sorted(merged_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Собираем чистый HTML
    html_out = '<div style="display:flex; flex-direction:column; gap:10px; margin-bottom: 20px;">'
    for sp, cnt in sorted_spots:
        pct = min(100, (cnt / 5000) * 100)
        
        if cnt < 100:
            grad = "linear-gradient(90deg, #6c757d, #495057)"
            glow = "rgba(108, 117, 125, 0.3)"
        elif cnt < 500:
            grad = "linear-gradient(90deg, #198754, #20c997)"
            glow = "rgba(32, 201, 151, 0.4)"
        elif cnt < 1500:
            grad = "linear-gradient(90deg, #0dcaf0, #0d6efd)"
            glow = "rgba(13, 202, 240, 0.5)"
        elif cnt < 3000:
            grad = "linear-gradient(90deg, #6f42c1, #d63384)"
            glow = "rgba(214, 51, 132, 0.5)"
        elif cnt < 5000:
            grad = "linear-gradient(90deg, #dc3545, #fd7e14)"
            glow = "rgba(253, 126, 20, 0.6)"
        else:
            grad = "linear-gradient(90deg, #ffc107, #ffef96)"
            glow = "rgba(255, 193, 7, 0.8)"
            
        html_out += f'''
        <div style="display:flex; align-items:center; gap:15px; background:#16181c; padding:12px 18px; border-radius:12px; border:1px solid #2d3139; box-shadow:0 4px 6px rgba(0,0,0,0.2);">
            <div style="flex:0 0 160px; color:#e9ecef; font-weight:800; font-size:13px; letter-spacing:0.05em; text-transform:uppercase; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="{sp}">{sp}</div>
            <div style="flex:0 0 45px; color:#fff; font-weight:900; font-size:15px; text-align:right; font-variant-numeric:tabular-nums;">{cnt}</div>
            <div style="flex:1; background:rgba(0,0,0,0.6); height:14px; border-radius:7px; box-shadow:inset 0 2px 4px rgba(0,0,0,0.8); position:relative; overflow:hidden;">
                <div style="width:{pct}%; height:100%; background:{grad}; border-radius:7px; box-shadow:0 0 12px {glow}; transition:width 0.5s ease-out;"></div>
            </div>
            <div style="flex:0 0 40px; color:#6c757d; font-weight:700; font-size:13px; text-align:right;">5000</div>
        </div>
        '''
    html_out += '</div>'
    
    st.markdown(html_out, unsafe_allow_html=True)
    # ==========================================


    with st.expander("📜 Raw History Log (click to expand)"):
        d = df.copy()
        d["Result"] = d["Result"].apply(lambda x: "✅" if x==1 else "❌")
        d = d.sort_values("Date", ascending=False)
        d["Date"] = d["Date"].dt.strftime("%Y-%m-%d %H:%M:%S")
        cols_to_show = ["Date", "Spot", "Hand", "CorrectAction", "UserAction", "Result"] if "UserAction" in d.columns else ["Date", "Spot", "Hand", "CorrectAction", "Result"]
        st.dataframe(d[cols_to_show], use_container_width=True, hide_index=True)

    st.divider()

    st.markdown("### 🚑 Data Recovery")
    with st.expander("Recover Spot Mastery from History", expanded=False):
        st.markdown("If your progress got reset, this will recalculate your experience, streak, and Spot Mastery from raw history.")
        
        if st.button("🔧 RECOVER SPOT MASTERY", use_container_width=True):
            df_hist = df.copy().sort_values("Date")
            new_mastery = {}
            total_correct = df_hist["Result"].sum()
            
            # Собираем уникальные даты для подсчета стрика
            unique_dates = sorted(df_hist["Date"].dt.date.unique())
            streak = 1
            if unique_dates:
                current_streak = 1
                for i in range(1, len(unique_dates)):
                    if (unique_dates[i] - unique_dates[i-1]).days == 1:
                        current_streak += 1
                    else:
                        current_streak = 1
                streak = current_streak

            # Восстанавливаем Spot Mastery
            ranges_db = utils.load_ranges()
            sp_to_full_key = {}
            for src, sc_dict in ranges_db.items():
                for sc, sp_dict in sc_dict.items():
                    for sp in sp_dict.keys():
                        sp_to_full_key[sp] = f"{src}|{sc}|{sp}"

            for _, row in df_hist.iterrows():
                sp = row["Spot"]
                if sp not in sp_to_full_key:
                    continue 
                    
                full_key = sp_to_full_key[sp]
                if full_key not in new_mastery:
                    new_mastery[full_key] = {"t": 0, "h": "", "d": ""}
                    
                new_mastery[full_key]["t"] += 1
                new_mastery[full_key]["h"] += "1" if row["Result"] == 1 else "0"
                if len(new_mastery[full_key]["h"]) > 100:
                    new_mastery[full_key]["h"] = new_mastery[full_key]["h"][-100:]
                new_mastery[full_key]["d"] = row["Date"].strftime("%Y-%m-%d")

            stats_dict = utils.load_user_stats()
            stats_dict["xp"] = int(total_correct * 10)
            stats_dict["total_hands"] = len(df_hist)
            stats_dict["streak"] = streak
            stats_dict["spot_mastery"] = new_mastery
            if unique_dates:
                stats_dict["last_date"] = unique_dates[-1].strftime("%Y-%m-%d")
                
            utils.save_user_stats(stats_dict)
            st.success("✅ Recovery complete! Refresh the page.")
            st.rerun()

    st.markdown("### 🗑️ Danger Zone")
    with st.expander("Clear History", expanded=False):
        d1, d2, d3, d4 = st.columns(4)
        if d1.button("Delete: 24 Hours", use_container_width=True):
            utils.delete_history(days=1); st.success("Done!"); st.rerun()
        if d2.button("Delete: 7 Days", use_container_width=True):
            utils.delete_history(days=7); st.success("Done!"); st.rerun()
        if d3.button("Delete: 30 Days", use_container_width=True):
            utils.delete_history(days=30); st.success("Done!"); st.rerun()
        if d4.button("NUKE ALL HISTORY", use_container_width=True):
            utils.delete_history(); st.success("Done!"); st.rerun()
