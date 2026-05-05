import pandas as pd

def clean_data(df):
    df.columns = df.columns.str.strip()
    return df

def standardize_columns(df, mapping):
    df = df.rename(columns=mapping)
    return df

def convert_types(df):
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    if 'Amount' in df.columns:
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    return df
