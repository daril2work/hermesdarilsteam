# 🛸 Integrasi SumoPod & Remote Hermes Autonomous Pod

Dokumen ini menjelaskan arsitektur integrasi antara aplikasi lokal **Hermes Agentic** dengan server **SumoPod AI Gateway** dan **Hermes Agent Pod (Nous Research)**.

---

## 1. Konfigurasi Pod di SumoPod

* **Pod URL:** `https://hermes-gwrdes.jkt8.sumopod.my.id`
* **Region:** ID Jakarta (Latensi terendah)
* **Template:** Hermes Agent (1 CPU, 1.0 GB RAM)
* **Dashboard Version:** `v0.21.2` (Nous Research)

### Kredensial Akses:
* **Dashboard Login:**
  * Username: `JbjUU8`
  * Password: `UxYuYKf1BJdpAAs1`
* **Pod API Server Key:** `sk-t9RjJEqXws30PRqj6dNprTDI`
* **SumoPod AI Gateway API Key:** `sk-riGjhXrfHLF15cwBJNU1vw`

---

## 2. Modul Konektor (`connector/sumopod_pod.py`)

Konektor ini menghubungkan klien Python dan Web UI FastAPI secara langsung ke API remote Hermes Pod:

### Method API Konektor:

| Method / Fungsi | Deskripsi | Return Value |
|---|---|---|
| `get_pod_status_info()` | Memeriksa status kesehatan, model aktif, dan konfigurasi webhook remote pod secara *real-time*. | `dict` (online, model, skills_count, sessions_count) |
| `get_remote_skills_list()` | Mengambil 53 modular skills native yang aktif di dalam remote pod. | `list` of skill objects |
| `get_remote_sessions_list()` | Mengambil daftar riwayat sesi percakapan dari remote pod. | `list` of session objects |
| `get_remote_session_messages(id)` | Mengambil transkrip isi pesan dari sesi tertentu di remote pod. | `list` of message objects |
| `trigger_webhook(event_name)` | Mengirim event / tugas otomatis ke Inbound Webhook Gateway di remote pod. | `str` status respons |

---

## 3. Web UI Dashboard Integration & REST Endpoints

Web UI Dashboard (`ui/web_dashboard.py`) menyediakan endpoint REST API untuk sinkronisasi otomatis:

* **`GET /api/pod/status`**: Menampilkan indikator status Pod online (`nemotron-3.5-lightning-free`), total 53 skills, dan jumlah sesi di footer sidebar.
* **`GET /api/pod/skills`**: Mengambil daftar 53 native skills dari Remote Pod.
* **`GET /api/pod/sessions`**: Menampilkan riwayat percakapan (*Chats History*) secara real-time di sidebar UI.
* **`GET /api/pod/sessions/{session_id}/messages`**: Memuat transkrip riwayat percakapan lama saat pengguna mengklik item riwayat di UI.

---

## 4. Contoh Penggunaan di Chat UI

1. **Memeriksa Status Pod:**
   > *"Cek status koneksi Hermes Pod saya di SumoPod."*
   Agen akan mengeksekusi `sumopod_get_pod_status` dan menampilkan:
   ```
   ✅ Hermes Pod Status: ONLINE & CONNECTED
   - Pod URL: https://hermes-gwrdes.jkt8.sumopod.my.id
   - Gateway Mode: Multi-Agent Autonomous Pod
   - Active Model in Pod: nemotron-3.5-lightning-free
   - Webhooks Gateway: 🟢 Enabled
   ```

2. **Sinkronisasi Riwayat Percakapan (History Sync):**
   Setiap kali Web UI dibuka, sistem otomatis menarik daftar sesi dari Remote Hermes Pod dan mengizinkan pengguna melihat serta melanjutkan transkrip percakapan sebelumnya.

