import streamlit as st
import json
import random
import time
from datetime import datetime
import pandas as pd
import poker_utils

def get_exact_hand_weight(hand, range_str):
    if not range_str or not isinstance(range_str, str): return 0.0
    cleaned = range_str.replace('\n', ' ').replace('\r', '')
    items = [x.strip() for x in cleaned.split(',')]
    for item in items:
        if ':' in item:
            h_part, w_part = item.split(':')
            try: weight = float(w_part)
            except: weight = 100.0
        else:
            h_part = item
            weight = 100.0
        if h_part == hand: return weight
    return 0.0

def get_card_html(card_str):
    if not card_str or len(card_str) < 2: return ""
    rank = card_str[0]
    suit = card_str[1].lower()
    
    if suit == 's': color, suit_sym = "#343a40", "♠"
    elif suit == 'h': color, suit_sym = "#dc3545", "♥"
    elif suit == 'd': color, suit_sym = "#0dcaf0", "♦"
    elif suit == 'c': color, suit_sym = "#28a745", "♣"
    else: color, suit_sym = "#343a40", suit
    
    return f'''
    <div style="background: #fff; border: 1px solid #dee2e6; border-radius: 6px; 
                width: 48px; height: 68px; display: flex; flex-direction: column; 
                justify-content: center; align-items: center; box-shadow: 0 3px 6px rgba(0,0,0,0.15); 
                margin: 0 3px; position: relative;">
        <div style="color: {color}; font-size: 22px; font-weight: 900; line-height: 1; position: absolute; top: 4px; left: 6px;">{rank}</div>
        <div style="color: {color}; font-size: 28px; line-height: 1; margin-top: 10px;">{suit_sym}</div>
    </div>
    '''

def init_fish_state():
    if "fish_initialized" not in st.session_state:
        st.session_state.fish_stats = poker_utils.load_user_stats(is_fish=True)
        st.session_state.fish_combo = 0
        st.session_state.fish_shields = 0
        st.session_state.fish_current_spot = None
        st.session_state.fish_hand = ""
        st.session_state.fish_feedback = None
        st.session_state.fish_settings_modal_open = False
        st.session_state.fish_initialized = True

