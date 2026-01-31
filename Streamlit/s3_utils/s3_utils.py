import boto3
import pandas as pd
from io import StringIO
from config import S3_BUCKET, S3_KEY, REGION_NAME

s3 = boto3.client("s3", region_name=REGION_NAME)

def load_csv_from_s3():
    try:
        obj = s3.get_object(Bucket=S3_BUCKET, Key=S3_KEY)
        return pd.read_csv(obj["Body"], sep=";", encoding="cp1252")
    except s3.exceptions.NoSuchKey:
        columns = ["Datum","Wochentag","Kursname","Lernart","Startzeit","Endzeit","Dauer (h)"]
        return pd.DataFrame(columns=columns)

def save_csv_to_s3(df):
    buffer = StringIO()
    df.to_csv(buffer, sep=";", index=False, encoding="cp1252")
    s3.put_object(Bucket=S3_BUCKET, Key=S3_KEY, Body=buffer.getvalue().encode("cp1252"))
