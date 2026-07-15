import streamlit as st
from utils import load_all_master_tables

st.set_page_config(
    page_title="Dashboard Informasi Wilayah Sungai Indonesia",
    page_icon="🌏",
    layout="wide",
)

st.title("🌏 Dashboard Informasi Wilayah Sungai Indonesia")
st.markdown(
    "Eksplorasi data Wilayah Sungai (WS), Daerah Aliran Sungai (DAS), "
    "dan relasinya dengan wilayah administratif (Provinsi & Kabupaten/Kota) "
    "di seluruh Indonesia."
)

st.markdown(
    "Dashboard ini menyediakan informasi spasial Wilayah Sungai (WS) dan Daerah Aliran Sungai (DAS) di Indonesia. "
    "Pengguna dapat menelusuri hubungan WS, DAS, provinsi, dan kabupaten/kota secara interaktif untuk mendukung analisis, perencanaan, "
    "serta pengambilan keputusan di bidang sumber daya air."
)

st.divider()

# --- Ringkasan nasional ---
data = load_all_master_tables()
ws_df = data["ws"]
das_df = data["das"]
provinsi_df = data["provinsi"]
kabkota_df = data["kabkota"]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Wilayah Sungai", f"{len(ws_df):,}")
col2.metric("Daerah Aliran Sungai", f"{len(das_df):,}")
col3.metric("Provinsi", f"{len(provinsi_df):,}")
col4.metric("Luas Total Wilayah Sungai", f"{ws_df['luas_ws_km2'].sum():,.0f} km²")

st.divider()

st.markdown(
    """
    ### Mulai eksplorasi
    Pilih menu pada sidebar untuk menelusuri data berdasarkan kebutuhan.

    - **WS** — Menampilkan luas WS, jumlah DAS, serta provinsi dan kabupaten/kota yang berada di dalam suatu WS.
    - **DAS** — Menampilkan informasi DAS beserta Wilayah Sungai induknya, dan kabupaten/kota yang dilintasi DAS tersebut.
    - **Provinsi** — Menampilkan seluruh WS dan DAS yang berada atau melintasi provinsi terpilih.
    - **Kab/Kota** — Menampilkan seluruh WS dan DAS yang berada atau melintasi kabupaten/kota terpilih.
    """
)

st.divider()

st.caption(
    "Subdit Keterpaduan Pengelolaan Sumber Daya Air \n\n"
    "Direktorat Jenderal Sumber Daya Air \n\n"
    "Kementerian Pekerjaan Umum" 
)