def show_settings_modal():
    if not st.session_state.get("fish_settings_modal_open", False): return
    
    st.markdown("""
    <style>
        .modal-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.8); z-index: 9998; backdrop-filter: blur(5px); }
        .modal-content { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: #1a1c20; border: 1px solid #333; border-radius: 12px; padding: 25px; z-index: 9999; width: 400px; max-width: 90vw; box-shadow: 0 10px 30px rgba(0,0,0,0.7); }
        .modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #333; padding-bottom: 10px; }
        .modal-header h3 { color: #fff; margin: 0; font-size: 18px; }
        .close-btn { background: transparent; border: none; color: #888; font-size: 24px; cursor: pointer; line-height: 1; }
        .close-btn:hover { color: #fff; }
        .stToggle { margin-bottom: 15px; }
    </style>
    <div class="modal-overlay"></div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="modal-content">', unsafe_allow_html=True)
        st.markdown('<div class="modal-header"><h3>⚙️ Fish Settings</h3></div>', unsafe_allow_html=True)
        
        sets = poker_utils.load_user_settings(is_fish=True)
        
        c1, c2 = st.columns([4, 1])
        with c1: st.markdown("<div style='color:#ccc; font-size:14px; margin-top:8px;'>Show Spot Mastery Info</div>", unsafe_allow_html=True)
        with c2: sm_on = st.toggle("SM", value=sets.get("show_mastery", True), key="set_f_sm", label_visibility="collapsed")
        
        c1, c2 = st.columns([4, 1])
        with c1: st.markdown("<div style='color:#ccc; font-size:14px; margin-top:8px;'>Show Matrix After Action</div>", unsafe_allow_html=True)
        with c2: mat_on = st.toggle("MAT", value=sets.get("show_matrix", False), key="set_f_mat", label_visibility="collapsed")
        
        if st.button("Save & Close", use_container_width=True, type="primary"):
            sets["show_mastery"] = sm_on
            sets["show_matrix"] = mat_on
            poker_utils.save_user_settings(sets, is_fish=True)
            st.session_state.fish_settings_modal_open = False
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)

def render_hud(stats, combo, shields):
    xp = stats.get("xp", 0)
    c_rank, next_xp = poker_utils.get_rank_info(xp)
    
    if next_xp == "MAX": xp_pct = 100
    else: xp_pct = min(100, int((xp / next_xp) * 100))
    
    shields_html = ""
    for _ in range(shields):
        shields_html += '<div style="width: 14px; height: 14px; border-radius: 50%; background: #0dcaf0; box-shadow: 0 0 8px #0dcaf0; border: 2px solid #fff; margin: 0 2px;"></div>'
        
    st.markdown(f"""
    <div style="background: #111; padding: 15px; border-radius: 10px; border: 1px solid #333; margin-bottom: 15px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="color: #aaa; font-size: 10px; font-weight: bold; letter-spacing: 1px;">RANK</div>
                <div style="color: #ffc107; font-size: 18px; font-weight: 900;">{c_rank}</div>
            </div>
            <div style="text-align: center;">
                <div style="color: #aaa; font-size: 10px; font-weight: bold; letter-spacing: 1px;">COMBO</div>
                <div style="color: #fff; font-size: 18px; font-weight: 900;">x{combo}</div>
            </div>
            <div style="text-align: center;">
                <div style="color: #aaa; font-size: 10px; font-weight: bold; letter-spacing: 1px;">SHIELDS</div>
                <div style="display: flex; justify-content: center; margin-top: 4px; min-height: 14px;">
                    {shields_html}
                </div>
            </div>
            <div style="text-align: right;">
                <div style="color: #aaa; font-size: 10px; font-weight: bold; letter-spacing: 1px;">XP</div>
                <div style="color: #28a745; font-size: 18px; font-weight: 900;">{xp}</div>
            </div>
        </div>
        <div style="background: #222; height: 6px; border-radius: 3px; margin-top: 12px; overflow: hidden;">
            <div style="background: linear-gradient(90deg, #ffc107, #ff5722); height: 100%; width: {xp_pct}%; box-shadow: 0 0 10px #ff5722;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def generate_spot():
    db = poker_utils.load_fish_data()
    if not db: return False
    
    vpip_sel = st.session_state.get("fish_filter_vpip", [])
    pos_sel = st.session_state.get("fish_filter_pos", [])
    line_sel = st.session_state.get("fish_filter_line", [])
    board_sel = st.session_state.get("fish_filter_board", [])
    runout_sel = st.session_state.get("fish_filter_runout", [])
    
    pool = []
    vpips = vpip_sel if vpip_sel else list(db.keys())
    for vp in vpips:
        if vp not in db: continue
        textures = board_sel if board_sel else list(db[vp].keys())
        for tex in textures:
            if tex not in db[vp]: continue
            pos_data = db[vp][tex]
            positions = pos_sel if pos_sel else list(pos_data.keys())
            for pos in positions:
                if pos not in pos_data: continue
                line_data = pos_data[pos]
                lines = line_sel if line_sel else list(line_data.keys())
                for line in lines:
                    if line not in line_data: continue
                    runout_data = line_data[line]
                    runouts = runout_sel if runout_sel else list(runout_data.keys())
                    for runout in runouts:
                        if runout not in runout_data: continue
                        spot_info = runout_data[runout]
                        if not spot_info.get("training") or not spot_info.get("actions"): continue
                        
                        pool.append({
                            "vpip": vp, "pos": pos, "line": line, "texture": tex, "runout": runout,
                            "data": spot_info
                        })
                        
    if not pool: return False
        
    chosen = random.choice(pool)
    st.session_state.fish_current_spot = chosen
    
    training_str = chosen["data"].get("training", "")
    hands = [h.strip() for h in training_str.split(",") if h.strip()]
    if not hands: return False
    
    st.session_state.fish_hand = random.choice(hands)
    st.session_state.fish_feedback = None
    return True

def handle_action(user_action):
    spot = st.session_state.fish_current_spot
    hand = st.session_state.fish_hand
    actions = spot["data"]["actions"]
    ranges = spot["data"]["ranges"]
    
    weights = []
    for act in actions:
        w = get_exact_hand_weight(hand, ranges.get(act, ""))
        weights.append((act, w))
        
    total_w = sum(w for _, w in weights)
    if total_w == 0:
        correct_action = actions[0] if actions else "UNKNOWN"
    else:
        roll = random.uniform(0, total_w)
        curr = 0
        correct_action = actions[-1]
        for act, w in weights:
            curr += w
            if roll <= curr:
                correct_action = act
                break
                
    is_correct = (user_action == correct_action)
    shield_used = False
    
    if is_correct:
        st.session_state.fish_combo += 1
        if st.session_state.fish_combo in [100, 250, 500, 1000]:
            st.session_state.fish_shields += 1
    else:
        if st.session_state.fish_shields > 0:
            st.session_state.fish_shields -= 1
            shield_used = True
        else:
            st.session_state.fish_combo = 0
            
    poker_utils.process_gamification(
        is_correct, st.session_state.fish_combo, 
        st.session_state.fish_stats.get("total_hands", 0), 
        spot_key=f"{spot['vpip']}_{spot['texture']}", 
        shield_used=shield_used, is_fish=True
    )
    
    record = {
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Fish_Type": spot["vpip"],
        "Position": spot["pos"],
        "Action_Line": spot["line"],
        "Texture": spot["texture"],
        "Runout": spot["runout"],
        "Hand": hand,
        "Action_Taken": user_action,
        "Correct_Action": correct_action,
        "Result": 1 if is_correct else 0,
        "XP": 0
    }
    poker_utils.save_to_history(record, is_fish=True)
    
    st.session_state.fish_feedback = {
        "correct": is_correct,
        "shield": shield_used,
        "expected": correct_action,
        "ranges": spot["data"].copy() 
    }
    st.session_state.fish_stats = poker_utils.load_user_stats(is_fish=True)

def show():
    init_fish_state()
    show_settings_modal()
    
    st.markdown("""
    <style>
        .table-container { background: #161a1d; padding: 20px; border-radius: 12px; border: 1px solid #343a40; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        .poker-table { background: radial-gradient(ellipse at center, #1e5a3a 0%, #0d2b18 100%); border-radius: 60px; padding: 40px 20px; border: 12px solid #2a1610; box-shadow: inset 0 0 40px rgba(0,0,0,0.8), 0 15px 30px rgba(0,0,0,0.6); position: relative; min-height: 350px; display: flex; flex-direction: column; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .felt-line { position: absolute; top: 15px; bottom: 15px; left: 15px; right: 15px; border: 2px dashed rgba(255,255,255,0.15); border-radius: 45px; pointer-events: none; }
        .info-hook { position: absolute; top: 25px; left: 35px; width: 28px; height: 28px; background: rgba(0,0,0,0.4); border: 2px solid rgba(255,255,255,0.3); border-radius: 50%; color: #ddd; display: flex; justify-content: center; align-items: center; font-weight: bold; font-family: serif; text-decoration: none; transition: 0.2s; z-index: 10; font-size: 14px; }
        .info-hook:hover { background: #0dcaf0; color: #000; border-color: #0dcaf0; box-shadow: 0 0 12px #0dcaf0; }
        .community-cards { display: flex; justify-content: center; align-items: center; min-height: 90px; margin: 20px 0; z-index: 5; }
        .pot-display { background: rgba(0,0,0,0.6); border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; padding: 6px 20px; color: #ffc107; font-weight: 900; font-size: 14px; letter-spacing: 1px; margin-bottom: 15px; }
        .villain-badge { background: #dc3545; color: white; padding: 5px 15px; border-radius: 6px; font-size: 12px; font-weight: 900; text-transform: uppercase; box-shadow: 0 4px 8px rgba(0,0,0,0.5); display: inline-block; border: 2px solid #a71d2a; letter-spacing: 1px; }
        .chip-stack { display: flex; flex-direction: column; align-items: center; position: absolute; top: 35px; right: 45px; z-index: 10; }
        .chip { background: repeating-linear-gradient(0deg, #f1c40f, #f1c40f 4px, #333 4px, #333 8px); border-radius: 50%; width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; font-size: 11px; font-weight: 900; color: #fff; text-shadow: 1px 1px 2px #000; box-shadow: 2px 4px 6px rgba(0,0,0,0.6); border: 3px solid #f39c12; }
        .hero-section { display: flex; justify-content: center; align-items: center; z-index: 5; background: rgba(0,0,0,0.3); padding: 10px 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.05); }
        .correct-flash { animation: flashGreen 0.6s ease-out; }
        .wrong-flash { animation: flashRed 0.6s ease-out; }
        @keyframes flashGreen { 0% { box-shadow: inset 0 0 100px rgba(40,167,69,0.9), 0 15px 30px rgba(0,0,0,0.6); } 100% { box-shadow: inset 0 0 40px rgba(0,0,0,0.8), 0 15px 30px rgba(0,0,0,0.6); } }
        @keyframes flashRed { 0% { box-shadow: inset 0 0 100px rgba(220,53,69,0.9), 0 15px 30px rgba(0,0,0,0.6); } 100% { box-shadow: inset 0 0 40px rgba(0,0,0,0.8), 0 15px 30px rgba(0,0,0,0.6); } }
        .spot-info-panel { background: #111; border: 1px solid #333; border-radius: 8px; padding: 15px; margin-bottom: 15px; }
        
        div[data-testid="stHorizontalBlock"] { gap: 8px !important; }
        .action-btn button { width: 100% !important; background: linear-gradient(180deg, #2c3034 0%, #1a1d20 100%) !important; border: 1px solid #495057 !important; color: #f8f9fa !important; padding: 15px !important; border-radius: 8px !important; font-weight: 900 !important; font-size: 14px !important; text-transform: uppercase !important; box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important; transition: all 0.2s !important; height: 60px !important; }
        .action-btn button:hover { border-color: #ffc107 !important; color: #ffc107 !important; transform: translateY(-2px) !important; box-shadow: 0 6px 12px rgba(255,193,7,0.2) !important; }
    </style>
    """, unsafe_allow_html=True)

    col_view1, col_view2 = st.columns([8, 2])
    with col_view2:
        view = st.radio("View", ["💻 Desktop", "📱 Mobile"], index=0 if st.session_state.get("actual_view_type", "💻 Desktop") == "💻 Desktop" else 1, horizontal=True, label_visibility="collapsed")
        if view != st.session_state.get("actual_view_type"):
            st.session_state.actual_view_type = view
            st.rerun()

    sets = poker_utils.load_user_settings(is_fish=True)
    db = poker_utils.load_fish_data()

    col1, col2 = st.columns([1, 3])
    
    with col1:
        render_hud(st.session_state.fish_stats, st.session_state.fish_combo, st.session_state.fish_shields)
        
        st.markdown('<div class="spot-info-panel"><h5 style="color:#0dcaf0; margin-top:0; font-weight:900; text-transform:uppercase;">Fish Radar</h5>', unsafe_allow_html=True)
        all_vpips = list(db.keys())
        vpip_sel = st.multiselect("VPIP", all_vpips, key="fish_filter_vpip")
        
        all_pos, all_boards = set(), set()
        vpips_to_scan = vpip_sel if vpip_sel else all_vpips
        for vp in vpips_to_scan:
            for tex, pos_data in db.get(vp, {}).items():
                all_boards.add(tex)
                for pos in pos_data.keys(): all_pos.add(pos)
                    
        pos_sel = st.multiselect("Position", list(all_pos), key="fish_filter_pos")
        board_sel = st.multiselect("Board", list(all_boards), key="fish_filter_board")
        
        all_lines, all_runouts = set(), set()
        boards_to_scan = board_sel if board_sel else list(all_boards)
        for vp in vpips_to_scan:
            for tex in boards_to_scan:
                pos_data = db.get(vp, {}).get(tex, {})
                for pos, line_data in pos_data.items():
                    if pos_sel and pos not in pos_sel: continue
                    for line, runout_data in line_data.items():
                        all_lines.add(line)
                        for runout in runout_data.keys(): all_runouts.add(runout)
                            
        line_sel = st.multiselect("Action Line", list(all_lines), key="fish_filter_line")
        runout_sel = st.multiselect("Runout", list(all_runouts), key="fish_filter_runout")
        
        if st.button("Apply & Next Spot", use_container_width=True):
            generate_spot()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        if sets.get("show_mastery", True) and st.session_state.fish_current_spot:
            spot = st.session_state.fish_current_spot
            spot_key = f"{spot['vpip']}_{spot['texture']}"
            m_info = poker_utils.get_spot_mastery_info(st.session_state.fish_stats.get("spot_mastery", {}).get(spot_key, {}))
            
            st.markdown(f"""
            <div class="spot-info-panel" style="display:flex; align-items:center; gap:15px;">
                <div style="width:50px; height:50px;">{m_info['svg']}</div>
                <div style="flex-grow:1;">
                    <div style="color:#aaa; font-size:10px; font-weight:bold; letter-spacing:1px;">SPOT MASTERY</div>
                    <div style="color:{m_info['color']}; font-size:14px; font-weight:900; text-transform:uppercase;">{m_info['name']}</div>
                    <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-top:5px;">
                        <div style="color:#888; font-size:10px;">Hands: {m_info['total']} / {m_info['next']}</div>
                        <div style="color:{m_info['color']}; font-size:12px; font-weight:bold;">{m_info['prog_pct']}%</div>
                    </div>
                    <div style="background:#222; height:4px; border-radius:2px; margin-top:4px; overflow:hidden;">
                        <div style="background:{m_info['color']}; height:100%; width:{m_info['prog_pct']}%; box-shadow:0 0 5px {m_info['color']};"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with st.expander("📝 Action History (Fish)"):
            try:
                if "fish_history_buffer" in st.session_state and st.session_state.fish_history_buffer:
                    df = pd.DataFrame(st.session_state.fish_history_buffer, columns=["Date", "Fish_Type", "Position", "Line", "Texture", "Runout", "Hand", "Action", "Correct", "Result", "XP"])
                    st.dataframe(df.tail(10)[["Hand", "Action", "Correct", "Result"]], use_container_width=True)
                else:
                    st.info("No history in this session yet.")
            except: pass

    with col2:
        top_c1, top_c2 = st.columns([9, 1])
        with top_c2:
            if st.button("⚙️", key="btn_fish_settings", help="Settings"):
                st.session_state.fish_settings_modal_open = True
                st.rerun()

        st.markdown('<div class="table-container">', unsafe_allow_html=True)
        
        if not st.session_state.fish_current_spot:
            if not generate_spot():
                st.info("Выстави фильтры или добавь базы в fish_data.")
                st.markdown('</div>', unsafe_allow_html=True)
                return

        spot = st.session_state.fish_current_spot
        setup = spot["data"].get("setup", {})
        
        fb_class, fb_text = "", ""
        if st.session_state.fish_feedback:
            fb = st.session_state.fish_feedback
            if fb["correct"]: fb_class = "correct-flash"
            else:
                fb_class = "wrong-flash"
                sh_txt = " (Shield Used)" if fb["shield"] else ""
                fb_text = f"<div style='text-align:center; color:#dc3545; font-size:16px; font-weight:900; margin-top:15px; text-transform:uppercase;'>❌ Missed. Expected: {fb['expected']}{sh_txt}</div>"

        b_cards = setup.get("board_cards", [])
        board_html = "".join([get_card_html(c) for c in b_cards])
        hero_h1 = st.session_state.fish_hand[:2] if len(st.session_state.fish_hand)>=2 else ""
        hero_h2 = st.session_state.fish_hand[2:] if len(st.session_state.fish_hand)>=4 else ""
        hero_html = get_card_html(hero_h1) + get_card_html(hero_h2)

        v_act, v_size, onenote = setup.get("villain_action", ""), setup.get("villain_sizing_bb", ""), setup.get("onenote_url", "")
        v_badge = f'<div class="villain-badge">{v_act}</div>' if v_act else ""
        chip_html = f'<div class="chip-stack"><div class="chip">{v_size}</div><div style="color:#fff; font-size:10px; font-weight:bold; margin-top:4px;">BB</div></div>' if v_size else ""
        hook_html = f'<a href="{onenote}" target="_blank" class="info-hook">i</a>' if onenote else ""

        st.markdown(f"""
        <div class="poker-table {fb_class}">
            <div class="felt-line"></div>
            {hook_html}
            {chip_html}
            <div style="text-align:center; color:rgba(255,255,255,0.4); font-size:12px; font-weight:bold; letter-spacing:2px; margin-bottom:10px; text-transform:uppercase; z-index:5;">
                {spot['vpip']} | {spot['pos']} | {spot['line']}
            </div>
            
            <div style="display:flex; flex-direction:column; align-items:center; z-index:5;">
                <div class="pot-display">POT: {setup.get("pot_size", 0)} BB</div>
                {v_badge}
            </div>
            
            <div class="community-cards">{board_html}</div>
            
            <div class="hero-section">
                <div style="margin-right:15px; color:#aaa; font-size:11px; font-weight:bold; text-align:right; text-transform:uppercase;">
                    HERO<br><span style="color:#fff; font-size:14px;">{setup.get("hero_pos", "UKN")}</span>
                </div>
                {hero_html}
            </div>
        </div>
        {fb_text}
        """, unsafe_allow_html=True)

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        
        actions = spot["data"].get("actions", [])
        if actions:
            cols = st.columns(len(actions))
            for idx, act in enumerate(actions):
                with cols[idx]:
                    st.markdown('<div class="action-btn">', unsafe_allow_html=True)
                    if st.button(act, key=f"btn_{act}_{spot['runout']}_{st.session_state.fish_stats.get('total_hands',0)}", use_container_width=True):
                        handle_action(act)
                        if not sets.get("show_matrix", False) or st.session_state.fish_feedback["correct"]:
                            generate_spot()
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                    
        if st.session_state.fish_feedback and not st.session_state.fish_feedback["correct"] and sets.get("show_matrix", False):
            st.markdown("<hr style='border-color:#333; margin:20px 0;'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color:#fff; text-align:center; margin-bottom:15px;'>Expected Ranges</h4>", unsafe_allow_html=True)
            
            r_data = st.session_state.fish_feedback["ranges"]
            target_hand_basic = st.session_state.fish_hand[:2]
            grid_html = poker_utils.render_range_matrix(r_data, target_hand=target_hand_basic)
            st.markdown(grid_html, unsafe_allow_html=True)
            
            if st.button("Next Spot", type="primary", use_container_width=True):
                generate_spot()
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
