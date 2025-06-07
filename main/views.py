import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
import json
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
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
    model="gemini-2.0-flash",
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
    
# ===== VIEWS UNTUK WEB INTERFACE =====

def index(request):
    """Homepage dengan overview semua fitur"""
    return render(request, 'index.html')

def chat_view(request):
    """View untuk halaman chat - menampilkan form dan riwayat chat"""
    chat_history = request.session.get('chat_history', [])
    
    # Convert chat_history to JSON string for JavaScript
    chat_history_json = json.dumps(chat_history) if chat_history else '[]'
    
    return render(request, 'chat.html', {
        'chat_history': chat_history,
        'chat_history_json': chat_history_json
    })


# Add these functions to your existing views.py

@csrf_exempt
def chat_ajax(request):
    """AJAX endpoint untuk chat"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question = data.get('question', '').strip()
            chat_history = data.get('chat_history', [])
            
            if not question:
                return JsonResponse({'error': 'Masukkan pertanyaan Anda.'}, status=400)
            
            # Panggil rag_chain dengan input dan chat_history yang diberikan
            result = chat_rag_chain.invoke({"input": question, "chat_history": chat_history})
            answer = result.get("answer", "")
            
            # Perbarui chat_history dengan pesan pengguna dan jawaban AI
            chat_history.append({"role": "human", "content": question})
            chat_history.append({"role": "ai", "content": answer})
            
            # Simpan ke session
            request.session['chat_history'] = chat_history
            
            return JsonResponse({
                "question": question,
                "answer": answer,
                "chat_history": chat_history,
                "success": True
            })
            
        except Exception as e:
            return JsonResponse({'error': f'Terjadi kesalahan: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def clear_chat_ajax(request):
    """AJAX endpoint untuk menghapus riwayat chat"""
    if request.method == 'POST':
        try:
            if 'chat_history' in request.session:
                del request.session['chat_history']
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': f'Terjadi kesalahan: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def clear_chat(request):
    """Clear chat history"""
    if 'chat_history' in request.session:
        del request.session['chat_history']
    messages.success(request, 'Riwayat chat telah dihapus.')
    return redirect('main:chat')

def document_analysis_view(request):
    """
    View untuk halaman analisis dokumen dengan handling yang lebih baik
    """
    context = {}
    
    if request.method == 'POST':
        if 'pdf_file' not in request.FILES:
            messages.error(request, 'Pilih file PDF untuk dianalisis.')
            return render(request, 'document-analysis.html', context)
        
        pdf_file = request.FILES['pdf_file']
        
        # Validasi file
        if not pdf_file.name.lower().endswith('.pdf'):
            messages.error(request, 'File harus berformat PDF.')
            return render(request, 'document-analysis.html', context)
        
        if pdf_file.size > 10 * 1024 * 1024:  # 10MB limit
            messages.error(request, 'Ukuran file maksimal 10MB.')
            return render(request, 'document-analysis.html', context)
        
        try:
            # Baca file PDF
            document_text = read_pdf(pdf_file)
            
            if not document_text.strip():
                messages.error(request, 'File PDF kosong atau tidak dapat dibaca.')
                return render(request, 'document-analysis.html', context)
            
            # Analisis dokumen dengan prompt yang sudah diperbaiki
            prompt = """Dokumen yang akan dianalisis adalah sebagai berikut:
{}

Tugas Anda adalah menganalisis dokumen tersebut dan memberikan output dalam format JSON dengan bidang berikut:
- Judul_Dokumen: Judul dokumen hukum.
- Tanggal: Tanggal yang disebutkan dalam dokumen.
- Pihak: Array berisi informasi pihak dengan format objek yang memiliki properti Nama, Jabatan, Alamat, dan Peran.
- Deskripsi: Ringkasan singkat mengenai isi dokumen.
- Perjanjian: Array berisi poin-poin perjanjian.
- Hak: Array berisi hak-hak yang disebutkan.
- Penyelesaian: Cara penyelesaian sengketa yang disebutkan dalam dokumen.
- Pembayaran: Ketentuan terkait pembayaran, jika ada.
- Pengecualian: Array berisi pengecualian yang disebutkan.
- Skor: Penilaian terhadap kelengkapan, kejelasan, dan kualitas dokumen (1-10).
- Kesimpulan: Kesimpulan keseluruhan tentang dokumen.
- Clause_Suggestion: Array berisi saran klausul dengan format objek yang memiliki properti title dan description.
- Analisis: Object berisi Kesesuaian, Kekurangan, Potensi_Celah_Hukum, dan Rekomendasi.

Berikan analisis yang mencakup:
- Kesesuaian dokumen dengan kebutuhan hukum.
- Kesalahan atau kekurangan dalam teks dokumen.
- Potensi celah hukum yang dapat menimbulkan masalah.
- Rekomendasi klausa tambahan untuk mencegah potensi masalah di masa depan.

