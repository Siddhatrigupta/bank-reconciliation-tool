import pandas as pd


def classify_transaction(row, source):
    narration = str(row.get("Description", "")).lower()

    if any(x in narration for x in ["charge", "fee", "bank charge"]):
        return "Bank Charges"
    elif "interest" in narration:
        return "Interest"
    elif any(x in narration for x in ["cheque", "chq"]):
        return "Outstanding Cheque"
    elif source == "gl":
        return "Outstanding Cheque"
    else:
        return "Others"


def match_transactions(bank_df, gl_df, tolerance_days=2):

    matched = []
    unmatched_bank = []
    unmatched_gl = gl_df.copy()

    for i, b_row in bank_df.iterrows():
        found_match = False

        for j, g_row in unmatched_gl.iterrows():

            if pd.notna(b_row['Amount']) and pd.notna(g_row['Amount']):

                if abs(b_row['Amount'] - g_row['Amount']) == 0:
                    if pd.notna(b_row['Date']) and pd.notna(g_row['Date']):
                        if abs((b_row['Date'] - g_row['Date']).days) <= tolerance_days:

                            matched.append({
                                "Bank Date": b_row['Date'],
                                "GL Date": g_row['Date'],
                                "Amount": b_row['Amount'],
                                "Status": "Matched",
                                "Difference": 0,
                                "Category": "Matched"
                            })

                            unmatched_gl = unmatched_gl.drop(j)
                            found_match = True
                            break

        if not found_match:
            b_row["Category"] = classify_transaction(b_row, "bank")
            unmatched_bank.append(b_row)

    unmatched_gl['Category'] = unmatched_gl.apply(
        lambda x: classify_transaction(x, "gl"), axis=1
    )

    return pd.DataFrame(matched), pd.DataFrame(unmatched_bank), unmatched_gl
