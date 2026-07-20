"""
Modul core buat clipping shapefile berdasarkan boundary WS.
Generic buat semua tipe geometry (Polygon, Line, Point).

Dipakai baik untuk testing lokal maupun nanti diimport ke halaman Streamlit.
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path


def export_gdf(gdf: gpd.GeoDataFrame, out_path_no_ext: Path, format: str) -> Path:
    """
    Export GeoDataFrame ke format pilihan user.

    Params:
        gdf: hasil clip yang mau disimpan
        out_path_no_ext: path TANPA ekstensi (ekstensi ditentukan otomatis dari format)
        format: salah satu dari "shp", "geojson", "gpkg"

    Returns:
        Path lengkap file yang tersimpan (file utama; shp punya file pendamping lain juga).
    """
    driver_map = {
        "shp": ("ESRI Shapefile", ".shp"),
        "geojson": ("GeoJSON", ".geojson"),
        "gpkg": ("GPKG", ".gpkg"),
    }
    if format not in driver_map:
        raise ValueError(f"Format '{format}' tidak dikenal. Pilihan: {list(driver_map.keys())}")

    driver, ext = driver_map[format]
    out_path = Path(str(out_path_no_ext) + ext)
    gdf.to_file(out_path, driver=driver)
    return out_path


def load_shapefile(path) -> gpd.GeoDataFrame:
    """Baca shapefile generic, dipakai buat baca layer INPUT (erosi, PL, dst)."""
    return gpd.read_file(path)


def get_ws_fullres_path(ws_name: str, base_dir: str) -> Path:
    """
    Cari path shp full-res buat 1 WS, berdasarkan struktur folder konsisten:
        base_dir/WS_XXX/WS_XXX.shp

    Params:
        ws_name: nama WS persis seperti di atribut data (misal "WS KAYAN BELAYAU")
        base_dir: folder induk tempat semua subfolder per-WS disimpan

    Returns:
        Path ke file .shp yang sesuai.

    Raises:
        FileNotFoundError kalau file/foldernya gak ketemu - biar error-nya
        jelas dan gampang di-debug (bukan silent error pas dipakai user nanti).
    """
    # Normalisasi nama WS ke pola nama folder: spasi DAN strip (-) sama-sama
    # diganti underscore (ketauan dari struktur folder asli kamu, misal
    # "WS KEPULAUAN YAMDENA-WETAR-KEI-ARU" -> "WS_KEPULAUAN_YAMDENA_WETAR_KEI_ARU")
    nama_folder = ws_name.replace(" ", "_").replace("-", "_")
    candidate = Path(base_dir) / nama_folder / f"{nama_folder}.shp"

    if not candidate.exists():
        raise FileNotFoundError(
            f"File full-res untuk WS '{ws_name}' tidak ditemukan di: {candidate}\n"
            f"Cek lagi apakah nama folder/file-nya konsisten dengan pola 'WS_XXX'."
        )

    return candidate


def load_ws_fullres(ws_name: str, base_dir: str) -> gpd.GeoDataFrame:
    """
    Load geometry full-res 1 WS langsung dari file per-WS-nya (BUKAN dari
    file gabungan nasional) - jauh lebih ringan karena cuma baca 1 file kecil
    (~beberapa MB), bukan file gabungan yang bisa ratusan MB.
    """
    path = get_ws_fullres_path(ws_name, base_dir)
    return gpd.read_file(path)


def ensure_valid_geometry(gdf: gpd.GeoDataFrame, label: str = "") -> gpd.GeoDataFrame:
    """
    Perbaiki geometry invalid pakai make_valid() (fungsi resmi GEOS, lebih
    modern & lebih menjaga bentuk asli dibanding trik buffer(0) lama).

    PENTING: panggil fungsi ini SEKALI SAJA per layer input, SEBELUM loop
    clip ke banyak WS - bukan di dalam clip_layer(). Kalau dipanggil ulang
    tiap WS, layer yang sama diperiksa & diperbaiki berkali-kali, boros waktu
    tanpa manfaat tambahan (hasil validasinya kan sama aja).
    """
    gdf = gdf.copy()
    invalid_mask = ~gdf.geometry.is_valid
    n_invalid = invalid_mask.sum()

    if n_invalid > 0:
        print(f"  [{label}] Memperbaiki {n_invalid} geometry invalid (make_valid())...")
        gdf.loc[invalid_mask, "geometry"] = gdf.loc[invalid_mask, "geometry"].make_valid()

    return gdf


def reproject_if_needed(gdf: gpd.GeoDataFrame, target_crs) -> gpd.GeoDataFrame:
    """Reproject gdf ke target_crs kalau CRS-nya beda. Kalau sama, dikembalikan apa adanya."""
    if gdf.crs is None:
        raise ValueError("GeoDataFrame tidak punya CRS terdefinisi, gak bisa direproject.")
    if str(gdf.crs) != str(target_crs):
        return gdf.to_crs(target_crs)
    return gdf


def add_derived_attributes(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Tambah kolom turunan (luas/panjang) berdasarkan tipe geometry, dihitung
    dalam CRS UTM yang di-estimasi otomatis sesuai lokasi data (jadi akurat
    dalam satuan meter, gak perlu manual tentuin zona UTM per WS).

    CATATAN PENTING soal nama & satuan kolom:
    - Nama kolom dijaga MAX 10 karakter dari awal (batas keras format shapefile/DBF),
      biar gak ke-truncate otomatis jadi nama aneh kayak 'luas_ha_1'.
    - Cuma simpan hektar (ha) / kilometer (km), BUKAN m2/meter mentah - soalnya
      nilai m2 buat area nasional bisa >1 milyar, kepanjangan buat lebar kolom
      default shapefile dan gagal ditulis (nilainya jadi kosong diam-diam).
      Hektar/km jauh lebih kecil digitnya, aman.
    """
    if gdf.empty:
        return gdf

    gdf = gdf.copy()
    utm_crs = gdf.estimate_utm_crs()
    gdf_utm = gdf.to_crs(utm_crs)

    geom_type = gdf.geom_type.iloc[0]

    def _set_column_aman(gdf, nama_kolom, nilai):
        """Set kolom, tapi buang dulu kolom lama kalau namanya tabrakan (case-insensitive)
        dgn kolom yg udah ada di data asli - biar GDAL gak auto-rename jadi 'nama_1' dst."""
        kolom_tabrakan = [c for c in gdf.columns if c.lower() == nama_kolom.lower()]
        if kolom_tabrakan:
            gdf = gdf.drop(columns=kolom_tabrakan)
        gdf[nama_kolom] = nilai
        return gdf

    if "Polygon" in geom_type:
        gdf = _set_column_aman(gdf, "luas_ha", (gdf_utm.geometry.area / 10_000).round(2))
    elif "LineString" in geom_type:
        gdf = _set_column_aman(gdf, "panjang_km", (gdf_utm.geometry.length / 1_000).round(3))
    # Point: gak perlu atribut turunan tambahan

    return gdf


