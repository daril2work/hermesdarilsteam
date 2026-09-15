# 🤖 Hermes Agentic Multi-Agent System

Sistem Multi-Agent cerdas berbasis **Hermes 3 / Nous Research** & **SumoPod AI Gateway**, dilengkapi antarmuka web modern bergaya Grok, eksekusi tools mandiri, integrasi Google Workspace (Drive), serta konektivitas ke remote **Hermes Autonomous Agent Pod**.

---

## 🌟 Fitur Utama

1. **Multi-Agent Orchestration (Chief of Staff):**
   * **Chief of Staff (👑):** Manager utama yang memecah tugas kompleks dan mendelegasikannya ke staf agen.
   * **Grok Original (🤖):** Persona klasik Grok yang cerdas, santai, dan tanpa filter.
   * **Grok Build (💻):** Spesialis rekayasa perangkat lunak dan eksekusi kode Python (*live execution*).
   * **Grok Deep Research (🔍):** Spesialis investigasi web real-time dan analisis konten halaman.
   * **Custom Agents (➕):** Kemampuan membuat agen kustom baru dengan tools pilihan.

2. **Reasoning Modes:**
   * 🤪 **Fun Mode:** Gaya bicara kasual, humoris, dan blak-blakan.
   * ⚡ **Regular Mode:** Jawaban langsung to-the-point dan efisien.
   * 🧠 **Think Mode:** Menjalankan penalaran mendalam (*Extended Chain-of-Thought*) dalam blok `<think>...</think>`.

3. **Tool System & Connectors:**
   * 🌐 **Web Search & Fetch Web Page:** Pencarian internet real-time & ekstraksi teks web.
   * 🐍 **Python Execution Engine:** Menjalankan kode Python secara dinamis di sandbox aman.
   * 📁 **Google Drive Connector:** Membaca, mencari, dan mengunggah dokumen/file di Google Drive.
   * 🚀 **Direct Remote Hermes Pod Integration:** Menampilkan status Pod real-time (`nemotron-3.5-lightning-free`), menyinkronkan 53 native skills, dan menarik riwayat percakapan (*sessions & transcripts*) secara langsung dari Remote Hermes Autonomous Pod.

---

## 📂 Struktur Dokumentasi

* 📖 [Integrasi SumoPod & Remote Hermes Pod](HERMES_SUMOPOD_INTEGRATION.md)
* 📁 [Integrasi Google Workspace & Drive](GOOGLE_WORKSPACE_INTEGRATION.md)
* ☁️ [Panduan Deployment ke PythonAnywhere](DEPLOYMENT_GUIDE.md)

---

## 🚀 Cara Menjalankan Aplikasi Lokal

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Konfigurasi Environment (`.env`):**
   Pastikan file `.env` sudah terisi dengan kredensial SumoPod:
   ```env
   SUMOPOD_API_BASE=https://ai.sumopod.com/v1
   SUMOPOD_API_KEY=sk-riGjhXrfHLF15cwBJNU1vw
   SUMOPOD_MODEL_NAME=deepseek-v4-flash
   ```

3. **Jalankan Server:**
   ```bash
   python main.py
   ```

4. **Buka Web UI:**
   Akses melalui browser di: **http://localhost:8000**
