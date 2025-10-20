import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from jetzy_email.service import draft_email

st.set_page_config(page_title="Jetzy Investor Email Agent", layout="centered")
st.title("Jetzy Investor Email Agent")

with st.form("email_form"):
    st.subheader("Investor & Event")
    c1, c2, c3 = st.columns(3)
    with c1:
        investor_first_name = st.text_input("Investor first name*", "Everett")
    with c2:
        firm = st.text_input("Firm*", "Legendary Ventures")
    with c3:
        context_event = st.text_input("Event*", "7BC Global VC Demo Day (NYC)")

    st.subheader("Personalization Lines")
    investor_background_line = st.text_input(
        "Investor background line*",
        "former operator and technical founder with expertise in ML and full-stack development"
    )
    firm_focus_line = st.text_input(
        "Firm focus line*",
        "marketplace and AI/ML-driven investments"
    )

    st.subheader("Traction & Proof")
    c4, c5 = st.columns(2)
    with c4:
        users_line = st.text_input("Users line*", "44,000+ users with ~25% MAU")
        growth_line = st.text_input("Growth line*", "entirely organic growth ($0 paid marketing)")
        revenue_line = st.text_input("Revenue line*", "~$450K in early B2B revenue")
    with c5:
        pipeline_line = st.text_input("Pipeline line*", "$2M+ pipeline")
        partnerships_line = st.text_input("Partnerships line*", "China and India")
        one_liner = st.text_input("One-liner (optional)", "")

    st.subheader("Closing")
    c6, c7 = st.columns(2)
    with c6:
        meeting_preference = st.selectbox("Meeting preference*", ["Either", "Zoom", "Coffee"], index=0)
    with c7:
        from_name = st.text_input("Signature name*", "Shama")

    submitted = st.form_submit_button("Generate Email")

if submitted:
    required = {
        "Investor first name": investor_first_name,
        "Firm": firm,
        "Event": context_event,
        "Investor background line": investor_background_line,
        "Firm focus line": firm_focus_line,
        "Users line": users_line,
        "Growth line": growth_line,
        "Revenue line": revenue_line,
        "Pipeline line": pipeline_line,
        "Partnerships line": partnerships_line,
        "Signature name": from_name,
    }
    missing = [k for k, v in required.items() if not v.strip()]
    if missing:
        st.error("Please fill the required fields: " + ", ".join(missing))
    else:
        payload = {
            "investor_first_name": investor_first_name.strip(),
            "firm": firm.strip(),
            "context_event": context_event.strip(),
            "investor_background_line": investor_background_line.strip(),
            "firm_focus_line": firm_focus_line.strip(),
            "users_line": users_line.strip(),
            "growth_line": growth_line.strip(),
            "revenue_line": revenue_line.strip(),
            "pipeline_line": pipeline_line.strip(),
            "partnerships_line": partnerships_line.strip(),
            "one_liner": (one_liner.strip() or None),
            "meeting_preference": meeting_preference,
            "from_name": from_name.strip(),
        }
        try:
            email_text = draft_email(payload)
            st.success("Draft generated")
            edited = st.text_area("Generated Email (editable):", email_text, height=520)
            st.download_button("⬇️ Download .txt", data=edited, file_name="jetzy_investor_email.txt", mime="text/plain")
        except Exception as e:
            import traceback
            st.error(f"Error: {e}")
            st.code("".join(traceback.format_exc()), language="python")