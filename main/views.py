import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
import json
from django.shortcuts import render
from django.http import HttpResponse

from langchain_google_genai import ChatGoogleGenerativeAI
# Load environment variables dari .env
load_dotenv()

# --- Import library LangChain dan lainnya ---


from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from main.prompts import chat_qa_prompt, chat_contextualize_q_prompt, analysis_qa_prompt, checklist_qa_prompt
from main.docs import retriever
from main.utils import read_pdf


# Inisialisasi LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0.2,
    top_p=0.95,
    top_k=40,
    max_tokens=8192,
    response_mime_type="text/plain"
)

# Buat retriever yang aware terhadap riwayat percakapan
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, chat_contextualize_q_prompt
)
# Buat chain untuk menjawab pertanyaan berdasarkan dokumen yang diretrieval
question_answer_chain = create_stuff_documents_chain(llm, chat_qa_prompt)
chat_rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

@csrf_exempt
def chat_api(request):
    """
    API endpoint yang menerima payload JSON POST berisi:
      - "question": pertanyaan pengguna (string)
      - "chat_history": riwayat chat sebelumnya (list of dict)
      
    API akan:
      - Mengambil "question" dan "chat_history" dari payload POST.
      - Memanggil rag_chain dengan input tersebut.
      - Menambahkan interaksi baru (pesan pengguna dan jawaban AI) ke dalam chat_history.
      - Mengembalikan response JSON yang berisi "question", "answer", dan chat_history yang ter-update.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Payload JSON tidak valid."}, status=400)

        # Ambil pertanyaan dan chat_history dari payload
        question = data.get("question", "").strip()
        chat_history = data.get("chat_history", [])

        if not question:
            return JsonResponse({"error": "Masukkan pertanyaan Anda.", "chat_history": chat_history}, status=400)

        if not isinstance(chat_history, list):
            return JsonResponse({"error": "chat_history harus berupa list.", "chat_history": []}, status=400)

        try:
            # Panggil rag_chain dengan input dan chat_history yang diberikan
            result = chat_rag_chain.invoke({"input": question, "chat_history": chat_history})
            answer = result.get("answer", "")

            # Perbarui chat_history dengan pesan pengguna dan jawaban AI
            chat_history.append({"role": "human", "content": question})
            chat_history.append({"role": "ai", "content": answer})

            return JsonResponse({
                "question": question,
                "answer": answer,
                "chat_history": chat_history
            })
        except Exception as e:
            return JsonResponse({"error": f"Terjadi kesalahan: {str(e)}", "chat_history": chat_history}, status=500)
    else:
        return JsonResponse({"error": "Metode tidak diizinkan. Gunakan POST."}, status=405)


# Buat chain analisis dokumen menggunakan combine_documents chain
analysis_chain = create_stuff_documents_chain(llm, analysis_qa_prompt)
# Buat retrieval chain untuk analisis dokumen (jika diperlukan retrieval)
analysis_rag_chain = create_retrieval_chain(retriever, analysis_chain)

@csrf_exempt
def analyze_document(request):
    """
    API endpoint untuk analisis dokumen.
    Menerima file PDF melalui POST (key: 'pdf_file') dan mengembalikan hasil analisis dalam format JSON.
    Menggunakan dokumen yang sama (combined_docs) untuk retrieval.
    """
    if request.method == "POST":
        if "pdf_file" not in request.FILES:
            return JsonResponse({"error": "File PDF tidak ditemukan. Kirim file dengan key 'pdf_file'."}, status=400)
        
        pdf_file = request.FILES["pdf_file"]
        try:
            document_text = read_pdf(pdf_file)
        except Exception as e:
            return JsonResponse({"error": f"Gagal membaca file PDF: {str(e)}"}, status=500)
        
        # Siapkan prompt analisis dengan memasukkan teks dokumen
        prompt = f"""Dokumen yang akan dianalisis adalah sebagai berikut:
{document_text}

Tugas Anda adalah menganalisis dokumen tersebut dan memberikan output dalam format JSON dengan bidang berikut:
- Judul Dokumen: Judul dokumen hukum.
- Tanggal: Tanggal yang disebutkan dalam dokumen.
- Pihak: Nama-nama pihak yang terlibat dalam dokumen.
- Deskripsi: Ringkasan singkat mengenai isi dokumen.
- Perjanjian: Kesepakatan atau kewajiban utama yang dibahas dalam dokumen.
- Hak: Hak-hak yang secara eksplisit disebutkan dalam dokumen.
- Penyelesaian: Cara penyelesaian sengketa yang disebutkan dalam dokumen.
- Pembayaran: Ketentuan terkait pembayaran, jika ada.
- Pengecualian: Ketentuan pengecualian atau kondisi tertentu yang disebutkan dalam dokumen.
- Skor: Penilaian terhadap kelengkapan, kejelasan, dan kualitas dokumen.

