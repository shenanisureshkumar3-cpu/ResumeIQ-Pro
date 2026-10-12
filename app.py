
import html
import re
from datetime import datetime
from io import BytesIO

import streamlit as st
import plotly.graph_objects as go

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)

from analyzer import extract_resume_text, analyze_resume


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="ResumeIQ Pro | Resume Intelligence",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =====================================================
# PROFESSIONAL LIGHT THEME
# =====================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    color-scheme: light;
    --primary: #7062DF;
    --primary-light: #F0EEFF;
    --background: #F7F8FC;
    --surface: #FFFFFF;
    --text: #111111;
    --muted: #50566B;
    --border: #E5E8F1;
}

html, body, .stApp {
    font-family: 'Inter', sans-serif !important;
    color: #111111 !important;
}

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: #F7F8FC !important;
    color: #111111 !important;
}

.block-container {
    max-width: 1240px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* TEXT */

[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3,
[data-testid="stMain"] h4,
[data-testid="stMain"] p,
[data-testid="stMain"] label,
[data-testid="stMain"] li {
    color: #111111 !important;
}

[data-testid="stMain"] h1 {
    font-size: 31px;
    font-weight: 800;
    letter-spacing: -1px;
}

[data-testid="stMain"] h2,
[data-testid="stMain"] h3 {
    font-weight: 700;
}

[data-testid="stMain"]
[data-testid="stCaptionContainer"] p {
    color: #50566B !important;
}

[data-testid="stMain"]
[data-testid="stWidgetLabel"] p {
    color: #222222 !important;
    font-weight: 600;
}

/* SIDEBAR */

[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E5E8F1 !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {
    color: #111111 !important;
}

.brand {
    padding: 18px 8px 24px;
    border-bottom: 1px solid #E9EAF3;
    margin-bottom: 22px;
}

.brand-title {
    color: #7062DF;
    font-size: 27px;
    font-weight: 800;
    letter-spacing: -1px;
}

.brand-subtitle {
    color: #555B70;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.4px;
    margin-top: 5px;
}

.sidebar-label {
    font-size: 11px;
    font-weight: 800;
    color: #555B70;
    letter-spacing: 1.4px;
    margin: 16px 8px 12px;
}

[data-testid="stSidebar"]
div[role="radiogroup"] {
    gap: 7px;
}

[data-testid="stSidebar"]
div[role="radiogroup"] label {
    border-radius: 11px;
    padding: 10px 12px;
}

[data-testid="stSidebar"]
div[role="radiogroup"] label:hover {
    background: #F6F4FF;
}

[data-testid="stSidebar"]
div[role="radiogroup"]
label:has(input:checked) {
    background: #EFEDFF !important;
    border-left: 3px solid #7062DF;
}

[data-testid="stSidebar"]
div[role="radiogroup"]
label:has(input:checked) p {
    color: #4936C3 !important;
    font-weight: 800;
}

.sidebar-note {
    background: #F3F1FF;
    border: 1px solid #E5DFFF;
    padding: 17px;
    border-radius: 15px;
    margin-top: 22px;
}

.sidebar-note-title {
    color: #5141C5;
    font-size: 13px;
    font-weight: 800;
}

.sidebar-note-text {
    color: #4D5268;
    font-size: 12px;
    line-height: 1.7;
    margin-top: 7px;
}

/* BUTTONS */

.stButton > button[kind="primary"] {
    background: #7062DF !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 11px !important;
    min-height: 46px;
    font-weight: 700;
}

.stButton > button[kind="primary"]:hover {
    background: #5B4BC9 !important;
}

.stButton > button[kind="secondary"],
.stDownloadButton > button {
    background: #FFFFFF !important;
    color: #25213C !important;
    border: 1px solid #DDE0EC !important;
    border-radius: 11px !important;
    min-height: 43px;
    font-weight: 600;
}

.stButton button p,
.stDownloadButton button p {
    color: inherit !important;
}

[data-testid="stMain"]
.stButton > button[kind="primary"] p {
    color: #FFFFFF !important;
}

/* DASHBOARD HERO */

.hero {
    background: linear-gradient(
        110deg,
        #7062DF 0%,
        #8795E9 100%
    );
    padding: 39px;
    border-radius: 20px;
    margin: 10px 0 26px;
}

.hero-kicker {
    color: #FFFFFF;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.4px;
    margin-bottom: 12px;
}

.hero-heading {
    color: #FFFFFF;
    font-size: 35px;
    font-weight: 800;
    line-height: 1.25;
    letter-spacing: -1px;
}

.hero-description {
    color: #FFFFFF;
    font-size: 14px;
    line-height: 1.85;
    margin-top: 12px;
    max-width: 620px;
}

/* CARDS */

.feature-card {
    background: #FFFFFF;
    border: 1px solid #E5E8F1;
    border-radius: 16px;
    padding: 23px;
    min-height: 178px;
    box-shadow: 0 4px 15px rgba(45,55,100,.025);
}

.feature-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 46px;
    height: 46px;
    border-radius: 12px;
    font-size: 23px;
    margin-bottom: 15px;
}

.feature-title {
    color: #111111;
    font-size: 15px;
    font-weight: 800;
    margin-bottom: 8px;
}

.feature-description {
    color: #50566B;
    font-size: 12px;
    line-height: 1.75;
}

/* METRIC CARDS */

[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E5E8F1;
    border-radius: 16px;
    padding: 20px;
}

[data-testid="stMetricLabel"] p {
    color: #50566B !important;
}

[data-testid="stMetricValue"] {
    color: #111111 !important;
    font-weight: 800;
}

/* INPUTS */

[data-testid="stMain"] input,
[data-testid="stMain"] textarea {
    background: #FFFFFF !important;
    color: #111111 !important;
}

[data-testid="stMain"]
[data-baseweb="select"] > div {
    background: #FFFFFF !important;
    color: #111111 !important;
}

[data-testid="stFileUploader"] {
    background: #FFFFFF;
    border: 1px solid #E5E8F1;
    border-radius: 15px;
    padding: 12px;
}

[data-testid="stFileUploaderDropzone"] {
    background: #F8F7FF;
    border: 1px dashed #C6BFFF;
    border-radius: 12px;
}

/* SKILL LABELS */

.skill {
    display: inline-block;
    background: #EEEBFF;
    color: #4334B8;
    font-size: 12px;
    font-weight: 700;
    padding: 8px 12px;
    margin: 4px;
    border-radius: 9px;
}

.skill.missing {
    background: #FFF1E4;
    color: #8B521F;
}

/* SECTION INTRO */

.page-intro {
    color: #50566B;
    font-size: 14px;
    line-height: 1.8;
    margin: 7px 0 25px;
}

/* FOOTER */

.footer {
    margin-top: 35px;
    border-top: 1px solid #E5E8F1;
    padding: 22px 0;
    text-align: center;
    color: #50566B;
    font-size: 12px;
}

/* MOBILE */

@media (max-width: 700px) {
    .hero {
        padding: 25px;
    }

    .hero-heading {
        font-size: 27px;
    }

    .block-container {
        padding-top: 1rem;
    }
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# JOB DESCRIPTION TEMPLATES
# =====================================================

JOB_TEMPLATES = {
    "Data Analyst": (
        "Junior Data Analyst. Required skills: Python, SQL, "
        "Excel, Power BI, Pandas, NumPy, data analysis, "
        "data visualization, communication and problem solving."
    ),
    "Software Developer": (
        "Junior Software Developer. Required skills: Python, "
        "JavaScript, HTML, CSS, SQL, Git, GitHub and API."
    ),
    "UI/UX Designer": (
        "Junior UI/UX Designer. Required skills: UI/UX, "
        "Figma, communication, HTML and CSS."
    ),
    "QA Engineer": (
        "Junior QA Engineer. Required skills: software testing, "
        "manual testing, automation testing, SQL, "
        "communication and problem solving."
    ),
    "AI Engineer": (
        "Junior AI Engineer. Required skills: Python, "
        "machine learning, artificial intelligence, "
        "Pandas, NumPy, scikit-learn and TensorFlow."
    ),
    "Business Analyst": (
        "Junior Business Analyst. Required skills: "
        "business analysis, Excel, SQL, Power BI, "
        "communication and project management."
    )
}


DEMO_RESUME = """
Jordan Lee
Email: jordan@example.com

Professional Summary
Computing graduate interested in data analytics
and software quality assurance.

Education
Higher National Diploma in Computing.

Work Experience
Quality Assurance Intern.
Performed manual testing and software testing.

Skills
Python, SQL, Excel, Power BI, Pandas,
Git, GitHub, HTML, CSS, communication
and problem solving.

Projects
Created a Power BI dashboard and
a Python data analysis application.
"""


SECTIONS = {
    "Contact information": r"email|phone|linkedin",
    "Professional summary": r"summary|profile|objective",
    "Work experience": r"experience|employment|internship",
    "Education": r"education|qualification|university",
    "Skills": r"skills|technologies",
    "Projects": r"projects|portfolio"
}


# =====================================================
# SESSION STATE
# =====================================================

PAGES = [
    "Dashboard",
    "Resume Analyzer",
    "Skill Intelligence",
    "Resume Health",
    "Recommendations",
    "Reports & History"
]

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "history" not in st.session_state:
    st.session_state.history = []

if "current_id" not in st.session_state:
    st.session_state.current_id = None

if "resume_source" not in st.session_state:
    st.session_state.resume_source = "Upload resume"

if "template" not in st.session_state:
    st.session_state.template = "Data Analyst"

if "job_description" not in st.session_state:
    st.session_state.job_description = ""


def navigate(page):
    st.session_state.page = page


def demo_mode():
    st.session_state.resume_source = "Try demo"
    st.session_state.template = "Data Analyst"
    st.session_state.job_description = JOB_TEMPLATES["Data Analyst"]
    navigate("Resume Analyzer")


def apply_template():
    st.session_state.job_description = (
        JOB_TEMPLATES[st.session_state.template]
    )


def current_record():
    return next(
        (
            record
            for record in st.session_state.history
            if record["id"] == st.session_state.current_id
        ),
        None
    )


def select_record(record_id):
    st.session_state.current_id = record_id
    navigate("Skill Intelligence")


def clear_history():
    st.session_state.history = []
    st.session_state.current_id = None


# =====================================================
# ANALYSIS FUNCTIONS
# =====================================================

def normalize_score(value):
    try:
        return max(0, min(100, float(value)))
    except (TypeError, ValueError):
        return 0.0


def prepare_result(raw, resume_text):
    result = dict(raw)

    for key in [
        "resume_skills",
        "job_skills",
        "matched_skills",
        "missing_skills"
    ]:
        result[key] = sorted(
            set(result.get(key) or [])
        )

    result["similarity"] = normalize_score(
        result.get("similarity")
    )

    coverage = result.get("skill_coverage")

    if coverage is None:
        total = len(result["job_skills"])
        coverage = (
            len(result["matched_skills"]) / total * 100
            if total else 0
        )

    result["skill_coverage"] = normalize_score(coverage)

    detected_sections = {
        name: bool(re.search(pattern, resume_text, re.I))
        for name, pattern in SECTIONS.items()
    }

    result["sections"] = detected_sections

    result["health"] = round(
        sum(detected_sections.values())
        / len(detected_sections) * 100,
        1
    )

    recommendations = []

    if result["missing_skills"]:
        recommendations.append(
            "Review the following job skills: "
            + ", ".join(result["missing_skills"][:6])
            + ". Add them to your resume only if you "
            "genuinely have those skills."
        )

    for name, found in detected_sections.items():
        if not found:
            recommendations.append(
                f"Review your {name.lower()} section. "
                "The checker could not recognize it."
            )

    if len(resume_text.split()) < 180:
        recommendations.append(
            "Consider including more relevant projects, "
            "experience and measurable achievements."
        )

    if not recommendations:
        recommendations.append(
            "Your basic checks look good. "
            "Review formatting, spelling and achievements."
        )

    result["recommendations"] = recommendations

    return result


def show_metrics(result):
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Skill Coverage",
        f"{result['skill_coverage']:.1f}%"
    )

    col2.metric(
        "Text Similarity",
        f"{result['similarity']:.1f}%"
    )

    col3.metric(
        "Resume Health",
        f"{result['health']:.1f}%"
    )


def show_skills(skills, missing=False):
    if not skills:
        st.caption("No skills detected.")
        return

    css_class = "skill missing" if missing else "skill"

    markup = "".join(
        f'<span class="{css_class}">'
        f'{html.escape(str(skill).title())}'
        '</span>'
        for skill in skills
    )

    st.markdown(markup, unsafe_allow_html=True)


def show_skill_chart(result):
    matched = len(result["matched_skills"])
    missing = len(result["missing_skills"])

    if matched + missing == 0:
        st.info("No recognized job skills available to chart.")
        return

    fig = go.Figure(
        go.Pie(
            labels=["Matched Skills", "Potential Gaps"],
            values=[matched, missing],
            hole=0.68,
            marker_colors=["#7062DF", "#54B8AA"]
        )
    )

    fig.update_layout(
        height=350,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter",
            color="#111111"
        ),
        margin=dict(l=10, r=10, t=15, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)


def show_health_chart(sections):
    labels = list(sections)
    values = [int(sections[name]) for name in labels]

    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker_color=[
                "#54B8AA" if value else "#E8A65A"
                for value in values
            ]
        )
    )

    fig.update_layout(
        height=350,
        xaxis=dict(range=[0, 1.1], visible=False),
        yaxis=dict(
            autorange="reversed",
            automargin=True
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter",
            color="#111111"
        ),
        margin=dict(l=10, r=20, t=10, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)


# =====================================================
# PDF REPORT GENERATOR
# =====================================================

def create_pdf(record):
    result = record["result"]

    output = BytesIO()

    doc = SimpleDocTemplate(
        output,
        leftMargin=45,
        rightMargin=45
    )

    styles = getSampleStyleSheet()

    def paragraph(text, style="BodyText"):
        return Paragraph(
            html.escape(str(text)),
            styles[style]
        )

    story = [
        paragraph("ResumeIQ Pro - Analysis Report", "Title"),
        Spacer(1, 15),
        paragraph("Resume: " + record["filename"]),
        paragraph("Target Role: " + record["role"]),
        paragraph("Date: " + record["date"]),
        Spacer(1, 15)
    ]

    table = Table([
        ["Metric", "Result"],
        ["Skill Coverage", f"{result['skill_coverage']:.1f}%"],
        ["Text Similarity", f"{result['similarity']:.1f}%"],
        ["Resume Health", f"{result['health']:.1f}%"]
    ])

    table.setStyle(TableStyle([
        (
            "BACKGROUND", (0, 0), (-1, 0),
            colors.HexColor("#EEEBFF")
        ),
        (
            "GRID", (0, 0), (-1, -1),
            0.5, colors.HexColor("#E5E8F1")
        ),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9)
    ]))

    story.append(table)

    groups = [
        ("Matched Skills", result["matched_skills"]),
        ("Potential Skill Gaps", result["missing_skills"]),
        ("Recommendations", result["recommendations"])
    ]

    for heading, items in groups:
        story.append(Spacer(1, 18))
        story.append(paragraph(heading, "Heading2"))

        for item in items or ["None detected"]:
            story.append(paragraph("- " + str(item)))

    story.append(Spacer(1, 20))

    story.append(paragraph(
        "Results are approximate text and keyword comparisons, "
        "not an official ATS score or hiring prediction."
    ))

    doc.build(story)

    return output.getvalue()