PENTING: Berikan HANYA JSON yang valid, tanpa text tambahan sebelum atau sesudahnya.

Contoh format output yang diharapkan:
{{
  "Judul_Dokumen": "Nama dokumen",
  "Tanggal": "Tanggal dokumen",
  "Pihak": [
    {{
      "Nama": "Nama pihak",
      "Jabatan": "Jabatan",
      "Alamat": "Alamat",
      "Peran": "Peran dalam perjanjian"
    }}
  ],
  "Deskripsi": "Deskripsi dokumen",
  "Perjanjian": ["Poin 1", "Poin 2"],
  "Hak": ["Hak 1", "Hak 2"],
  "Penyelesaian": "Cara penyelesaian sengketa",
  "Pembayaran": "Ketentuan pembayaran",
  "Pengecualian": ["Pengecualian 1"],
  "Skor": 7,
  "Kesimpulan": "Kesimpulan analisis",
  "Clause_Suggestion": [
    {{
      "title": "Judul klausul",
      "description": "Deskripsi klausul"
    }}
  ],
  "Analisis": {{
    "Kesesuaian": "Analisis kesesuaian",
    "Kekurangan": "Analisis kekurangan",
    "Potensi_Celah_Hukum": "Analisis celah hukum",
    "Rekomendasi": "Rekomendasi perbaikan"
  }}
}}
""".format(document_text)
            
            result = analysis_rag_chain.invoke({"input": prompt})
            answer = result.get("answer", "")
            
            # Clean up the answer - remove any non-JSON text
            answer = answer.strip()
            if answer.startswith('```json'):
                answer = answer[7:]
            if answer.startswith('```'):
                answer = answer[3:]
            if answer.endswith('```'):
                answer = answer[:-3]
            answer = answer.strip()
            
            # Coba parse sebagai JSON
            try:
                analysis_result = json.loads(answer)
                
                # Process and clean the data
                processed_analysis = process_analysis_result(analysis_result)
                
                context['analysis'] = {
                    'summary': processed_analysis.get('Kesimpulan', 'Tidak ada kesimpulan'),
                    'legal_risks': "Skor dokumen: {}/10. {}".format(
                        processed_analysis.get('Skor', 'N/A'),
                        processed_analysis.get('Analisis', {}).get('Potensi_Celah_Hukum', 'Tidak ada analisis risiko.')
                    ),
                    'full_result': processed_analysis
                }
                
            except json.JSONDecodeError as e:
                # Fallback jika tidak bisa parse JSON
                messages.error(request, 'Format hasil analisis tidak valid: {}'.format(str(e)))
                context['analysis'] = {
                    'summary': 'Error dalam parsing hasil analisis',
                    'legal_risks': 'Tidak dapat memproses hasil analisis',
                    'full_result': {'raw_answer': answer, 'error': str(e)}
                }
            
            context['filename'] = pdf_file.name
            messages.success(request, 'Dokumen "{}" berhasil dianalisis.'.format(pdf_file.name))
            
        except Exception as e:
            messages.error(request, 'Gagal menganalisis dokumen: {}'.format(str(e)))
    
    return render(request, 'document-analysis.html', context)

def process_analysis_result(data):
    """
    Process and clean the analysis result data
    """
    processed = {}
    
    # Basic fields
    processed['Judul_Dokumen'] = data.get('Judul Dokumen', data.get('Judul_Dokumen', ''))
    processed['Tanggal'] = data.get('Tanggal', '')
    processed['Deskripsi'] = data.get('Deskripsi', '')
    processed['Penyelesaian'] = data.get('Penyelesaian', '')
    processed['Pembayaran'] = data.get('Pembayaran', '')
    processed['Skor'] = data.get('Skor', 0)
    processed['Kesimpulan'] = data.get('Kesimpulan', '')
    
    # Process Pihak - fix the duplicate field issue
    pihak_data = data.get('Pihak', [])
    processed_pihak = []
    
    if isinstance(pihak_data, list):
        for pihak in pihak_data:
            if isinstance(pihak, dict):
                clean_pihak = {
                    'Nama': pihak.get('Nama', ''),
                    'Jabatan': pihak.get('Jabatan', ''),
                    'Alamat': pihak.get('Alamat', ''),
                    'Peran': pihak.get('Peran', pihak.get('Pihak', ''))  # Use Peran or fallback to Pihak
                }
                processed_pihak.append(clean_pihak)
            else:
                processed_pihak.append(str(pihak))
    
    processed['Pihak'] = processed_pihak
    
    # Process arrays
    processed['Perjanjian'] = data.get('Perjanjian', [])
    processed['Hak'] = data.get('Hak', [])
    processed['Pengecualian'] = data.get('Pengecualian', [])
    
    # Process Clause Suggestions
    clause_suggestions = data.get('Clause Suggestion', data.get('Clause_Suggestion', []))
    processed['Clause_Suggestion'] = clause_suggestions
    
    # Process Analisis
    analisis_data = data.get('Analisis', {})
    if isinstance(analisis_data, dict):
        processed['Analisis'] = {
            'Kesesuaian': analisis_data.get('Kesesuaian Dokumen dengan Kebutuhan Hukum', 
                                         analisis_data.get('Kesesuaian', '')),
            'Kekurangan': analisis_data.get('Kesalahan atau Kekurangan dalam Teks Dokumen',
                                          analisis_data.get('Kekurangan', '')),
            'Potensi_Celah_Hukum': analisis_data.get('Potensi Celah Hukum yang Dapat Menimbulkan Masalah',
                                                   analisis_data.get('Potensi_Celah_Hukum', '')),
            'Rekomendasi': analisis_data.get('Rekomendasi Klausa Tambahan',
                                           analisis_data.get('Rekomendasi', ''))
        }
    else:
        processed['Analisis'] = {}
    
    return processed


def business_checklist_view(request):
    """
    View untuk halaman generator checklist bisnis
    Menggunakan template business-checklist.html yang sudah ada
    """
    context = {}
    
    if request.method == 'POST':
        # Ambil data dari form sesuai dengan field name di template
        business_info = {
            "Nama Ide Bisnis": request.POST.get('business_name', ''),
            "Deskripsi Ide": request.POST.get('business_description', ''),
            "Target Pasar": request.POST.get('target_market', ''),
            "Model Bisnis": request.POST.get('business_model', ''),
            "Lokasi Operasional": request.POST.get('location', ''),
            "Bentuk Usaha": request.POST.get('business_type', 'PT'),
            "Kebutuhan Modal": request.POST.get('capital_needed', ''),
            "Tim atau Pendiri": request.POST.get('team_members', '').split(',') if request.POST.get('team_members') else [],
            "Jenis Produk/Jasa": request.POST.get('product_type', ''),
            "Rencana Pemasaran": request.POST.get('marketing_plan', ''),
            "Regulasi yang Diketahui": request.POST.get('known_regulations', '').split(',') if request.POST.get('known_regulations') else [],
            "Kemitraan/Investor": request.POST.get('partnerships', 'Tidak ada')
        }
        
        # Buat prompt dengan format yang lebih aman
        team_members_str = ', '.join(business_info["Tim atau Pendiri"])
        known_regulations_str = ', '.join(business_info["Regulasi yang Diketahui"])
        
        prompt = """
