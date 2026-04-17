import streamlit as st
from views import mobile, desktop, compare, stats
from views import postflop_desktop, postflop_mobile

st.set_page_config(page_title="Poker Trainer", layout="wide", initial_sidebar_state="collapsed")

def detect_mobile():
    try:
        if hasattr(st, "context") and hasattr(st.context, "headers"):
            ua = st.context.headers.get("User-Agent", "").lower()
            return "mobi" in ua or "android" in ua or "iphone" in ua
    except: pass
    try:
        from streamlit.web.server.websocket_headers import _get_websocket_headers
        headers = _get_websocket_headers()
        ua = headers.get("User-Agent", "").lower()
        return "mobi" in ua or "android" in ua or "iphone" in ua
    except: pass
    return False

def main():
    st.markdown("""
    <style>
        [data-testid="collapsedControl"] { display: none !important; }
        header[data-testid="stHeader"] { background: transparent !important; height: 0px !important; min-height: 0px !important; }
        .block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; }
        
        .compact-tabs { display: none; }
        .compact-tabs + div[role="radiogroup"] {
            display: inline-flex !important;
            background: #1a1c20 !important;
            padding: 2px !important;
            border-radius: 8px !important;
            border: 1px solid #333 !important;
            gap: 2px !important;
            margin-top: -5px !important;
            margin-bottom: -5px !important;
        }
        .compact-tabs + div[role="radiogroup"] label {
            padding: 4px 10px !important;
            background: transparent !important;
            border-radius: 6px !important;
            cursor: pointer !important;
            margin: 0 !important;
            border: none !important;
        }
        .compact-tabs + div[role="radiogroup"] label div:first-child { display: none !important; }
        .compact-tabs + div[role="radiogroup"] label p { 
            color: #888 !important; font-size: 12px !important; font-weight: bold !important; margin: 0 !important; text-transform: uppercase; 
        }
        .compact-tabs + div[role="radiogroup"] label[data-checked="true"],
        .compact-tabs + div[role="radiogroup"] label:has(input:checked) {
            background: #ffc107 !important; box-shadow: 0 1px 3px rgba(0,0,0,0.4) !important;
        }
        .compact-tabs + div[role="radiogroup"] label[data-checked="true"] p,
        .compact-tabs + div[role="radiogroup"] label:has(input:checked) p {
            color: #000 !important; font-weight: 900 !important;
        }
        
        div[data-testid="stVerticalBlock"] > div { padding-bottom: 0 !important; margin-bottom: 0 !important; }
        div.element-container { margin-bottom: 2px !important; }
    </style>
    """, unsafe_allow_html=True)

    if "actual_view_type" not in st.session_state:
        st.session_state.actual_view_type = "📱 Mobile" if detect_mobile() else "💻 Desktop"
        
    # ЗАЩИТА ОТ КЭША: Если в памяти лежит старое название с эмодзи, сбрасываем на Preflop
    if "actual_app_mode" not in st.session_state or st.session_state.actual_app_mode not in ["Preflop", "Postflop", "Ranges", "Stats"]:
        st.session_state.actual_app_mode = "Preflop"

    st.markdown('<div class="compact-tabs"></div>', unsafe_allow_html=True)
    nav_mode = st.radio(
        "Nav", 
        ["Preflop", "Postflop", "Ranges", "Stats"], 
        index=["Preflop", "Postflop", "Ranges", "Stats"].index(st.session_state.actual_app_mode),
        horizontal=True, 
        label_visibility="collapsed"
    )
    if nav_mode != st.session_state.actual_app_mode:
        st.session_state.actual_app_mode = nav_mode
        st.rerun()

    # ОБНОВЛЕННАЯ ЛОГИКА (без эмодзи)
    if st.session_state.actual_app_mode == "Ranges":
        compare.show()
    elif st.session_state.actual_app_mode == "Stats":
        stats.show()
    elif st.session_state.actual_app_mode == "Postflop":
        if st.session_state.actual_view_type == "📱 Mobile":
            postflop_mobile.show()
        else:
            postflop_desktop.show()
    else:
        if st.session_state.actual_view_type == "📱 Mobile":
            mobile.show()
        else:
            desktop.show()

if __name__ == "__main__":
    main()
