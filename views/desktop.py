import streamlit as st
import random
import time
from datetime import datetime
import poker_utils as utils
import inspect

def get_spot_training_hands(spot_key, mastery_dict):
    spot_stats = mastery_dict.get(spot_key, {})
    if not isinstance(spot_stats, dict):
        return 0
    try:
        return max(0, int(spot_stats.get("t", 0) or 0))
    except (TypeError, ValueError):
        return 0

def build_spot_training_progress_html(hands_played):
    hands_val = max(0, int(hands_played))
    pct = max(0, min(hands_val, 2500)) / 25
    if hands_val <= 100:
        gradient = "linear-gradient(90deg, #7d8792 0%, #a9b3bd 100%)"
    elif hands_val <= 500:
        gradient = "linear-gradient(90deg, #2fd67b 0%, #17b26a 100%)"
    elif hands_val <= 1000:
        gradient = "linear-gradient(90deg, #37c3ff 0%, #2b7fff 100%)"
    else:
        gradient = "linear-gradient(90deg, #f07a42 0%, #ffcc4d 100%)"
    return f"""
        <div style="margin:-4px 0 10px 28px; padding-right:4px; display:flex; align-items:center; gap:8px;">
            <div style="flex:1; height:3px; border-radius:999px; background:rgba(255,255,255,0.08); overflow:hidden; box-shadow:inset 0 1px 2px rgba(0,0,0,0.45);">
                <div style="width:{pct:.1f}%; height:100%; border-radius:999px; background:{gradient}; box-shadow:0 0 10px rgba(255,255,255,0.14);"></div>
            </div>
            <div style="min-width:52px; text-align:right; font-size:9px; line-height:1; font-weight:800; color:rgba(180,190,205,0.78); white-space:nowrap;">{hands_val}/2500</div>
        </div>
    """

def generate_desktop_theme(bg_rad1, bg_rad2, shadow1, shadow2, shadow3, seat_rad, seat_border, seat_act_border, seat_act_shadow, anim_name, pulse_shadow1, pulse_shadow2, text_color, badge_bg, bar_fill, card_bg, card_border, rng_bg, hero_panel_bg, hero_panel_border):
    return f"""<style>
    .game-area {{ background: radial-gradient(ellipse 50% 38% at 50% 44%, {bg_rad1} 0%, transparent 68%), radial-gradient(ellipse 90% 80% at 50% 50%, {bg_rad2}) !important; box-shadow: 0 0 0 12px {shadow1}, 0 0 0 20px {shadow2}, 0 0 0 26px {shadow3}, 0 0 50px 8px rgba(0,0,0,0.95), inset 0 2px 20px rgba(255,255,255,0.03) !important; }}
    .game-area::before {{ background: repeating-linear-gradient(45deg, rgba(255,255,255,0.008) 0px, rgba(255,255,255,0.008) 1px, transparent 1px, transparent 10px), repeating-linear-gradient(-45deg, rgba(255,255,255,0.008) 0px, rgba(255,255,255,0.008) 1px, transparent 1px, transparent 10px) !important; }}
    .game-area::after {{ border: 1px solid rgba(255,255,255,0.04) !important; }}
    .seat::before {{ background: radial-gradient(circle at 38% 30%, {seat_rad}) !important; border: 2px solid {seat_border} !important; box-shadow: 0 0 0 3px rgba(0,0,0,0.6), inset 0 1px 2px rgba(255,255,255,0.04) !important; }}
    .seat::after {{ background: rgba(255,255,255,0.06) !important; box-shadow: 0 8px 0 rgba(255,255,255,0.04) !important; }}
    .seat-active::before {{ border-color: {seat_act_border} !important; box-shadow: 0 0 0 3px rgba(0,0,0,0.6), 0 0 15px {seat_act_shadow} !important; animation: {anim_name} 3s ease-in-out infinite !important; }}
    @keyframes {anim_name} {{ 0%,100% {{ box-shadow: 0 0 0 3px rgba(0,0,0,0.6), 0 0 10px {pulse_shadow1}; }} 50% {{ box-shadow: 0 0 0 3px rgba(0,0,0,0.6), 0 0 25px {pulse_shadow2}; }} }}
    .seat-label {{ color: {text_color} !important; }}
    .info-spot {{ color: {text_color} !important; }}
    .mastery-badge {{ background: {badge_bg} !important; border: 1px solid {seat_border} !important; color: {text_color} !important; }}
    .mastery-bar-fill {{ background: {bar_fill} !important; }}
    .hands-left {{ color: {text_color} !important; opacity: 0.8; }}
    .floating-reward {{ color: {text_color} !important; }}
    .hero-panel {{ background: {hero_panel_bg} !important; border: 2px solid {hero_panel_border} !important; box-shadow: 0 0 20px {rng_bg} !important; }}
    .rng-desktop {{ color: {text_color} !important; background: {rng_bg} !important; border: 1.5px solid {seat_border} !important; }}
    .card {{ background: {card_bg} !important; border: 1px solid {card_border} !important; }}
    </style>"""

