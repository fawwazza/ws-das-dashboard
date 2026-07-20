"""
Fungsi bersama yang dipakai di app.py dan semua halaman di pages/.
Ditaruh di sini biar gak nulis ulang logic load-data di tiap file.
"""

import streamlit as st
import pandas as pd
import geopandas as gpd
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

# ============================================================
# CONFIG - nama kolom identifier di tabel RELASI (ws_provinsi.csv, dst).
# Ini beda dari tabel master (ws_master.csv dst) yg kolomnya udah
# kita seragamkan sendiri di script 03 (nama_ws, luas_ws_km2, dst).
# Tabel relasi masih pakai nama kolom ASLI dari data sumber kamu -
# SESUAIKAN kalau beda dari default di bawah.
# ============================================================
COL_WS_NAME = "WS"
COL_DAS_NAME = "NAMA_DAS"
COL_DAS_WS_INDUK = "WS"   # kolom WS induk di layer DAS (sesuaikan kalau beda)
COL_PROVINSI_NAME = "WADMPR"
COL_KABKOTA_NAME = "NAMOBJ"


@st.cache_data
def load_csv(filename: str) -> pd.DataFrame:
    """Load 1 file CSV dari folder data/, di-cache biar gak baca ulang tiap rerun."""
    return pd.read_csv(DATA_DIR / filename)


@st.cache_data
def load_geojson(filename: str) -> gpd.GeoDataFrame:
    """Load 1 file GeoJSON dari folder data/, di-cache biar gak baca ulang tiap rerun."""
    return gpd.read_file(DATA_DIR / filename)


@st.cache_data
def load_all_master_tables():
    """Load semua tabel master sekaligus, dipakai di halaman landing (app.py)."""
    return {
        "ws": load_csv("ws_master.csv"),
        "das": load_csv("das_master.csv"),
        "provinsi": load_csv("provinsi_master.csv"),
        "kabkota": load_csv("kabkota_master.csv"),
    }


def add_total_dan_persen(df: pd.DataFrame, kolom_nilai: str) -> pd.DataFrame:
    """
    Tambah kolom '% dari total' dan baris 'TOTAL' di baris paling bawah,
    dipakai buat tabel rekap luas/panjang di semua halaman biar konsisten.

    Params:
        df: DataFrame yang mau ditambahin (harus udah dalam bentuk final utk ditampilkan)
        kolom_nilai: nama kolom angka yang jadi dasar hitung persentase & total (misal "Luas (km²)")
    """
    if df.empty:
        return df

    df = df.copy()
    total = df[kolom_nilai].sum()
    df["% dari total"] = (df[kolom_nilai] / total * 100).round(1) if total else 0.0

    # Baris TOTAL - kolom non-angka diisi "TOTAL" di kolom pertama, kosong di kolom lain
    baris_total = {col: "" for col in df.columns}
    baris_total[df.columns[0]] = "TOTAL"
    baris_total[kolom_nilai] = round(total, 2)
    baris_total["% dari total"] = 100.0

    return pd.concat([df, pd.DataFrame([baris_total])], ignore_index=True)
