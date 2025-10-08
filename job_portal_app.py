import streamlit as st
import pandas as pd
import re
import random
from datetime import datetime, timedelta
import io
import PyPDF2


# Config

SKILLS = ["python","sql","excel","tableau","power bi","javascript","react","aws","docker","java"]


# Functions

def extract_skills(text):
    if not isinstance(text, str):
        return []
    text_low = text.lower()
    return [skill for skill in SKILLS if skill in text_low]

def parse_salary(s):
    try:
        nums = re.findall(r"\d+", str(s))
        return int(nums[0]) if nums else None
    except:
        return None

def generate_fake_jobs(n=50):
    titles = ["Data Analyst","Software Engineer","Frontend Developer","Backend Developer",
              "Data Scientist","DevOps Engineer","Business Analyst","ML Engineer"]
    companies = ["Acme Corp","Globex","Innotech","Cyberdyne","Wayne Enterprises"]
    locations = ["Remote","London, UK","Berlin, Germany","Cluj-Napoca, Romania","Bucharest, Romania"]

    data = []
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2025, 1, 1)

    for i in range(n):
        title = random.choice(titles)
        company = random.choice(companies)
        location = random.choice(locations)
        date_posted = start_date + timedelta(days=random.randint(0, (end_date-start_date).days))
        date_posted_str = date_posted.strftime("%Y-%m-%d")
        salary_min = random.choice([2000,2500,3000,3500,4000,4500])
        salary_max = salary_min + random.choice([500,1000,2000])
        salary = f"{salary_min}-{salary_max} EUR/month"
        desc_skills = random.sample(SKILLS, k=random.randint(2,4))
        description = f"We are looking for a {title}. Skills required: {', '.join(desc_skills)}."
        url = f"https://example.com/job/{i}"
        data.append([title, company, location, date_posted_str, salary, description, url])

    df = pd.DataFrame(data, columns=["title","company","location","date_posted","salary","description","url"])
    return df

