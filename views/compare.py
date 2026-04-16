
import streamlit as st
import poker_utils as utils

def get_spot_data_for_tab(ranges_db, suffix, tab):
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

    with tab:
        opts_sc = sorted(list(sc_map.keys()))
        idx_sc = opts_sc.index(curr_sc) if curr_sc in opts_sc else 0
        sc = st.selectbox(f"Сценарий", opts_sc, key=k_sc, index=idx_sc) if opts_sc else None

        opts_sp = [x[0] for x in sc_map[sc]] if sc else []
        idx_sp = opts_sp.index(curr_sp) if curr_sp in opts_sp else 0
        sp = st.selectbox(f"Спот", opts_sp, key=k_sp, index=idx_sp) if opts_sp else None

    if sc and sp:
        src = next((x[1] for x in sc_map[sc] if x[0] == sp), None)
        return sc, sp, ranges_db[src][sc][sp]
    return None, None, None

def render_header(sc, sp, emoji):
    if sc and sp:
        short_sc = sc.replace("Def vs 3bet", "Def3B").replace("Open Raise", "OR").replace("BB def vs PFR", "BB vs PFR")
        return f"<div class='range-header'>{emoji} {short_sc}</div><div class='range-subheader'>{sp}</div>"
    return f"<div class='range-header'>{emoji} Пусто</div><div class='range-subheader'>...</div>"

def show():
    st.markdown("""
        <style>
            /* Убираем лишние отступы экрана */
            .block-container { 
                padding: 1rem 0.2rem 5rem 0.2rem !important; 
                max-width: 100% !important; 
                overflow-x: hidden !important; 
            }
            
            /* --- СТИЛИЗАЦИЯ ЗАГОЛОВКОВ --- */
            .range-header {
                font-size: 9.5px;
                font-weight: 900;
                color: #ffc107;
                line-height: 1;
                margin-bottom: 0px;
                text-align: center;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                padding-top: 2px;
            }
            .range-subheader {
                font-size: 7.5px;
                color: #aaa;
                font-weight: bold;
                line-height: 1;
                text-align: center;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                margin-bottom: 2px;
            }
            
            /* СЫРОЙ HTML КОНТЕЙНЕР ДЛЯ МАТРИЦ */
            .custom-matrix-row {
                display: flex;
                flex-direction: row;
                flex-wrap: nowrap;
                justify-content: space-between;
                align-items: stretch;
                gap: 4px;
                width: 100%;
                margin-top: 4px;
            }
            .custom-matrix-label {
                flex: 1 1 50%;
                min-width: 0;
                width: calc(50% - 2px);
                display: block;
                margin: 0;
                cursor: pointer;
                -webkit-tap-highlight-color: transparent;
            }
            .custom-matrix-col {
                height: 100%;
                background: #0a0a0c;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 1px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.6);
                transition: all 0.2s ease-in-out;
            }
            
            /* Переписываем стили, которые генерирует poker_utils.py */
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
            
            /* Ужимаем статистику под матрицей */
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

            /* --- ЧИСТЫЙ CSS ЗУМ (FULLSCREEN) БЕЗ JS --- */
            .expand-btn { display: none; }
            .expand-btn:checked + .custom-matrix-col {
                position: fixed;
                top: 0; left: 0; right: 0; bottom: 0;
                z-index: 99999;
                background: #0a0a0c;
                padding: 15px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                width: 100vw;
                height: 100vh;
            }
            
            /* Стилизация внутри раскрытой матрицы */
            .expand-btn:checked + .custom-matrix-col > div[style*="display:grid"] {
                width: 100%;
                max-width: 500px;
            }
            .expand-btn:checked + .custom-matrix-col .range-header {
                font-size: 18px !important;
                padding-bottom: 4px;
                color: #ffc107;
            }
            .expand-btn:checked + .custom-matrix-col .range-subheader {
                font-size: 14px !important;
                margin-bottom: 12px;
            }
            .expand-btn:checked + .custom-matrix-col div[title] {
                font-size: 11px !important;
                line-height: 1.1 !important;
            }
            .expand-btn:checked + .custom-matrix-col div[title] > div:first-child {
                font-size: 13px !important;
            }
            .expand-btn:checked + .custom-matrix-col > div:last-child {
                margin-top: 15px !important;
                gap: 10px !important;
            }
            .expand-btn:checked + .custom-matrix-col > div:last-child > div {
                font-size: 12px !important;
                padding: 4px 8px !important;
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

    st.markdown("<h4 style='margin-bottom:5px; margin-top:-10px; text-align:center; color:#fff; text-transform:uppercase; font-weight:900; font-size: 14px; letter-spacing:1px;'>🔬 Range Lab</h4>", unsafe_allow_html=True)

    ranges_db = utils.load_ranges()
    if not ranges_db: 
        st.error("База ренджей пуста.")
        return

    # --- ЕДИНАЯ ПАНЕЛЬ УПРАВЛЕНИЯ ---
    with st.expander("⚙️ ПАНЕЛЬ УПРАВЛЕНИЯ РЕНДЖАМИ", expanded=False):
        tab1, tab2, tab3, tab4 = st.tabs(["1️⃣", "2️⃣", "3️⃣", "4️⃣"])
        
        sc_a, sp_a, data_a = get_spot_data_for_tab(ranges_db, "A", tab1)
        sc_b, sp_b, data_b = get_spot_data_for_tab(ranges_db, "B", tab2)
        sc_c, sp_c, data_c = get_spot_data_for_tab(ranges_db, "C", tab3)
        sc_d, sp_d, data_d = get_spot_data_for_tab(ranges_db, "D", tab4)

    # --- ВЫВОД МАТРИЦ ---
    
    # ПЕРВЫЙ РЯД
    header_a = render_header(sc_a, sp_a, "1️⃣")
    matrix_a_html = utils.render_range_matrix(data_a) if data_a else "<div class='empty-matrix'>Нет данных</div>"
    
    header_b = render_header(sc_b, sp_b, "2️⃣")
    matrix_b_html = utils.render_range_matrix(data_b) if data_b else "<div class='empty-matrix'>Нет данных</div>"

    st.markdown(f"""
    <div class="custom-matrix-row">
        <label class="custom-matrix-label">
            <input type="checkbox" class="expand-btn">
            <div class="custom-matrix-col">{header_a}{matrix_a_html}</div>
        </label>
        <label class="custom-matrix-label">
            <input type="checkbox" class="expand-btn">
            <div class="custom-matrix-col">{header_b}{matrix_b_html}</div>
        </label>
    </div>
    """, unsafe_allow_html=True)

    # ВТОРОЙ РЯД
    header_c = render_header(sc_c, sp_c, "3️⃣")
    matrix_c_html = utils.render_range_matrix(data_c) if data_c else "<div class='empty-matrix'>Нет данных</div>"
    
    header_d = render_header(sc_d, sp_d, "4️⃣")
    matrix_d_html = utils.render_range_matrix(data_d) if data_d else "<div class='empty-matrix'>Нет данных</div>"

    st.markdown(f"""
    <div class="custom-matrix-row">
        <label class="custom-matrix-label">
            <input type="checkbox" class="expand-btn">
            <div class="custom-matrix-col">{header_c}{matrix_c_html}</div>
        </label>
        <label class="custom-matrix-label">
            <input type="checkbox" class="expand-btn">
            <div class="custom-matrix-col">{header_d}{matrix_d_html}</div>
        </label>
    </div>
    """, unsafe_allow_html=True)
