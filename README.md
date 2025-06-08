# LegalLink - AI Legal Assistant

LegalLink adalah proyek pribadi sistem AI yang dirancang untuk membantu dalam analisis hukum, memberikan konsultasi bisnis, dan analisis dokumen hukum menggunakan teknologi RAG (Retrieval-Augmented Generation) dengan Google Gemini. Proyek ini dikembangkan sebagai bagian dari eksplorasi penggunaan AI untuk aplikasi hukum di Indonesia.

## Fitur Utama

### 1. Chatbot Hukum AI
- Konsultasi hukum interaktif dengan riwayat percakapan
- Menggunakan database dokumen hukum Indonesia
- Jawaban berbasis konteks dengan referensi pasal
- Interface web yang responsif dan user-friendly
- Real-time chat dengan loading indicators dan typing animations

### 2. Analisis Dokumen Hukum
- Upload dan analisis dokumen PDF melalui drag & drop interface
- Ekstraksi informasi penting (pihak, tanggal, kewajiban, hak)
- Penilaian kelengkapan dan kualitas dokumen (skor 1-10)
- Rekomendasi perbaikan dan klausul tambahan
- Analisis risiko hukum dan celah potensial
- Export hasil analisis ke PDF

### 3. Generator Checklist Bisnis
- Analisis ide bisnis berdasarkan input pengguna
- Checklist langkah-langkah hukum dan administratif
- Identifikasi risiko dan rekomendasi mitigasi
- Output dalam format JSON terstruktur
- Form wizard dengan progress indicators
- Validasi input real-time

## Teknologi yang Digunakan

### Backend
- **Django 4.2+** - Web framework Python
- **LangChain** - Framework untuk aplikasi LLM
- **Google Gemini 2.0 Flash** - Large Language Model
- **FAISS** - Vector database untuk document retrieval
- **PyPDF2** - Library untuk processing PDF
- **Google GenerativeAI Embeddings** - Text embeddings

### Frontend
- **Bootstrap 5.3** - CSS framework
- **Font Awesome 6** - Icon library
- **JavaScript ES6+** - Client-side scripting
- **AJAX** - Asynchronous requests
- **CSS3 Animations** - Modern UI animations

### Database Dokumen Hukum
Sistem menggunakan database dokumen hukum Indonesia:
- UU No. 40/2007 tentang Perseroan Terbatas
- UU No. 8/1999 tentang Perlindungan Konsumen
- KUH Perdata (Kitab Undang-Undang Hukum Perdata)
- KUH Dagang (Kitab Undang-Undang Hukum Dagang)
- UU No. 19/2016 tentang Informasi dan Transaksi Elektronik
- UU No. 13/2003 tentang Ketenagakerjaan
- UU No. 30/1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa
- UU No. 11/2020 tentang Cipta Kerja

## Struktur Proyek

```
legallink/
├── legallink/              # Django project settings
│   ├── settings.py         # Konfigurasi Django
│   ├── urls.py            # URL routing utama
│   └── wsgi.py            # WSGI configuration
├── main/                   # Main Django app
│   ├── views.py           # API endpoints dan web views
│   ├── models.py          # Database models
│   ├── prompts.py         # AI prompts dan chains
│   ├── docs.py            # Document processing & vectorstore
│   ├── utils.py           # Helper functions
│   └── urls.py            # App URL routing
├── templates/              # HTML templates
│   ├── base.html          # Base template
│   ├── index.html         # Homepage
│   ├── chat.html          # Chat interface
│   ├── document-analysis.html  # Document analysis page
│   ├── business-checklist.html # Business checklist generator
│   └── partials/          # Reusable template components
├── static/                 # Static files
│   ├── css/               # Custom CSS
│   ├── js/                # Custom JavaScript
│   ├── docs/              # Legal documents (PDF)
│   └── images/            # Static images
├── notebook/               # Jupyter notebooks untuk development
│   ├── chatbot.ipynb      # Chat development
│   ├── document.ipynb     # Document analysis development
│   └── checklist.ipynb    # Business checklist development
├── temp/                   # Temporary files
├── .env                    # Environment variables
├── requirements.txt        # Python dependencies
└── README.md              # Project documentation
```

## Instalasi dan Setup

### 1. Prasyarat
- Python 3.9+
- pip (Python package manager)
- Git
- Google AI API Key (untuk Gemini)

### 2. Clone Repository
```bash
git clone <repository-url>
cd legallink
```

### 3. Setup Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Environment Variables
Buat file `.env` di root directory:
```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
SECRET_KEY=your_django_secret_key_here
DEBUG=True
```

