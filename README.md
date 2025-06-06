# LegalLink - AI Legal Assistant

LegalLink adalah sistem AI yang dirancang untuk membantu dalam analisis hukum, memberikan konsultasi bisnis, dan analisis dokumen hukum menggunakan teknologi RAG (Retrieval-Augmented Generation) dengan Google Gemini.

## Fitur Utama

### 1. Chatbot Hukum AI
- Konsultasi hukum interaktif dengan riwayat percakapan
- Menggunakan database dokumen hukum Indonesia
- Jawaban berbasis konteks dengan referensi pasal

### 2. Analisis Dokumen Hukum
- Upload dan analisis dokumen PDF
- Ekstraksi informasi penting (pihak, tanggal, kewajiban, hak)
- Penilaian kelengkapan dan kualitas dokumen
- Rekomendasi perbaikan dan klausul tambahan

### 3. Generator Checklist Bisnis
- Analisis ide bisnis berdasarkan input pengguna
- Checklist langkah-langkah hukum dan administratif
- Identifikasi risiko dan rekomendasi mitigasi
- Output dalam format JSON terstruktur

## Struktur Proyek

```
legallink/
├── legallink/          # Django project settings
├── main/               # Main Django app
│   ├── views.py        # API endpoints
│   ├── models.py       # Database models
│   ├── prompts.py      # AI prompts dan chains
│   ├── docs.py         # Document processing
│   └── utils.py        # Helper functions
├── templates/          # HTML templates
├── static/docs/        # Legal documents (PDF)
├── notebook/           # Jupyter notebooks untuk development
└── requirements.txt    # Dependencies
```

## Instalasi

1. **Clone repository**
```bash
git clone <repository-url>
cd legallink
```

2. **Buat virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# atau
.venv\Scripts\activate     # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment variables**
Buat file `.env` di root directory:
```env
GOOGLE_API_KEY=your_google_api_key_here
SECRET_KEY=your_django_secret_key
DEBUG=True
```

5. **Migrasi database**
```bash
python manage.py migrate
```

6. **Jalankan server**
```bash
python manage.py runserver
```

## API Endpoints

### 1. Chatbot API
**Endpoint:** `POST /chatbot`

Untuk konsultasi hukum interaktif dengan riwayat percakapan.

**Request Body:**
```json
{
    "question": "Apa saja syarat sahnya kontrak kerja?",
    "chat_history": [
        {"role": "human", "content": "Halo, saya butuh bantuan hukum."},
        {"role": "ai", "content": "Halo, ada yang bisa saya bantu?"}
    ]
}
```

**Response:**
```json
{
    "question": "Apa saja syarat sahnya kontrak kerja?",
    "answer": "Syarat sahnya kontrak kerja berdasarkan KUHPerdata...",
    "chat_history": [
        {"role": "human", "content": "Halo, saya butuh bantuan hukum."},
        {"role": "ai", "content": "Halo, ada yang bisa saya bantu?"},
        {"role": "human", "content": "Apa saja syarat sahnya kontrak kerja?"},
        {"role": "ai", "content": "Syarat sahnya kontrak kerja berdasarkan KUHPerdata..."}
    ]
}
```

### 2. Analisis Dokumen API
**Endpoint:** `POST /analyze_document`

Untuk menganalisis dokumen hukum dalam format PDF.

**Request:** Multipart form dengan file PDF
```python
import requests

url = "http://127.0.0.1:8000/analyze_document"
with open("dokumen_hukum.pdf", "rb") as pdf_file:
    files = {"pdf_file": pdf_file}
    response = requests.post(url, files=files)
```

**Response:**
```json
{
    "Judul Dokumen": "Perjanjian Kerjasama UMKM",
    "Tanggal": "26 Mei 2016",
    "Pihak": ["Fani Najmun Nisa", "PT. Indomarco Prismatama"],
    "Deskripsi": "Perjanjian kerjasama pemasaran produk UMKM",
    "Perjanjian": ["Penyerahan produk untuk dipasarkan..."],
    "Hak": {
        "PIHAK KESATU": "Menerima pembayaran",
        "PIHAK KEDUA": "Memasarkan produk"
    },
    "Penyelesaian": "Musyawarah untuk mufakat",
    "Pembayaran": "Diatur dalam addendum",
    "Pengecualian": null,
    "Skor": 6,
    "Kesimpulan": "Dokumen memerlukan revisi...",
    "Clause Suggestion": [
        {
            "title": "Jangka Waktu Perjanjian",
            "description": "Menentukan jangka waktu berlaku..."
        }
    ]
}
```