# =====================================================
# SIDEBAR NAVIGATION
# =====================================================

with st.sidebar:

    st.markdown(
        '<div class="brand">'
        '<div class="brand-title">✦ resumeiq.</div>'
        '<div class="brand-subtitle">'
        'CAREER INTELLIGENCE PLATFORM'
        '</div></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-label">WORKSPACE</div>',
        unsafe_allow_html=True
    )

    st.radio(
        "Navigation",
        PAGES,
        key="page",
        label_visibility="collapsed"
    )

    st.markdown(
        '<div class="sidebar-label">QUICK ACCESS</div>',
        unsafe_allow_html=True
    )

    st.button(
        "✨ Try Demo Analysis",
        on_click=demo_mode,
        use_container_width=True,
        type="primary"
    )

    st.markdown(
        '<div class="sidebar-note">'
        '<div class="sidebar-note-title">'
        'Career growth made simple'
        '</div>'
        '<div class="sidebar-note-text">'
        'Analyze your resume, understand your skills '
        'and prepare for your next opportunity.'
        '</div></div>',
        unsafe_allow_html=True
    )

    st.caption("ResumeIQ Pro 2.0")


# =====================================================
# DASHBOARD
# =====================================================

if st.session_state.page == "Dashboard":

    st.markdown(
        '<div class="hero">'
        '<div class="hero-kicker">'
        'WELCOME TO RESUMEIQ PRO'
        '</div>'
        '<div class="hero-heading">'
        'Build a stronger resume.'
        '</div>'
        '<div class="hero-description">'
        'Analyze your CV, identify relevant skills '
        'and discover practical ways to prepare '
        'for your next career opportunity.'
        '</div></div>',
        unsafe_allow_html=True
    )

    st.subheader("Your Career Workspace")

    st.caption(
        "Everything you need to understand and improve your resume."
    )

    features = [
        (
            "📄", "#F0EEFF",
            "Resume Analyzer",
            "Compare your resume with a job description."
        ),
        (
            "📊", "#EAF5FC",
            "Skill Intelligence",
            "Explore matched skills and potential gaps."
        ),
        (
            "💚", "#EAF8F4",
            "Resume Health",
            "Check your resume's structure and sections."
        ),
        (
            "💡", "#FFF5E9",
            "Recommendations",
            "Discover practical ways to improve your CV."
        )
    ]

    columns = st.columns(4)

    for column, (icon, background, title, description) in zip(
        columns, features
    ):
        with column:
            st.markdown(
                '<div class="feature-card">'
                f'<div class="feature-icon" '
                f'style="background:{background}">'
                f'{icon}</div>'
                f'<div class="feature-title">{title}</div>'
                f'<div class="feature-description">'
                f'{description}</div>'
                '</div>',
                unsafe_allow_html=True
            )

    st.write("")

    left, right = st.columns(2)

    with left:
        st.button(
            "Start Resume Analysis →",
            type="primary",
            use_container_width=True,
            on_click=navigate,
            args=("Resume Analyzer",)
        )

    with right:
        st.button(
            "Try Demo Resume",
            use_container_width=True,
            on_click=demo_mode
        )

    st.divider()

    st.subheader("Recent Activity")

    if st.session_state.history:
        show_metrics(
            st.session_state.history[0]["result"]
        )
    else:
        st.info(
            "You haven't analyzed a resume yet. "
            "Start your first analysis to see results here."
        )


