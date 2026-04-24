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
            try: weight = float(w_part)
            except: weight = 100.0
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
    return f'<div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; width: 45px; height: 65px; display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.3); margin: 0 2px;"><div style="color: {color}; font-size: 20px; font-weight: 900; line-height: 1;">{rank}</div><div style="color: {color}; font-size: 22px; line-height: 1;">{sym}</div></div>'

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
                        pool.append({"vpip": vp, "pos": pos, "line": line, "texture": tex, "runout": runout, "data": spot_info})
    if not pool: return False
    chosen = random.choice(pool)
    st.session_state.fish_current_spot = chosen
    hands = [h.strip() for h in chosen["data"].get("training", "").split(",") if h.strip()]
    if not hands: return False
    st.session_state.fish_hand = random.choice(hands)
    st.session_state.fish_feedback = None
    return True

def handle_action(user_action):
    spot = st.session_state.fish_current_spot
    hand = st.session_state.fish_hand
    actions = spot["data"]["actions"]
    ranges = spot["data"]["ranges"]
    weights = [(act, get_exact_hand_weight(hand, ranges.get(act, ""))) for act in actions]
    total_w = sum(w for _, w in weights)
    
    if total_w == 0: correct_action = actions[0] if actions else "UNKNOWN"
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
        if st.session_state.fish_combo in [100, 250, 500, 1000]: st.session_state.fish_shields += 1
    else:
        if st.session_state.fish_shields > 0:
            st.session_state.fish_shields -= 1
            shield_used = True
        else: st.session_state.fish_combo = 0
            
    poker_utils.process_gamification(is_correct, st.session_state.fish_combo, st.session_state.fish_stats.get("total_hands", 0), spot_key=f"{spot['vpip']}_{spot['texture']}", shield_used=shield_used, is_fish=True)
    
    record = {"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Fish_Type": spot["vpip"], "Position": spot["pos"], "Action_Line": spot["line"], "Texture": spot["texture"], "Runout": spot["runout"], "Hand": hand, "Action_Taken": user_action, "Correct_Action": correct_action, "Result": 1 if is_correct else 0, "XP": 0}
    poker_utils.save_to_history(record, is_fish=True)
    st.session_state.fish_feedback = {"correct": is_correct, "shield": shield_used, "expected": correct_action}
    st.session_state.fish_stats = poker_utils.load_user_stats(is_fish=True)