Berikan analisis dokumen, termasuk:
- Kesesuaian dokumen dengan kebutuhan hukum.
- Kesalahan atau kekurangan dalam teks dokumen.
- Potensi celah hukum yang dapat menimbulkan masalah.
- Rekomendasi klausa tambahan untuk mencegah potensi masalah di masa depan atau meningkatkan kejelasan dokumen.

Pastikan untuk hanya menggunakan informasi yang relevan dari dokumen dan kosongkan bidang yang tidak ada informasinya.
"""
        try:
            result = analysis_rag_chain.invoke({"input": prompt})
            answer = result.get("answer", "")
            try:
                output_data = json.loads(answer)
                return JsonResponse(output_data)
            except Exception:
                return JsonResponse({"analysis": answer})
        except Exception as e:
            return JsonResponse({"error": f"Terjadi kesalahan saat analisis: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "Metode tidak diizinkan. Gunakan POST."}, status=405)

checklist_question_answer_chain = create_stuff_documents_chain(llm, checklist_qa_prompt)
# Membuat rag_chain tanpa chat history (langsung menggunakan retriever)
checklist_rag_chain = create_retrieval_chain(retriever, checklist_question_answer_chain)

@csrf_exempt
def generate_business_checklist(request):
    """
    API endpoint untuk mengenerate checklist dari ide bisnis.
    Mengharapkan payload POST dalam format JSON dengan key:
      - "business_info": { ... }  // Data ide bisnis (dictionary)
    
    Contoh payload:
    {
        "business_info": {
            "Nama Ide Bisnis": "Snack Sehat Nusantara",
            "Deskripsi Ide": "Menjual snack sehat berbahan lokal...",
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
    """
    if request.method != "POST":
        return JsonResponse({"error": "Metode tidak diizinkan. Gunakan POST."}, status=405)
    
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "Payload JSON tidak valid."}, status=400)
    
    business_info = data.get("business_info", {})
    if not isinstance(business_info, dict):
        return JsonResponse({"error": "business_info harus berupa objek JSON."}, status=400)
    
    # Ekstrak informasi ide bisnis dengan default jika tidak ada
    nama = business_info.get("Nama Ide Bisnis", "Tidak disebutkan")
    deskripsi = business_info.get("Deskripsi Ide", "Tidak disebutkan")
    target_pasar = business_info.get("Target Pasar", "Tidak disebutkan")
    model_bisnis = business_info.get("Model Bisnis", "Tidak disebutkan")
    lokasi = business_info.get("Lokasi Operasional", "Tidak disebutkan")
    bentuk = business_info.get("Bentuk Usaha", "Tidak disebutkan")
    modal = business_info.get("Kebutuhan Modal", "Tidak disebutkan")
    tim = business_info.get("Tim atau Pendiri", ["Tidak disebutkan"])
    jenis_produk = business_info.get("Jenis Produk/Jasa", "Tidak disebutkan")
    pemasaran = business_info.get("Rencana Pemasaran", "Tidak disebutkan")
    regulasi = business_info.get("Regulasi yang Diketahui", ["Tidak disebutkan"])
    kemitraan = business_info.get("Kemitraan/Investor", "Tidak disebutkan")
    
    # Susun prompt berdasarkan data ide bisnis
    prompt = f"""
Saya memiliki ide bisnis sebagai berikut:
- Nama Ide Bisnis: {nama}
- Deskripsi Ide: {deskripsi}
- Target Pasar: {target_pasar}
- Model Bisnis: {model_bisnis}
- Lokasi Operasional: {lokasi}
- Bentuk Usaha: {bentuk}
- Kebutuhan Modal: {modal}
- Tim atau Pendiri: {', '.join(tim) if isinstance(tim, list) else tim}
- Jenis Produk/Jasa: {jenis_produk}
- Rencana Pemasaran: {pemasaran}
- Regulasi yang Diketahui: {', '.join(regulasi) if isinstance(regulasi, list) else regulasi}
- Kemitraan/Investor: {kemitraan}

Tolong bantu analisis ide bisnis saya. Berikut permintaan saya:

1. Analisis singkat terhadap informasi bisnis di atas.
2. Susun checklist poin-poin penting yang harus saya perhatikan, serta sertakan acuan pasal dari RAG (jika relevan).
3. Jelaskan risiko hukum atau administratif yang mungkin muncul.
4. Berikan rekomendasi atau langkah tambahan untuk memperkuat rencana bisnis saya.

Jangan lupa, jawaban akhir harus dalam format JSON sesuai instruksi yang telah ditetapkan.
    """
    
    try:
        # Panggil chain tanpa menggunakan chat history
        result = checklist_rag_chain.invoke({"input": prompt})
        answer = result.get("answer", "")
        return JsonResponse({"checklist": answer})
    except Exception as e:
        return JsonResponse({"error": f"Terjadi kesalahan: {str(e)}"}, status=500)