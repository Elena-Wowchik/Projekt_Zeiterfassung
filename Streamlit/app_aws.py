# ==============================
#streamlit start: C:\Users\evovtch>D:
#D:\awrDATEN\lena\DATA SCIENCE INSTITUTE\Projekt_Zeiterfassung\Streamlit>streamlit run app_aws.py
#streamlit run "D:\awrDATEN\lena\DATA SCIENCE INSTITUTE\Projekt_Zeiterfassung\Streamlit\app_aws.py"

# IMPORTS
# ==============================
import streamlit as st  # Streamlit für Web-App UI
import sys  # Standardmodul, nicht direkt genutzt hier, evtl. für spätere Erweiterungen
import os  # Standardmodul, nicht direkt genutzt hier
import boto3  # AWS SDK für Python, Zugriff auf S3
from io import StringIO  # Für Zwischenspeicher von CSV-Daten
import pandas as pd  # Datenanalyse und DataFrame-Struktur
from datetime import datetime, timedelta  # Für Datum und Zeitberechnungen
import re  # Reguläre Ausdrücke, z.B. für Spalten-Erkennung

# ==============================
# AWS S3 KONFIGURATION
# ==============================
S3_BUCKET = "zeitefassung-bucket"  # Name des S3-Buckets
S3_KEY = "zeiterfassung/zeiterfassung.csv"  # Pfad/Key innerhalb des Buckets

# boto3-Client erstellen mit harten Zugangsdaten
# Hinweis: Für lokale Entwicklung funktioniert, in Produktion besser Umgebungsvariablen nutzen
s3 = boto3.client(
    "s3",
    region_name="eu-central-1",
    aws_access_key_id="AKIA45JVDZCWYG3OZDN3",
    aws_secret_access_key="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",
)

# ==============================
# S3-Verbindung testen
# ==============================
try:
    # ListObjects-Versuch, um zu prüfen, ob Lenawow IAM-Benutzer Zugriff auf den Bucket hat
    s3.list_objects_v2(Bucket="zeitefassung-bucket")
    print("S3 Zugriff OK ✅")  # Erfolgreiche Verbindung
except Exception as e:
    # Fehlermeldung, z.B. AccessDenied wenn Berechtigungen fehlen
    print(f"S3 Zugriff FEHLER ❌: {e}")

# ===========================
# Funktion zum Bereinigen aller Spalten
# ============================


def clean_dataframe_for_glue(df):
    """
    Alle leeren Zellen in DataFrame ersetzen, damit Glue die CSV korrekt erkennt.
    - Textspalten: "" (leer)
    - Zahlen/Double-Spalten: 0
    - Dauer-Spalte DE-Format (Komma statt Punkt)
    """
    # Mapping: Spaltenname → Ersatzwert
    replace_map = {
        "Datum": "",
        "Wochentag": "",
        "Kursname": "",
        "Lernart": "",
        "Startzeit": "",
        "Endzeit": "",
        "Dauer (h)": 0,
    }

    for col, val in replace_map.items():
        if col in df.columns:
            df[col] = df[col].fillna(val)  # NAs ersetzen
            if val != 0:
                df[col] = df[col].replace("", val)  # leere Strings ersetzen
            else:
                # Für Zahlen: Komma zu Punkt, als float
                df[col] = df[col].apply(
                    lambda x: float(str(x).replace(",", ".")) if x != "" else 0
                )

    return df


# ==============================
# STREAMLIT APP SETUP
# ==============================
st.set_page_config(page_title="Zeiterfassung", page_icon="⏰", layout="centered")
st.title("Zeiterfassung Fortführung")  # Titel der App

# ==============================
# HILFSFUNKTIONEN
# ==============================


def detect_duration_column(df):
    """
    Funktion: Versucht, die Spalte für Dauer/Stunden automatisch zu erkennen.
    - sucht nach 'dauer' oder 'stunden' (Groß-/Kleinschreibung egal)
    - falls keine Spalte gefunden, gibt Standard 'Dauer (h)' zurück
    """
    for col in df.columns:
        if re.search(r"(dauer|stunden)", col, flags=re.IGNORECASE):
            return col
    return "Dauer (h)"


def normalize_duration_column_values(series):
    """
    Funktion: Formatiert Werte in der Dauer-Spalte
    - Zahlen in String umwandeln
    - Punkt durch Komma ersetzen (DE-Format)
    - unnötige Nullen nach Komma entfernen
    """


def normalize_duration_column_values(series):
    def fmt(v):
        if pd.isna(v) or v == "":
            return float("nan")  # Leere Felder als NaN
        if isinstance(v, (int, float)):
            return v  # Zahl unverändert
        s = str(v).strip().replace(",", ".")  # Komma → Punkt
        return float(s)  # als float zurückgeben

    return series.apply(fmt)


