import streamlit as st

from views import review_common as rc


def _css():
    st.markdown("""
    <style>
    .block-container { padding-left: 1rem !important; padding-right: 1rem !important; padding-top: .75rem !important; }
    .review-mobile {
        color: #f7f9ff;
        font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    .review-kicker-m {
        margin-top: 14px;
        color: #59f0a6;
        font-size: 11px;
        font-weight: 950;
        letter-spacing: .16em;
        text-transform: uppercase;
    }
    .review-title-m {
        margin: 10px 0 8px;
        font-size: 34px;
        line-height: .98;
        font-weight: 950;
        letter-spacing: 0;
    }
    .review-copy-m {
        color: #aab8d8;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 14px;
    }
    .metric-grid-m {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 9px;
        margin: 10px 0 14px;
    }
    .metric-card-m, .review-panel-m, .queue-item-m {
        border: 1px solid rgba(255,255,255,.12);
        background: linear-gradient(180deg, rgba(255,255,255,.055), rgba(255,255,255,.022)), #171a21;
        border-radius: 16px;
        box-shadow: 0 14px 32px rgba(0,0,0,.30), inset 0 1px 0 rgba(255,255,255,.05);
    }
    .metric-card-m {
        padding: 14px 13px;
        min-height: 86px;
    }
    .metric-label-m {
        color: #a8b9da;
        font-size: 10px;
        font-weight: 950;
        letter-spacing: .12em;
        text-transform: uppercase;
    }
    .metric-value-m {
        margin-top: 12px;
        font-size: 30px;
        line-height: 1;
        font-weight: 950;
    }
    .metric-foot-m {
        margin-top: 8px;
        color: #8797b4;
        font-size: 11px;
        font-weight: 800;
    }
    .review-panel-m {
        padding: 16px;
        margin: 10px 0;
    }
    .panel-title-m {
        font-size: 21px;
        font-weight: 950;
        margin-bottom: 12px;
    }
    .calendar-week-m {
        display: grid;
        grid-template-columns: repeat(7, minmax(0,1fr));
        gap: 5px;
        margin-bottom: 14px;
    }
    .day-cell-m {
        border: 1px solid rgba(255,255,255,.10);
        background: #20242d;
        border-radius: 12px;
        min-height: 64px;
        padding: 8px 4px;
        text-align: center;
    }
    .day-cell-m.today {
        border-color: rgba(255,75,85,.72);
        background: linear-gradient(180deg, rgba(255,75,85,.28), rgba(255,75,85,.10));
    }
    .day-name-m {
        color: #9fb0d0;
        font-size: 9px;
        font-weight: 950;
        text-transform: uppercase;
    }
    .day-count-m {
        margin-top: 12px;
        color: #fff;
        font-size: 21px;
        font-weight: 950;
    }
    .queue-item-m {
        padding: 15px 14px;
        margin-bottom: 12px;
        position: relative;
        overflow: hidden;
    }
    .queue-item-m:before {
        content: "";
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 4px;
        background: linear-gradient(180deg, #ff4b55, #55df96);
    }
    .queue-name-m {
        font-size: 18px;
        font-weight: 950;
        color: #fff;
        line-height: 1.15;
        padding-left: 2px;
    }
    .queue-detail-m {
        margin-top: 5px;
        color: #9fb0d0;
        font-size: 12px;
        font-weight: 750;
    }
    .pill-row-m {
        margin-top: 10px;
        display: flex;
        gap: 6px;
        flex-wrap: wrap;
    }
    .soft-pill-m {
        padding: 6px 9px;
        border-radius: 999px;
        border: 1px solid rgba(255,255,255,.10);
        background: rgba(7,10,16,.45);
        color: #eaf1ff;
        font-size: 11px;
        font-weight: 900;
    }
    .progress-1000-m {
        margin-top: 12px;
        height: 7px;
        border-radius: 99px;
        background: #070a10;
        overflow: hidden;
    }
    .progress-1000-m > div {
        height: 100%;
        border-radius: inherit;
        background: linear-gradient(90deg, #58e193, #f0dc3d, #ff4b9c);
    }
    .section-row-m {
        display: grid;
        grid-template-columns: 70px 1fr 38px;
        gap: 9px;
        align-items: center;
        margin: 10px 0;
        color: #dce7ff;
        font-size: 13px;
        font-weight: 900;
    }
    .review-filter-label-m {
        color: #9fb0d0;
        font-size: 10px;
        font-weight: 950;
        letter-spacing: .12em;
        text-transform: uppercase;
        margin: 12px 0 7px 2px;
    }
    div[role="radiogroup"][aria-label="Review period mobile"],
    div[role="radiogroup"][aria-label="Review sections mobile"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        width: 100% !important;
        background: #191c23 !important;
        padding: 4px !important;
        border-radius: 13px !important;
        border: 1px solid rgba(255,255,255,0.13) !important;
        gap: 3px !important;
        box-shadow: 0 8px 22px rgba(0,0,0,.24), inset 0 1px 0 rgba(255,255,255,.05) !important;
        overflow: hidden !important;
    }
    div[role="radiogroup"][aria-label="Review period mobile"] label,
    div[role="radiogroup"][aria-label="Review sections mobile"] label {
        flex: 1 1 0 !important;
        min-width: 0 !important;
        display: inline-flex !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 10px 3px !important;
        margin: 0 !important;
        border-radius: 9px !important;
        cursor: pointer !important;
        border: none !important;
        background: transparent !important;
        white-space: nowrap !important;
    }
    div[role="radiogroup"][aria-label="Review period mobile"] label > div:first-child,
    div[role="radiogroup"][aria-label="Review sections mobile"] label > div:first-child {
        display: none !important;
    }
    div[role="radiogroup"][aria-label="Review period mobile"] label p,
    div[role="radiogroup"][aria-label="Review sections mobile"] label p {
        margin: 0 !important;
        color: #a9b5c9 !important;
        font-size: 9.3px !important;
        font-weight: 900 !important;
        line-height: 1 !important;
        letter-spacing: 0 !important;
        text-transform: uppercase !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    div[role="radiogroup"][aria-label="Review period mobile"] label:has(input:checked),
    div[role="radiogroup"][aria-label="Review sections mobile"] label:has(input:checked) {
        background: #ff4b55 !important;
        box-shadow: 0 8px 18px rgba(255,75,85,.22), inset 0 1px 0 rgba(255,255,255,.16) !important;
    }
    div[role="radiogroup"][aria-label="Review period mobile"] label:has(input:checked) p,
    div[role="radiogroup"][aria-label="Review sections mobile"] label:has(input:checked) p {
        color: #fff !important;
    }
    .queue-shell-m {
        border: 1px solid rgba(255,255,255,.12);
        background: linear-gradient(180deg, rgba(255,255,255,.055), rgba(255,255,255,.02)), #171a21;
        border-radius: 16px;
        padding: 15px 14px 4px;
        box-shadow: 0 14px 32px rgba(0,0,0,.30), inset 0 1px 0 rgba(255,255,255,.05);
        margin-top: 12px;
    }
    .line-track-m {
        height: 7px;
        border-radius: 99px;
        background: #090c12;
        overflow: hidden;
    }
    .line-fill-m {
        height: 100%;
        border-radius: inherit;
        background: linear-gradient(90deg, #47e18f, #e7d928);
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
    .primary-review-btn button {
        background: linear-gradient(180deg, #ff5260, #e83f4f) !important;
        box-shadow: 0 10px 28px rgba(255,75,85,.28), inset 0 1px 0 rgba(255,255,255,.18) !important;
    }
    </style>
    """, unsafe_allow_html=True)


