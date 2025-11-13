# Projekt_Zeiterfassung
Dieses Projekt dient der Zeiterfassung von Weiterbildungsmaßnahmen über 12 Monate. Die Daten werden über eine Streamlit-Eingabemaske erfasst, anschließend automatisch über eine ETL-Pipeline in Power Query transformiert und in Power BI visualisiert.

Projektübersicht

Ziel: Erfassen und Visualisieren von Weiterbildungszeiten und Lernarten über 12 Monate.

Technologien:

Streamlit – für die Eingabemaske

ETL (Extract, Transform, Load) – automatische Übertragung der Daten in Power Query

Power Query (Excel / Power BI) – zur Datenaufbereitung und Transformation

Power BI – zur Visualisierung der Daten

Features

Streamlit Eingabemaske

Erfassung von Kursen, Dauer (Stunden), Lernart (z. B. Präsenz, Online, Selbststudium) und Monat

Validierung der Eingaben

Automatische Übertragung der Eingabedaten in das Power Query Datenmodell (ETL)

Datenverarbeitung

Rohdaten werden automatisch importiert

Bereinigung, Aggregation und Berechnung von Gesamtstunden pro Monat / Lernart

Historisierung der Daten für Langzeit-Tracking

Visualisierung

Darstellung der Weiterbildungszeiten in Power BI

Interaktive Diagramme nach Monat, Kursart und Lernart

Trendanalysen über 12 Monate

ETL-Workflow

Extract: Streamlit speichert die Daten automatisch in einer CSV/SQL-Tabelle

Transform: Power Query verarbeitet die Rohdaten (Aggregation, Berechnung, Bereinigung)

Load: Die bereinigten Daten werden ins Power BI-Dashboard geladen

Optional: Automatisierung kann z. B. über geplante Tasks oder Power Automate erfolgen.

