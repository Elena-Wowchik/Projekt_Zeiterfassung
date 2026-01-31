# hilfsfunktionen.py
from datetime import timedelta

def weekday_deutsch(datum):
    """
    Wandelt englischen Wochentag in Deutsch um.
    """
    tage_deutsch = {
        "Monday": "Montag",
        "Tuesday": "Dienstag",
        "Wednesday": "Mittwoch",
        "Thursday": "Donnerstag",
        "Friday": "Freitag",
        "Saturday": "Samstag",
        "Sunday": "Sonntag",
    }
    return tage_deutsch[datum.strftime("%A")]

def berechne_dauer_in_stunden(startzeit, endzeit):
    """
    Berechnet Dauer in Stunden zwischen zwei datetime.time Objekten.
    Berücksichtigt Fall über Mitternacht.
    """
    start_dt = timedelta(hours=startzeit.hour, minutes=startzeit.minute)
    end_dt = timedelta(hours=endzeit.hour, minutes=endzeit.minute)
    dauer = end_dt - start_dt
    if dauer.total_seconds() < 0:
        dauer += timedelta(days=1)
    return round(dauer.total_seconds() / 3600, 2)

def replace_comma_with_dot(value):
    """
    Ersetzt Komma durch Punkt, z. B. für DE/EN Zahlenformat.
    """
    if isinstance(value, str):
        return value.replace(",", ".")
    return value

def format_time_hhmm(t):
    """
    Formatiert datetime.time als HH:MM String
    """
    return t.strftime("%H:%M")
