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
        # Сокращаем длинные названия для экономии места
        short_sc = curr_sc.replace("Def vs 3bet", "Def3B").replace("Open Raise", "OR").replace("BB def vs PFR", "BB vs PFR")
        display_text = f"<div style='font-weight:900;font-size:11px;color:#ffc107;margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{emoji} {short_sc}</div><div style='font-size:10px;color:#aaa;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{curr_sp}</div>"
    else:
        display_text = f"<div style='color:#666;font-style:italic;font-size:11px;font-weight:bold;'>{emoji} Выбрать...</div>"

    st.markdown(display_text, unsafe_allow_html=True)

    with st.popover("⚙️ Настроить", use_container_width=True):
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
            /* Сжимаем боковые отступы экрана, чтобы выжать максимум ширины */
            .block-container { padding-top: 1.5rem !important; padding-bottom: 5rem !important; padding-left: 0.3rem !important; padding-right: 0.3rem !important; max-width: 100% !important; }
            
            /* ЛОМАЕМ СТРИМЛИТ: Жестко заставляем колонки стоять в ряд на мобилках */
            div[data-testid="stHorizontalBlock"] {
                display: flex !important;
                flex-direction: row !important;
                flex-wrap: nowrap !important;
                gap: 6px !important;
            }
            div[data-testid="column"] {
                width: 50% !important;
                flex: 1 1 calc(50% - 3px) !important;
                min-width: 0 !important;
                margin-bottom: 10px !important;
            }
            
            /* Дизайн коробок с матрицами */
            .matrix-box { border: 1px solid #333; border-radius: 6px; padding: 2px; background: #111; margin-top: 4px; overflow: hidden; box-shadow: 0 4px 8px rgba(0,0,0,0.5); }
            
            /* Ужимаем шрифты до микроскопических, чтобы влезли в 50% ширины айфона */
            .matrix-box div[title] { font-size: 6px !important; font-weight: bold !important; line-height: 1 !important; }
            
            /* Сжимаем статистику под матрицей */
            .matrix-box > div > div:last-child > div { font-size: 8px !important; padding: 2px 4px !important; border-radius: 4px !important; }
            
            /* Компактные кнопки поповеров */
            div[data-testid="stPopover"] button { padding: 2px 4px !important; font-size: 10px !important; height: 28px !important; min-height: 28px !important; background: #1c1e22 !important; border-color: #3a3d42 !important; }
            div[data-testid="stPopover"] button p { font-size: 11px !important; font-weight: 700 !important; color: #ccc !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h4 style='margin-bottom:10px; color:#fff; text-transform:uppercase; font-weight:900; letter-spacing:1px;'>🔬 Range Lab</h4>", unsafe_allow_html=True)

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
