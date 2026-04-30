import streamlit as st

from views import review_common as rc


def _css():
    st.markdown("""
    <style>
    .review-shell {
        max-width: 1320px;
        margin: 0 auto;
        color: #f7f9ff;
        font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    .review-kicker {
        margin-top: 24px;
        color: #59f0a6;
        font-size: 12px;
        font-weight: 900;
        letter-spacing: .16em;
        text-transform: uppercase;
    }
    .review-hero {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        gap: 28px;
        padding: 18px 0 18px;
    }
    .review-title {
        font-size: clamp(46px, 5vw, 76px);
        line-height: .95;
        font-weight: 950;
        letter-spacing: 0;
        margin: 0;
    }
    .review-subtitle {
        margin-top: 14px;
        color: #aab8d8;
        font-size: 17px;
        font-weight: 500;
    }
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 16px;
        margin: 6px 0 18px;
    }
    .review-card, .metric-card, .queue-card, .calendar-card {
        border: 1px solid rgba(255,255,255,.12);
        background:
            linear-gradient(180deg, rgba(255,255,255,.055), rgba(255,255,255,.02)),
            #171a21;
        box-shadow: 0 16px 42px rgba(0,0,0,.32), inset 0 1px 0 rgba(255,255,255,.05);
        border-radius: 18px;
    }
    .metric-card {
        padding: 24px 22px 20px;
        min-height: 124px;
    }
    .metric-label {
        color: #abc0e4;
        font-size: 12px;
        font-weight: 900;
        letter-spacing: .12em;
        text-transform: uppercase;
    }
    .metric-value {
        margin-top: 16px;
        font-size: 38px;
        line-height: 1;
        font-weight: 950;
        color: #fff;
    }
    .metric-foot {
        margin-top: 12px;
        color: #95a4c1;
        font-weight: 750;
        font-size: 14px;
    }
    .metric-late .metric-value { color: #ff5a68; }
    .review-layout {
        display: grid;
        grid-template-columns: 390px minmax(0, 1fr);
        gap: 18px;
        align-items: stretch;
    }
    .calendar-card, .queue-card {
        padding: 22px;
        min-height: 520px;
    }
    .section-title {
        font-size: 26px;
        font-weight: 950;
        margin: 0 0 18px;
    }
    .calendar-week {
        display: grid;
        grid-template-columns: repeat(7, minmax(0,1fr));
        gap: 8px;
        margin-bottom: 22px;
    }
    .day-cell {
        min-height: 92px;
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,.10);
        background: #20242d;
        padding: 11px 8px;
        text-align: center;
    }
    .day-cell.today {
        border-color: rgba(255,75,85,.72);
        background: linear-gradient(180deg, rgba(255,75,85,.30), rgba(255,75,85,.10));
    }
    .day-name {
        color: #9fb0d0;
        font-size: 11px;
        font-weight: 900;
        letter-spacing: .08em;
        text-transform: uppercase;
    }
    .day-count {
        margin-top: 18px;
        color: #fff;
        font-size: 28px;
        line-height: 1;
        font-weight: 950;
    }
    .section-row {
        display: grid;
        grid-template-columns: 74px 1fr 46px;
        gap: 12px;
        align-items: center;
        margin: 14px 0;
        color: #dce7ff;
        font-weight: 900;
    }
    .line-track {
        height: 8px;
        border-radius: 99px;
        background: #090c12;
        overflow: hidden;
    }
    .line-fill {
        height: 100%;
        border-radius: inherit;
        background: linear-gradient(90deg, #47e18f, #e7d928);
    }
    .toolbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
        margin-bottom: 18px;
    }
    .queue-item {
        border: 1px solid rgba(255,255,255,.10);
        background: linear-gradient(180deg, rgba(255,255,255,.05), rgba(255,255,255,.025));
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
        position: relative;
        overflow: hidden;
    }
    .queue-item:before {
        content: "";
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 5px;
        background: linear-gradient(180deg, #ff4b55, #48df91);
    }
    .queue-top {
        display: flex;
        justify-content: space-between;
        gap: 14px;
        align-items: flex-start;
    }
    .queue-name {
        font-size: 20px;
        font-weight: 950;
        color: #fff;
        line-height: 1.15;
    }
    .queue-detail {
        margin-top: 6px;
        color: #9fb0d0;
        font-size: 13px;
        font-weight: 750;
    }
    .pill-row {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        justify-content: flex-end;
    }
    .soft-pill {
        padding: 7px 10px;
        border-radius: 999px;
        border: 1px solid rgba(255,255,255,.10);
        background: rgba(7,10,16,.45);
        color: #eaf1ff;
        font-size: 12px;
        font-weight: 900;
        white-space: nowrap;
    }
    .progress-1000 {
        margin-top: 14px;
        height: 8px;
        border-radius: 99px;
        background: #070a10;
        overflow: hidden;
    }
    .progress-1000 > div {
        height: 100%;
        border-radius: inherit;
        background: linear-gradient(90deg, #58e193, #f0dc3d, #ff4b9c);
    }
    .launch-panel {
        border: 1px solid rgba(255,255,255,.12);
        border-radius: 18px;
        padding: 18px;
        margin: 8px 0 20px;
        background: radial-gradient(circle at top left, rgba(255,75,85,.18), transparent 45%), #171a21;
    }
    div[data-testid="stButton"] > button {
        border-radius: 13px !important;
        border: 1px solid rgba(255,255,255,.14) !important;
        background: linear-gradient(180deg, #242832, #171b23) !important;
        color: #f7f9ff !important;
        font-weight: 900 !important;
        min-height: 42px !important;
        box-shadow: 0 8px 20px rgba(0,0,0,.28), inset 0 1px 0 rgba(255,255,255,.06) !important;
    }
    div[data-testid="stButton"] > button:hover {
        border-color: rgba(255,75,85,.55) !important;
        color: #fff !important;
        transform: translateY(-1px);
    }
    .primary-review-btn button {
        background: linear-gradient(180deg, #ff5260, #e83f4f) !important;
        box-shadow: 0 10px 28px rgba(255,75,85,.28), inset 0 1px 0 rgba(255,255,255,.18) !important;
    }
    </style>
    """, unsafe_allow_html=True)


