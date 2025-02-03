import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
import json
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
# Load environment variables dari .env
load_dotenv()

# --- Import library LangChain dan lainnya ---
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_chroma import Chroma
from langchain_core.messages import AIMessage, HumanMessage

# --- Fungsi untuk memuat dan memisahkan dokumen PDF ---
def load_and_split_pdf(file_path, text_splitter):
    loader = PyPDFLoader(file_path)
    data = loader.load()  # Muat dokumen sebagai satu kesatuan
    split_docs = text_splitter.split_documents(data)  # Pisahkan dokumen
    return split_docs

# --- Inisialisasi Global (hanya di-load satu kali saat startup) ---

# Inisialisasi text splitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap =400,separators= ["\n\nPasal", "\n\nBAB", "\n\nBagian", "\n\n"])

# Gabungkan dokumen dari file-file PDF
combined_docs = []
file_paths = [
    "5. UU-40-2007 PERSEROAN TERBATAS.pdf",
    "e39ab-uu-nomor-8-tahun-1999.pdf",
    "kolonial_kuh_perdata_fix.pdf",
    "KUH DAGANG.pdf",
    "UU Nomor  19 Tahun 2016.pdf",
    "UU Nomor 13 Tahun 2003.pdf",
    "UU_1999_30.pdf",
    "UU_Nomor_11_Tahun_2020-compressed.pdf",
]
base_path = os.path.join(settings.BASE_DIR, 'static', 'docs')

for file_path in file_paths:
    full_path = os.path.join(base_path, file_path)
    print(f"Processing: {full_path}")
    additional_docs = load_and_split_pdf(full_path, text_splitter)
    combined_docs += additional_docs
    print(f"Added {len(additional_docs)} documents from {file_path}")

print("Total number of combined documents:", len(combined_docs))

# Inisialisasi vectorstore dengan embeddings (hanya satu kali)
vectorstore = Chroma.from_documents(
    documents=combined_docs,
    embedding=GoogleGenerativeAIEmbeddings(model="models/embedding-001")
)
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})

# Inisialisasi LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0.2,
    top_p=0.95,
    top_k=40,
    max_tokens=8192,
    response_mime_type="text/plain"
)

# Definisikan prompt sistem untuk QA
system_prompt = """
Anda adalah AI hukum yang sangat terlatih, dirancang untuk menjawab pertanyaan pengguna dengan cara yang jelas, akurat, dan ramah. Anda bertugas untuk:

1. **Pemanfaatan Konteks Dokumen**:
   - Berikut adalah konteks dokumen yang ditemukan:
     {context}
   - Gunakan konteks ini untuk mendukung jawaban Anda jika relevan dengan pertanyaan pengguna.
   - Jika konteks dokumen tidak relevan dengan pertanyaan, abaikan konteks tersebut dan gunakan pengetahuan hukum Anda untuk memberikan jawaban.

2. **Fokus pada Pertanyaan**:
   - Berikan jawaban yang langsung menjawab inti pertanyaan pengguna.
   - Jangan menyertakan informasi yang tidak relevan atau tidak mendukung jawaban.

3. **Penyampaian Jawaban**:
   - Jawaban Anda harus terstruktur dengan format berikut:
     - **Jawaban Langsung**: Jawab inti pertanyaan dengan ringkas dan jelas.
     - **Penjelasan**: Berikan alasan atau dasar hukum yang mendukung jawaban Anda.
     - Jika ada pasal yang relevan, tambahkan rujukan pasal tersebut. Jika tidak ada, cukup berikan jawaban tanpa menyebutkan bahwa rujukan tidak ditemukan.

4. **Nada dan Gaya**:
   - Gunakan bahasa yang profesional tetapi tetap ramah dan mudah dipahami.
   - Hindari istilah teknis yang berlebihan, dan jika digunakan, berikan penjelasan singkat untuk membantu pengguna memahami.

5. **Ketentuan Khusus**:
   - Jika retrieval menghasilkan dokumen yang tidak relevan, berikan jawaban berdasarkan pengetahuan hukum Anda tanpa menyebutkan informasi retrieval yang tidak relevan.
   - Jangan memberikan informasi yang tidak diminta atau spekulatif.

**Catatan Penting**:
- Prioritaskan keakuratan dan relevansi dalam setiap jawaban.
- Jangan menyertakan bagian "Rujukan Pasal" jika tidak ada pasal yang relevan.
- Fokus utama Anda adalah memberikan jawaban langsung yang akurat, relevan, dan mendukung kebutuhan pengguna.
"""

