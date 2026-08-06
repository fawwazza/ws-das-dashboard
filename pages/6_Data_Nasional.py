import streamlit as st
import io
import zipfile

from utils import load_csv
from drive_utils import download_file_bytes

st.title("Unduh Data Nasional per WS")
st.caption(
    "Data Nasional yang sudah di-clip "
    "per Wilayah Sungai. Pilih WS, lalu pilih layer yang ingin diunduh."
)
st.caption(
    "Data Erosi. Sumber: KLHK 2022. Skala 1:250.000. \n \n"
    "Data Jenis Tanah. Sumber: FAO UNESCO 2007. Skala 1:3.000.000. \n \n"
    "Data Kawasan Hutan. Sumber: KEMENHUT 2024. Skala 1:50.000. \n \n"
    "Data RURHL DAS. Sumber: KEMENHUT 2025. Skala 1:50.000. \n \n"
    "Data Tutupan Lahan/Penutupan Lahan. Sumber: KLHK 2024. Skala 1:50.000. \n \n"
)

st.divider()

# --- Load data ---
ws_master = load_csv("ws_master.csv")
manifest = load_csv("drive_manifest.csv")

# --- Pilih WS ---
daftar_ws = sorted(ws_master["nama_ws"].dropna().unique())
ws_terpilih = st.selectbox("Pilih Wilayah Sungai", daftar_ws)

# Manifest pakai format underscore (WS_ACEH_MEUREUDU), sedangkan ws_master
# pakai format biasa (WS ACEH MEUREUDU) - normalisasi dulu biar bisa dicocokkan
ws_key = ws_terpilih.replace(" ", "_").replace("-", "_")

manifest_ws = manifest[manifest["ws_name"] == ws_key]

if manifest_ws.empty:
    st.warning(f"Belum ada data nasional yang tersedia untuk **{ws_terpilih}**.")
    st.stop()

daftar_layer = sorted(manifest_ws["layer_name"].unique())

st.markdown(f"**{len(daftar_layer)} layer tersedia** untuk {ws_terpilih}:")
layer_terpilih = st.multiselect(
    "Pilih layer yang ingin diunduh", daftar_layer, default=daftar_layer
)

st.divider()

if not layer_terpilih:
    st.info("Pilih minimal 1 layer di atas.")
    st.stop()

if st.button("⬇️ Siapkan Unduhan", type="primary"):
    baris_diambil = manifest_ws[manifest_ws["layer_name"].isin(layer_terpilih)]

    zip_buffer = io.BytesIO()
    progress = st.progress(0.0, text="Mengunduh dari Drive...")

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, (_, row) in enumerate(baris_diambil.iterrows()):
            progress.progress(
                (i + 1) / len(baris_diambil),
                text=f"Mengunduh {row['filename']}...",
            )
            file_bytes = download_file_bytes(row["drive_file_id"])
            zf.writestr(row["filename"], file_bytes)

    progress.progress(1.0, text="Selesai!")
    zip_buffer.seek(0)

    st.success(f"Berhasil menyiapkan {len(layer_terpilih)} layer untuk {ws_terpilih}.")
    st.download_button(
        label="⬇️ Download ZIP",
        data=zip_buffer,
        file_name=f"{ws_key}_data_nasional.zip",
        mime="application/zip",
    )
