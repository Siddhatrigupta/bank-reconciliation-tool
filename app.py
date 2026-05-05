import streamlit as st
import pandas as pd

from utils import clean_data, standardize_columns, convert_types
from matching_engine import match_transactions
from template_generator import generate_output

st.set_page_config(page_title="Bank Reconciliation Tool", layout="wide")

st.title("🏦 Bank Reconciliation Tool (BlackLine Style)")

# Upload files
bank_file = st.file_uploader("Upload Bank Statement", type=["xlsx"])
gl_file = st.file_uploader("Upload GL / Accounting Data", type=["xlsx"])


def detect_company_name(df):
    for col in df.columns:
        for val in df[col].astype(str):
            val_lower = val.lower()
            if any(x in val_lower for x in ["ltd", "limited", "pvt", "private"]):
                return val.strip()
    return "Company"


if bank_file and gl_file:

    bank_df = pd.read_excel(bank_file)
    gl_df = pd.read_excel(gl_file)

    # Clean & convert
    bank_df = convert_types(clean_data(bank_df))
    gl_df = convert_types(clean_data(gl_df))

    # ⚠️ UPDATE THESE BASED ON YOUR FILE FORMAT
    bank_df = standardize_columns(bank_df, {
        "Txn Date": "Date",
        "Amount": "Amount",
        "Narration": "Description"
    })

    gl_df = standardize_columns(gl_df, {
        "Posting Date": "Date",
        "Amount": "Amount",
        "Description": "Description"
    })

    company_name = detect_company_name(gl_df)
    st.write(f"📌 Detected Company: {company_name}")

    if st.button("Run Reconciliation"):

        matched, unmatched_bank, unmatched_gl = match_transactions(bank_df, gl_df)

        st.success("✅ Reconciliation Completed!")

        # Summary
        bank_total = bank_df['Amount'].sum()
        gl_total = gl_df['Amount'].sum()
        difference = bank_total - gl_total

        st.subheader("📊 Reconciliation Summary")
        st.write({
            "Bank Balance": bank_total,
            "Books Balance": gl_total,
            "Difference": difference
        })

        # Display tables
        st.subheader("✅ Matched Transactions")
        st.dataframe(matched)

        st.subheader("❌ Unmatched Bank")
        st.dataframe(unmatched_bank)

        st.subheader("❌ Unmatched GL")
        st.dataframe(unmatched_gl)

        # Generate Excel
        output_file = f"{company_name}_Bank_Reco.xlsx"

        generate_output(
            output_file,
            bank_df,
            gl_df,
            matched,
            unmatched_bank,
            unmatched_gl,
            company_name
        )

        with open(output_file, "rb") as f:
            st.download_button("📥 Download Reconciliation File", f, file_name=output_file)
