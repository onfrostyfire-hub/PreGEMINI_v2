import streamlit as st
import json
import pandas as pd
import os
import random
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials

SPOTS_DIR = 'spots_data'
RANKS = 'AKQJT98765432'

# --- GOOGLE SHEETS CORE ---
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
SPREADSHEET_ID = '15ouWJYZuQET1-sy7k5Wrn1fAzNUX6ssk5K8SOM9uYOc'

@st.cache_resource
def get_gspread_client():
    try:
        creds_dict = json.loads(st.secrets["GOOGLE_JSON"])
        creds_dict["private_key"] = creds_dict["private_key"].replace('\\n', '\n')
        credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        return gspread.authorize(credentials)
    except Exception as e:
        st.error(f"Google Sheets Connection Error: {e}")
        st.stop()

@st.cache_resource
def get_worksheets():
    client = get_gspread_client()
    sh = client.open_by_key(SPREADSHEET_ID)
    return {
        "Settings": sh.worksheet("Settings"),
        "History": sh.worksheet("History")
    }

@st.cache_data(ttl=60)
def load_history():
    try:
        vals = get_worksheets()["History"].get_all_values()
        if not vals or len(vals) < 2: return pd.DataFrame(columns=["Date", "Spot", "Hand", "Result", "CorrectAction", "UserAction"])
        
        headers = vals[0]
        if "UserAction" not in headers:
            headers.append("UserAction")
            for r in vals[1:]: r.append("UNKNOWN")
            
        df = pd.DataFrame(vals[1:], columns=headers)
        return df
    except: return pd.DataFrame(columns=["Date", "Spot", "Hand", "Result", "CorrectAction", "UserAction"])

def rebuild_srs_from_history():
    df = load_history()
    weights = {}
    
    if df.empty or "Spot" not in df.columns or "Result" not in df.columns:
        return weights

    df = df.sort_values("Date")
    
    for _, row in df.iterrows():
        spot = str(row.get("Spot", ""))
        hand = str(row.get("Hand", ""))
        try:
            result = int(float(row.get("Result", 0)))
        except:
            continue
            
        key = f"{spot}_{hand}"
        w = weights.get(key, 100)
        
        if result == 1:
            w = int(w * 0.8)
        else:
            w = int((w * 1.5) + (20 if w < 50 else 50))
            
        weights[key] = max(10, min(w, 2000))
        
    return weights

def init_cloud_data():
    if "app_initialized" not in st.session_state:
        sheets = get_worksheets()
        
        try:
            st.session_state["srs_data"] = rebuild_srs_from_history()
        except Exception as e:
            st.error(f"🚨 Ошибка динамической сборки SRS: {e}")
            st.session_state["srs_data"] = {}
        
        try:
            set_val = sheets["Settings"].acell('A1').value
            if set_val:
                st.session_state["user_settings"] = json.loads(set_val)
            else:
                st.session_state["user_settings"] = {}
        except Exception as e:
            st.error(f"🚨 Ошибка чтения Settings: {e}")
            st.stop()
            
        st.session_state["history_buffer"] = []
        st.session_state["unsaved_count"] = 0
        st.session_state["settings_changed"] = False
        st.session_state["app_initialized"] = True

# --- GAMIFICATION CORE ---
def load_user_stats():
    init_cloud_data()
    sets = st.session_state.get("user_settings", {})
    stats = sets.get("stats", {})
    if "xp" not in stats: stats["xp"] = 0
    if "streak" not in stats: stats["streak"] = 0
    if "last_date" not in stats: stats["last_date"] = ""
    if "max_combo" not in stats: stats["max_combo"] = 0
    if "total_hands" not in stats: stats["total_hands"] = 0
    if "dailies" not in stats: stats["dailies"] = {"date": "", "quests": []}
    if "spot_mastery" not in stats: stats["spot_mastery"] = {}
    return stats

def save_user_stats(stats):
    sets = st.session_state.get("user_settings", {})
    sets["stats"] = stats
    save_user_settings(sets)