def pdf_to_text(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + " "
    return text

def job_match_score(job_skills, cv_skills):
    if not job_skills:
        return 0
    matches = len(set(job_skills) & set(cv_skills))
    return matches / len(set(job_skills))

def convert_df_to_csv(df_dict):
    output = io.StringIO()
    for name, d in df_dict.items():
        output.write(f"# {name}\n")
        d.to_csv(output, index=False)
        output.write("\n")
    return output.getvalue()


# Streamlit UI

st.title("💼 Job Market & Smart Recommender App")

#  Tabs 
tab1, tab2 = st.tabs(["📊 Market Overview", "💻 Job Recommendations"])

#  Shared job dataset 
st.sidebar.header("Job Dataset Options")
use_fake = st.sidebar.checkbox("Generate dataset", value=True)

if use_fake:
    df_jobs = generate_fake_jobs(50)
else:
    uploaded = st.sidebar.file_uploader("Upload jobs CSV", type="csv")
    if uploaded:
        df_jobs = pd.read_csv(uploaded)
    else:
        st.sidebar.info("Upload a CSV or check 'Generate dataset'")
        st.stop()

# Ensure required columns
for col in ["description","date_posted","salary"]:
    if col not in df_jobs.columns:
        df_jobs[col] = None
df_jobs["skills"] = df_jobs["description"].apply(extract_skills)


# Tab 1: Market Overview

with tab1:
    st.header("📊 Job Market Overview")

    st.subheader("Raw Job Data Preview")
    st.dataframe(df_jobs.head())

    # Top Skills
    skill_counts = {}
    for skills in df_jobs["skills"]:
        for s in skills:
            skill_counts[s] = skill_counts.get(s,0)+1
    skills_df = pd.DataFrame(skill_counts.items(), columns=["Skill","Count"]).sort_values("Count", ascending=False)
    st.subheader("🔥 Top Skills in Job Postings")
    st.bar_chart(skills_df.set_index("Skill"))

    # Jobs over time
    if df_jobs["date_posted"].notna().any():
        df_jobs["date_posted"] = pd.to_datetime(df_jobs["date_posted"], errors="coerce")
        trend = df_jobs.groupby(df_jobs["date_posted"].dt.to_period("M")).size()
        st.subheader("📈 Job Postings Over Time")
        st.line_chart(trend)

    # Salary by Skill
    salary_df = pd.DataFrame()
    if df_jobs["salary"].notna().any():
        df_jobs["salary_num"] = df_jobs["salary"].apply(parse_salary)
        salary_by_skill = []
        for skill in SKILLS:
            subset = df_jobs[df_jobs["skills"].apply(lambda x: skill in x)]
            if len(subset)>0:
                salary_by_skill.append((skill, subset["salary_num"].mean()))
        salary_df = pd.DataFrame(salary_by_skill, columns=["Skill","Avg Salary"]).dropna()
        if not salary_df.empty:
            st.subheader("💰 Average Salary by Skill")
            st.bar_chart(salary_df.set_index("Skill"))

    # Download Market Analysis CSV
    if st.button("💾 Download Market Analysis CSV"):
        analysis_dict = {"Top Skills": skills_df}
        if not salary_df.empty:
            analysis_dict["Salary by Skill"] = salary_df
        if df_jobs["date_posted"].notna().any():
            trend_df = trend.reset_index()
            trend_df.columns = ["Month","Postings"]
            analysis_dict["Job Postings Over Time"] = trend_df
        csv_content = convert_df_to_csv(analysis_dict)
        st.download_button("Download CSV", data=csv_content, file_name="market_analysis.csv", mime="text/csv")


# Tab 2: Job Recommendations

with tab2:
    st.header("💻 Personalized Job Recommendations")

    # CV upload
    cv_file = st.file_uploader("Upload your CV (PDF or TXT)", type=["pdf","txt"])

    if cv_file:
        
        with st.spinner("Analyzing your CV..."):
            import time
            time.sleep(2)  

            if cv_file.type == "application/pdf":
                cv_text = pdf_to_text(cv_file)
            else:
                cv_text = str(cv_file.read(), "utf-8")
            
            cv_skills = extract_skills(cv_text)
        

        st.success("✅ CV analysis complete!")
        st.subheader("Detected Skills from Your CV")
        st.write(cv_skills)

        # Compute match scores
        df_jobs["match_score"] = df_jobs["skills"].apply(lambda x: job_match_score(x, cv_skills))
        df_sorted = df_jobs.sort_values("match_score", ascending=False)

        st.subheader("Top Recommended Jobs")
        st.dataframe(df_sorted[["title","company","location","match_score"]].head(10))

        # Skill gap analysis
        st.subheader("Skill Gap Analysis")
        missing_skills_count = {}
        for skill in SKILLS:
            if skill not in cv_skills:
                count = df_jobs["skills"].apply(lambda x: skill in x).sum()
                missing_skills_count[skill] = count
        missing_df = pd.DataFrame(missing_skills_count.items(), columns=["Missing Skill","Count"]).sort_values("Count", ascending=False)
        st.bar_chart(missing_df.set_index("Missing Skill"))

        
if cv_file:
    
    df_sorted = df_jobs.sort_values("match_score", ascending=False)

   
      # Download recommended jobs for Tableau
    st.subheader("Export Recommended Jobs for Tableau")
    analysis_dict = {
        "Recommended Jobs": df_sorted[["title","company","location","match_score"]],
        "Missing Skills": df_sorted[["title","missing_skills"]] if "missing_skills" in df_sorted.columns else pd.DataFrame()
    }
    csv_content = convert_df_to_csv(analysis_dict)
    st.download_button(
        label="💾 Download Recommended Jobs for Tableau",
        data=csv_content,
        file_name="recommended_jobs_for_tableau.csv",
        mime="text/csv"
    )
    st.dataframe(df_sorted.head(10))


        

