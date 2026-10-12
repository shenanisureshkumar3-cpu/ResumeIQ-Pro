
import html
import re
from datetime import datetime
from io import BytesIO

import plotly.graph_objects as go
import streamlit as st

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from analyzer import extract_resume_text, analyze_resume


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ResumeIQ Pro | Career Intelligence",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# PAGES
# ============================================================

PAGES = {
    "◈  Dashboard": "Dashboard",
    "▣  Resume Analyzer": "Resume Analyzer",
    "◉  Skill Intelligence": "Skill Intelligence",
    "✚  Resume Health": "Resume Health",
    "✦  Recommendations": "Recommendations",
    "▤  Reports & History": "Reports & History",
}


# ============================================================
# JOB TEMPLATES
# ============================================================

JOB_TEMPLATES = {
    "Data Analyst": (
        "Junior Data Analyst\n"
        "Required skills: Python, SQL, Excel, Power BI, "
        "Pandas, NumPy, data analysis, data visualization, "
        "communication and problem solving."
    ),
    "Software Developer": (
        "Junior Software Developer\n"
        "Required skills: Python, JavaScript, HTML, CSS, "
        "SQL, Git, GitHub, APIs and problem solving."
    ),
    "UI/UX Designer": (
        "Junior UI/UX Designer\n"
        "Required skills: UI/UX, Figma, wireframing, "
        "prototyping, user research and communication."
    ),
    "QA Engineer": (
        "Junior QA Engineer\n"
        "Required skills: software testing, manual testing, "
        "regression testing, user acceptance testing, "
        "SQL and communication."
    ),
    "AI Engineer": (
        "Junior AI Engineer\n"
        "Required skills: Python, machine learning, "
        "artificial intelligence, Pandas, NumPy, "
        "scikit-learn, TensorFlow and data analysis."
    ),
    "Business Analyst": (
        "Junior Business Analyst\n"
        "Required skills: business analysis, Excel, SQL, "
        "Power BI, communication, problem solving "
        "and project management."
    ),
}


DEMO_RESUME = """
Jordan Lee
Email: jordan@example.com

Professional Summary
Computing graduate interested in data analytics.

Education
Higher National Diploma in Computing.

Work Experience
Quality Assurance Intern.
Performed manual testing, regression testing
and user acceptance testing.

Technical Skills
Python, SQL, Excel, Power BI, Pandas, NumPy,
HTML, CSS, Git, GitHub, communication
and problem solving.

Projects
Created a Power BI dashboard and
a Python data analysis application.
"""


SECTION_PATTERNS = {
    "Contact": r"\b(email|phone|contact|linkedin)\b",
    "Summary": r"\b(summary|profile|objective)\b",
    "Experience": r"\b(experience|employment|internship)\b",
    "Education": r"\b(education|qualifications?|university)\b",
    "Skills": r"\b(skills|technologies)\b",
    "Projects": r"\b(projects|portfolio)\b",
}


# ============================================================
# PREMIUM DESIGN
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* GENERAL */

:root {
    color-scheme: light;
}

html, body {
    font-family: 'DM Sans', sans-serif;
}

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: #F7F8FE !important;
    color: #252746 !important;
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* MAIN PAGE TEXT FIX */

[data-testid="stMain"] {
    color: #252746 !important;
}

[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3,
[data-testid="stMain"] h4 {
    color: #252746 !important;
    font-family: 'Plus Jakarta Sans', sans-serif;
}

[data-testid="stMain"] p,
[data-testid="stMain"] label,
[data-testid="stMain"] li {
    color: #252746;
}

[data-testid="stMain"]
[data-testid="stCaptionContainer"] p {
    color: #6B728B !important;
}

[data-testid="stMain"]
[data-testid="stWidgetLabel"] p {
    color: #6B728B !important;
}

[data-testid="stMain"] input,
[data-testid="stMain"] textarea {
    background: #FFFFFF !important;
    color: #252746 !important;
}

[data-testid="stMain"]
[data-baseweb="select"] > div {
    background: #FFFFFF !important;
    color: #252746 !important;
}

/* BUTTONS */

.stButton > button[kind="primary"] {
    background: linear-gradient(
        100deg,
        #705CF6,
        #4187F5
    ) !important;
    color: #FFFFFF !important;
    border: none;
    border-radius: 12px;
    min-height: 48px;
    font-weight: 700;
}

.stButton > button[kind="secondary"],
.stDownloadButton > button {
    background: #FFFFFF;
    color: #494D70 !important;
    border: 1px solid #E1E3F2;
    border-radius: 11px;
    min-height: 43px;
    font-weight: 600;
}

/* METRICS */

[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E8EAF5;
    border-radius: 17px;
    padding: 20px;
}

[data-testid="stMetricLabel"] p {
    color: #737B96 !important;
}

[data-testid="stMetricValue"] {
    color: #252746 !important;
    font-weight: 800;
}

/* FILE UPLOADER */

[data-testid="stFileUploader"] {
    background: #FFFFFF;
    border: 1px solid #E8EAF5;
    border-radius: 15px;
    padding: 12px;
}

[data-testid="stFileUploaderDropzone"] {
    background: #FAF9FF;
    border: 1px dashed #BFB8FC;
    border-radius: 12px;
}

/* SIDEBAR */

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #151B38,
        #1C2348 60%,
        #202751
    ) !important;
    border-right: 1px solid #30375E !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {
    color: #DCE1F8;
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 4px 25px;
    border-bottom: 1px solid #343B60;
    margin-bottom: 14px;
}

