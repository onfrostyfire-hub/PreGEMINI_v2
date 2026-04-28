import streamlit as st
import random
import time
import os
import json
from datetime import datetime
import pandas as pd
import poker_utils as utils

# --- ЖЕЛЕЗНЫЕ ОБЁРТКИ ДЛЯ FISH (Только Google Sheets) ---
def safe_load_stats():
    settings = utils.load_user_settings(is_fish=True)
    stats = settings.get("stats", {})
    if "xp" not in stats: stats["xp"] = 0
    if "combo" not in stats: stats["combo"] = 0
    if "shields" not in stats: stats["shields"] = 0
    if "spot_mastery" not in stats: stats["spot_mastery"] = {}
    if "streak" not in stats: stats["streak"] = 0
    if "total_hands" not in stats: stats["total_hands"] = 0
    if "max_combo" not in stats: stats["max_combo"] = 0
    return stats

def safe_save_stats(data):
    settings = utils.load_user_settings(is_fish=True)
    settings["stats"] = data
    utils.save_user_settings(settings, is_fish=True)

def safe_save_history(data):
    utils.save_to_history(data, is_fish=True)
# --------------------------------------------------------

def map_suit(s):
    mapping = {'h': '♥\ufe0e', 'd': '♦\ufe0e', 'c': '♣\ufe0e', 's': '♠\ufe0e'}
    return mapping.get(s.lower(), '♠\ufe0e')

def get_suit_color_class(s):
    if '♥' in s: return "suit-red"
    if '♦' in s: return "suit-blue"
    if '♣' in s: return "suit-green"
    return "suit-black"

def fish_parse_range(r_str):
    if not r_str: return []
    return [x.split(':')[0].strip() for x in r_str.split(',')]

def fish_get_weight(hand, r_str):
    if not r_str: return 0.0
    items = [x.strip() for x in r_str.split(',')]
    for item in items:
        if not item: continue
        parts = item.split(':')
        h = parts[0].strip()
        w = float(parts[1])*100 if len(parts)>1 and float(parts[1])<=1.0 else (float(parts[1]) if len(parts)>1 else 100.0)
        if h == hand: return w
    return 0.0

def generate_desktop_theme(bg_rad1, bg_rad2, shadow1, shadow2, shadow3, seat_rad, seat_border, seat_act_border, seat_act_shadow, anim_name, pulse_shadow1, pulse_shadow2, text_color, badge_bg, bar_fill, card_bg, card_border, rng_bg):
    return f"""<style>
    .desktop-game-area {{ 
        background: radial-gradient(ellipse 50% 38% at 50% 42%, {bg_rad1} 0%, transparent 70%), radial-gradient(ellipse 88% 78% at 50% 50%, {bg_rad2}) !important; 
        border-color: {shadow1} !important; 
    }}
    .seat-active-desk .ava-desk, .seat-active-desk .plate-desk {{ border-color: {seat_act_border} !important; }}
    .seat-active-desk .ava-desk {{ box-shadow: 0 -4px 10px {pulse_shadow1}, inset 0 2px 4px rgba(255,255,255,0.1) !important; animation: {anim_name}_ava 2.6s ease-in-out infinite !important; }}
    .seat-active-desk .plate-desk {{ box-shadow: 0 4px 10px {pulse_shadow1} !important; animation: {anim_name}_plate 2.6s ease-in-out infinite !important; }}
    
    @keyframes {anim_name}_ava {{ 0%,100% {{ box-shadow: 0 -4px 8px {pulse_shadow1}, inset 0 2px 4px rgba(255,255,255,0.1); }} 50% {{ box-shadow: 0 -4px 20px {pulse_shadow2}, inset 0 2px 4px rgba(255,255,255,0.1); }} }}
    @keyframes {anim_name}_plate {{ 0%,100% {{ box-shadow: 0 4px 8px {pulse_shadow1}; }} 50% {{ box-shadow: 0 4px 20px {pulse_shadow2}; }} }}
    
    .card-desk {{ background: {card_bg} !important; border: 1px solid {card_border} !important; }}
    .rng-badge-desk {{ color: {text_color} !important; background: {rng_bg} !important; border: 1.5px solid {seat_border} !important; }}
    .hero-plate-desk {{ border-color: {seat_act_border} !important; }}
    .hero-plate-desk .pos-desk {{ color: {seat_act_border} !important; }}
    
    /* ИКОНКА ONENOTE */
    .info-hook {{ position: absolute; top: 405px; left: 475px; width: 26px; height: 26px; background: rgba(0,0,0,0.6); border: 1.5px solid rgba(255,255,255,0.4); border-radius: 50%; color: #fff; display: flex; justify-content: center; align-items: center; font-weight: bold; font-family: serif; text-decoration: none; transition: 0.2s; z-index: 100; font-size: 14px; text-shadow: none; }}
    .info-hook:hover {{ background: #0dcaf0; color: #000; border-color: #0dcaf0; box-shadow: 0 0 12px #0dcaf0; }}
    </style>"""

THEMES = {
    0: {"icon": "⚪", "name": "Sandbox", "css": generate_desktop_theme("rgba(50,55,60,0.5)", "#202428 0%, #15181a 55%, #0a0b0d 100%", "#1f2329", "#16181b", "#0b0d0f", "#1f2226 0%, #111316 60%, #08090a 100%", "rgba(140,150,160,0.18)", "rgba(160,170,180,0.55)", "rgba(160,170,180,0.48)", "r0-pulse", "rgba(160,170,180,0.38)", "rgba(160,170,180,0.7)", "rgba(150,160,170,0.9)", "rgba(150,160,170,0.09)", "linear-gradient(90deg, #8b959e, #5b636a)", "#f8faff", "rgba(255,255,255,0.85)", "rgba(150,160,170,0.09)")},
    1: {"icon": "🌱", "name": "Basic", "css": generate_desktop_theme("rgba(30,55,38,0.5)", "#1a2e20 0%, #111e16 55%, #090e0b 100%", "#182b1d", "#182219", "#0b100d", "#1a2d21 0%, #0e1a12 60%, #080d0a 100%", "rgba(120,160,130,0.18)", "rgba(120,180,140,0.55)", "rgba(120,180,140,0.45)", "r1-pulse", "rgba(120,180,140,0.38)", "rgba(120,180,140,0.7)", "rgba(130,190,150,0.9)", "rgba(120,180,140,0.08)", "linear-gradient(90deg, #6ab880, #4a9060)", "#f8faff", "rgba(255,255,255,0.85)", "rgba(120,180,140,0.08)")},
    2: {"icon": "💎", "name": "Solid", "css": generate_desktop_theme("rgba(10,50,80,0.6)", "#0b3040 0%, #071e2e 58%, #030e18 100%", "#0c2738", "#0f2234", "#060e17", "#162840 0%, #0c1a28 60%, #060e18 100%", "rgba(60,130,200,0.22)", "rgba(60,160,255,0.78)", "rgba(60,160,255,0.42)", "r2-pulse", "rgba(60,160,255,0.34)", "rgba(60,160,255,0.62)", "rgba(80,170,255,0.9)", "rgba(60,130,200,0.09)", "linear-gradient(90deg, #3ab0ff, #1480d8)", "#f8faff", "rgba(255,255,255,0.85)", "rgba(60,130,200,0.09)")},
    3: {"icon": "🔥", "name": "Unexploitable", "css": generate_desktop_theme("rgba(90,18,28,0.65)", "#3a0d14 0%, #240810 58%, #0f0408 100%", "#2b0d12", "#2e1014", "#12060a", "#3a1c10 0%, #221008 60%, #0f0804 100%", "rgba(180,110,40,0.28)", "rgba(210,150,50,0.88)", "rgba(210,150,50,0.48)", "r3-pulse", "rgba(210,150,50,0.4)", "rgba(220,165,60,0.68)", "rgba(220,165,65,0.9)", "rgba(180,110,40,0.09)", "linear-gradient(90deg, #d49030, #a86018)", "linear-gradient(145deg, #f5f0e8 0%, #ede5d4 100%)", "rgba(210,175,110,0.7)", "rgba(180,110,40,0.09)")},
    4: {"icon": "⚡", "name": "Elite", "css": generate_desktop_theme("rgba(55,20,90,0.6)", "#1e0d30 0%, #130820 58%, #07030f 100%", "#1b0b2e", "#1e1028", "#0d0614", "#2a1840 0%, #180e28 60%, #0a0812 100%", "rgba(160,130,220,0.28)", "rgba(190,160,255,0.88)", "rgba(170,130,255,0.52)", "r4-pulse", "rgba(170,130,255,0.42)", "rgba(190,150,255,0.7)", "rgba(190,165,255,0.9)", "rgba(140,110,220,0.09)", "linear-gradient(90deg, #a070ff, #7040d8)", "linear-gradient(150deg, #2a2a32 0%, #1e1e26 100%)", "rgba(200,190,230,0.3)", "rgba(140,110,220,0.09)")},
    5: {"icon": "☢️", "name": "Solver", "css": generate_desktop_theme("rgba(60,50,10,0.5)", "#141410 0%, #0c0c09 55%, #050504 100%", "#1a1a12", "#1c1c16", "#0a0a08", "#1c1a10 0%, #111008 60%, #080806 100%", "rgba(190,158,50,0.3)", "rgba(220,188,70,0.95)", "rgba(220,188,70,0.58)", "r5-pulse", "rgba(220,188,70,0.46)", "rgba(240,205,80,0.78)", "rgba(220,188,70,0.9)", "rgba(190,158,50,0.1)", "linear-gradient(90deg, #d4a820, #a07810)", "linear-gradient(150deg, #1a1a18 0%, #111110 100%)", "rgba(210,180,70,0.38)", "rgba(190,158,50,0.1)")}
}

