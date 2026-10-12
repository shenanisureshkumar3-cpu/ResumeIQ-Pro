
import hashlib
import html
import re
from datetime import datetime
from io import BytesIO

import plotly.graph_objects as go
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)

from analyzer import extract_resume_text, analyze_resume

try:
    from analyzer import SKILLS
except ImportError:
    SKILLS = {}


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ResumeIQ Pro | Career Intelligence",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

PAGES = [
    "Dashboard",
    "Resume Analyzer",
    "Skill Intelligence",
    "Resume Health",
    "Recommendations",
    "Reports & History"
]

NAV_LABELS = [
    "◈  Dashboard",
    "▣  Resume Analyzer",
    "◉  Skill Intelligence",
    "✚  Resume Health",
    "✦  Recommendations",
    "▤  Reports & History"
]

LABEL_TO_PAGE = dict(zip(NAV_LABELS, PAGES))
PAGE_TO_LABEL = dict(zip(PAGES, NAV_LABELS))


# ============================================================
# PREMIUM UI DESIGN
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
    --purple: #705CF6;
    --ink: #232643;
    --muted: #777E98;
    --line: #E8EAF5;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: #F7F8FE;
}

.block-container {
    max-width: 1240px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #232643;
    letter-spacing: -.035em;
}

[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E8EAF5;
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0 6px 22px rgba(39,42,90,.035);
}

[data-testid="stMetricLabel"] {
    color: #7B8097;
    font-weight: 600;
}

[data-testid="stMetricValue"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #252746;
    font-weight: 800;
}

[data-testid="stFileUploader"] {
    background: white;
    border: 1px solid #E8EAF5;
    border-radius: 16px;
    padding: 12px;
}

[data-testid="stFileUploaderDropzone"] {
    background: #FAF9FF;
    border: 1px dashed #BFB8FC;
    border-radius: 13px;
}

[data-testid="stTextArea"] textarea {
    background: white;
    border: 1px solid #E6E7F2;
    border-radius: 13px;
    line-height: 1.7;
}

.stButton > button[kind="primary"],
.stDownloadButton > button[kind="primary"] {
    background: linear-gradient(100deg,#705CF6,#4187F5);
    color: white;
    border: none;
    border-radius: 12px;
    min-height: 49px;
    font-weight: 700;
    box-shadow: 0 8px 20px rgba(112,92,246,.16);
}

.stButton > button[kind="primary"]:hover,
.stDownloadButton > button[kind="primary"]:hover {
    background: #5948D8;
    color: white;
}

.stButton > button[kind="secondary"] {
    background: white;
    border: 1px solid #E1E3F2;
    color: #4A4E72;
    border-radius: 11px;
    min-height: 43px;
    font-weight: 600;
}

.stButton > button[kind="secondary"]:hover {
    border-color: #705CF6;
    color: #705CF6;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 17px;
    border-color: #E8EAF5;
}

/* MAIN DASHBOARD */

.hero {
    background: linear-gradient(
        115deg,#6552E9,#617AF2 57%,#30A7CE
    );
    color: white;
    border-radius: 23px;
    padding: 43px;
    margin: 10px 0 26px;
    box-shadow: 0 15px 35px rgba(89,91,205,.15);
}

.hero-kicker {
    color: #E8E7FF;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.7px;
}

.hero-title {
    color: white;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 800;
    font-size: clamp(29px,4vw,45px);
    line-height: 1.2;
    letter-spacing: -1.5px;
    margin: 13px 0;
}

.hero-copy {
    color: #F2F3FF;
    font-size: 14px;
    line-height: 1.85;
    max-width: 660px;
}

.feature {
    background: white;
    border: 1px solid #E8EAF5;
    border-radius: 18px;
    padding: 22px;
    min-height: 164px;
    box-shadow: 0 6px 20px rgba(39,42,90,.03);
}

.feature-icon {
    font-size: 27px;
    margin-bottom: 10px;
}

.feature-title {
    font-size: 15px;
    color: #252746;
    font-weight: 800;
    margin-bottom: 7px;
}

.feature-copy {
    color: #7B8097;
    font-size: 13px;
    line-height: 1.7;
}

.strip {
    display: flex;
    height: 5px;
    border-radius: 10px;
    overflow: hidden;
    margin: 15px 0 26px;
}

.strip span {
    flex: 1;
}

.tag {
    display: inline-block;
    padding: 8px 12px;
    margin: 4px 5px 4px 0;
    background: #EEEAFE;
    color: #5948C8;
    font-size: 12px;
    font-weight: 700;
    border-radius: 9px;
}

.tag.missing {
    background: #FFF0E5;
    color: #A3622A;
}

.info-panel {
    background: #ECF2FF;
    color: #3F609A;
    padding: 16px 18px;
    border-radius: 13px;
    font-size: 13px;
    line-height: 1.8;
    margin: 16px 0;
}

.footer {
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid #E7E9F4;
    text-align: center;
    color: #9297AD;
    font-size: 12px;
}

/* =========================================
   PREMIUM DARK SIDEBAR
========================================= */

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #151B38 0%,
        #1C2348 60%,
        #202751 100%
    ) !important;
    border-right: 1px solid #30375E !important;
}

