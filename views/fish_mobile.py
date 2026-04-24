import streamlit as st
import random
import time
from datetime import datetime
import poker_utils

def get_exact_hand_weight(hand, range_str):
    if not range_str or not isinstance(range_str, str): return 0.0
    cleaned = range_str.replace('\n', ' ').replace('\r', '')
    items = [x.strip() for x in cleaned.split(',')]
    for item in items:
        if ':' in item:
            h_part, w_part = item.split(':')
            try:
                weight = float(w_part)
            except:
                weight = 100.0
        else:
            h_part = item
            weight = 100.0
        if h_part == hand: return weight
    return 0.0

def get_card_html(card_str):
    if len(card_str) < 2: return ""
    rank, suit = card_str[0], card_str[1].lower()
    if suit == 's': color, sym = "#6c757d", "♠"
    elif suit == 'h': color, sym = "#dc3545", "♥"
    elif suit == 'd': color, sym = "#0dcaf0", "♦"
    elif suit == 'c': color, sym = "#28a745", "♣"
    else: color, sym = "#fff", suit
    
    return f'''
    <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); 
                border-radius: 6px; width: 38px; height: 55px; display: flex; flex-direction: column; 
                justify-content: center; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.3); margin: 0 1px;">
        <div style="color: {color}; font-size: 16px; font-weight: 900; line-height: 1;">{rank}</div>
        <div style="color: {color}; font-size: 18px; line-height: 1;">{sym}</div>
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
        st.session_state.fish_initialized = True

def generate_spot():
    db = poker_utils.load_fish_data()
    if not db:
        st.warning("База fish_data пуста. Загрузи JSON-файлы.")
        return False
        
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
                        
    if not pool:
        st.warning("Нет спотов под эти фильтры.")
        return False
        
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
            
    alerts, xp_gained = poker_utils.process_gamification(
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
        "XP": xp_gained
    }
    poker_utils.save_to_history(record, is_fish=True)
    
    st.session_state.fish_feedback = {
        "correct": is_correct,
        "shield": shield_used,
        "expected": correct_action
    }
    st.session_state.fish_stats = poker_utils.load_user_stats(is_fish=True)

def show():
    init_fish_state()
    st.markdown("""
    <style>
        .fish-table { background: radial-gradient(circle at center, #1a2a3a 0%, #0d151c 100%); border-radius: 12px; padding: 15px 10px; box-shadow: inset 0 0 30px rgba(0,0,0,0.8), 0 5px 15px rgba(0,0,0,0.5); border: 1px solid #2c3e50; position: relative; margin-top: 5px; }
        .info-hook { position: absolute; top: 10px; left: 10px; width: 20px; height: 20px; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.3); border-radius: 50%; color: #aaa; display: flex; justify-content: center; align-items: center; font-size: 12px; font-weight: bold; font-family: serif; text-decoration: none; transition: 0.2s; z-index: 10; }
        .info-hook:active { background: #0dcaf0; color: #000; box-shadow: 0 0 10px #0dcaf0; }
        .chip { background: linear-gradient(135deg, #f1c40f 0%, #f39c12 100%); border: 1px dashed #d35400; border-radius: 50%; width: 30px; height: 30px; display: flex; justify-content: center; align-items: center; font-size: 9px; font-weight: 900; color: #000; box-shadow: 2px 2px 5px rgba(0,0,0,0.5); position: absolute; top: 15px; right: 15px; z-index: 10; }
        .villain-badge { background: #dc3545; color: white; padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: 900; text-transform: uppercase; box-shadow: 0 2px 5px rgba(0,0,0,0.5); display: inline-block; margin-top: 5px; border: 1px solid #ff4d4d; }
        
        .fish-mobile-actions { display: flex; gap: 5px; width: 100%; margin-top: 10px; }
        .fish-mobile-actions > div { flex: 1; }
        .fish-mobile-actions button { width: 100% !important; background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.2) !important; color: #fff !important; padding: 10px 2px !important; border-radius: 8px !important; font-size: 12px !important; font-weight: bold !important; height: 45px !important; }
        .fish-mobile-actions button:active { background: rgba(255,255,255,0.1) !important; border-color: #ffc107 !important; color: #ffc107 !important; }
        
        div[data-testid="stHorizontalBlock"]:has(> div > .fish-btn-hack) { display: flex !important; flex-wrap: nowrap !important; gap: 4px !important; width: 100% !important; }
        div[data-testid="stHorizontalBlock"]:has(> div > .fish-btn-hack) > div { min-width: 0 !important; flex: 1 1 0% !important; width: auto !important; padding: 0 !important; }
        .fish-btn-hack button { width: 100% !important; background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.2) !important; color: #fff !important; padding: 8px 2px !important; border-radius: 6px !important; font-size: 11px !important; font-weight: 900 !important; height: 45px !important; text-transform: uppercase; }
        
        .correct-flash { animation: flashGreen 0.5s ease-out; }
        .wrong-flash { animation: flashRed 0.5s ease-out; }
        @keyframes flashGreen { 0% { box-shadow: inset 0 0 60px rgba(40,167,69,0.8); } 100% { box-shadow: inset 0 0 30px rgba(0,0,0,0.8); } }
        @keyframes flashRed { 0% { box-shadow: inset 0 0 60px rgba(220,53,69,0.8); } 100% { box-shadow: inset 0 0 30px rgba(0,0,0,0.8); } }
    </style>
    """, unsafe_allow_html=True)

    db = poker_utils.load_fish_data()
    
    with st.expander("⚙️ RADAR FILTERS", expanded=(not st.session_state.fish_current_spot)):
        all_vpips = list(db.keys())
        vpip_sel = st.multiselect("VPIP", all_vpips, key="fish_filter_vpip")
        
        all_pos = set()
        all_boards = set()
        vpips_to_scan = vpip_sel if vpip_sel else all_vpips
        for vp in vpips_to_scan:
            for tex, pos_data in db.get(vp, {}).items():
                all_boards.add(tex)
                for pos in pos_data.keys():
                    all_pos.add(pos)
                    
        pos_sel = st.multiselect("Position", list(all_pos), key="fish_filter_pos")
        board_sel = st.multiselect("Board", list(all_boards), key="fish_filter_board")
        
        all_lines = set()
        all_runouts = set()
        boards_to_scan = board_sel if board_sel else list(all_boards)
        for vp in vpips_to_scan:
            for tex in boards_to_scan:
                pos_data = db.get(vp, {}).get(tex, {})
                for pos, line_data in pos_data.items():
                    if pos_sel and pos not in pos_sel: continue
                    for line, runout_data in line_data.items():
                        all_lines.add(line)
                        for runout in runout_data.keys():
                            all_runouts.add(runout)
                            
        line_sel = st.multiselect("Action Line", list(all_lines), key="fish_filter_line")
        runout_sel = st.multiselect("Runout", list(all_runouts), key="fish_filter_runout")
        
        if st.button("Apply & Next Spot", use_container_width=True):
            generate_spot()
            st.rerun()

    if not st.session_state.fish_current_spot:
        generate_spot()
        if not st.session_state.fish_current_spot:
            st.info("Выстави фильтры или добавь базы в fish_data.")
            return

    spot = st.session_state.fish_current_spot
    setup = spot["data"].get("setup", {})
    
    c_xp, c_rnk = st.session_state.fish_stats.get("xp",0), st.session_state.fish_combo
    c_sh = st.session_state.fish_shields
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; background:#111; padding:5px 10px; border-radius:6px; border:1px solid #333; margin-bottom:5px;">
        <div style="text-align:center;"><span style="color:#aaa; font-size:9px;">COMBO</span><br><span style="color:#ffc107; font-size:14px; font-weight:900;">x{c_rnk}</span></div>
        <div style="text-align:center;"><span style="color:#aaa; font-size:9px;">SHIELDS</span><br><span style="color:#0dcaf0; font-size:14px; font-weight:900;">{c_sh}</span></div>
        <div style="text-align:center;"><span style="color:#aaa; font-size:9px;">XP</span><br><span style="color:#28a745; font-size:14px; font-weight:900;">{c_xp}</span></div>
    </div>
    """, unsafe_allow_html=True)

    fb_class = ""
    fb_text = ""
    if st.session_state.fish_feedback:
        fb = st.session_state.fish_feedback
        if fb["correct"]: fb_class = "correct-flash"
        else:
            fb_class = "wrong-flash"
            sh_txt = " (Shield)" if fb["shield"] else ""
            fb_text = f"<div style='text-align:center; color:#dc3545; font-size:12px; font-weight:bold; margin-top:5px;'>Miss: {fb['expected']}{sh_txt}</div>"

    b_cards = setup.get("board_cards", [])
    board_html = "".join([get_card_html(c) for c in b_cards])
    
    hero_h1 = st.session_state.fish_hand[:2] if len(st.session_state.fish_hand)>=2 else ""
    hero_h2 = st.session_state.fish_hand[2:] if len(st.session_state.fish_hand)>=4 else ""
    hero_html = get_card_html(hero_h1) + get_card_html(hero_h2)

    v_act = setup.get("villain_action", "")
    v_badge = f'<div class="villain-badge">{v_act}</div>' if v_act else ""
    v_size = setup.get("villain_sizing_bb")
    chip_html = f'<div class="chip">{v_size}</div>' if v_size else ""
    
    onenote = setup.get("onenote_url")
    hook_html = f'<a href="{onenote}" target="_blank" class="info-hook">i</a>' if onenote else ""

    st.markdown(f"""
    <div class="fish-table {fb_class}">
        {hook_html}
        {chip_html}
        <div style="text-align:center; color:#adb5bd; font-size:10px; font-weight:bold; letter-spacing:0.5px; margin-bottom:10px;">
            {spot['vpip']} | {spot['pos']} | {spot['line']}
        </div>
        
        <div style="display:flex; justify-content:center; align-items:center; min-height:60px; margin-bottom:10px;">
            {board_html}
        </div>
        
        <div style="text-align:center; margin-bottom:15px;">
            <div style="color:#6c757d; font-size:11px; font-weight:bold; margin-bottom:2px;">POT: {setup.get("pot_size", 0)} BB</div>
            {v_badge}
        </div>
        
        <div style="display:flex; justify-content:center; align-items:center;">
            <div style="margin-right:10px; color:#aaa; font-size:9px; font-weight:bold; text-align:right;">HERO<br>{setup.get("hero_pos", "UKN")}</div>
            {hero_html}
        </div>
    </div>
    {fb_text}
    """, unsafe_allow_html=True)

    actions = spot["data"].get("actions", [])
    if actions:
        cols = st.columns(len(actions))
        for idx, act in enumerate(actions):
            with cols[idx]:
                st.markdown('<div class="fish-btn-hack">', unsafe_allow_html=True)
                if st.button(act, key=f"btn_{act}_{spot['runout']}_{st.session_state.fish_stats['total_hands']}"):
                    handle_action(act)
                    generate_spot()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
