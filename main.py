from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from .parser import extract_text_from_upload
from .model import score_resumes, ScoreOutput
import uvicorn

app = FastAPI(title='AI Resume & Hiring Assistance - Pro')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

@app.post('/score', response_model=List[ScoreOutput])
async def score_endpoint(files: List[UploadFile] = File(...), job_description: str = Form(...), job_domain: Optional[str] = Form(None)):
    parsed = []
    for f in files:
        text = await extract_text_from_upload(f)
        parsed.append({'filename': f.filename, 'text': text})
    results = score_resumes(parsed, job_description, job_domain=job_domain)
    return results

@app.get('/health')
def health():
    return {'status':'ok'}

if __name__ == '__main__':
    uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=True)