[data-testid="stSidebar"]
[data-testid="stSidebarUserContent"] {
    padding-top: 1.2rem;
}

[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {
    color: #DCE1F8;
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 4px 24px;
    margin-bottom: 12px;
    border-bottom: 1px solid #343B60;
}

.sidebar-logo {
    width: 44px;
    height: 44px;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 13px;
    background: linear-gradient(
        135deg,#8876FF,#5D6EEC
    );
    color: white !important;
    font-size: 25px;
    box-shadow: 0 6px 20px rgba(112,92,246,.3);
}

.sidebar-brand-name {
    color: #FFFFFF;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 22px;
    font-weight: 800;
    letter-spacing: -1px;
}

.sidebar-brand-name span {
    color: #A393FF !important;
}

.sidebar-brand-subtitle {
    color: #9FA9D0;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 1.3px;
    margin-top: 3px;
}

.sidebar-section-title {
    color: #929FC7;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.8px;
    margin: 19px 0 10px 9px;
}

[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 7px;
}

[data-testid="stSidebar"]
div[role="radiogroup"] label {
    border-radius: 12px;
    padding: 11px 12px;
    background: transparent;
    transition: background .2s ease;
    cursor: pointer;
}

[data-testid="stSidebar"]
div[role="radiogroup"] label:hover {
    background: #2C355E !important;
}

[data-testid="stSidebar"]
div[role="radiogroup"]
label:has(input:checked) {
    background: linear-gradient(
        90deg,#5145A4,#3B427A
    ) !important;
    border-left: 3px solid #A79BFF;
}

[data-testid="stSidebar"]
div[role="radiogroup"] label p {
    color: #C8CFEA !important;
    font-size: 13px;
    font-weight: 600;
}

[data-testid="stSidebar"]
div[role="radiogroup"]
label:has(input:checked) p {
    color: #FFFFFF !important;
    font-weight: 800;
}

[data-testid="stSidebar"]
div[role="radiogroup"]
label input[type="radio"] {
    accent-color: #A79BFF;
}

[data-testid="stSidebar"]
.stButton > button[kind="primary"] {
    background: linear-gradient(
        100deg,#7865FA,#557DF4
    ) !important;
    color: #FFFFFF !important;
    border-radius: 12px;
    border: none;
    font-weight: 700;
    min-height: 46px;
}

.sidebar-help {
    margin-top: 20px;
    padding: 20px 17px;
    background: linear-gradient(
        145deg,#34366F,#283359
    );
    border: 1px solid #474B84;
    border-radius: 17px;
}

.sidebar-help-icon {
    color: #C2B8FF;
    font-size: 24px;
    margin-bottom: 9px;
}

.sidebar-help-title {
    color: #FFFFFF;
    font-size: 13px;
    font-weight: 800;
    margin-bottom: 8px;
}

.sidebar-help-text {
    color: #B9C2E3;
    font-size: 12px;
    line-height: 1.75;
}

.sidebar-footer {
    border-top: 1px solid #343B60;
    padding: 20px 7px 10px;
    margin-top: 22px;
    color: #DCE1F8;
    font-size: 12px;
    font-weight: 700;
}

.sidebar-status-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    background: #28D6AE;
    border-radius: 50%;
    margin-right: 7px;
}

.sidebar-footer-subtitle {
    color: #8794BD;
    font-size: 11px;
    font-weight: 400;
    margin: 7px 0 0 18px;
}

