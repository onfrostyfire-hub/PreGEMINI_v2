import streamlit as st
import poker_utils as utils

def render_popover_and_matrix(ranges_db, suffix, emoji):
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

    # 1. Заголовки спотов (плотные, без лишних отступов)
    if curr_sc and curr_sp:
        short_sc = curr_sc.replace("Def vs 3bet", "Def3B").replace("Open Raise", "OR").replace("BB def vs PFR", "BB vs PFR")
        st.markdown(f"<div class='r-hdr'>{emoji} {short_sc}</div><div class='r-sub'>{curr_sp}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='r-hdr'>{emoji} Пусто</div><div class='r-sub'>...</div>", unsafe_allow_html=True)

    # 2. Кнопка фильтра
    with st.popover("⚙️ ФИЛЬТР", use_container_width=True):
        opts_sc = sorted(list(sc_map.keys()))
        idx_sc = opts_sc.index(curr_sc) if curr_sc in opts_sc else 0
        sc = st.selectbox(f"Сценарий {suffix}", opts_sc, key=k_sc, index=idx_sc) if opts_sc else None

        opts_sp = [x[0] for x in sc_map[sc]] if sc else []
        idx_sp = opts_sp.index(curr_sp) if curr_sp in opts_sp else 0
        sp = st.selectbox(f"Спот {suffix}", opts_sp, key=k_sp, index=idx_sp) if opts_sp else None

    # 3. Рендер самой матрицы
    if sc and sp:
        src = next((x[1] for x in sc_map[sc] if x[0] == sp), None)
        matrix_html = utils.render_range_matrix(ranges_db[src][sc][sp])
        st.markdown(f"<div class='matrix-wrapper'>{matrix_html}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='empty-matrix'>Нет данных</div>", unsafe_allow_html=True)


def show():
    st.markdown("""
        <style>
            /* Срезаем глобальные отступы экрана */
            .block-container { 
                padding: 0.5rem 0.2rem 4rem 0.2rem !important; 
                max-width: 100% !important; 
                overflow-x: hidden !important; 
            }
            
            /* Жесткая сетка для 2-х колонок на мобилках */
            div[data-testid="stHorizontalBlock"] {
                display: flex !important;
                flex-direction: row !important;
                flex-wrap: nowrap !important;
                gap: 6px !important;
                width: 100% !important;
                padding: 0 !important;
                margin-bottom: 6px !important;
            }
            
            /* Дизайн коробки каждого ренджа */
            div[data-testid="column"] {
                width: 50% !important;
                flex: 1 1 calc(50% - 3px) !important;
                min-width: 0 !important;
                background: #0a0a0c;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 4px !important;
                box-shadow: 0 2px 6px rgba(0,0,0,0.6);
            }

            /* --- УБИВАЕМ СКРЫТЫЕ ОТСТУПЫ СТРИМЛИТА --- */
            div[data-testid="column"] > div[data-testid="stVerticalBlock"] { gap: 2px !important; }
            div[data-testid="column"] div.element-container { margin-bottom: 0 !important; }
            
            /* Стилизация заголовков */
            .r-hdr { font-size: 10px; font-weight: 900; color: #ffc107; text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.1; margin-bottom: 1px; }
            .r-sub { font-size: 8px; color: #aaa; font-weight: bold; text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1; margin-bottom: 2px; }
            
            /* Сжимаем кнопку поповера */
            div[data-testid="stPopover"] button { 
                padding: 0px !important; 
                height: 20px !important; 
                min-height: 20px !important; 
                background: #1c1e22 !important; 
                border-color: #3a3d42 !important; 
                border-radius: 4px !important;
                margin-bottom: 2px !important;
            }
            div[data-testid="stPopover"] button p { 
                font-size: 9px !important; 
                font-weight: 800 !important;
                color: #ccc !important;
                letter-spacing: 0.5px;
                margin: 0 !important;
            }
            
            /* --- ФИКСЫ ДЛЯ МАТРИЦЫ ИЗ utils.render_range_matrix --- */
            .matrix-wrapper > div:first-child {
                gap: 0px !important; 
                padding: 0px !important;
                border: 1px solid #222 !important;
            }
            .matrix-wrapper div[title] { 
                font-size: 5.5px !important; 
                font-weight: 800 !important; 
                letter-spacing: -0.5px !important;
                min-width: 0 !important;
                min-height: 0 !important;
                box-shadow: inset 0 0 0 0.5px rgba(0,0,0,0.4) !important; 
            }
            
            /* Статистика (Call/Raise) под матрицей */
            .matrix-wrapper > div:last-child {
                gap: 2px !important;
                margin-top: 4px !important;
                padding-bottom: 2px !important;
                justify-content: center !important;
            }
            .matrix-wrapper > div:last-child > div { 
                font-size: 6px !important; 
                padding: 1px 3px !important; 
                border-radius: 2px !important;
                letter-spacing: -0.2px !important;
                white-space: nowrap !important;
            }
            
            .empty-matrix {
                color: #444; 
                text-align: center; 
                font-size: 9px; 
                padding: 30px 0; 
                border: 1px dashed #333; 
                border-radius: 4px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h4 style='margin-bottom:6px; margin-top:-18px; text-align:center; color:#fff; text-transform:uppercase; font-weight:900; font-size: 14px; letter-spacing:1px;'>🔬 Range Lab</h4>", unsafe_allow_html=True)

    ranges_db = utils.load_ranges()
    if not ranges_db: 
        st.error("База ренджей пуста.")
        return

    # ПЕРВЫЙ РЯД
    col1, col2 = st.columns(2)
    with col1:
        render_popover_and_matrix(ranges_db, "A", "1️⃣")
    with col2:
        render_popover_and_matrix(ranges_db, "B", "2️⃣")

    # ВТОРОЙ РЯД
    col3, col4 = st.columns(2)
    with col3:
        render_popover_and_matrix(ranges_db, "C", "3️⃣")
    with col4:
        render_popover_and_matrix(ranges_db, "D", "4️⃣")
