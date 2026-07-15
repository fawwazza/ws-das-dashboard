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
    """Load semua tabel master sekaligus, dipakai di halaman landing (Beranda.py)."""
    return {
        "ws": load_csv("ws_master.csv"),
        "das": load_csv("das_master.csv"),
        "provinsi": load_csv("provinsi_master.csv"),
        "kabkota": load_csv("kabkota_master.csv"),
    }