Saya memiliki ide bisnis sebagai berikut:
- Nama Ide Bisnis: {}
- Deskripsi Ide: {}
- Target Pasar: {}
- Model Bisnis: {}
- Lokasi Operasional: {}
- Bentuk Usaha: {}
- Kebutuhan Modal: {}
- Tim atau Pendiri: {}
- Jenis Produk/Jasa: {}
- Rencana Pemasaran: {}
- Regulasi yang Diketahui: {}
- Kemitraan/Investor: {}

Tolong bantu analisis ide bisnis saya. Berikan jawaban dalam format JSON dengan struktur:
{{
  "analisis_informasi_bisnis": "analisis singkat",
  "checklist": [
    {{
      "poin": "nama poin",
      "deskripsi": "deskripsi detail",
      "acuan_pasal": "referensi hukum jika ada"
    }}
  ],
  "risiko": [
    {{
      "deskripsi": "deskripsi risiko",
      "rekomendasi": "cara mitigasi"
    }}
  ],
  "rekomendasi_tambahan": ["rekomendasi 1", "rekomendasi 2"]
}}
""".format(
            business_info["Nama Ide Bisnis"],
            business_info["Deskripsi Ide"],
            business_info["Target Pasar"],
            business_info["Model Bisnis"],
            business_info["Lokasi Operasional"],
            business_info["Bentuk Usaha"],
            business_info["Kebutuhan Modal"],
            team_members_str,
            business_info["Jenis Produk/Jasa"],
            business_info["Rencana Pemasaran"],
            known_regulations_str,
            business_info["Kemitraan/Investor"]
        )
        
        try:
            result = checklist_rag_chain.invoke({"input": prompt})
            answer = result.get("answer", "")
            
            # Clean up the answer
            answer = answer.strip()
            if answer.startswith('```json'):
                answer = answer[7:]
            if answer.startswith('```'):
                answer = answer[3:]
            if answer.endswith('```'):
                answer = answer[:-3]
            answer = answer.strip()
            
            # Coba parse sebagai JSON
            try:
                checklist_result = json.loads(answer)
                context['checklist_results'] = checklist_result
            except json.JSONDecodeError:
                context['checklist_results'] = {
                    "analisis_informasi_bisnis": answer,
                    "checklist": [],
                    "risiko": [],
                    "rekomendasi_tambahan": []
                }
            
            context['business_info'] = business_info
            messages.success(request, 'Checklist bisnis berhasil dibuat.')
            
        except Exception as e:
            messages.error(request, 'Terjadi kesalahan: {}'.format(str(e)))
    
    return render(request, 'business-checklist.html', context)