### 6. Persiapan Database
```bash
python manage.py migrate
```

### 7. Jalankan Server
```bash
python manage.py runserver
```

Akses aplikasi di: `http://127.0.0.1:8000`

## API Documentation

### 1. Chat API
**Endpoint:** `POST /chatbot`

Konsultasi hukum interaktif dengan riwayat percakapan.

```python
import requests
import json

url = "http://127.0.0.1:8000/chatbot"
payload = {
    "question": "Apa saja syarat sahnya kontrak kerja?",
    "chat_history": []
}
headers = {"Content-Type": "application/json"}
response = requests.post(url, data=json.dumps(payload), headers=headers)
```

**Response Format:**
```json
{
    "question": "Apa saja syarat sahnya kontrak kerja?",
    "answer": "Syarat sahnya kontrak kerja berdasarkan KUHPerdata...",
    "chat_history": [...]
}
```

### 2. Document Analysis API
**Endpoint:** `POST /analyze_document`

Analisis dokumen hukum dalam format PDF.

```python
import requests

url = "http://127.0.0.1:8000/analyze_document"
with open("dokumen_hukum.pdf", "rb") as pdf_file:
    files = {"pdf_file": pdf_file}
    response = requests.post(url, files=files)
```

**Response Format:**
```json
{
    "Judul_Dokumen": "Perjanjian Kerjasama UMKM",
    "Tanggal": "26 Mei 2016",
    "Pihak": [
        {
            "Nama": "Fani Najmun Nisa",
            "Jabatan": "Direktur",
            "Peran": "PIHAK KESATU"
        }
    ],
    "Deskripsi": "Perjanjian kerjasama pemasaran...",
    "Perjanjian": ["Poin perjanjian 1", "Poin perjanjian 2"],
    "Hak": ["Hak pihak kesatu", "Hak pihak kedua"],
    "Penyelesaian": "Musyawarah untuk mufakat",
    "Pembayaran": "Diatur dalam addendum",
    "Skor": 6,
    "Analisis": {
        "Kesesuaian": "Analisis kesesuaian dokumen...",
        "Kekurangan": "Kekurangan yang ditemukan...",
        "Potensi_Celah_Hukum": "Risiko hukum yang teridentifikasi...",
        "Rekomendasi": "Saran perbaikan..."
    },
    "Clause_Suggestion": [
        {
            "title": "Jangka Waktu Perjanjian",
            "description": "Menentukan jangka waktu berlaku..."
        }
    ]
}
```

### 3. Business Checklist API
**Endpoint:** `POST /checklist`

Generator checklist bisnis berdasarkan ide dan informasi yang diberikan.

```python
import requests
import json

url = "http://127.0.0.1:8000/checklist"
payload = {
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
headers = {"Content-Type": "application/json"}
response = requests.post(url, data=json.dumps(payload), headers=headers)
```

**Response Format:**
```json
{
    "analisis_informasi_bisnis": "Analisis ide bisnis...",
    "checklist": [
        {
            "poin": "Pendirian PT",
            "deskripsi": "Menyiapkan dokumen pendirian PT...",
            "acuan_pasal": "UU No. 40/2007 Pasal 7"
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

### 4. Additional Web Endpoints
- `GET /` - Homepage
- `GET /chat` - Chat interface
- `GET /document-analysis` - Document analysis page
- `GET /business-checklist` - Business checklist generator
- `POST /chat-ajax` - AJAX chat endpoint
- `POST /clear-chat-ajax` - Clear chat history

## Penggunaan Web Interface

### 1. Chat AI Hukum
1. Buka halaman Chat AI dari homepage
2. Ketik pertanyaan hukum di input field
3. Gunakan contoh pertanyaan yang tersedia
4. Lihat jawaban AI dengan referensi pasal (jika ada)
5. Lanjutkan percakapan dengan riwayat tersimpan
6. Hapus riwayat chat jika diperlukan

### 2. Analisis Dokumen
1. Buka halaman Analisis Dokumen
2. Upload file PDF dengan drag & drop atau browse
3. Klik "Analisis Dokumen"
4. Tunggu proses analisis (beberapa menit)
5. Lihat hasil analisis lengkap:
   - Informasi dokumen (pihak, tanggal, dll)
   - Poin-poin perjanjian dan hak
   - Skor kelengkapan dokumen
   - Analisis risiko dan rekomendasi
   - Saran klausul tambahan
6. Cetak atau simpan laporan

### 3. Generator Checklist Bisnis
1. Buka halaman Generator Checklist Bisnis
2. Isi form informasi bisnis:
   - Nama dan deskripsi ide bisnis
   - Target pasar dan model bisnis
   - Bentuk usaha dan lokasi operasional
   - Modal, tim pendiri, dan rencana pemasaran
   - Regulasi yang sudah diketahui
3. Klik "Generate Checklist"
4. Tunggu proses AI (beberapa menit)
5. Lihat hasil checklist:
   - Analisis ide bisnis
   - Checklist langkah hukum dan administratif
   - Identifikasi risiko dan mitigasi
   - Rekomendasi tambahan

## Development dan Testing

### 1. Jupyter Notebooks
Gunakan notebook untuk development dan testing:
```bash
# Install jupyter jika belum ada
pip install jupyter

