import pandas as pd
import re

def clean_dataframe_for_glue(df):
    replace_map = {"Datum": "", "Wochentag": "", "Kursname": "", "Lernart": "",
                   "Startzeit": "", "Endzeit": "", "Dauer (h)": 0}
    for col, val in replace_map.items():
        if col in df.columns:
            df[col] = df[col].fillna(val)
            if val != 0:
                df[col] = df[col].replace("", val)
            else:
                df[col] = df[col].apply(lambda x: float(str(x).replace(",", ".")) if x != "" else 0)
    return df

def detect_duration_column(df):
    for col in df.columns:
        if re.search(r"(dauer|stunden)", col, flags=re.IGNORECASE):
            return col
    return "Dauer (h)"

def normalize_duration_column_values(series):
    def fmt(v):
        if pd.isna(v) or v == "":
            return float("nan")
        if isinstance(v, (int, float)):
            return v
        return float(str(v).strip().replace(",", "."))
    return series.apply(fmt)