def show():
    init_fish_state()
    st.markdown("""
    <style>
        .fish-table { background: radial-gradient(circle at center, #1a2a3a 0%, #0d151c 100%); border-radius: 15px; padding: 20px; box-shadow: inset 0 0 50px rgba(0,0,0,0.8), 0 10px 20px rgba(0,0,0,0.5); border: 2px solid #2c3e50; position: relative; }
        .info-hook { position: absolute; top: 15px; left: 15px; width: 24px; height: 24px; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.3); border-radius: 50%; color: #aaa; display: flex; justify-content: center; align-items: center; font-weight: bold; font-family: serif; text-decoration: none; transition: 0.2s; }
        .info-hook:hover { background: #0dcaf0; color: #000; box-shadow: 0 0 10px #0dcaf0; }
        .chip { background: linear-gradient(135deg, #f1c40f 0%, #f39c12 100%); border: 2px dashed #d35400; border-radius: 50%; width: 36px; height: 36px; display: flex; justify-content: center; align-items: center; font-size: 10px; font-weight: 900; color: #000; box-shadow: 2px 2px 5px rgba(0,0,0,0.5); position: absolute; top: 20px; right: 20px; }
        .villain-badge { background: #dc3545; color: white; padding: 4px 12px; border-radius: 4px; font-size: 11px; font-weight: 900; text-transform: uppercase; box-shadow: 0 2px 5px rgba(0,0,0,0.5); display: inline-block; margin-top: 10px; border: 1px solid #ff4d4d; }
        .fish-btn button { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.2) !important; color: #fff !important; padding: 15px !important; border-radius: 10px !important; font-weight: bold !important; transition: 0.2s !important; height: 60px !important; text-transform: uppercase; }
        .fish-btn button:hover { background: rgba(255,255,255,0.1) !important; border-color: #ffc107 !important; color: #ffc107 !important; box-shadow: 0 0 10px rgba(255,193,7,0.3) !important; }
        .correct-flash { animation: flashGreen 0.5s ease-out; }
        .wrong-flash { animation: flashRed 0.5s ease-out; }
        @keyframes flashGreen { 0% { box-shadow: inset 0 0 100px rgba(40,167,69,0.8); } 100% { box-shadow: inset 0 0 50px rgba(0,0,0,0.8); } }
        @keyframes flashRed { 0% { box-shadow: inset 0 0 100px rgba(220,53,69,0.8); } 100% { box-shadow: inset 0 0 50px rgba(0,0,0,0.8); } }
    </style>
    """, unsafe_allow_html=True)

    db = poker_utils.load_fish_data()
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown('<div style="background:#111; padding:15px; border-radius:10px; border:1px solid #333;">', unsafe_allow_html=True)
        st.markdown("<h5 style='color:#0dcaf0; margin-bottom:15px; font-weight:900;'>FISH RADAR</h5>", unsafe_allow_html=True)
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

        if st.session_state.fish_current_spot:
            spot = st.session_state.fish_current_spot
            spot_key = f"{spot['vpip']}_{spot['texture']}"
            m_info = poker_utils.get_spot_mastery_info(st.session_state.fish_stats.get("spot_mastery", {}).get(spot_key, {}))
            st.markdown(f'<div style="background:#111; padding:15px; border-radius:10px; border:1px solid #333; display:flex; align-items:center; gap:15px; margin-top:15px;"><div style="width:50px; height:50px;">{m_info["svg"]}</div><div style="flex-grow:1;"><div style="color:#aaa; font-size:10px; font-weight:bold; letter-spacing:1px;">SPOT MASTERY</div><div style="color:{m_info["color"]}; font-size:14px; font-weight:900; text-transform:uppercase;">{m_info["name"]}</div><div style="display:flex; justify-content:space-between; align-items:flex-end; margin-top:5px;"><div style="color:#888; font-size:10px;">Hands: {m_info["total"]} / {m_info["next"]}</div><div style="color:{m_info["color"]}; font-size:12px; font-weight:bold;">{m_info["prog_pct"]}%</div></div><div style="background:#222; height:4px; border-radius:2px; margin-top:4px; overflow:hidden;"><div style="background:{m_info["color"]}; height:100%; width:{m_info["prog_pct"]}%; box-shadow:0 0 5px {m_info["color"]};"></div></div></div></div>', unsafe_allow_html=True)

    with col2:
        if not st.session_state.fish_current_spot:
            if not generate_spot():
                st.info("Выстави фильтры или добавь базы в fish_data.")
                return

        spot = st.session_state.fish_current_spot
        setup = spot["data"].get("setup", {})
        
        c_xp, c_combo, c_sh = st.session_state.fish_stats.get("xp",0), st.session_state.fish_combo, st.session_state.fish_shields
        rank_name, next_xp = poker_utils.get_rank_info(c_xp)
        xp_pct = 100 if next_xp == "MAX" else min(100, int((c_xp / next_xp) * 100))
        sh_html = "".join(['<div style="width:14px; height:14px; border-radius:50%; background:#0dcaf0; box-shadow:0 0 8px #0dcaf0; border:2px solid #fff; margin:0 2px;"></div>' for _ in range(c_sh)])
        
        st.markdown(f'<div style="background:#111; padding:15px; border-radius:10px; border:1px solid #333; margin-bottom:15px;"><div style="display:flex; justify-content:space-between; align-items:center;"><div><div style="color:#aaa; font-size:10px; font-weight:bold; letter-spacing:1px;">RANK</div><div style="color:#ffc107; font-size:18px; font-weight:900;">{rank_name}</div></div><div style="text-align:center;"><div style="color:#aaa; font-size:10px; font-weight:bold; letter-spacing:1px;">COMBO</div><div style="color:#fff; font-size:18px; font-weight:900;">x{c_combo}</div></div><div style="text-align:center;"><div style="color:#aaa; font-size:10px; font-weight:bold; letter-spacing:1px;">SHIELDS</div><div style="display:flex; justify-content:center; margin-top:4px; min-height:14px;">{sh_html}</div></div><div style="text-align:right;"><div style="color:#aaa; font-size:10px; font-weight:bold; letter-spacing:1px;">XP</div><div style="color:#28a745; font-size:18px; font-weight:900;">{c_xp}</div></div></div><div style="background:#222; height:6px; border-radius:3px; margin-top:12px; overflow:hidden;"><div style="background:linear-gradient(90deg, #ffc107, #ff5722); height:100%; width:{xp_pct}%; box-shadow:0 0 10px #ff5722;"></div></div></div>', unsafe_allow_html=True)

        fb_class, fb_text = "", ""
        if st.session_state.fish_feedback:
            fb = st.session_state.fish_feedback
            if fb["correct"]: fb_class = "correct-flash"
            else:
                fb_class = "wrong-flash"
                sh_txt = " (Shield)" if fb["shield"] else ""
                fb_text = f"<div style='text-align:center; color:#dc3545; font-weight:bold; margin-top:10px;'>Miss. Expected: {fb['expected']}{sh_txt}</div>"

        b_cards = setup.get("board_cards", [])
        board_html = "".join([get_card_html(c) for c in b_cards])
        hero_h1 = st.session_state.fish_hand[:2] if len(st.session_state.fish_hand)>=2 else ""
        hero_h2 = st.session_state.fish_hand[2:] if len(st.session_state.fish_hand)>=4 else ""
        hero_html = get_card_html(hero_h1) + get_card_html(hero_h2)

        v_act, v_size, onenote = setup.get("villain_action", ""), setup.get("villain_sizing_bb"), setup.get("onenote_url")
        v_badge = f'<div class="villain-badge">{v_act}</div>' if v_act else ""
        chip_html = f'<div class="chip">{v_size}</div>' if v_size else ""
        hook_html = f'<a href="{onenote}" target="_blank" class="info-hook">i</a>' if onenote else ""

        st.markdown(f'<div class="fish-table {fb_class}">{hook_html}{chip_html}<div style="text-align:center; color:#adb5bd; font-size:12px; font-weight:bold; letter-spacing:1px; margin-bottom:15px;">{spot["vpip"]} | {spot["pos"]} | {spot["line"]}</div><div style="display:flex; justify-content:center; align-items:center; min-height:80px; margin-bottom:20px;">{board_html}</div><div style="text-align:center; margin-bottom:20px;"><div style="color:#6c757d; font-size:12px; font-weight:bold; margin-bottom:5px;">POT: {setup.get("pot_size", 0)} BB</div>{v_badge}</div><div style="display:flex; justify-content:center; align-items:center; margin-top:20px;"><div style="margin-right:15px; color:#aaa; font-size:10px; font-weight:bold;">HERO<br>{setup.get("hero_pos", "UKN")}</div>{hero_html}</div></div>{fb_text}', unsafe_allow_html=True)

        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        actions = spot["data"].get("actions", [])
        if actions:
            cols = st.columns(len(actions))
            for idx, act in enumerate(actions):
                with cols[idx]:
                    st.markdown('<div class="fish-btn">', unsafe_allow_html=True)
                    if st.button(act, key=f"btn_{act}_{spot['runout']}_{st.session_state.fish_stats.get('total_hands',0)}", use_container_width=True):
                        handle_action(act)
                        generate_spot()
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
