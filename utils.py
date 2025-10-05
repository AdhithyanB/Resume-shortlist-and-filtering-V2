import re
from typing import List, Tuple

SOFT_SKILLS = ['communication','team','lead','leadership','collaborat','problem solv','presentation','mentor','manage','organized']
EDU_KEYWORDS = ['bachelor','master','phd','b.sc','m.sc','bs','ms','btech','mtech','degree','mba','associate']
DOMAIN_KEYWORDS = {
    'fintech': ['finance','fintech','bank','trading','payments'],
    'healthcare': ['health','healthcare','clinical','pharma','medical'],
    'ai': ['machine learning','ml','deep learning','nlp','computer vision','artificial intelligence'],
    'software': ['software','backend','frontend','full-stack','devops','engineering']
}

def extract_skills(text: str, top_k: int = 40) -> List[str]:
    SKILL_KEYWORDS = ['python','java','c++','c#','sql','mongodb','postgres','tensorflow','pytorch','keras','scikit-learn','spark','aws','gcp','azure','docker','kubernetes','react','angular','node','fastapi','flask','django','nlp','opencv','pandas','numpy']
    found = []
    low = text.lower()
    for k in SKILL_KEYWORDS:
        if k in low and k not in found:
            found.append(k)
            if len(found) >= top_k:
                break
    return found

def extract_certifications(text: str) -> List[str]:
    cands = re.findall(r'([A-Za-z0-9\-\s]{2,40}certif[A-Za-z0-9\-\s]{0,40})', text, flags=re.IGNORECASE)
    fallback = []
    low = text.lower()
    for key in ['aws certified','gcp','azure','professional','certified','certificate']:
        if key in low:
            fallback.append(key)
    return list(dict.fromkeys(cands + fallback))[:10]

def extract_years_of_experience(text: str) -> float:
    years = re.findall(r'(\d{1,2})\+?\s+years', text, flags=re.IGNORECASE)
    years = [int(y) for y in years]
    if years:
        return max(years)
    spans = re.findall(r'(20\d{2})\s*[-to]+\s*(20\d{2})', text)
    total = 0
    for a,b in spans:
        try:
            total = max(total, int(b)-int(a))
        except:
            pass
    if total>0:
        return total
    return 0.0

def detect_red_flags(text: str) -> List[str]:
    flags = []
    low = text.lower()
    if len(low.split()) < 80:
        flags.append('very_short_resume')
    years = re.findall(r'(\d{4})', text)
    if len(years) >= 4:
        flags.append('possible_job_hopping')
    emails = re.findall(r'[\w\.-]+@[\w\.-]+', text)
    for e in emails:
        if e.endswith(('.ru', '.cn')):
            flags.append('suspicious_email_domain')
    yrs = extract_years_of_experience(text)
    if yrs>50:
        flags.append('unrealistic_experience')
    return list(dict.fromkeys(flags))

def extract_education(text: str) -> List[str]:
    low = text.lower()
    found = []
    for k in EDU_KEYWORDS:
        if k in low:
            found.append(k)
    return found

def detect_domain_fit(text: str, job_domain: str=None) -> Tuple[str, float]:
    low = text.lower()
    scores = {}
    for domain, kws in DOMAIN_KEYWORDS.items():
        score = sum(low.count(k) for k in kws)
        scores[domain] = score
    best = max(scores, key=lambda k: scores[k])
    total = sum(scores.values()) if sum(scores.values())>0 else 1
    pct = round(scores[best]/total*100,2) if total>0 else 0.0
    if job_domain:
        jd = job_domain.lower()
        align = 100.0 if jd in best else pct
        return best, align
    return best, pct

def readability_score(text: str) -> float:
    words = text.split()
    if not words:
        return 0.0
    avg_word_len = sum(len(w) for w in words)/len(words)
    sentences = text.count('.')+text.count('!')+text.count('?')
    if sentences==0:
        sentences = 1
    wps = len(words)/sentences
    score = max(0, min(100, 100 - (abs(15-wps)*4 + max(0,(avg_word_len-6))*3)))
    return round(score,2)
