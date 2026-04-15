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

    # Заголовок выбранного ренджа (максимально плотный, убраны все лишние line-height)
    if curr_sc and curr_sp:
        short_sc = curr_sc.replace("Def vs 3bet", "Def3B").replace("Open Raise", "OR").replace("BB def vs PFR", "BB vs PFR")
        st.markdown(f"<div style='line-height:1; margin-bottom:2px; text-align:center;'><div style='font-weight:900;font-size:10px;color:#ffc107;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{emoji} {short_sc}</div><div style='font-size:8.5px;color:#aaa;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:1px;'>{curr_sp}</div></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='line-height:1; margin-bottom:2px; text-align:center;'><div style='font-weight:900;font-size:10px;color:#666;font-style:italic;'>{emoji} Пусто</div><div style='font-size:8.5px;color:#444;margin-top:1px;'>...</div></div>", unsafe_allow_html=True)

    # Микро-кнопка фильтра
    with st.popover("⚙️ ФИЛЬТР", use_container_width=True):
        opts_sc = sorted(list(sc_map.keys()))
        idx_sc = opts_sc.index(curr_sc) if curr_sc in opts_sc else 0
        sc = st.selectbox(f"Сценарий {suffix}", opts_sc, key=k_sc, index=idx_sc) if opts_sc else None

        opts_sp = [x[0] for x in sc_map[sc]] if sc else []
        idx_sp = opts_sp.index(curr_sp) if curr_sp in opts_sp else 0
        sp = st.selectbox(f"Спот {suffix}", opts_sp, key=k_sp, index=idx_sp) if opts_sp else None

    if sc and sp:
        src = next((x[1] for x in sc_map[sc] if x[0] == sp), None)
        return ranges_db[src][sc][sp]
    return None

def show():
    st.markdown("""
        <style>
            /* Максимально срезаем отступы контейнера страницы */
            .block-container { 
                padding: 0.2rem 0.2rem 1rem 0.2rem !important; 
                max-width: 100% !important; 
                overflow-x: hidden !important; 
            }
            
            /* ЖЕСТКИЙ ФИКС СТРИМЛИТА ДЛЯ ФИЛЬТРОВ: убиваем скрытые зазоры между текстом и кнопкой */
            div[data-testid="column"] > div[data-testid="stVerticalBlock"] {
                gap: 0px !important;
            }
            div[data-testid="column"] .element-container {
                margin-bottom: 0px !important;
            }
            
            /* Жесткая сетка для мобилки: 2 колонки ровно по 50% */
            div[data-testid="stHorizontalBlock"] {
                display: flex !important;
                flex-direction: row !important;
                flex-wrap: nowrap !important;
                gap: 4px !important;
                width: 100% !important;
                padding: 0 !important;
                margin-bottom: 2px !important; /* Отступ от кнопок до матрицы */
            }
            div[data-testid="column"] {
                width: 50% !important;
                flex: 1 1 calc(50% - 2px) !important;
                min-width: 0 !important;
                padding: 2px 2px 0px 2px !important; /* Убран нижний отступ коробки фильтра */
                background: #0a0a0c;
                border: 1px solid #333;
                border-radius: 6px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.6);
            }
            
            /* Сжимаем кнопку фильтра (popover) до предела */
            div[data-testid="stPopover"] {
                margin-bottom: 2px !important;
            }
            div[data-testid="stPopover"] button { 
                padding: 0px !important; 
                height: 18px !important; 
                min-height: 18px !important; 
                background: #1c1e22 !important; 
                border-color: #3a3d42 !important; 
                border-radius: 3px !important;
            }
            div[data-testid="stPopover"] button p { 
                font-size: 8.5px !important; 
                font-weight: 800 !important;
                color: #ccc !important;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin: 0 !important;
            }
            
            /* --- СЫРОЙ HTML КОНТЕЙНЕР ДЛЯ МАТРИЦ (ТВОЙ КОД, НЕ ТРОНУТ) --- */
            .custom-matrix-row {
                display: flex;
                flex-direction: row;
                flex-wrap: nowrap;
                justify-content: space-between;
                align-items: flex-start;
                gap: 4px;
                width: 100%;
                margin-top: 2px;
                margin-bottom: 6px; /* Отступ между первым и вторым рядом */
            }
            .custom-matrix-col {
                flex: 1 1 50%;
                min-width: 0;
                width: 50%;
                background: #0a0a0c;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 1px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.6);
            }
            
            /* --- СТИЛИ МАТРИЦЫ (ТВОЙ КОД, НЕ ТРОНУТ) --- */
            .custom-matrix-col > div:first-child {
                gap: 0px !important; 
                padding: 0px !important;
                border: none !important;
            }
            .custom-matrix-col div[title] { 
                font-size: 5.5px !important; 
                font-weight: 800 !important; 
                letter-spacing: -0.5px !important;
                min-width: 0 !important;
                min-height: 0 !important;
                overflow: hidden !important;
                box-shadow: inset 0 0 0 0.5px rgba(0,0,0,0.4) !important; 
            }
            
            /* Статистика под матрицей (Call/Raise) */
            .custom-matrix-col > div:last-child {
                gap: 2px !important;
                margin-top: 4px !important;
                padding-bottom: 2px !important;
                justify-content: center !important;
            }
            .custom-matrix-col > div:last-child > div { 
                font-size: 6px !important; 
                padding: 1px 3px !important; 
                border-radius: 2px !important;
                letter-spacing: -0.2px !important;
                white-space: nowrap !important;
            }
            
            /* Заглушка, если рендж не выбран */
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

    st.markdown("<h4 style='margin-bottom:4px; margin-top:-10px; text-align:center; color:#fff; text-transform:uppercase; font-weight:900; font-size: 13px; letter-spacing:1px;'>🔬 Range Lab</h4>", unsafe_allow_html=True)

    ranges_db = utils.load_ranges()
    if not ranges_db: 
        st.error("База ренджей пуста.")
        return

    # === ПЕРВЫЙ РЯД (A и B) ===
    col1, col2 = st.columns(2)
    with col1:
        data_a = render_popover_selector(ranges_db, "A", "1️⃣")
    with col2:
        data_b = render_popover_selector(ranges_db, "B", "2️⃣")

    matrix_a_html = utils.render_range_matrix(data_a) if data_a else "<div class='empty-matrix'>Нет данных</div>"
    matrix_b_html = utils.render_range_matrix(data_b) if data_b else "<div class='empty-matrix'>Нет данных</div>"

    st.markdown(f"""
    <div class="custom-matrix-row">
        <div class="custom-matrix-col">{matrix_a_html}</div>
        <div class="custom-matrix-col">{matrix_b_html}</div>
    </div>
    """, unsafe_allow_html=True)

    # === ВТОРОЙ РЯД (C и D) ===
    col3, col4 = st.columns(2)
    with col3:
        data_c = render_popover_selector(ranges_db, "C", "3️⃣")
    with col4:
        data_d = render_popover_selector(ranges_db, "D", "4️⃣")

    matrix_c_html = utils.render_range_matrix(data_c) if data_c else "<div class='empty-matrix'>Нет данных</div>"
    matrix_d_html = utils.render_range_matrix(data_d) if data_d else "<div class='empty-matrix'>Нет данных</div>"

    st.markdown(f"""
    <div class="custom-matrix-row">
        <div class="custom-matrix-col">{matrix_c_html}</div>
        <div class="custom-matrix-col">{matrix_d_html}</div>
    </div>
    """, unsafe_allow_html=True)