### 3. Generator Checklist Bisnis API
**Endpoint:** `POST /checklist`

Untuk menganalisis ide bisnis dan menghasilkan checklist hukum.

**Request Body:**
```json
{
    "business_info": {
        "Nama Ide Bisnis": "Snack Sehat Nusantara",
        "Deskripsi Ide": "Menjual snack sehat berbahan lokal",
        "Target Pasar": "Anak muda usia 18-35 di kota besar",
        "Model Bisnis": "Penjualan langsung dan online",
        "Lokasi Operasional": "Jakarta",
        "Bentuk Usaha": "PT",
        "Kebutuhan Modal": "100 juta",
        "Tim atau Pendiri": ["Fani Najmun Nisa", "Rizky Mahardika"],
        "Jenis Produk/Jasa": "Makanan ringan",
        "Rencana Pemasaran": "Media sosial dan influencer marketing",
        "Regulasi yang Diketahui": ["UU Perlindungan Konsumen", "Izin PIRT"],
        "Kemitraan/Investor": "Tidak ada"
    }
}
```

**Response:**
```json
{
    "analisis_informasi_bisnis": "Snack Sehat Nusantara memiliki potensi pasar yang baik...",
    "checklist": [
        {
            "poin": "Pendirian PT",
            "deskripsi": "Menyiapkan dokumen pendirian PT seperti akta pendirian...",
            "acuan_pasal": ""
        },
        {
            "poin": "Izin PIRT",
            "deskripsi": "Mengurus Izin PIRT dari Dinas Kesehatan...",
            "acuan_pasal": ""
        }
    ],
    "risiko": [
        {
            "deskripsi": "Pelanggaran HAKI: Peniruan merek dagang",
            "rekomendasi": "Segera daftarkan merek dagang"
        }
    ],
    "rekomendasi_tambahan": [
        "Melakukan riset pasar lebih lanjut",
        "Membangun brand image yang kuat"
    ]
}
```

## Penggunaan dengan Python

### Contoh Chat API
```python
import requests
import json

url = "http://127.0.0.1:8000/chatbot"

payload = {
    "question": "Apa hukum tentang perlindungan konsumen?",
    "chat_history": []
}

headers = {"Content-Type": "application/json"}
response = requests.post(url, data=json.dumps(payload), headers=headers)

print(json.dumps(response.json(), indent=2, ensure_ascii=False))
```

### Contoh Analisis Dokumen
```python
import requests

url = "http://127.0.0.1:8000/analyze_document"

with open("dokumen_kontrak.pdf", "rb") as pdf_file:
    files = {"pdf_file": pdf_file}
    response = requests.post(url, files=files)
    
print(response.json())
```

### Contoh Generator Checklist
```python
import requests
import json

url = "http://127.0.0.1:8000/checklist"

payload = {
    "business_info": {
        "Nama Ide Bisnis": "Startup Teknologi",
        "Deskripsi Ide": "Platform marketplace online",
        "Target Pasar": "UMKM Indonesia",
        "Model Bisnis": "Commission-based",
        "Lokasi Operasional": "Jakarta",
        "Bentuk Usaha": "PT",
        "Kebutuhan Modal": "500 juta",
        "Tim atau Pendiri": ["John Doe", "Jane Smith"],
        "Jenis Produk/Jasa": "Platform digital",
        "Rencana Pemasaran": "Digital marketing dan partnership",
        "Regulasi yang Diketahui": ["UU ITE", "UU Perdagangan"],
        "Kemitraan/Investor": "Angel investor"
    }
}

headers = {"Content-Type": "application/json"}
response = requests.post(url, data=json.dumps(payload), headers=headers)

print(json.dumps(response.json(), indent=2, ensure_ascii=False))
```

