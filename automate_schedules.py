"""
Core logic: parse Accounting Pack → populate Schedules template.
Imported by app.py — no changes needed here month to month.
"""

import re, shutil, io
import pandas as pd
from openpyxl import load_workbook
from datetime import datetime


def parse_transactions(file_obj):
    df_raw = pd.read_excel(file_obj, sheet_name='Transaction List FTM', header=None)
    rows, current_date, current_vch_type, current_vch_no = [], None, None, None

    for _, row in df_raw.iterrows():
        date_val    = row[1]
        particulars = str(row[2]).strip()  if pd.notna(row[2])  else ''
        vch_type    = str(row[10]).strip() if pd.notna(row[10]) else ''
        vch_no      = str(row[11]).strip() if pd.notna(row[11]) else ''

        try: debit  = float(row[12]) if pd.notna(row[12]) else 0.0
        except: debit = 0.0
        try: credit = float(row[13]) if pd.notna(row[13]) else 0.0
        except: credit = 0.0
        try: net    = float(row[14]) if pd.notna(row[14]) else 0.0
        except: net = 0.0

        if isinstance(date_val, (pd.Timestamp, datetime)) and vch_type and vch_type != 'nan':
            current_date, current_vch_type, current_vch_no = date_val, vch_type, vch_no

        if re.match(r'^\d{4}', particulars):
            rows.append({'Date': current_date, 'Vch_Type': current_vch_type,
                         'Vch_No': current_vch_no, 'Account_Code': particulars[:4],
                         'Account_Name': particulars,
                         'Debit': debit, 'Credit': credit, 'Net': net})

    txn = pd.DataFrame(rows)
    agg = txn.groupby('Account_Code').agg(
        Total_Debit=('Debit', 'sum'), Total_Credit=('Credit', 'sum'),
        Net=('Net', 'sum'), Account_Name=('Account_Name', 'first')
    ).reset_index()
    return txn, agg


def dr(agg, code):
    r = agg[agg['Account_Code'] == code]
    return float(r['Total_Debit'].values[0]) if not r.empty else 0.0

def cr(agg, code):
    r = agg[agg['Account_Code'] == code]
    return float(r['Total_Credit'].values[0]) if not r.empty else 0.0

def dr_sum(agg, codes):
    return sum(dr(agg, c) for c in codes)

def sw(ws, row, col, value):
    cell = ws.cell(row=row, column=col)
    if cell.__class__.__name__ != 'MergedCell':
        cell.value = value


