from PyPDF2 import PdfReader
# Fungsi bantu untuk membaca PDF (menggunakan PyPDF2)
def read_pdf(file_obj):
    """
    Membaca isi file PDF dan mengembalikan teks yang terkandung di dalamnya.
    Args:
        file_obj (file-like object): File PDF yang diupload.
    Returns:
        str: Teks gabungan dari semua halaman PDF.
    """
    reader = PdfReader(file_obj)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()
