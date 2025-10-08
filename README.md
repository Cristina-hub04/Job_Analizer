# Job_Analizer

**Job Market & Smart Recommender App**

**A Streamlit web application** that **analyzes** job postings, **identifies** in-demand skills, and **provides** personalized job recommendations based on a user’s CV. Perfect for students and junior job seekers to explore the job market and discover jobs that match their skills. The app let's you download the recommendations via **Tableau**.

**Features**

1️⃣ **Market Overview**

Upload or generate a dataset of job postings.

Analyze and visualize:

Top in-demand skills

Job postings over time

Average salary by skill

Interactive Plotly charts for dynamic dashboards

Download CSV for analysis or Tableau

2️⃣ **CV-Based Job Recommendations**

Upload your CV (PDF or TXT)

Automatically extract your skills

Compute skill match scores for each job

Show top recommended jobs in a clean table

Highlight missing skills per job

Optional filters: location, minimum skill match, salary range

Download personalized recommendations as CSV for Tableau

3️⃣ **User-Friendly Interface**

Streamlit tabs separate Market Overview and Job Recommendations

Progress spinners and success animations for interactivity

Clean layout with columns, metrics, and charts




### Installation

1️⃣ Clone the repository

```bash
git clone https://github.com/yourusername/job-market-recommender.git
cd job-market-recommender
```


2️⃣ Install dependencies

```bash
pip install streamlit pandas plotly PyPDF2
```

3️⃣ Run the app

```bash
streamlit run job_portal_app.py
```
💡 Tips:

Make sure you are using Python 3.9 or higher.

On some systems, you might need pip3 instead of pip:
```bash
pip3 install streamlit pandas plotly PyPDF2
```


Includes progress spinners and success animations.

Clean layout with columns, metrics, and interactive charts.