def _metric_cards(counts, section_counts):
    st.markdown(f"""
    <div class="metric-grid">
      <div class="metric-card">
        <div class="metric-label">Today</div>
        <div class="metric-value">{counts.get("Today", 0)}</div>
        <div class="metric-foot">{section_counts.get("Fish", 0)} Fish active</div>
      </div>
      <div class="metric-card metric-late">
        <div class="metric-label">Late</div>
        <div class="metric-value">{counts.get("Late", 0)}</div>
        <div class="metric-foot">Highest priority queue</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Next 7 Days</div>
        <div class="metric-value">{counts.get("Next 7 Days", 0)}</div>
        <div class="metric-foot">Planned repetitions</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Active Spots</div>
        <div class="metric-value">{counts.get("Active Spots", 0)}</div>
        <div class="metric-foot">Shown after 100 hands</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def _calendar(spots):
    days = rc.calendar_counts(spots)
    max_count = max([d["count"] for d in days] + [1])
    cells = []
    for i, day in enumerate(days):
        cls = "day-cell today" if i == 0 else "day-cell"
        cells.append(
            f'<div class="{cls}"><div class="day-name">{rc.esc(day["label"])}</div>'
            f'<div class="day-count">{day["count"]}</div></div>'
        )
    section_counts = rc.section_counts(spots)
    rows = []
    for label, value in section_counts.items():
        width = int((value / max(max(section_counts.values()), 1)) * 100)
        rows.append(
            f'<div class="section-row"><div>{label}</div>'
            f'<div class="line-track"><div class="line-fill" style="width:{width}%"></div></div>'
            f'<div>{value}</div></div>'
        )
    st.markdown(f"""
    <div class="calendar-card">
      <div class="section-title">Review Calendar</div>
      <div class="calendar-week">{''.join(cells)}</div>
      {''.join(rows)}
    </div>
    """, unsafe_allow_html=True)


def _render_launch_choice():
    choice = st.session_state.get("review_launch_choice")
    if not choice:
        return
    groups = choice.get("groups", {})
    label = choice.get("label", "Review")
    st.markdown(f'<div class="launch-panel"><div class="section-title">Choose Trainer</div><div style="color:#aab8d8;margin-bottom:12px;">{rc.esc(label)} contains spots from multiple sections. Pick one trainer to start.</div>', unsafe_allow_html=True)
    cols = st.columns(max(1, len(groups)))
    for col, (section, keys) in zip(cols, groups.items()):
        with col:
            if st.button(f"{section} - {len(keys)} spots", key=rc.stable_key("launch_group_d", section + label), use_container_width=True):
                st.session_state.pop("review_launch_choice", None)
                rc.start_review_training(section, keys, label)
    if st.button("Cancel", key="cancel_group_launch_d"):
        st.session_state.pop("review_launch_choice", None)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _queue_card(spot, index):
    progress = min(100, int((spot["total"] / 1000) * 100))
    due_text = "Late " + str(spot["late_days"]) + "d" if spot["late_days"] else ("Today" if spot["days_until"] == 0 else f"In {spot['days_until']}d")
    st.markdown(f"""
    <div class="queue-item">
      <div class="queue-top">
        <div>
          <div class="queue-name">{rc.esc(spot["display"])}</div>
          <div class="queue-detail">{rc.esc(spot["section"])} - {rc.esc(spot["detail"])}</div>
        </div>
        <div class="pill-row">
          <div class="soft-pill">{rc.esc(due_text)}</div>
          <div class="soft-pill">{spot["accuracy"]:.1f}%</div>
          <div class="soft-pill">{spot["total"]}/1000</div>
        </div>
      </div>
      <div class="progress-1000"><div style="width:{progress}%"></div></div>
    </div>
    """, unsafe_allow_html=True)
    c1, c2, c3 = st.columns([0.22, 0.22, 0.56])
    with c1:
        if st.button("Train", key=rc.stable_key("train_spot_d", spot["section"] + spot["key"]), use_container_width=True):
            rc.start_review_training(spot["section"], [spot["key"]], f"Review - {spot['display']}")
    with c2:
        if st.button("Hide from Review", key=rc.stable_key("hide_spot_d", spot["section"] + spot["key"]), use_container_width=True):
            rc.hide_spot(spot["section"], spot["key"])
            st.rerun()
    with c3:
        st.checkbox("Select", key=rc.stable_key("select_spot_d", spot["section"] + spot["key"]))


def _settings_sidebar():
    with st.sidebar:
        st.markdown("### Review Settings")
        _, review = rc.load_review_settings()
        visible_default = [s for s in rc.SECTIONS if s not in set(review.get("hidden_sections", []))]
        visible = st.multiselect("Visible sections", rc.SECTIONS, default=visible_default)
        min_hands = st.number_input("Minimum hands per spot", min_value=0, max_value=5000, value=int(review.get("min_hands", rc.MIN_REVIEW_HANDS)), step=25)
        if st.button("Save Review Settings", use_container_width=True):
            review["hidden_sections"] = [s for s in rc.SECTIONS if s not in visible]
            review["min_hands"] = int(min_hands)
            rc.save_review_settings(review)
            st.rerun()
        hidden_count = len(review.get("hidden_spots", []))
        st.caption(f"Hidden spots: {hidden_count}")
        if hidden_count and st.button("Unhide all spots", use_container_width=True):
            rc.unhide_all_spots()
            st.rerun()


def show():
    _css()
    _settings_sidebar()

    spots = rc.build_review_spots()
    counts = rc.bucket_counts(spots)
    sec_counts = rc.section_counts(spots)

    default_period = "Late" if counts.get("Late") else ("Today" if counts.get("Today") else ("Next 7 Days" if counts.get("Next 7 Days") else "Active Spots"))

    st.markdown('<div class="review-shell">', unsafe_allow_html=True)
    st.markdown("""
    <div class="review-kicker">Repeat Queue</div>
    <div class="review-hero">
      <div>
        <h1 class="review-title">Today's Review Queue</h1>
        <div class="review-subtitle">Smart repeat list for spots that are late, due today, or coming up soon.</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    a, b, c, d = st.columns([0.18, 0.18, 0.18, 0.46])
    with a:
        st.markdown('<div class="primary-review-btn">', unsafe_allow_html=True)
        if st.button("Train Today", use_container_width=True, key="review_train_today_d"):
            rc.request_grouped_launch("Today", [s for s in spots if s["bucket"] == "Today"])
        st.markdown("</div>", unsafe_allow_html=True)
    with b:
        if st.button("Train Late", use_container_width=True, key="review_train_late_d"):
            rc.request_grouped_launch("Late", [s for s in spots if s["bucket"] == "Late"])
    with c:
        if st.button("Train Next 7", use_container_width=True, key="review_train_next_d"):
            rc.request_grouped_launch("Next 7 Days", [s for s in spots if s["bucket"] == "Next 7 Days"])

    _metric_cards(counts, sec_counts)
    _render_launch_choice()

    st.markdown('<div class="toolbar">', unsafe_allow_html=True)
    period = st.radio("Queue", rc.PERIODS, index=rc.PERIODS.index(default_period), horizontal=True, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    f1, f2 = st.columns([0.45, 0.55])
    with f1:
        selected_sections = st.multiselect("Sections", rc.SECTIONS, default=[s for s in rc.SECTIONS if sec_counts.get(s, 0) > 0] or rc.SECTIONS)
    with f2:
        search = st.text_input("Search spots", placeholder="Board, line, scenario...")

    visible_spots = rc.filter_spots(spots, selected_sections, period, search)

    left, right = st.columns([0.32, 0.68], gap="large")
    with left:
        _calendar(spots)
    with right:
        st.markdown('<div class="queue-card"><div class="section-title">Smart Priority Queue</div>', unsafe_allow_html=True)
        selected_items = []
        if not visible_spots:
            st.info("No Review spots match the current filters.")
        for idx, spot in enumerate(visible_spots[:40]):
            _queue_card(spot, idx)
            if st.session_state.get(rc.stable_key("select_spot_d", spot["section"] + spot["key"])):
                selected_items.append(spot)
        if len(visible_spots) > 40:
            st.caption(f"Showing first 40 of {len(visible_spots)} spots.")
        if selected_items:
            st.markdown('<div class="primary-review-btn">', unsafe_allow_html=True)
            if st.button(f"Train Selected ({len(selected_items)})", key="train_selected_review_d", use_container_width=True):
                rc.request_grouped_launch("Selected Review Spots", selected_items)
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
