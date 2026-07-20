import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

from utils import load_csv, load_geojson, COL_WS_NAME, COL_PROVINSI_NAME, COL_KABKOTA_NAME, add_total_dan_persen

st.title("Eksplorasi Wilayah Sungai (WS)")

# --- Load data ---
ws_master = load_csv("ws_master.csv")
ws_geo = load_geojson("ws_simplified.geojson")
ws_provinsi = load_csv("ws_provinsi.csv")
ws_kabkota = load_csv("ws_kabkota.csv")

# --- Sidebar: filter ---
st.sidebar.header("Filter")
daftar_ws = sorted(ws_master["nama_ws"].dropna().unique())
ws_terpilih = st.sidebar.selectbox("Pilih Wilayah Sungai", daftar_ws)

# --- Layout: peta di kiri, detail di kanan ---
col_peta, col_detail = st.columns([1.4, 1])

with col_peta:
    st.subheader("Peta")

    # Peta dasar, pusat di Indonesia
    m = folium.Map(location=[-2.5, 118], zoom_start=5, tiles="CartoDB positron")

    def style_function(feature):
        nama = feature["properties"].get(COL_WS_NAME)
        if nama == ws_terpilih:
            return {"fillColor": "#2563eb", "color": "#1e3a8a", "weight": 2, "fillOpacity": 0.6}
        return {"fillColor": "#94a3b8", "color": "#64748b", "weight": 0.5, "fillOpacity": 0.15}

    folium.GeoJson(
        ws_geo,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(fields=[COL_WS_NAME], aliases=["WS:"]),
    ).add_to(m)

    # Zoom otomatis ke WS yg dipilih
    ws_geom_terpilih = ws_geo[ws_geo[COL_WS_NAME] == ws_terpilih]
    if not ws_geom_terpilih.empty:
        bounds = ws_geom_terpilih.total_bounds  # [minx, miny, maxx, maxy]
        m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

    st_folium(m, width=None, height=550, returned_objects=[], key=f"map_ws_{ws_terpilih}")

with col_detail:
    st.subheader(ws_terpilih)

    row = ws_master[ws_master["nama_ws"] == ws_terpilih]
    if not row.empty:
        row = row.iloc[0]
        c1, c2 = st.columns(2)
        c1.metric("Luas WS", f"{row['luas_ws_km2']:,.1f} km²")
        c2.metric("Jumlah DAS", f"{int(row['jumlah_das'])}")
        if "kode_ws" in row.index and pd.notna(row.get("kode_ws")):
            st.caption(f"Kode WS: {row['kode_ws']}")
        if "status_ws" in row.index and pd.notna(row.get("status_ws")):
            st.markdown(f"**Status WS:** {row['status_ws']}")

    st.markdown("**Provinsi yang dilintasi**")
    prov_ws = (
        ws_provinsi[ws_provinsi[COL_WS_NAME] == ws_terpilih]
        [[COL_PROVINSI_NAME, "luas_km2"]]
        .sort_values("luas_km2", ascending=False)
        .rename(columns={COL_PROVINSI_NAME: "Provinsi", "luas_km2": "Luas (km²)"})
    )
    prov_ws = add_total_dan_persen(prov_ws, "Luas (km²)")
    st.dataframe(prov_ws, hide_index=True, use_container_width=True)

    st.markdown("**Kab/Kota yang dilintasi**")
    kab_ws = (
        ws_kabkota[ws_kabkota[COL_WS_NAME] == ws_terpilih]
        [[COL_KABKOTA_NAME, "luas_km2"]]
        .sort_values("luas_km2", ascending=False)
        .rename(columns={COL_KABKOTA_NAME: "Kab/Kota", "luas_km2": "Luas (km²)"})
    )
    kab_ws = add_total_dan_persen(kab_ws, "Luas (km²)")
    st.dataframe(kab_ws, hide_index=True, use_container_width=True, height=250)
