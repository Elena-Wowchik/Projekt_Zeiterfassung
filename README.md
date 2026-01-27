# Projekt_Zeiterfassung (NOCH IN ARBEIT)
📌 Projektübersicht
[zeiterfassung_Projekt_Präsentation.pptx](https://github.com/user-attachments/files/24886483/zeiterfassung_Projekt_Prasentation.pptx)

![schemabild](https://github.com/user-attachments/assets/1d20d485-651c-4f5d-9555-25f0a6d36ee0)

Dieses Projekt ermöglicht die digitale Zeiterfassung von Lern- und Arbeitsstunden mit einer interaktiven Streamlit-App.
Die Daten werden als CSV gespeichert und können anschließend über AWS S3 → Glue/Athena in Power BI visualisiert werden.

Features:

Zeiterfassung nach Datum, Kurs, Lernart, Thema, Start-/Endzeit

Automatische Berechnung der Dauer

Einheitliche CSV-Formatierung (Datum: dd.mm.yyyy, Dauer: Stunden mit Komma)

Tabelle der bisherigen Einträge mit zuletzt hinzugefügtem Eintrag oben

Vorbereitung für AWS S3 Upload und Power BI Visualisierung

Robuste Handhabung alter CSV-Dateien und fehlender Spalten

🛠️ Technologien

Python 3.x

Streamlit → interaktive GUI

Pandas → Datenmanagement & CSV-Verarbeitung

Boto3 → AWS S3 Upload

AWS S3 / Glue / Athena → Speicherung und Abfrage

Power BI → Visualisierung & Reporting

Transform: Power Query verarbeitet die Rohdaten (Aggregation, Berechnung, Bereinigung)

Load: Die bereinigten Daten werden ins Power BI-Dashboard geladen