# Jalankan jupyter
jupyter notebook notebook/
```

Tersedia notebook:
- `chatbot.ipynb` - Development chat functionality
- `document.ipynb` - Development document analysis
- `checklist.ipynb` - Development business checklist

### 2. Menambah Dokumen Hukum
1. Letakkan file PDF di folder `static/docs/`
2. Update list `file_paths` di `main/docs.py`
3. Restart server untuk memproses dokumen baru

### 3. Modifikasi AI Prompts
Edit file `main/prompts.py` untuk mengubah perilaku AI:
- `chat_system_prompt` - Untuk chatbot
- `analysis_system_prompt` - Untuk analisis dokumen
- `checklist_system_prompt` - Untuk generator checklist

### 4. Styling dan UI
- CSS files di `static/css/`
- JavaScript files di `static/js/`
- Bootstrap 5 untuk responsive design
- Font Awesome untuk icons

## Error Handling

Aplikasi menangani berbagai jenis error:
- **400 Bad Request** - Input tidak valid atau hilang
- **405 Method Not Allowed** - Metode HTTP tidak sesuai
- **500 Internal Server Error** - Error dalam pemrosesan AI atau file
- **ResourceExhausted** - Quota API Google habis
- **File Processing Error** - Error membaca atau memproses PDF

## Performance dan Limitations

### Performance
- Rata-rata response time: 10-30 detik (tergantung kompleksitas)
- Maksimal ukuran file PDF: 10MB
- Concurrent users: Tergantung Google API quota
- Vector database: In-memory ChromaDB

### Limitations
- Hanya mendukung dokumen PDF
- Bahasa Indonesia saja
- Tergantung pada kualitas scan PDF
- Memerlukan koneksi internet untuk AI processing
- Quota Google API terbatas

## Troubleshooting

### 1. Google API Key Issues
```bash
# Periksa API key di .env
GOOGLE_API_KEY=your_actual_api_key

# Test API key
python -c "from google.generativeai import configure, GenerativeModel; configure(api_key='YOUR_KEY'); print('API Key valid')"
```

### 2. PDF Processing Issues
- Pastikan file PDF dapat dibaca (tidak corrupt)
- Cek format PDF (harus text-based, bukan scan image)
- Ukuran file tidak terlalu besar (< 10MB)

### 3. Database Issues
```bash
# Reset database jika diperlukan
python manage.py migrate --run-syncdb
```

### 4. Static Files Issues
```bash
# Collect static files
python manage.py collectstatic
```

## Contributing

Sebagai proyek pribadi, kontribusi terbuka untuk:
1. Bug fixes
2. Feature improvements
3. Documentation updates
4. Performance optimizations

### Development Workflow
1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request


## License

Proyek ini dikembangkan untuk keperluan edukasi dan penelitian. Distributed under the MIT License. See `LICENSE` for more information.

## Disclaimer

⚠️ **PENTING**: Sistem ini adalah alat bantu edukasi dan tidak menggantikan konsultasi hukum profesional. Selalu konsultasikan dengan ahli hukum untuk keputusan penting.

## Contact & Support

- **Developer**: Vincent Davis Leonard
- **Institution**: Fakultas Ilmu Komputer Universitas Indonesia (Angkatan 2023)
- **Email**: vincentdavisleonard@gmail.com
- **GitHub**: [https://github.com/vincent-davis](https://github.com/vincent-davis)
- **LinkedIn**: [Vincent Davis Leonard](https://www.linkedin.com/in/vincent-davis-bb678828a/)

## Acknowledgments

- Google Gemini AI untuk LLM capabilities
- LangChain untuk framework RAG
- Bootstrap untuk UI components
- Django community untuk web framework
- Open source legal documents dari berbagai sumber pemerintah Indonesia
- Fakultas Ilmu Komputer Universitas Indonesia untuk dukungan akademis

---

**Made with ❤️ by Vincent Davis Leonard using Python, Django, and Google Gemini AI**