# =====================================================
# RESUME ANALYZER
# =====================================================

elif st.session_state.page == "Resume Analyzer":

    st.title("Resume Analyzer")

    st.markdown(
        '<div class="page-intro">'
        'Upload your resume and compare it with '
        'a job description to understand your skills.'
        '</div>',
        unsafe_allow_html=True
    )

    st.subheader("Step 1 — Choose Your Resume")

    st.radio(
        "Resume source",
        ["Upload resume", "Try demo"],
        key="resume_source",
        horizontal=True
    )

    uploaded_file = None

    if st.session_state.resume_source == "Upload resume":

        uploaded_file = st.file_uploader(
            "Upload a PDF or DOCX resume",
            type=["pdf", "docx"]
        )

        if uploaded_file:
            st.success(
                f"Selected file: {uploaded_file.name}"
            )

    else:
        st.info(
            "Demo mode uses a fictional resume for testing."
        )

        with st.expander("View Demo Resume"):
            st.text(DEMO_RESUME)

    st.divider()

    st.subheader("Step 2 — Select Your Target Role")

    col1, col2 = st.columns([3, 1])

    with col1:
        st.selectbox(
            "Choose a job template",
            list(JOB_TEMPLATES),
            key="template"
        )

    with col2:
        st.write("")
        st.write("")

        st.button(
            "Use Template",
            on_click=apply_template,
            use_container_width=True
        )

    job_description = st.text_area(
        "Job Description",
        key="job_description",
        height=200,
        placeholder="Paste the job description here..."
    )

    st.divider()

    st.subheader("Step 3 — Analyze")

    if st.button(
        "Analyze My Resume →",
        type="primary",
        use_container_width=True
    ):

        if not job_description.strip():
            st.warning(
                "Please enter a job description first."
            )

        elif (
            st.session_state.resume_source == "Upload resume"
            and uploaded_file is None
        ):
            st.warning(
                "Please upload your resume first."
            )

        else:
            try:
                with st.spinner("Analyzing your resume..."):

                    if st.session_state.resume_source == "Try demo":
                        resume_text = DEMO_RESUME
                        filename = "Demo Resume"

                    else:
                        if uploaded_file.size > 10 * 1024 * 1024:
                            raise ValueError(
                                "The maximum upload size is 10 MB."
                            )

                        resume_text = extract_resume_text(
                            uploaded_file
                        )

                        filename = uploaded_file.name

                    if not resume_text.strip():
                        raise ValueError(
                            "No readable text found in the resume."
                        )

                    raw = analyze_resume(
                        resume_text,
                        job_description
                    )

                    result = prepare_result(
                        raw,
                        resume_text
                    )

                    role = next(
                        (
                            line.strip()[:80]
                            for line in job_description.splitlines()
                            if line.strip()
                        ),
                        "Custom Job"
                    )

                    record = {
                        "id": datetime.now().strftime(
                            "%Y%m%d%H%M%S%f"
                        ),
                        "date": datetime.now().strftime(
                            "%d %b %Y, %H:%M"
                        ),
                        "filename": filename,
                        "role": role,
                        "result": result
                    }

                    st.session_state.history.insert(
                        0, record
                    )

                    st.session_state.history = (
                        st.session_state.history[:8]
                    )

                    st.session_state.current_id = (
                        record["id"]
                    )

                st.success(
                    "Your resume analysis is complete!"
                )

            except Exception as error:
                st.error(
                    "Unable to complete the analysis."
                )

                with st.expander("Technical details"):
                    st.code(str(error))

    record = current_record()

    if record:

        st.subheader("Your Analysis Results")

        show_metrics(record["result"])

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Matched Skills")
            show_skills(
                record["result"]["matched_skills"]
            )

        with col2:
            st.markdown("#### Potential Skill Gaps")
            show_skills(
                record["result"]["missing_skills"],
                missing=True
            )

        st.write("")

        st.button(
            "Explore Skill Intelligence →",
            on_click=navigate,
            args=("Skill Intelligence",),
            use_container_width=True
        )

        st.caption(
            "Scores are approximate comparisons, "
            "not official ATS scores."
        )