@media (max-width:700px) {
    .hero {
        padding: 28px 23px;
        border-radius: 18px;
    }

    .hero-title {
        font-size: 29px;
    }

    .feature {
        min-height: auto;
    }

    .block-container {
        padding-top: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# JOB DESCRIPTION TEMPLATES
# ============================================================

JOB_TEMPLATES = {
    "Data Analyst": (
        "Junior Data Analyst\n"
        "Required skills: Python, SQL, Excel, Power BI, "
        "Pandas, NumPy, data analysis, data visualization, "
        "communication and problem solving.\n"
        "Responsibilities: Prepare datasets, build dashboards "
        "and present insights."
    ),
    "Software Developer": (
        "Junior Software Developer\n"
        "Required skills: Python, JavaScript, HTML, CSS, SQL, "
        "Git, GitHub and problem solving.\n"
        "Responsibilities: Develop applications, debug software, "
        "work with APIs and test features."
    ),
    "UI/UX Designer": (
        "Junior UI/UX Designer\n"
        "Required skills: UI/UX, Figma, wireframing, prototyping, "
        "communication and problem solving.\n"
        "Responsibilities: Design interfaces, create prototypes "
        "and work with developers."
    ),
    "QA Engineer": (
        "Junior QA Engineer\n"
        "Required skills: software testing, manual testing, "
        "regression testing, user acceptance testing, SQL, "
        "Git, communication and problem solving.\n"
        "Responsibilities: Prepare test cases, report defects "
        "and validate fixes."
    ),
    "AI Engineer": (
        "Junior AI Engineer\n"
        "Required skills: Python, artificial intelligence, "
        "machine learning, data analysis, Pandas, NumPy, "
        "scikit-learn, TensorFlow, Git and communication.\n"
        "Responsibilities: Prepare datasets, train models "
        "and evaluate results."
    ),
    "Business Analyst": (
        "Junior Business Analyst\n"
        "Required skills: business analysis, Excel, SQL, "
        "Power BI, communication, problem solving "
        "and project management.\n"
        "Responsibilities: Document requirements, analyze "
        "processes and present findings."
    )
}

DEMO_RESUME = """
Jordan Lee
Email: jordan@example.com
Phone: 077 000 0000

Professional Summary
Computing graduate interested in data analytics
and software quality assurance.

Education
Higher National Diploma in Computing.

Work Experience
Quality Assurance Intern.
Performed manual testing, regression testing
and user acceptance testing.

Technical Skills
Python, SQL, Excel, Power BI, Pandas, NumPy,
HTML, CSS, Git, GitHub, Figma,
communication and problem solving.

Projects
Created a Power BI dashboard and a
Python data analysis application.
"""


# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {
    "nav_selection": NAV_LABELS[0],
    "input_mode": "Upload resume",
    "selected_template": "Data Analyst",
    "job_description": "",
    "history": [],
    "current_id": None
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# NAVIGATION CALLBACKS
# ============================================================

def navigate(page):
    st.session_state.nav_selection = PAGE_TO_LABEL[page]


def open_record(record_id, page="Skill Intelligence"):
    st.session_state.current_id = record_id
    navigate(page)


def start_demo():
    st.session_state.input_mode = "Try demo"
    st.session_state.selected_template = "Data Analyst"
    st.session_state.job_description = (
        JOB_TEMPLATES["Data Analyst"]
    )
    navigate("Resume Analyzer")


def load_template():
    st.session_state.job_description = (
        JOB_TEMPLATES[st.session_state.selected_template]
    )


def clear_history():
    st.session_state.history = []
    st.session_state.current_id = None


def get_record():
    return next(
        (
            record for record in st.session_state.history
            if record["id"] == st.session_state.current_id
        ),
        None
    )


# ============================================================
# ANALYZER COMPATIBILITY
# ============================================================

SECTION_PATTERNS = {
    "Contact": r"\b(email|phone|contact|linkedin)\b",
    "Summary": r"\b(summary|profile|objective|about me)\b",
    "Experience": (
        r"\b(experience|employment|internship|work history)\b"
    ),
    "Education": (
        r"\b(education|qualifications?|university|college)\b"
    ),
    "Skills": r"\b(skills|technologies|technical skills)\b",
    "Projects": r"\b(projects|portfolio|github)\b"
}


def safe_number(value):
    try:
        return max(0.0, min(float(value), 100.0))
    except (TypeError, ValueError):
        return 0.0


def normalize_result(raw, resume_text, job_text):
    result = dict(raw)

    matched = sorted(
        set(result.get("matched_skills") or [])
    )
    missing = sorted(
        set(result.get("missing_skills") or [])
    )
    resume_skills = sorted(
        set(result.get("resume_skills") or matched)
    )
    job_skills = sorted(
        set(result.get("job_skills") or matched + missing)
    )

    coverage = result.get("skill_coverage")

    if coverage is None:
        coverage = (
            100 * len(matched) / len(job_skills)
            if job_skills else 0
        )

    result.update(
        skill_coverage=safe_number(coverage),
        similarity=safe_number(result.get("similarity")),
        matched_skills=matched,
        missing_skills=missing,
        resume_skills=resume_skills,
        job_skills=job_skills
    )

    existing = result.get("resume_health")

    sections = (
        existing.get("sections")
        if isinstance(existing, dict)
        else None
    )

    if not isinstance(sections, dict):
        sections = result.get("sections")

    if not isinstance(sections, dict):
        sections = {
            name: bool(re.search(pattern, resume_text, re.I))
            for name, pattern in SECTION_PATTERNS.items()
        }

    sections = {
        str(name): bool(found)
        for name, found in sections.items()
    }

    health_score = (
        100 * sum(sections.values()) / len(sections)
        if sections else 0
    )

    result["resume_health"] = {
        "sections": sections,
        "score": round(health_score, 1)
    }

    categories = result.get("skill_categories")

    if not isinstance(categories, dict):
        categories = {
            name: [
                skill for skill in resume_skills
                if skill in values
            ]
            for name, values in SKILLS.items()
        }

        categories = {
            name: values
            for name, values in categories.items()
            if values
        }

        if not categories and resume_skills:
            categories = {
                "Recognized skills": resume_skills
            }

    result["skill_categories"] = categories

    recommendations = result.get("recommendations")

    if not isinstance(recommendations, list):
        recommendations = []

    if not recommendations:
        if missing:
            recommendations.append(
                "Review the job skills not detected in "
                "your resume: "
                + ", ".join(missing[:5])
                + ". Only include skills you genuinely have."
            )

        for name, found in sections.items():
            if not found:
                recommendations.append(
                    "Review your " + name.lower()
                    + " section. It was not recognized "
                    "by the text checker."
                )

        if len(resume_text.split()) < 180:
            recommendations.append(
                "Your resume appears short. Consider "
                "adding relevant projects, responsibilities "
                "or achievements."
            )

        if not recommendations:
            recommendations.append(
                "Review wording, formatting and evidence "
                "of achievements before applying."
            )

    result["recommendations"] = recommendations

    return result


# ============================================================
# UI HELPERS
# ============================================================

def color_strip():
    st.markdown(
        '<div class="strip">'
        '<span style="background:#705CF6"></span>'
        '<span style="background:#3478F6"></span>'
        '<span style="background:#0FB99C"></span>'
        '<span style="background:#F4A261"></span>'
        '<span style="background:#E66DA9"></span>'
        '</div>',
        unsafe_allow_html=True
    )


def feature(icon, title, description):
    markup = (
        '<div class="feature">'
        '<div class="feature-icon">' + icon + '</div>'
        '<div class="feature-title">'
        + html.escape(title) + '</div>'
        '<div class="feature-copy">'
        + html.escape(description) + '</div>'
        '</div>'
    )

    st.markdown(markup, unsafe_allow_html=True)


def tags(skills, missing=False):
    if not skills:
        st.caption("None detected.")
        return

    css_class = "tag missing" if missing else "tag"

    markup = "".join(
        '<span class="' + css_class + '">'
        + html.escape(str(skill).title())
        + '</span>'
        for skill in skills
    )

    st.markdown(markup, unsafe_allow_html=True)


def metrics(result):
    a, b, c = st.columns(3)

    a.metric(
        "Skill coverage",
        f"{result['skill_coverage']:.1f}%"
    )

    b.metric(
        "Text similarity",
        f"{result['similarity']:.1f}%"
    )

    c.metric(
        "Resume health",
        f"{result['resume_health']['score']:.1f}%"
    )


# ============================================================
# CHARTS
# ============================================================

def donut_chart(result):
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
            textinfo="percent"
        )
    )

    fig.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.1
        )
    )

    st.plotly_chart(fig, use_container_width=True)


