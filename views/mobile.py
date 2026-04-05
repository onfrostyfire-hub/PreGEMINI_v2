import streamlit as st
import random
from datetime import datetime
import poker_utils as utils

def show():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@500;700;900&display=swap');

        .block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; max-width: 100% !important; overflow-x: hidden !important; }
        [data-testid="stExpander"] { margin-top: -5px !important; margin-bottom: 5px !important; }
        
        div[data-testid="stHorizontalBlock"] { display: grid !important; grid-template-columns: repeat(auto-fit, minmax(10px, 1fr)) !important; gap: 8px !important; width: 100% !important; }
        div[data-testid="column"] { width: 100% !important; min-width: 0 !important; max-width: 100% !important; margin-bottom: 0 !important; }
        div[data-testid="stButton"] { width: 100% !important; }
        div[data-testid="stButton"] button { width: 100% !important; height: 50px !important; padding: 0 !important; border-radius: 12px !important; border: none !important; transition: transform 0.1s !important; }
        div[data-testid="stButton"] button:active { transform: translateY(4px) !important; box-shadow: 0 1px 0 transparent !important; }
        div[data-testid="stButton"] button p { font-family: 'Roboto', sans-serif !important; font-size: 15px !important; font-weight: 900 !important; margin: 0 !important; letter-spacing: 0.5px !important; text-transform: uppercase !important; color: #ffffff !important; }

        .mobile-game-area { 
            position: relative; width: 100%; height: 250px; 
            margin: 35px auto 55px auto; 
            border-radius: 125px; box-shadow: 0 4px 15px rgba(0,0,0,0.8); 
            transition: background 0.5s, box-shadow 0.5s, border-color 0.5s;
            border-style: solid; border-width: 6px;
        }
        
        .mastery-glow { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border-radius: inherit; pointer-events: none; z-index: 1; transition: box-shadow 0.5s ease; }
        .mastery-badge { font-size: 9px; font-weight: bold; background: rgba(0,0,0,0.6); padding: 2px 8px; border-radius: 10px; display: inline-flex; align-items: center; gap: 4px; margin-top: 4px; text-transform: uppercase; border: 1px solid rgba(255,255,255,0.1); z-index: 30; }
        .rusty-True { filter: grayscale(100%) opacity(0.6); }
        .mastery-bar-bg { width: 80px; height: 3px; background: #111; border-radius: 2px; margin: 4px auto 0 auto; overflow: hidden; box-shadow: inset 0 1px 2px rgba(0,0,0,0.8); z-index: 30; }
        .mastery-bar-fill { height: 100%; transition: width 0.3s; }
        .hands-left-mob { font-size: 8px; color: #aaa; text-transform: uppercase; font-weight: bold; margin-top: 2px; }
        
        .crest-left-mob { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); width: 75px; height: 75px; z-index: 1; pointer-events: none; display: flex; justify-content: center; align-items: center; }
        .crest-right-mob { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); width: 75px; height: 75px; z-index: 1; pointer-events: none; display: flex; justify-content: center; align-items: center; }
        
        .combo-glow-5 { border-color: #0dcaf0 !important; box-shadow: 0 0 10px rgba(13, 202, 240, 0.4), 0 4px 15px rgba(0,0,0,0.8) !important; }
        .combo-glow-10 { border-color: #ffc107 !important; box-shadow: 0 0 15px rgba(255, 193, 7, 0.5), 0 4px 15px rgba(0,0,0,0.8) !important; }
        .combo-glow-25 { border-color: #fd7e14 !important; box-shadow: 0 0 20px rgba(253, 126, 20, 0.6), 0 4px 15px rgba(0,0,0,0.8) !important; animation: pulse-slow 2s infinite; }
        .combo-glow-50 { border-color: #dc3545 !important; box-shadow: 0 0 30px rgba(220, 53, 69, 0.7), 0 4px 15px rgba(0,0,0,0.8) !important; animation: pulse-menace 1.5s infinite; }
        .combo-glow-100 { border-color: #6f42c1 !important; box-shadow: 0 0 40px rgba(111, 66, 193, 0.8), 0 4px 15px rgba(0,0,0,0.8) !important; animation: pulse-neon 1s infinite; }
        .combo-glow-200 { border-color: #00e5ff !important; box-shadow: 0 0 50px rgba(0, 229, 255, 0.8), 0 4px 15px rgba(0,0,0,0.8) !important; animation: pulse-plasma 1s infinite alternate; }
        .combo-glow-500 { border-color: #ff00ff !important; box-shadow: 0 0 60px rgba(255, 0, 255, 0.9), 0 4px 15px rgba(0,0,0,0.8) !important; animation: pulse-matrix 0.8s infinite alternate; }
        .combo-glow-1000 { border-color: #00ff00 !important; box-shadow: 0 0 80px rgba(0, 255, 0, 1.0), 0 4px 15px rgba(0,0,0,0.8) !important; animation: pulse-god 0.5s infinite alternate; }
        
        @keyframes pulse-slow { 0% { box-shadow: 0 0 15px rgba(253, 126, 20, 0.4); } 50% { box-shadow: 0 0 25px rgba(253, 126, 20, 0.7); } 100% { box-shadow: 0 0 15px rgba(253, 126, 20, 0.4); } }
        @keyframes pulse-menace { 0% { box-shadow: 0 0 20px rgba(220, 53, 69, 0.5); } 50% { box-shadow: 0 0 40px rgba(220, 53, 69, 0.9); } 100% { box-shadow: 0 0 20px rgba(220, 53, 69, 0.5); } }
        @keyframes pulse-neon { 0% { box-shadow: 0 0 30px rgba(111, 66, 193, 0.6); } 50% { box-shadow: 0 0 60px rgba(111, 66, 193, 1.0); } 100% { box-shadow: 0 0 30px rgba(111, 66, 193, 0.6); } }
        @keyframes pulse-plasma { 0% { box-shadow: 0 0 30px rgba(0, 229, 255, 0.6); } 100% { box-shadow: 0 0 70px rgba(0, 229, 255, 1.0); } }
        @keyframes pulse-matrix { 0% { box-shadow: 0 0 40px rgba(255, 0, 255, 0.7); } 100% { box-shadow: 0 0 90px rgba(255, 0, 255, 1.0); } }
        @keyframes pulse-god { 0% { box-shadow: 0 0 50px rgba(0, 255, 0, 0.8); } 100% { box-shadow: 0 0 120px rgba(0, 255, 0, 1.0); } }

        .mob-info { position: absolute; top: 24%; width: 100%; text-align: center; pointer-events: none; z-index: 15; }
        .mob-info-spot { font-size: 20px; font-weight: 900; color: rgba(255,255,255,0.15); line-height: 1; z-index: 30; position: relative; }
        .seat { position: absolute; width: 44px; height: 44px; background: #222; border: 1px solid #444; border-radius: 8px; display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 5; }
        .seat-label { font-size: 9px; color: #fff; font-weight: bold; margin-top: auto; margin-bottom: 2px; }
        .seat-active { border-color: #ffc107; background: #2a2a2a; }
        .seat-folded { opacity: 0.4; border-color: #333; }
        
        .opp-cards-mob { position: absolute; top: -14px; display: flex; z-index: 20; }
        .opp-card-mob { width: 18px; height: 26px; background: #fff; border-radius: 2px; border: 1px solid #777; background-image: repeating-linear-gradient(45deg, #b71c1c 0, #b71c1c 2px, #fff 2px, #fff 4px); box-shadow: 1px 1px 3px rgba(0,0,0,0.8); }
        .opp-card-mob.right { margin-left: -8px; transform: rotate(12deg) translateY(2px); }

        .chip-container { position: absolute; z-index: 25; display: flex; flex-direction: column; align-items: center; pointer-events: none; }
        .chip-mob { width: 14px; height: 14px; background: #111; border: 2px dashed #d32f2f; border-radius: 50%; box-shadow: 1px 1px 2px rgba(0,0,0,0.8); }
        .chip-3bet { width: 16px; height: 16px; background: #d32f2f; border: 2px solid #fff; border-radius: 50%; box-shadow: 0 2px 5px rgba(0,0,0,0.8); }
        .dealer-mob { width: 16px; height: 16px; background: #ffc107; border-radius: 50%; color: #000; font-weight: bold; font-size: 9px; display: flex; justify-content: center; align-items: center; border: 1px solid #bfa006; position: absolute; z-index: 35; }
        .bet-txt { font-size: 10px; font-weight: bold; color: #fff; text-shadow: 1px 1px 2px #000; background: rgba(0,0,0,0.6); padding: 1px 3px; border-radius: 4px; margin-top: -5px; z-index: 20; }
        
        .hero-mob { position: absolute; bottom: -50px; left: 50%; transform: translateX(-50%); display: flex; gap: 5px; z-index: 30; padding: 5px 10px; border-radius: 12px; transition: all 0.5s ease; }
        .card-mob { width: 45px; height: 64px; background: white; border-radius: 4px; position: relative; color: black; box-shadow: 0 2px 5px rgba(0,0,0,0.5); }
        .tl-mob { position: absolute; top: 1px; left: 3px; font-weight: bold; font-size: 14px; line-height: 1; }
        .c-mob { position: absolute; top: 55%; left: 50%; transform: translate(-50%,-50%); font-size: 26px; }
        .suit-red { color: #d32f2f; } .suit-blue { color: #0056b3; } .suit-black { color: #111; } .suit-green { color: #198754; }
        .rng-badge { position: absolute; bottom: 50px; right: -15px; width: 30px; height: 30px; background: #6f42c1; border: 2px solid #fff; border-radius: 50%; color: white; font-weight: bold; font-size: 12px; display: flex; justify-content: center; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.5); z-index: 40; }
        
        .floating-reward { position: absolute; top: -30px; left: 50%; transform: translateX(-50%); font-size: 24px; font-weight: 900; text-shadow: 0px 2px 5px rgba(0,0,0,0.9), 0px 0px 2px #000; z-index: 100; pointer-events: none; animation: floatUpFade 1.2s ease-out forwards; }
        @keyframes floatUpFade { 0% { opacity: 1; transform: translate(-50%, 0) scale(0.5); } 20% { opacity: 1; transform: translate(-50%, -15px) scale(1.2); } 100% { opacity: 0; transform: translate(-50%, -80px) scale(1); } }
        
        .rage-bar-container { width: 100%; max-width: 700px; margin: 0 auto 15px auto; background: rgba(0,0,0,0.6); border: 2px solid #333; border-radius: 20px; padding: 4px; display: flex; align-items: center; position: relative; box-shadow: inset 0 2px 10px rgba(0,0,0,0.8); height: 32px; }
        .rage-bar-fill { height: 100%; border-radius: 16px; transition: width 0.3s ease-out; position: relative; overflow: hidden; box-shadow: inset 0 2px 5px rgba(255,255,255,0.3), inset 0 -2px 5px rgba(0,0,0,0.4); }
        
        /* Хаотичные пузырьки */
        .rage-bar-fill::before, .rage-bar-fill::after { content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background-image: radial-gradient(circle, rgba(255,255,255,0.8) 1px, transparent 2px), radial-gradient(circle, rgba(255,255,255,0.5) 2px, transparent 3px), radial-gradient(circle, rgba(255,255,255,0.4) 1px, transparent 2px); z-index: 1; pointer-events: none; }
        .rage-bar-fill::before { background-size: 20px 25px, 35px 40px, 15px 20px; animation: bubbleRise1 1.2s infinite linear; }
        .rage-bar-fill::after { background-size: 25px 30px, 45px 50px, 22px 28px; animation: bubbleRise2 1.7s infinite linear; opacity: 0.6; }
        @keyframes bubbleRise1 { 0% { background-position: 0px 25px, 0px 40px, 0px 20px; } 50% { background-position: 5px 12.5px, -5px 20px, 3px 10px; } 100% { background-position: 0px 0px, 0px 0px, 0px 0px; } }
        @keyframes bubbleRise2 { 0% { background-position: 0px 30px, 0px 50px, 0px 28px; } 50% { background-position: -6px 15px, 6px 25px, -4px 14px; } 100% { background-position: 0px 0px, 0px 0px, 0px 0px; } }

        .rage-labels { position: absolute; width: 100%; display: flex; justify-content: space-between; padding: 0 15px; font-weight: 900; font-size: 14px; color: #fff; text-shadow: 0 1px 3px #000, 0 0 5px #000; pointer-events: none; z-index: 2; top: 50%; transform: translateY(-50%); }
        .rage-pulse { animation: ragePulse 0.4s infinite alternate; }
        @keyframes ragePulse { 0% { filter: brightness(1); box-shadow: 0 0 5px #dc3545; } 100% { filter: brightness(1.3); box-shadow: 0 0 25px #dc3545, inset 0 0 10px #fff; } }
        .rage-flash { animation: whiteFlash 0.6s ease-out; }
        @keyframes whiteFlash { 0% { box-shadow: 0 0 50px #fff, inset 0 0 50px #fff; background: #fff; border-color: #fff; } 100% { box-shadow: 0 0 0 transparent; } }

        .glass-shatter { position: absolute; top:0; left:0; right:0; bottom:0; z-index:999; pointer-events: none; background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(255,255,255,0.2) 10px, rgba(255,255,255,0.2) 12px), repeating-linear-gradient(-45deg, transparent, transparent 15px, rgba(255,255,255,0.3) 15px, rgba(255,255,255,0.3) 18px); animation: shatterAnim 0.8s ease-out forwards; }
        @keyframes shatterAnim { 0% {opacity:1; transform: scale(1);} 100% {opacity:0; transform: scale(1.1);} }

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
            st.session_state.hand = None; st.rerun()

    pool = sel_spots_keys
    if not pool:
        st.warning("⚠️ No spots selected.")
        st.stop()

    # ИНИЦИАЛИЗАЦИЯ И СИНХРОНИЗАЦИЯ КОМБО С БАЗОЙ
    stats_data_init = utils.load_user_stats()
    if 'combo' not in st.session_state: st.session_state.combo = stats_data_init.get("combo", 0)
    if 'shields' not in st.session_state: st.session_state.shields = stats_data_init.get("shields", 0)

    if 'shield_break_anim' not in st.session_state: st.session_state.shield_break_anim = False
    if 'session_hands' not in st.session_state: st.session_state.session_hands = 0
    if 'session_correct' not in st.session_state: st.session_state.session_correct = 0
    
    if 'toast_msgs' not in st.session_state: st.session_state.toast_msgs = []
    if st.session_state.toast_msgs:
        for msg in st.session_state.toast_msgs:
            msg_str = str(msg)
            st.toast(msg_str, icon="🔥" if "Combo" in msg_str else "🎯")
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
    rank_name, next_xp = utils.get_rank_info(stats_data["xp"])
    c = st.session_state.combo
    progress_pct = int((stats_data["xp"] / next_xp) * 100) if next_xp != "MAX" else 100
    
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

    if m_rank <= 1:
        table_bg = "radial-gradient(ellipse at center, #4b6b50 0%, #2a3c2d 100%)"
        table_border = "#3b3b3b"
        hero_bg = "#495057"
        hero_border = "#6c757d"
        hero_shadow = "none"
    elif m_rank <= 4:
        table_bg = "radial-gradient(ellipse at center, #2e7d32 0%, #1b5e20 100%)"
        table_border = "#4a1c1c"
        hero_bg = "#212529"
        hero_border = "#adb5bd"
        hero_shadow = "0 0 10px #adb5bd"
    else:
        table_bg = "radial-gradient(ellipse at center, #2b1b3d 0%, #11081a 100%)"
        table_border = "#1a1a1a"
        hero_bg = "#111"
        hero_border = "#ffc107"
        hero_shadow = "0 0 25px #ffc107, inset 0 0 15px #ffc107"

    st.markdown(f"<style>.mobile-game-area {{ background: {table_bg} !important; border-color: {table_border} !important; }} .hero-mob {{ background: {hero_bg} !important; border: 2px solid {hero_border} !important; box-shadow: {hero_shadow} !important; }}</style>", unsafe_allow_html=True)

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

    combo_cls = ""
    if c >= 1000: combo_cls = "combo-glow-1000"
    elif c >= 500: combo_cls = "combo-glow-500"
    elif c >= 200: combo_cls = "combo-glow-200"
    elif c >= 100: combo_cls = "combo-glow-100"
    elif c >= 50: combo_cls = "combo-glow-50"
    elif c >= 25: combo_cls = "combo-glow-25"
    elif c >= 10: combo_cls = "combo-glow-10"
    elif c >= 5: combo_cls = "combo-glow-5"

    shield_display = f'<span style="font-size:14px; margin-left:8px; filter:drop-shadow(0 0 5px #0dcaf0); display:{"inline-flex" if st.session_state.shields > 0 else "none"};">🛡️x{st.session_state.shields}</span>'
    combo_badge = f'<div style="flex:1; display:flex; justify-content:center; align-items:center;"><div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 4px 12px; border-radius: 20px; display: inline-flex; align-items: center; justify-content: center;"><span style="font-size:18px; font-weight:900; color:#fff;">🔥 {c}</span>{shield_display}</div></div>'

    header_html = f'<div style="background:#111; border-radius:10px; margin-bottom:10px; border:1px solid #333; overflow:hidden; font-family:sans-serif;"><div style="height: 3px; width: 100%; background: #222;"><div style="height: 100%; width: {wr if sh > 0 else 100}%; background: {wr_color if sh > 0 else "#444"}; transition: width 0.3s;"></div></div><div style="padding:6px 12px 0 12px; display:flex; justify-content:space-between; align-items:center;"><div style="flex:1;"><div style="font-size:13px; font-weight:bold; color:#ffc107;">{rank_name}</div><div style="background:#333; height:4px; border-radius:2px; margin-top:3px; width:100%;"><div style="background:#28a745; height:100%; width:{progress_pct}%; border-radius:2px;"></div></div></div><div style="font-size:10px; color:#aaa; margin-left:10px; font-weight:bold;">${stats_data["xp"]} / ${next_xp}</div></div><div style="display:flex; justify-content:space-between; align-items:center; padding:6px 12px;"><div style="flex:1;"><div style="font-size:11px; font-weight:bold; color:#aaa;">Winrate</div><div style="font-size:13px; font-weight:bold; color:{wr_color};">{wr}%</div></div>{combo_badge}<div style="flex:1; text-align:right;"><div style="font-size:11px; font-weight:bold; color:#aaa;">Hands</div><div style="font-size:13px; font-weight:bold; color:#fff;">{sh}</div></div></div></div>'
    
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
        return {0: "bottom: -20px; left: 50%; transform: translateX(-50%);", 1: "bottom: 10%; left: -5%;", 2: "top: 10%; left: -5%;", 
                3: "top: -20px; left: 50%; transform: translateX(-50%);", 4: "top: 10%; right: -5%;", 5: "bottom: 10%; right: -5%;"}.get(idx, "")

    def get_chip_style(idx):
        return {
            0: "bottom: 35px; left: 50%; transform: translateX(-50%);", 
            1: "bottom: 20%; left: 10%;", 
            2: "top: 20%; left: 10%;",
            3: "top: 35px; left: 50%; transform: translateX(-50%);", 
            4: "top: 20%; right: 10%;", 
            5: "bottom: 20%; right: 10%;"
        }.get(idx, "")

    def get_btn_style(idx):
        return {0: "bottom: -10px; left: 50%; margin-left: -80px; z-index: 35;", 1: "bottom: 25%; left: 16%;", 2: "top: 10%; left: 16%;",
                3: "top: 10%; left: 60%;", 4: "top: 10%; right: 16%;", 5: "bottom: 25%; right: 12%;"}.get(idx, "")

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
            if bet_amount <= 1.0:
                if is_3bet_pot: chips_html += f'<div class="chip-container" style="{cs}"><div class="chip-3bet"></div>{bet_txt}</div>'
                else: chips_html += f'<div class="chip-container" style="{cs}"><div class="chip-mob"></div>{bet_txt}</div>'
            else:
                if is_3bet_pot: chips_html += f'<div class="chip-container" style="{cs}"><div class="chip-3bet"></div><div class="chip-3bet" style="margin-top:-12px;"></div>{bet_txt}</div>'
                else: chips_html += f'<div class="chip-container" style="{cs}"><div class="chip-mob"></div><div class="chip-mob" style="margin-top:-5px;"></div>{bet_txt}</div>'
        
        if p == btn_pos:
            bs = get_btn_style(i)
            chips_html += f'<div class="dealer-mob" style="{bs}">D</div>'

    hero_cs = get_chip_style(0)
    if display_hero_bet is not None: 
        bet_txt = f'<div class="bet-txt">{display_hero_bet}bb</div>'
        if display_hero_bet <= 1.0:
            chips_html += f'<div class="chip-container" style="{hero_cs}"><div class="chip-mob"></div>{bet_txt}</div>'
        else:
            chips_html += f'<div class="chip-container" style="{hero_cs}"><div class="chip-mob"></div><div class="chip-mob" style="margin-top:-5px;"></div>{bet_txt}</div>'
        
    if rot[0] == btn_pos:
        hero_bs = get_btn_style(0)
        chips_html += f'<div class="dealer-mob" style="{hero_bs}">D</div>'

    html = f'<div class="mobile-game-area {combo_cls}">{shatter_html}<div class="crest-left-mob">{m_svg}</div><div class="crest-right-mob">{m_svg}</div><div class="mastery-glow"></div><div class="mob-info"><div class="mob-info-spot">{sp}</div><div class="mastery-badge rusty-{m_rust}">{m_icon} {m_name}</div><div class="mastery-bar-bg"><div class="mastery-bar-fill" style="width: {m_pct}%; background: {m_color};"></div></div><div class="hands-left-mob">{hands_left_text}</div></div>{opp_html}{chips_html}<div class="hero-mob">{anim_html}<div class="card-mob"><div class="tl-mob {c1}">{h_val[0]}<br>{s1}</div><div class="c-mob {c1}">{s1}</div></div><div class="card-mob"><div class="tl-mob {c2}">{h_val[1]}<br>{s2}</div><div class="c-mob {c2}">{s2}</div></div><div class="rng-badge">{rng}</div></div></div>'
    
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
                st.session_state.toast_msgs.append(f"Combo x{st.session_state.combo}! +1 🛡️ Shield!")
                
            st.session_state.last_error = False
            st.session_state.hand = None
            
            if st.session_state.combo in [10, 25, 50, 100, 250, 500, 1000]:
                msgs = {
                    10: "Combo x10! Warming up.", 25: "Combo x25! Reading them like a book.",
                    50: "Combo x50! Sniper.", 100: "Combo x100! Machine.",
                    250: "Combo x250! Are you even human?", 500: "Combo x500! God Mode activated.",
                    1000: "Combo x1000! Solvers fear you."
                }
                st.session_state.toast_msgs.append(msgs.get(st.session_state.combo, "Unstoppable!"))
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

        # СОХРАНЕНИЕ КОМБО И ЩИТОВ В ОБЛАКО
        try:
            curr_settings = utils.load_user_settings()
            if "stats" not in curr_settings: curr_settings["stats"] = {}
            curr_settings["stats"]["combo"] = st.session_state.combo
            curr_settings["stats"]["shields"] = st.session_state.shields
            utils.save_user_settings(curr_settings)
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