# Definisikan prompt untuk reformulasi pertanyaan agar mandiri (contextualization)
contextualize_q_system_prompt = '''Anda adalah asisten hukum AI yang dirancang untuk memahami dan mengolah pertanyaan hukum. Tugas Anda adalah:

1. **Mengidentifikasi Kebutuhan Konteks**:
   - Berdasarkan sejarah percakapan (chat history) dan dokumen hukum yang relevan, tentukan apakah pertanyaan terbaru pengguna memerlukan konteks tambahan untuk dipahami sepenuhnya.

2. **Reformulasi Pertanyaan**:
   - Jika pertanyaan pengguna merujuk pada konteks dari percakapan sebelumnya, reformulasikan pertanyaan tersebut menjadi pertanyaan mandiri yang jelas dan lengkap tanpa memerlukan chat history.
   - Jika pertanyaan sudah mandiri dan jelas, kembalikan pertanyaan tersebut apa adanya.

3. **Tujuan Reformulasi**:
   - Buat pertanyaan mandiri agar sistem dapat mencari dokumen hukum yang relevan dan memberikan jawaban yang akurat.

**Peraturan**:
- Jangan menjawab pertanyaan.
- Jangan memberikan penjelasan tambahan.
- Hanya kembalikan pertanyaan dalam format yang mandiri dan dapat dipahami tanpa referensi ke chat history.
- Jika pertanyaan sudah jelas dan tidak memerlukan perubahan, kembalikan seperti apa adanya.
'''

# Buat prompt untuk reformulasi pertanyaan berdasarkan riwayat percakapan
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

# Buat retriever yang aware terhadap riwayat percakapan
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

# Buat prompt untuk chain QA
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

# Buat chain untuk menjawab pertanyaan berdasarkan dokumen yang diretrieval
question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

# Gabungkan keduanya menjadi retrieval chain (RAG)
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

# --- API View Django ---
@csrf_exempt
def chat_api(request):
    """
    View ini:
      - GET: Merender halaman form chat beserta riwayat chat (jika ada) yang disimpan di session.
      - POST: Mengambil input pertanyaan, memanggil rag_chain untuk mendapatkan jawaban, 
              memperbarui chat history, dan merender ulang halaman dengan riwayat chat yang ter-update.
    """
    # Ambil chat history dari session (jika belum ada, set ke list kosong)
    chat_history = request.session.get("chat_history", [])

    if request.method == "GET":
        context = {"chat_history": chat_history}
        return render(request, "chat_form.html", context)
    
    elif request.method == "POST":
        question = request.POST.get("question", "").strip()

        if not question:
            context = {
                "error": "Masukkan pertanyaan Anda.",
                "chat_history": chat_history,
            }
            return render(request, "chat_form.html", context)

        try:
            # Panggil rag_chain dengan input dan chat_history yang tersimpan
            result = rag_chain.invoke({"input": question, "chat_history": chat_history})
            answer = result.get("answer", "")

            # Perbarui chat_history dengan pesan pengguna dan jawaban AI
            chat_history.append({"role": "human", "content": question})
            chat_history.append({"role": "ai", "content": answer})
            # Simpan chat_history yang diperbarui ke session
            request.session["chat_history"] = chat_history

            context = {
                "question": question,
                "answer": answer,
                "chat_history": chat_history,
            }
            return render(request, "chat_form.html", context)
        except Exception as e:
            context = {
                "error": f"Terjadi kesalahan: {str(e)}",
                "chat_history": chat_history,
            }
            return render(request, "chat_form.html", context)
    
    else:
        return HttpResponse("Metode tidak diizinkan.", status=405)