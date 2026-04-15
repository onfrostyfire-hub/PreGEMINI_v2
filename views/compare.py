import streamlit as st
import poker_utils as utils

def render_popover_selector(ranges_db, suffix, emoji):
    k_sc = f"sc_{suffix}"
    k_sp = f"sp_{suffix}"

    sc_map = {}
    for src, sc_dict in ranges_db.items():
        for sc, sp_dict in sc_dict.items():
            if sc not in sc_map: sc_map[sc] = []
            for sp in sp_dict.keys():
                sc_map[sc].append((sp, src))

    curr_sc = st.session_state.get(k_sc)
    curr_sp = st.session_state.get(k_sp)

    if curr_sp and curr_sc:
        short_sc = curr_sc.replace("Def vs 3bet", "Def3B").replace("Open Raise", "OR").replace("BB def vs PFR", "BB vs PFR")
        display_text = f"<div style='font-weight:900;font-size:10px;color:#ffc107;margin-bottom:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{emoji} {short_sc}</div><div style='font-size:9px;color:#aaa;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{curr_sp}</div>"
    else:
        display_text = f"<div style='color:#666;font-style:italic;font-size:10px;font-weight:bold;'>{emoji} Выбрать...</div>"

    st.markdown(display_text, unsafe_allow_html=True)

    with st.popover("⚙️", use_container_width=True):
        opts_sc = sorted(list(sc_map.keys()))
        idx_sc = opts_sc.index(curr_sc) if curr_sc in opts_sc else 0
        sc = st.selectbox("Сценарий", opts_sc, key=k_sc, index=idx_sc) if opts_sc else None

        opts_sp = [x[0] for x in sc_map[sc]] if sc else []
        idx_sp = opts_sp.index(curr_sp) if curr_sp in opts_sp else 0
        sp = st.selectbox("Спот", opts_sp, key=k_sp, index=idx_sp) if opts_sp else None

    if sc and sp:
        src = next((x[1] for x in sc_map[sc] if x[0] == sp), None)
        return ranges_db[src][sc][sp]
    return None

def show():
    st.markdown("""
        <style>
            /* Убираем отступы контейнера страницы */
            .block-container { 
                padding: 1rem 0.2rem 5rem 0.2rem !important; 
                max-width: 100% !important; 
                overflow-x: hidden !important; 
            }
            
            /* ЖЕСТКИЙ ФЛЕКСБОКС ДЛЯ МОБИЛКИ: две колонки ровно по 50% */
            div[data-testid="stHorizontalBlock"] {
                display: flex !important;
                flex-direction: row !important;
                flex-wrap: nowrap !important;
                gap: 4px !important;
                width: 100% !important;
                padding: 0 !important;
            }
            div[data-testid="column"] {
                width: 50% !important;
                flex: 1 1 50% !important;
                min-width: 0 !important;
                padding: 0 !important;
            }
            
            /* Коробка вокруг матрицы */
            .matrix-box { 
                border: 1px solid #333; 
                border-radius: 4px; 
                padding: 1px; 
                background: #0a0a0c; 
                margin-top: 2px; 
                width: 100%;
                overflow: hidden; 
                box-shadow: 0 2px 6px rgba(0,0,0,0.6);
            }
            
            /* ЛОМАЕМ СТРУКТУРУ РЕНДЕРА МАТРИЦЫ ИЗ poker_utils.py */
            /* 1. Убираем зазоры (gap) между картами, чтобы сэкономить место */
            .matrix-box > div:first-child {
                gap: 0px !important; 
                padding: 0px !important;
                border: none !important;
            }
            /* 2. Жестко ужимаем ячейки и шрифт внутри них */
            .matrix-box div[title] { 
                font-size: 5.5px !important; 
                font-weight: 800 !important; 
                letter-spacing: -0.5px !important;
                min-width: 0 !important;
                min-height: 0 !important;
                overflow: hidden !important;
                box-shadow: inset 0 0 0 0.5px rgba(0,0,0,0.3) !important; /* Визуальный разделитель вместо gap */
            }
            
            /* Ужимаем плашки статистики под матрицей (Raise/Call/Fold) */
            .matrix-box > div:last-child {
                gap: 2px !important;
                margin-top: 4px !important;
            }
            .matrix-box > div:last-child > div { 
                font-size: 7px !important; 
                padding: 2px 3px !important; 
                border-radius: 3px !important;
                letter-spacing: -0.2px !important;
                white-space: nowrap !important;
            }
            
            /* Микро-кнопки поповеров настроек */
            div[data-testid="stPopover"] {
                margin-top: -10px !important;
            }
            div[data-testid="stPopover"] button { 
                padding: 0px !important; 
                height: 22px !important; 
                min-height: 22px !important; 
                background: #1c1e22 !important; 
                border-color: #3a3d42 !important; 
            }
            div[data-testid="stPopover"] button p { 
                font-size: 10px !important; 
                line-height: 1 !important;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h4 style='margin-bottom:5px; margin-top:-10px; text-align:center; color:#fff; text-transform:uppercase; font-weight:900; font-size: 14px; letter-spacing:1px;'>🔬 Range Lab</h4>", unsafe_allow_html=True)

    ranges_db = utils.load_ranges()
    if not ranges_db: 
        st.error("База ренджей пуста.")
        return

    col1, col2 = st.columns(2)

    with col1:
        data_a = render_popover_selector(ranges_db, "A", "🅰️")
        if data_a:
            st.markdown('<div class="matrix-box">', unsafe_allow_html=True)
            st.markdown(utils.render_range_matrix(data_a), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        data_b = render_popover_selector(ranges_db, "B", "🅱️")
        if data_b:
            st.markdown('<div class="matrix-box">', unsafe_allow_html=True)
            st.markdown(utils.render_range_matrix(data_b), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
