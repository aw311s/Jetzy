import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from jetzy_email.service import draft_email

st.set_page_config(page_title="Jetzy Investor Email Agent", layout="centered")
st.title("Jetzy Investor Email Agent")

with st.form("email_form"):
    st.subheader("Investor")
    inv_name = st.text_input("Name", "Everett Huang")
    inv_firm = st.text_input("Firm", "Legendary Ventures")
    inv_hooks = st.text_input("Hooks (comma-separated)", "former operator, technical founder, ML, full stack")
    inv_event = st.text_input("Context event", "7BC Global VC Demo Day (NYC)")

    st.subheader("Portfolio Themes")
    themes = st.multiselect(
        "Select themes",
        ["marketplace", "ai-ml", "consumer-tech", "travel"],
        default=["marketplace", "ai-ml"],
    )

    st.subheader("Jetzy Core")
    one_liner = st.text_input("One-liner", "Social-first, AI-powered travel platform for the experience economy.")
    positioning = st.text_input("Positioning", "community layer for the travel ecosystem")
    diffs = st.text_area(
        "Differentiators (one per line)",
        "proprietary AI and social graph that drives personalization\n"
        "community-driven marketplace flywheel\n"
        "authentic experiences + people-matching"
    )
    partners = st.text_input("Partnerships (comma-separated)", "Tourism boards: China, India")

    st.subheader("Traction (label: value per line)")
    traction_raw = st.text_area(
        "Items",
        "Users: 44,000+; ~25% MAU\n"
        "Growth: 100% organic; $0 paid marketing\n"
        "Revenue: ~$450K B2B; $2M+ pipeline"
    )

    submitted = st.form_submit_button("Generate Email")

if submitted:
    traction_items = []
    for line in traction_raw.splitlines():
        if ":" in line:
            label, value = line.split(":", 1)
            traction_items.append({"label": label.strip(), "value": value.strip()})

    payload = {
        "investor_profile": {
            "name": inv_name,
            "firm": inv_firm,
            "hooks": [h.strip() for h in inv_hooks.split(",") if h.strip()],
            "context_event": inv_event,
        },
        "portfolio_themes": themes,
        "jetzy_core": {
            "one_liner": one_liner,
            "positioning": positioning,
            "differentiators": [d.strip() for d in diffs.splitlines() if d.strip()],
            "partnerships": [p.strip() for p in partners.split(",") if p.strip()],
            "traction_items": traction_items,
        },
    }

    try:
        email_text = draft_email(payload)
        st.success("Draft generated")
        st.code(email_text, language="markdown")
    except Exception as e:
        st.error(f"Error: {e}")