def get_rank_info(xp):
    tiers = [
        (0, "🐟 Fish"), (2000, "🪨 Nit"), (7500, "🚶 Reg"),
        (20000, "⚔️ Grinder"), (50000, "🦈 Shark"), (100000, "🎩 High Roller"),
        (250000, "👑 Boss"), (500000, "🤖 GTO Machine"), (1000000, "👽 Poker God")
    ]
    current_rank = tiers[0][1]
    next_xp = tiers[1][0]
    for i, (req_xp, name) in enumerate(tiers):
        if xp >= req_xp:
            current_rank = name
            next_xp = tiers[i+1][0] if i+1 < len(tiers) else "MAX"
    return current_rank, next_xp

def generate_dailies():
    return [
        {"id": "play", "desc": "Play 100 hands", "target": 100, "progress": 0, "done": False, "xp": 500},
        {"id": "correct", "desc": "50 correct answers", "target": 50, "progress": 0, "done": False, "xp": 500},
        {"id": "combo", "desc": "Combo x15", "target": 15, "progress": 0, "done": False, "xp": 1000}
    ]

def get_spot_mastery_info(spot_data_dict):
    if not isinstance(spot_data_dict, dict):
        spot_data_dict = {}

    total = spot_data_dict.get("t", 0)
    hist = spot_data_dict.get("h", "")
    last_date_str = spot_data_dict.get("d", "")

    days_missed = 0
    if last_date_str:
        try:
            last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
            days_missed = (datetime.now().date() - last_date).days
        except: pass

    is_rusty = days_missed > 7
    penalty = 1 if days_missed > 14 else 0

    wr_100 = (hist.count('1') / len(hist) * 100) if len(hist) > 0 else 0.0

    rank = 0
    if total >= 5000 and wr_100 >= 95: rank = 5
    elif total >= 3000 and wr_100 >= 92: rank = 4
    elif total >= 1500 and wr_100 >= 88: rank = 3
    elif total >= 500 and wr_100 >= 82: rank = 2
    elif total >= 100 and wr_100 >= 75: rank = 1

    rank = max(0, rank - penalty)

    svg_basic = '''<svg viewBox="0 0 100 100" style="width:100%;height:100%;opacity:0.35;pointer-events:none;filter:drop-shadow(0 0 10px #28a745);">
      <circle cx="50" cy="50" r="35" fill="#111" stroke="#28a745" stroke-width="4"/>
      <circle cx="50" cy="50" r="25" fill="none" stroke="#28a745" stroke-width="2" stroke-dasharray="5 5"/>
      <circle cx="50" cy="50" r="10" fill="#28a745" opacity="0.7"/>
      <path d="M50 5 V20 M50 95 V80 M5 50 H20 M95 50 H80" stroke="#28a745" stroke-width="4" stroke-linecap="round"/>
    </svg>'''

    svg_solid = '''<svg viewBox="0 0 100 100" style="width:100%;height:100%;opacity:0.45;pointer-events:none;filter:drop-shadow(0 0 12px #0dcaf0);">
      <path d="M20 20 L50 5 L80 20 L80 60 C80 80 50 95 50 95 C50 95 20 80 20 60 Z" fill="#111" stroke="#0dcaf0" stroke-width="4"/>
      <path d="M50 5 V95 C80 80 80 60 80 20 L50 5 Z" fill="#0dcaf0" opacity="0.3"/>
      <polygon points="50,30 70,50 50,70 30,50" fill="none" stroke="#0dcaf0" stroke-width="4"/>
      <polygon points="50,40 60,50 50,60 40,50" fill="#0dcaf0" opacity="0.9"/>
    </svg>'''

    svg_unexp = '''<svg viewBox="0 0 100 100" style="width:100%;height:100%;opacity:0.55;pointer-events:none;filter:drop-shadow(0 0 15px #6f42c1);">
      <g stroke="#6f42c1" stroke-width="4" stroke-linecap="round">
        <line x1="10" y1="90" x2="90" y2="10"/><line x1="10" y1="10" x2="90" y2="90"/>
      </g>
      <path d="M20 25 L50 10 L80 25 L80 55 C80 80 50 95 50 95 C50 95 20 80 20 55 Z" fill="#111" stroke="#6f42c1" stroke-width="4"/>
      <path d="M50 10 V95 C80 80 80 55 80 25 L50 10 Z" fill="#6f42c1" opacity="0.4"/>
    </svg>'''

    svg_elite = '''<svg viewBox="0 0 100 100" style="width:100%;height:100%;opacity:0.75;pointer-events:none;filter:drop-shadow(0 0 18px #dc3545);">
      <path d="M 45 95 C 5 90, -5 40, 25 15" fill="none" stroke="#dc3545" stroke-width="4" stroke-dasharray="6 4" stroke-linecap="round"/>
      <path d="M 55 95 C 95 90, 105 40, 75 15" fill="none" stroke="#dc3545" stroke-width="4" stroke-dasharray="6 4" stroke-linecap="round"/>
      <g stroke="#dc3545" stroke-width="4" stroke-linecap="round">
        <line x1="25" y1="75" x2="75" y2="25"/><line x1="25" y1="25" x2="75" y2="75"/>
      </g>
      <path d="M30 40 L50 25 L70 40 L70 65 C70 80 50 90 50 90 C50 90 30 80 30 65 Z" fill="#111" stroke="#dc3545" stroke-width="3"/>
      <path d="M35 35 L42 15 L50 25 L58 15 L65 35 Z" fill="#dc3545" stroke="#111" stroke-width="2"/>
    </svg>'''

    svg_solver = '''<svg viewBox="0 0 100 100" style="width:100%;height:100%;opacity:0.95;pointer-events:none;filter:drop-shadow(0 0 20px #ffc107) drop-shadow(0 0 5px #ffffff);">
      <path d="M 45 98 C 0 95, -10 35, 25 5" fill="none" stroke="#ffc107" stroke-width="5" stroke-dasharray="8 6" stroke-linecap="round"/>
      <path d="M 55 98 C 100 95, 110 35, 75 5" fill="none" stroke="#ffc107" stroke-width="5" stroke-dasharray="8 6" stroke-linecap="round"/>
      <polygon points="50,15 80,32 80,68 50,85 20,68 20,32" fill="#111" stroke="#ffc107" stroke-width="3"/>
      <polygon points="50,15 80,32 80,68 50,85 20,68 20,32" fill="#ffc107" opacity="0.2"/>
      <line x1="50" y1="15" x2="50" y2="85" stroke="#ffc107" stroke-width="2"/>
      <line x1="20" y1="32" x2="80" y2="68" stroke="#ffc107" stroke-width="2"/>
      <line x1="20" y1="68" x2="80" y2="32" stroke="#ffc107" stroke-width="2"/>
      <circle cx="50" cy="50" r="16" fill="#ffc107"/>
      <circle cx="50" cy="50" r="6" fill="#111"/>
    </svg>'''

    ranks_info = [
        {"n": "Sandbox", "i": "⚪", "c": "#6c757d", "nt": 100, "req_wr": 75, "svg": ""},
        {"n": "Basic", "i": "🟢", "c": "#28a745", "nt": 500, "req_wr": 82, "svg": svg_basic},
        {"n": "Solid", "i": "🔵", "c": "#0dcaf0", "nt": 1500, "req_wr": 88, "svg": svg_solid},
        {"n": "Unexploitable", "i": "🟣", "c": "#6f42c1", "nt": 3000, "req_wr": 92, "svg": svg_unexp},
        {"n": "Elite", "i": "🔴", "c": "#dc3545", "nt": 5000, "req_wr": 95, "svg": svg_elite},
        {"n": "Solver", "i": "☢️", "c": "#ffc107", "nt": 5000, "req_wr": 100, "svg": svg_solver},
    ]
    
    info = ranks_info[rank]

    if rank == 5:
        prog_pct = 100
    else:
        target_hands = info["nt"]
        target_wr = info["req_wr"]
        
        if target_hands > 0:
            prog_pct = int((total / target_hands) * 100)
        else:
            prog_pct = 100
            
        if prog_pct >= 100:
            if wr_100 < target_wr:
                prog_pct = 99
            else:
                prog_pct = 100
                
    if prog_pct > 100: prog_pct = 100

    name = info["n"]
    if is_rusty:
        name += " (Rusty)"

    return {
        "rank": rank, "name": name, "icon": info["i"], "color": info["c"],
        "is_rusty": is_rusty, "prog_pct": prog_pct, "total": total, "next": info["nt"], "svg": info["svg"]
    }