def clip_layer(
    input_gdf: gpd.GeoDataFrame,
    boundary_geom,
    layer_name: str,
    ws_name: str,
) -> gpd.GeoDataFrame:
    """
    Clip 1 layer input dengan 1 boundary WS. Generic buat semua tipe geometry.

    PENTING: input_gdf HARUS SUDAH divalidasi (lihat ensure_valid_geometry())
    dan di-reproject SEBELUM manggil fungsi ini. Validasi sengaja gak
    dilakukan di sini lagi, biar gak diulang tiap kali fungsi ini dipanggil
    untuk WS yang berbeda-beda (1 layer bisa di-clip ke banyak WS).

    Params:
        input_gdf: GeoDataFrame data yang mau di-clip (erosi, PL, CAT, dll),
                   sudah valid & sudah 1 CRS sama boundary_geom
        boundary_geom: GeoDataFrame boundary WS, HARUS full-res (bukan simplified)
        layer_name: nama layer (idealnya = nama file yang diupload, tanpa ekstensi)
        ws_name: nama WS

    Returns:
        GeoDataFrame hasil clip, dengan kolom tambahan luas_ha/panjang_km.
    """
    geom_type_asli = input_gdf.geom_type.iloc[0] if not input_gdf.empty else None

    clipped = gpd.clip(input_gdf, boundary_geom)

    if clipped.empty:
        print(f"  [{layer_name} x {ws_name}] Hasil clip KOSONG - cek apakah layer dan WS beririsan.")
        return clipped

    # Clip pada data Polygon kadang menghasilkan irisan berupa garis/titik
    # (kalau posisinya cuma "nyerempet" tepi boundary, bukan overlap area).
    # Hasil campuran tipe geometri gini gak bisa disimpan ke 1 shapefile
    # (shapefile cuma boleh 1 tipe geometri per file) - jadi dibuang.
    if geom_type_asli and "Polygon" in geom_type_asli:
        keep_mask = clipped.geometry.type.isin(["Polygon", "MultiPolygon"])
    elif geom_type_asli and "LineString" in geom_type_asli:
        keep_mask = clipped.geometry.type.isin(["LineString", "MultiLineString"])
    else:
        keep_mask = clipped.geometry.type.isin(["Point", "MultiPoint"])

    n_dibuang = (~keep_mask).sum()
    if n_dibuang > 0:
        print(f"  [{layer_name} x {ws_name}] {n_dibuang} hasil clip berupa artefak tipe geometri "
              f"berbeda (mis. garis nyerempet dari data polygon) - dibuang.")
        clipped = clipped[keep_mask]

    if clipped.empty:
        return clipped

    clipped = add_derived_attributes(clipped)
    # Nama field dijaga max 10 karakter (batas shapefile), lihat catatan di add_derived_attributes
    clipped["sumber"] = layer_name    # isi = nama layer/file sumber data
    clipped["ws_clip"] = ws_name      # isi = nama WS yang jadi boundary clip

    return clipped


