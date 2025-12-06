import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import re

CSV_FILE = "zeiterfassung.csv"
st.title("Zeiterfassung Fortführung")


def detect_duration_column(df):
    for col in df.columns:
        if re.search(r"(dauer|stunden)", col, flags=re.IGNORECASE):
            return col
    return "Dauer (h)"


def normalize_duration_column_values(series):
    def fmt(v):
        if pd.isna(v):
            return ""
        # numeric -> '3.5' oder '3' -> '3,5' bzw '3'
        if isinstance(v, (int, float)):
            s = f"{v:g}"  # 3.0 -> '3', 3.5 -> '3.5'
            return s.replace(".", ",")
        s = str(v).strip()
        # replace dot decimal sep with comma
        s = s.replace(".", ",")
        # remove trailing zero like '3,50' -> '3,5'
        s = re.sub(r",(\d)0+$", r",\1", s)
        return s

    return series.apply(fmt)


# Formular (wie gehabt)
with st.form("zeiterfassung_form"):
    datum = st.date_input("Datum", value=datetime.today())
    wochentag = st.selectbox(
        "Wochentag",
        [
            "Montag",
            "Dienstag",
            "Mittwoch",
            "Donnerstag",
            "Freitag",
            "Samstag",
            "Sonntag",
        ],
    )
    kursname = st.text_input("Kursname")
    lernart = st.selectbox(
        "Lernart", ["Theorie (Video)", "Live-Call-Vorlesung", "Selbststudium"]
    )
    thema = st.text_input("Thema")
    startzeit = st.time_input("Startzeit")
    endzeit = st.time_input("Endzeit")

    start_dt = timedelta(hours=startzeit.hour, minutes=startzeit.minute)
    end_dt = timedelta(hours=endzeit.hour, minutes=endzeit.minute)
    dauer = end_dt - start_dt
    if dauer.total_seconds() < 0:
        dauer += timedelta(days=1)
    stunden = round(dauer.total_seconds() / 3600, 2)
    st.info(f"Dauer automatisch berechnet: {stunden} Stunden")

    submitted = st.form_submit_button("Eintragen")

    if submitted:
        # lade Datei (cp1252 für Umlaute)
        try:
            df = pd.read_csv(CSV_FILE, sep=";", encoding="cp1252")
        except FileNotFoundError:
            df = pd.DataFrame(
                columns=[
                    "Datum",
                    "Wochentag",
                    "Kursname",
                    "Lernart",
                    "Thema",
                    "Startzeit",
                    "Endzeit",
                    "Dauer (h)",
                ]
            )

        # Erkenne Durations-Spalte
        duration_col = detect_duration_column(df)
        if duration_col not in df.columns:
            df[duration_col] = ""

        # Normalisiere EXISTIERENDE Werte (wichtig!)
        df[duration_col] = normalize_duration_column_values(df[duration_col])

        # Erzeuge Dauer-String für den neuen Eintrag (deutsches Format)
        dauer_str = f"{stunden:g}".replace(".", ",")

        neue_zeile = {
            "Datum": datum.strftime("%d.%m.%Y"),
            "Wochentag": wochentag,
            "Kursname": kursname,
            "Lernart": lernart,
            "Thema": thema,
            "Startzeit": startzeit.strftime("%H:%M"),
            "Endzeit": endzeit.strftime("%H:%M"),
            duration_col: dauer_str,
        }

        # Anhängen
        df = pd.concat([df, pd.DataFrame([neue_zeile])], ignore_index=True)

        # ***WICHTIG: Nochmals komplette Dauer-Spalte normalisieren (falls der Datentyp beim concat geändert wurde)***
        df[duration_col] = normalize_duration_column_values(df[duration_col])

        # Optional: gewünschte Spaltenreihenfolge (ändert nichts an zusätzlichen Spalten, die vorhanden sind)
        cols_wanted = [
            "Datum",
            "Wochentag",
            "Kursname",
            "Lernart",
            "Thema",
            "Startzeit",
            "Endzeit",
            duration_col,
        ]
        cols_final = [c for c in cols_wanted if c in df.columns] + [
            c for c in df.columns if c not in cols_wanted
        ]
        df = df[cols_final]

        # Speichern (cp1252 für Umlaute). Jetzt sind alle Dauer-Werte Strings wie '3,5'.
        df.to_csv(CSV_FILE, sep=";", index=False, encoding="cp1252")
        st.success("Zeiterfassung erfolgreich gespeichert!")

# Anzeige: lade und zeige normalisierte Datei
try:
    df_display = pd.read_csv(CSV_FILE, sep=";", encoding="cp1252")
    duration_col_display = detect_duration_column(df_display)
    if duration_col_display in df_display.columns:
        df_display[duration_col_display] = normalize_duration_column_values(
            df_display[duration_col_display]
        )
    st.subheader("Bisherige Einträge")
    st.dataframe(df_display)
except FileNotFoundError:
    st.info("Noch keine Einträge vorhanden.")
