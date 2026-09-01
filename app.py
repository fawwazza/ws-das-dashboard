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
# 3. Footer kredit di sidebar - fixed di pojok kiri bawah layar.
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
        background-color: #F0F4F8;
        border: 1px solid #D5E0EB;
        border-left: 4px solid #F2B705;
        border-radius: 6px;
        padding: 10px 14px;
    }
    .sidebar-footer {
        position: fixed;
        bottom: 1rem;
        left: 1rem;
        width: 15rem;
        font-size: 0.75rem;
        color: #6b7785;
        line-height: 1.4;
        z-index: 999;
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
        "Dashboard ini menyajikan informasi geospasial mengenai Wilayah Sungai (WS) dan Daerah Aliran Sungai (DAS) di seluruh Indonesia, "
        "beserta keterkaitannya dengan wilayah administratif provinsi dan kabupaten/kota. Informasi disajikan secara interaktif "
        "untuk memudahkan pengguna dalam mengeksplorasi, memahami, dan menganalisis keterkaitan antarwilayah berdasarkan data spasial yang tersedia. "

        "Dashboard dilengkapi dengan fitur eksplorasi data, pencarian berdasarkan wilayah, clipping data berdasarkan WS yang dipilih, "
        "serta pengunduhan data spasial nasional yang telah dipotong per Wilayah Sungai. "
        "Fitur-fitur tersebut dirancang untuk memberikan akses data yang lebih praktis dan fleksibel, "
        "sehingga dapat mendukung kebutuhan analisis, perencanaan, dan pengelolaan sumber daya air."
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
        - **Kab/Kota** — Menampilkan WS & DAS apa saja yang ada di suatu kabupaten/kota.
        - **Clipping Tool** — Menyediakan fasilitas pemotongan data spasial berdasarkan batas Wilayah Sungai.
        - **Unduh Data Nasional** — Menyediakan data nasional yang telah dipotong per Wilayah Sungai dan siap untuk diunduh.
        """
    )

    st.divider()

    st.caption(
        "Dikembangkan oleh Subdirektorat Keterpaduan Pengelolaan SDA, "
        "Direktorat Jendral Sumber Daya Air, Kementerian Pekerjaan Umum."
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
        st.Page("pages/6_Data_Nasional.py", title="Unduh Data Nasional"),
    ]
)

pg.run()

st.sidebar.markdown(
    """
    <div class="sidebar-footer">
    Concept & Development by Fawwaz ZA.<br>
    </div>
    """,
    unsafe_allow_html=True,
)