def sanity_check_luas(clipped_gdf: gpd.GeoDataFrame, ws_boundary_gdf: gpd.GeoDataFrame, label: str) -> bool:
    """
    QA sederhana: luas total hasil clip TIDAK BOLEH lebih besar dari luas WS
    boundary-nya sendiri. Kalau ini kejadian, ada yang salah di proses clip
    (mirip semangat QA anomaly yang pernah ketemu di kasus DAS).
    """
    if clipped_gdf.empty or "luas_ha" not in clipped_gdf.columns:
        return True  # gak relevan buat layer non-polygon atau hasil kosong

    ws_utm = ws_boundary_gdf.to_crs(ws_boundary_gdf.estimate_utm_crs())
    luas_ws_ha = ws_utm.geometry.area.sum() / 10_000
    luas_clip_ha = clipped_gdf["luas_ha"].sum()

    if luas_clip_ha > luas_ws_ha * 1.01:  # toleransi 1% buat floating point
        print(
            f"  ⚠️  [{label}] PERINGATAN: luas hasil clip ({luas_clip_ha:,.2f} ha) "
            f"melebihi luas WS ({luas_ws_ha:,.2f} ha). Ada yang perlu dicek!"
        )
        return False

    return True


def batch_clip(
    input_layers: dict,
    ws_boundaries: dict,
    output_dir: str,
) -> dict:
    """
    Clip banyak layer x banyak WS sekaligus.

    Params:
        input_layers: dict {nama_layer: path_ke_shapefile}
        ws_boundaries: dict {nama_ws: GeoDataFrame boundary WS (full-res, sudah difilter 1 WS)}
        output_dir: folder buat nyimpen hasil

    Returns:
        dict {(layer_name, ws_name): GeoDataFrame hasil clip}
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    hasil = {}

    for layer_name, layer_path in input_layers.items():
        print(f"\nMemproses layer: {layer_name}")
        input_gdf = load_shapefile(layer_path)

        # Validasi & reproject dilakukan SEKALI di sini, SEBELUM loop WS -
        # bukan di dalam clip_layer() - biar gak diulang tiap WS (boros waktu).
        input_gdf = ensure_valid_geometry(input_gdf, label=layer_name)

        for ws_name, ws_gdf in ws_boundaries.items():
            input_gdf_proj = reproject_if_needed(input_gdf, ws_gdf.crs)
            clipped = clip_layer(input_gdf_proj, ws_gdf, layer_name, ws_name)
            hasil[(layer_name, ws_name)] = clipped

            if not clipped.empty:
                sanity_check_luas(clipped, ws_gdf, label=f"{layer_name} x {ws_name}")

                # Penamaan file: Layer_NamaWS.shp (nama WS dipakai apa adanya,
                # gak ditambah prefix "WS_" lagi karena biasanya nama WS di
                # data kamu sendiri udah mengandung kata "WS")
                nama_file_aman = ws_name.replace(" ", "_").replace("/", "-")
                out_path = output_dir / f"{layer_name}_{nama_file_aman}.shp"
                clipped.to_file(out_path)
                print(f"  -> Disimpan: {out_path} ({len(clipped)} fitur)")

    return hasil
