# ☁️ Panduan Deployment ke PythonAnywhere

Panduan ini memandu proses deploy aplikasi **Hermes Agentic (FastAPI)** ke server **PythonAnywhere** menggunakan WSGI bridge (`a2wsgi`).

---

## 1. Persiapan File di Repository

File berikut sudah disiapkan di dalam project:
* [`wsgi.py`](../wsgi.py): Entrypoint WSGI yang menghubungkan ASGI FastAPI ke server WSGI PythonAnywhere.
* [`requirements.txt`](../requirements.txt): Daftar dependencies termasuk `fastapi`, `uvicorn`, `a2wsgi`, dan `jinja2`.

---

## 2. Langkah-Langkah Deploy

### Langkah 1: Upload Code ke PythonAnywhere
Di Bash Console PythonAnywhere:
```bash
git clone <URL_REPO_GITHUB> hermes-agentic
cd hermes-agentic
```

### Langkah 2: Buat Virtual Environment & Install Requirements
```bash
mkvirtualenv hermes-env --python=/usr/bin/python3.10
pip install -r requirements.txt
```

### Langkah 3: Setup File `.env`
```bash
nano .env
```
Isi dengan:
```env
SUMOPOD_API_BASE=https://ai.sumopod.com/v1
SUMOPOD_API_KEY=sk-riGjhXrfHLF15cwBJNU1vw
SUMOPOD_MODEL_NAME=deepseek-v4-flash
```

### Langkah 4: Konfigurasi Web Tab di PythonAnywhere
1. Masuk ke tab **Web** > **Add a new web app** > pilih **Manual configuration** > **Python 3.10**.
2. Atur path:
   * **Source code:** `/home/<username>/hermes-agentic`
   * **Working directory:** `/home/<username>/hermes-agentic`
   * **Virtualenv:** `/home/<username>/.virtualenvs/hermes-env`

### Langkah 5: Edit WSGI Configuration File
Klik link **WSGI configuration file** di tab Web, hapus isinya dan ganti dengan:
```python
import sys
import os

path = '/home/<username>/hermes-agentic'
if path not in sys.path:
    sys.path.insert(0, path)

from dotenv import load_dotenv
load_dotenv(os.path.join(path, ".env"))

from a2wsgi import ASGIMiddleware
from ui.web_dashboard import app

application = ASGIMiddleware(app)
```

### Langkah 6: Reload Web App
Klik tombol hijau **Reload <username>.pythonanywhere.com**, lalu buka website kamu di browser!
