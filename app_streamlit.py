import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='AI Resume Pro Demo', layout='wide')
st.title('AI Resume & Hiring Assistance — Pro Demo (Investor-ready)')

with st.sidebar:
    st.header('Demo Controls')
    api_url = st.text_input('Backend API URL', value='http://localhost:8000/score')

st.markdown('Upload multiple resumes (PDF/DOCX/TXT). Use sample resumes in sample_data/resumes or upload your own.')
uploaded = st.file_uploader('Upload resumes', accept_multiple_files=True, type=['pdf','docx','txt'])
job_desc = st.text_area('Job description', height=200, value='We are hiring a Machine Learning Engineer with 3+ years of experience in NLP, Python and ML frameworks.')

if st.button('Score Resumes'):
    if not uploaded:
        st.warning('Upload at least one resume.')
    elif not job_desc.strip():
        st.warning('Provide a job description.')
    else:
        files = []
        for f in uploaded:
            files.append(('files', (f.name, f.getvalue(), 'application/octet-stream')))
        data = {'job_description': job_desc}
        try:
            resp = requests.post(api_url, files=files, data=data, timeout=60)
            resp.raise_for_status()
            results = resp.json()
        except Exception as e:
            st.error(f'Error calling backend: {e}')
            results = []
        if results:
            df = pd.DataFrame(results)
            display_df = df.rename(columns={
                'Candidate_Name':'Candidate Name','Match_Score_pct':'Match Score (%)',
                'Skill_Match_pct':'Skill Match (%)','Experience_Match_pct':'Experience Match (%)',
                'Education_Match_pct':'Education Match (%)','Domain_Fit':'Domain Fit',
                'ATS_Keywords_pct':'ATS Keywords Match (%)','Soft_Skills_Score':'Soft Skills Score',
                'Certifications_and_Achievements':'Certifications & Achievements','Red_Flags_pct':'Red Flags (%)',
                'Resume_Length_Readability':'Resume Readability','Diversity_of_Skills':'Diversity of Skills',
                'Final_Recommendation':'Final Recommendation','Last_Updated':'Last Updated'
            })
            st.subheader('Candidate Scoring Table')
            st.dataframe(display_df, height=400)
            st.subheader('Match Score Distribution')
            fig = px.bar(display_df, x='Candidate Name', y='Match Score (%)', color='Match Score (%)', text='Match Score (%)')
            st.plotly_chart(fig, use_container_width=True)
            st.subheader('Red Flags Summary')
            fig2 = px.bar(display_df, x='Candidate Name', y='Red Flags (%)', color='Red Flags (%)', text='Red Flags (%)')
            st.plotly_chart(fig2, use_container_width=True)
            csv = display_df.to_csv(index=False).encode('utf-8')
            st.download_button('Download CSV', data=csv, file_name='candidate_scores.csv', mime='text/csv')
