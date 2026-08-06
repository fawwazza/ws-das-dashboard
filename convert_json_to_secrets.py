"""
Convert file JSON Service Account (dari Google Cloud) jadi format
.streamlit/secrets.toml yang bisa langsung dipakai Streamlit.

Cara pakai:
    python convert_json_to_secrets.py path/ke/file-service-account.json
"""

import sys
import json
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        print("Cara pakai: python convert_json_to_secrets.py path/ke/file.json")
        return

    json_path = Path(sys.argv[1])
    with open(json_path, "r") as f:
        data = json.load(f)

    output_lines = ["[gcp_service_account]"]
    for key, value in data.items():
        if isinstance(value, str):
            # Escape berurutan: backslash dulu, lalu kutip, lalu BARIS BARU.
            # Baris baru WAJIB di-escape jadi literal \n - soalnya private_key
            # itu multi-baris (format PEM), dan TOML basic string ("...")
            # gak boleh punya baris baru mentah di dalamnya.
            value_escaped = (
                value.replace("\\", "\\\\")
                .replace('"', '\\"')
                .replace("\r\n", "\\n")
                .replace("\n", "\\n")
            )
            output_lines.append(f'{key} = "{value_escaped}"')
        else:
            output_lines.append(f'{key} = {json.dumps(value)}')

    hasil = "\n".join(output_lines)

    out_path = Path(".streamlit") / "secrets.toml"
    out_path.parent.mkdir(exist_ok=True)

    if out_path.exists():
        print(f"PERHATIAN: {out_path} sudah ada. Isinya akan DITIMPA.")
        input("Tekan Enter buat lanjut, atau Ctrl+C buat batal...")

    with open(out_path, "w") as f:
        f.write(hasil + "\n")

    print(f"Berhasil! Kredensial disimpan di: {out_path}")
    print("\nPENTING:")
    print("1. JANGAN commit file .streamlit/secrets.toml ini ke Git!")
    print("   Pastikan '.streamlit/secrets.toml' ada di .gitignore kamu.")
    print("2. Buat versi PUBLIK (Streamlit Cloud), isi file ini nanti perlu")
    print("   di-paste manual ke menu 'Secrets' di dashboard Streamlit Cloud kamu.")


if __name__ == "__main__":
    main()