def process_gamification(is_correct, combo, session_total_hands, spot_key=None, shield_used=False):
    stats = load_user_stats()
    now_date = datetime.now().date()
    now_date_str = now_date.strftime("%Y-%m-%d")
    alerts = []
    
    m_rank = 0
    if spot_key:
        s_data = stats.get("spot_mastery", {}).get(spot_key, {})
        m_info = get_spot_mastery_info(s_data)
        m_rank = m_info["rank"]

    multiplier = 1.0
    if combo >= 1000: mult = 25.0
    elif combo >= 500: mult = 10.0
    elif combo >= 250: multiplier = 5.0
    elif combo >= 100: multiplier = 4.0
    elif combo >= 50: multiplier = 3.0
    elif combo >= 25: multiplier = 2.0
    elif combo >= 10: multiplier = 1.5
    
    st.session_state["xp_multiplier"] = multiplier

    if stats["last_date"]:
        try:
            last_date = datetime.strptime(stats["last_date"], "%Y-%m-%d").date()
            delta = (now_date - last_date).days
            if delta == 1: stats["streak"] += 1
            elif delta > 1: stats["streak"] = 1
        except: stats["streak"] = 1
    else: stats["streak"] = 1
    stats["last_date"] = now_date_str
    
    stats["total_hands"] += 1
    
    reward_val = 0
    if shield_used:
        reward_val = 0
    else:
        if is_correct:
            reward_val = int(10 * multiplier)
        else:
            if m_rank == 0:
                reward_val = 0
            elif m_rank == 1:
                reward_val = -int(10 * multiplier)
            else:
                reward_val = -int(20 * multiplier)
            
    stats["xp"] += reward_val
    if stats["xp"] < 0: stats["xp"] = 0
    
    if combo > stats.get("max_combo", 0): stats["max_combo"] = combo
    
    if stats["dailies"].get("date") != now_date_str:
        stats["dailies"] = {"date": now_date_str, "quests": generate_dailies()}
        
    for q in stats["dailies"]["quests"]:
        if not q["done"]:
            if q["id"] == "play": q["progress"] += 1
            elif q["id"] == "correct" and is_correct: q["progress"] += 1
            elif q["id"] == "combo" and combo > q["progress"]: q["progress"] = combo
            
            if q["progress"] >= q["target"]:
                q["progress"] = q["target"]
                q["done"] = True
                stats["xp"] += q["xp"]
                alerts.append(f"🎯 Daily: {q['desc']} (+${q['xp']})")

    if spot_key:
        if "spot_mastery" not in stats: stats["spot_mastery"] = {}
        s_data = stats["spot_mastery"].get(spot_key)
        if not isinstance(s_data, dict):
            s_data = {"h": "", "t": 0, "d": ""}
        
        s_data["t"] += 1
        s_data["d"] = now_date_str
        s_data["h"] += "1" if is_correct else "0"
        
        if len(s_data["h"]) > 100: s_data["h"] = s_data["h"][-100:]
        stats["spot_mastery"][spot_key] = s_data

    save_user_stats(stats)
    return alerts, reward_val

