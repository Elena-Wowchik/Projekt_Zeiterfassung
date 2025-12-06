# app.py (komplett korrigiert & stabilisiert)
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, date, time
import courses_module as cm

# ---------------------------------------------
# PAGE CONFIG
# ---------------------------------------------
st.set_page_config(page_title="Zeiterfassung", page_icon="⏱️", layout="wide")

# ---------------------------------------------
# CSV PATHS
# ---------------------------------------------
CSV_BASE = Path(__file__).parent / "zeittracking_gesamt.csv"
CSV_SAVE = Path(__file__).parent / "zeiterfassung.csv"

# ---------------------------------------------
# EXPECTED COLUMNS
# ---------------------------------------------
EXPECTED_COLS = [
    "Datum",
    "Wochentag",
    "Kursname",
    "Lernart",
    "Thema / Inhalt",
    "Startzeit",
    "Endzeit",
    "Dauer (h)",
    "Lernmodus / Quelle",
    "Beschreibung",
    "Created_at",
]

courses = cm.load_courses()


# ---------------------------------------------------------
# UTILS: delimiter detection
# ---------------------------------------------------------
def detect_delimiter(path: Path, default=","):
    if not path.exists():
        return default
    try:
        text = path.read_text(encoding="utf-8-sig")
    except:
        text = path.read_text(encoding="latin1")
    for line in text.splitlines():
        if line.strip():
            return "," if line.count(",") >= line.count(";") else ";"
    return default


# ---------------------------------------------------------
# Ensure correct columns
# ---------------------------------------------------------
def ensure_columns(df: pd.DataFrame):
    df = df.copy()
    for col in EXPECTED_COLS:
        if col not in df.columns:
            df[col] = pd.NA
    return df[EXPECTED_COLS]


# ---------------------------------------------------------
# Parse dates / times
# ---------------------------------------------------------
def parse_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Datum
    df["Datum"] = pd.to_datetime(df["Datum"], dayfirst=True, errors="coerce")

    # Zeit parser
    def parse_time(value, refdate):
        if pd.isna(value):
            return pd.NaT
        try:
            return pd.to_datetime(value)
        except:
            try:
                t = pd.to_datetime(str(value), errors="coerce").time()
                if refdate is not None and not pd.isna(refdate):
                    return datetime.combine(refdate.date(), t)
                return pd.NaT
            except:
                return pd.NaT

    starts, ends = [], []
    for _, row in df.iterrows():
        starts.append(parse_time(row["Startzeit"], row["Datum"]))
        ends.append(parse_time(row["Endzeit"], row["Datum"]))

    df["Startzeit"] = pd.to_datetime(starts, errors="coerce")
    df["Endzeit"] = pd.to_datetime(ends, errors="coerce")

    # Dauer
    df["Dauer (h)"] = (
        df["Dauer (h)"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .astype(float, errors="ignore")
    )

    mask = df["Dauer (h)"].isna() & df["Startzeit"].notna() & df["Endzeit"].notna()
    df.loc[mask, "Dauer (h)"] = (
        (df.loc[mask, "Endzeit"] - df.loc[mask, "Startzeit"]).dt.total_seconds() / 3600
    ).round(2)

    return df


# ---------------------------------------------------------
# FLEXIBLE CSV LOADER
# ---------------------------------------------------------
def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=EXPECTED_COLS)

    delim = detect_delimiter(path)

    for enc in ("utf-8-sig", "utf-8", "latin1"):
        try:
            df = pd.read_csv(path, sep=delim, encoding=enc, dtype=str)
            break
        except:
            df = None

    if df is None:
        df = pd.read_csv(path, sep=delim)

    df = df.replace({"": pd.NA})
    df = ensure_columns(df)
    df = parse_datetime_columns(df)
    return df