def _settings_panel():
    with st.expander("Review Settings", expanded=False):
        _, review = rc.load_review_settings()
        visible_default = [s for s in rc.SECTIONS if s not in set(review.get("hidden_sections", []))]
        visible = st.multiselect("Visible sections", rc.SECTIONS, default=visible_default)
        min_hands = st.number_input("Minimum hands per spot", min_value=0, max_value=5000, value=int(review.get("min_hands", rc.MIN_REVIEW_HANDS)), step=25)
        if st.button("Save Review Settings", use_container_width=True, key="save_review_settings_m"):
            review["hidden_sections"] = [s for s in rc.SECTIONS if s not in visible]
            review["min_hands"] = int(min_hands)
            rc.save_review_settings(review)
            st.rerun()
        hidden_count = len(review.get("hidden_spots", []))
        st.caption(f"Hidden spots: {hidden_count}")
        if hidden_count and st.button("Unhide all spots", use_container_width=True, key="unhide_review_m"):
            rc.unhide_all_spots()
            st.rerun()


def _metric_cards(counts, sec_counts):
    st.markdown(f"""
    <div class="metric-grid-m">
      <div class="metric-card-m">
        <div class="metric-label-m">Today</div>
        <div class="metric-value-m">{counts.get("Today", 0)}</div>
        <div class="metric-foot-m">Due now</div>
      </div>
      <div class="metric-card-m">
        <div class="metric-label-m">Late</div>
        <div class="metric-value-m" style="color:#ff5a68;">{counts.get("Late", 0)}</div>
        <div class="metric-foot-m">Highest priority</div>
      </div>
      <div class="metric-card-m">
        <div class="metric-label-m">Next 7 Days</div>
        <div class="metric-value-m">{counts.get("Next 7 Days", 0)}</div>
        <div class="metric-foot-m">Coming up</div>
      </div>
      <div class="metric-card-m">
        <div class="metric-label-m">Active Spots</div>
        <div class="metric-value-m">{counts.get("Active Spots", 0)}</div>
        <div class="metric-foot-m">{sec_counts.get("Fish", 0)} Fish</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def _calendar(spots):
    days = rc.calendar_counts(spots)
    cells = []
    for i, day in enumerate(days):
        cls = "day-cell-m today" if i == 0 else "day-cell-m"
        cells.append(
            f'<div class="{cls}"><div class="day-name-m">{rc.esc(day["label"])}</div>'
            f'<div class="day-count-m">{day["count"]}</div></div>'
        )
    section_counts = rc.section_counts(spots)
    max_value = max(max(section_counts.values()), 1)
    rows = []
    for label, value in section_counts.items():
        width = int((value / max_value) * 100)
        rows.append(
            f'<div class="section-row-m"><div>{label}</div>'
            f'<div class="line-track-m"><div class="line-fill-m" style="width:{width}%"></div></div>'
            f'<div>{value}</div></div>'
        )
    st.markdown(f"""
    <div class="review-panel-m">
      <div class="panel-title-m">Review Calendar</div>
      <div class="calendar-week-m">{''.join(cells)}</div>
      {''.join(rows)}
    </div>
    """, unsafe_allow_html=True)


def _render_launch_choice():
    choice = st.session_state.get("review_launch_choice")
    if not choice:
        return
    groups = choice.get("groups", {})
    label = choice.get("label", "Review")
    st.markdown(f'<div class="review-panel-m"><div class="panel-title-m">Choose Trainer</div><div style="color:#aab8d8;margin-bottom:10px;">{rc.esc(label)} has multiple sections. Pick one.</div>', unsafe_allow_html=True)
    for section, keys in groups.items():
        if st.button(f"{section} - {len(keys)} spots", key=rc.stable_key("launch_group_m", section + label), use_container_width=True):
            st.session_state.pop("review_launch_choice", None)
            rc.start_review_training(section, keys, label)
    if st.button("Cancel", key="cancel_group_launch_m", use_container_width=True):
        st.session_state.pop("review_launch_choice", None)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _period_filter(default_period):
    current = st.session_state.get("review_period_choice_m", default_period)
    if current not in rc.PERIODS:
        current = default_period
    period = st.radio(
        "Review period mobile",
        rc.PERIODS,
        index=rc.PERIODS.index(current),
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state.review_period_choice_m = period
    return period


def _section_filter():
    options = ["All"] + rc.SECTIONS
    current = st.session_state.get("review_section_choice_m", "All")
    if current not in options:
        current = "All"
    choice = st.radio(
        "Review sections mobile",
        options,
        index=options.index(current),
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state.review_section_choice_m = choice
    return rc.SECTIONS if choice == "All" else [choice]


def _queue_card(spot):
    progress = min(100, int((spot["total"] / 1000) * 100))
    due_text = "Late " + str(spot["late_days"]) + "d" if spot["late_days"] else ("Today" if spot["days_until"] == 0 else f"In {spot['days_until']}d")
    st.markdown(f"""
    <div class="queue-item-m">
      <div class="queue-name-m">{rc.esc(spot["display"])}</div>
      <div class="queue-detail-m">{rc.esc(spot["section"])} - {rc.esc(spot["detail"])}</div>
      <div class="pill-row-m">
        <div class="soft-pill-m">{rc.esc(due_text)}</div>
        <div class="soft-pill-m">{spot["accuracy"]:.1f}%</div>
        <div class="soft-pill-m">{spot["total"]}/1000</div>
      </div>
      <div class="progress-1000-m"><div style="width:{progress}%"></div></div>
    </div>
    """, unsafe_allow_html=True)
    c1, c2 = st.columns([0.48, 0.52])
    with c1:
        if st.button("Train", key=rc.stable_key("train_spot_m", spot["section"] + spot["key"]), use_container_width=True):
            rc.start_review_training(spot["section"], [spot["key"]], f"Review - {spot['display']}")
    with c2:
        if st.button("Hide from Review", key=rc.stable_key("hide_spot_m", spot["section"] + spot["key"]), use_container_width=True):
            rc.hide_spot(spot["section"], spot["key"])
            st.rerun()
    selected = st.checkbox("Select", key=rc.stable_key("select_spot_m", spot["section"] + spot["key"]))
    return selected


def show():
    _css()
    spots = rc.build_review_spots()
    counts = rc.bucket_counts(spots)
    sec_counts = rc.section_counts(spots)
    default_period = "Late" if counts.get("Late") else ("Today" if counts.get("Today") else ("Next 7 Days" if counts.get("Next 7 Days") else "Active Spots"))

    st.markdown('<div class="review-mobile">', unsafe_allow_html=True)
    st.markdown("""
    <div class="review-kicker-m">Repeat Queue</div>
    <div class="review-title-m">Today's Review Queue</div>
    <div class="review-copy-m">Late, due today, and upcoming spots. Only spots with 100+ hands are shown.</div>
    """, unsafe_allow_html=True)

    _settings_panel()

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="primary-review-btn">', unsafe_allow_html=True)
        if st.button("Train Today", use_container_width=True, key="review_train_today_m"):
            rc.request_grouped_launch("Today", [s for s in spots if s["bucket"] == "Today"])
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        if st.button("Train Late", use_container_width=True, key="review_train_late_m"):
            rc.request_grouped_launch("Late", [s for s in spots if s["bucket"] == "Late"])
    if st.button("Train Next 7 Days", use_container_width=True, key="review_train_next_m"):
        rc.request_grouped_launch("Next 7 Days", [s for s in spots if s["bucket"] == "Next 7 Days"])

    _metric_cards(counts, sec_counts)
    _render_launch_choice()
    st.markdown('<div class="review-filter-label-m">Queue</div>', unsafe_allow_html=True)
    period = _period_filter(default_period)
    st.markdown('<div class="review-filter-label-m">Sections</div>', unsafe_allow_html=True)
    sections = _section_filter()
    search = st.text_input("Search spots", placeholder="Board, line, scenario...")

    visible_spots = rc.filter_spots(spots, sections, period, search)
    if not visible_spots and period != "Active Spots":
        visible_spots = rc.filter_spots(spots, sections, "Active Spots", search)
        st.caption(f"No exact {period} matches, showing Active Spots.")

    st.markdown('<div class="queue-shell-m"><div class="panel-title-m">Smart Priority Queue</div></div>', unsafe_allow_html=True)
    selected_items = []
    if not visible_spots:
        st.info("No Review spots match the current filters.")
    for spot in visible_spots[:30]:
        if _queue_card(spot):
            selected_items.append(spot)
    if len(visible_spots) > 30:
        st.caption(f"Showing first 30 of {len(visible_spots)} spots.")
    if selected_items:
        st.markdown('<div class="primary-review-btn">', unsafe_allow_html=True)
        if st.button(f"Train Selected ({len(selected_items)})", key="train_selected_review_m", use_container_width=True):
            rc.request_grouped_launch("Selected Review Spots", selected_items)
        st.markdown("</div>", unsafe_allow_html=True)
    _calendar(spots)
    st.markdown("</div>", unsafe_allow_html=True)
