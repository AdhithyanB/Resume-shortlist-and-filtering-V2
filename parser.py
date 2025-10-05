import io
from fastapi import UploadFile

try:
    import pdfplumber
except Exception:
    pdfplumber = None

try:
    import docx
except Exception:
    docx = None

def text_from_pdf_bytes(data: bytes) -> str:
    if pdfplumber is None:
        try:
            return data.decode('utf-8', errors='ignore')
        except:
            return ''
    text = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            text.append(page.extract_text() or '')
    return '\n'.join(text)

def text_from_docx_bytes(data: bytes) -> str:
    if docx is None:
        try:
            return data.decode('utf-8', errors='ignore')
        except:
            return ''
    buf = io.BytesIO(data)
    doc = docx.Document(buf)
    paras = [p.text for p in doc.paragraphs]
    return '\n'.join(paras)

async def extract_text_from_upload(upload_file: UploadFile) -> str:
    ext = upload_file.filename.split('.')[-1].lower() if upload_file.filename else ''
    data = await upload_file.read()
    if ext in ['pdf']:
        return text_from_pdf_bytes(data)
    elif ext in ['docx', 'doc']:
        return text_from_docx_bytes(data)
    else:
        try:
            return data.decode('utf-8', errors='ignore')
        except:
            return ''
