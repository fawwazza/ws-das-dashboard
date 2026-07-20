import streamlit as st
import geopandas as gpd
import zipfile
import tempfile
import io
from pathlib import Path

from utils import load_csv, DATA_DIR
from clip_engine import (
    ensure_valid_geometry,
    reproject_if_needed,
    clip_layer,
    sanity_check_luas,
    load_ws_fullres,
    export_gdf,
)

# ============================================================
# CONFIG
# ============================================================

# Folder induk 124 subfolder WS full-res (struktur: WS_FULLRES_DIR/WS_XXX/WS_XXX.shp)
# Pakai DATA_DIR yg sama dari utils.py (root project/data/), BUKAN dihitung ulang
# di sini - soalnya file ini ada di dalam pages/, kalau dihitung dari sini
# hasilnya salah folder.
WS_FULLRES_DIR = DATA_DIR / "ws_fullres"

FORMAT_OPTIONS = {
    "Shapefile (.shp)": "shp",
    "GeoJSON (.geojson)": "geojson",
    "GeoPackage (.gpkg)": "gpkg",
}

st.title("Clipping Tool")
st.caption(
    "Upload data (.zip berisi shapefile), pilih Wilayah Sungai sebagai batas potong, "
    "lalu unduh hasilnya. Clip menggunakan geometri WS resolusi penuh (bukan versi "
    "sederhana yang dipakai di peta dashboard), jadi hasilnya presisi."
)

st.divider()

# ============================================================
# STEP 1 - Upload
# ============================================================

st.subheader("1. Upload data")
uploaded_zip = st.file_uploader(
    "Upload file .zip berisi shapefile (.shp + .shx + .dbf + .prj)", type="zip"
)

input_gdf = None
layer_name = None

if uploaded_zip is not None:
    with tempfile.TemporaryDirectory() as tmp_extract_dir:
        with zipfile.ZipFile(uploaded_zip) as zf:
            zf.extractall(tmp_extract_dir)

        shp_files = list(Path(tmp_extract_dir).rglob("*.shp"))

        if not shp_files:
            st.error("Tidak ditemukan file .shp di dalam zip yang diupload. Cek lagi isi zip-nya.")
        elif len(shp_files) > 1:
            st.error(
                f"Ditemukan {len(shp_files)} file .shp di dalam zip. "
                f"Untuk versi ini, upload cuma boleh berisi 1 shapefile saja."
            )
        else:
            shp_path = shp_files[0]
            layer_name = shp_path.stem  # nama layer = nama file, sesuai kesepakatan
            input_gdf = gpd.read_file(shp_path)
            # Baca ke memori sepenuhnya di sini karena file sumber di tmp_extract_dir
            # akan otomatis terhapus begitu blok 'with' ini selesai.

    if input_gdf is not None:
        st.success(f"Berhasil dibaca: **{layer_name}** ({len(input_gdf)} fitur, tipe {input_gdf.geom_type.iloc[0]})")

st.divider()

# ============================================================
# STEP 2 - Pilih WS
# ============================================================

st.subheader("2. Pilih Wilayah Sungai (boundary clip)")

ws_master = load_csv("ws_master.csv")
daftar_ws = sorted(ws_master["nama_ws"].dropna().unique())
ws_terpilih = st.multiselect("Pilih satu atau beberapa WS", daftar_ws)

st.divider()

# ============================================================
# STEP 3 - Format output
# ============================================================

st.subheader("3. Pilih format hasil")
format_label = st.radio("Format file hasil clip", list(FORMAT_OPTIONS.keys()), horizontal=True)
format_pilihan = FORMAT_OPTIONS[format_label]

st.divider()

# ============================================================
# STEP 4 - Proses
# ============================================================

st.subheader("4. Proses")

proses_diklik = st.button("🔪 Proses Clipping", type="primary", disabled=(input_gdf is None or not ws_terpilih))

if input_gdf is None:
    st.info("Upload data dulu di Step 1.")
elif not ws_terpilih:
    st.info("Pilih minimal 1 WS di Step 2.")

if proses_diklik and input_gdf is not None and ws_terpilih:
    with st.spinner("Memvalidasi geometry data input..."):
        input_gdf_valid = ensure_valid_geometry(input_gdf, label=layer_name)

    hasil_semua = {}
    progress = st.progress(0.0, text="Memulai proses clip...")

    for i, ws_name in enumerate(ws_terpilih):
        progress.progress((i) / len(ws_terpilih), text=f"Memproses {ws_name}...")

        try:
            ws_boundary = load_ws_fullres(ws_name, WS_FULLRES_DIR)
        except FileNotFoundError as e:
            st.error(str(e))
            continue

        input_proj = reproject_if_needed(input_gdf_valid, ws_boundary.crs)
        clipped = clip_layer(input_proj, ws_boundary, layer_name, ws_name)

        if clipped.empty:
            st.warning(f"Hasil clip untuk **{ws_name}** kosong (data tidak beririsan dengan WS ini).")
            continue

        sanity_check_luas(clipped, ws_boundary, label=f"{layer_name} x {ws_name}")
        hasil_semua[ws_name] = clipped

    progress.progress(1.0, text="Selesai!")

    if not hasil_semua:
        st.error("Tidak ada hasil clip yang valid dari semua WS yang dipilih.")
    else:
        st.success(f"Berhasil clip ke {len(hasil_semua)} WS.")

        # --- Preview ringkasan ---
        st.markdown("### Ringkasan hasil")
        for ws_name, gdf in hasil_semua.items():
            col1, col2 = st.columns(2)
            col1.metric(f"{ws_name} - jumlah fitur", len(gdf))
            if "luas_ha" in gdf.columns:
                col2.metric(f"{ws_name} - total luas", f"{gdf['luas_ha'].sum():,.1f} ha")
            elif "panjang_km" in gdf.columns:
                col2.metric(f"{ws_name} - total panjang", f"{gdf['panjang_km'].sum():,.1f} km")

        # --- Kemas semua hasil jadi 1 zip di memori (gak ditulis ke disk permanen) ---
        with tempfile.TemporaryDirectory() as tmp_out_dir:
            for ws_name, gdf in hasil_semua.items():
                nama_file_aman = ws_name.replace(" ", "_").replace("-", "_")
                out_path_no_ext = Path(tmp_out_dir) / f"{layer_name}_{nama_file_aman}"
                export_gdf(gdf, out_path_no_ext, format_pilihan)

            # Zip semua file hasil (utk shp, otomatis ikut semua sidecar file .shx/.dbf/.prj)
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for f in Path(tmp_out_dir).iterdir():
                    zf.write(f, arcname=f.name)
            zip_buffer.seek(0)

            st.download_button(
                label="⬇️ Download hasil (.zip)",
                data=zip_buffer,
                file_name=f"{layer_name}_clip_hasil.zip",
                mime="application/zip",
            )
