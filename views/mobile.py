import streamlit as st
import random
from datetime import datetime
import poker_utils as utils

def show():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@500;700;900&display=swap');

        /* 1. ПОДНИМАЕМ ВСЁ ВВЕРХ И УБИРАЕМ СКРЫТЫЕ ОТСТУПЫ */
        .block-container { padding-top: 0.2rem !important; padding-bottom: 0.5rem !important; max-width: 100% !important; overflow-x: hidden !important; }
        div.element-container { margin-bottom: 0 !important; }
        div[data-testid="stVerticalBlock"] > div { padding-top: 0 !important; padding-bottom: 0 !important; margin-bottom: 0 !important; }

        /* 2. СЖИМАЕМ МЕНЮ ИЗ app.py СТРОГО В ОДНУ СТРОКУ */
        div[role="radiogroup"] { flex-wrap: nowrap !important; gap: 2px !important; justify-content: center !important; margin-bottom: -15px !important; }
        div[role="radiogroup"] label { padding: 4px 8px !important; min-height: 20px !important; }
        div[role="radiogroup"] label p { font-size: 12px !important; white-space: nowrap !important; }

        /* 3. СЖИМАЕМ ЭКСПАНДЕР (Spot Filters) И ОТСТУПЫ ВОКРУГ НЕГО */
        div[data-testid="stExpander"] { margin-top: -10px !important; margin-bottom: -5px !important; }
        details[data-testid="stExpanderDetails"] { margin-bottom: 0 !important; }

        /* 4. КНОПКИ ДЕЙСТВИЙ */
        div[data-testid="stHorizontalBlock"] { display: grid !important; grid-template-columns: repeat(auto-fit, minmax(10px, 1fr)) !important; gap: 8px !important; width: 100% !important; }
        div[data-testid="column"] { width: 100% !important; min-width: 0 !important; max-width: 100% !important; margin-bottom: 0 !important; }
        div[data-testid="stButton"] { width: 100% !important; }
        div[data-testid="stButton"] button { width: 100% !important; height: 50px !important; padding: 0 !important; border-radius: 12px !important; border: none !important; transition: transform 0.1s !important; }
        div[data-testid="stButton"] button:active { transform: translateY(4px) !important; box-shadow: 0 1px 0 transparent !important; }
        div[data-testid="stButton"] button p { font-family: 'Roboto', sans-serif !important; font-size: 15px !important; font-weight: 900 !important; margin: 0 !important; letter-spacing: 0.5px !important; text-transform: uppercase !important; color: #ffffff !important; }

        /* ═══════════════════════════════════════════
           БАЗОВЫЕ СТИЛИ (Дизайн переопределяется ниже)
           ═══════════════════════════════════════════ */

        .mobile-game-area {
          position: relative !important;
          width: 100% !important;
          max-width: 390px !important;
          height: 250px !important;
          margin: 50px auto 55px auto !important; /* ЕЩЕ СИЛЬНЕЕ УБРАЛ ПУСТОТУ НАД СТОЛОМ */
          border-radius: 125px !important;
          overflow: visible !important;
          background:
            radial-gradient(ellipse 50% 38% at 50% 42%, rgba(18,62,38,0.7) 0%, transparent 70%),
            radial-gradient(ellipse 88% 78% at 50% 50%, #0d3d26 0%, #082418 60%, #040f0c 100%) !important;
          box-shadow:
            0 0 0 8px #0a1710,
            0 0 0 13px #13241a,
            0 0 0 17px #080f0b,
            0 0 50px 8px rgba(0,0,0,0.95),
            inset 0 2px 20px rgba(255,255,255,0.03),
            inset 0 -3px 12px rgba(0,0,0,0.5) !important;
          transition: background 0.5s, box-shadow 0.5s, border-color 0.5s;
        }
        .mobile-game-area::before {
          content: '' !important;
          position: absolute !important;
          inset: 0 !important;
          border-radius: 125px !important;
          background:
            repeating-linear-gradient(45deg,  rgba(255,255,255,0.011) 0px, rgba(255,255,255,0.011) 1px, transparent 1px, transparent 9px),
            repeating-linear-gradient(-45deg, rgba(255,255,255,0.011) 0px, rgba(255,255,255,0.011) 1px, transparent 1px, transparent 9px) !important;
          pointer-events: none !important;
          z-index: 0 !important;
        }
        .mobile-game-area::after {
          content: '' !important;
          position: absolute !important;
          inset: 10px !important;
          border-radius: 115px !important;
          border: 1px solid rgba(255,255,255,0.06) !important;
          pointer-events: none !important;
          z-index: 0 !important;
        }

        .glass-shatter, .mastery-glow, .crest-left-mob, .crest-right-mob { display: none !important; }

        .mob-info {
          position: absolute !important;
          top: 50% !important;
          left: 50% !important;
          transform: translate(-50%, -52%) !important;
          z-index: 10 !important;
          text-align: center !important;
          display: flex !important;
          flex-direction: column !important;
          align-items: center !important;
          gap: 4px !important;
          pointer-events: none !important;
          width: 100% !important;
        }
        .mob-info-spot {
          font-size: 11px !important;
          font-weight: 600 !important;
          letter-spacing: 0.2em !important;
          text-transform: uppercase !important;
          color: rgba(160,210,180,0.45) !important;
          text-shadow: 0 0 10px rgba(0,220,100,0.25), 0 1px 4px rgba(0,0,0,0.95) !important;
        }
        .mastery-badge {
          display: inline-flex !important;
          align-items: center !important;
          gap: 4px !important;
          background: rgba(255,205,50,0.08) !important;
          border: 1px solid rgba(255,205,50,0.2) !important;
          border-radius: 20px !important;
          padding: 2px 9px 2px 7px !important;
          font-size: 9.5px !important;
          font-weight: 700 !important;
          letter-spacing: 0.05em !important;
          color: rgba(255,205,50,0.85) !important;
          text-shadow: 0 0 7px rgba(255,205,50,0.4) !important;
        }
        .mastery-bar-bg { width: 60px !important; height: 2px !important; background: rgba(255,255,255,0.07) !important; border-radius: 2px !important; overflow: hidden !important; }
        .mastery-bar-fill { height: 100% !important; background: linear-gradient(90deg, #17f07e, #00b85e) !important; border-radius: 2px !important; box-shadow: 0 0 5px rgba(23,240,126,0.65) !important; }
        .hands-left-mob { font-size: 9px !important; color: rgba(130,185,155,0.35) !important; letter-spacing: 0.06em !important; text-shadow: 0 1px 3px rgba(0,0,0,0.95) !important; }

        .seat {
          position: absolute !important;
          z-index: 20 !important;
          display: flex !important;
          flex-direction: column !important;
          align-items: center !important;
          gap: 3px !important;
        }
        .seat::before {
          content: '' !important;
          display: block !important;
          width: 49px !important;
          height: 49px !important;
          border-radius: 50% !important;
          background: radial-gradient(circle at 38% 30%, #203d2e 0%, #0e2018 60%, #080f0e 100%) !important;
          border: 1.5px solid rgba(0,240,110,0.2) !important;
          box-shadow:
            0 0 0 3px rgba(0,0,0,0.65),
            0 0 8px rgba(0,240,110,0.08),
            inset 0 1px 3px rgba(255,255,255,0.06) !important;
        }
        .seat::after {
          content: '' !important;
          position: absolute !important;
          top: 7px !important;
          left: 50% !important;
          transform: translateX(-50%) !important;
          width: 14px !important;
          height: 14px !important;
          border-radius: 50% !important;
          background: rgba(255,255,255,0.07) !important;
          box-shadow: 0 8px 0 rgba(255,255,255,0.05) !important;
          pointer-events: none !important;
        }

        .seat-active::before {
          border-color: rgba(0,240,110,0.8) !important;
          box-shadow: 0 0 0 3px rgba(0,0,0,0.65), 0 0 16px rgba(0,240,110,0.45), 0 0 30px rgba(0,240,110,0.2), inset 0 1px 3px rgba(255,255,255,0.09) !important;
          animation: pulse-seat 2.6s ease-in-out infinite !important;
        }
        @keyframes pulse-seat {
          0%,100% { box-shadow: 0 0 0 3px rgba(0,0,0,0.65), 0 0 12px rgba(0,240,110,0.38), inset 0 1px 3px rgba(255,255,255,0.09); }
          50%      { box-shadow: 0 0 0 3px rgba(0,0,0,0.65), 0 0 26px rgba(0,240,110,0.7), 0 0 44px rgba(0,240,110,0.25), inset 0 1px 3px rgba(255,255,255,0.09); }
        }

        .seat-folded::before { border-color: rgba(80,80,80,0.15) !important; opacity: 0.6 !important; box-shadow: none !important; animation: none !important; }
        .seat-folded::after { opacity: 0.5 !important; }
        .seat-folded .opp-cards-mob { opacity: 0.5 !important; }
        .seat-label { font-size: 8px !important; font-weight: 700 !important; letter-spacing: 0.14em !important; text-transform: uppercase !important; color: rgba(160,210,180,0.5) !important; text-shadow: 0 0 4px rgba(0,220,100,0.25), 0 1px 3px rgba(0,0,0,0.98) !important; }

        .opp-cards-mob { position: absolute !important; top: -18px !important; left: 50% !important; transform: translateX(-50%) !important; display: flex !important; align-items: flex-end !important; }
        .opp-card-mob {
          width: 14px !important; height: 20px !important; border-radius: 3px !important; position: relative !important;
          background: repeating-linear-gradient(45deg, rgba(15,70,185,0.95) 0px, rgba(15,70,185,0.95) 2px, rgba(8,44,130,0.95) 2px, rgba(8,44,130,0.95) 6px) !important;
          border: 1px solid rgba(80,140,255,0.3) !important; box-shadow: 0 2px 5px rgba(0,0,0,0.8), inset 0 0 0 1px rgba(255,255,255,0.06) !important;
        }
        .opp-card-mob::before { content: '' !important; position: absolute !important; inset: 2px !important; border-radius: 2px !important; border: 1px solid rgba(80,140,255,0.15) !important; }
        .opp-card-mob.right { margin-left: -5px !important; transform: rotate(10deg) !important; z-index: -1 !important; }

        .dealer-mob {
          position: absolute !important; z-index: 30 !important; width: 20px !important; height: 20px !important; border-radius: 50% !important; display: flex !important; align-items: center !important; justify-content: center !important;
          font-size: 8px !important; font-weight: 900 !important; color: #120700 !important;
          background: radial-gradient(circle at 38% 30%, #ffd84a, #c88408) !important;
          border: 1.5px solid rgba(255,255,255,0.35) !important;
          box-shadow: 0 0 0 2px rgba(0,0,0,0.7), 0 2px 10px rgba(200,132,8,0.7), inset 0 1px 3px rgba(255,255,255,0.55) !important;
        }

        .chip-container { position: absolute !important; z-index: 22 !important; display: flex !important; flex-direction: column !important; align-items: center !important; gap: 3px !important; }
        
        .chip-mob, .chip-3bet, .chip-4bet {
          width: 15px !important;
          height: 15px !important;
          border-radius: 50% !important;
          position: relative !important;
          background:
            repeating-conic-gradient(rgba(255,255,255,0.13) 0deg 18deg, transparent 18deg 36deg),
            radial-gradient(circle at 36% 30%, #1e3a8a, #0c1844) !important;
          border: 2px solid rgba(255,255,255,0.22) !important;
          box-shadow:
            0 0 0 1.5px rgba(0,0,0,0.7),
            0 2px 5px rgba(0,0,0,0.8),
            inset 0 1px 2px rgba(255,255,255,0.2) !important;
        }
        
        .chip-3bet { background: radial-gradient(circle at 36% 30%, #ff5722, #9e3211) !important; }
        
        .chip-4bet {
          background:
            repeating-conic-gradient(rgba(255,255,255,0.15) 0deg 18deg, transparent 18deg 36deg),
            radial-gradient(circle at 36% 30%, #68158e, #3F055B) !important;
        }

        .chip-mob::before, .chip-3bet::before, .chip-4bet::before {
          content: '' !important; position: absolute !important; inset: 4px !important; border-radius: 50% !important; border: 1px solid rgba(255,255,255,0.12) !important;
        }
        
        .chip-mob::after, .chip-3bet::after, .chip-4bet::after {
          content: '' !important; position: absolute !important; top: 2px !important; left: 2px !important; width: 6px !important; height: 4px !important; border-radius: 50% !important; background: rgba(255,255,255,0.22) !important; filter: blur(1px) !important;
        }
        
        .bet-txt { font-size: 10px !important; font-weight: 700 !important; color: rgba(255,235,190,0.9) !important; text-shadow: 0 0 5px rgba(255,195,40,0.5), 0 1px 3px rgba(0,0,0,0.98) !important; letter-spacing: 0.03em !important; white-space: nowrap !important; }

        .hero-mob { position: absolute !important; bottom: -55px !important; left: 50% !important; transform: translateX(-50%) !important; z-index: 30 !important; display: flex !important; align-items: flex-start !important; gap: 7px !important; }

        .floating-reward { position: absolute !important; top: -38px !important; left: 50% !important; transform: translateX(-50%) !important; font-size: 14px !important; font-weight: 800 !important; color: #17f07e !important; text-shadow: 0 0 12px rgba(23,240,126,0.8), 0 0 28px rgba(23,240,126,0.3) !important; white-space: nowrap !important; animation: float-reward 2.2s ease-out forwards !important; pointer-events: none !important; }
        @keyframes float-reward { 0%   { opacity: 1; transform: translateX(-50%) translateY(0); } 100% { opacity: 0; transform: translateX(-50%) translateY(-24px); } }

        .card-mob {
          width: 54px !important; height: 78px !important; border-radius: 8px !important; position: relative !important; background: #f8faff !important; border: 1px solid rgba(255,255,255,0.85) !important;
          box-shadow: 0 0 0 1px rgba(0,0,0,0.2), 0 -6px 16px rgba(0,0,0,0.7), 0 -12px 30px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,1) !important;
          display: flex !important; flex-direction: column !important; align-items: flex-start !important; overflow: hidden !important;
        }
        .card-mob::after { content: '' !important; position: absolute !important; top: 0 !important; left: 0 !important; width: 60% !important; height: 45% !important; background: linear-gradient(135deg, rgba(255,255,255,0.45) 0%, transparent 100%) !important; pointer-events: none !important; border-radius: 8px 0 0 0 !important; }
        .tl-mob { padding: 4px 0 0 5px !important; font-size: 15px !important; font-weight: 900 !important; line-height: 0.9 !important; letter-spacing: -0.04em !important; z-index: 2 !important; position: relative !important; }
        .c-mob { position: absolute !important; top: 55% !important; left: 50% !important; transform: translate(-50%,-50%) !important; font-size: 24px !important; opacity: 1 !important; line-height: 1 !important; z-index: 2 !important;}
        .suit-red   { color: #c00a0a !important; }
        .suit-black { color: #0a0a0a !important; }
        .suit-blue  { color: #0056b3 !important; }
        .suit-green { color: #198754 !important; }

        .rng-badge {
          position: absolute !important;
          bottom: 50px !important;
          right: -31px !important;
          width: 28px !important;
          height: 28px !important;
          background: #6f42c1 !important;
          border: 2px solid #fff !important;
          border-radius: 50% !important;
          color: white !important;
          font-weight: bold !important;
          font-size: 12px !important;
          display: flex !important;
          align-items: center !important;
          justify-content: center !important;
          box-shadow: 0 2px 5px rgba(0,0,0,0.5) !important;
          z-index: 40 !important;
        }

        .rage-bar-container { width: 100%; max-width: 700px; margin: 2 auto 4px auto; background: rgba(0,0,0,0.6); border: 2px solid #333; border-radius: 20px; padding: 3px; display: flex; align-items: center; position: relative; box-shadow: inset 0 2px 10px rgba(0,0,0,0.8); height: 24px; }
        .rage-bar-fill { height: 100%; border-radius: 16px; transition: width 0.3s ease-out; position: relative; overflow: hidden; box-shadow: inset 0 2px 5px rgba(255,255,255,0.3), inset 0 -2px 5px rgba(0,0,0,0.4); }
        .rage-bar-fill::before, .rage-bar-fill::after { content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background-image: radial-gradient(circle, rgba(255,255,255,0.8) 1px, transparent 2px), radial-gradient(circle, rgba(255,255,255,0.5) 2px, transparent 3px), radial-gradient(circle, rgba(255,255,255,0.4) 1px, transparent 2px); z-index: 1; pointer-events: none; }
        .rage-bar-fill::before { background-size: 20px 25px, 35px 40px, 15px 20px; animation: bubbleRise1 1.2s infinite linear; }
        .rage-bar-fill::after { background-size: 25px 30px, 45px 50px, 22px 28px; animation: bubbleRise2 1.7s infinite linear; opacity: 0.6; }
        @keyframes bubbleRise1 { 0% { background-position: 0px 25px, 0px 40px, 0px 20px; } 50% { background-position: 5px 12.5px, -5px 20px, 3px 10px; } 100% { background-position: 0px 0px, 0px 0px, 0px 0px; } }
        @keyframes bubbleRise2 { 0% { background-position: 0px 30px, 0px 50px, 0px 28px; } 50% { background-position: -6px 15px, 6px 25px, -4px 14px; } 100% { background-position: 0px 0px, 0px 0px, 0px 0px; } }
        .rage-labels { position: absolute; width: 100%; display: flex; justify-content: space-between; padding: 0 15px; font-weight: 900; font-size: 12px; color: #fff; text-shadow: 0 1px 3px #000, 0 0 5px #000; pointer-events: none; z-index: 2; top: 50%; transform: translateY(-50%); }
        .rage-pulse { animation: ragePulse 0.4s infinite alternate; }
        @keyframes ragePulse { 0% { filter: brightness(1); box-shadow: 0 0 5px #dc3545; } 100% { filter: brightness(1.3); box-shadow: 0 0 25px #dc3545, inset 0 0 10px #fff; } }
        .rage-flash { animation: whiteFlash 0.6s ease-out; }
        @keyframes whiteFlash { 0% { box-shadow: 0 0 50px #fff, inset 0 0 50px #fff; background: #fff; border-color: #fff; } 100% { box-shadow: 0 0 0 transparent; } }

        .combo-glow-5 { border-color: #0dcaf0 !important; box-shadow: 0 0 10px rgba(13, 202, 240, 0.4), 0 4px 15px rgba(0,0,0,0.8) !important; }
        .combo-glow-10 { border-color: #ffc107 !important; box-shadow: 0 0 15px rgba(255, 193, 7, 0.5), 0 4px 15px rgba(0,0,0,0.8) !important; }
        .combo-glow-25 { border-color: #fd7e14 !important; box-shadow: 0 0 20px rgba(253, 126, 20, 0.6), 0 4px 15px rgba(0,0,0,0.8) !important; animation: pulse-slow 2s infinite; }
        .combo-glow-50 { border-color: #dc3545 !important; box-shadow: 0 0 30px rgba(220, 53, 69, 0.7), 0 4px 15px rgba(0,0,0,0.8) !important; animation: pulse-menace 1.5s infinite; }
        .combo-glow-100 { border-color: #6f42c1 !important; box-shadow: 0 0 40px rgba(111, 66, 193, 0.8), 0 4px 15px rgba(0,0,0,0.8) !important; animation: pulse-neon 1s infinite; }
        .combo-glow-200 { border-color: #00e5ff !important; box-shadow: 0 0 50px rgba(0, 229, 255, 0.8), 0 4px 15px rgba(0,0,0,0.8) !important; animation: pulse-plasma 1s infinite alternate; }
        .combo-glow-500 { border-color: #ff00ff !important; box-shadow: 0 0 60px rgba(255, 0, 255, 0.9), 0 4px 15px rgba(0,0,0,0.8) !important; animation: pulse-matrix 0.8s infinite alternate; }
        .combo-glow-1000 { border-color: #00ff00 !important; box-shadow: 0 0 80px rgba(0, 255, 0, 1.0), 0 4px 15px rgba(0,0,0,0.8) !important; animation: pulse-god 0.5s infinite alternate; }
        
        .rng-hint { text-align: center; color: #6c757d; font-size: 11px; font-family: 'Roboto', sans-serif; font-weight: 500; margin-bottom: 8px; letter-spacing: 0.5px; }
        </style>
    """, unsafe_allow_html=True)

    ranges_db = utils.load_ranges()
    if not ranges_db: st.error("Ranges database is empty."); return

    scenario_map = {}
    for src, sc_dict in ranges_db.items():
        for sc, sp_dict in sc_dict.items():
            if sc not in scenario_map: scenario_map[sc] = []
            for sp in sp_dict.keys():
                scenario_map[sc].append((sp, f"{src}|{sc}|{sp}"))
                
    all_scenarios = sorted(list(scenario_map.keys()))

    with st.expander("⚙️ Spot Filters", expanded=False):
        c_v1, c_v2 = st.columns(2)
        with c_v1:
            if st.button("📱 Mobile View", key="mv_btn"):
                st.session_state.actual_view_type = "📱 Mobile"; st.rerun()
        with c_v2:
            if st.button("💻 Desktop View", key="dv_btn"):
                st.session_state.actual_view_type = "💻 Desktop"; st.rerun()
        st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)

        saved = utils.load_user_settings()
        sel_sc = st.multiselect("Scenario", all_scenarios, default=[s for s in saved.get("scenarios", []) if s in all_scenarios])
        
        sel_spots_keys = []
        if sel_sc:
            st.markdown("**Spots for training:**")
            saved_spots = saved.get("spots", [])
            for sc in sel_sc:
                st.markdown(f"<div style='color:#ffc107; font-size:14px; font-weight:bold; margin-top:8px;'>{sc}</div>", unsafe_allow_html=True)
                for sp_name, sp_key in scenario_map[sc]:
                    is_checked = (sp_key in saved_spots) if "spots" in saved else True
                    if st.checkbox(sp_name, value=is_checked, key=f"m_chk_{sp_key}"):
                        sel_spots_keys.append(sp_key)
        
        if st.button("🚀 Apply Settings", use_container_width=True):
            saved["scenarios"] = sel_sc
            saved["spots"] = sel_spots_keys
            utils.save_user_settings(saved)
            if hasattr(utils, "force_sync"):
                utils.force_sync()
            st.session_state.hand = None; st.rerun()

    pool = sel_spots_keys
    if not pool:
        st.warning("⚠️ No spots selected.")
        st.stop()

    stats_data_init = utils.load_user_stats()
    if 'combo' not in st.session_state: st.session_state.combo = stats_data_init.get("combo", 0)
    if 'shields' not in st.session_state: st.session_state.shields = stats_data_init.get("shields", 0)

    if 'shield_break_anim' not in st.session_state: st.session_state.shield_break_anim = False
    if 'session_hands' not in st.session_state: st.session_state.session_hands = 0
    if 'session_correct' not in st.session_state: st.session_state.session_correct = 0
    
    if 'toast_msgs' not in st.session_state: st.session_state.toast_msgs = []
    if st.session_state.toast_msgs:
        for msg in st.session_state.toast_msgs:
            st.toast(msg, icon="🔥" if "Combo" in msg else "🎯")
        st.session_state.toast_msgs = []

    if 'hand' not in st.session_state: st.session_state.hand = None
    if 'rng' not in st.session_state: st.session_state.rng = 0
    if 'suits' not in st.session_state: st.session_state.suits = None
    if 'current_spot_key' not in st.session_state: st.session_state.current_spot_key = None 
    if 'last_error' not in st.session_state: st.session_state.last_error = False

    if st.session_state.hand is None or st.session_state.current_spot_key is None or st.session_state.current_spot_key not in pool:
        chosen = random.choice(pool)
        st.session_state.current_spot_key = chosen
        src, sc, sp = chosen.split('|')
        data = ranges_db[src][sc][sp]
        r_data = data.get("ranges", data)
        t_range = r_data.get("training", r_data.get("source", r_data.get("full", "")))
        poss = utils.parse_range_to_list(t_range)
        srs = utils.load_srs_data()
        w = [srs.get(f"{src}_{sc}_{sp}_{h}".replace(" ","_"), 100) for h in poss]
        if sum(w) == 0: w = [100]*len(poss)
            
        st.session_state.hand = random.choices(poss, weights=w, k=1)[0]
        st.session_state.rng = random.randint(0, 99)
        ps = ['♠','♥','♦','♣']; s1 = random.choice(ps)
        st.session_state.suits = [s1, s1 if 's' in st.session_state.hand else random.choice([x for x in ps if x!=s1])]

    src, sc, sp = st.session_state.current_spot_key.split('|')
    data = ranges_db[src][sc][sp]
    r_data = data.get("ranges", data)
    
    setup = data.get("setup", {})
    hero_pos = setup.get("hero_pos", "EP")
    villain_pos = setup.get("villain_pos")
    btn_pos = setup.get("btn_pos", "BTN")
    cards_in_play = setup.get("active_players", [])
    bets_on_table = setup.get("table_bets", {})
    display_hero_bet = setup.get("hero_bet")
    is_3bet_pot = setup.get("is_3bet_pot", False)

    is_defense = bool(villain_pos is not None or "call" in r_data or "Call" in r_data)
    rng = st.session_state.rng
    correct_act = "FOLD"
    r_call = r_data.get("call", r_data.get("Call", ""))
    r_raise = r_data.get("4bet", r_data.get("3bet", r_data.get("Raise", "")))
    r_full = r_data.get("full", r_data.get("Full", ""))

    if is_defense:
        w_c = utils.get_weight(st.session_state.hand, r_call)
        w_raise_val = utils.get_weight(st.session_state.hand, r_raise)
        if rng < w_raise_val: correct_act = "RAISE"
        elif rng < (w_raise_val + w_c): correct_act = "CALL"
    else:
        w = utils.get_weight(st.session_state.hand, r_full)
        if rng < w: correct_act = "RAISE"

    h_val = st.session_state.hand; s1, s2 = st.session_state.suits
    c1 = "suit-red" if s1 == '♥' else "suit-blue" if s1 == '♦' else "suit-green" if s1 == '♣' else "suit-black"
    c2 = "suit-red" if s2 == '♥' else "suit-blue" if s2 == '♦' else "suit-green" if s2 == '♣' else "suit-black"

    stats_data = utils.load_user_stats()
    rank_name, next_xp = utils.get_rank_info(stats_data.get("xp", 0))
    c = st.session_state.combo
    
    sh = st.session_state.session_hands
    scorr = st.session_state.session_correct
    wr = int((scorr / sh * 100)) if sh > 0 else 0
    wr_color = '#28a745' if wr >= 90 else '#ffc107' if wr >= 80 else '#dc3545'

    try:
        mastery = utils.get_spot_mastery_info(stats_data.get("spot_mastery", {}).get(st.session_state.current_spot_key, {}))
    except Exception as e:
        mastery = {"rank": 0, "name": "Sandbox", "icon": "⚪", "color": "#6c757d", "is_rusty": False, "prog_pct": 0, "total": 0, "next": 100, "svg": ""}
        
    m_color = mastery['color']
    m_svg = mastery.get("svg", "")
    m_rust = mastery.get("is_rusty", False)
    m_icon = mastery.get("icon", "")
    m_name = mastery.get("name", "")
    m_pct = mastery.get("prog_pct", 0)
    m_total = mastery.get("total", 0)
    m_next = mastery.get("next", 100)
    m_rank = mastery.get("rank", 0)
    
    if m_rank >= 5:
        hands_left_text = "MAX RANK"
    else:
        h_left = max(0, m_next - m_total)
        hands_left_text = f"Remaining: {h_left} hands"

    # ─────────────────────────────────────────────────────────────────
    # DYNAMIC SPOT MASTERY CSS INJECTION
    # ─────────────────────────────────────────────────────────────────
    visual_rank = m_rank if m_rank > 0 else 1
    
    if visual_rank == 1:
        m_icon = "🌱"
        m_name = "Rookie I"
        table_css = """<style>
        .mobile-game-area { background: radial-gradient(ellipse 50% 38% at 50% 44%, rgba(30,55,38,0.5) 0%, transparent 68%), radial-gradient(ellipse 90% 80% at 50% 50%, #1a2e20 0%, #111e16 55%, #090e0b 100%) !important; box-shadow: 0 0 0 8px #0e1410, 0 0 0 13px #182219, 0 0 0 17px #0b100d, 0 0 40px 6px rgba(0,0,0,0.9), inset 0 2px 16px rgba(255,255,255,0.02) !important; }
        .mobile-game-area::before { background: repeating-linear-gradient(45deg,  rgba(255,255,255,0.008) 0px, rgba(255,255,255,0.008) 1px, transparent 1px, transparent 10px), repeating-linear-gradient(-45deg, rgba(255,255,255,0.008) 0px, rgba(255,255,255,0.008) 1px, transparent 1px, transparent 10px) !important; }
        .mobile-game-area::after { border: 1px solid rgba(255,255,255,0.04) !important; }
        .seat::before { background: radial-gradient(circle at 38% 30%, #1a2d21 0%, #0e1a12 60%, #080d0a 100%) !important; border: 1.5px solid rgba(120,160,130,0.18) !important; box-shadow: 0 0 0 3px rgba(0,0,0,0.6), inset 0 1px 2px rgba(255,255,255,0.04) !important; }
        .seat::after { background: rgba(255,255,255,0.06) !important; box-shadow: 0 8px 0 rgba(255,255,255,0.04) !important; }
        .seat-active::before { border-color: rgba(120,180,140,0.55) !important; box-shadow: 0 0 0 3px rgba(0,0,0,0.6), 0 0 10px rgba(120,180,140,0.28) !important; animation: r1-pulse 3s ease-in-out infinite !important; }
        @keyframes r1-pulse { 0%,100% { box-shadow: 0 0 0 3px rgba(0,0,0,0.6), 0 0 7px rgba(120,180,140,0.22); } 50% { box-shadow: 0 0 0 3px rgba(0,0,0,0.6), 0 0 16px rgba(120,180,140,0.42); } }
        .seat-label { color: rgba(140,190,155,0.45) !important; text-shadow: 0 1px 3px rgba(0,0,0,0.95) !important; }
        .mob-info-spot { color: rgba(140,185,155,0.4) !important; text-shadow: 0 1px 4px rgba(0,0,0,0.95) !important; }
        .mastery-badge { background: rgba(120,180,140,0.07) !important; border: 1px solid rgba(120,180,140,0.18) !important; color: rgba(130,190,150,0.8) !important; }
        .mastery-bar-fill { background: linear-gradient(90deg, #6ab880, #4a9060) !important; }
        .hands-left-mob { color: rgba(110,165,130,0.35) !important; }
        .floating-reward { color: #6ab880 !important; text-shadow: 0 0 10px rgba(106,184,128,0.6) !important; }
        .card-mob { background: #f8faff !important; border: 1px solid rgba(255,255,255,0.85) !important; box-shadow: 0 0 0 1px rgba(0,0,0,0.2), 0 -6px 16px rgba(0,0,0,0.7), 0 -12px 30px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,1) !important; }
        .card-mob::after { background: linear-gradient(135deg, rgba(255,255,255,0.45) 0%, transparent 100%) !important; }
        .suit-red { color: #c00a0a !important; }
        .suit-black { color: #0a0a0a !important; }
        .rng-badge { color: rgba(130,190,150,0.8) !important; background: rgba(120,180,140,0.08) !important; border: 1.5px solid rgba(120,180,140,0.25) !important; }
        </style>"""
    elif visual_rank == 2:
        m_icon = "💎"
        m_name = "Advanced II"
        table_css = """<style>
        .mobile-game-area { background: radial-gradient(ellipse 55% 40% at 50% 40%, rgba(10,50,80,0.6) 0%, transparent 70%), radial-gradient(ellipse 88% 78% at 50% 50%, #0b3040 0%, #071e2e 58%, #030e18 100%) !important; box-shadow: 0 0 0 8px #081420, 0 0 0 13px #0f2234, 0 0 0 17px #060e17, 0 0 50px 8px rgba(0,0,0,0.92), inset 0 2px 18px rgba(255,255,255,0.025) !important; }
        .mobile-game-area::before { background: repeating-linear-gradient(45deg,  rgba(100,180,255,0.012) 0px, rgba(100,180,255,0.012) 1px, transparent 1px, transparent 10px), repeating-linear-gradient(-45deg, rgba(100,180,255,0.012) 0px, rgba(100,180,255,0.012) 1px, transparent 1px, transparent 10px) !important; }
        .mobile-game-area::after { border: 1px solid rgba(100,180,255,0.07) !important; }
        .seat::before { background: radial-gradient(circle at 38% 30%, #162840 0%, #0c1a28 60%, #060e18 100%) !important; border: 1.5px solid rgba(60,130,200,0.22) !important; box-shadow: 0 0 0 3px rgba(0,0,0,0.65), 0 0 7px rgba(60,130,200,0.1), inset 0 1px 3px rgba(255,255,255,0.05) !important; }
        .seat::after { background: rgba(255,255,255,0.065) !important; box-shadow: 0 8px 0 rgba(255,255,255,0.045) !important; }
        .seat-active::before { border-color: rgba(60,160,255,0.78) !important; box-shadow: 0 0 0 3px rgba(0,0,0,0.65), 0 0 16px rgba(60,160,255,0.42), 0 0 28px rgba(60,160,255,0.16) !important; animation: r2-pulse 2.8s ease-in-out infinite !important; }
        @keyframes r2-pulse { 0%,100% { box-shadow: 0 0 0 3px rgba(0,0,0,0.65), 0 0 12px rgba(60,160,255,0.34); } 50% { box-shadow: 0 0 0 3px rgba(0,0,0,0.65), 0 0 24px rgba(60,160,255,0.62), 0 0 40px rgba(60,160,255,0.22); } }
        .seat-label { color: rgba(80,160,230,0.55) !important; text-shadow: 0 0 4px rgba(60,140,220,0.2), 0 1px 3px rgba(0,0,0,0.98) !important; }
        .mob-info-spot { color: rgba(100,170,220,0.45) !important; text-shadow: 0 1px 4px rgba(0,0,0,0.95) !important; }
        .mastery-badge { background: rgba(60,130,200,0.09) !important; border: 1px solid rgba(60,130,200,0.22) !important; color: rgba(80,170,255,0.85) !important; }
        .mastery-bar-fill { background: linear-gradient(90deg, #3ab0ff, #1480d8) !important; }
        .hands-left-mob { color: rgba(70,140,210,0.35) !important; }
        .floating-reward { color: #3ab0ff !important; text-shadow: 0 0 10px rgba(58,176,255,0.65) !important; }
        .card-mob { background: #f8faff !important; border: 1px solid rgba(255,255,255,0.85) !important; box-shadow: 0 0 0 1px rgba(0,0,0,0.2), 0 -6px 16px rgba(0,0,0,0.7), 0 -12px 30px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,1) !important; }
        .card-mob::after { background: linear-gradient(135deg, rgba(255,255,255,0.45) 0%, transparent 100%) !important; }
        .suit-red { color: #c00a0a !important; }
        .suit-black { color: #0a0a0a !important; }
        .rng-badge { color: rgba(80,170,255,0.85) !important; background: rgba(60,130,200,0.09) !important; border: 1.5px solid rgba(60,130,200,0.28) !important; }
        </style>"""
    elif visual_rank == 3:
        m_icon = "🔥"
        m_name = "Master III"
        table_css = """<style>
        .mobile-game-area { background: radial-gradient(ellipse 52% 40% at 50% 42%, rgba(90,18,28,0.65) 0%, transparent 70%), radial-gradient(ellipse 88% 78% at 50% 50%, #3a0d14 0%, #240810 58%, #0f0408 100%) !important; box-shadow: 0 0 0 8px #1a080a, 0 0 0 13px #2e1014, 0 0 0 17px #12060a, 0 0 50px 8px rgba(0,0,0,0.95), inset 0 2px 18px rgba(255,255,255,0.025) !important; }
        .mobile-game-area::before { background: repeating-linear-gradient(45deg,  rgba(200,100,50,0.014) 0px, rgba(200,100,50,0.014) 1px, transparent 1px, transparent 9px), repeating-linear-gradient(-45deg, rgba(200,100,50,0.014) 0px, rgba(200,100,50,0.014) 1px, transparent 1px, transparent 9px) !important; }
        .mobile-game-area::after { border: 1px solid rgba(200,120,60,0.08) !important; }
        .seat::before { background: radial-gradient(circle at 38% 30%, #3a1c10 0%, #221008 60%, #0f0804 100%) !important; border: 1.5px solid rgba(180,110,40,0.28) !important; box-shadow: 0 0 0 3px rgba(0,0,0,0.65), 0 0 8px rgba(180,110,40,0.1), inset 0 1px 3px rgba(255,255,255,0.06) !important; }
        .seat::after { background: rgba(255,200,100,0.06) !important; box-shadow: 0 8px 0 rgba(255,200,100,0.04) !important; }
        .seat-active::before { border-color: rgba(210,150,50,0.88) !important; box-shadow: 0 0 0 3px rgba(0,0,0,0.65), 0 0 16px rgba(210,150,50,0.48), 0 0 28px rgba(210,150,50,0.18) !important; animation: r3-pulse 2.6s ease-in-out infinite !important; }
        @keyframes r3-pulse { 0%,100% { box-shadow: 0 0 0 3px rgba(0,0,0,0.65), 0 0 12px rgba(210,150,50,0.4); } 50% { box-shadow: 0 0 0 3px rgba(0,0,0,0.65), 0 0 24px rgba(220,165,60,0.68), 0 0 38px rgba(210,150,50,0.22); } }
        .seat-label { color: rgba(200,140,50,0.55) !important; text-shadow: 0 0 4px rgba(180,110,30,0.2), 0 1px 3px rgba(0,0,0,0.98) !important; }
        .mob-info-spot { color: rgba(200,140,60,0.45) !important; text-shadow: 0 1px 4px rgba(0,0,0,0.95) !important; }
        .mastery-badge { background: rgba(180,110,40,0.09) !important; border: 1px solid rgba(180,110,40,0.24) !important; color: rgba(220,165,65,0.88) !important; }
        .mastery-bar-fill { background: linear-gradient(90deg, #d49030, #a86018) !important; }
        .hands-left-mob { color: rgba(180,110,40,0.35) !important; }
        .floating-reward { color: #d49030 !important; text-shadow: 0 0 10px rgba(212,144,48,0.65) !important; }
        .card-mob { background: linear-gradient(145deg, #f5f0e8 0%, #ede5d4 100%) !important; border: 1px solid rgba(210,175,110,0.7) !important; box-shadow: 0 0 0 1px rgba(0,0,0,0.15), 0 -6px 16px rgba(0,0,0,0.65), 0 -12px 28px rgba(0,0,0,0.38), 0 0 14px rgba(200,150,60,0.12), inset 0 1px 0 rgba(255,255,255,0.9) !important; }
        .card-mob::after { background: linear-gradient(135deg, rgba(255,240,200,0.5) 0%, rgba(220,190,130,0.1) 50%, transparent 100%) !important; }
        .suit-red { color: #a80808 !important; }
        .suit-black { color: #1a0a04 !important; }
        .rng-badge { color: rgba(220,165,65,0.88) !important; background: rgba(180,110,40,0.09) !important; border: 1.5px solid rgba(180,110,40,0.3) !important; }
        </style>"""
    elif visual_rank == 4:
        m_icon = "⚡"
        m_name = "Grandmaster IV"
        table_css = """<style>
        .mobile-game-area { background: radial-gradient(ellipse 52% 40% at 50% 42%, rgba(55,20,90,0.6) 0%, transparent 70%), radial-gradient(ellipse 88% 78% at 50% 50%, #1e0d30 0%, #130820 58%, #07030f 100%) !important; box-shadow: 0 0 0 8px #120818, 0 0 0 13px #1e1028, 0 0 0 17px #0d0614, 0 0 50px 8px rgba(0,0,0,0.96), inset 0 2px 18px rgba(255,255,255,0.025) !important; }
        .mobile-game-area::before { background: repeating-linear-gradient(45deg,  rgba(160,100,255,0.016) 0px, rgba(160,100,255,0.016) 1px, transparent 1px, transparent 9px), repeating-linear-gradient(-45deg, rgba(160,100,255,0.016) 0px, rgba(160,100,255,0.016) 1px, transparent 1px, transparent 9px) !important; }
        .mobile-game-area::after { border: 1px solid rgba(160,100,255,0.09) !important; }
        .seat::before { background: radial-gradient(circle at 38% 30%, #2a1840 0%, #180e28 60%, #0a0812 100%) !important; border: 1.5px solid rgba(160,130,220,0.28) !important; box-shadow: 0 0 0 3px rgba(0,0,0,0.68), 0 0 8px rgba(160,130,220,0.1), inset 0 1px 3px rgba(255,255,255,0.06) !important; }
        .seat::after { background: rgba(180,150,255,0.06) !important; box-shadow: 0 8px 0 rgba(180,150,255,0.04) !important; }
        .seat-active::before { border-color: rgba(190,160,255,0.88) !important; box-shadow: 0 0 0 3px rgba(0,0,0,0.68), 0 0 18px rgba(170,130,255,0.52), 0 0 32px rgba(170,130,255,0.2) !important; animation: r4-pulse 2.4s ease-in-out infinite !important; }
        @keyframes r4-pulse { 0%,100% { box-shadow: 0 0 0 3px rgba(0,0,0,0.68), 0 0 14px rgba(170,130,255,0.42); } 50% { box-shadow: 0 0 0 3px rgba(0,0,0,0.68), 0 0 26px rgba(190,150,255,0.7), 0 0 44px rgba(170,130,255,0.26); } }
        .seat-label { color: rgba(180,155,240,0.55) !important; text-shadow: 0 0 4px rgba(150,120,220,0.22), 0 1px 3px rgba(0,0,0,0.98) !important; }
        .mob-info-spot { color: rgba(170,145,230,0.45) !important; text-shadow: 0 1px 4px rgba(0,0,0,0.95) !important; }
        .mastery-badge { background: rgba(140,110,220,0.09) !important; border: 1px solid rgba(140,110,220,0.22) !important; color: rgba(190,165,255,0.88) !important; }
        .mastery-bar-fill { background: linear-gradient(90deg, #a070ff, #7040d8) !important; }
        .hands-left-mob { color: rgba(140,110,220,0.35) !important; }
        .floating-reward { color: #a878ff !important; text-shadow: 0 0 12px rgba(168,120,255,0.7) !important; }
        .card-mob { background: linear-gradient(150deg, #2a2a32 0%, #1e1e26 100%) !important; border: 1px solid rgba(200,190,230,0.3) !important; box-shadow: 0 0 0 1px rgba(0,0,0,0.5), 0 -6px 16px rgba(0,0,0,0.75), 0 -12px 28px rgba(0,0,0,0.5), 0 0 16px rgba(160,130,255,0.14), inset 0 1px 0 rgba(255,255,255,0.12) !important; }
        .card-mob::after { background: linear-gradient(135deg, rgba(220,210,255,0.18) 0%, rgba(180,160,240,0.05) 40%, transparent 100%) !important; }
        .suit-red { color: #ff4466 !important; }
        .suit-black { color: #d0c8f0 !important; }
        .rng-badge { color: rgba(190,165,255,0.88) !important; background: rgba(140,110,220,0.09) !important; border: 1.5px solid rgba(140,110,220,0.3) !important; }
        </style>"""
    else:
        m_icon = "👑"
        m_name = "Legend V"
        table_css = """<style>
        .mobile-game-area { background: radial-gradient(ellipse 50% 36% at 50% 42%, rgba(60,50,10,0.5) 0%, transparent 68%), radial-gradient(ellipse 88% 78% at 50% 50%, #141410 0%, #0c0c09 55%, #050504 100%) !important; box-shadow: 0 0 0 8px #0f0f0c, 0 0 0 13px #1c1c16, 0 0 0 17px #0a0a08, 0 0 0 28px 5px rgba(200,170,50,0.05), 0 0 60px 10px rgba(0,0,0,0.98), inset 0 2px 20px rgba(255,255,255,0.02) !important; }
        .mobile-game-area::before { background: repeating-linear-gradient(45deg,  rgba(220,185,80,0.022) 0px, rgba(220,185,80,0.022) 1px, transparent 1px, transparent 8px), repeating-linear-gradient(-45deg, rgba(220,185,80,0.022) 0px, rgba(220,185,80,0.022) 1px, transparent 1px, transparent 8px) !important; }
        .mobile-game-area::after { border: 1px solid rgba(200,168,60,0.12) !important; }
        .seat::before { background: radial-gradient(circle at 38% 30%, #1c1a10 0%, #111008 60%, #080806 100%) !important; border: 1.5px solid rgba(190,158,50,0.3) !important; box-shadow: 0 0 0 3px rgba(0,0,0,0.7), 0 0 8px rgba(190,158,50,0.1), inset 0 1px 3px rgba(255,255,255,0.06) !important; }
        .seat::after { background: rgba(220,188,70,0.07) !important; box-shadow: 0 8px 0 rgba(220,188,70,0.05) !important; }
        .seat-active::before { border-color: rgba(220,188,70,0.95) !important; box-shadow: 0 0 0 3px rgba(0,0,0,0.7), 0 0 18px rgba(220,188,70,0.58), 0 0 36px rgba(200,165,40,0.22) !important; animation: r5-pulse 2.2s ease-in-out infinite !important; }
        @keyframes r5-pulse { 0%,100% { box-shadow: 0 0 0 3px rgba(0,0,0,0.7), 0 0 14px rgba(220,188,70,0.46); } 50% { box-shadow: 0 0 0 3px rgba(0,0,0,0.7), 0 0 28px rgba(240,205,80,0.78), 0 0 50px rgba(220,185,50,0.28); } }
        .seat-label { color: rgba(215,182,60,0.55) !important; text-shadow: 0 0 4px rgba(190,158,40,0.25), 0 1px 3px rgba(0,0,0,0.98) !important; }
        .mob-info-spot { color: rgba(210,178,55,0.45) !important; text-shadow: 0 0 8px rgba(190,155,40,0.22), 0 1px 4px rgba(0,0,0,0.95) !important; }
        .mastery-badge { background: rgba(190,158,50,0.1) !important; border: 1px solid rgba(190,158,50,0.25) !important; color: rgba(220,188,70,0.9) !important; text-shadow: 0 0 6px rgba(190,155,40,0.4) !important; }
        .mastery-bar-fill { background: linear-gradient(90deg, #d4a820, #a07810) !important; box-shadow: 0 0 5px rgba(212,168,32,0.6) !important; }
        .hands-left-mob { color: rgba(180,148,40,0.35) !important; }
        .floating-reward { color: #d4a820 !important; text-shadow: 0 0 14px rgba(212,168,32,0.8), 0 0 28px rgba(190,140,20,0.35) !important; }
        .card-mob { background: linear-gradient(150deg, #1a1a18 0%, #111110 100%) !important; border: 1px solid rgba(210,180,70,0.38) !important; box-shadow: 0 0 0 1px rgba(0,0,0,0.6), 0 -6px 16px rgba(0,0,0,0.8), 0 -12px 30px rgba(0,0,0,0.55), 0 0 18px rgba(200,168,50,0.18), inset 0 1px 0 rgba(255,255,255,0.07) !important; }
        .card-mob::after { background: linear-gradient(135deg, rgba(240,210,90,0.16) 0%, rgba(200,168,50,0.04) 40%, transparent 100%) !important; }
        .suit-red { color: #ff3355 !important; }
        .suit-black { color: #e8e0c8 !important; }
        .rng-badge { color: rgba(220,188,70,0.9) !important; background: rgba(190,158,50,0.1) !important; border: 1.5px solid rgba(190,158,50,0.3) !important; box-shadow: 0 0 7px rgba(190,155,40,0.22) !important; }
        </style>"""
        
    st.markdown(table_css, unsafe_allow_html=True)

    combo_cls = ""
    if c >= 1000: combo_cls = "combo-glow-1000"
    elif c >= 500: combo_cls = "combo-glow-500"
    elif c >= 200: combo_cls = "combo-glow-200"
    elif c >= 100: combo_cls = "combo-glow-100"
    elif c >= 50: combo_cls = "combo-glow-50"
    elif c >= 25: combo_cls = "combo-glow-25"
    elif c >= 10: combo_cls = "combo-glow-10"
    elif c >= 5: combo_cls = "combo-glow-5"

    tiers = [(0, 1.0), (10, 1.5), (25, 2.0), (50, 3.0), (100, 4.0), (250, 5.0), (500, 10.0)]
    curr_mult = 1.0; next_mult = 1.5; prev_req = 0; next_req = 10
    for i in range(len(tiers)):
        if c >= tiers[i][0]:
            curr_mult = tiers[i][1]
            prev_req = tiers[i][0]
            if i + 1 < len(tiers):
                next_req = tiers[i+1][0]
                next_mult = tiers[i+1][1]
            else:
                next_req = c 
                next_mult = "MAX"
                
    if next_mult == "MAX":
        rage_pct = 100
        lbl_left = f"x{curr_mult}"; lbl_right = "MAX"
    else:
        rage_pct = int((c - prev_req) / (next_req - prev_req) * 100)
        lbl_left = f"x{curr_mult}"; lbl_right = f"x{next_mult}"

    is_pulsing = "rage-pulse" if rage_pct >= 95 and next_mult != "MAX" else ""
    is_flashing = "rage-flash" if st.session_state.pop("just_leveled_up", False) else ""
    
    if curr_mult == 1.0: grad = "linear-gradient(90deg, #17a2b8, #0dcaf0)"
    elif curr_mult == 1.5: grad = "linear-gradient(90deg, #0dcaf0, #28a745)"
    elif curr_mult == 2.0: grad = "linear-gradient(90deg, #28a745, #ffc107)"
    elif curr_mult == 3.0: grad = "linear-gradient(90deg, #ffc107, #fd7e14)"
    elif curr_mult == 4.0: grad = "linear-gradient(90deg, #fd7e14, #dc3545)"
    elif curr_mult == 5.0: grad = "linear-gradient(90deg, #dc3545, #6f42c1)"
    else: grad = "linear-gradient(90deg, #6f42c1, #ff00ff)"

    progress_pct = int((stats_data.get("xp", 0) / next_xp) * 100) if next_xp != "MAX" else 100

    shield_display = f'<span style="font-size:12px; margin-left:6px; filter:drop-shadow(0 0 5px #0dcaf0); display:{"inline-flex" if st.session_state.shields > 0 else "none"};">🛡️x{st.session_state.shields}</span>'
    combo_badge = f'<div style="flex:1; display:flex; justify-content:center; align-items:center;"><div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 2px 10px; border-radius: 15px; display: inline-flex; align-items: center; justify-content: center;"><span style="font-size:15px; font-weight:900; color:#fff;">🔥 {c}</span>{shield_display}</div></div>'

    # Прибил этот блок выше за счет margin-top: -15px
    header_html = f'<div style="margin-top:-15px; background:#111; border-radius:8px; margin-bottom:1px; border:1px solid #333; overflow:hidden; font-family:sans-serif;"><div style="height: 2px; width: 100%; background: #222;"><div style="height: 100%; width: {wr if sh > 0 else 100}%; background: {wr_color if sh > 0 else "#444"}; transition: width 0.3s;"></div></div><div style="padding:4px 10px 0 10px; display:flex; justify-content:space-between; align-items:center;"><div style="flex:1;"><div style="font-size:12px; font-weight:bold; color:#ffc107;">{rank_name}</div><div style="background:#333; height:4px; border-radius:2px; margin-top:2px; width:100%;"><div style="background:#28a745; height:100%; width:{progress_pct}%; border-radius:2px;"></div></div></div><div style="font-size:9px; color:#aaa; margin-left:10px; font-weight:bold;">${stats_data.get("xp", 0)} / ${next_xp}</div></div><div style="display:flex; justify-content:space-between; align-items:center; padding:2px 10px 4px 10px;"><div style="flex:1;"><div style="font-size:10px; font-weight:bold; color:#aaa;">Winrate</div><div style="font-size:12px; font-weight:bold; color:{wr_color};">{wr}%</div></div>{combo_badge}<div style="flex:1; text-align:right;"><div style="font-size:10px; font-weight:bold; color:#aaa;">Hands</div><div style="font-size:12px; font-weight:bold; color:#fff;">{sh}</div></div></div></div>'
    
    rage_bar_html = f'''
    <div class="rage-bar-container {is_flashing}">
        <div class="rage-bar-fill {is_pulsing}" style="width: {rage_pct}%; background: {grad};"></div>
        <div class="rage-labels">
            <span>{lbl_left}</span>
            <span>{lbl_right}</span>
        </div>
    </div>
    '''

    anim_html = ""
    anim_reward = st.session_state.pop("anim_reward", None)
    if anim_reward is not None:
        if anim_reward > 0: a_color = "#00ff00"; a_text = f"+${anim_reward}"
        elif anim_reward < 0: a_color = "#ff0000"; a_text = f"-${abs(anim_reward)}"
        else: a_color = "#888"; a_text = "$0"
        anim_html = f'<div class="floating-reward" style="color: {a_color}">{a_text}</div>'
        
    shatter_html = '<div class="glass-shatter"></div>' if st.session_state.pop("shield_break_anim", False) else ""

    st.markdown(header_html, unsafe_allow_html=True)
    st.markdown(rage_bar_html, unsafe_allow_html=True)

    order = ["EP", "MP", "CO", "BTN", "SB", "BB"]
    try: hero_idx = order.index(hero_pos)
    except ValueError: hero_idx = 0
    rot = order[hero_idx:] + order[:hero_idx]

    def get_seat_style(idx):
        return {
            1: "top: 75%; left: -2%; transform: translateY(-50%);", 
            2: "top: 8%; left: 2%;", 
            3: "top: -17%; left: 50%; transform: translateX(-50%);", 
            4: "top: 8%; right: 2%;", 
            5: "top: 75%; right: -2%; transform: translateY(-50%);"
        }.get(idx, "")

    def get_chip_style(idx):
        return {
            0: "bottom: 38px; left: 50%; transform: translateX(-50%);", 
            1: "top: 63%; left: 16%; transform: translateY(-50%);", 
            2: "top: 23%; left: 20%;",
            3: "top: 13%; left: 50%; transform: translateX(-50%);", 
            4: "top: 23%; right: 20%;", 
            5: "top: 63%; right: 16%; transform: translateY(-50%);"
        }.get(idx, "")

    def get_btn_style(idx):
        return {
            0: "bottom: 15px; left: 50%; margin-left: -85px; z-index: 35;", 
            1: "top: 77%; left: 13%; transform: translateY(-50%);", 
            2: "top: 25%; left: 13%;",
            3: "top: 10%; left: 55%;", 
            4: "top: 25%; right: 13%;", 
            5: "top: 77%; right: 13%; transform: translateY(-50%);"
        }.get(idx, "")

    opp_html = ""; chips_html = ""

    for i in range(1, 6):
        p = rot[i]
        has_cards = (p in cards_in_play)
        cls = "seat-active" if has_cards else "seat-folded"
        cards = '<div class="opp-cards-mob"><div class="opp-card-mob"></div><div class="opp-card-mob right"></div></div>' if has_cards else ""
        ss = get_seat_style(i)
        opp_html += f'<div class="seat {cls}" style="{ss}">{cards}<span class="seat-label">{p}</span></div>'
        
        cs = get_chip_style(i)
        bet_amount = bets_on_table.get(p)
        if bet_amount is not None:
            bet_txt = f'<div class="bet-txt">{bet_amount}bb</div>'
            if bet_amount >= 15.0:
                chips_html += f'<div class="chip-container" style="{cs}"><div class="chip-4bet"></div><div class="chip-4bet" style="margin-top:-13px;"></div><div class="chip-4bet" style="margin-top:-13px;"></div>{bet_txt}</div>'
            elif bet_amount <= 1.0:
                if is_3bet_pot: chips_html += f'<div class="chip-container" style="{cs}"><div class="chip-3bet"></div>{bet_txt}</div>'
                else: chips_html += f'<div class="chip-container" style="{cs}"><div class="chip-mob"></div>{bet_txt}</div>'
            else:
                if is_3bet_pot: chips_html += f'<div class="chip-container" style="{cs}"><div class="chip-3bet"></div><div class="chip-3bet" style="margin-top:-13px;"></div>{bet_txt}</div>'
                else: chips_html += f'<div class="chip-container" style="{cs}"><div class="chip-mob"></div><div class="chip-mob" style="margin-top:-13px;"></div>{bet_txt}</div>'
        
        if p == btn_pos:
            bs = get_btn_style(i)
            chips_html += f'<div class="dealer-mob" style="{bs}">D</div>'

    hero_cs = get_chip_style(0)
    if display_hero_bet is not None: 
        bet_txt = f'<div class="bet-txt">{display_hero_bet}bb</div>'
        if display_hero_bet >= 15.0:
            chips_html += f'<div class="chip-container" style="{hero_cs}"><div class="chip-4bet"></div><div class="chip-4bet" style="margin-top:-13px;"></div><div class="chip-4bet" style="margin-top:-13px;"></div>{bet_txt}</div>'
        elif display_hero_bet <= 1.0:
            chips_html += f'<div class="chip-container" style="{hero_cs}"><div class="chip-mob"></div>{bet_txt}</div>'
        else:
            chips_html += f'<div class="chip-container" style="{hero_cs}"><div class="chip-mob"></div><div class="chip-mob" style="margin-top:-13px;"></div>{bet_txt}</div>'
        
    if rot[0] == btn_pos:
        hero_bs = get_btn_style(0)
        chips_html += f'<div class="dealer-mob" style="{hero_bs}">D</div>'

    html = f'<div class="mobile-game-area {combo_cls}">{shatter_html}<div class="crest-left-mob">{m_svg}</div><div class="crest-right-mob">{m_svg}</div><div class="mastery-glow"></div><div class="mob-info"><div class="mob-info-spot">{sp}</div><div class="mastery-badge rusty-{m_rust}">{m_icon} {m_name}</div><div class="mastery-bar-bg"><div class="mastery-bar-fill" style="width: {m_pct}%;"></div></div><div class="hands-left-mob">{hands_left_text}</div></div>{opp_html}{chips_html}<div class="hero-mob">{anim_html}<div class="card-mob"><div class="tl-mob {c1}">{h_val[0]}<br>{s1}</div><div class="c-mob {c1}">{s1}</div></div><div class="card-mob"><div class="tl-mob {c2}">{h_val[1]}<br>{s2}</div><div class="c-mob {c2}">{s2}</div></div><div class="rng-badge">{rng}</div></div></div>'
    
    st.markdown(html, unsafe_allow_html=True)

    if not st.session_state.last_error:
        if is_defense:
            st.markdown('<div class="rng-hint">RNG 0-Freq: ACTION &nbsp;|&nbsp; Freq-100: FOLD</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="rng-hint">RNG 0-Freq: RAISE &nbsp;|&nbsp; Freq-100: FOLD</div>', unsafe_allow_html=True)

    def handle_action(action):
        corr = (correct_act == action)
        st.session_state.session_hands += 1
        
        c_old = st.session_state.combo
        old_mult = 1.0
        if c_old >= 500: old_mult = 10.0
        elif c_old >= 250: old_mult = 5.0
        elif c_old >= 100: old_mult = 4.0
        elif c_old >= 50: old_mult = 3.0
        elif c_old >= 25: old_mult = 2.0
        elif c_old >= 10: old_mult = 1.5

        k = f"{src}_{sc}_{sp}".replace(" ","_")
        utils.update_srs_auto(k, st.session_state.hand, corr)
        
        utils.save_to_history({
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
            "Spot": sp, "Hand": f"{h_val}", "Result": int(corr), 
            "CorrectAction": correct_act, "UserAction": action
        })
        
        shield_used = False
        if corr:
            st.session_state.session_correct += 1
            st.session_state.combo += 1
            if st.session_state.combo in [100, 250, 500, 1000]:
                st.session_state.shields += 1
                
            st.session_state.last_error = False
            st.session_state.hand = None
        else:
            if st.session_state.shields > 0:
                st.session_state.shields -= 1
                st.session_state.shield_break_anim = True
                st.session_state.last_error = True
                shield_used = True
                st.session_state.msg = f"🛡️ ЩИТ СЛОМАН! Защита от мисклика. GTO: {correct_act}"
            else:
                st.session_state.combo = 0
                st.session_state.last_error = True
                st.session_state.msg = f"❌ WRONG! You chose {action}, but GTO is {correct_act}"
            
        c_new = st.session_state.combo
        new_mult = 1.0
        if c_new >= 500: new_mult = 10.0
        elif c_new >= 250: new_mult = 5.0
        elif c_new >= 100: new_mult = 4.0
        elif c_new >= 50: new_mult = 3.0
        elif c_new >= 25: new_mult = 2.0
        elif c_new >= 10: new_mult = 1.5

        if new_mult > old_mult:
            st.session_state.just_leveled_up = True

        try:
            import inspect
            sig = inspect.signature(utils.process_gamification)
            if 'shield_used' in sig.parameters:
                res = utils.process_gamification(corr, st.session_state.combo, st.session_state.session_hands, st.session_state.current_spot_key, shield_used=shield_used)
            else:
                res = utils.process_gamification(corr, st.session_state.combo, st.session_state.session_hands, st.session_state.current_spot_key)
            
            if isinstance(res, tuple):
                alerts = res[0]
                st.session_state.anim_reward = res[1]
            else:
                alerts = res
                
            if alerts: st.session_state.toast_msgs.extend(alerts)
        except Exception: pass
        
        try:
            curr_stats = utils.load_user_stats()
            curr_stats["combo"] = st.session_state.combo
            curr_stats["shields"] = st.session_state.shields
            utils.save_user_stats(curr_stats)
            if hasattr(utils, "force_sync"):
                utils.force_sync()
        except Exception: pass
        
        st.rerun()

    if st.session_state.last_error:
        st.markdown(f'<div style="background:#dc3545; color:white; padding:12px; border-radius:12px; text-align:center; font-weight:bold; margin-bottom:15px; font-size:16px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);">{st.session_state.msg}</div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🎯 Correct Range", "🧠 SRS Matrix"])
        with tab1:
            st.markdown(utils.render_range_matrix(data, st.session_state.hand), unsafe_allow_html=True)
        with tab2:
            st.markdown(utils.render_srs_matrix(data, src, sc, sp, utils.load_srs_data(), st.session_state.hand), unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("UNDERSTOOD, NEXT", type="primary", use_container_width=True):
            st.session_state.last_error = False
            st.session_state.hand = None
            st.session_state.shield_break_anim = False
            st.rerun()

    else:
        with st.expander("🫣 Peek Range", expanded=False):
            st.markdown(utils.render_range_matrix(data, st.session_state.hand), unsafe_allow_html=True)
            
        if is_defense:
            st.markdown("""<style>
                div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) button { background: linear-gradient(180deg, #6c757d, #495057) !important; box-shadow: 0 4px 0 #343a40 !important; }
                div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) button { background: linear-gradient(180deg, #20c997, #198754) !important; box-shadow: 0 4px 0 #0f5132 !important; }
                div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3) button { background: linear-gradient(180deg, #e83e8c, #dc3545) !important; box-shadow: 0 4px 0 #a02531 !important; }
            </style>""", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("FOLD", key="f"): handle_action("FOLD")
            with c2:
                if st.button("CALL", key="c"): handle_action("CALL")
            with c3:
                if st.button("RAISE", key="r"): handle_action("RAISE")
        else:
            st.markdown("""<style>
                div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) button { background: linear-gradient(180deg, #6c757d, #495057) !important; box-shadow: 0 4px 0 #343a40 !important; }
                div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) button { background: linear-gradient(180deg, #e83e8c, #dc3545) !important; box-shadow: 0 4px 0 #a02531 !important; }
            </style>""", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("FOLD", key="f"): handle_action("FOLD")
            with c2:
                if st.button("RAISE", key="r"): handle_action("RAISE")
