from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from django.conf import settings
from langchain_chroma import Chroma
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
    # "e39ab-uu-nomor-8-tahun-1999.pdf",
    # "kolonial_kuh_perdata_fix.pdf",
    # "KUH DAGANG.pdf",
    # "UU Nomor  19 Tahun 2016.pdf",
    # "UU Nomor 13 Tahun 2003.pdf",
    # "UU_1999_30.pdf",
    # "UU_Nomor_11_Tahun_2020-compressed.pdf",
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