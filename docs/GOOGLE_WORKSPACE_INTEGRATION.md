# 📁 Integrasi Google Workspace & Drive

Dokumen ini menjelaskan cara kerja dan langkah konfigurasi integrasi **Google Drive & Workspace** pada sistem Hermes Agentic.

---

## 1. Kemampuan Tool Google Drive

Agen (khususnya **Chief of Staff 👑**) memiliki akses ke 3 tool manipulasi file di Google Drive:

| Tool | Fungsi | Parameter |
|---|---|---|
| **`gdrive_list_files`** | Mencari dan menampilkan daftar file di Google Drive. | `query` *(opsional)*, `max_results` *(default 10)* |
| **`gdrive_read_file`** | Membaca isi teks dari Google Docs, Google Sheets, atau file teks. | `file_id` *(wajib)* |
| **`gdrive_upload_file`** | Mengunggah atau membuat file teks/dokumen baru ke Google Drive. | `name` *(nama file)*, `content` *(isi teks)*, `folder_id` *(opsional)* |

---

## 2. Cara Konfigurasi Autentikasi Google Cloud

Agar Hermes dapat mengakses Google Drive Anda:

### Opsi A: Menggunakan Service Account (Rekomendasi)
1. Buka [Google Cloud Console](https://console.cloud.google.com/).
2. Buat Project baru atau pilih project yang sudah ada.
3. Aktifkan **Google Drive API**.
4. Masuk ke menu **IAM & Admin** > **Service Accounts** > **Create Service Account**.
5. Buat **Key** baru bertipe **JSON**, lalu unduh file tersebut.
6. Ganti nama file tersebut menjadi **`service_account.json`** dan letakkan di root folder project:
   ```
   d:\hermes-agentic\service_account.json
   ```
7. Bagikan (Share) folder atau file Google Drive yang ingin dibaca ke alamat email service account tersebut (contoh: `my-bot@project-id.iam.gserviceaccount.com`).

### Opsi B: Menggunakan OAuth2 Token
Simpan file token OAuth2 Anda dengan nama **`token.json`** di root folder project:
```
d:\hermes-agentic\token.json
```

---

## 3. Contoh Skenario Penggunaan

1. **Mencari File:**
   > *"Cari file laporan keuangan di Google Drive saya."*
2. **Membaca Dokumen:**
   > *"Baca isi dokumen dengan ID `1A2B3C...` dan buatkan ringkasannya."*
3. **Membuat Catatan Otomatis:**
   > *"Simpan ringkasan riset ini ke Google Drive dengan nama `Ringkasan_AI_2026.md`."*