def show():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800;900&family=Roboto:wght@500;700;900&display=swap');

        /* БАЗОВЫЕ НАСТРОЙКИ ДЕСКТОПА */
        .stApp { background-color: #0b0c10; color: #e9ecef; }
        .block-container { padding-top: 4.5rem !important; max-width: 1400px !important; }
        
        /* СТОЛ ДЛЯ ДЕСКТОПА (ШИРОКИЙ ОВАЛ) */
        .game-area { position: relative; width: 100%; max-width: 860px; height: 380px; margin: 40px auto 50px auto !important; border-radius: 190px; transition: background 0.5s, box-shadow 0.15s ease-in-out, border-color 0.15s ease-in-out; overflow: visible; }
        .game-area::before { content: ''; position: absolute; inset: 0; border-radius: 190px; pointer-events: none; z-index: 0; }
        .game-area::after { content: ''; position: absolute; inset: 15px; border-radius: 175px; pointer-events: none; z-index: 0; }
        
        /* СВЕЧЕНИЕ ПРИ ОТВЕТАХ ДЛЯ ДЕСКТОПА */
        .game-area.table-glow-correct {
            box-shadow: 0 0 0 12px #198754, 0 0 40px rgba(25,135,84,0.8), inset 0 0 25px rgba(25,135,84,0.5) !important;
            border-color: #198754 !important;
        }
        .game-area.table-glow-correct::after {
            border-color: rgba(25,135,84,0.55) !important;
            box-shadow: inset 0 0 18px rgba(25,135,84,0.35) !important;
        }
        .game-area.table-glow-incorrect {
            box-shadow: 0 0 0 12px #dc3545, 0 0 40px rgba(220,53,69,0.8), inset 0 0 25px rgba(220,53,69,0.5) !important;
            border-color: #dc3545 !important;
        }
        .game-area.table-glow-incorrect::after {
            border-color: rgba(220,53,69,0.55) !important;
            box-shadow: inset 0 0 18px rgba(220,53,69,0.35) !important;
        }
        
        /* СКРЫВАЕМ SVG ГЕРБЫ ИЗ СТАРОЙ ВЕРСИИ */
        .glass-shatter, .mastery-glow, .crest-left, .crest-right { display: none !important; }

        /* ИНФОБЛОК СТОЛА */
        .table-info { position: absolute; top: 40%; width: 100%; text-align: center; pointer-events: none; z-index: 15; display: flex; flex-direction: column; align-items: center; gap: 5px; }
        .info-spot { font-size: 20px; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; z-index: 30; position: relative; text-shadow: 0 1px 4px rgba(0,0,0,0.95); }
        .info-src { display: none; }
        .mastery-badge { display: inline-flex; align-items: center; gap: 4px; border-radius: 20px; padding: 3px 12px; font-size: 11px; font-weight: 700; letter-spacing: 0.05em; }
        .mastery-bar-bg { width: 80px; height: 3px; background: rgba(255,255,255,0.07); border-radius: 3px; overflow: hidden; margin-top: 2px; }
        .mastery-bar-fill { height: 100%; border-radius: 3px; }
        .hands-left { font-size: 11px; letter-spacing: 0.06em; margin-top: 2px; }

        /* ИГРОКИ (SEATS) */
        .seat { position: absolute; width: 65px; height: 65px; display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 20; gap: 3px; }
        .seat::before { content: ''; display: block; position: absolute; inset: 0; border-radius: 50%; z-index: -1; }
        .seat::after { content: ''; position: absolute; top: 12px; left: 50%; transform: translateX(-50%); width: 20px; height: 20px; border-radius: 50%; background: rgba(255,255,255,0.07); box-shadow: 0 8px 0 rgba(255,255,255,0.05); pointer-events: none; }
        .seat-folded::before { border-color: rgba(80,80,80,0.15) !important; opacity: 0.6 !important; box-shadow: none !important; animation: none !important; }
        .seat-folded::after { opacity: 0.5 !important; }
        .seat-folded .opp-cards-desk { opacity: 0.5 !important; }
        .seat-label { font-size: 10px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; margin-bottom: 5px; text-shadow: 0 1px 3px rgba(0,0,0,0.9); }

        /* КАРТЫ ОППОНЕНТОВ ДЕСКТОП */
        .opp-cards-desk { position: absolute; top: -15px; display: flex; align-items: flex-end; z-index: 20; }
        .opp-card-desk { width: 22px; height: 32px; border-radius: 4px; position: relative; background: repeating-linear-gradient(45deg, rgba(15,70,185,0.95) 0px, rgba(15,70,185,0.95) 2px, rgba(8,44,130,0.95) 2px, rgba(8,44,130,0.95) 6px) !important; border: 1px solid rgba(80,140,255,0.3) !important; box-shadow: 0 2px 5px rgba(0,0,0,0.8), inset 0 0 0 1px rgba(255,255,255,0.06) !important; }
        .opp-card-desk::before { content: ''; position: absolute; inset: 2px; border-radius: 2px; border: 1px solid rgba(80,140,255,0.15) !important; }
        .opp-card-desk.right { margin-left: -8px; transform: rotate(10deg) translateY(2px); z-index: -1 !important; }

        /* ДИЛЕР И ФИШКИ */
        .dealer-button { position: absolute; z-index: 35; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: 900; color: #120700; background: radial-gradient(circle at 38% 30%, #ffd84a, #c88408) !important; border: 1.5px solid rgba(255,255,255,0.35) !important; box-shadow: 0 0 0 2px rgba(0,0,0,0.7), 0 2px 10px rgba(200,132,8,0.7), inset 0 1px 3px rgba(255,255,255,0.55) !important; }
        .chip-container { position: absolute; z-index: 22; display: flex; flex-direction: column; align-items: center; gap: 3px; pointer-events: none; }
        .poker-chip, .chip-3bet, .chip-4bet { width: 22px; height: 22px; border-radius: 50%; position: relative; background: repeating-conic-gradient(rgba(255,255,255,0.13) 0deg 18deg, transparent 18deg 36deg), radial-gradient(circle at 36% 30%, #1e3a8a, #0c1844) !important; border: 2px solid rgba(255,255,255,0.22) !important; box-shadow: 0 0 0 1.5px rgba(0,0,0,0.7), 0 2px 5px rgba(0,0,0,0.8), inset 0 1px 2px rgba(255,255,255,0.2) !important; }
        .chip-3bet { background: radial-gradient(circle at 36% 30%, #ff5722, #9e3211) !important; }
        .chip-4bet { background: repeating-conic-gradient(rgba(255,255,255,0.15) 0deg 18deg, transparent 18deg 36deg), radial-gradient(circle at 36% 30%, #68158e, #3F055B) !important; }
        .poker-chip::before, .chip-3bet::before, .chip-4bet::before { content: ''; position: absolute; inset: 4px; border-radius: 50%; border: 1px solid rgba(255,255,255,0.12); }
        .poker-chip::after, .chip-3bet::after, .chip-4bet::after { content: ''; position: absolute; top: 2px; left: 2px; width: 8px; height: 5px; border-radius: 50%; background: rgba(255,255,255,0.22); filter: blur(1px); }
        .bet-txt { font-size: 13px; font-weight: 700; color: rgba(255,235,190,0.9); text-shadow: 0 0 5px rgba(255,195,40,0.5), 0 1px 3px rgba(0,0,0,0.98); letter-spacing: 0.03em; white-space: nowrap; margin-top: -3px; }

        /* HERO PANEL */
        .hero-panel { position: absolute; bottom: -80px; left: 50%; transform: translateX(-50%); z-index: 30; display: flex; align-items: flex-start; gap: 10px; padding: 10px 20px; border-radius: 16px; transition: all 0.5s ease; }
        .hero-label { position: absolute; top: -10px; left: 50%; transform: translateX(-50%); color: #ffc107; font-weight: 900; font-size: 11px; letter-spacing: 0.1em; text-shadow: 0 1px 3px #000; background: #111; padding: 2px 8px; border-radius: 8px; border: 1px solid #444; }
        .card { width: 58px; height: 84px; border-radius: 8px; position: relative; box-shadow: 0 0 0 1px rgba(0,0,0,0.2), 0 -6px 16px rgba(0,0,0,0.7), 0 -12px 30px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,1); display: flex; flex-direction: column; align-items: flex-start; overflow: hidden; }
        .card::after { content: ''; position: absolute; top: 0; left: 0; width: 60%; height: 45%; background: linear-gradient(135deg, rgba(255,255,255,0.45) 0%, transparent 100%); pointer-events: none; border-radius: 8px 0 0 0; }
        .tl { padding: 4px 0 0 5px; font-size: 18px; font-weight: 900; line-height: 0.9; letter-spacing: -0.04em; z-index: 2; position: relative; font-family: Arial, sans-serif !important; }
        .cent { position: absolute; top: 55%; left: 50%; transform: translate(-50%,-50%); font-size: 30px; opacity: 1; line-height: 1; z-index: 2; font-family: Arial, sans-serif !important; }
        .suit-red   { color: #c00a0a !important; }
        .suit-black { color: #0a0a0a !important; }
        .suit-blue  { color: #0056b3 !important; }
        .suit-green { color: #198754 !important; }
        .rng-desktop { position: absolute; right: -55px; bottom: 15px; width: 34px; height: 34px; border-radius: 50%; font-weight: bold; font-size: 14px; display: flex; align-items: center; justify-content: center; z-index: 40; box-shadow: 0 2px 8px rgba(0,0,0,0.6); }

        /* CARBON NOIR STATS HEADER */
        .cn-mob-header { margin-top: -35px; margin-bottom: 5px; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; -webkit-font-smoothing: antialiased; border-radius: 14px; overflow: hidden; position: relative; background: linear-gradient(165deg, rgba(18,22,28,0.92) 0%, rgba(8,10,14,0.96) 100%); border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 1px 0 rgba(255,255,255,0.06) inset, 0 8px 32px rgba(0,0,0,0.55), 0 0 0 1px rgba(0,0,0,0.4); backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px); max-width: 860px; margin: 0 auto 10px auto; }
        .cn-mob-header::before { content: ''; position: absolute; inset: 0; border-radius: 14px; pointer-events: none; background: linear-gradient(125deg, rgba(255,255,255,0.07) 0%, transparent 42%, transparent 58%, rgba(255,255,255,0.03) 100%); z-index: 0; }
        .cn-mob-wr-track { height: 3px; width: 100%; background: rgba(0,0,0,0.45); position: relative; z-index: 1; }
        .cn-mob-wr-fill { height: 100%; transition: width 0.35s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 0 0 12px currentColor; }
        .cn-mob-inner { position: relative; z-index: 1; padding: 8px 10px 9px; }
        .cn-mob-row1 { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 6px; }
        .cn-mob-rank { font-size: 11px; font-weight: 800; letter-spacing: 0.04em; text-transform: uppercase; color: rgba(255,214,120,0.95); text-shadow: 0 0 20px rgba(255,200,80,0.25); line-height: 1.15; }
        .cn-mob-xp-meta { font-size: 9px; font-weight: 700; font-variant-numeric: tabular-nums; color: rgba(180,190,205,0.85); white-space: nowrap; letter-spacing: 0.02em; }
        .cn-mob-xp-bar-wrap { flex: 1; min-width: 0; margin-top: 3px; }
        .cn-mob-xp-bar-bg { height: 4px; border-radius: 4px; background: rgba(0,0,0,0.5); box-shadow: inset 0 1px 3px rgba(0,0,0,0.6); overflow: hidden; }
        .cn-mob-xp-bar-fill { height: 100%; border-radius: 4px; background: linear-gradient(90deg, #1a7a4a, #2ee88a); box-shadow: 0 0 10px rgba(46,232,138,0.45); transition: width 0.35s cubic-bezier(0.4, 0, 0.2, 1); }
        .cn-mob-row2 { display: flex; align-items: stretch; justify-content: space-between; gap: 6px; margin-top: 2px; }
        .cn-mob-stat { flex: 1; min-width: 0; }
        .cn-mob-stat-label { font-size: 8px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: rgba(140,150,165,0.75); margin-bottom: 1px; }
        .cn-mob-stat-val { font-size: 13px; font-weight: 800; font-variant-numeric: tabular-nums; letter-spacing: -0.02em; line-height: 1.1; }
        .cn-mob-stat-val.light { color: rgba(245,248,252,0.98); }
        .cn-mob-combo-wrap { flex: 1.15; display: flex; justify-content: center; align-items: center; min-width: 0; position: relative; }
        .cn-mob-combo-pill { display: inline-flex; align-items: center; justify-content: center; gap: 4px; padding: 3px 11px 3px 9px; border-radius: 999px; background: linear-gradient(145deg, rgba(255,255,255,0.09) 0%, rgba(255,255,255,0.02) 100%); border: 1px solid rgba(255,255,255,0.12); box-shadow: 0 1px 0 rgba(255,255,255,0.08) inset, 0 4px 16px rgba(0,0,0,0.35); }
        .cn-mob-combo-fire { font-size: 14px; font-weight: 900; color: #fff; text-shadow: 0 0 18px rgba(255,120,40,0.55); letter-spacing: -0.03em; }
        .cn-mob-shield { font-size: 11px; margin-left: 2px; font-weight: 800; color: rgba(120,230,255,0.95); filter: drop-shadow(0 0 6px rgba(0,200,255,0.55)); align-items: center; gap: 2px; }

        /* ПЕЧАТЬ BOT ДЛЯ 1000+ КОМБО */
        .bot-stamp { position: absolute; right: -40px; top: -10px; color: #dc3545; font-size: 14px; font-weight: 900; letter-spacing: 0.15em; border: 2px solid #dc3545; padding: 2px 6px; border-radius: 4px; transform: rotate(-15deg); font-family: 'Courier New', Courier, monospace; text-shadow: 0 0 5px rgba(220,53,69,0.6); box-shadow: 0 0 10px rgba(220,53,69,0.3), inset 0 0 5px rgba(220,53,69,0.3); pointer-events: none; opacity: 0.9; z-index: 50; animation: stamp-appear 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards; }
        @keyframes stamp-appear { 0% { transform: scale(2) rotate(-30deg); opacity: 0; } 100% { transform: scale(1) rotate(-15deg); opacity: 0.9; } }

        /* RAGE BAR NEON */
        .rage-bar-container { width: 100%; max-width: 860px; margin: 5px auto 45px auto !important; height: 26px; border-radius: 999px; position: relative; display: flex; align-items: stretch; padding: 3px; background: linear-gradient(180deg, rgba(12,14,20,0.95) 0%, rgba(6,8,12,0.98) 100%); border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 0 0 1px rgba(0,0,0,0.5), 0 4px 20px rgba(0,0,0,0.55), inset 0 2px 6px rgba(0,0,0,0.65), inset 0 -1px 0 rgba(255,255,255,0.05); overflow: hidden; }
        .rage-bar-container::before { content: ''; position: absolute; inset: 0; border-radius: inherit; pointer-events: none; background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.04) 50%, transparent 100%); z-index: 3; }
        .rage-bar-fill { height: 100%; border-radius: 999px; transition: width 0.35s cubic-bezier(0.4, 0, 0.2, 1); position: relative; overflow: hidden; min-width: 0; box-shadow: inset 0 2px 8px rgba(255,255,255,0.35), inset 0 -3px 8px rgba(0,0,0,0.45), 0 0 20px rgba(255,255,255,0.12); }
        .rage-bar-fill::before, .rage-bar-fill::after { content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background-image: radial-gradient(circle, rgba(255,255,255,0.85) 1px, transparent 2px), radial-gradient(circle, rgba(255,255,255,0.45) 2px, transparent 3px), radial-gradient(circle, rgba(255,255,255,0.35) 1px, transparent 2px); z-index: 1; pointer-events: none; }
        .rage-bar-fill::before { background-size: 18px 22px, 32px 36px, 14px 18px; animation: bubbleRise1 1.15s infinite linear; opacity: 0.85; }
        .rage-bar-fill::after { background-size: 22px 28px, 40px 46px, 20px 24px; animation: bubbleRise2 1.65s infinite linear; opacity: 0.45; }
        @keyframes bubbleRise1 { 0% { background-position: 0px 22px, 0px 36px, 0px 18px; } 50% { background-position: 5px 11px, -5px 18px, 3px 9px; } 100% { background-position: 0px 0px, 0px 0px, 0px 0px; } }
        @keyframes bubbleRise2 { 0% { background-position: 0px 28px, 0px 46px, 0px 24px; } 50% { background-position: -6px 14px, 6px 22px, -4px 12px; } 100% { background-position: 0px 0px, 0px 0px, 0px 0px; } }
        .rage-labels { position: absolute; left: 0; right: 0; top: 50%; transform: translateY(-50%); display: flex; justify-content: space-between; align-items: center; padding: 0 14px; pointer-events: none; z-index: 4; font-family: 'Inter', system-ui, sans-serif; font-weight: 800; font-size: 11px; font-variant-numeric: tabular-nums; letter-spacing: 0.02em; color: rgba(255,255,255,0.98); text-shadow: 0 1px 2px rgba(0,0,0,0.95), 0 0 12px rgba(0,0,0,0.8), 0 0 1px rgba(0,0,0,1); }
        .rage-pulse { animation: ragePulseNeon 0.45s ease-in-out infinite alternate; }
        @keyframes ragePulseNeon { 0% { filter: brightness(1) saturate(1); box-shadow: inset 0 2px 8px rgba(255,255,255,0.3), 0 0 8px rgba(255,60,80,0.35); } 100% { filter: brightness(1.15) saturate(1.2); box-shadow: inset 0 2px 12px rgba(255,255,255,0.5), 0 0 22px rgba(255,80,100,0.65), 0 0 40px rgba(255,40,60,0.25); } }
        .rage-flash { animation: rageTubeFlash 0.65s ease-out; }
        @keyframes rageTubeFlash { 0% { box-shadow: 0 0 0 1px rgba(255,255,255,0.9), 0 0 40px rgba(255,255,255,0.8), inset 0 0 30px rgba(255,255,255,0.5); border-color: rgba(255,255,255,0.65); } 100% { box-shadow: 0 4px 20px rgba(0,0,0,0.55), inset 0 2px 6px rgba(0,0,0,0.65); border-color: rgba(255,255,255,0.1); } }

        /* COMBO GLOWS */
        .combo-glow-5 { border-color: #0dcaf0 !important; box-shadow: 0 0 10px rgba(13, 202, 240, 0.4), 0 4px 15px rgba(0,0,0,0.8) !important; }
        .combo-glow-10 { border-color: #ffc107 !important; box-shadow: 0 0 15px rgba(255, 193, 7, 0.5), 0 4px 15px rgba(0,0,0,0.8) !important; }
        .combo-glow-25 { border-color: #fd7e14 !important; box-shadow: 0 0 20px rgba(253, 126, 20, 0.6), 0 4px 15px rgba(0,0,0,0.8) !important; animation: pulse-slow 2s infinite; }
        .combo-glow-50 { border-color: #dc3545 !important; box-shadow: 0 0 30px rgba(220, 53, 69, 0.7), 0 4px 15px rgba(0,0,0,0.8) !important; animation: pulse-menace 1.5s infinite; }
        .combo-glow-100 { border-color: #6f42c1 !important; box-shadow: 0 0 40px rgba(111, 66, 193, 0.8), 0 4px 15px rgba(0,0,0,0.8) !important; animation: pulse-neon 1s infinite; }
        .combo-glow-200 { border-color: #00e5ff !important; box-shadow: 0 0 50px rgba(0, 229, 255, 0.8), 0 4px 15px rgba(0,0,0,0.8) !important; animation: pulse-plasma 1s infinite alternate; }
        .combo-glow-500 { border-color: #ff00ff !important; box-shadow: 0 0 60px rgba(255, 0, 255, 0.9), 0 4px 15px rgba(0,0,0,0.8) !important; animation: pulse-matrix 0.8s infinite alternate; }
        .combo-glow-1000 { border-color: #00ff00 !important; box-shadow: 0 0 80px rgba(0, 255, 0, 1.0), 0 4px 15px rgba(0,0,0,0.8) !important; animation: pulse-god 0.5s infinite alternate; }
        
        .rng-hint-box { text-align: center; color: #888; font-size: 13px; font-family: monospace; margin-top: 60px; margin-bottom: 10px; background: #2b2b2b; padding: 5px; border-radius: 6px; border: 1px solid #444; width: 100%; }
        
        .floating-reward { position: absolute; top: -38px; left: 50%; transform: translateX(-50%); font-size: 18px; font-weight: 900; text-shadow: 0px 2px 5px rgba(0,0,0,0.9), 0px 0px 2px #000; z-index: 100; pointer-events: none; animation: float-reward 1.2s ease-out forwards; }
        @keyframes float-reward { 0% { opacity: 1; transform: translate(-50%, 0) scale(0.8); } 20% { opacity: 1; transform: translate(-50%, -15px) scale(1.2); } 100% { opacity: 0; transform: translate(-50%, -50px) scale(1); } }

        /* КНОПКИ ДЕЙСТВИЙ (АДАПТИВНО) */
        div[data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: row !important; width: 100% !important; gap: 10px !important; padding: 0 5px !important; }
        div[data-testid="column"], div[data-testid="stColumn"] { flex: 1 1 0px !important; width: 100% !important; min-width: 0 !important; margin-bottom: 0 !important; }
        div[data-testid="stButton"] { width: 100% !important; padding-bottom: 15px !important; }
        
        div[data-testid="stButton"] button {
            width: 100% !important; height: 65px !important; padding: 0 !important; border: none !important; border-radius: 12px !important;
            transition: all 0.05s cubic-bezier(0.2, 0, 0, 1) !important; cursor: pointer !important; position: relative !important; overflow: hidden !important; display: flex !important; align-items: center !important; justify-content: center !important;
        }
        div[data-testid="stButton"] button:active { transform: translateY(4px) scale(0.95) !important; filter: brightness(1.3) !important; }
        div[data-testid="stButton"] button::after { content: '' !important; position: absolute !important; top: 0 !important; left: 0 !important; right: 0 !important; height: 50% !important; background: linear-gradient(180deg, rgba(255,255,255,0.07) 0%, transparent 100%) !important; border-radius: 12px 12px 0 0 !important; pointer-events: none !important; }
        div[data-testid="stButton"] button p { font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', sans-serif !important; font-size: 15px !important; font-weight: 900 !important; margin: 0 !important; letter-spacing: 0.12em !important; text-transform: uppercase !important; }
        </style>
    """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────
    # СЛОВАРЬ ДИЗАЙНОВ (THEMES ДЛЯ ДЕСКТОПА)
    # ─────────────────────────────────────────────────────────────────
    THEMES = {
        0: {
            "icon": "⚪", "name": "Sandbox",
            "css": generate_desktop_theme(
                "rgba(50,55,60,0.5)", "#202428 0%, #15181a 55%, #0a0b0d 100%", "#0e1012", "#16181b", "#0b0d0f", 
                "#1f2226 0%, #111316 60%, #08090a 100%", "rgba(140,150,160,0.18)", "rgba(160,170,180,0.55)", "rgba(160,170,180,0.28)",
                "r0-pulse", "rgba(160,170,180,0.22)", "rgba(160,170,180,0.42)", "rgba(150,160,170,0.6)", "rgba(150,160,170,0.08)", 
                "linear-gradient(90deg, #8b959e, #5b636a)", "#f8faff", "rgba(255,255,255,0.85)", "rgba(150,160,170,0.08)", "rgba(20,24,28,0.95)", "rgba(150,160,170,0.25)"
            )
        },
        1: {
            "icon": "🌱", "name": "Basic",
            "css": generate_desktop_theme(
                "rgba(30,55,38,0.5)", "#1a2e20 0%, #111e16 55%, #090e0b 100%", "#0e1410", "#182219", "#0b100d",
                "#1a2d21 0%, #0e1a12 60%, #080d0a 100%", "rgba(120,160,130,0.18)", "rgba(120,180,140,0.55)", "rgba(120,180,140,0.28)",
                "r1-pulse", "rgba(120,180,140,0.22)", "rgba(120,180,140,0.42)", "rgba(140,185,155,0.8)", "rgba(120,180,140,0.07)",
                "linear-gradient(90deg, #6ab880, #4a9060)", "#f8faff", "rgba(255,255,255,0.85)", "rgba(120,180,140,0.08)", "rgba(14,20,16,0.95)", "rgba(120,180,140,0.25)"
            )
        },
        2: {
            "icon": "💎", "name": "Solid",
            "css": generate_desktop_theme(
                "rgba(10,50,80,0.6)", "#0b3040 0%, #071e2e 58%, #030e18 100%", "#081420", "#0f2234", "#060e17",
                "#162840 0%, #0c1a28 60%, #060e18 100%", "rgba(60,130,200,0.22)", "rgba(60,160,255,0.78)", "rgba(60,160,255,0.42)",
                "r2-pulse", "rgba(60,160,255,0.34)", "rgba(60,160,255,0.62)", "rgba(100,170,220,0.8)", "rgba(60,130,200,0.09)",
                "linear-gradient(90deg, #3ab0ff, #1480d8)", "#f8faff", "rgba(255,255,255,0.85)", "rgba(60,130,200,0.09)", "rgba(8,20,32,0.95)", "rgba(60,130,200,0.28)"
            )
        },
        3: {
            "icon": "🔥", "name": "Unexploitable",
            "css": generate_desktop_theme(
                "rgba(90,18,28,0.65)", "#3a0d14 0%, #240810 58%, #0f0408 100%", "#1a080a", "#2e1014", "#12060a",
                "#3a1c10 0%, #221008 60%, #0f0804 100%", "rgba(180,110,40,0.28)", "rgba(210,150,50,0.88)", "rgba(210,150,50,0.48)",
                "r3-pulse", "rgba(210,150,50,0.4)", "rgba(220,165,60,0.68)", "rgba(200,140,60,0.8)", "rgba(180,110,40,0.09)",
                "linear-gradient(90deg, #d49030, #a86018)", "linear-gradient(145deg, #f5f0e8 0%, #ede5d4 100%)", "rgba(210,175,110,0.7)", "rgba(180,110,40,0.09)", "rgba(26,8,10,0.95)", "rgba(180,110,40,0.3)"
            )
        },
        4: {
            "icon": "⚡", "name": "Elite",
            "css": generate_desktop_theme(
                "rgba(55,20,90,0.6)", "#1e0d30 0%, #130820 58%, #07030f 100%", "#120818", "#1e1028", "#0d0614",
                "#2a1840 0%, #180e28 60%, #0a0812 100%", "rgba(160,130,220,0.28)", "rgba(190,160,255,0.88)", "rgba(170,130,255,0.52)",
                "r4-pulse", "rgba(170,130,255,0.42)", "rgba(190,150,255,0.7)", "rgba(170,145,230,0.8)", "rgba(140,110,220,0.09)",
                "linear-gradient(90deg, #a070ff, #7040d8)", "linear-gradient(150deg, #2a2a32 0%, #1e1e26 100%)", "rgba(200,190,230,0.3)", "rgba(140,110,220,0.09)", "rgba(18,8,24,0.95)", "rgba(140,110,220,0.3)"
            )
        },
        5: {
            "icon": "☢️", "name": "Solver",
            "css": generate_desktop_theme(
                "rgba(60,50,10,0.5)", "#141410 0%, #0c0c09 55%, #050504 100%", "#0f0f0c", "#1c1c16", "#0a0a08",
                "#1c1a10 0%, #111008 60%, #080806 100%", "rgba(190,158,50,0.3)", "rgba(220,188,70,0.95)", "rgba(220,188,70,0.58)",
                "r5-pulse", "rgba(220,188,70,0.46)", "rgba(240,205,80,0.78)", "rgba(210,178,55,0.8)", "rgba(190,158,50,0.1)",
                "linear-gradient(90deg, #d4a820, #a07810)", "linear-gradient(150deg, #1a1a18 0%, #111110 100%)", "rgba(210,180,70,0.38)", "rgba(190,158,50,0.1)", "rgba(15,15,12,0.95)", "rgba(190,158,50,0.3)"
            )
        }
    }

    try:
        if hasattr(utils, 'load_ranges'): ranges_db = utils.load_ranges()
        elif hasattr(utils, 'load_preflop_ranges'): ranges_db = utils.load_preflop_ranges()
        else: st.error("Функция загрузки ренджей не найдена в poker_utils.py"); return
    except Exception as e:
        st.error(f"Ошибка загрузки базы: {e}")
        return

    if not ranges_db: st.error("Ranges database is empty."); return
    
    scenario_map = {}
    for src, sc_dict in ranges_db.items():
        for sc, sp_dict in sc_dict.items():
            if sc not in scenario_map: scenario_map[sc] = []
            for sp in sp_dict.keys():
                scenario_map[sc].append((sp, f"{src}|{sc}|{sp}"))
    
    all_scenarios = sorted(list(scenario_map.keys()))

    with st.sidebar:
        st.header("⚙️ Settings")
        dv_btn = st.radio("Interface Mode", ["📱 Mobile", "💻 Desktop"], index=0 if st.session_state.actual_view_type=="📱 Mobile" else 1)
        if dv_btn != st.session_state.actual_view_type:
            st.session_state.actual_view_type = dv_btn
            st.rerun()
            
        st.markdown("---")
        saved = utils.load_user_settings()
        filter_mastery = utils.load_user_stats().get("spot_mastery", {})
        if not isinstance(filter_mastery, dict):
            filter_mastery = {}
        
        saved_sc = [s for s in saved.get("scenarios", []) if s in all_scenarios]
        sel_sc = st.multiselect("Scenario", all_scenarios, default=saved_sc if saved_sc else (all_scenarios[:1] if all_scenarios else []))
        
        sel_spots_keys = []
        if sel_sc:
            st.markdown("**Spots for training:**")
            saved_spots = saved.get("spots", [])
            for sc in sel_sc:
                st.markdown(f"<div style='color:#ffc107; font-size:14px; font-weight:bold; margin-top:8px;'>{sc}</div>", unsafe_allow_html=True)
                for sp_name, sp_key in scenario_map[sc]:
                    is_checked = (sp_key in saved_spots) if "spots" in saved else True
                    if st.checkbox(sp_name, value=is_checked, key=f"d_chk_{sp_key}"):
                        sel_spots_keys.append(sp_key)
                    hands_played = get_spot_training_hands(sp_key, filter_mastery)
                    st.markdown(build_spot_training_progress_html(hands_played), unsafe_allow_html=True)
        
        if st.button("🚀 Apply Settings", use_container_width=True):
            saved["scenarios"] = sel_sc
            saved["spots"] = sel_spots_keys
            utils.save_user_settings(saved)
            st.session_state.hand = None
            st.rerun()

    pool = sel_spots_keys
    if not pool:
        st.warning("⚠️ No spots selected. Check menu on the left.")
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
            st.toast(str(msg), icon="🔥" if "Combo" in str(msg) else "🎯")
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
    table_size = setup.get("table_size", 6)

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
        mastery_dict = stats_data.get("spot_mastery", {})
        if isinstance(mastery_dict, dict):
            spot_data_mastery = mastery_dict.get(st.session_state.current_spot_key, {})
        else:
            spot_data_mastery = {}
        mastery = utils.get_spot_mastery_info(spot_data_mastery)
    except Exception:
        mastery = {"rank": 0, "name": "Sandbox", "icon": "⚪", "color": "#6c757d", "is_rusty": False, "prog_pct": 0, "total": 0, "next": 100, "svg": ""}
        
    m_rust = mastery.get("is_rusty", False)
    m_pct = mastery.get("prog_pct", 0)
    m_total = mastery.get("total", 0)
    m_next = mastery.get("next", 100)
    m_rank = mastery.get("rank", 0)
    
    if m_rank >= 5: hands_left_text = "MAX RANK"
    else: hands_left_text = f"Remaining: {max(0, m_next - m_total)} hands"

    visual_rank = m_rank if m_rank >= 0 else 0
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

    is_flashing_correct = st.session_state.get("flash_correct", False)
    table_status_class = ""
    if is_flashing_correct:
        table_status_class = "table-glow-correct"
    elif st.session_state.last_error:
        table_status_class = "table-glow-incorrect"

    tiers = [(0, 1.0), (10, 1.5), (25, 2.0), (50, 3.0), (100, 4.0), (250, 5.0), (500, 10.0), (1000, 25.0)]
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
    elif curr_mult == 10.0: grad = "linear-gradient(90deg, #6f42c1, #ff00ff)"
    else: grad = "linear-gradient(90deg, #ff00ff, #00ff00)" # ЯДОВИТО-ЗЕЛЕНЫЙ ДЛЯ 1000+

    progress_pct = int((stats_data.get("xp", 0) / next_xp) * 100) if next_xp != "MAX" else 100

    shield_display = (
        f'<span class="cn-mob-shield" style="'
        f'display:{"inline-flex" if st.session_state.shields > 0 else "none"};'
        f'">🛡️{st.session_state.shields}</span>'
    )
    
    # ДОБАВЛЯЕМ ПЕЧАТЬ [BOT]
    bot_stamp = '<div class="bot-stamp">BOT</div>' if c >= 1000 else ''

    combo_badge = (
        f'<div class="cn-mob-combo-wrap">'
        f'<div class="cn-mob-combo-pill">'
        f'<span class="cn-mob-combo-fire">🔥{c}</span>'
        f'{shield_display}'
        f'{bot_stamp}'
        f'</div></div>'
    )

    header_html = (
        f'<div class="cn-mob-header">'
        f'<div class="cn-mob-wr-track">'
        f'<div class="cn-mob-wr-fill" style="width:{wr if sh > 0 else 100}%; background:{wr_color if sh > 0 else "#2a2a2a"}; box-shadow:0 0 8px {wr_color if sh > 0 else "transparent"};"></div></div>'
        f'<div class="cn-mob-inner">'
        f'<div class="cn-mob-row1">'
        f'<div style="flex:1;min-width:0;">'
        f'<div class="cn-mob-rank">{rank_name}</div>'
        f'<div class="cn-mob-xp-bar-wrap"><div class="cn-mob-xp-bar-bg"><div class="cn-mob-xp-bar-fill" style="width:{progress_pct}%;"></div></div></div>'
        f'</div>'
        f'<div class="cn-mob-xp-meta">${stats_data.get("xp", 0)} <span style="color:rgba(255,255,255,0.15);margin:0 2px;">/</span> ${next_xp}</div>'
        f'</div>'
        f'<div class="cn-mob-row2">'
        f'<div class="cn-mob-stat">'
        f'<div class="cn-mob-stat-label">Winrate</div>'
        f'<div class="cn-mob-stat-val" style="color:{wr_color}; text-shadow:0 0 10px {wr_color}44;">{wr}%</div>'
        f'</div>'
        f'{combo_badge}'
        f'<div class="cn-mob-stat" style="text-align:right;">'
        f'<div class="cn-mob-stat-label">Hands</div>'
        f'<div class="cn-mob-stat-val light">{sh}</div>'
        f'</div>'
        f'</div></div></div>'
    )

    rage_bar_html = f"""
<div class="rage-bar-container {is_flashing}">
  <div class="rage-bar-fill {is_pulsing}" style="width: {rage_pct}%; background: {grad};"></div>
  <div class="rage-labels">
    <span>{lbl_left}</span>
    <span>{lbl_right}</span>
  </div>
</div>
"""

    anim_html = ""
    anim_reward = st.session_state.pop("anim_reward", None)
    if anim_reward is not None:
        if anim_reward > 0: a_color = "#00ff00"; a_text = f"+${anim_reward}"
        elif anim_reward < 0: a_color = "#ff0000"; a_text = f"-${abs(anim_reward)}"
        else: a_color = "#888"; a_text = "$0"
        anim_html = f'<div class="floating-reward" style="color: {a_color}">{a_text}</div>'

    col_center, col_right = st.columns([2.2, 1])

    with col_center:
        st.markdown(header_html, unsafe_allow_html=True)
        st.markdown(rage_bar_html, unsafe_allow_html=True)

        order = ["EP", "MP", "CO", "BTN", "SB", "BB"]
        try: hero_idx = order.index(hero_pos)
        except ValueError: hero_idx = 0
        rot = order[hero_idx:] + order[:hero_idx]

        def get_seat_style(idx):
            return {
                1: "bottom: 12%; left: -10px;", 
                2: "top: 12%; left: -10px;", 
                3: "top: -30px; left: 50%; transform: translateX(-50%);", 
                4: "top: 12%; right: -10px;", 
                5: "bottom: 12%; right: -10px;"
            }.get(idx, "")

        def get_chip_style(idx):
            return {
                0: "bottom: 15%; left: 50%; transform: translateX(-50%);", 
                1: "bottom: 25%; left: 12%;", 
                2: "top: 25%; left: 12%;",
                3: "top: 20%; left: 50%; transform: translateX(-50%);", 
                4: "top: 25%; right: 12%;", 
                5: "bottom: 25%; right: 12%;"
            }.get(idx, "")

        def get_btn_style(idx):
            return {
                0: "bottom: -15px; left: 50%; margin-left: -130px; z-index: 35;", 
                1: "bottom: 28%; left: 6%;", 
                2: "top: 10%; left: 8%;",
                3: "top: 8%; left: 55%;", 
                4: "top: 10%; right: 8%;", 
                5: "bottom: 28%; right: 6%;"
            }.get(idx, "")

        opp_html = ""; chips_html = ""

        if table_size == 2:
            villain_p = "BB" if hero_pos == "SB" else "SB"
            cls = "seat-active"
            cards = '<div class="opp-cards-desk"><div class="opp-card-desk"></div><div class="opp-card-desk right"></div></div>'
            ss = get_seat_style(3)
            opp_html += f'<div class="seat {cls}" style="{ss}">{cards}<span class="seat-label">{villain_p}</span></div>'
            
            cs = get_chip_style(3)
            bet_amount = bets_on_table.get(villain_p)
            if bet_amount is not None:
                bet_txt = f'<div class="bet-txt">{bet_amount}bb</div>'
                if bet_amount >= 15.0:
                    chips_html += f'<div class="chip-container" style="{cs}"><div class="chip-4bet"></div><div class="chip-4bet" style="margin-top:-13px;"></div><div class="chip-4bet" style="margin-top:-13px;"></div>{bet_txt}</div>'
                elif bet_amount <= 1.0:
                    if is_3bet_pot: chips_html += f'<div class="chip-container" style="{cs}"><div class="chip-3bet"></div>{bet_txt}</div>'
                    else: chips_html += f'<div class="chip-container" style="{cs}"><div class="poker-chip"></div>{bet_txt}</div>'
                else:
                    if is_3bet_pot: chips_html += f'<div class="chip-container" style="{cs}"><div class="chip-3bet"></div><div class="chip-3bet" style="margin-top:-13px;"></div>{bet_txt}</div>'
                    else: chips_html += f'<div class="chip-container" style="{cs}"><div class="poker-chip"></div><div class="poker-chip" style="margin-top:-13px;"></div>{bet_txt}</div>'
            
            if villain_p == btn_pos:
                bs = get_btn_style(3)
                chips_html += f'<div class="dealer-button" style="{bs}">D</div>'
        else:
            for i in range(1, 6):
                p = rot[i]
                has_cards = (p in cards_in_play)
                cls = "seat-active" if has_cards else "seat-folded"
                cards = '<div class="opp-cards-desk"><div class="opp-card-desk"></div><div class="opp-card-desk right"></div></div>' if has_cards else ""
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
                        else: chips_html += f'<div class="chip-container" style="{cs}"><div class="poker-chip"></div>{bet_txt}</div>'
                    else:
                        if is_3bet_pot: chips_html += f'<div class="chip-container" style="{cs}"><div class="chip-3bet"></div><div class="chip-3bet" style="margin-top:-13px;"></div>{bet_txt}</div>'
                        else: chips_html += f'<div class="chip-container" style="{cs}"><div class="poker-chip"></div><div class="poker-chip" style="margin-top:-13px;"></div>{bet_txt}</div>'
                
                if p == btn_pos:
                    bs = get_btn_style(i)
                    chips_html += f'<div class="dealer-button" style="{bs}">D</div>'

        hero_cs = get_chip_style(0)
        if display_hero_bet is not None: 
            bet_txt = f'<div class="bet-txt">{display_hero_bet}bb</div>'
            if display_hero_bet >= 15.0:
                chips_html += f'<div class="chip-container" style="{hero_cs}"><div class="chip-4bet"></div><div class="chip-4bet" style="margin-top:-13px;"></div><div class="chip-4bet" style="margin-top:-13px;"></div>{bet_txt}</div>'
            elif display_hero_bet <= 1.0:
                chips_html += f'<div class="chip-container" style="{hero_cs}"><div class="poker-chip"></div>{bet_txt}</div>'
            else:
                chips_html += f'<div class="chip-container" style="{hero_cs}"><div class="poker-chip"></div><div class="poker-chip" style="margin-top:-13px;"></div>{bet_txt}</div>'
            
        if rot[0] == btn_pos:
            hero_bs = get_btn_style(0)
            chips_html += f'<div class="dealer-button" style="{hero_bs}">D</div>'

        html = f'<div class="game-area {combo_cls} {table_status_class}"><div class="table-info"><div class="info-src">{sc}</div><div class="info-spot">{sp}</div><div class="mastery-badge rusty-{m_rust}">{m_icon} {m_name}</div><div class="mastery-bar-bg"><div class="mastery-bar-fill" style="width: {m_pct}%;"></div></div><div class="hands-left">{hands_left_text}</div></div>{opp_html}{chips_html}<div class="hero-panel">{anim_html}<div class="card"><div class="tl {c1}">{h_val[0]}<br>{s1}</div><div class="cent {c1}">{s1}</div></div><div class="card"><div class="tl {c2}">{h_val[1]}<br>{s2}</div><div class="cent {c2}">{s2}</div></div><div class="rng-desktop">{rng}</div></div></div>'
        
        st.markdown(html, unsafe_allow_html=True)

        if not st.session_state.last_error:
            if is_defense:
                st.markdown('<div class="rng-hint-box">📉 0..Freq → Action &nbsp;|&nbsp; 📈 Freq..100 → Fold</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="rng-hint-box">📉 0..Freq → Raise &nbsp;|&nbsp; 📈 Freq..100 → Fold</div>', unsafe_allow_html=True)

        def handle_action(action):
            corr = (correct_act == action)
            st.session_state.session_hands += 1
            
            c_old = st.session_state.combo
            old_mult = 1.0
            if c_old >= 1000: old_mult = 25.0
            elif c_old >= 500: old_mult = 10.0
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
                st.session_state.flash_correct = True
            else:
                st.session_state.flash_correct = False
                if st.session_state.shields > 0:
                    st.session_state.shields -= 1
                    st.session_state.last_error = True
                    shield_used = True
                    st.session_state.msg = f"🛡️ ЩИТ СЛОМАН! Защита от мисклика. GTO: {correct_act}"
                else:
                    st.session_state.combo = 0
                    st.session_state.last_error = True
                    st.session_state.msg = f"❌ WRONG! You chose {action}, but GTO is {correct_act}"
                
            c_new = st.session_state.combo
            new_mult = 1.0
            if c_new >= 1000: new_mult = 25.0
            elif c_new >= 500: new_mult = 10.0
            elif c_new >= 250: new_mult = 5.0
            elif c_new >= 100: new_mult = 4.0
            elif c_new >= 50: new_mult = 3.0
            elif c_new >= 25: new_mult = 2.0
            elif c_new >= 10: new_mult = 1.5

            if new_mult > old_mult:
                st.session_state.just_leveled_up = True

            try:
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

        if is_flashing_correct:
            time.sleep(0.5)
            st.session_state.flash_correct = False
            st.session_state.hand = None
            st.rerun()
        elif st.session_state.last_error:
            st.markdown(f'<div style="background:#dc3545; color:white; padding:12px; border-radius:12px; text-align:center; font-weight:bold; margin-bottom:15px; font-size:16px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);">{st.session_state.msg}</div>', unsafe_allow_html=True)
            
            st.markdown("""<style>
            div[data-testid="stButton"] button[kind="primary"] {
                background: linear-gradient(180deg, #1c3a55 0%, #102436 100%) !important;
                box-shadow: 0 4px 0 #081520, 0 6px 20px rgba(30,120,200,0.15), inset 0 1px 0 rgba(60,160,255,0.12), inset 0 0 0 1px rgba(40,130,220,0.14) !important;
                border: none !important; height: 65px !important; border-radius: 12px !important;
            }
            div[data-testid="stButton"] button[kind="primary"]:active {
                transform: translateY(3px) scale(0.95) !important;
                box-shadow: 0 1px 0 #081520, inset 0 1px 0 rgba(60,160,255,0.08) !important; filter: brightness(1.3) !important;
            }
            div[data-testid="stButton"] button[kind="primary"] p {
                color: rgba(80,180,255,0.95) !important; text-shadow: 0 0 12px rgba(50,160,240,0.4) !important; font-size: 15px !important; font-weight: 900 !important; letter-spacing: 0.12em !important; text-transform: uppercase !important;
            }
            </style>""", unsafe_allow_html=True)
            
            if st.button("UNDERSTOOD, NEXT", type="primary", use_container_width=True):
                st.session_state.last_error = False
                st.session_state.hand = None
                st.session_state.shield_break_anim = False
                st.rerun()

        else:
            if is_defense:
                st.markdown("""<style>
                /* ── FOLD ── */
                div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) button,
                div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(1) button {
                    background: linear-gradient(180deg, #252830 0%, #16181f 100%) !important;
                    box-shadow: 0 4px 0 #0c0d12, 0 6px 16px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.08), inset 0 0 0 1px rgba(255,255,255,0.06) !important;
                }
                div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) button:active,
                div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(1) button:active {
                    box-shadow: 0 1px 0 #0c0d12, inset 0 1px 0 rgba(255,255,255,0.05), 0 0 20px rgba(255,255,255,0.15) !important; filter: brightness(1.5) !important;
                }
                div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) button p,
                div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(1) button p { color: rgba(190,190,205,0.8) !important; }

                /* ── CALL ── */
                div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) button,
                div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) button {
                    background: linear-gradient(180deg, #0c3828 0%, #071e16 100%) !important;
                    box-shadow: 0 4px 0 #030f0b, 0 6px 20px rgba(0,180,80,0.12), inset 0 1px 0 rgba(0,230,110,0.12), inset 0 0 0 1px rgba(0,200,90,0.1) !important;
                }
                div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) button:active,
                div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) button:active {
                    box-shadow: 0 1px 0 #030f0b, inset 0 1px 0 rgba(0,200,90,0.08), 0 0 20px rgba(0,255,100,0.5) !important; filter: brightness(1.4) saturate(1.2) !important;
                }
                div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) button p,
                div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) button p { color: rgba(50,220,130,0.92) !important; text-shadow: 0 0 12px rgba(30,200,100,0.4) !important; }

                /* ── RAISE ── */
                div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3) button,
                div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(3) button {
                    background: linear-gradient(180deg, #4a0909 0%, #300505 100%) !important;
                    box-shadow: 0 4px 0 #1a0303, 0 6px 20px rgba(180,20,20,0.2), inset 0 1px 0 rgba(255,80,80,0.14), inset 0 0 0 1px rgba(200,30,30,0.18) !important;
                }
                div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3) button:active,
                div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(3) button:active {
                    box-shadow: 0 1px 0 #1a0303, inset 0 1px 0 rgba(255,80,80,0.1), 0 0 20px rgba(255,50,50,0.5) !important; filter: brightness(1.4) saturate(1.2) !important;
                }
                div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3) button p,
                div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(3) button p { color: rgba(255,90,90,0.95) !important; text-shadow: 0 0 14px rgba(220,50,50,0.5) !important; }
                </style>""", unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button("FOLD", key="f", use_container_width=True): handle_action("FOLD")
                with c2:
                    if st.button("CALL", key="c", use_container_width=True): handle_action("CALL")
                with c3:
                    if st.button("RAISE", key="r", use_container_width=True): handle_action("RAISE")
            else:
                st.markdown("""<style>
                /* ── FOLD ── */
                div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) button,
                div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(1) button {
                    background: linear-gradient(180deg, #252830 0%, #16181f 100%) !important;
                    box-shadow: 0 4px 0 #0c0d12, 0 6px 16px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.08), inset 0 0 0 1px rgba(255,255,255,0.06) !important;
                }
                div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) button:active,
                div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(1) button:active {
                    box-shadow: 0 1px 0 #0c0d12, inset 0 1px 0 rgba(255,255,255,0.05), 0 0 20px rgba(255,255,255,0.15) !important; filter: brightness(1.5) !important;
                }
                div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) button p,
                div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(1) button p { color: rgba(190,190,205,0.8) !important; }

                /* ── RAISE ── */
                div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) button,
                div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) button {
                    background: linear-gradient(180deg, #4a0909 0%, #300505 100%) !important;
                    box-shadow: 0 4px 0 #1a0303, 0 6px 20px rgba(180,20,20,0.2), inset 0 1px 0 rgba(255,80,80,0.14), inset 0 0 0 1px rgba(200,30,30,0.18) !important;
                }
                div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) button:active,
                div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) button:active {
                    box-shadow: 0 1px 0 #1a0303, inset 0 1px 0 rgba(255,80,80,0.1), 0 0 20px rgba(255,50,50,0.5) !important; filter: brightness(1.4) saturate(1.2) !important;
                }
                div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) button p,
                div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) button p { color: rgba(255,90,90,0.95) !important; text-shadow: 0 0 14px rgba(220,50,50,0.5) !important; }
                </style>""", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("FOLD", key="f", use_container_width=True): handle_action("FOLD")
                with c2:
                    if st.button("RAISE", key="r", use_container_width=True): handle_action("RAISE")

    with col_right:
        if not st.session_state.last_error:
            st.markdown(f"<div style='text-align:center;font-weight:bold;margin-bottom:10px;'>{sp}</div>", unsafe_allow_html=True)
            with st.expander("🫣 Peek Range", expanded=False):
                st.markdown(utils.render_range_matrix(data, st.session_state.hand), unsafe_allow_html=True)
