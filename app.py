import streamlit as st
import os
from automate_schedules import populate_schedules

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ANSR Global – Schedule Automation",
    page_icon="📊",
    layout="centered"
)

# ── Header ───────────────────────────────────────────────────────────────────
st.title("📊 ANSR Global – Schedule Automation")
st.markdown(
    "Upload the **Accounting Pack** for any month. "
    "The app will auto-populate all 10 schedule sheets and give you a ready-to-download Excel file."
)
st.divider()

# ── Template check ───────────────────────────────────────────────────────────
TEMPLATE_PATH = "Schedules_Template.xlsx"   # sits in the repo root

if not os.path.exists(TEMPLATE_PATH):
    st.error(
        f"❌ Schedules template not found: `{TEMPLATE_PATH}`\n\n"
        "Make sure `Schedules_Template.xlsx` is committed to the root of your GitHub repo."
    )
    st.stop()

# ── Upload ───────────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "Upload Accounting Pack (.xlsx)",
    type=["xlsx"],
    help="Must contain a sheet named 'Transaction List FTM'"
)

if uploaded:
    st.info(f"✅ File received: **{uploaded.name}**")

    with st.spinner("Processing transactions and populating schedules…"):
        try:
            output_bytes, month_label = populate_schedules(uploaded, TEMPLATE_PATH)
            filename = f"Schedules_{month_label.replace(' ', '_')}.xlsx"

            st.success(f"🎉 Done! Schedules populated for **{month_label}**")
            st.divider()

            # ── Download button ───────────────────────────────────────────
            st.download_button(
                label="⬇️  Download Populated Schedules",
                data=output_bytes,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

            # ── Quick summary ─────────────────────────────────────────────
            st.divider()
            st.markdown("**Sheets populated:**")
            sheets = [
                "Revenue Workings", "Accrued Expenses", "Inter Company Payable",
                "Accounts Payable", "Employee Payables", "Statutory Liability – Employees",
                "Withholding Taxes", "Bank Balance", "Employee Provisions",
                "Provision for Income Tax"
            ]
            cols = st.columns(2)
            for i, s in enumerate(sheets):
                cols[i % 2].markdown(f"✔️ {s}")

        except Exception as e:
            st.error(f"❌ Something went wrong:\n\n`{e}`")
            st.markdown(
                "**Common reasons:**\n"
                "- The sheet `Transaction List FTM` is missing or renamed\n"
                "- The file format is different from the expected template\n"
                "- Columns have shifted"
            )
else:
    st.markdown(
        """
        ### How it works
        1. Download the Accounting Pack from Tally for the month
        2. Upload it here  
        3. Download the auto-populated Schedules file  
        4. Review the few manual fields (ANSR Fees, CSR, bank statement balance)
        """
    )