.sidebar-logo {
    width: 45px;
    height: 45px;
    display: flex;
    justify-content: center;
    align-items: center;
    background: linear-gradient(
        135deg,
        #8876FF,
        #5D6EEC
    );
    border-radius: 13px;
    color: #FFFFFF;
    font-size: 25px;
}

.sidebar-name {
    color: #FFFFFF;
    font-size: 22px;
    font-weight: 800;
    letter-spacing: -1px;
}

.sidebar-name span {
    color: #A393FF;
}

.sidebar-subtitle {
    color: #9FA9D0;
    font-size: 9px;
    font-weight: 800;
    letter-spacing: 1.3px;
}

.sidebar-section {
    color: #929FC7;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.7px;
    margin: 23px 0 12px 9px;
}

[data-testid="stSidebar"]
div[role="radiogroup"] {
    gap: 7px;
}

[data-testid="stSidebar"]
div[role="radiogroup"] label {
    padding: 11px 12px;
    border-radius: 12px;
    transition: background .2s;
}

[data-testid="stSidebar"]
div[role="radiogroup"] label:hover {
    background: #2C355E !important;
}

[data-testid="stSidebar"]
div[role="radiogroup"]
label:has(input:checked) {
    background: linear-gradient(
        90deg,
        #5145A4,
        #3B427A
    ) !important;
    border-left: 3px solid #A79BFF;
}

[data-testid="stSidebar"]
div[role="radiogroup"] label p {
    color: #DCE1F8 !important;
    font-size: 13px;
    font-weight: 600;
}

[data-testid="stSidebar"]
div[role="radiogroup"]
label:has(input:checked) p {
    color: #FFFFFF !important;
    font-weight: 800;
}

[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(
        100deg,
        #7865FA,
        #557DF4
    ) !important;
    color: #FFFFFF !important;
    border: none;
    border-radius: 12px;
    min-height: 47px;
    font-weight: 700;
}

.sidebar-help {
    margin-top: 24px;
    padding: 20px 18px;
    background: linear-gradient(
        145deg,
        #34366F,
        #283359
    );
    border: 1px solid #474B84;
    border-radius: 17px;
}

.sidebar-help-title {
    color: #FFFFFF;
    font-size: 13px;
    font-weight: 800;
    margin-bottom: 8px;
}

.sidebar-help-copy {
    color: #B9C2E3;
    font-size: 12px;
    line-height: 1.75;
}

.sidebar-footer {
    margin-top: 24px;
    padding: 20px 7px;
    border-top: 1px solid #343B60;
    color: #DCE1F8;
    font-size: 12px;
}

/* DASHBOARD HERO */

.hero {
    background: linear-gradient(
        115deg,
        #6552E9,
        #617AF2 57%,
        #30A7CE
    );
    padding: 43px;
    border-radius: 23px;
    margin: 10px 0 26px;
    box-shadow: 0 15px 35px rgba(89,91,205,.15);
}

.hero-title {
    color: #FFFFFF !important;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 800;
    font-size: 42px;
    line-height: 1.2;
    margin: 13px 0;
}

.hero-kicker {
    color: #E8E7FF !important;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.7px;
}

.hero-copy {
    color: #F2F3FF !important;
    font-size: 14px;
    line-height: 1.85;
    max-width: 660px;
}

