import streamlit as st
import pandas as pd

from forms.forms import zeiterfassung_form
from s3_utils.s3_utils import load_csv_from_s3, save_csv_to_s3
from data_cleaning.data_cleaning import (
    clean_dataframe_for_glue,
    detect_duration_column,
    normalize_duration_column_values,
)

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(page_title="Zeiterfassung", page_icon="⏰", layout="centered")
st.markdown(
    """
    <style>
    /* Sidebar Hintergrund */
    section[data-testid="stSidebar"] {
        background-color: #0b5ed7;
    }

    /* Sidebar Text */
    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Hauptbereich etwas Luft */
    .block-container {
        padding-top: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
# =====================================
# SIDEBAR (Design wie Power BI)
# =====================================
with st.sidebar:
    st.image("dsi-logo.png", width=250)
    st.markdown("## Zeiterfassung")
    st.markdown("Data Science Institute")

    namen = ["Elena Wowchik", "Max Mustermann", "Anna Beispiel"]

    name = st.selectbox("Name auswählen", namen, index=0)
    st.markdown(f"**{name}**")
# =====================================
# HAUPTBEREICH
# =====================================
st.title("⏰ Zeiterfassung – Lernzeiten")

# =====================================
# ZUGRIFFSLOGIK
# =====================================
if name != "Elena Wowchik":
    st.warning("⛔ Zugriff eingeschränkt")
    st.info("Bitte wähle **Elena Wowchik**, um die Zeiterfassung zu nutzen.")
    st.stop()

st.success(f"Willkommen {name} 👋")

# =====================================
# ZWEI SPALTEN
# =====================================
# anpassen, damit Spalten volle Breite nutzen
# ============================
st.markdown(
    """
    <style>
    /* Block-Container max-width entfernen */
    .block-container {
        padding-top: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 100% !important;
    }

    /* Tabellenbreite komplett */
    div[data-testid="stDataFrameContainer"] {
        width: 100% !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
col1, col2 = st.columns([1, 2], gap="large")  # Zwei Spalten

# ===============================
# LINKSE SPALTE – FORMULAR
# ===============================
with col1:
    with st.form("zeiterfassung_form"):
        submitted, datum, weekday, kursname, lernart, startzeit, endzeit, stunden = (
            zeiterfassung_form()
        )

    if submitted:
        if kursname.startswith("–") or lernart.startswith("–"):
            st.warning("Bitte Kurs und Lernart auswählen!")
            st.stop()

        # CSV laden
        df = load_csv_from_s3()
        df = clean_dataframe_for_glue(df)

        duration_col = detect_duration_column(df)
        if duration_col not in df.columns:
            df[duration_col] = 0

        df[duration_col] = normalize_duration_column_values(df[duration_col])

        # Neue Zeile
        neue_zeile = {
            "Datum": datum.strftime("%d.%m.%Y"),
            "Wochentag": weekday,
            "Kursname": kursname,
            "Lernart": lernart,
            "Startzeit": startzeit.strftime("%H:%M"),
            "Endzeit": endzeit.strftime("%H:%M"),
            duration_col: f"{stunden:g}".replace(".", ","),
        }

        df = pd.concat([df, pd.DataFrame([neue_zeile])], ignore_index=True)
        df[duration_col] = normalize_duration_column_values(df[duration_col])

        df = df[
            [
                "Datum",
                "Wochentag",
                "Kursname",
                "Lernart",
                "Startzeit",
                "Endzeit",
                duration_col,
            ]
        ]

        save_csv_to_s3(df)
        st.success("✅ Zeiterfassung erfolgreich in AWS S3 gespeichert!")

# ===============================
# RECHTE SPALTE – BISHERIGE EINTRÄGE
# ===============================
with col2:
    st.subheader("📋 Bisherige Einträge")

    df_display = load_csv_from_s3()
    df_display = clean_dataframe_for_glue(df_display)
    duration_col_display = detect_duration_column(df_display)

    if duration_col_display in df_display.columns:
        df_display[duration_col_display] = normalize_duration_column_values(
            df_display[duration_col_display]
        )

    # Button zum Löschen des letzten Eintrags
    if st.button("🗑️ Letzten Eintrag dauerhaft löschen"):
        if not df_display.empty:
            df_display = df_display.iloc[:-1]  # Letzte Zeile löschen
            save_csv_to_s3(df_display)  # CSV zurück zu S3 speichern
            st.success("✅ Letzter Eintrag wurde dauerhaft gelöscht!")

    # Tabelle anzeigen (neu geladen oder aktualisiert)
    st.dataframe(df_display.iloc[::-1])