# =====================================================
# SKILL INTELLIGENCE
# =====================================================

elif st.session_state.page == "Skill Intelligence":

    st.title("Skill Intelligence")

    st.markdown(
        '<div class="page-intro">'
        'Understand how your recognized skills '
        'compare with your target role.'
        '</div>',
        unsafe_allow_html=True
    )

    record = current_record()

    if not record:
        st.info(
            "Analyze a resume first to see your skill insights."
        )

        st.button(
            "Go to Resume Analyzer",
            on_click=navigate,
            args=("Resume Analyzer",)
        )

    else:
        result = record["result"]

        show_metrics(result)

        st.subheader("Skill Match Overview")

        show_skill_chart(result)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Matched Skills")
            show_skills(result["matched_skills"])

        with col2:
            st.subheader("Skills to Explore")
            show_skills(
                result["missing_skills"],
                missing=True
            )

        st.info(
            "Only include skills on your resume "
            "that accurately reflect your experience."
        )


# =====================================================
# RESUME HEALTH
# =====================================================

elif st.session_state.page == "Resume Health":

    st.title("Resume Health")

    st.markdown(
        '<div class="page-intro">'
        'Check whether important resume sections '
        'are recognized.'
        '</div>',
        unsafe_allow_html=True
    )

    record = current_record()

    if not record:
        st.info(
            "Analyze a resume first to check its structure."
        )

    else:
        result = record["result"]

        col1, col2 = st.columns(2)

        col1.metric(
            "Resume Health",
            f"{result['health']:.1f}%"
        )

        col2.metric(
            "Sections Detected",
            f"{sum(result['sections'].values())}"
            f" / {len(result['sections'])}"
        )

        st.subheader("Resume Section Overview")

        show_health_chart(result["sections"])

        st.subheader("Section Checklist")

        for section, found in result["sections"].items():

            with st.container(border=True):

                col1, col2 = st.columns([3, 1])

                col1.markdown(f"**{section}**")

                if found:
                    col2.success("Detected")
                else:
                    col2.warning("Review")

        st.caption(
            "This check uses text patterns. "
            "Some existing sections may not be recognized."
        )


