import streamlit as st
from views import mobile, desktop, compare, stats_mobile, stats_desktop
from views import postflop_desktop, postflop_mobile
from views import review_desktop, review_mobile

# Заглушка, пока ты не вставишь код в новые файлы
try:
    from views import fish_desktop, fish_mobile
    FISH_AVAILABLE = True
except ImportError:
    FISH_AVAILABLE = False

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
        div[role="radiogroup"][aria-label="Nav"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
            width: min(100%, 720px) !important;
            max-width: 720px !important;
            background: #1a1c20 !important;
            padding: 4px !important;
            border-radius: 12px !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            gap: 4px !important;
            margin: -6px 0 4px 0 !important;
            box-shadow: 0 2px 10px rgba(0,0,0,0.26), inset 0 1px 0 rgba(255,255,255,0.04) !important;
            overflow: hidden !important;
        }
        div[role="radiogroup"][aria-label="Nav"] label {
            flex: 1 1 0 !important;
            min-width: 0 !important;
            display: inline-flex !important;
            justify-content: center !important;
            align-items: center !important;
            padding: 7px 8px !important;
            background: transparent !important;
            border-radius: 8px !important;
            cursor: pointer !important;
            margin: 0 !important;
            border: none !important;
            white-space: nowrap !important;
        }
        div[role="radiogroup"][aria-label="Nav"] label > div:first-child { display: none !important; }
        div[role="radiogroup"][aria-label="Nav"] label p {
            color: #9aa0aa !important;
            font-size: 12px !important;
            font-weight: 800 !important;
            line-height: 1 !important;
            margin: 0 !important;
            text-transform: uppercase;
            white-space: nowrap !important;
            letter-spacing: 0 !important;
        }
        div[role="radiogroup"][aria-label="Nav"] label[data-checked="true"],
        div[role="radiogroup"][aria-label="Nav"] label:has(input:checked) {
            background: #ff4b55 !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.4) !important;
        }
        div[role="radiogroup"][aria-label="Nav"] label[data-checked="true"] p,
        div[role="radiogroup"][aria-label="Nav"] label:has(input:checked) p {
            color: #fff !important;
            font-weight: 900 !important;
        }
        @media (max-width: 640px) {
            div[role="radiogroup"][aria-label="Nav"] {
                width: calc(100vw - 28px) !important;
                max-width: none !important;
                gap: 2px !important;
                padding: 4px !important;
                margin-top: -10px !important;
                margin-bottom: 2px !important;
            }
            div[role="radiogroup"][aria-label="Nav"] label { padding: 7px 4px !important; }
            div[role="radiogroup"][aria-label="Nav"] label p { font-size: 9.8px !important; }
        }
        
        div[data-testid="stVerticalBlock"] > div { padding-bottom: 0 !important; margin-bottom: 0 !important; }
        div.element-container { margin-bottom: 2px !important; }
    </style>
    """, unsafe_allow_html=True)

    if "actual_view_type" not in st.session_state:
        st.session_state.actual_view_type = "📱 Mobile" if detect_mobile() else "💻 Desktop"
        
    nav_options = ["Review", "Preflop", "Postflop", "Fish", "Ranges", "Stats"]
    if "actual_app_mode" not in st.session_state or st.session_state.actual_app_mode not in nav_options:
        st.session_state.actual_app_mode = "Review"

    st.markdown('<div class="compact-tabs"></div>', unsafe_allow_html=True)
    nav_mode = st.radio(
        "Nav", 
        nav_options, 
        index=nav_options.index(st.session_state.actual_app_mode),
        horizontal=True, 
        label_visibility="collapsed"
    )
    if nav_mode != st.session_state.actual_app_mode:
        st.session_state.actual_app_mode = nav_mode
        st.rerun()

    if st.session_state.actual_app_mode == "Review":
        if st.session_state.actual_view_type == "📱 Mobile":
            review_mobile.show()
        else:
            review_desktop.show()
    elif st.session_state.actual_app_mode == "Ranges":
        compare.show()
    elif st.session_state.actual_app_mode == "Stats":
        if st.session_state.actual_view_type == "📱 Mobile":
            stats_mobile.show()
        else:
            stats_desktop.show()
    elif st.session_state.actual_app_mode == "Postflop":
        if st.session_state.actual_view_type == "📱 Mobile":
            postflop_mobile.show()
        else:
            postflop_desktop.show()
    elif st.session_state.actual_app_mode == "Fish":
        if not FISH_AVAILABLE:
            st.error("Файлы fish_mobile.py и fish_desktop.py еще не созданы. Жду подкрепления.")
        elif st.session_state.actual_view_type == "📱 Mobile":
            fish_mobile.show()
        else:
            fish_desktop.show()
    else:
        if st.session_state.actual_view_type == "📱 Mobile":
            mobile.show()
        else:
            desktop.show()

if __name__ == "__main__":
    main()
