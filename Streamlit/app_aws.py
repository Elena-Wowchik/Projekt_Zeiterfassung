from forms.forms import zeiterfassung_form
from s3_utils.s3_utils import load_csv_from_s3, save_csv_to_s3
from data_cleaning.data_cleaning import clean_dataframe_for_glue, detect_duration_column, normalize_duration_column_values
from utils.utils import weekday_deutsch, berechne_dauer_in_stunden, replace_comma_with_dot, format_time_hhmm
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Zeiterfassung", page_icon="⏰", layout="centered")
st.title("Zeiterfassung Fortführung")

with st.form("zeiterfassung_form"):
    submitted, datum, weekday, kursname, lernart, startzeit, endzeit, stunden = zeiterfassung_form()

if submitted:
    if kursname.startswith("–") or lernart.startswith("–"):
        st.warning("Bitte Kurs und Lernart auswählen!")
        st.stop()

    df = load_csv_from_s3()
    df = clean_dataframe_for_glue(df)
    duration_col = detect_duration_column(df)
    if duration_col not in df.columns:
        df[duration_col] = 0
    df[duration_col] = normalize_duration_column_values(df[duration_col])

    neue_zeile = {"Datum": datum.strftime("%d.%m.%Y"),
                  "Wochentag": weekday,
                  "Kursname": kursname,
                  "Lernart": lernart,
                  "Startzeit": startzeit.strftime("%H:%M"),
                  "Endzeit": endzeit.strftime("%H:%M"),
                  duration_col: f"{stunden:g}".replace(".", ",")}

    df = pd.concat([df, pd.DataFrame([neue_zeile])], ignore_index=True)
    df[duration_col] = normalize_duration_column_values(df[duration_col])
    df = df[["Datum","Wochentag","Kursname","Lernart","Startzeit","Endzeit",duration_col]]
    save_csv_to_s3(df)
    st.success("Zeiterfassung erfolgreich in AWS S3 gespeichert!")

# Bisherige Einträge
df_display = load_csv_from_s3()
df_display = clean_dataframe_for_glue(df_display)
duration_col_display = detect_duration_column(df_display)
df_display[duration_col_display] = normalize_duration_column_values(df_display[duration_col_display])
st.subheader("Bisherige Einträge")
st.dataframe(df_display.iloc[::-1])
