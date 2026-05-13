# AI Resume Analyzer and Job Role Predictor

An AI-based resume analysis web application that predicts suitable job roles, calculates ATS score, detects skills, finds missing skills, and generates a PDF resume analysis report.

## Features

- Login and Register system
- Resume PDF upload
- Resume text analysis
- Machine Learning based job role prediction
- ATS resume score
- Skill detection
- Missing skill suggestions
- Skill match percentage
- Pie chart visualization
- Career roadmap
- Resume analysis history using SQLite
- Downloadable PDF report
- Dark professional UI

## Technologies Used

- Python
- Streamlit
- Scikit-learn
- SQLite
- Pandas
- Matplotlib
- PyPDF2
- ReportLab
- Joblib

## Project Structure

```text
AI_Resume_Analyzer
│
├── app.py
├── database.py
├── train_model.py
├── resume_dataset.csv
├── model.pkl
├── vectorizer.pkl
├── requirements.txt
├── README.md
└── resume_analyzer.db