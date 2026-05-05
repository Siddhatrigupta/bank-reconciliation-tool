import pandas as pd

def generate_summary(bank_df, gl_df, unmatched_bank, unmatched_gl):

    bank_balance = bank_df['Amount'].sum()
    gl_balance = gl_df['Amount'].sum()

    diff = bank_balance - gl_balance

    bank_charges = unmatched_bank[unmatched_bank['Category'] == "Bank Charges"]['Amount'].sum()
    interest = unmatched_bank[unmatched_bank['Category'] == "Interest"]['Amount'].sum()
    outstanding = unmatched_gl[unmatched_gl['Category'] == "Outstanding Cheque"]['Amount'].sum()

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
            diff,
            interest,
            -bank_charges,
            -outstanding,
            bank_balance + interest - bank_charges - outstanding
        ]
    })

    return summary


def generate_output(file_name, bank_df, gl_df, matched, unmatched_bank, unmatched_gl, company_name):

    summary = generate_summary(bank_df, gl_df, unmatched_bank, unmatched_gl)

    with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:

        # Sheet 1: Reconciliation (Template Style)
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
                "Type": "Bank",
                "Amount": row.get("Amount"),
                "Category": row.get("Category"),
                "Comment": f"{row.get('Category')} - Not in GL"
            })

        for _, row in unmatched_gl.iterrows():
            comments.append({
                "Type": "GL",
                "Amount": row.get("Amount"),
                "Category": row.get("Category"),
                "Comment": f"{row.get('Category')} - Not in Bank"
            })

        pd.DataFrame(comments).to_excel(writer, sheet_name='Comments', index=False)