# ---------------------------------------------------------
# SAVE: robust + no empty rows
# ---------------------------------------------------------
def save_all(df: pd.DataFrame):
    df = ensure_columns(df)
    df = parse_datetime_columns(df)

    # Remove empty rows
    df = df.dropna(how="all", subset=EXPECTED_COLS)

    # Format Dauer als Dezimalpunkt
    df["Dauer (h)"] = df["Dauer (h)"].apply(
        lambda x: "" if pd.isna(x) else f"{float(x):.2f}"
    )

    # Format date/time columns
    for col in ["Datum", "Startzeit", "Endzeit", "Created_at"]:
        if col in df:
            df[col] = df[col].apply(
                lambda x: (
                    ""
                    if pd.isna(x)
                    else (x.isoformat() if hasattr(x, "isoformat") else str(x))
                )
            )

    delim = detect_delimiter(CSV_SAVE if CSV_SAVE.exists() else CSV_BASE)

    df.to_csv(CSV_SAVE, index=False, sep=delim, encoding="utf-8-sig")


# ---------------------------------------------------------
# INIT SESSION
# ---------------------------------------------------------
if "df" not in st.session_state:
    df_base = load_csv(CSV_BASE)
    if CSV_SAVE.exists():
        df_saved = load_csv(CSV_SAVE)
        st.session_state.df = pd.concat([df_base, df_saved], ignore_index=True)
    else:
        st.session_state.df = df_base.copy()


# ---------------------------------------------------------
# UI
# ---------------------------------------------------------
st.title("⏱️ Zeiterfassung – Eintrag erstellen")
st.write(f"Gesamtzeilen: {len(st.session_state.df):,}")

datum = st.date_input("Datum", value=date.today())

wochentag = st.selectbox(
    "Wochentag",
    ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"],
    index=datetime.today().weekday(),
)

kursname = st.selectbox("Kursname", options=courses)

lernart = st.selectbox(
    "Lernart",
    [
        "Selbststudium",
        "Live-Call-Vorlesung",
        "Theorie-Video",
        "Live-Call-Hausaufgaben",
        "Sonstiges",
    ],
)

thema = st.text_input("Thema / Inhalt")

col1, col2, col3 = st.columns([1.5, 1.5, 2])
with col1:
    start = st.time_input("Startzeit", value=time(9, 0))
with col2:
    end = st.time_input("Endzeit", value=time(10, 0))

start_dt = datetime.combine(datum, start)
end_dt = datetime.combine(datum, end)
computed_duration = round(((end_dt - start_dt).total_seconds() / 3600) % 24, 2)

with col3:
    dauer = st.number_input(
        "Dauer (h)",
        min_value=0.0,
        step=0.25,
        value=float(computed_duration),
        format="%.2f",
    )

lernmodus = st.selectbox(
    "Lernmodus / Quelle",
    [
        "Eigenständig",
        "Udemy",
        "DSI",
        "YouTube",
        "Excel",
        "Python",
        "GPT",
        "Buch",
        "Sonstiges",
    ],
)

beschreibung = st.text_area("Beschreibung / Notizen", height=80)


# ---------------------------------------------------------
# SAVE BUTTON
# ---------------------------------------------------------
if st.button("Speichern"):

    entry = {
        "Datum": datum.strftime("%d.%m.%Y"),
        "Wochentag": wochentag,
        "Kursname": kursname,
        "Lernart": lernart,
        "Thema / Inhalt": thema,
        "Startzeit": start_dt.isoformat(),
        "Endzeit": end_dt.isoformat(),
        "Dauer (h)": float(dauer),
        "Lernmodus / Quelle": lernmodus,
        "Beschreibung": beschreibung,
        "Created_at": datetime.now().isoformat(),
    }

    st.session_state.df = pd.concat(
        [st.session_state.df, pd.DataFrame([entry])], ignore_index=True
    )

    save_all(st.session_state.df)

    st.success(f"Eintrag gespeichert! Gespeichert in {CSV_SAVE.name}")
    st.dataframe(st.session_state.df.tail(10))