def load_csv_from_s3():
    """
    Funktion: Lädt CSV aus S3
    - Wenn Datei existiert: als DataFrame zurückgeben
    - Wenn Key nicht existiert: neue leere DataFrame mit Standardspalten erstellen
    """
    try:
        obj = s3.get_object(Bucket=S3_BUCKET, Key=S3_KEY)
        return pd.read_csv(obj["Body"], sep=";", encoding="cp1252")
    except s3.exceptions.NoSuchKey:
        # Datei existiert noch nicht → leere Tabelle erstellen
        return pd.DataFrame(
            columns=[
                "Datum",
                "Wochentag",
                "Kursname",
                "Lernart",
                "Startzeit",
                "Endzeit",
                "Dauer (h)",
            ]
        )


def save_csv_to_s3(df):
    """
    Funktion: Speichert DataFrame als CSV in S3
    - Zwischenspeicher StringIO nutzen
    - Encoding cp1252 für Kompatibilität
    """
    buffer = StringIO()
    df.to_csv(buffer, sep=";", index=False, encoding="cp1252")
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=S3_KEY,
        Body=buffer.getvalue().encode("cp1252"),
    )


# ==============================
# STREAMLIT FORMULAR
# ==============================
with st.form("zeiterfassung_form"):
    datum = st.date_input("Datum", value=datetime.today())  # Datumsauswahl

    # Übersetzung Wochentag auf Deutsch
    tage_deutsch = {
        "Monday": "Montag",
        "Tuesday": "Dienstag",
        "Wednesday": "Mittwoch",
        "Thursday": "Donnerstag",
        "Friday": "Freitag",
        "Saturday": "Samstag",
        "Sunday": "Sonntag",
    }
    weekday = tage_deutsch[datum.strftime("%A")]
    st.write(f"{datum.strftime('%d.%m.%Y')} – {weekday}")  # Anzeige

    # Auswahl der Kurse
    kursname = st.selectbox(
        "Kurs",
        [
            "– bitte auswählen –",
            "AWS",
            "Excel",
            "EDA",
            "ETL",
            "Tableau",
            "SQL",
            "ScrumPO",
            "Teilprojekt",
            "PowerBI",
            "Machine Learning",
            "Docker",
            "GitHub",
            "Statistik",
            "NoSQL",
            "Python",
            "Streamlit",
            "Projekt",
            "BigData",
            "Organisation",
            "Karrierecoaching",
        ],
    )

    # Auswahl Lernart
    lernart = st.selectbox(
        "Lernart",
        [
            "– bitte auswählen –",
            "Theorie (Video)",
            "Live-Call-Vorlesung",
            "Selbststudium",
            "Live-Call-Hausaufgaben",
        ],
    )

    # Zeit-Eingabe
    startzeit = st.time_input("Startzeit")
    endzeit = st.time_input("Endzeit")

    # Dauer automatisch berechnen
    start_dt = timedelta(hours=startzeit.hour, minutes=startzeit.minute)
    end_dt = timedelta(hours=endzeit.hour, minutes=endzeit.minute)
    dauer = end_dt - start_dt
    if dauer.total_seconds() < 0:
        # Fall über Mitternacht
        dauer += timedelta(days=1)

    stunden = round(dauer.total_seconds() / 3600, 2)
    st.info(f"Dauer automatisch berechnet: {stunden} Stunden")

    # Button für Eintrag
    submitted = st.form_submit_button("Eintragen")

# ==============================
# SPEICHERN DER EINTRÄGE
# ==============================
if submitted:
    # Validierung: Kurs und Lernart müssen ausgewählt werden
    if kursname.startswith("–") or lernart.startswith("–"):
        st.warning("Bitte Kurs und Lernart auswählen!")
        st.stop()  # Stoppt die weitere Verarbeitung

    df = load_csv_from_s3()  # Alte CSV laden

    # **Neu: alle leeren Felder bereinigen**
    df = clean_dataframe_for_glue(df)

    duration_col = detect_duration_column(df)  # Spalte für Dauer erkennen
    if duration_col not in df.columns:
        df[duration_col] = 0

    # Dauer-Spalte normalisieren
    df[duration_col] = normalize_duration_column_values(df[duration_col])
    # Formatierung

    # Neue Zeile erstellen
    neue_zeile = {
        "Datum": datum.strftime("%d.%m.%Y"),
        "Wochentag": weekday,
        "Kursname": kursname,
        "Lernart": lernart,
        "Startzeit": startzeit.strftime("%H:%M"),
        "Endzeit": endzeit.strftime("%H:%M"),
        duration_col: f"{stunden:g}".replace(".", ","),
    }

    # Neue Zeile anhängen
    df = pd.concat([df, pd.DataFrame([neue_zeile])], ignore_index=True)
    df[duration_col] = normalize_duration_column_values(df[duration_col])

    # Spaltenreihenfolge erzwingen
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

    save_csv_to_s3(df)  # In S3 speichern
    st.success("Zeiterfassung erfolgreich in AWS S3 gespeichert!")

# ==============================
# ANZEIGE BISHERIGER EINTRÄGE
# ==============================
df_display = load_csv_from_s3()
df_display = clean_dataframe_for_glue(df_display)
duration_col_display = detect_duration_column(df_display)

if duration_col_display in df_display.columns:
    df_display[duration_col_display] = normalize_duration_column_values(
        df_display[duration_col_display]
    )

st.subheader("Bisherige Einträge")
st.dataframe(df_display.iloc[::-1])  # Neueste Einträge oben
