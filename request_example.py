import requests
import json

# # URL endpoint API (sesuaikan dengan alamat server Anda)
# url = "http://127.0.0.1:8000/chatbot"

# # Contoh payload dengan chat history yang representatif:
# # Percakapan sebelumnya:
# # 1. Pengguna: "Halo, saya butuh bantuan hukum."
# # 2. AI: "Halo, ada yang bisa saya bantu?"
# # 3. Pengguna: "Saya ingin tahu tentang kontrak kerja."
# # 4. AI: "Kontrak kerja adalah perjanjian antara dua pihak dengan syarat-syarat tertentu..."
# #
# # Pertanyaan baru: "Apa saja syarat sahnya kontrak kerja?"

# payload = {
#     "question": "Apa saja syarat sahnya kontrak kerja?",
#     "chat_history": [
#         {"role": "human", "content": "Halo, saya butuh bantuan hukum."},
#         {"role": "ai", "content": "Halo, ada yang bisa saya bantu?"},
#         {"role": "human", "content": "Saya ingin tahu tentang kontrak kerja."},
#         {"role": "ai", "content": "Kontrak kerja adalah perjanjian antara dua pihak dengan syarat-syarat tertentu, seperti adanya kesepakatan, objek yang jelas, dan adanya pertimbangan."}
#     ]
# }

# headers = {
#     "Content-Type": "application/json"
# }

# # Melakukan POST request
# response = requests.post(url, data=json.dumps(payload), headers=headers)

# # Menampilkan hasil response
# print(json.dumps(response.json(), indent=2, ensure_ascii=False))



# # URL endpoint analisis dokumen (sesuaikan jika perlu)
# url = "http://127.0.0.1:8000/analyze_document"

# # Buka file PDF yang ingin diuji
# with open("Kerjasama_UMKM.pdf", "rb") as pdf_file:
#     files = {"pdf_file": pdf_file}
#     response = requests.post(url, files=files)

# # Cetak hasil response sebagai JSON
# print(response.json())


# Sesuaikan URL endpoint dengan URL aplikasi Django Anda,
# misalnya: "http://127.0.0.1:8000/generate_business_checklist"
url = "http://127.0.0.1:8000/checklist"

payload = {
    "business_info": {
        "Nama Ide Bisnis": "Snack Sehat Nusantara",
        "Deskripsi Ide": "Menjual snack sehat berbahan lokal seperti singkong dan talas dengan berbagai rasa.",
        "Target Pasar": "Anak muda usia 18-35 di kota besar.",
        "Model Bisnis": "Penjualan langsung dan online melalui e-commerce.",
        "Lokasi Operasional": "Jakarta",
        "Bentuk Usaha": "PT",
        "Kebutuhan Modal": "100 juta",
        "Tim atau Pendiri": ["Fani Najmun Nisa", "Rizky Mahardika"],
        "Jenis Produk/Jasa": "Makanan ringan",
        "Rencana Pemasaran": "Menggunakan media sosial untuk promosi dan influencer marketing.",
        "Regulasi yang Diketahui": ["UU Perlindungan Konsumen", "Izin PIRT"],
        "Kemitraan/Investor": "Tidak ada"
    }
}

headers = {"Content-Type": "application/json"}

response = requests.post(url, data=json.dumps(payload), headers=headers)



print("Response JSON:")


print(response.json())