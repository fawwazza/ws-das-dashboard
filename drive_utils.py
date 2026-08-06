"""
Modul buat koneksi ke Google Drive API pakai Service Account.
Dipakai di halaman Streamlit buat listing & download file hasil clip.
"""

import io
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


@st.cache_resource
def get_drive_service():
    """
    Bikin koneksi ke Drive API pakai kredensial dari Streamlit Secrets.
    Di-cache pakai @st.cache_resource (bukan cache_data) karena ini objek
    koneksi/service, bukan data biasa - biar gak bikin ulang koneksi tiap rerun.
    """
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)


def download_file_bytes(file_id: str) -> bytes:
    """Download 1 file dari Drive berdasarkan ID-nya, kembalikan isinya sbg bytes."""
    service = get_drive_service()
    request = service.files().get_media(fileId=file_id)

    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()

    buf.seek(0)
    return buf.read()