# --- ADAPTIVE SRS ALGORITHM ---
def load_srs_data():
    init_cloud_data()
    return st.session_state.get("srs_data", {})

def update_srs_auto(spot_id, hand, is_correct):
    init_cloud_data()
    data = st.session_state["srs_data"]
    key = f"{spot_id}_{hand}"
    w = data.get(key, 100)
    
    if is_correct:
        w = int(w * 0.8)
    else:
        w = int((w * 1.5) + (20 if w < 50 else 50))
            
    data[key] = max(10, min(w, 2000))
    st.session_state["unsaved_count"] += 1
    check_auto_sync()

def load_user_settings(is_postflop=False, **kwargs):
    init_cloud_data()
    settings = st.session_state.get("user_settings", {})
    if is_postflop:
        if "postflop_settings" not in settings:
            settings["postflop_settings"] = {}
        return settings["postflop_settings"]
    return settings

def save_user_settings(settings, is_postflop=False, **kwargs):
    init_cloud_data()
    if is_postflop:
        curr = st.session_state.get("user_settings", {})
        curr["postflop_settings"] = settings
        st.session_state["user_settings"] = curr
    else:
        st.session_state["user_settings"] = settings
    st.session_state["settings_changed"] = True
    st.session_state["unsaved_count"] += 1
    check_auto_sync()

