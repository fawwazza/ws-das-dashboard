import streamlit as st
import folium
from streamlit_folium import st_folium

from utils import load_csv, load_geojson, COL_PROVINSI_NAME, COL_WS_NAME, COL_DAS_NAME

st.set_page_config(page_title="Provinsi - Dashboard WS & DAS", page_icon="🌊", layout="wide")

st.title("Eksplorasi per Provinsi")

# --- Load data ---
provinsi_master = load_csv("provinsi_master.csv")
provinsi_geo = load_geojson("provinsi_simplified.geojson")
ws_provinsi = load_csv("ws_provinsi.csv")
das_provinsi = load_csv("das_provinsi.csv")

# --- Sidebar ---
st.sidebar.header("Filter")
daftar_provinsi = sorted(provinsi_master[COL_PROVINSI_NAME].dropna().unique())
provinsi_terpilih = st.sidebar.selectbox("Pilih Provinsi", daftar_provinsi)

col_peta, col_detail = st.columns([1.4, 1])

with col_peta:
    st.subheader("Peta")

    geo_terpilih = provinsi_geo[provinsi_geo[COL_PROVINSI_NAME] == provinsi_terpilih]

    if geo_terpilih.empty:
        st.info("Geometri provinsi ini tidak ditemukan di file geojson.")
    else:
        bounds = geo_terpilih.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2
        m = folium.Map(location=[center_lat, center_lon], tiles="CartoDB positron")

        folium.GeoJson(
            geo_terpilih,
            style_function=lambda f: {
                "fillColor": "#f59e0b", "color": "#92400e", "weight": 2, "fillOpacity": 0.5
            },
            tooltip=folium.GeoJsonTooltip(fields=[COL_PROVINSI_NAME], aliases=["Provinsi:"]),
        ).add_to(m)

        m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
        st_folium(m, width=None, height=550, returned_objects=[], key=f"map_prov_{provinsi_terpilih}")

with col_detail:
    st.subheader(provinsi_terpilih)

    row = provinsi_master[provinsi_master[COL_PROVINSI_NAME] == provinsi_terpilih]
    if not row.empty:
        row = row.iloc[0]
        c1, c2 = st.columns(2)
        c1.metric("Jumlah WS", f"{int(row['jumlah_ws'])}")
        c2.metric("Jumlah DAS", f"{int(row['jumlah_das'])}")
        c3, c4 = st.columns(2)
        c3.metric("Luas WS di sini", f"{row['luas_ws_km2']:,.1f} km²")
        c4.metric("Luas DAS di sini", f"{row['luas_das_km2']:,.1f} km²")

    st.markdown("**Wilayah Sungai (WS) di provinsi ini**")
    ws_di_provinsi = (
        ws_provinsi[ws_provinsi[COL_PROVINSI_NAME] == provinsi_terpilih]
        [[COL_WS_NAME, "luas_km2"]]
        .sort_values("luas_km2", ascending=False)
        .rename(columns={COL_WS_NAME: "WS", "luas_km2": "Luas (km²)"})
    )
    st.dataframe(ws_di_provinsi, hide_index=True, use_container_width=True, height=200)

    st.markdown("**DAS di provinsi ini**")
    das_di_provinsi = (
        das_provinsi[das_provinsi[COL_PROVINSI_NAME] == provinsi_terpilih]
        [[COL_DAS_NAME, "luas_km2"]]
        .sort_values("luas_km2", ascending=False)
        .rename(columns={COL_DAS_NAME: "DAS", "luas_km2": "Luas (km²)"})
    )
    st.dataframe(das_di_provinsi, hide_index=True, use_container_width=True, height=250)
    st.caption(
        "Catatan: nama DAS bisa muncul lebih dari sekali di seluruh dataset "
        "(ada DAS berbeda dengan nama yang sama di WS/provinsi lain)."
    )