def category_chart(result):
    categories = result["skill_categories"]

    if not categories:
        st.info("No recognized skill categories.")
        return

    names = list(categories)
    counts = [
        len(categories[name])
        for name in names
    ]

    fig = go.Figure(
        go.Bar(
            x=counts,
            y=names,
            orientation="h",
            marker_color="#705CF6",
            text=counts,
            textposition="outside"
        )
    )

    fig.update_layout(
        height=max(260, len(names) * 60),
        margin=dict(l=10, r=35, t=10, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            rangemode="tozero",
            gridcolor="#E8EAF5"
        ),
        yaxis=dict(
            autorange="reversed",
            automargin=True
        )
    )

    st.plotly_chart(fig, use_container_width=True)


def health_chart(sections):
    names = list(sections)

    values = [
        int(sections[name])
        for name in names
    ]

    fig = go.Figure(
        go.Bar(
            x=values,
            y=names,
            orientation="h",
            marker_color=[
                "#0FB99C" if value else "#F4A261"
                for value in values
            ]
        )
    )

    fig.update_layout(
        height=350,
        margin=dict(l=10, r=20, t=10, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            range=[0, 1.1],
            visible=False
        ),
        yaxis=dict(
            autorange="reversed",
            automargin=True
        ),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# PDF REPORT GENERATOR
# ============================================================

def generate_pdf(record):
    result = record["result"]
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=(595, 842),
        leftMargin=45,
        rightMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ResumeIQTitle",
            parent=styles["Title"],
            fontSize=22,
            leading=28,
            textColor=colors.HexColor("#5948D8"),
            spaceAfter=10
        )
    )

    styles.add(
        ParagraphStyle(
            name="ResumeIQSection",
            parent=styles["Heading2"],
            fontSize=12,
            leading=17,
            textColor=colors.HexColor("#252746"),
            spaceBefore=16,
            spaceAfter=8
        )
    )

    def paragraph(value, style="BodyText"):
        return Paragraph(
            html.escape(str(value)),
            styles[style]
        )

    story = [
        paragraph("ResumeIQ Pro", "ResumeIQTitle"),
        paragraph("Career Intelligence Report"),
        Spacer(1, 12),
        paragraph("Resume: " + record["filename"]),
        paragraph("Role: " + record["role"]),
        paragraph("Date: " + record["date"]),
        Spacer(1, 16)
    ]

    data = [
        ["Measure", "Value"],
        [
            "Skill coverage",
            f"{result['skill_coverage']:.1f}%"
        ],
        [
            "Text similarity",
            f"{result['similarity']:.1f}%"
        ],
        [
            "Resume health",
            f"{result['resume_health']['score']:.1f}%"
        ]
    ]

    table = Table(
        data,
        colWidths=[340, 160]
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND", (0, 0), (-1, 0),
                colors.HexColor("#EDEAFF")
            ),
            (
                "ROWBACKGROUNDS", (0, 1), (-1, -1),
                [
                    colors.white,
                    colors.HexColor("#F8F8FD")
                ]
            ),
            (
                "TOPPADDING", (0, 0), (-1, -1), 10
            ),
            (
                "BOTTOMPADDING", (0, 0), (-1, -1), 10
            )
        ])
    )

    story.extend([
        table,
        Spacer(1, 15)
    ])

    blocks = [
        (
            "Matched skills",
            result["matched_skills"]
        ),
        (
            "Potential skill gaps",
            result["missing_skills"]
        ),
        (
            "Resume structure",
            [
                f"{name}: "
                + ("Detected" if found else "Review")
                for name, found in
                result["resume_health"]["sections"].items()
            ]
        ),
        (
            "Recommendations",
            result["recommendations"]
        )
    ]

    for heading, items in blocks:
        story.append(
            paragraph(heading, "ResumeIQSection")
        )

        for item in items or ["None detected"]:
            story.append(
                paragraph("- " + str(item))
            )

    story.extend([
        Spacer(1, 15),
        paragraph(
            "This report uses keyword recognition, "
            "text similarity and section detection. "
            "It is not an official ATS score or "
            "prediction of hiring success."
        )
    ])

    doc.build(story)

    return buffer.getvalue()