def save_to_history(record):
    init_cloud_data()
    row = [
        str(record.get("Date", "")), 
        str(record.get("Spot", "")), 
        str(record.get("Hand", "")), 
        str(record.get("Result", "")), 
        str(record.get("CorrectAction", "")),
        str(record.get("UserAction", ""))
    ]
    st.session_state["history_buffer"].append(row)
    st.session_state["unsaved_count"] += 1
    check_auto_sync()

def check_auto_sync():
    if st.session_state.get("unsaved_count", 0) >= 6: 
        force_sync()

# --- ИЗОЛИРОВАННОЕ СОХРАНЕНИЕ ---
def force_sync():
    if st.session_state.get("unsaved_count", 0) == 0: return
    sheets = get_worksheets()
    sync_success = True

    if "history_buffer" in st.session_state and st.session_state["history_buffer"]:
        try:
            sheets["History"].append_rows(st.session_state["history_buffer"])
            st.session_state["history_buffer"] = []
            load_history.clear()
        except Exception as e:
            sync_success = False
            print(f"History Sync error: {e}")

    if st.session_state.get("settings_changed"):
        try:
            sheets["Settings"].update_acell('A1', json.dumps(st.session_state["user_settings"]))
            st.session_state["settings_changed"] = False
        except Exception as e:
            sync_success = False
            print(f"Settings Sync error: {e}")
            
    st.session_state["unsaved_count"] = 0
    if sync_success:
        st.toast("☁️ История сохранена", icon="✅")

def delete_history(days=None):
    try:
        sheets = get_worksheets()
        headers = ["Date", "Spot", "Hand", "Result", "CorrectAction", "UserAction"]
        if days is None:
            sheets["History"].clear()
            sheets["History"].append_row(headers)
        else:
            df = load_history()
            if df.empty: return
            df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
            now = datetime.now()
            cutoff = now - timedelta(days=days)
            df_new = df[df["Date"] >= cutoff] 
            sheets["History"].clear()
            rows = [headers] + df_new.astype(str).values.tolist()
            sheets["History"].update(values=rows, range_name="A1")
        load_history.clear()
        if "history_buffer" in st.session_state: st.session_state["history_buffer"] = []
    except Exception as e: st.error(f"Error clearing history: {e}")