# =====================================================
# RECOMMENDATIONS
# =====================================================

elif st.session_state.page == "Recommendations":

    st.title("Career Recommendations")

    st.markdown(
        '<div class="page-intro">'
        'Practical suggestions to help you '
        'improve your resume.'
        '</div>',
        unsafe_allow_html=True
    )

    record = current_record()

    if not record:
        st.info(
            "Analyze a resume first to get recommendations."
        )

    else:
        st.subheader("Your Improvement Checklist")

        for index, recommendation in enumerate(
            record["result"]["recommendations"],
            start=1
        ):

            with st.container(border=True):

                st.checkbox(
                    recommendation,
                    key=f"recommendation_{record['id']}_{index}"
                )

        st.divider()

        st.subheader("Recommended Next Steps")

        st.write(
            "**1.** Review the skills required by your target job."
        )

        st.write(
            "**2.** Highlight relevant experience and projects."
        )

        st.write(
            "**3.** Improve the structure and readability of your CV."
        )

        st.write(
            "**4.** Run another analysis after updating your resume."
        )


# =====================================================
# REPORTS AND HISTORY
# =====================================================

elif st.session_state.page == "Reports & History":

    st.title("Reports & History")

    st.markdown(
        '<div class="page-intro">'
        'Review your recent analyses and '
        'download professional PDF reports.'
        '</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.history:

        st.info(
            "No reports yet. Analyze a resume to create one."
        )

    else:
        st.caption(
            "Up to eight analyses are kept "
            "in your current session."
        )

        for index, record in enumerate(
            st.session_state.history
        ):

            with st.container(border=True):

                st.markdown(
                    "### " + html.escape(record["role"])
                )

                st.caption(
                    record["filename"]
                    + " • "
                    + record["date"]
                )

                show_metrics(record["result"])

                col1, col2 = st.columns(2)

                with col1:
                    st.button(
                        "View Analysis",
                        key=f"view_{record['id']}",
                        on_click=select_record,
                        args=(record["id"],),
                        use_container_width=True
                    )

                with col2:
                    st.download_button(
                        "Download PDF",
                        data=create_pdf(record),
                        file_name=(
                            f"ResumeIQ_Report_{index + 1}.pdf"
                        ),
                        mime="application/pdf",
                        key=f"pdf_{record['id']}",
                        use_container_width=True
                    )

        st.divider()

        st.button(
            "Clear History",
            on_click=clear_history
        )


# =====================================================
# FOOTER
# =====================================================

st.markdown(
    '<div class="footer">'
    'ResumeIQ Pro 2.0 · Professional Resume Intelligence'
    '<div style="margin-top:6px">'
    'Built with Python, Streamlit and scikit-learn'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)

with st.expander("About ResumeIQ & Privacy"):

    st.write(
        "ResumeIQ compares resume text with job descriptions "
        "using skill detection and text similarity."
    )

    st.write(
        "It does not provide an official ATS score "
        "or predict hiring decisions."
    )

    st.write(
        "Your analysis history is stored temporarily "
        "in the current Streamlit session, "
        "not in a permanent database."
    )

    st.write(
        "Avoid uploading sensitive information "
        "you do not want processed by the hosting service."
    )