# ============================================================
# PREMIUM SIDEBAR
# ============================================================

with st.sidebar:

    # Single-line HTML avoids raw HTML appearing on screen.
    st.markdown(
        '<div class="sidebar-brand">'
        '<div class="sidebar-logo">✦</div>'
        '<div>'
        '<div class="sidebar-brand-name">'
        'resumeiq<span>.</span>'
        '</div>'
        '<div class="sidebar-brand-subtitle">'
        'CAREER INTELLIGENCE'
        '</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-section-title">'
        'WORKSPACE'
        '</div>',
        unsafe_allow_html=True
    )

    st.radio(
        "Workspace",
        NAV_LABELS,
        key="nav_selection",
        label_visibility="collapsed"
    )

    st.markdown(
        '<div class="sidebar-section-title">'
        'QUICK ACCESS'
        '</div>',
        unsafe_allow_html=True
    )

    st.button(
        "✦  Try Demo Analysis",
        on_click=start_demo,
        use_container_width=True,
        type="primary"
    )

    st.markdown(
        '<div class="sidebar-help">'
        '<div class="sidebar-help-icon">✧</div>'
        '<div class="sidebar-help-title">'
        'Your career companion'
        '</div>'
        '<div class="sidebar-help-text">'
        'Understand your strengths, identify skill gaps '
        'and improve your next application.'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-footer">'
        '<span class="sidebar-status-dot"></span>'
        'ResumeIQ Pro 2.0'
        '<div class="sidebar-footer-subtitle">'
        'Built with Python &amp; Streamlit'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )


