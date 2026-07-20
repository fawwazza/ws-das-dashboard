import streamlit as st
from utils import load_all_master_tables

st.set_page_config(
    page_title="Dashboard WS Indonesia",
    page_icon="🌏",
    layout="wide",
)

# CSS global - berlaku ke semua halaman karena dieksekusi di entry point (app.py)
# 1. Fix teks di st.metric() yang kepotong (...) kalau kepanjangan - biar wrap
#    ke baris baru & tetap kebaca semua, gak di-ellipsis paksa.
# 2. Aksen kuning tipis di border metric card, biar ada nuansa ala web instansi PU
#    (putih-biru-kuning), gak cuma putih-biru polos.
st.markdown(
    """
    <style>
    [data-testid="stMetricValue"] {
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
        font-size: 1.6rem !important;
        line-height: 1.3 !important;
    }
    [data-testid="stMetricLabel"] {
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
    }
    [data-testid="stMetric"] {
        background-color: #FAFAFA;
        border: 1px solid #E8E8E8;
        border-left: 4px solid #F2B705;
        border-radius: 6px;
        padding: 10px 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def halaman_beranda():
    st.title("🌏 Dashboard Wilayah Sungai Indonesia")
    st.markdown(
        "Eksplorasi data spasial Wilayah Sungai (WS), Daerah Aliran Sungai (DAS), "
        "dan relasinya dengan wilayah administratif (Provinsi & Kabupaten/Kota) "
        "di seluruh Indonesia."
    )

    st.markdown(
        "Dashboard ini menyediakan informasi spasial Wilayah Sungai (WS) dan Daerah Aliran Sungai (DAS) di Indonesia. "
        "Pengguna dapat menelusuri hubungan WS, DAS, provinsi, dan kabupaten/kota secara interaktif "
        "untuk mendukung analisis, perencanaan, serta pengambilan keputusan di bidang sumber daya air. "
    )
    st.divider()

    # --- Ringkasan nasional ---
    data = load_all_master_tables()
    ws_df = data["ws"]
    das_df = data["das"]
    provinsi_df = data["provinsi"]
    kabkota_df = data["kabkota"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Wilayah Sungai", f"{len(ws_df):,}")
    col2.metric("Daerah Aliran Sungai", f"{len(das_df):,}")
    col3.metric("Luas Total Wilayah Sungai", f"{ws_df['luas_ws_km2'].sum():,.0f} km²")

    st.divider()

    st.markdown(
        """
        ### Mulai eksplorasi
        Pilih menu pada sidebar untuk menelusuri data berdasarkan kebutuhan.

        - **WS** — Menampilkan luas WS, jumlah DAS, serta provinsi dan kabupaten/kota yang berada di dalam suatu WS.
        - **DAS** — Menampilkan informasi DAS beserta Wilayah Sungai induknya, dan kabupaten/kota yang dilintasi DAS tersebut.
        - **Provinsi** — Menampilkan seluruh WS dan DAS yang berada atau melintasi provinsi terpilih.
        - **Kab/Kota** — Menampilkan WS & DAS apa saja yang ada di suatu kabupaten/kota
        """
    )

    st.caption(
        "Data diolah dari data internal Direktorat Jenderal Sumber Daya Air, "
        "Kementerian Pekerjaan Umum. Beberapa data telah disederhanakan untuk keperluan tampilan."
    )


# --- Navigasi: label sidebar diatur di sini, TIDAK bergantung nama file ---
pg = st.navigation(
    [
        st.Page(halaman_beranda, title="Beranda", default=True),
        st.Page("pages/1_WS.py", title="WS"),
        st.Page("pages/2_DAS.py", title="DAS"),
        st.Page("pages/3_Provinsi.py", title="Provinsi"),
        st.Page("pages/4_KabKota.py", title="Kab/Kota"),
        st.Page("pages/5_Clipping_Tool.py", title="Clipping Tool"),
    ]
)
pg.run()
