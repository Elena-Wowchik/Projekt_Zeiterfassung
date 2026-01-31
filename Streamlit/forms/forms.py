import streamlit as st
from datetime import datetime, timedelta


def zeiterfassung_form():
    datum = st.date_input("Datum", value=datetime.today())
    # Wochentag auf Deutsch
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
    st.write(f"{datum.strftime('%d.%m.%Y')} – {weekday}")

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
    return submitted, datum, weekday, kursname, lernart, startzeit, endzeit, stunden
