from typing import List, Dict, Optional
from pydantic import BaseModel
from .utils import extract_skills, extract_certifications, extract_years_of_experience, detect_red_flags, extract_education, detect_domain_fit, readability_score
import math

class ScoreOutput(BaseModel):
    Rank: int
    Candidate_Name: str
    Match_Score_pct: float
    Skill_Match_pct: float
    Experience_Match_pct: float
    Education_Match_pct: float
    Domain_Fit: str
    ATS_Keywords_pct: float
    Soft_Skills_Score: float
    Certifications_and_Achievements: List[str]
    Red_Flags_pct: float
    Resume_Length_Readability: float
    Last_Updated: str
    Diversity_of_Skills: float
    Final_Recommendation: str

USE_EMBEDDINGS = False
try:
    from sentence_transformers import SentenceTransformer, util
    model = SentenceTransformer('all-MiniLM-L6-v2')
    USE_EMBEDDINGS = True
except Exception:
    USE_EMBEDDINGS = False

from sklearn.feature_extraction.text import TfidfVectorizer

def _compute_semantic_similarity(job_desc: str, texts: List[str]) -> List[float]:
    if USE_EMBEDDINGS:
        job_emb = model.encode(job_desc, convert_to_tensor=True)
        emb = model.encode(texts, convert_to_tensor=True)
        sims = util.cos_sim(job_emb, emb)[0].cpu().tolist()
        return [float(s) for s in sims]
    else:
        corpus = [job_desc] + texts
        vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        X = vectorizer.fit_transform(corpus)
        job_vec = X[0]
        sims = (X[1:] @ job_vec.T).toarray().flatten()
        maxv = max(sims) if len(sims)>0 else 1.0
        return [float(s)/maxv if maxv>0 else 0.0 for s in sims]

def score_resumes(parsed_resumes: List[Dict], job_description: str, job_domain: Optional[str]=None) -> List[Dict]:
    texts = [r['text'] for r in parsed_resumes]
    filenames = [r['filename'] for r in parsed_resumes]
    sem_sims = _compute_semantic_similarity(job_description, texts)
    results = []
    for idx, (fn, text, sim) in enumerate(zip(filenames, texts, sem_sims)):
        skills = extract_skills(text)
        skill_match = min(len(skills)/8*100,100)
        yrs = extract_years_of_experience(text)
        exp_match = min(yrs/5*100,100)
        edu = extract_education(text)
        edu_score = min(len(edu)/2*100,100)
        domain, domain_pct = detect_domain_fit(text, job_domain)
        certs = extract_certifications(text)
        red_flags = detect_red_flags(text)
        red_pct = min(len(red_flags)*20,100)
        soft_score = sum(1 for k in ['communication','team','lead'] if k in text.lower())/3*100
        ats_pct = skill_match
        read_score = readability_score(text)
        diversity = min(len(set(skills))/10*100,100)
        last_updated = 'N/A'
        final = (sim*100*0.4 + skill_match*0.25 + exp_match*0.15 + edu_score*0.1 + soft_score*0.05 - red_pct*0.1)
        final = max(0, min(final, 100))
        recommendation = 'Shortlist' if final>75 else ('Review Manually' if final>50 else 'Reject')
        results.append({
            'Rank': idx+1,
            'Candidate_Name': fn,
            'Match_Score_pct': round(sim*100,2),
            'Skill_Match_pct': round(skill_match,2),
            'Experience_Match_pct': round(exp_match,2),
            'Education_Match_pct': round(edu_score,2),
            'Domain_Fit': domain,
            'ATS_Keywords_pct': round(ats_pct,2),
            'Soft_Skills_Score': round(soft_score,2),
            'Certifications_and_Achievements': certs,
            'Red_Flags_pct': round(red_pct,2),
            'Resume_Length_Readability': round(read_score,2),
            'Last_Updated': last_updated,
            'Diversity_of_Skills': round(diversity,2),
            'Final_Recommendation': recommendation
        })
    results = sorted(results, key=lambda x: x['Match_Score_pct'], reverse=True)
    for i,r in enumerate(results):
        r['Rank'] = i+1
    return results
