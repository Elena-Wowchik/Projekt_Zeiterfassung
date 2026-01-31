import pandas as pd

EXCEL_PATH = "D:/awrDATEN/lena/DATA SCIENCE INSTITUTE/Projekt_Zeiterfassung/Streamlit/Zeiterfassung_maerz_november.xlsm"

# Excel-Datei einlesen
xls = pd.read_excel(EXCEL_PATH, sheet_name=None)

# Alle Blätter prüfen
for name, df in xls.items():
    print(f"Blatt: {name}, Zeilen: {len(df)}, Spalten: {df.columns.tolist()}")

