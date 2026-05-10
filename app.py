import streamlit as st
import os
from automate_schedules import populate_schedules

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ANSR – Schedule Automation",
    page_icon="📊",
    layout="centered"
)

# ── Custom CSS (ANSR brand: teal + orange) ────────────────────────────────────
st.markdown("""
<style>
    /* Import font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Background */
    .stApp {
        background-color: #F4F6F9;
    }

    /* Hide Streamlit default header/footer */
    #MainMenu, footer, header { visibility: hidden; }

    /* ── Top navbar ── */
    .navbar {
        background: linear-gradient(135deg, #00677F 0%, #004F63 100%);
        padding: 18px 32px;
        border-radius: 0 0 16px 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 32px;
        box-shadow: 0 4px 20px rgba(0,103,127,0.25);
    }
    .navbar-title {
        color: white;
        font-size: 22px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .navbar-subtitle {
        color: rgba(255,255,255,0.75);
        font-size: 13px;
        margin-top: 2px;
    }
    .navbar-logo {
        background: white;
        color: #00677F;
        font-weight: 800;
        font-size: 20px;
        letter-spacing: 2px;
        padding: 8px 16px;
        border-radius: 8px;
    }

    /* ── Cards ── */
    .card {
        background: white;
        border-radius: 16px;
        padding: 28px 32px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        margin-bottom: 20px;
    }
    .card-title {
        font-size: 15px;
        font-weight: 600;
        color: #00677F;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    /* ── Step badges ── */
    .steps {
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
        margin-top: 12px;
    }
    .step {
        display: flex;
        align-items: center;
        gap: 10px;
        background: #F0FAFB;
        border: 1px solid #C8E8EE;
        border-radius: 10px;
        padding: 10px 16px;
        flex: 1;
        min-width: 160px;
    }
    .step-num {
        background: #00677F;
        color: white;
        border-radius: 50%;
        width: 26px;
        height: 26px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 13px;
        font-weight: 700;
        flex-shrink: 0;
    }
    .step-text {
        font-size: 13px;
        color: #2C3E50;
        line-height: 1.4;
    }

    /* ── Upload area styling ── */
    [data-testid="stFileUploader"] {
        border: 2px dashed #00677F !important;
        border-radius: 12px !important;
        background: #F0FAFB !important;
        padding: 8px !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #F47B20 !important;
        background: #FFF8F3 !important;
    }

    /* ── Download button ── */
    [data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, #F47B20 0%, #D4600A 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 14px 28px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(244,123,32,0.35) !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stDownloadButton"] > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(244,123,32,0.45) !important;
    }

    /* ── Success box ── */
    .success-box {
        background: linear-gradient(135deg, #E8F8F5 0%, #D5F5EE 100%);
        border: 1px solid #27AE60;
        border-radius: 12px;
        padding: 18px 24px;
        margin: 16px 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .success-icon { font-size: 28px; }
    .success-text { font-size: 15px; color: #1E8449; font-weight: 600; }

    /* ── Sheet checklist ── */
    .sheet-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-top: 12px;
    }
    .sheet-item {
        display: flex;
        align-items: center;
        gap: 8px;
        background: #F8FFFE;
        border: 1px solid #C8E8EE;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        color: #2C3E50;
    }
    .sheet-dot {
        width: 8px; height: 8px;
        background: #F47B20;
        border-radius: 50%;
        flex-shrink: 0;
    }

    /* ── Divider ── */
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #C8E8EE, transparent);
        margin: 20px 0;
    }

    /* ── Manual fields note ── */
    .note-box {
        background: #FFF8F0;
        border-left: 4px solid #F47B20;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        font-size: 13px;
        color: #7D4E00;
        margin-top: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ── Navbar ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
    <div>
        <div class="navbar-title">Schedule Automation</div>
        <div class="navbar-subtitle">Finance Operations · Internal Tool</div>
    </div>
    <div class="navbar-logo">ANSR</div>
</div>
""", unsafe_allow_html=True)

# ── Template check ────────────────────────────────────────────────────────────
TEMPLATE_PATH = "Schedules_Template.xlsx"
if not os.path.exists(TEMPLATE_PATH):
    st.error("❌ `Schedules_Template.xlsx` not found in the repo root. Please commit it to GitHub.")
    st.stop()

# ── How it works card ─────────────────────────────────────────────────────────
st.markdown("""
<div class="card">
    <div class="card-title">How it works</div>
    <div class="steps">
        <div class="step">
            <div class="step-num">1</div>
            <div class="step-text">Export Accounting Pack from Tally for the month</div>
        </div>
        <div class="step">
            <div class="step-num">2</div>
            <div class="step-text">Upload the <b>.xlsx</b> file below</div>
        </div>
        <div class="step">
            <div class="step-num">3</div>
            <div class="step-text">Download the fully populated Schedules file</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Upload card ───────────────────────────────────────────────────────────────
st.markdown('<div class="card"><div class="card-title">Upload Accounting Pack</div>', unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Drag & drop or browse — must contain sheet 'Transaction List FTM'",
    type=["xlsx"],
    label_visibility="visible"
)
st.markdown('</div>', unsafe_allow_html=True)

# ── Processing ────────────────────────────────────────────────────────────────
if uploaded:
    with st.spinner("⚙️  Reading transactions and populating all schedules…"):
        try:
            output_bytes, month_label = populate_schedules(uploaded, TEMPLATE_PATH)
            filename = f"Schedules_{month_label.replace(' ', '_')}.xlsx"

            # Success message
            st.markdown(f"""
            <div class="success-box">
                <div class="success-icon">✅</div>
                <div class="success-text">Done! Schedules populated for <u>{month_label}</u></div>
            </div>
            """, unsafe_allow_html=True)

            # Download button
            st.download_button(
                label=f"⬇️  Download  {filename}",
                data=output_bytes,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

            # Sheets populated
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            st.markdown('<div class="card-title" style="color:#00677F;font-size:13px;font-weight:600;letter-spacing:0.8px;text-transform:uppercase;">Sheets auto-populated</div>', unsafe_allow_html=True)
            sheets = [
                "Revenue Workings", "Accrued Expenses",
                "Inter Company Payable", "Accounts Payable",
                "Employee Payables", "Statutory Liability – Employees",
                "Withholding Taxes", "Bank Balance",
                "Employee Provisions", "Provision for Income Tax",
            ]
            grid_html = '<div class="sheet-grid">'
            for s in sheets:
                grid_html += f'<div class="sheet-item"><div class="sheet-dot"></div>{s}</div>'
            grid_html += '</div>'
            st.markdown(grid_html, unsafe_allow_html=True)

            # Manual fields note
            st.markdown("""
            <div class="note-box">
                ⚠️ <b>3 fields still need manual entry:</b>
                ANSR Fees · Bank Statement Balance · CSR / Membership amounts
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Error: `{e}`")
            st.markdown("""
            **Common causes:**
            - Sheet `Transaction List FTM` is missing or renamed
            - Columns have shifted from the expected format
            """)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; margin-top:48px; color:#9BA8B4; font-size:12px;">
    ANSR Global · Finance Operations · Internal Use Only
</div>
""", unsafe_allow_html=True)