# Resolve sidebar selection to internal page name.
page = LABEL_TO_PAGE[st.session_state.nav_selection]


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
        'Understand your resume, discover relevant '
        'skills and turn feedback into a practical '
        'plan for your next application.'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    color_strip()

    st.subheader("Explore your workspace")

    st.caption(
        "A smarter way to prepare your next application."
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        feature(
            "📄",
            "Resume Analyzer",
            "Compare your resume against "
            "a target job description."
        )

    with c2:
        feature(
            "📊",
            "Skill Intelligence",
            "Explore recognized skills "
            "and potential gaps."
        )

    with c3:
        feature(
            "🎯",
            "Career Recommendations",
            "Get practical suggestions "
            "to improve your resume."
        )

    st.write("")

    a, b = st.columns(2)

    with a:
        st.button(
            "Start a new analysis →",
            type="primary",
            use_container_width=True,
            on_click=navigate,
            args=("Resume Analyzer",)
        )

    with b:
        st.button(
            "Explore with demo data",
            use_container_width=True,
            on_click=start_demo
        )

    st.divider()
    st.subheader("Your activity")

    history = st.session_state.history

    if not history:
        st.info(
            "No analyses yet. Start your first "
            "resume review to see activity here."
        )

    else:
        latest = history[0]

        a, b, c = st.columns(3)

        a.metric(
            "Latest skill coverage",
            f"{latest['result']['skill_coverage']:.1f}%"
        )

        b.metric(
            "Latest resume health",
            f"{latest['result']['resume_health']['score']:.1f}%"
        )

        c.metric(
            "Analyses this session",
            len(history)
        )

        st.caption(
            "Latest role: " + latest["role"]
        )

        st.button(
            "View analysis history →",
            on_click=navigate,
            args=("Reports & History",)
        )


# ============================================================
# RESUME ANALYZER
# ============================================================

elif page == "Resume Analyzer":

    st.title("Resume Analyzer")

    st.caption(
        "Three simple steps to understand "
        "your resume's alignment with a role."
    )

    color_strip()

    st.subheader("01 — Choose your resume")

    st.radio(
        "Resume source",
        ["Upload resume", "Try demo"],
        key="input_mode",
        horizontal=True
    )

    uploaded_file = None

    if st.session_state.input_mode == "Upload resume":

        uploaded_file = st.file_uploader(
            "Upload your PDF or DOCX",
            type=["pdf", "docx"],
            help="Maximum 10 MB"
        )

        if uploaded_file is not None:
            st.success(
                "Selected: " + uploaded_file.name
            )

    else:
        st.info(
            "Demo mode uses a fictional computing "
            "graduate's resume."
        )

        with st.expander("Preview demo resume"):
            st.text(DEMO_RESUME)

    st.divider()

    st.subheader("02 — Select your target role")

    left, right = st.columns([3, 1])

    with left:
        st.selectbox(
            "Job role template",
            list(JOB_TEMPLATES),
            key="selected_template"
        )

    with right:
        st.write("")
        st.write("")

        st.button(
            "Use template",
            on_click=load_template,
            use_container_width=True
        )

    job_text = st.text_area(
        "Job description",
        key="job_description",
        height=220,
        placeholder=(
            "Paste the job title, responsibilities "
            "and required skills here..."
        )
    )

    st.caption(
        "Templates are examples. You can edit "
        "the text to match a real job listing."
    )

    st.divider()

    st.subheader("03 — Analyze your resume")

    clicked = st.button(
        "Analyze resume →",
        type="primary",
        use_container_width=True
    )

    if clicked:

        if (
            st.session_state.input_mode == "Upload resume"
            and uploaded_file is None
        ):
            st.warning("Please upload a resume first.")

        elif not job_text.strip():
            st.warning(
                "Please enter a job description "
                "or select a template."
            )

        else:
            try:
                with st.spinner(
                    "Analyzing your resume..."
                ):

                    if st.session_state.input_mode == "Try demo":
                        resume_text = DEMO_RESUME
                        filename = "Demo_Resume.txt"
                        raw_bytes = DEMO_RESUME.encode("utf-8")

                    else:
                        raw_bytes = uploaded_file.getvalue()

                        if len(raw_bytes) > 10 * 1024 * 1024:
                            raise ValueError(
                                "Please upload a file "
                                "smaller than 10 MB."
                            )

                        resume_text = extract_resume_text(
                            uploaded_file
                        )

                        filename = uploaded_file.name

                    if not resume_text.strip():
                        raise ValueError(
                            "No readable text found. "
                            "Please use a text-based PDF "
                            "or DOCX document."
                        )

                    raw_result = analyze_resume(
                        resume_text,
                        job_text
                    )

                    result = normalize_result(
                        raw_result,
                        resume_text,
                        job_text
                    )

                    role = next(
                        (
                            line.strip()[:80]
                            for line in job_text.splitlines()
                            if line.strip()
                        ),
                        "Custom role"
                    )

                    signature = (
                        hashlib.sha256(raw_bytes).hexdigest(),
                        job_text
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
                        "signature": signature
                    }

                    st.session_state.history.insert(
                        0,
                        record
                    )

                    st.session_state.history = (
                        st.session_state.history[:8]
                    )

                    st.session_state.current_id = (
                        record["id"]
                    )

                st.success(
                    "Analysis complete! "
                    "Your results are ready."
                )

            except ValueError as error:
                st.error(str(error))

            except Exception as error:
                st.error(
                    "The analysis could not be completed. "
                    "Check the file and try again."
                )

                with st.expander("Technical details"):
                    st.code(str(error))

    record = get_record()

    if record is not None:

        if st.session_state.input_mode == "Try demo":
            current_bytes = DEMO_RESUME.encode("utf-8")

        elif uploaded_file is not None:
            current_bytes = uploaded_file.getvalue()

        else:
            current_bytes = None

        current_signature = (
            (
                hashlib.sha256(current_bytes).hexdigest(),
                job_text
            )
            if current_bytes is not None
            else None
        )

        if current_signature != record["signature"]:
            st.info(
                "Your inputs have changed. "
                "Click Analyze resume to refresh "
                "the results."
            )

        else:
            result = record["result"]

            st.markdown("## Your analysis results")

            metrics(result)

            st.caption(
                "These are approximate text and "
                "skill measures, not an official "
                "ATS score or hiring prediction."
            )

            a, b = st.columns(2)

            with a:
                st.markdown("### Matched skills")
                tags(result["matched_skills"])

            with b:
                st.markdown("### Potential skill gaps")

                tags(
                    result["missing_skills"],
                    missing=True
                )

            st.write("")

            a, b = st.columns(2)

            with a:
                st.button(
                    "Explore skill intelligence →",
                    on_click=navigate,
                    args=("Skill Intelligence",),
                    use_container_width=True
                )

            with b:
                st.button(
                    "View recommendations →",
                    on_click=navigate,
                    args=("Recommendations",),
                    use_container_width=True
                )


# ============================================================
# SKILL INTELLIGENCE
# ============================================================

elif page == "Skill Intelligence":

    st.title("Skill Intelligence")

    st.caption(
        "Explore recognized skills, categories "
        "and possible areas for improvement."
    )

    record = get_record()

    if record is None:

        st.info(
            "Analyze a resume first to see "
            "your skill intelligence."
        )

        st.button(
            "Go to Resume Analyzer →",
            on_click=navigate,
            args=("Resume Analyzer",)
        )

    else:
        result = record["result"]

        st.caption(
            "Analysis: " + record["filename"]
        )

        a, b, c = st.columns(3)

        a.metric(
            "Matched skills",
            len(result["matched_skills"])
        )

        b.metric(
            "Potential gaps",
            len(result["missing_skills"])
        )

        c.metric(
            "Skill coverage",
            f"{result['skill_coverage']:.1f}%"
        )

        st.write("")

        left, right = st.columns(2)

        with left:
            st.subheader("Job skill alignment")
            donut_chart(result)

        with right:
            st.subheader("Resume skill categories")
            category_chart(result)

        st.divider()

        left, right = st.columns(2)

        with left:
            st.subheader("Skills you match")
            tags(result["matched_skills"])

        with right:
            st.subheader("Skills to explore")

            tags(
                result["missing_skills"],
                missing=True
            )

        st.subheader("Learning priorities")

        if result["missing_skills"]:

            for index, skill in enumerate(
                result["missing_skills"][:5],
                start=1
            ):
                with st.container(border=True):

                    st.markdown(
                        f"**{index:02d} — {skill.title()}**"
                    )

                    st.caption(
                        "If you already have this skill, "
                        "show evidence of it in your CV. "
                        "Otherwise, consider learning it."
                    )

        else:
            st.success(
                "No gaps found within the "
                "recognized job skills."
            )


# ============================================================
# RESUME HEALTH
# ============================================================

elif page == "Resume Health":

    st.title("Resume Health Check")

    st.caption(
        "Check whether common resume sections "
        "were recognized."
    )

    record = get_record()

    if record is None:

        st.info("Analyze a resume first.")

        st.button(
            "Go to Resume Analyzer →",
            on_click=navigate,
            args=("Resume Analyzer",)
        )

    else:
        health = record["result"]["resume_health"]
        sections = health["sections"]

        a, b = st.columns(2)

        a.metric(
            "Section completeness",
            f"{health['score']:.1f}%"
        )

        b.metric(
            "Sections detected",
            f"{sum(sections.values())} / {len(sections)}"
        )

        st.subheader("Resume structure overview")

        health_chart(sections)

        st.subheader("Detailed section checks")

        for name, detected in sections.items():

            with st.container(border=True):

                left, right = st.columns([3, 1])

                with left:
                    st.markdown(f"**{name}**")

                with right:
                    if detected:
                        st.success("Detected")
                    else:
                        st.warning("Review")

        st.info(
            "Section recognition is approximate. "
            "A section may exist under a different "
            "heading and still be marked Review."
        )


# ============================================================
# RECOMMENDATIONS
# ============================================================

elif page == "Recommendations":

    st.title("Career Recommendations")

    st.caption(
        "Practical suggestions based on "
        "your selected analysis."
    )

    record = get_record()

    if record is None:

        st.info("Analyze a resume first.")

        st.button(
            "Go to Resume Analyzer →",
            on_click=navigate,
            args=("Resume Analyzer",)
        )

    else:
        result = record["result"]

        st.markdown(
            '<div class="info-panel">'
            'Use these recommendations as a guide. '
            'Only add skills, projects and experience '
            'that genuinely reflect your background.'
            '</div>',
            unsafe_allow_html=True
        )

        st.subheader("Your improvement checklist")

        for index, suggestion in enumerate(
            result["recommendations"],
            start=1
        ):

            with st.container(border=True):

                st.checkbox(
                    suggestion,
                    key=f"task_{record['id']}_{index}"
                )

        st.divider()

        st.subheader("Your next steps")

        st.write(
            "**1.** Review any job skills that "
            "were not detected in your resume."
        )

        st.write(
            "**2.** Highlight relevant projects "
            "and measurable achievements."
        )

        st.write(
            "**3.** Check headings, spelling "
            "and document formatting."
        )

        st.write(
            "**4.** Update your resume and "
            "run a new analysis."
        )


# ============================================================
# REPORTS & HISTORY
# ============================================================

elif page == "Reports & History":

    st.title("Reports & Analysis History")

    st.caption(
        "Review recent analyses and "
        "download your PDF reports."
    )

    history = st.session_state.history

    if not history:

        st.info(
            "No reports yet. Analyze a resume "
            "to create your first report."
        )

        st.button(
            "Start an analysis →",
            on_click=navigate,
            args=("Resume Analyzer",)
        )

    else:
        st.subheader("Recent analyses")

        st.caption(
            "Up to eight analyses are stored "
            "in your current Streamlit session. "
            "They are not permanently saved."
        )

        for index, record in enumerate(history):

            result = record["result"]

            with st.container(border=True):

                st.markdown(
                    "**" + html.escape(record["role"]) + "**"
                )

                st.caption(
                    record["filename"]
                    + " • "
                    + record["date"]
                )

                metrics(result)

                a, b = st.columns(2)

                with a:
                    # Navigation uses a callback to avoid
                    # StreamlitWidgetAlreadyInstantiatedError.
                    st.button(
                        "View skill analysis",
                        key=f"view_{record['id']}",
                        use_container_width=True,
                        on_click=open_record,
                        args=(
                            record["id"],
                            "Skill Intelligence"
                        )
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
                        use_container_width=True
                    )

        st.divider()

        st.button(
            "Clear session history",
            on_click=clear_history,
            use_container_width=True
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="footer">'
    'ResumeIQ Pro 2.0 · Career Intelligence Platform'
    '<div style="margin-top:6px">'
    'Built with Python, Streamlit and scikit-learn'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)

with st.expander("About ResumeIQ & privacy"):

    st.write(
        "ResumeIQ uses text extraction, "
        "keyword-based skill detection, "
        "TF-IDF similarity and resume "
        "section recognition."
    )

    st.write(
        "It does not use a generative AI model "
        "or predict hiring decisions."
    )

    st.write(
        "Analyses are stored temporarily "
        "in Streamlit session state. "
        "This application does not intentionally "
        "save uploaded resumes to a database."
    )

    st.write(
        "Avoid uploading sensitive information "
        "you do not want processed by the "
        "application hosting provider."
    )
