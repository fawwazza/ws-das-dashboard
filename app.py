import streamlit as st
from utils import load_all_master_tables

st.set_page_config(
    page_title="Dashboard WS & DAS Indonesia",
    page_icon="🌊",
    layout="wide",
)

st.title("🌊 Dashboard Wilayah Sungai & DAS Indonesia")
st.markdown(
    "Eksplorasi data spasial Wilayah Sungai (WS), Daerah Aliran Sungai (DAS), "
    "dan relasinya dengan wilayah administratif (Provinsi & Kabupaten/Kota) "
    "di seluruh Indonesia."
)

st.divider()

# --- Ringkasan nasional ---
data = load_all_master_tables()
ws_df = data["ws"]
das_df = data["das"]
provinsi_df = data["provinsi"]
kabkota_df = data["kabkota"]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Jumlah WS", f"{len(ws_df):,}")
col2.metric("Jumlah DAS", f"{len(das_df):,}")
col3.metric("Provinsi Terlibat", f"{len(provinsi_df):,}")
col4.metric("Luas Total WS", f"{ws_df['luas_ws_km2'].sum():,.0f} km²")

st.divider()

st.markdown(
    """
    ### Cara menjelajah
    Gunakan navigasi di **sidebar kiri** untuk memilih sudut pandang eksplorasi:

    - **WS** — jelajah per Wilayah Sungai, lihat DAS di dalamnya dan provinsi/kab-kota yang dilintasi
    - **DAS** — jelajah per Daerah Aliran Sungai
    - **Provinsi** — lihat WS & DAS apa saja yang ada di suatu provinsi
    - **Kab/Kota** — lihat WS & DAS apa saja yang ada di suatu kabupaten/kota
    """
)

st.caption(
    "Data diolah dari data internal Direktorat Jenderal Sumber Daya Air, "
    "Kementerian Pekerjaan Umum. Beberapa data telah disederhanakan untuk keperluan tampilan."
)
