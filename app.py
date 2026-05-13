import streamlit as st
import joblib
import matplotlib.pyplot as plt
from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

from database import (
    create_tables,
    add_user,
    check_user,
    user_exists,
    save_history,
    get_history
)

# ---------------- LOAD MODEL ----------------
model = joblib.load("model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

# ---------------- DATABASE ----------------
create_tables()

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# ---------------- DARK THEME ----------------
st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
    color: white;
}

h1, h2, h3, h4, h5, h6 {
    color: #00FFF7;
}

p, label, div {
    color: white;
}

.stTextInput input {
    background-color: #1E1E1E;
    color: white;
    border: 1px solid #00ADB5;
    border-radius: 8px;
}

.stTextArea textarea {
    background-color: #1E1E1E;
    color: white;
    border: 1px solid #00ADB5;
    border-radius: 10px;
}

.stButton>button {
    background-color: #00ADB5;
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 240px;
    font-size: 16px;
    font-weight: bold;
    border: none;
}

.stButton>button:hover {
    background-color: #008C94;
    color: white;
}

[data-testid="stSidebar"] {
    background-color: #161B22;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# ---------------- LOGIN / REGISTER PAGE ----------------
def login_page():
    st.title("🔐 AI Resume Analyzer Login")
    st.write("Login or register to access the resume analyzer system.")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            user = check_user(username, password)

            if user:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password.")

    with tab2:
        new_username = st.text_input("Create Username", key="reg_user")
        new_password = st.text_input("Create Password", type="password", key="reg_pass")

        if st.button("Register"):
            if new_username == "" or new_password == "":
                st.warning("Please enter username and password.")
            elif user_exists(new_username):
                st.error("Username already exists.")
            else:
                add_user(new_username, new_password)
                st.success("Registration successful! Now login.")

# ---------------- PDF REPORT ----------------
def create_pdf_report(predicted_role, detected_skills, missing_skills, ats_score, skill_match):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(70, 750, "AI Resume Analysis Report")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(70, 710, f"Username: {st.session_state.username}")
    pdf.drawString(70, 685, f"Predicted Job Role: {predicted_role}")
    pdf.drawString(70, 660, f"ATS Resume Score: {ats_score}/100")
    pdf.drawString(70, 635, f"Skill Match Percentage: {skill_match}%")

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(70, 595, "Detected Skills:")

    y = 570
    pdf.setFont("Helvetica", 12)

    if detected_skills:
        for skill in detected_skills:
            pdf.drawString(90, y, f"- {skill}")
            y -= 18
    else:
        pdf.drawString(90, y, "No major skills detected.")
        y -= 18

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(70, y - 20, "Missing Skills:")

    y -= 45
    pdf.setFont("Helvetica", 12)

    if missing_skills:
        for skill in missing_skills:
            pdf.drawString(90, y, f"- {skill}")
            y -= 18
    else:
        pdf.drawString(90, y, "No missing skills detected.")

    pdf.save()
    buffer.seek(0)
    return buffer

# ---------------- MAIN APP ----------------
def resume_analyzer_app():

    st.sidebar.title("📄 AI Resume Analyzer")
    st.sidebar.write(f"Welcome, {st.session_state.username}")

    menu = st.sidebar.radio(
        "Menu",
        ["Analyze Resume", "View History"]
    )

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    st.sidebar.info("""
Features:
- SQLite Login/Register
- AI Job Prediction
- ATS Resume Score
- Skill Match Analysis
- Resume History
- PDF Report Download
""")

    if menu == "View History":
        st.title("📜 Resume Analysis History")

        records = get_history(st.session_state.username)

        if records:
            for i, record in enumerate(records, start=1):
                predicted_role, ats_score, skill_match, detected_skills = record

                st.subheader(f"Analysis {i}")
                st.write(f"Predicted Role: {predicted_role}")
                st.write(f"ATS Score: {ats_score}/100")
                st.write(f"Skill Match: {skill_match}%")
                st.write(f"Detected Skills: {detected_skills}")
                st.markdown("---")
        else:
            st.info("No resume analysis history found.")

    else:
        st.title("📄 AI Resume Analyzer and Job Role Predictor")
        st.write("Analyze resume, predict job role, calculate ATS score, and get improvement suggestions.")

        uploaded_file = st.file_uploader("Upload Resume PDF", type=["pdf"])

        resume_text = ""

        if uploaded_file is not None:
            pdf_reader = PdfReader(uploaded_file)

            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    resume_text += text

        manual_text = st.text_area("Or Paste Resume Text Here", height=200)

        if manual_text:
            resume_text = manual_text

        all_skills = [
            "Python", "Java", "C", "C++", "SQL", "HTML", "CSS",
            "JavaScript", "React", "Node", "Machine Learning",
            "Data Analysis", "Deep Learning", "NLP", "TensorFlow",
            "Cybersecurity", "AWS", "Docker", "Git", "Linux",
            "Communication", "Leadership", "Networking",
            "Kotlin", "Firebase"
        ]

        role_skills = {
            "Data Scientist": ["Python", "SQL", "Machine Learning", "Data Analysis"],
            "Web Developer": ["HTML", "CSS", "JavaScript", "React"],
            "Java Developer": ["Java", "SQL", "Git"],
            "Cyber Security Analyst": ["Cybersecurity", "Linux", "Networking"],
            "AI Engineer": ["Python", "Machine Learning", "Deep Learning", "NLP"],
            "DevOps Engineer": ["AWS", "Docker", "Linux", "Git"],
            "Android Developer": ["Java", "Kotlin", "Firebase"],
            "Software Engineer": ["Python", "Java", "SQL", "Git"]
        }

        if st.button("🚀 Analyze Resume"):

            if resume_text.strip() == "":
                st.warning("Please upload resume or paste resume text.")

            else:
                transformed_text = vectorizer.transform([resume_text])
                predicted_role = model.predict(transformed_text)[0]

                st.success(f"🎯 Predicted Job Role: {predicted_role}")

                detected_skills = []

                for skill in all_skills:
                    if skill.lower() in resume_text.lower():
                        detected_skills.append(skill)

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Detected Skills", len(detected_skills))

                with col2:
                    st.metric("Predicted Role", predicted_role)

                with col3:
                    word_count = len(resume_text.split())
                    st.metric("Resume Words", word_count)

                st.subheader("✅ Detected Skills")

                if detected_skills:
                    st.write(", ".join(detected_skills))
                else:
                    st.write("No major skills detected.")

                required_skills = role_skills.get(predicted_role, [])
                missing_skills = []

                for skill in required_skills:
                    if skill.lower() not in resume_text.lower():
                        missing_skills.append(skill)

                matched_count = len(required_skills) - len(missing_skills)

                if required_skills:
                    skill_match = int((matched_count / len(required_skills)) * 100)
                else:
                    skill_match = 50

                ats_score = 0

                if word_count >= 50:
                    ats_score += 20
                if word_count >= 100:
                    ats_score += 20
                if len(detected_skills) >= 3:
                    ats_score += 20
                if len(detected_skills) >= 6:
                    ats_score += 20
                if "project" in resume_text.lower() or "projects" in resume_text.lower():
                    ats_score += 10
                if "internship" in resume_text.lower() or "experience" in resume_text.lower():
                    ats_score += 10

                save_history(
                    st.session_state.username,
                    predicted_role,
                    ats_score,
                    skill_match,
                    ", ".join(detected_skills)
                )

                st.success("Analysis saved to history.")

                st.subheader("📊 ATS Resume Score")
                st.progress(ats_score)
                st.write(f"ATS Score: {ats_score}/100")

                st.subheader("🎯 Skill Match Percentage")
                st.progress(skill_match)
                st.write(f"Skill Match for {predicted_role}: {skill_match}%")

                st.subheader("❌ Missing Skills")

                if missing_skills:
                    for skill in missing_skills:
                        st.write(f"Add this skill: {skill}")
                else:
                    st.write("Great! You have the required skills for this role.")

                st.subheader("📈 Skills Chart")

                labels = ["Matched Skills", "Missing Skills"]
                values = [matched_count, len(missing_skills)]

                fig, ax = plt.subplots(figsize=(3, 3))
                ax.pie(values, labels=labels, autopct="%1.1f%%", textprops={"fontsize": 8})
                ax.set_title("Skill Match Analysis", fontsize=10)
                st.pyplot(fig, use_container_width=False)

                st.subheader("💼 Internship / Job Improvement Suggestions")

                if ats_score < 60:
                    st.write("1. Add more technical skills related to your target job role.")
                    st.write("2. Add academic projects with technologies used.")
                    st.write("3. Add internship, certification, or training details.")
                    st.write("4. Include GitHub, LinkedIn, and portfolio links.")
                else:
                    st.write("Your resume looks strong. Add measurable achievements and real-world projects.")

                st.subheader("🛣️ Career Roadmap")

                if predicted_role == "Data Scientist":
                    st.write("Python → SQL → Statistics → Machine Learning → Projects → Internship")
                elif predicted_role == "Web Developer":
                    st.write("HTML → CSS → JavaScript → React → Backend → Portfolio Projects")
                elif predicted_role == "Java Developer":
                    st.write("Core Java → JDBC → Spring Boot → MySQL → Projects")
                elif predicted_role == "Cyber Security Analyst":
                    st.write("Networking → Linux → Cybersecurity → Tools → Certifications")
                elif predicted_role == "AI Engineer":
                    st.write("Python → ML → Deep Learning → NLP → AI Projects")
                else:
                    st.write("Build strong programming skills, projects, and internship experience.")

                pdf_report = create_pdf_report(
                    predicted_role,
                    detected_skills,
                    missing_skills,
                    ats_score,
                    skill_match
                )

                st.download_button(
                    label="📥 Download Resume Analysis Report",
                    data=pdf_report,
                    file_name="resume_analysis_report.pdf",
                    mime="application/pdf"
                )

# ---------------- RUN APP ----------------
if st.session_state.logged_in:
    resume_analyzer_app()
else:
    login_page()