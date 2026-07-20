import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

from utils import load_csv, load_geojson, COL_DAS_NAME, COL_DAS_WS_INDUK, COL_PROVINSI_NAME, COL_KABKOTA_NAME, add_total_dan_persen

st.title("Eksplorasi Daerah Aliran Sungai (DAS)")
st.caption(
    "Karena jumlah DAS sangat banyak (~42 ribu), pilih WS terlebih dahulu "
    "untuk mempersempit tampilan peta."
)

# --- Load tabel (ringan, aman di-load penuh) ---
ws_master = load_csv("ws_master.csv")
das_master = load_csv("das_master.csv")
das_provinsi = load_csv("das_provinsi.csv")
das_kabkota = load_csv("das_kabkota.csv")

# --- Sidebar: drill-down WS -> DAS ---
st.sidebar.header("Filter")
daftar_ws = sorted(ws_master["nama_ws"].dropna().unique())
ws_terpilih = st.sidebar.selectbox("1. Pilih WS", daftar_ws)

das_dalam_ws = das_master[das_master["nama_ws_induk"] == ws_terpilih]
daftar_das = sorted(das_dalam_ws["nama_das"].dropna().unique())

if not daftar_das:
    st.warning(f"Tidak ditemukan DAS untuk WS '{ws_terpilih}'. Cek konsistensi data.")
    st.stop()

das_terpilih = st.sidebar.selectbox(f"2. Pilih DAS ({len(daftar_das)} tersedia)", daftar_das)

# --- Load geometri DAS HANYA yg dibutuhkan (filter dulu sebelum render peta) ---
das_geo_full = load_geojson("das_simplified.geojson")
das_geo_dalam_ws = das_geo_full[das_geo_full[COL_DAS_WS_INDUK] == ws_terpilih]

# --- Layout: peta di kiri, detail di kanan ---
col_peta, col_detail = st.columns([1.4, 1])

with col_peta:
    st.subheader(f"Peta DAS dalam WS {ws_terpilih}")

    if das_geo_dalam_ws.empty:
        st.info("Geometri DAS untuk WS ini tidak ditemukan di file geojson.")
    else:
        bounds = das_geo_dalam_ws.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2
        m = folium.Map(location=[center_lat, center_lon], tiles="CartoDB positron")

        def style_function(feature):
            nama = feature["properties"].get(COL_DAS_NAME)
            if nama == das_terpilih:
                return {"fillColor": "#16a34a", "color": "#14532d", "weight": 2, "fillOpacity": 0.65}
            return {"fillColor": "#94a3b8", "color": "#64748b", "weight": 0.7, "fillOpacity": 0.25}

        folium.GeoJson(
            das_geo_dalam_ws,
            style_function=style_function,
            tooltip=folium.GeoJsonTooltip(fields=[COL_DAS_NAME], aliases=["DAS:"]),
        ).add_to(m)

        m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
        st_folium(m, width=None, height=550, returned_objects=[], key=f"map_das_{ws_terpilih}_{das_terpilih}")

with col_detail:
    st.subheader(das_terpilih)

    row = das_master[das_master["nama_das"] == das_terpilih]
    if not row.empty:
        row = row.iloc[0]

        c1, c2 = st.columns(2)

        with c1:
            st.metric("Luas DAS", f"{row['luas_das_km2']:,.1f} km²")

        with c2:
            st.markdown(f"""
            <div style="
                border:1px solid #e6e6e6;
                border-left:4px solid #f0b400;
                border-radius:8px;
                padding:16px;
                min-height:88px;
            ">
                <div style="font-size:14px;color:#6b7280;">
                    WS Induk
                </div>
                <div style="
                    font-size:18px;
                    font-weight:600;
                    margin-top:6px;
                    word-wrap:break-word;
                ">
                    {row["nama_ws_induk"]}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("**Provinsi yang dilintasi**")
    prov_das = (
        das_provinsi[das_provinsi[COL_DAS_NAME] == das_terpilih]
        [[COL_PROVINSI_NAME, "luas_km2"]]
        .sort_values("luas_km2", ascending=False)
        .rename(columns={COL_PROVINSI_NAME: "Provinsi", "luas_km2": "Luas (km²)"})
    )
    prov_das = add_total_dan_persen(prov_das, "Luas (km²)")
    st.dataframe(prov_das, hide_index=True, use_container_width=True)

    st.markdown("**Kab/Kota yang dilintasi**")
    kab_das = (
        das_kabkota[das_kabkota[COL_DAS_NAME] == das_terpilih]
        [[COL_KABKOTA_NAME, "luas_km2"]]
        .sort_values("luas_km2", ascending=False)
        .rename(columns={COL_KABKOTA_NAME: "Kab/Kota", "luas_km2": "Luas (km²)"})
    )
    kab_das = add_total_dan_persen(kab_das, "Luas (km²)")
    st.dataframe(kab_das, hide_index=True, use_container_width=True, height=250)

    st.divider()
    st.markdown(f"**Semua DAS dalam WS {ws_terpilih}** ({len(das_dalam_ws)} DAS)")
    tabel_das_dalam_ws = (
        das_dalam_ws[["nama_das", "luas_das_km2"]]
        .sort_values("luas_das_km2", ascending=False)
        .rename(columns={"nama_das": "Nama DAS", "luas_das_km2": "Luas (km²)"})
    )
    tabel_das_dalam_ws = add_total_dan_persen(tabel_das_dalam_ws, "Luas (km²)")
    st.dataframe(
        tabel_das_dalam_ws,
        hide_index=True,
        use_container_width=True,
        height=250,
    )