def show():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@500;700;900&display=swap');

        .pf-pot-badge-desk { position: absolute; top: 22%; left: 50%; transform: translateX(-50%); z-index: 15; }
        .pf-street-pot-desk { position: absolute; top: 60%; left: 50%; transform: translateX(-50%); z-index: 18; display: flex; flex-direction: row; align-items: center; justify-content: center; gap: 8px; pointer-events: none; }
        .pf-board-desk { position: absolute; top: 45%; left: 50%; transform: translate(-50%, -50%); z-index: 15; }
        
        .desktop-game-area { 
            position: relative; width: 100%; max-width: 850px; height: 380px; 
            margin: 20px auto 90px auto; 
            border: 16px solid #1a1c20; 
            border-radius: 200px; 
            box-shadow: 0 10px 40px rgba(0,0,0,0.8), inset 0 3px 15px rgba(0,0,0,0.6); 
            transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out; 
        }
        
        .rng-hint-wrap-desk { text-align: center; color: #6c757d; font-size: 13px; font-family: 'Roboto', sans-serif; font-weight: 500; letter-spacing: 0.5px; margin-bottom: 15px; margin-top: 15px; }
        div[data-testid="stHorizontalBlock"] { gap: 15px !important; margin-top: 10px; max-width: 850px; margin-left: auto; margin-right: auto; }

        .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; max-width: 1200px !important; }
        div[data-testid="column"] { width: 100% !important; min-width: 0 !important; max-width: 100% !important; margin-bottom: 0 !important; }
        div[data-testid="stButton"] { width: 100% !important; }
        div[data-testid="stButton"] button { width: 100% !important; height: 60px !important; padding: 0 !important; border-radius: 14px !important; border: none !important; transition: transform 0.1s !important; background: #343a40 !important; color: #fff !important; box-shadow: 0 5px 0 #1d2124 !important; }
        div[data-testid="stButton"] button:active { transform: translateY(5px) !important; box-shadow: 0 0 0 transparent !important; }
        div[data-testid="stButton"] button p { font-family: 'Roboto', sans-serif !important; font-size: 18px !important; font-weight: 900 !important; margin: 0 !important; letter-spacing: 1px !important; text-transform: uppercase !important; }
        div.element-container:has(#fish-runouts-all-d-marker) + div.element-container div[data-testid="stButton"] { width: 54px !important; margin-left: auto !important; }
        div.element-container:has(#fish-runouts-all-d-marker) + div.element-container div[data-testid="stButton"] button { width: 54px !important; height: 26px !important; min-height: 26px !important; padding: 0 !important; border-radius: 8px !important; background: #242932 !important; border: 1px solid rgba(255,255,255,0.18) !important; box-shadow: none !important; }
        div.element-container:has(#fish-runouts-all-d-marker) + div.element-container div[data-testid="stButton"] button:active { transform: translateY(1px) !important; }
        div.element-container:has(#fish-runouts-all-d-marker) + div.element-container div[data-testid="stButton"] button p { font-size: 11px !important; letter-spacing: 0.06em !important; color: rgba(255,255,255,0.88) !important; }

        .cn-desk-header { max-width: 850px; margin: 0 auto 10px auto; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; -webkit-font-smoothing: antialiased; border-radius: 16px; overflow: hidden; position: relative; background: linear-gradient(165deg, rgba(18,22,28,0.92) 0%, rgba(8,10,14,0.96) 100%); border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 1px 0 rgba(255,255,255,0.06) inset, 0 8px 32px rgba(0,0,0,0.55), 0 0 0 1px rgba(0,0,0,0.4); backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px); }
        .cn-desk-header::before { content: ''; position: absolute; inset: 0; border-radius: 16px; pointer-events: none; background: linear-gradient(125deg, rgba(255,255,255,0.07) 0%, transparent 42%, transparent 58%, rgba(255,255,255,0.03) 100%); z-index: 0; }
        .cn-desk-wr-track { height: 4px; width: 100%; background: rgba(0,0,0,0.45); position: relative; z-index: 1; }
        .cn-desk-wr-fill { height: 100%; transition: width 0.35s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 0 0 12px currentColor; }
        .cn-desk-inner { position: relative; z-index: 1; padding: 12px 20px 14px; }
        .cn-desk-row1 { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 8px; }
        .cn-desk-rank { font-size: 14px; font-weight: 800; letter-spacing: 0.04em; text-transform: uppercase; color: rgba(255,214,120,0.95); text-shadow: 0 0 20px rgba(255,200,80,0.25); line-height: 1.15; }
        .cn-desk-xp-meta { font-size: 12px; font-weight: 700; font-variant-numeric: tabular-nums; color: rgba(180,190,205,0.85); white-space: nowrap; letter-spacing: 0.02em; }
        .cn-desk-xp-bar-wrap { flex: 1; min-width: 0; margin-top: 4px; }
        .cn-desk-xp-bar-bg { height: 6px; border-radius: 6px; background: rgba(0,0,0,0.5); box-shadow: inset 0 1px 3px rgba(0,0,0,0.6); overflow: hidden; }
        .cn-desk-xp-bar-fill { height: 100%; border-radius: 6px; background: linear-gradient(90deg, #1a7a4a, #2ee88a); box-shadow: 0 0 10px rgba(46,232,138,0.45); transition: width 0.35s cubic-bezier(0.4, 0, 0.2, 1); }
        .cn-desk-row2 { display: flex; align-items: stretch; justify-content: space-between; gap: 10px; margin-top: 4px; }
        .cn-desk-stat { flex: 1; min-width: 0; }
        .cn-desk-stat-label { font-size: 10px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: rgba(140,150,165,0.75); margin-bottom: 2px; }
        .cn-desk-stat-val { font-size: 16px; font-weight: 800; font-variant-numeric: tabular-nums; letter-spacing: -0.02em; line-height: 1.1; }
        .cn-desk-stat-val.light { color: rgba(245,248,252,0.98); }
        .cn-desk-combo-wrap { flex: 1.15; display: flex; justify-content: center; align-items: center; min-width: 0; }
        .cn-desk-combo-pill { display: inline-flex; align-items: center; justify-content: center; gap: 6px; padding: 4px 16px 4px 12px; border-radius: 999px; background: linear-gradient(145deg, rgba(255,255,255,0.09) 0%, rgba(255,255,255,0.02) 100%); border: 1px solid rgba(255,255,255,0.12); box-shadow: 0 1px 0 rgba(255,255,255,0.08) inset, 0 4px 16px rgba(0,0,0,0.35); }
        .cn-desk-combo-fire { font-size: 18px; font-weight: 900; color: #fff; text-shadow: 0 0 18px rgba(255,120,40,0.55); letter-spacing: -0.03em; }
        .cn-desk-shield { font-size: 14px; margin-left: 4px; font-weight: 800; color: rgba(120,230,255,0.95); filter: drop-shadow(0 0 6px rgba(0,200,255,0.55)); align-items: center; gap: 3px; }

        .rage-bar-container-desk { width: 100%; max-width: 850px; margin: 0 auto 15px auto; height: 32px; border-radius: 999px; position: relative; display: flex; align-items: stretch; padding: 4px; background: linear-gradient(180deg, rgba(12,14,20,0.95) 0%, rgba(6,8,12,0.98) 100%); border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 0 0 1px rgba(0,0,0,0.5), 0 4px 20px rgba(0,0,0,0.55), inset 0 2px 6px rgba(0,0,0,0.65), inset 0 -1px 0 rgba(255,255,255,0.05); overflow: hidden; }
        .rage-bar-container-desk::before { content: ''; position: absolute; inset: 0; border-radius: inherit; pointer-events: none; background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.04) 50%, transparent 100%); z-index: 3; }
        .rage-bar-fill-desk { height: 100%; border-radius: 999px; transition: width 0.35s cubic-bezier(0.4, 0, 0.2, 1); position: relative; overflow: hidden; min-width: 0; box-shadow: inset 0 2px 8px rgba(255,255,255,0.35), inset 0 -3px 8px rgba(0,0,0,0.45), 0 0 20px rgba(255,255,255,0.12); }
        .rage-bar-fill-desk::before, .rage-bar-fill-desk::after { content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background-image: radial-gradient(circle, rgba(255,255,255,0.85) 1px, transparent 2px), radial-gradient(circle, rgba(255,255,255,0.45) 2px, transparent 3px), radial-gradient(circle, rgba(255,255,255,0.35) 1px, transparent 2px); z-index: 1; pointer-events: none; }
        .rage-bar-fill-desk::before { background-size: 18px 22px, 32px 36px, 14px 18px; animation: bubbleRise1 1.15s infinite linear; opacity: 0.85; }
        .rage-bar-fill-desk::after { background-size: 22px 28px, 40px 46px, 20px 24px; animation: bubbleRise2 1.65s infinite linear; opacity: 0.45; }
        .rage-labels-desk { position: absolute; left: 0; right: 0; top: 50%; transform: translateY(-50%); display: flex; justify-content: space-between; align-items: center; padding: 0 16px; pointer-events: none; z-index: 4; font-family: 'Inter', system-ui, sans-serif; font-weight: 800; font-size: 13px; font-variant-numeric: tabular-nums; letter-spacing: 0.02em; color: rgba(255,255,255,0.98); text-shadow: 0 1px 2px rgba(0,0,0,0.95), 0 0 12px rgba(0,0,0,0.8), 0 0 1px rgba(0,0,0,1); }
        .rage-pulse-desk { animation: ragePulseNeon 0.45s ease-in-out infinite alternate; }
        .rage-flash-desk { animation: rageTubeFlash 0.65s ease-out; }
        @keyframes bubbleRise1 { 0% { background-position: 0px 22px, 0px 36px, 0px 18px; } 50% { background-position: 5px 11px, -5px 18px, 3px 9px; } 100% { background-position: 0px 0px, 0px 0px, 0px 0px; } }
        @keyframes bubbleRise2 { 0% { background-position: 0px 28px, 0px 46px, 0px 24px; } 50% { background-position: -6px 14px, 6px 22px, -4px 12px; } 100% { background-position: 0px 0px, 0px 0px, 0px 0px; } }
        @keyframes ragePulseNeon { 0% { filter: brightness(1) saturate(1); box-shadow: inset 0 2px 8px rgba(255,255,255,0.3), 0 0 8px rgba(255,60,80,0.35); } 100% { filter: brightness(1.15) saturate(1.2); box-shadow: inset 0 2px 12px rgba(255,255,255,0.5), 0 0 22px rgba(255,80,100,0.65), 0 0 40px rgba(255,40,60,0.25); } }
        @keyframes rageTubeFlash { 0% { box-shadow: 0 0 0 1px rgba(255,255,255,0.9), 0 0 40px rgba(255,255,255,0.8), inset 0 0 30px rgba(255,255,255,0.5); border-color: rgba(255,255,255,0.65); } 100% { box-shadow: 0 4px 20px rgba(0,0,0,0.55), inset 0 2px 6px rgba(0,0,0,0.65); border-color: rgba(255,255,255,0.1); } }

        .desktop-game-area.table-glow-correct { border-color: #198754 !important; box-shadow: 0 0 35px rgba(25,135,84,0.6), inset 0 0 25px rgba(25,135,84,0.4) !important; }
        .desktop-game-area.table-glow-incorrect { border-color: #dc3545 !important; box-shadow: 0 0 35px rgba(220,53,69,0.6), inset 0 0 25px rgba(220,53,69,0.4) !important; }

        .seat-desk { position: absolute !important; z-index: 20 !important; display: flex !important; flex-direction: column !important; align-items: center !important; gap: 0 !important; width: 95px !important; height: 65px !important; background: transparent !important; border: none !important; box-shadow: none !important; }
        .ava-desk { width: 85px !important; height: 40px !important; background: linear-gradient(180deg, #2a2d32 0%, #1c1e22 100%) !important; border-radius: 85px 85px 0 0 !important; border: 2px solid #3a3d42 !important; border-bottom: none !important; box-shadow: inset 0 2px 4px rgba(255,255,255,0.05) !important; transition: all 0.3s ease !important; }
        .plate-desk { width: 95px !important; height: 28px !important; background: #141518 !important; border-radius: 0 0 8px 8px !important; border: 2px solid #3a3d42 !important; display: flex !important; justify-content: space-between !important; align-items: center !important; padding: 0 8px !important; box-sizing: border-box !important; font-size: 14px !important; box-shadow: 0 4px 8px rgba(0,0,0,0.5) !important; transition: all 0.3s ease !important; }
        .pos-desk { font-weight: 900 !important; color: #fff !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important; }
        .stack-desk { font-weight: 700 !important; color: #fff !important; font-size: 13px !important; }

        .seat-folded-desk { opacity: 0.85 !important; filter: grayscale(50%) !important; }
        .seat-folded-desk .opp-cards-desk { opacity: 0.6 !important; }
        
        .opp-cards-desk { position: absolute !important; top: -30px !important; left: 50% !important; transform: translateX(-50%) !important; display: flex !important; align-items: flex-end !important; pointer-events: none; }
        .opp-card-desk { width: 30px !important; height: 42px !important; border-radius: 4px !important; position: relative !important; background: repeating-linear-gradient(45deg, rgba(15,70,185,0.95) 0px, rgba(15,70,185,0.95) 2px, rgba(8,44,130,0.95) 2px, rgba(8,44,130,0.95) 6px) !important; border: 1px solid rgba(80,140,255,0.3) !important; box-shadow: 0 2px 5px rgba(0,0,0,0.8), inset 0 0 0 1px rgba(255,255,255,0.06) !important; }
        .opp-card-desk::before { content: '' !important; position: absolute !important; inset: 2px !important; border-radius: 2px !important; border: 1px solid rgba(80,140,255,0.15) !important; }
        .opp-card-desk.right-desk { margin-left: -8px !important; transform: rotate(10deg) !important; z-index: -1 !important; }

        .pot-badge-desk { background: #111; color: #ffc107; font-weight: bold; font-size: 14px; padding: 4px 14px; border-radius: 14px; border: 1.5px solid #ffc107; box-shadow: 0 2px 6px rgba(0,0,0,0.6); }
        .street-chip-pile-desk { position: relative; width: 34px; height: 28px; filter: drop-shadow(0 4px 5px rgba(0,0,0,0.65)); }
        .street-chip-pot-desk { position: absolute; left: 2px; width: 30px; height: 9px; border-radius: 50%; border: 1px solid rgba(255,255,255,0.34); background: radial-gradient(ellipse at 50% 28%, rgba(255,255,255,0.95) 0 17%, transparent 18%), linear-gradient(90deg, rgba(255,255,255,0.72) 0 10%, transparent 10% 21%, rgba(255,255,255,0.72) 21% 31%, transparent 31% 69%, rgba(255,255,255,0.72) 69% 79%, transparent 79% 90%, rgba(255,255,255,0.72) 90% 100%), linear-gradient(180deg, #f05f62 0%, #c82238 52%, #7e1022 100%); box-shadow: inset 0 1px 1px rgba(255,255,255,0.45), inset 0 -2px 2px rgba(0,0,0,0.32), 0 1px 0 rgba(0,0,0,0.7); }
        .street-chip-pot-desk.c1 { top: 18px; background-color: #b91c1c; }
        .street-chip-pot-desk.c2 { top: 14px; background: radial-gradient(ellipse at 50% 28%, rgba(255,255,255,0.95) 0 17%, transparent 18%), linear-gradient(90deg, rgba(255,255,255,0.72) 0 10%, transparent 10% 21%, rgba(255,255,255,0.72) 21% 31%, transparent 31% 69%, rgba(255,255,255,0.72) 69% 79%, transparent 79% 90%, rgba(255,255,255,0.72) 90% 100%), linear-gradient(180deg, #5ea7ff 0%, #1d5fc4 54%, #123a7a 100%); }
        .street-chip-pot-desk.c3 { top: 10px; background: radial-gradient(ellipse at 50% 28%, rgba(255,255,255,0.95) 0 17%, transparent 18%), linear-gradient(90deg, rgba(255,255,255,0.72) 0 10%, transparent 10% 21%, rgba(255,255,255,0.72) 21% 31%, transparent 31% 69%, rgba(255,255,255,0.72) 69% 79%, transparent 79% 90%, rgba(255,255,255,0.72) 90% 100%), linear-gradient(180deg, #f7d36c 0%, #c48714 54%, #7a5108 100%); }
        .street-chip-pot-desk.c4 { top: 6px; background: radial-gradient(ellipse at 50% 28%, rgba(255,255,255,0.95) 0 17%, transparent 18%), linear-gradient(90deg, rgba(255,255,255,0.72) 0 10%, transparent 10% 21%, rgba(255,255,255,0.72) 21% 31%, transparent 31% 69%, rgba(255,255,255,0.72) 69% 79%, transparent 79% 90%, rgba(255,255,255,0.72) 90% 100%), linear-gradient(180deg, #5bdc83 0%, #188544 54%, #0e4f2b 100%); }
        .street-chip-pot-desk.c5 { top: 2px; background: radial-gradient(ellipse at 50% 28%, rgba(255,255,255,0.95) 0 17%, transparent 18%), linear-gradient(90deg, rgba(255,255,255,0.72) 0 10%, transparent 10% 21%, rgba(255,255,255,0.72) 21% 31%, transparent 31% 69%, rgba(255,255,255,0.72) 69% 79%, transparent 79% 90%, rgba(255,255,255,0.72) 90% 100%), linear-gradient(180deg, #f5f7fb 0%, #bfc8d3 54%, #778392 100%); }
        .street-pot-txt-desk { background: rgba(8,9,12,0.9); border: 1px solid rgba(255,193,7,0.35); color: #f4d384; border-radius: 9px; padding: 2px 8px; font-size: 11px; font-weight: 800; line-height: 1.25; box-shadow: 0 2px 5px rgba(0,0,0,0.6); white-space: nowrap; }
        .board-container-desk { display: flex; gap: 6px; background: rgba(0,0,0,0.4); padding: 8px 16px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        .board-card-desk { width: 50px; height: 72px; background: white; border-radius: 4px; position: relative; color: black; box-shadow: 0 2px 5px rgba(0,0,0,0.6); font-family: Arial, sans-serif !important; }
        .bc-tl-desk { position: absolute; top: 3px; left: 4px; font-weight: 900; font-size: 16px; line-height: 1; }
        .bc-c-desk { position: absolute; top: 55%; left: 50%; transform: translate(-50%,-50%); font-size: 28px; line-height: 1; }
        
        .villain-act-badge-desk { position: absolute; background: #dc3545; color: #fff; font-weight: bold; font-size: 11px; padding: 2px 8px; border-radius: 6px; border: 1px solid #ffaaaa; box-shadow: 0 2px 5px rgba(0,0,0,0.6); z-index: 25; text-transform: uppercase; white-space: nowrap; left: 50%; transform: translateX(-50%); bottom: -20px; }

        .dealer-desk { position: absolute !important; z-index: 30 !important; width: 26px !important; height: 26px !important; border-radius: 50% !important; display: flex !important; align-items: center !important; justify-content: center !important; font-size: 11px !important; font-weight: 900 !important; color: #120700 !important; background: radial-gradient(circle at 38% 30%, #ffd84a, #c88408) !important; border: 2px solid rgba(255,255,255,0.35) !important; box-shadow: 0 0 0 2px rgba(0,0,0,0.7), 0 2px 10px rgba(200,132,8,0.7), inset 0 1px 3px rgba(255,255,255,0.55) !important; }

        .chip-container-desk { position: absolute !important; z-index: 22 !important; display: flex !important; flex-direction: column !important; align-items: center !important; gap: 4px !important; }
        .chip-desk, .chip-3bet-desk, .chip-4bet-desk { width: 20px !important; height: 20px !important; border-radius: 50% !important; position: relative !important; background: repeating-conic-gradient(rgba(255,255,255,0.13) 0deg 18deg, transparent 18deg 36deg), radial-gradient(circle at 36% 30%, #1e3a8a, #0c1844) !important; border: 2px solid rgba(255,255,255,0.22) !important; box-shadow: 0 0 0 1.5px rgba(0,0,0,0.7), 0 2px 5px rgba(0,0,0,0.8), inset 0 1px 2px rgba(255,255,255,0.2) !important; }
        .chip-3bet-desk { background: radial-gradient(circle at 36% 30%, #ff5722, #9e3211) !important; }
        .chip-4bet-desk { background: repeating-conic-gradient(rgba(255,255,255,0.15) 0deg 18deg, transparent 18deg 36deg), radial-gradient(circle at 36% 30%, #68158e, #3F055B) !important; }
        .chip-desk::before, .chip-3bet-desk::before, .chip-4bet-desk::before { content: '' !important; position: absolute !important; inset: 4px !important; border-radius: 50% !important; border: 1px solid rgba(255,255,255,0.12) !important; }
        .chip-desk::after, .chip-3bet-desk::after, .chip-4bet-desk::after { content: '' !important; position: absolute !important; top: 2px !important; left: 2px !important; width: 8px !important; height: 5px !important; border-radius: 50% !important; background: rgba(255,255,255,0.22) !important; filter: blur(1px) !important; }
        
        .bet-txt-desk { font-size: 12px !important; font-weight: 700 !important; color: rgba(255,235,190,0.9) !important; text-shadow: 0 0 6px rgba(255,195,40,0.6), 0 1px 3px rgba(0,0,0,0.98) !important; letter-spacing: 0.03em !important; white-space: nowrap !important; }

        .hero-desk { position: absolute !important; bottom: -70px !important; left: 50% !important; transform: translateX(-50%) !important; z-index: 30 !important; display: flex !important; flex-direction: column !important; align-items: center !important; gap: 6px !important; width: 140px !important; }
        .hero-cards-wrap-desk { display: flex !important; gap: 8px !important; position: relative !important; }
        .hero-plate-desk { width: 100px !important; height: 22px !important; background: #141518 !important; border-radius: 6px !important; border: 2px solid #ffc107 !important; display: flex !important; justify-content: space-between !important; align-items: center !important; padding: 0 8px !important; box-sizing: border-box !important; font-size: 12px !important; font-weight: bold !important; box-shadow: 0 4px 12px rgba(0,0,0,0.7) !important; transition: border-color 0.3s; }
        
        .floating-reward-desk { position: absolute !important; top: -45px !important; left: 50% !important; transform: translateX(-50%) !important; font-size: 18px !important; font-weight: 900 !important; color: #17f07e !important; text-shadow: 0 0 15px rgba(23,240,126,0.8), 0 0 30px rgba(23,240,126,0.4) !important; white-space: nowrap !important; animation: float-reward-desk 2.2s ease-out forwards !important; pointer-events: none !important; }
        @keyframes float-reward-desk { 0%   { opacity: 1; transform: translateX(-50%) translateY(0); } 100% { opacity: 0; transform: translateX(-50%) translateY(-30px); } }

        .card-desk { width: 55px !important; height: 78px !important; border-radius: 6px !important; position: relative !important; display: flex !important; flex-direction: column !important; align-items: flex-start !important; overflow: hidden !important; box-shadow: 0 0 0 1px rgba(0,0,0,0.2), 0 -8px 20px rgba(0,0,0,0.7), 0 -15px 40px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,1) !important;}
        .card-desk::after { content: '' !important; position: absolute !important; top: 0 !important; left: 0 !important; width: 60% !important; height: 45% !important; background: linear-gradient(135deg, rgba(255,255,255,0.45) 0%, transparent 100%) !important; pointer-events: none !important; border-radius: 6px 0 0 0 !important; }
        .tl-desk { padding: 4px 0 0 5px !important; font-size: 16px !important; font-weight: 900 !important; line-height: 0.9 !important; letter-spacing: -0.04em !important; z-index: 2 !important; position: relative !important; font-family: Arial, sans-serif !important; }
        .c-desk { position: absolute !important; top: 55% !important; left: 50% !important; transform: translate(-50%,-50%) !important; font-size: 28px !important; opacity: 1 !important; line-height: 1 !important; z-index: 2 !important; font-family: Arial, sans-serif !important; }
        .suit-red   { color: #c00a0a !important; }
        .suit-black { color: #0a0a0a !important; }
        .suit-blue  { color: #0056b3 !important; }
        .suit-green { color: #198754 !important; }
        
        .rng-badge-desk { position: absolute !important; top: 50% !important; right: -35px !important; transform: translateY(-50%) !important; width: 30px !important; height: 30px !important; border-radius: 50% !important; font-weight: 900 !important; font-size: 13px !important; display: flex !important; align-items: center !important; justify-content: center !important; box-shadow: 0 4px 8px rgba(0,0,0,0.6) !important; z-index: 40 !important; }
        
        /* ── Action Buttons Color Overrides (Desktop) ── */
        .pf-btn-0 button { background: linear-gradient(180deg, #252830 0%, #16181f 100%) !important; box-shadow: 0 5px 0 #0c0d12, 0 8px 20px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.08), inset 0 0 0 1px rgba(255,255,255,0.06) !important; }
        .pf-btn-0 button:active { box-shadow: 0 1px 0 #0c0d12, inset 0 1px 0 rgba(255,255,255,0.05), 0 0 25px rgba(255,255,255,0.15) !important; filter: brightness(1.5) !important; }
        .pf-btn-0 button p { color: rgba(190,190,205,0.8) !important; }

        .pf-btn-1 button { background: linear-gradient(180deg, #0c3828 0%, #071e16 100%) !important; box-shadow: 0 4px 0 #030f0b, 0 8px 25px rgba(0,180,80,0.15), inset 0 1px 0 rgba(0,230,110,0.12), inset 0 0 0 1px rgba(0,200,90,0.1) !important; }
        .pf-btn-1 button:active { box-shadow: 0 1px 0 #030f0b, inset 0 1px 0 rgba(0,200,90,0.08), 0 0 25px rgba(0,255,100,0.5) !important; filter: brightness(1.4) saturate(1.2) !important; }
        .pf-btn-1 button p { color: rgba(50,220,130,0.92) !important; text-shadow: 0 0 15px rgba(30,200,100,0.4) !important; }

        .pf-btn-2 button { background: linear-gradient(180deg, #4a0909 0%, #300505 100%) !important; box-shadow: 0 5px 0 #1a0303, 0 8px 25px rgba(180,20,20,0.25), inset 0 1px 0 rgba(255,80,80,0.14), inset 0 0 0 1px rgba(200,30,30,0.18) !important; }
        .pf-btn-2 button:active { box-shadow: 0 1px 0 #1a0303, inset 0 1px 0 rgba(255,80,80,0.1), 0 0 20px rgba(255,50,50,0.5) !important; filter: brightness(1.4) saturate(1.2) !important; }
        .pf-btn-2 button p { color: rgba(255,90,90,0.95) !important; text-shadow: 0 0 15px rgba(220,50,50,0.5) !important; }

        .pf-btn-3 button { background: linear-gradient(180deg, #30094a 0%, #160530 100%) !important; box-shadow: 0 5px 0 #0f031a, 0 8px 25px rgba(180,20,220,0.25), inset 0 1px 0 rgba(220,80,255,0.14), inset 0 0 0 1px rgba(200,30,220,0.18) !important; }
        .pf-btn-3 button:active { box-shadow: 0 1px 0 #0f031a, inset 0 1px 0 rgba(220,80,255,0.1), 0 0 20px rgba(220,50,255,0.5) !important; filter: brightness(1.4) saturate(1.2) !important; }
        .pf-btn-3 button p { color: rgba(230,90,255,0.95) !important; text-shadow: 0 0 14px rgba(220,50,255,0.5) !important; }

        </style>
    """, unsafe_allow_html=True)

    fish_db = utils.load_fish_data()
    if not fish_db: 
        st.error("База пуста. Проверь файлы JSON в папке fish_data.")
        return

    flat_fish_db = {}
    for vp, b_data in fish_db.items():
        for tex, p_data in b_data.items():
            for pos, l_data in p_data.items():
                for line, r_data in l_data.items():
                    for runout, spot_info in r_data.items():
                        flat_fish_db[f"{vp}|{tex}|{pos}|{line}|{runout}"] = spot_info

    with st.sidebar:
        st.markdown("### ⚙️ View & Fish Filters")
        c_v1, c_v2 = st.columns(2)
        with c_v1:
            if st.button("📱 Mobile", key="mv_btn"): st.session_state.actual_view_type = "📱 Mobile"; st.rerun()
        with c_v2:
            if st.button("💻 Desktop", key="dv_btn"): st.session_state.actual_view_type = "💻 Desktop"; st.rerun()
        st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)

        saved = utils.load_user_settings(is_fish=True)
        
        all_vpips = sorted(list(fish_db.keys()))
        sel_vpips = st.multiselect("1. VPIP", all_vpips, default=[x for x in saved.get("fish_sel_vpips", []) if x in all_vpips])
        
        avail_pos = set(); avail_boards = set()
        for vp in (sel_vpips or all_vpips):
            for tex, pos_data in fish_db.get(vp, {}).items():
                avail_boards.add(tex)
                for pos in pos_data.keys(): avail_pos.add(pos)

        sel_boards = st.multiselect("2. Board", sorted(list(avail_boards)), default=[x for x in saved.get("fish_sel_boards", []) if x in avail_boards])
        sel_pos = st.multiselect("3. Position", sorted(list(avail_pos)), default=[x for x in saved.get("fish_sel_pos", []) if x in avail_pos])
        
        avail_lines = set(); avail_runouts = set()
        for vp in (sel_vpips or all_vpips):
            for tex in (sel_boards or list(avail_boards)):
                for pos, line_data in fish_db.get(vp, {}).get(tex, {}).items():
                    if sel_pos and pos not in sel_pos: continue
                    for line, runout_data in line_data.items():
                        avail_lines.add(line)
                        for runout in runout_data.keys(): avail_runouts.add(runout)

        sel_lines = st.multiselect("4. Action Line", sorted(list(avail_lines)), default=[x for x in saved.get("fish_sel_lines", []) if x in avail_lines])
        
        sel_spots_keys = []
        if sel_lines:
            saved_runouts = saved.get("fish_spots", [])
            
            matching_runouts = []
            for vp in (sel_vpips or all_vpips):
                for tex in (sel_boards or list(avail_boards)):
                    for pos, line_data in fish_db.get(vp, {}).get(tex, {}).items():
                        if sel_pos and pos not in sel_pos: continue
                        for line, runout_data in line_data.items():
                            if sel_lines and line not in sel_lines: continue
                            for runout in runout_data.keys():
                                full_key = f"{vp}|{tex}|{pos}|{line}|{runout}"
                                matching_runouts.append((runout, full_key))

            def runout_is_checked(full_key):
                widget_key = f"fish_chk_d_{full_key}"
                if widget_key in st.session_state:
                    return bool(st.session_state[widget_key])
                return (full_key in saved_runouts) if "fish_spots" in saved else True

            all_runouts_selected = bool(matching_runouts) and all(runout_is_checked(full_key) for _, full_key in matching_runouts)
            title_col, all_col = st.columns([0.78, 0.22])
            with title_col:
                st.markdown("**5. Runouts:**")
            with all_col:
                st.markdown('<span id="fish-runouts-all-d-marker"></span>', unsafe_allow_html=True)
                if matching_runouts and st.button("ALL", key="fish_runouts_all_d", use_container_width=False):
                    target_state = not all_runouts_selected
                    for _, full_key in matching_runouts:
                        st.session_state[f"fish_chk_d_{full_key}"] = target_state
                    saved["fish_sel_vpips"] = sel_vpips
                    saved["fish_sel_boards"] = sel_boards
                    saved["fish_sel_pos"] = sel_pos
                    saved["fish_sel_lines"] = sel_lines
                    saved["fish_spots"] = [full_key for _, full_key in matching_runouts] if target_state else []
                    utils.save_user_settings(saved, is_fish=True)
                    st.session_state.fish_hand = None
                    st.rerun()
            
            for runout_name, full_key in matching_runouts:
                is_checked = runout_is_checked(full_key)
                parts = full_key.split('|')
                spot_setup = flat_fish_db.get(full_key, {}).get("setup", {})
                line_lbl = spot_setup.get("spot_label", parts[3])
                short_lbl = f"{runout_name} ({parts[0]} | {line_lbl})"
                if st.checkbox(short_lbl, value=is_checked, key=f"fish_chk_d_{full_key}"):
                    sel_spots_keys.append(full_key)
        
        if st.button("🚀 Apply Filters", use_container_width=True):
            saved["fish_sel_vpips"] = sel_vpips
            saved["fish_sel_boards"] = sel_boards
            saved["fish_sel_pos"] = sel_pos
            saved["fish_sel_lines"] = sel_lines
            saved["fish_spots"] = sel_spots_keys
            utils.save_user_settings(saved, is_fish=True)
            st.session_state.fish_hand = None
            st.rerun()

    pool = sel_spots_keys
    if not pool:
        st.warning("⚠️ Выбери фильтры в боковом меню.")
        st.stop()

    stats_data_init = safe_load_stats()
    if 'fish_shields' not in st.session_state: st.session_state.fish_shields = stats_data_init.get("shields", 0)
    if 'fish_combo' not in st.session_state: st.session_state.fish_combo = stats_data_init.get("combo", 0)

    for k in ['fish_session_hands', 'fish_session_correct', 'fish_rng']:
        if k not in st.session_state: st.session_state[k] = 0
    if 'fish_toast_msgs' not in st.session_state: st.session_state.fish_toast_msgs = []
    if st.session_state.fish_toast_msgs:
        for msg in st.session_state.fish_toast_msgs: st.toast(msg, icon="🔥" if "Combo" in msg else "🎯")
        st.session_state.fish_toast_msgs = []
    if 'fish_hand' not in st.session_state: st.session_state.fish_hand = None
    if 'fish_current_spot_key' not in st.session_state: st.session_state.fish_current_spot_key = None
    if 'fish_last_error' not in st.session_state: st.session_state.fish_last_error = False
    
    if st.session_state.fish_hand is None or st.session_state.fish_current_spot_key is None or st.session_state.fish_current_spot_key not in pool:
        chosen_key = random.choice(pool)
        st.session_state.fish_current_spot_key = chosen_key
        data = flat_fish_db[chosen_key]
        t_range = data.get("training", "")
        poss = fish_parse_range(t_range)
        srs = utils.load_srs_data() 
        w = [srs.get(f"{chosen_key}_{h}".replace(" ","_"), 100) for h in poss]
        
        if sum(w) == 0: w = [100]*len(poss)
        st.session_state.fish_hand = random.choices(poss, weights=w, k=1)[0]
        st.session_state.fish_rng = random.randint(0, 99)

    chosen_key = st.session_state.fish_current_spot_key
    data = flat_fish_db[chosen_key]
    chosen_parts = chosen_key.split('|')
    setup = data.get("setup", {})
    spot_line_name = setup.get("spot_label", chosen_parts[3] if len(chosen_parts) > 3 else chosen_key)
    
    hero_pos = setup.get("hero_pos", "BTN")
    villain_pos = setup.get("villain_pos", "BB")
    btn_pos = setup.get("btn_pos", "BTN")
    active_players = setup.get("active_players", [hero_pos, villain_pos])
    board_raw = setup.get("board_cards", [])
    base_pot = setup.get("pot_size", 0)
    villain_act = setup.get("villain_action", "")
    hero_act = setup.get("hero_action", "")
    actions = data.get("actions", ["Check"])
    ranges = data.get("ranges", {})
    
    v_size = setup.get("villain_sizing_bb", "")
    is_bet = villain_act and ("BET" in villain_act.upper() or "RAISE" in villain_act.upper() or "ALL-IN" in villain_act.upper())
    
    def fmt_bb_value(value):
        try:
            numeric_value = float(value)
            return str(int(numeric_value)) if numeric_value.is_integer() else f"{numeric_value:.1f}"
        except (TypeError, ValueError):
            return str(value)

    street_pot = setup.get("street_start_pot_bb", base_pot)
    display_pot = setup.get("total_pot_bb")
    if display_pot is None:
        display_pot = base_pot
        if is_bet and v_size:
            try: display_pot = round(float(base_pot) + float(v_size), 1)
            except (TypeError, ValueError): pass
    display_pot_str = fmt_bb_value(display_pot)
    street_pot_str = fmt_bb_value(street_pot)

    table_size = setup.get("table_size", 6)
    stacks_data = setup.get("stacks", {})

    h_val = st.session_state.fish_hand
    action_weights = {act: fish_get_weight(h_val, ranges.get(act, "")) for act in actions}
    
    sorted_actions = sorted(actions, key=lambda x: 1 if x.lower() in ['check', 'fold'] else 0)
    
    correct_act = sorted_actions[0]
    cumulative = 0
    for act in sorted_actions:
        if st.session_state.fish_rng < cumulative + action_weights[act]:
            correct_act = act
            break
        cumulative += action_weights[act]

    if len(h_val) == 4:
        r1, s1_raw, r2, s2_raw = h_val[0], h_val[1], h_val[2], h_val[3]
        s1, s2 = map_suit(s1_raw), map_suit(s2_raw)
    else:
        r1, r2 = h_val[0] if len(h_val)>0 else 'X', h_val[1] if len(h_val)>1 else 'X'
        s1, s2 = map_suit('s'), map_suit('s')
        
    c1, c2 = get_suit_color_class(s1), get_suit_color_class(s2)

    stats_data = safe_load_stats()
    rank_name, next_xp = utils.get_rank_info(stats_data.get("xp", 0))
    c = st.session_state.fish_combo
    progress_pct = int((stats_data.get("xp", 0) / next_xp) * 100) if next_xp != "MAX" else 100
    
    sh = st.session_state.fish_session_hands
    scorr = st.session_state.fish_session_correct
    wr = int((scorr / sh * 100)) if sh > 0 else 0
    wr_color = '#28a745' if wr >= 90 else '#ffc107' if wr >= 80 else '#dc3545'

    try: mastery = utils.get_spot_mastery_info(stats_data.get("spot_mastery", {}).get(chosen_key, {}))
    except: mastery = {"rank": 0, "name": "Sandbox", "icon": "⚪", "color": "#6c757d", "is_rusty": False, "prog_pct": 0, "total": 0, "next": 100, "svg": ""}

    m_rust = mastery.get("is_rusty", False)
    m_pct = mastery.get("prog_pct", 0)
    m_total = mastery.get("total", 0)
    m_next = mastery.get("next", 100)
    if mastery.get("rank", 0) >= 5: hands_left_text = "MAX RANK"
    else: hands_left_text = f"Remaining: {max(0, m_next - m_total)} hands"

    visual_rank = mastery.get("rank", 0)
    if visual_rank > 5: visual_rank = 5

    theme = THEMES[visual_rank]
    m_icon = theme["icon"]
    m_name = theme["name"]
    st.markdown(theme["css"], unsafe_allow_html=True)

    combo_cls = ""
    if c >= 1000: combo_cls = "combo-glow-1000"
    elif c >= 500: combo_cls = "combo-glow-500"
    elif c >= 200: combo_cls = "combo-glow-200"
    elif c >= 100: combo_cls = "combo-glow-100"
    elif c >= 50: combo_cls = "combo-glow-50"
    elif c >= 25: combo_cls = "combo-glow-25"
    elif c >= 10: combo_cls = "combo-glow-10"
    elif c >= 5: combo_cls = "combo-glow-5"

    is_flashing_correct = st.session_state.get("fish_flash_correct", False)
    table_status_class = ""
    if is_flashing_correct:
        table_status_class = "table-glow-correct"
    elif st.session_state.fish_last_error:
        table_status_class = "table-glow-incorrect"

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

    is_pulsing = "rage-pulse-desk" if rage_pct >= 95 and next_mult != "MAX" else ""
    is_flashing = "rage-flash-desk" if st.session_state.pop("fish_just_leveled_up", False) else ""
    
    if curr_mult == 1.0: grad = "linear-gradient(90deg, #17a2b8, #0dcaf0)"
    elif curr_mult == 1.5: grad = "linear-gradient(90deg, #0dcaf0, #28a745)"
    elif curr_mult == 2.0: grad = "linear-gradient(90deg, #28a745, #ffc107)"
    elif curr_mult == 3.0: grad = "linear-gradient(90deg, #ffc107, #fd7e14)"
    elif curr_mult == 4.0: grad = "linear-gradient(90deg, #fd7e14, #dc3545)"
    elif curr_mult == 5.0: grad = "linear-gradient(90deg, #dc3545, #6f42c1)"
    else: grad = "linear-gradient(90deg, #6f42c1, #ff00ff)"

    shield_display = (
        f'<span style="'
        f'display:{"inline-flex" if st.session_state.fish_shields > 0 else "none"};'
        f'align-items:center;gap:3px;'
        f'font-size:14px;font-weight:800;letter-spacing:0.04em;'
        f'padding:2px 8px 2px 6px;margin-left:6px;'
        f'background:rgba(13,202,240,0.09);'
        f'border:1px solid rgba(13,202,240,0.28);'
        f'border-radius:8px;'
        f'color:rgba(13,202,240,0.92);'
        f'box-shadow:0 0 8px rgba(13,202,240,0.12);'
        f'">🛡️{st.session_state.fish_shields}</span>'
    )

    combo_badge = (
        f'<div style="flex:1;display:flex;justify-content:center;align-items:center;">'
        f'<div style="'
        f'display:inline-flex;align-items:center;gap:2px;'
        f'padding:4px 16px 4px 12px;border-radius:20px;'
        f'background:rgba(255,255,255,0.035);'
        f'border:1px solid rgba(255,255,255,0.09);'
        f'box-shadow:0 0 14px rgba(255,150,20,0.07),inset 0 1px 0 rgba(255,255,255,0.05);'
        f'">'
        f'<span style="'
        f'font-size:18px;font-weight:900;color:#fff;letter-spacing:-0.03em;'
        f'text-shadow:0 0 12px rgba(255,130,10,0.8),0 0 24px rgba(255,100,0,0.3);'
        f'">🔥{c}</span>'
        f'{shield_display}'
        f'</div></div>'
    )

    header_html = (
        f'<div class="cn-desk-header">'
        f'<div class="cn-desk-wr-track">'
        f'<div class="cn-desk-wr-fill" style="width:{wr if sh > 0 else 100}%; background:{wr_color if sh > 0 else "#2a2a2a"}; box-shadow:0 0 8px {wr_color if sh > 0 else "transparent"};"></div></div>'
        f'<div class="cn-desk-inner">'
        f'<div class="cn-desk-row1">'
        f'<div style="flex:1;min-width:0;">'
        f'<div class="cn-desk-rank">{rank_name}</div>'
        f'<div class="cn-desk-xp-bar-wrap"><div class="cn-desk-xp-bar-bg"><div class="cn-desk-xp-bar-fill" style="width:{progress_pct}%;"></div></div></div>'
        f'</div>'
        f'<div class="cn-desk-xp-meta">${stats_data.get("xp", 0)} <span style="color:rgba(255,255,255,0.15);margin:0 4px;">/</span> ${next_xp}</div>'
        f'</div>'
        f'<div class="cn-desk-row2">'
        f'<div class="cn-desk-stat">'
        f'<div class="cn-desk-stat-label">Winrate</div>'
        f'<div class="cn-desk-stat-val" style="color:{wr_color}; text-shadow:0 0 10px {wr_color}44;">{wr}%</div>'
        f'</div>'
        f'<div class="cn-desk-combo-wrap">{combo_badge}</div>'
        f'<div class="cn-desk-stat" style="text-align:right;">'
        f'<div class="cn-desk-stat-label">Hands</div>'
        f'<div class="cn-desk-stat-val light">{sh}</div>'
        f'</div>'
        f'</div></div></div>'
    )

    rage_bar_html = f"""
    <div class="rage-bar-container-desk {is_flashing}">
      <div class="rage-bar-fill-desk {is_pulsing}" style="width: {rage_pct}%; background: {grad};"></div>
      <div class="rage-labels-desk">
        <span>{lbl_left}</span>
        <span>{lbl_right}</span>
      </div>
    </div>
    """

    anim_html = ""
    anim_reward = st.session_state.pop("fish_anim_reward", None)
    if anim_reward is not None:
        if anim_reward > 0: a_color = "#00ff00"; a_text = f"+${anim_reward}"
        elif anim_reward < 0: a_color = "#ff0000"; a_text = f"-${abs(anim_reward)}"
        else: a_color = "#888"; a_text = "$0"
        anim_html = f'<div class="floating-reward-desk" style="color: {a_color}">{a_text}</div>'
        
    shatter_html = '<div class="glass-shatter"></div>' if st.session_state.pop("fish_shield_break_anim", False) else ""

    st.markdown(header_html, unsafe_allow_html=True)
    st.markdown(rage_bar_html, unsafe_allow_html=True)

    order = ["EP", "MP", "CO", "BTN", "SB", "BB"]
    try: hero_idx = order.index(hero_pos)
    except ValueError: hero_idx = 0
    rot = order[hero_idx:] + order[:hero_idx]

    is_hu = (table_size == 2)

    def get_seat_style(idx):
        return {
            1: "top: 75%; left: -3%; transform: translateY(-50%);", 
            2: "top: 15%; left: -3%;", 
            3: "top: -10%; left: 50%; transform: translateX(-50%);", 
            4: "top: 15%; right: -3%;", 
            5: "top: 75%; right: -3%; transform: translateY(-50%);"
        }.get(idx, "")

    def get_chip_style(idx):
        return {
            0: "bottom: 45px; left: 50%; transform: translateX(-50%);", 
            1: "top: 60%; left: 16%; transform: translateY(-50%);", 
            2: "top: 25%; left: 10%;",
            3: "top: 15%; left: 50%; transform: translateX(-50%);", 
            4: "top: 25%; right: 10%;", 
            5: "top: 60%; right: 16%; transform: translateY(-50%);"
        }.get(idx, "")

    def get_btn_style(idx):
        return {
            0: "bottom: 20px; left: 50%; margin-left: -110px; z-index: 35;", 
            1: "top: 77%; left: 12%; transform: translateY(-50%);", 
            2: "top: 28%; left: 3%;",
            3: "top: 12%; left: 58%;", 
            4: "top: 28%; right: 3%;", 
            5: "top: 77%; right: 12%; transform: translateY(-50%);"
        }.get(idx, "")

    opp_html = ""; chips_html = ""

    if is_hu:
        villain_p = [p for p in active_players if p != hero_pos][0] if len(active_players) > 1 else "BB"
        p_stack = stacks_data.get(villain_p, "---")
        cls = "seat-active-desk"
        cards = '<div class="opp-cards-desk"><div class="opp-card-desk"></div><div class="opp-card-desk right-desk"></div></div>'
        ss = get_seat_style(3)
        
        v_act_html = ""
        if villain_act:
            if is_bet:
                act_word = "RAISE" if "RAISE" in villain_act.upper() else ("ALL-IN" if "ALL-IN" in villain_act.upper() else "BET")
                v_act_html = f'<div class="villain-act-badge-desk act-bottom-mob">{act_word}</div>'
            else:
                v_act_html = f'<div class="villain-act-badge-desk act-bottom-mob">{villain_act}</div>'
                
        opp_html += f'<div class="seat-desk {cls}" style="{ss}">{cards}<div class="ava-desk"></div><div class="plate-desk"><span class="pos-desk">{villain_p}</span><span class="stack-desk">{p_stack}</span></div>{v_act_html}</div>'
        
        cs = get_chip_style(3)
        if is_bet:
            bet_amount_str = f"{v_size}" if v_size else villain_act.upper().replace("BET", "").replace("RAISE", "").replace("ALL-IN", "").strip().lower()
            bet_txt = f'<div class="bet-txt-desk">{bet_amount_str} bb</div>'
            chips_html += f'<div class="chip-container-desk" style="{cs}"><div class="chip-desk"></div>{bet_txt}</div>'
        
        if villain_p == btn_pos:
            bs = get_btn_style(3)
            chips_html += f'<div class="dealer-desk" style="{bs}">D</div>'
    else:
        for i in range(1, 6):
            p = rot[i]
            p_stack = stacks_data.get(p, "---")
            has_cards = (p in active_players)
            cls = "seat-active-desk" if has_cards else "seat-folded-desk"
            cards = '<div class="opp-cards-desk"><div class="opp-card-desk"></div><div class="opp-card-desk right-desk"></div></div>' if has_cards else ""
            ss = get_seat_style(i)
            
            v_act_html = ""
            if p == villain_pos and villain_act:
                if is_bet:
                    act_word = "RAISE" if "RAISE" in villain_act.upper() else ("ALL-IN" if "ALL-IN" in villain_act.upper() else "BET")
                    v_act_html = f'<div class="villain-act-badge-desk act-bottom-mob">{act_word}</div>'
                else:
                    v_act_html = f'<div class="villain-act-badge-desk act-bottom-mob">{villain_act}</div>'
                
            opp_html += f'<div class="seat-desk {cls}" style="{ss}">{cards}<div class="ava-desk"></div><div class="plate-desk"><span class="pos-desk">{p}</span><span class="stack-desk">{p_stack}</span></div>{v_act_html}</div>'

            if p == btn_pos:
                bs = get_btn_style(i)
                chips_html += f'<div class="dealer-desk" style="{bs}">D</div>'
                
            if p == villain_pos and is_bet:
                cs = get_chip_style(i)
                bet_amount_str = f"{v_size}" if v_size else villain_act.upper().replace("BET", "").replace("RAISE", "").replace("ALL-IN", "").strip().lower()
                bet_txt = f'<div class="bet-txt-desk">{bet_amount_str} bb</div>'
                chips_html += f'<div class="chip-container-desk" style="{cs}"><div class="chip-desk"></div>{bet_txt}</div>'

    if hero_act:
        is_hero_bet = ("BET" in hero_act.upper() or "RAISE" in hero_act.upper() or "ALL-IN" in hero_act.upper())
        if is_hero_bet:
            hero_cs = get_chip_style(0)
            hero_bet_amount_str = hero_act.upper().replace("BET", "").replace("RAISE", "").replace("ALL-IN", "").strip().lower()
            hero_bet_txt = f'<div class="bet-txt-desk">{hero_bet_amount_str} bb</div>'
            chips_html += f'<div class="chip-container-desk" style="{hero_cs}"><div class="chip-desk"></div>{hero_bet_txt}</div>'

    hero_stack = stacks_data.get(hero_pos, "---")
    if rot[0] == btn_pos:
        hero_bs = get_btn_style(0)
        chips_html += f'<div class="dealer-desk" style="{hero_bs}">D</div>'

    board_html = ""
    for card in board_raw:
        rank_str = card[:-1].upper()
        suit = map_suit(card[-1])
        sc = get_suit_color_class(suit)
        board_html += f'<div class="board-card-desk"><div class="bc-tl-desk {sc}">{rank_str}</div><div class="bc-c-desk {sc}">{suit}</div></div>'

    street_pot_html = ""
    if street_pot not in (None, ""):
        street_pot_html = f'<div class="pf-street-pot-desk"><div class="street-chip-pile-desk"><div class="street-chip-pot-desk c1"></div><div class="street-chip-pot-desk c2"></div><div class="street-chip-pot-desk c3"></div><div class="street-chip-pot-desk c4"></div><div class="street-chip-pot-desk c5"></div></div><div class="street-pot-txt-desk">{street_pot_str} bb</div></div>'
        
    mastery_html = f"""<div style="position: absolute; bottom: -60px; left: 20px; z-index: 15; width: 120px; display: flex; flex-direction: column; align-items: flex-start; gap: 4px; pointer-events: none;">
        <div style="background: #111; border: 1px solid rgba(255,255,255,0.2); color: #fff; display: inline-flex; align-items: center; gap: 4px; border-radius: 20px; padding: 3px 10px; font-size: 11px; font-weight: 700; letter-spacing: 0.05em;">{m_icon} {m_name}</div>
        <div style="width: 80px; height: 3px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden; margin-top: 2px;"><div style="height: 100%; border-radius: 3px; background: #0dcaf0; width: {m_pct}%;"></div></div>
        <div style="font-size: 10px; letter-spacing: 0.06em; margin-top: 2px; color: rgba(255,255,255,0.7);">{hands_left_text}</div>
    </div>"""

    onenote = setup.get("info_link", setup.get("onenote_url", ""))
    if onenote:
        hook_html = f'<a href="{onenote}" target="_blank" class="info-hook" title="Open in OneNote">i</a>'
    else:
        hook_html = f'<a href="#" target="_blank" class="info-hook" style="opacity:0.3; cursor:default;" onclick="return false;" title="No link">i</a>'

    html = f'<div class="desktop-game-area {combo_cls} {table_status_class}">{shatter_html}<div class="pf-pot-badge-desk"><div class="pot-badge-desk">Total Pot: {display_pot_str} bb</div></div><div class="pf-board-desk"><div class="board-container-desk">{board_html}</div></div>{street_pot_html}{hook_html}{mastery_html}{opp_html}{chips_html}<div class="hero-desk">{anim_html}<div class="hero-cards-wrap-desk"><div class="card-desk"><div class="tl-desk {c1}">{r1}<br>{s1}</div><div class="c-desk {c1}">{s1}</div></div><div class="card-desk"><div class="tl-desk {c2}">{r2}<br>{s2}</div><div class="c-desk {c2}">{s2}</div></div><div class="rng-badge-desk">{st.session_state.fish_rng}</div></div><div class="hero-plate-desk"><span class="pos-desk">HERO {hero_pos}</span><span class="stack-desk">{hero_stack}</span></div></div></div>'
    
    st.markdown(html, unsafe_allow_html=True)

    def handle_action(action):
        corr = (correct_act == action)
        st.session_state.fish_session_hands += 1
        
        k = f"{chosen_key}_{h_val}".replace(" ","_")
        utils.update_srs_auto(k, h_val, corr)
        
        shield_used = False
        if corr:
            st.session_state.fish_session_correct += 1
            st.session_state.fish_combo += 1
            st.session_state.fish_last_error = False
            st.session_state.fish_flash_correct = True
            
            c_new = st.session_state.fish_combo
            if c_new == 100:
                st.session_state.fish_shields += 1
                st.session_state.fish_toast_msgs.append("🛡️ +1 ЩИТ (100 комбо)!")
            elif c_new == 250:
                st.session_state.fish_shields += 1
                st.session_state.fish_toast_msgs.append("🛡️ +1 ЩИТ (250 комбо)!")
            elif c_new == 500:
                st.session_state.fish_shields += 1
                st.session_state.fish_toast_msgs.append("🛡️ +1 ЩИТ (500 комбо)!")
            elif c_new == 1000:
                st.session_state.fish_shields += 4
                st.session_state.fish_toast_msgs.append("🛡️ +4 ЩИТА (1000 комбо - GODLIKE)!")

        else:
            st.session_state.fish_flash_correct = False
            if st.session_state.fish_shields > 0:
                st.session_state.fish_shields -= 1
                st.session_state.fish_shield_break_anim = True
                st.session_state.fish_last_error = True
                shield_used = True
                st.session_state.fish_msg = f"🛡️ ЩИТ ПРОБИТ! Защита от мисклика. Правильно: {correct_act}"
            else:
                st.session_state.fish_combo = 0
                st.session_state.fish_last_error = True
                st.session_state.fish_msg = f"❌ ОШИБКА! Правильно: {correct_act}"
            
        c_new = st.session_state.fish_combo
        new_mult = 1.0
        if c_new >= 500: new_mult = 10.0
        elif c_new >= 250: new_mult = 5.0
        elif c_new >= 100: new_mult = 4.0
        elif c_new >= 50: new_mult = 3.0
        elif c_new >= 25: new_mult = 2.0
        elif c_new >= 10: new_mult = 1.5

        if new_mult > curr_mult:
            st.session_state.fish_just_leveled_up = True

        curr_stats = safe_load_stats()
        curr_stats["combo"] = st.session_state.fish_combo
        curr_stats["shields"] = st.session_state.fish_shields
        curr_stats["total_hands"] = curr_stats.get("total_hands", 0) + 1
        
        now_date_str = datetime.now().strftime("%Y-%m-%d")
        
        last_date = curr_stats.get("last_date", "")
        if last_date:
            try:
                delta = (datetime.now().date() - datetime.strptime(last_date, "%Y-%m-%d").date()).days
                if delta == 1: curr_stats["streak"] = curr_stats.get("streak", 1) + 1
                elif delta > 1: curr_stats["streak"] = 1
            except: curr_stats["streak"] = 1
        else: curr_stats["streak"] = 1
        curr_stats["last_date"] = now_date_str
        
        if "spot_mastery" not in curr_stats: curr_stats["spot_mastery"] = {}
        sp_data = curr_stats["spot_mastery"].get(chosen_key, {"t": 0, "h": "", "d": ""})
        if not isinstance(sp_data, dict): sp_data = {"t": 0, "h": "", "d": ""}
        sp_data["t"] += 1
        sp_data["h"] += "1" if corr else "0"
        sp_data["d"] = now_date_str
        if len(sp_data["h"]) > 100: sp_data["h"] = sp_data["h"][-100:]
        curr_stats["spot_mastery"][chosen_key] = sp_data
        
        if curr_stats.get("dailies", {}).get("date") != now_date_str:
            try: curr_stats["dailies"] = {"date": now_date_str, "quests": utils.generate_dailies()}
            except: pass
            
        if "dailies" in curr_stats and "quests" in curr_stats["dailies"]:
            for q in curr_stats["dailies"]["quests"]:
                if not q.get("done", False):
                    if q["id"] == "play": q["progress"] += 1
                    elif q["id"] == "correct" and corr: q["progress"] += 1
                    elif q["id"] == "combo" and c_new > q["progress"]: q["progress"] = c_new
                    
                    if q["progress"] >= q["target"]:
                        q["progress"] = q["target"]
                        q["done"] = True
                        curr_stats["xp"] = curr_stats.get("xp", 0) + q.get("xp", 0)
                        st.session_state.fish_toast_msgs.append(f"🎯 Daily: {q['desc']} (+${q['xp']})")
        
        reward_val = 0
        if not shield_used:
            if corr: reward_val = int(10 * curr_mult)
            else:
                if visual_rank == 1: reward_val = -int(10 * curr_mult)
                elif visual_rank > 1: reward_val = -int(20 * curr_mult)
        
        curr_stats["xp"] = curr_stats.get("xp", 0) + reward_val
        if curr_stats["xp"] < 0: curr_stats["xp"] = 0
        
        if c_new > curr_stats.get("max_combo", 0):
            curr_stats["max_combo"] = c_new
            
        safe_save_stats(curr_stats)
        st.session_state.fish_anim_reward = reward_val
        
        parts = chosen_key.split('|')
        safe_save_history({
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
            "Fish_Type": parts[0] if len(parts) > 0 else "",
            "Position": parts[2] if len(parts) > 2 else "",
            "Action_Line": parts[3] if len(parts) > 3 else "",
            "Texture": parts[1] if len(parts) > 1 else "",
            "Runout": parts[4] if len(parts) > 4 else "",
            "Hand": f"{h_val}", 
            "Action_Taken": action,
            "Correct_Action": correct_act, 
            "Result": int(corr),
            "XP": reward_val
        })

        if hasattr(utils, "force_sync"):
            utils.force_sync()
            
        st.rerun()

    if is_flashing_correct:
        time.sleep(0.5)
        st.session_state.fish_flash_correct = False
        st.session_state.fish_hand = None
        st.rerun()
    elif st.session_state.fish_last_error:
        st.markdown(f'<div style="background:#dc3545; color:white; padding:15px; border-radius:14px; text-align:center; font-weight:bold; margin-bottom:20px; font-size:18px; box-shadow: 0 5px 15px rgba(0,0,0,0.3); max-width: 850px; margin-left: auto; margin-right: auto;">{st.session_state.fish_msg}</div>', unsafe_allow_html=True)
        st.markdown("""<style>
        div[data-testid="stButton"] button[kind="primary"] {
            background: linear-gradient(180deg, #1c3a55 0%, #102436 100%) !important;
            box-shadow: 0 5px 0 #081520, 0 8px 25px rgba(30,120,200,0.2), inset 0 1px 0 rgba(60,160,255,0.12), inset 0 0 0 1px rgba(40,130,220,0.14) !important;
            border: none !important; height: 60px !important; border-radius: 14px !important; max-width: 850px; margin: 0 auto;
        }
        div[data-testid="stButton"] button[kind="primary"]:active { transform: translateY(5px) !important; box-shadow: 0 1px 0 #081520, inset 0 1px 0 rgba(60,160,255,0.08) !important; }
        div[data-testid="stButton"] button[kind="primary"] p { color: rgba(80,180,255,0.95) !important; text-shadow: 0 0 15px rgba(50,160,240,0.5) !important; font-size: 16px !important; font-weight: 900 !important; letter-spacing: 0.1em !important; text-transform: uppercase !important; }
        </style>""", unsafe_allow_html=True)
        
        if st.button("UNDERSTOOD, NEXT", type="primary", use_container_width=True):
            st.session_state.fish_last_error = False
            st.session_state.fish_hand = None
            st.session_state.fish_shield_break_anim = False
            st.rerun()
    else:
        st.markdown(f'<div class="rng-hint-wrap-desk">{spot_line_name}</div>', unsafe_allow_html=True)

        btn_cols = st.columns(len(actions))
        for i, act in enumerate(actions):
            with btn_cols[i]:
                st.markdown(f'<div class="pf-btn-{i}">', unsafe_allow_html=True)
                if st.button(act.upper(), key=f"pf_btn_{i}", use_container_width=True):
                    handle_action(act)
                st.markdown('</div>', unsafe_allow_html=True)
