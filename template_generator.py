import pandas as pd


def generate_summary(bank_df, gl_df, unmatched_bank, unmatched_gl):

    bank_balance = bank_df['Amount'].sum()
    gl_balance = gl_df['Amount'].sum()

    difference = bank_balance - gl_balance

    bank_charges = unmatched_bank[
        unmatched_bank['Category'] == "Bank Charges"
    ]['Amount'].sum()

    interest = unmatched_bank[
        unmatched_bank['Category'] == "Interest"
    ]['Amount'].sum()

    outstanding = unmatched_gl[
        unmatched_gl['Category'] == "Outstanding Cheque"
    ]['Amount'].sum()

    adjusted_balance = bank_balance + interest - bank_charges - outstanding

    summary = pd.DataFrame({
        "Particulars": [
            "Balance as per Bank",
            "Balance as per Books",
            "Difference",
            "Add: Interest",
            "Less: Bank Charges",
            "Less: Outstanding Cheques",
            "Adjusted Balance"
        ],
        "Amount": [
            bank_balance,
            gl_balance,
            difference,
            interest,
            -bank_charges,
            -outstanding,
            adjusted_balance
        ]
    })

    return summary


def generate_output(file_name, bank_df, gl_df, matched, unmatched_bank, unmatched_gl, company_name):

    summary = generate_summary(bank_df, gl_df, unmatched_bank, unmatched_gl)

    comment_map = {
        "Bank Charges": "Bank deducted charges not recorded in books",
        "Interest": "Interest credited by bank not recorded in books",
        "Outstanding Cheque": "Cheque issued but not cleared yet",
        "Others": "Needs manual review"
    }

    with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:

        # Sheet 1: Reconciliation Summary
        summary.to_excel(writer, sheet_name='Bank Reco', index=False)

        # Sheet 2: Matched
        matched.to_excel(writer, sheet_name='Matched', index=False)

        # Sheet 3: Unmatched Bank
        unmatched_bank.to_excel(writer, sheet_name='Unmatched Bank', index=False)

        # Sheet 4: Unmatched GL
        unmatched_gl.to_excel(writer, sheet_name='Unmatched GL', index=False)

        # Sheet 5: Comments
        comments = []

        for _, row in unmatched_bank.iterrows():
            comments.append({
                "Source": "Bank",
                "Amount": row.get("Amount"),
                "Category": row.get("Category"),
                "Comment": comment_map.get(row.get("Category"), "Check manually")
            })

        for _, row in unmatched_gl.iterrows():
            comments.append({
                "Source": "GL",
                "Amount": row.get("Amount"),
                "Category": row.get("Category"),
                "Comment": comment_map.get(row.get("Category"), "Check manually")
            })

        pd.DataFrame(comments).to_excel(writer, sheet_name='Comments', index=False)