.feature {
    background: #FFFFFF;
    border: 1px solid #E8EAF5;
    border-radius: 18px;
    padding: 23px;
    min-height: 165px;
}

.feature-title {
    color: #252746;
    font-size: 15px;
    font-weight: 800;
    margin: 12px 0 7px;
}

.feature-copy {
    color: #737B96;
    font-size: 13px;
    line-height: 1.75;
}

.skill-tag {
    display: inline-block;
    background: #EEEAFE;
    color: #5948C8;
    padding: 8px 12px;
    margin: 4px;
    border-radius: 9px;
    font-size: 12px;
    font-weight: 700;
}

.skill-tag.missing {
    background: #FFF0E5;
    color: #A3622A;
}

.color-strip {
    height: 5px;
    border-radius: 10px;
    margin: 15px 0 26px;
    background: linear-gradient(
        90deg,
        #705CF6 0% 25%,
        #3478F6 25% 50%,
        #0FB99C 50% 75%,
        #F4A261 75% 90%,
        #E66DA9 90%
    );
}

@media (max-width: 700px) {
    .hero {
        padding: 27px;
    }

    .hero-title {
        font-size: 29px;
    }
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {
    "navigation": list(PAGES)[0],
    "resume_source": "Upload resume",
    "template": "Data Analyst",
    "job_description": "",
    "history": [],
    "current_id": None,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# NAVIGATION
# ============================================================

def navigate(page):
    for label, destination in PAGES.items():
        if destination == page:
            st.session_state.navigation = label
            return


def start_demo():
    st.session_state.resume_source = "Try demo"
    st.session_state.template = "Data Analyst"
    st.session_state.job_description = JOB_TEMPLATES["Data Analyst"]
    navigate("Resume Analyzer")


def use_template():
    st.session_state.job_description = (
        JOB_TEMPLATES[st.session_state.template]
    )


def open_record(record_id):
    st.session_state.current_id = record_id
    navigate("Skill Intelligence")


def clear_history():
    st.session_state.history = []
    st.session_state.current_id = None


def get_record():
    return next(
        (
            record for record in st.session_state.history
            if record["id"] == st.session_state.current_id
        ),
        None,
    )


# ============================================================
# ANALYSIS HELPERS
# ============================================================

def safe_score(value):
    try:
        return max(0.0, min(float(value), 100.0))
    except (TypeError, ValueError):
        return 0.0


def normalize_result(raw, resume_text):
    result = dict(raw)

    result["similarity"] = safe_score(
        result.get("similarity")
    )

    for key in (
        "resume_skills",
        "job_skills",
        "matched_skills",
        "missing_skills",
    ):
        result[key] = sorted(
            set(result.get(key) or [])
        )

    coverage = result.get("skill_coverage")

    if coverage is None:
        total = len(result["job_skills"])
        coverage = (
            len(result["matched_skills"]) / total * 100
            if total else 0
        )

    result["skill_coverage"] = safe_score(coverage)

    sections = {
        name: bool(re.search(pattern, resume_text, re.I))
        for name, pattern in SECTION_PATTERNS.items()
    }

    result["sections"] = sections

    result["health_score"] = round(
        sum(sections.values()) / len(sections) * 100,
        1,
    )

    recommendations = []

    if result["missing_skills"]:
        recommendations.append(
            "Review these skills from the job description: "
            + ", ".join(result["missing_skills"][:6])
            + ". Only include skills you genuinely have."
        )

    for section, found in sections.items():
        if not found:
            recommendations.append(
                f"Review your {section.lower()} section. "
                "It was not recognized by the checker."
            )

    if len(resume_text.split()) < 180:
        recommendations.append(
            "Consider adding relevant projects, "
            "responsibilities or achievements."
        )

    if not recommendations:
        recommendations.append(
            "Review your formatting, spelling and achievements "
            "before submitting your resume."
        )

    result["recommendations"] = recommendations

    return result


def show_metrics(result):
    a, b, c = st.columns(3)

    a.metric(
        "Skill coverage",
        f"{result['skill_coverage']:.1f}%",
    )

    b.metric(
        "Text similarity",
        f"{result['similarity']:.1f}%",
    )

    c.metric(
        "Resume health",
        f"{result['health_score']:.1f}%",
    )


def show_tags(skills, missing=False):
    if not skills:
        st.caption("None detected.")
        return

    css_class = "skill-tag missing" if missing else "skill-tag"

    markup = "".join(
        '<span class="' + css_class + '">'
        + html.escape(str(skill).title())
        + "</span>"
        for skill in skills
    )

    st.markdown(markup, unsafe_allow_html=True)


def show_skill_chart(result):
    matched = len(result["matched_skills"])
    missing = len(result["missing_skills"])

    if matched + missing == 0:
        st.info("No recognized job skills to chart.")
        return

    fig = go.Figure(
        go.Pie(
            labels=["Matched", "Potential gaps"],
            values=[matched, missing],
            hole=0.68,
            marker_colors=["#0FB99C", "#F4A261"],
        )
    )

    fig.update_layout(
        height=340,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#252746"),
        margin=dict(l=10, r=10, t=10, b=10),
    )

    st.plotly_chart(fig, use_container_width=True)


def show_health_chart(sections):
    names = list(sections)
    values = [int(sections[name]) for name in names]

    fig = go.Figure(
        go.Bar(
            x=values,
            y=names,
            orientation="h",
            marker_color=[
                "#0FB99C" if value else "#F4A261"
                for value in values
            ],
        )
    )

    fig.update_layout(
        height=350,
        xaxis=dict(range=[0, 1.1], visible=False),
        yaxis=dict(autorange="reversed", automargin=True),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#252746"),
        margin=dict(l=10, r=20, t=10, b=20),
    )

    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# PDF GENERATOR
# ============================================================

def generate_pdf(record):
    result = record["result"]
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    def para(value, style="BodyText"):
        return Paragraph(
            html.escape(str(value)),
            styles[style],
        )

    story = [
        para("ResumeIQ Pro — Career Intelligence Report", "Title"),
        Spacer(1, 15),
        para("Resume: " + record["filename"]),
        para("Role: " + record["role"]),
        para("Date: " + record["date"]),
        Spacer(1, 15),
    ]

    table = Table([
        ["Metric", "Result"],
        ["Skill coverage", f"{result['skill_coverage']:.1f}%"],
        ["Text similarity", f"{result['similarity']:.1f}%"],
        ["Resume health", f"{result['health_score']:.1f}%"],
    ])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0),
         colors.HexColor("#EDEAFF")),
        ("GRID", (0, 0), (-1, -1),
         0.4, colors.HexColor("#E1E3F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))

    story.append(table)

    groups = [
        ("Matched skills", result["matched_skills"]),
        ("Potential gaps", result["missing_skills"]),
        ("Recommendations", result["recommendations"]),
    ]

    for heading, items in groups:
        story.append(Spacer(1, 18))
        story.append(para(heading, "Heading2"))

        for item in items or ["None detected"]:
            story.append(para("- " + str(item)))

    story.append(Spacer(1, 15))

    story.append(para(
        "Results are approximate keyword and text comparisons, "
        "not an official ATS score or hiring prediction."
    ))

    doc.build(story)
    return buffer.getvalue()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-brand">'
        '<div class="sidebar-logo">✦</div>'
        '<div><div class="sidebar-name">'
        'resumeiq<span>.</span></div>'
        '<div class="sidebar-subtitle">'
        'CAREER INTELLIGENCE</div></div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-section">WORKSPACE</div>',
        unsafe_allow_html=True,
    )

    st.radio(
        "Workspace",
        list(PAGES),
        key="navigation",
        label_visibility="collapsed",
    )

    st.markdown(
        '<div class="sidebar-section">QUICK ACCESS</div>',
        unsafe_allow_html=True,
    )

    st.button(
        "✦  Try Demo Analysis",
        on_click=start_demo,
        use_container_width=True,
    )

    st.markdown(
        '<div class="sidebar-help">'
        '<div class="sidebar-help-title">'
        '✧ Your career companion</div>'
        '<div class="sidebar-help-copy">'
        'Understand your strengths, identify skill gaps '
        'and prepare for your next application.'
        '</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-footer">'
        '🟢 ResumeIQ Pro 2.0'
        '<div style="margin-top:7px;color:#8794BD">'
        'Built with Python &amp; Streamlit'
        '</div></div>',
        unsafe_allow_html=True,
    )

page = PAGES[st.session_state.navigation]


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    st.markdown(
        '<div class="hero">'
        '<div class="hero-kicker">'
        'WELCOME TO YOUR CAREER WORKSPACE'
        '</div>'
        '<div class="hero-title">'
        'Your next opportunity starts here.'
        '</div>'
        '<div class="hero-copy">'
        'Understand your resume, discover relevant skills '
        'and improve your next job application.'
        '</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="color-strip"></div>',
        unsafe_allow_html=True,
    )

    st.subheader("Explore your workspace")

    features = [
        (
            "📄",
            "Resume Analyzer",
            "Compare your resume against a job description.",
        ),
        (
            "📊",
            "Skill Intelligence",
            "Explore recognized skills and potential gaps.",
        ),
        (
            "🎯",
            "Career Recommendations",
            "Get practical suggestions to improve your CV.",
        ),
    ]

    cols = st.columns(3)

    for col, (icon, title, description) in zip(cols, features):
        with col:
            st.markdown(
                '<div class="feature">'
                f'<div style="font-size:28px">{icon}</div>'
                f'<div class="feature-title">{title}</div>'
                f'<div class="feature-copy">{description}</div>'
                '</div>',
                unsafe_allow_html=True,
            )

    st.write("")

    a, b = st.columns(2)

    with a:
        st.button(
            "Start new analysis →",
            type="primary",
            use_container_width=True,
            on_click=navigate,
            args=("Resume Analyzer",),
        )

    with b:
        st.button(
            "Explore with demo data",
            use_container_width=True,
            on_click=start_demo,
        )

    st.divider()

    st.subheader("Your activity")

    if not st.session_state.history:
        st.info("No analyses yet. Start your first resume review.")
    else:
        latest = st.session_state.history[0]
        show_metrics(latest["result"])


# ============================================================
# RESUME ANALYZER
# ============================================================

elif page == "Resume Analyzer":

    st.title("Resume Analyzer")
    st.caption(
        "Compare your resume with a target job description."
    )

    st.markdown(
        '<div class="color-strip"></div>',
        unsafe_allow_html=True,
    )

    st.subheader("01 — Choose your resume")

    st.radio(
        "Resume source",
        ["Upload resume", "Try demo"],
        key="resume_source",
        horizontal=True,
    )

    uploaded_file = None

    if st.session_state.resume_source == "Upload resume":

        uploaded_file = st.file_uploader(
            "Upload your PDF or DOCX",
            type=["pdf", "docx"],
        )

        if uploaded_file is not None:
            st.success("Selected: " + uploaded_file.name)

    else:
        st.info("Using a fictional demonstration resume.")

        with st.expander("Preview demo resume"):
            st.text(DEMO_RESUME)

    st.divider()
    st.subheader("02 — Select your target role")

    a, b = st.columns([3, 1])

    with a:
        st.selectbox(
            "Job role template",
            list(JOB_TEMPLATES),
            key="template",
        )

    with b:
        st.write("")
        st.write("")

        st.button(
            "Use template",
            on_click=use_template,
            use_container_width=True,
        )

    job_text = st.text_area(
        "Job description",
        key="job_description",
        height=220,
        placeholder="Paste the job description here...",
    )

    st.divider()
    st.subheader("03 — Analyze your resume")

    if st.button(
        "Analyze resume →",
        type="primary",
        use_container_width=True,
    ):

        if not job_text.strip():
            st.warning("Please enter a job description.")

        elif (
            st.session_state.resume_source == "Upload resume"
            and uploaded_file is None
        ):
            st.warning("Please upload your resume first.")

        else:
            try:
                with st.spinner("Analyzing your resume..."):

                    if st.session_state.resume_source == "Try demo":
                        resume_text = DEMO_RESUME
                        filename = "Demo_Resume.txt"
                    else:
                        if uploaded_file.size > 10 * 1024 * 1024:
                            raise ValueError(
                                "Please upload a file smaller than 10 MB."
                            )

                        resume_text = extract_resume_text(uploaded_file)
                        filename = uploaded_file.name

                    if not resume_text.strip():
                        raise ValueError(
                            "No readable text found in the resume."
                        )

                    raw = analyze_resume(
                        resume_text,
                        job_text,
                    )

                    result = normalize_result(
                        raw,
                        resume_text,
                    )

                    role = next(
                        (
                            line.strip()[:80]
                            for line in job_text.splitlines()
                            if line.strip()
                        ),
                        "Custom role",
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
                        "result": result,
                    }

                    st.session_state.history.insert(0, record)
                    st.session_state.history = (
                        st.session_state.history[:8]
                    )
                    st.session_state.current_id = record["id"]

                st.success("Analysis completed successfully!")

            except Exception as error:
                st.error("Unable to analyze the resume.")

                with st.expander("Technical details"):
                    st.code(str(error))

    record = get_record()

    if record:
        st.subheader("Latest analysis")
        show_metrics(record["result"])

        a, b = st.columns(2)

        with a:
            st.markdown("#### Matched skills")
            show_tags(record["result"]["matched_skills"])

        with b:
            st.markdown("#### Potential gaps")
            show_tags(
                record["result"]["missing_skills"],
                missing=True,
            )

        st.button(
            "Explore skill intelligence →",
            on_click=navigate,
            args=("Skill Intelligence",),
        )


# ============================================================
# SKILL INTELLIGENCE
# ============================================================

elif page == "Skill Intelligence":

    st.title("Skill Intelligence")
    st.caption("Explore your skill alignment with a job role.")

    record = get_record()

    if record is None:
        st.info("Analyze a resume first.")

        st.button(
            "Go to Resume Analyzer",
            on_click=navigate,
            args=("Resume Analyzer",),
        )

    else:
        result = record["result"]

        show_metrics(result)

        st.subheader("Skill match overview")
        show_skill_chart(result)

        a, b = st.columns(2)

        with a:
            st.subheader("Matched skills")
            show_tags(result["matched_skills"])

        with b:
            st.subheader("Potential gaps")
            show_tags(result["missing_skills"], missing=True)

        st.info(
            "Only add missing skills to your resume "
            "if you genuinely have those skills."
        )


# ============================================================
# RESUME HEALTH
# ============================================================

elif page == "Resume Health":

    st.title("Resume Health")
    st.caption("Review the structure of your resume.")

    record = get_record()

    if record is None:
        st.info("Analyze a resume first.")

    else:
        result = record["result"]

        a, b = st.columns(2)

        a.metric(
            "Resume health",
            f"{result['health_score']:.1f}%",
        )

        b.metric(
            "Sections detected",
            f"{sum(result['sections'].values())}"
            f" / {len(result['sections'])}",
        )

        show_health_chart(result["sections"])

        for section, found in result["sections"].items():
            with st.container(border=True):
                a, b = st.columns([3, 1])

                a.markdown(f"**{section}**")

                if found:
                    b.success("Detected")
                else:
                    b.warning("Review")

        st.caption(
            "Section detection is approximate. "
            "Different headings may not be recognized."
        )


# ============================================================
# RECOMMENDATIONS
# ============================================================

elif page == "Recommendations":

    st.title("Career Recommendations")
    st.caption("A practical checklist for improving your CV.")

    record = get_record()

    if record is None:
        st.info("Analyze a resume first.")

    else:
        st.subheader("Your improvement checklist")

        for index, suggestion in enumerate(
            record["result"]["recommendations"],
            start=1,
        ):
            with st.container(border=True):
                st.checkbox(
                    suggestion,
                    key=f"task_{record['id']}_{index}",
                )

        st.divider()

        st.markdown(
            "**Next step:** Update your resume with accurate "
            "information, then analyze it again."
        )


# ============================================================
# REPORTS & HISTORY
# ============================================================

elif page == "Reports & History":

    st.title("Reports & History")
    st.caption(
        "Review recent analyses and download PDF reports."
    )

    if not st.session_state.history:
        st.info("No reports yet. Analyze a resume first.")

    else:
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

                a, b = st.columns(2)

                with a:
                    st.button(
                        "View skill analysis",
                        key=f"view_{record['id']}",
                        on_click=open_record,
                        args=(record["id"],),
                        use_container_width=True,
                    )

                with b:
                    st.download_button(
                        "Download PDF",
                        data=generate_pdf(record),
                        file_name=(
                            f"ResumeIQ_Report_{index + 1}.pdf"
                        ),
                        mime="application/pdf",
                        key=f"pdf_{record['id']}",
                        use_container_width=True,
                    )

        st.button(
            "Clear session history",
            on_click=clear_history,
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "ResumeIQ Pro 2.0 · Career Intelligence Platform · "
    "Built with Python, Streamlit and scikit-learn."
)

with st.expander("About ResumeIQ & privacy"):

    st.write(
        "ResumeIQ uses text extraction, keyword-based "
        "skill detection, text similarity and "
        "resume section recognition."
    )

    st.write(
        "It does not predict hiring decisions "
        "or provide an official ATS score."
    )

    st.write(
        "Analysis history is temporarily stored in "
        "Streamlit session state."
    )

    st.write(
        "Avoid uploading sensitive personal information "
        "you do not want processed by the hosting provider."
    )