@st.cache_data(ttl=0)
def load_ranges():
    db = {}
    if not os.path.exists(SPOTS_DIR): return db
    for file in os.listdir(SPOTS_DIR):
        if file.endswith('.json'):
            with open(os.path.join(SPOTS_DIR, file), 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    src = data.get("source", "Unknown")
                    sc = data.get("scenario", "Unknown")
                    if src not in db: db[src] = {}
                    if sc not in db[src]: db[src][sc] = {}
                    db[src][sc].update(data.get("spots", {}))
                except Exception as e: st.error(f"Read error {file}: {e}")
    return db

@st.cache_data(ttl=0)
def load_postflop_ranges():
    db = {}
    pf_dir = 'postflop_data' if os.path.exists('postflop_data') else SPOTS_DIR
    if not os.path.exists(pf_dir): return db
    for file in os.listdir(pf_dir):
        if file.endswith('.json'):
            with open(os.path.join(pf_dir, file), 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    src = data.get("source", "Unknown")
                    sc = data.get("scenario", "Unknown")
                    if src not in db: db[src] = {}
                    if sc not in db[src]: db[src][sc] = {}
                    db[src][sc].update(data.get("spots", {}))
                except Exception as e: st.error(f"Read error {file}: {e}")
    return db

ALL_HANDS = []
for i, r1 in enumerate(RANKS):
    for j, r2 in enumerate(RANKS):
        if i < j: ALL_HANDS.append(r1 + r2 + 's'); ALL_HANDS.append(r1 + r2 + 'o')
        elif i == j: ALL_HANDS.append(r1 + r2)

def get_weight(hand, range_str):
    if not range_str or not isinstance(range_str, str): return 0.0
    cleaned = range_str.replace('\n', ' ').replace('\r', '')
    items = [x.strip() for x in cleaned.split(',')]
    for item in items:
        if ':' in item:
            h_part, w_part = item.split(':')
            try:
                weight = float(w_part)
                if weight <= 1.0: weight *= 100
            except: weight = 100.0
        else:
            h_part = item
            weight = 100.0
        if h_part == hand: return weight
        if len(h_part) == 2 and h_part[0] != h_part[1] and hand.startswith(h_part): return weight
    return 0.0

def parse_range_to_list(range_str):
    if not range_str or not isinstance(range_str, str) or "22+" in range_str or range_str == "ALL": return ALL_HANDS.copy()
    hand_list = []
    cleaned = range_str.replace('\n', ' ').replace('\r', '')
    items = [x.strip() for x in cleaned.split(',')]
    for item in items:
        if not item: continue
        h = item.split(':')[0]
        if h in ALL_HANDS: hand_list.append(h)
        elif len(h) == 2:
            if h[0] == h[1]: hand_list.append(h)
            else: hand_list.extend([h+'s', h+'o'])
    if not hand_list: return ALL_HANDS.copy()
    return list(set(hand_list))

def render_range_matrix(spot_data, target_hand=None):
    ranges = spot_data.get("ranges", spot_data)
    r_call = ranges.get("call", ranges.get("Call", ""))
    r_raise = ranges.get("4bet", ranges.get("3bet", ranges.get("Raise", "")))
    r_full = ranges.get("full", ranges.get("Full", ""))
    
    grid_html = '<div style="display:grid;grid-template-columns:repeat(13,1fr);gap:1px;background:#111;padding:1px;border:1px solid #444;">'
    for r1 in RANKS:
        for r2 in RANKS:
            if RANKS.index(r1) == RANKS.index(r2): h = r1 + r2
            elif RANKS.index(r1) < RANKS.index(r2): h = r1 + r2 + 's'
            else: h = r2 + r1 + 'o'
            
            w_c = get_weight(h, r_call)
            w_4 = get_weight(h, r_raise)
            w_f = get_weight(h, r_full)
            
            raise_w = w_4 if w_4 > 0 else w_f
            call_w = w_c
            
            total_w = raise_w + call_w
            if total_w > 100:
                raise_w = (raise_w / total_w) * 100
                call_w = (call_w / total_w) * 100
            
            style = "aspect-ratio:1;display:flex;justify-content:center;align-items:center;font-size:7px;cursor:default;color:#fff;"
            
            if raise_w == 0 and call_w == 0:
                bg = "#2c3034"
                style += "color:#495057;"
            elif raise_w >= 100: bg = "#d63384"
            elif call_w >= 100: bg = "#28a745"
            else:
                stops = []
                curr_pct = 0.0
                if raise_w > 0:
                    stops.append(f"#d63384 {curr_pct}%")
                    curr_pct += raise_w
                    stops.append(f"#d63384 {curr_pct}%")
                if call_w > 0:
                    stops.append(f"#28a745 {curr_pct}%")
                    curr_pct += call_w
                    stops.append(f"#28a745 {curr_pct}%")
                if curr_pct < 100:
                    stops.append(f"#2c3034 {curr_pct}%")
                    stops.append(f"#2c3034 100%")
                bg = f"linear-gradient(to right, {', '.join(stops)})"
            
            style += f"background:{bg};"
            if target_hand and h == target_hand: style += "border:1.5px solid #ffc107;z-index:10;box-shadow: 0 0 4px #ffc107;"
            grid_html += f'<div style="{style}" title="{h} | Raise: {raise_w:.0f}%, Call: {call_w:.0f}%">{h}</div>'
    grid_html += '</div>'

    stats = spot_data.get("stats", {})
    if stats:
        stats_html = '<div style="display:flex; gap:8px; justify-content:center; margin-top:10px; flex-wrap:wrap; font-size:12px; font-weight:bold; font-family:sans-serif;">'
        for k, v in stats.items():
            kl = k.lower()
            if "raise" in kl or "3bet" in kl or "4bet" in kl or "pfr" in kl: color = "#d63384" 
            elif "call" in kl: color = "#28a745" 
            elif "fold" in kl: color = "#6c757d" 
            else: color = "#adb5bd" 
            stats_html += f'<div style="background:#222; border:1px solid {color}; color:{color}; padding:4px 10px; border-radius:6px; box-shadow: 0 2px 4px rgba(0,0,0,0.4);">{k} {v}</div>'
        stats_html += '</div>'
        grid_html += stats_html
    return grid_html

def _get_fuzzy_weight(srs_data, src, sc, sp, h):
    exact_keys = [
        f"{sp}_{h}",
        f"{sp}_{h}".replace(" ", "_"),
        f"{src}_{sc}_{sp}_{h}".replace(" ", "_"),
        f"{sc}_{sp}_{h}".replace(" ", "_")
    ]
    for k in exact_keys:
        if k in srs_data:
            return srs_data[k]
            
    for k, v in srs_data.items():
        if sp in k and h in k:
            return v
            
    return 100

def render_srs_matrix(spot_data, src, sc, sp, srs_data, target_hand=None):
    grid_html = '<div style="display:grid;grid-template-columns:repeat(13,1fr);gap:1px;background:#111;padding:1px;border:1px solid #444;">'
    for r1 in RANKS:
        for r2 in RANKS:
            if RANKS.index(r1) == RANKS.index(r2): h = r1 + r2
            elif RANKS.index(r1) < RANKS.index(r2): h = r1 + r2 + 's'
            else: h = r2 + r1 + 'o'
            
            w = _get_fuzzy_weight(srs_data, src, sc, sp, h)
            
            if w <= 10: bg = "#0f5132" 
            elif w <= 50: bg = "#198754" 
            elif w <= 150: bg = "#2c3034" 
            elif w <= 500: bg = "#854000" 
            elif w <= 1000: bg = "#fd7e14" 
            else: bg = "#dc3545" 
            
            style = f"aspect-ratio:1;display:flex;flex-direction:column;justify-content:center;align-items:center;cursor:default;color:#fff;background:{bg};"
            if target_hand and h == target_hand: style += "border:1.5px solid #ffc107;z-index:10;box-shadow: 0 0 4px #ffc107;"
            
            grid_html += f'<div style="{style}" title="{h} | Weight: {w}">'
            grid_html += f'<div style="font-size:9px; font-weight:bold; line-height:1;">{h}</div>'
            grid_html += f'<div style="font-size:7px; color:#ffc107; margin-top:2px; font-weight:bold;">{w}</div>'
            grid_html += '</div>'
            
    grid_html += '</div>'
    
    grid_html += '''
    <div style="display:flex; justify-content:center; gap:10px; margin-top:10px; font-size:10px; color:#aaa; font-family:sans-serif; text-transform:uppercase; font-weight:bold;">
        <div style="display:flex; align-items:center; gap:4px;"><div style="width:10px;height:10px;background:#0f5132;border-radius:2px;"></div>Mastered</div>
        <div style="display:flex; align-items:center; gap:4px;"><div style="width:10px;height:10px;background:#2c3034;border-radius:2px;"></div>Default</div>
        <div style="display:flex; align-items:center; gap:4px;"><div style="width:10px;height:10px;background:#dc3545;border-radius:2px;"></div>Leak</div>
    </div>
    '''
    return grid_html
