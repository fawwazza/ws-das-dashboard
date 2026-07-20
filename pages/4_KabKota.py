import streamlit as st
import folium
from streamlit_folium import st_folium

from utils import load_csv, load_geojson, COL_KABKOTA_NAME, COL_WS_NAME, COL_DAS_NAME, add_total_dan_persen

st.title("Eksplorasi per Kabupaten/Kota")

# --- Load data ---
kabkota_master = load_csv("kabkota_master.csv")
kabkota_geo = load_geojson("kabkota_simplified.geojson")
ws_kabkota = load_csv("ws_kabkota.csv")
das_kabkota = load_csv("das_kabkota.csv")

# --- Sidebar ---
st.sidebar.header("Filter")
daftar_kabkota = sorted(kabkota_master[COL_KABKOTA_NAME].dropna().unique())
kabkota_terpilih = st.sidebar.selectbox("Pilih Kab/Kota", daftar_kabkota)

col_peta, col_detail = st.columns([1.4, 1])

with col_peta:
    st.subheader("Peta")

    geo_terpilih = kabkota_geo[kabkota_geo[COL_KABKOTA_NAME] == kabkota_terpilih]

    if geo_terpilih.empty:
        st.info("Geometri kab/kota ini tidak ditemukan di file geojson.")
    else:
        bounds = geo_terpilih.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2
        m = folium.Map(location=[center_lat, center_lon], tiles="CartoDB positron")

        folium.GeoJson(
            geo_terpilih,
            style_function=lambda f: {
                "fillColor": "#a855f7", "color": "#581c87", "weight": 2, "fillOpacity": 0.5
            },
            tooltip=folium.GeoJsonTooltip(fields=[COL_KABKOTA_NAME], aliases=["Kab/Kota:"]),
        ).add_to(m)

        m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
        st_folium(m, width=None, height=550, returned_objects=[], key=f"map_kab_{kabkota_terpilih}")

with col_detail:
    st.subheader(kabkota_terpilih)

    row = kabkota_master[kabkota_master[COL_KABKOTA_NAME] == kabkota_terpilih]
    if not row.empty:
        row = row.iloc[0]
        c1, c2 = st.columns(2)
        c1.metric("Jumlah WS", f"{int(row['jumlah_ws'])}")
        c2.metric("Jumlah DAS", f"{int(row['jumlah_das'])}")
        # Sama kayak halaman Provinsi: Luas WS & Luas DAS di sini secara teori
        # nilainya sama, jadi cukup 1 metric aja.
        st.metric("Luas Kab/Kota", f"{row['luas_ws_km2']:,.1f} km²")

    st.markdown("**Wilayah Sungai (WS) di kab/kota ini**")
    ws_di_kabkota = (
        ws_kabkota[ws_kabkota[COL_KABKOTA_NAME] == kabkota_terpilih]
        [[COL_WS_NAME, "luas_km2"]]
        .sort_values("luas_km2", ascending=False)
        .rename(columns={COL_WS_NAME: "WS", "luas_km2": "Luas (km²)"})
    )
    ws_di_kabkota = add_total_dan_persen(ws_di_kabkota, "Luas (km²)")
    st.dataframe(ws_di_kabkota, hide_index=True, use_container_width=True, height=200)

    st.markdown("**DAS di kab/kota ini**")
    das_di_kabkota = (
        das_kabkota[das_kabkota[COL_KABKOTA_NAME] == kabkota_terpilih]
        [[COL_DAS_NAME, "luas_km2"]]
        .sort_values("luas_km2", ascending=False)
        .rename(columns={COL_DAS_NAME: "DAS", "luas_km2": "Luas (km²)"})
    )
    das_di_kabkota = add_total_dan_persen(das_di_kabkota, "Luas (km²)")
    st.dataframe(das_di_kabkota, hide_index=True, use_container_width=True, height=250)
    st.caption(
        "Catatan: nama DAS bisa muncul lebih dari sekali di seluruh dataset "
        "(ada DAS berbeda dengan nama yang sama di WS/kab-kota lain)."
    )