def populate_schedules(accounting_pack_file, template_path) -> bytes:
    """
    accounting_pack_file : file-like object (from st.file_uploader)
    template_path        : path to the Schedules template on disk
    Returns              : bytes of the populated Excel file
    """
    txn, agg = parse_transactions(accounting_pack_file)
    first_date = txn['Date'].dropna().iloc[0] if not txn['Date'].dropna().empty else datetime.today()
    month_label = first_date.strftime('%B %Y') if hasattr(first_date, 'strftime') else ''

    # Load template into memory buffer so we never modify the original
    with open(template_path, 'rb') as f:
        buf = io.BytesIO(f.read())
    wb = load_workbook(buf)

    # 1. Revenue Workings (col C=3, rows 6-26)
    ws = wb['Revenue Workings']
    rv = {
        6:  dr_sum(agg, ['5001', '5006']),
        7:  dr_sum(agg, ['5011', '5012']),
        8:  dr(agg, '5018'),
        9:  dr(agg, '5024'),
        10: dr_sum(agg, ['5019', '5021']),
        11: dr_sum(agg, ['5049', '5053']),
        12: dr_sum(agg, ['5032', '5033', '5034', '5035', '5037', '5038', '5039', '5040']),
        13: dr_sum(agg, ['5041', '5042', '5043', '5044', '5046']),
        14: 0,
        15: dr_sum(agg, ['5013', '5014', '5015', '5016']),
        16: dr_sum(agg, ['5054', '5056', '5057']),
        17: 0, 18: 0,
        19: dr(agg, '5017'),
        20: dr(agg, '5055'),
        21: dr(agg, '5048'),
        22: dr(agg, '5047'),
        23: dr(agg, '5079'),
        24: 0,
        25: dr_sum(agg, ['5072', '5073', '5074', '5075', '5076']),
        26: dr(agg, '5077'),
    }
    for r, v in rv.items():
        sw(ws, r, 3, v)

    # 2. Accrued Expenses (col D=4, rows 6-18)
    ws = wb['Accrued Expenses']
    ae = {6: dr(agg,'5048'), 7: dr_sum(agg,['5037','5038']),
          8: dr(agg,'5056'), 9:0,10:0,11:0,12:0,13:0,14:0,15:0,16:0,17:0,18:0}
    for r, v in ae.items():
        sw(ws, r, 4, v)

    # 3. Inter Company Payable
    ws = wb['Inter Company Payable']
    ic = txn[(txn['Account_Code'] == '2024') & (txn['Net'] < 0)].copy()
    r = 5
    for _, t in ic.iterrows():
        d = t['Date']
        ds = d.strftime('%d-%b-%Y') if (pd.notna(d) and hasattr(d, 'strftime')) else ''
        sw(ws, r, 2, ds); sw(ws, r, 3, 'Parent Company')
        sw(ws, r, 4, 'Advance Received'); sw(ws, r, 6, abs(t['Net']))
        r += 1
    sw(ws, 9, 6, cr(agg, '2024'))

    # 4. Accounts Payable
    ws = wb['Accounts Payable']
    ap = txn[(txn['Vch_Type']=='PURCHASE JOURNAL') & (txn['Account_Code']=='2001')].drop_duplicates('Vch_No')
    r = 5
    for _, t in ap.iterrows():
        d = t['Date']
        ds = d.strftime('%d-%b-%Y') if (pd.notna(d) and hasattr(d, 'strftime')) else ''
        sw(ws, r, 2, ds); sw(ws, r, 3, t['Vch_No'])
        sw(ws, r, 4, t['Account_Name']); sw(ws, r, 5, abs(t['Net']))
        r += 1

    # 5. Employee Payables (col C=3)
    ws = wb['Employee payables']
    sw(ws, 4, 3, month_label)
    sw(ws, 5, 3, cr(agg, '2003'))
    sw(ws, 6, 3, 0)
    sw(ws, 7, 3, cr(agg, '2004'))
    sw(ws, 8, 3, cr(agg, '2005'))

    # 6. Statutory Liability - Employees (col D=4)
    ws = wb['Statutory Liability - Employees']
    sw(ws, 4, 4, month_label)
    sw(ws, 5, 4, cr(agg, '2012'))
    sw(ws, 6, 4, cr(agg, '2013'))
    sw(ws, 7, 4, dr(agg, '2014'))

    # 7. Withholding Taxes (col D=4)
    ws = wb['Witholding taxes']
    sw(ws, 4, 4, month_label)
    tds_map = {'192': 5, '194 C': 6, '194 J': 7, '194 I': 8,
               '194 H': 9, '194 Q': 10, '195': 11}
    buckets = {r: 0.0 for r in range(5, 12)}
    for _, t in txn[txn['Account_Code'] == '2019'].iterrows():
        for key, rn in tds_map.items():
            if key in t['Account_Name']:
                buckets[rn] += abs(t['Net']); break
    for rn, v in buckets.items():
        sw(ws, rn, 4, v)

    # 8. Bank Balance (col C=3)
    ws = wb['Bank Balance']
    sw(ws, 5, 3, dr(agg, '1001') - cr(agg, '1001'))
    sw(ws, 5, 4, 0)

    # 9. Employee Provisions - Gratuity (col D=4)
    ws = wb['Employee Provisions']
    for r in range(6, 18):
        cm = ws.cell(row=r, column=3).value
        if isinstance(cm, (pd.Timestamp, datetime)):
            if cm.month == first_date.month and cm.year == first_date.year:
                sw(ws, r, 4, dr(agg, '5011')); break

    # 10. Provision for Income Tax (col E=5)
    ws = wb['Provision for Income tax']
    for r in range(7, 19):
        cm = ws.cell(row=r, column=4).value
        if isinstance(cm, (pd.Timestamp, datetime)):
            if cm.month == first_date.month and cm.year == first_date.year:
                sw(ws, r, 5, cr(agg, '2011')); break

    # Return as bytes
    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    return out.read(), month_label
