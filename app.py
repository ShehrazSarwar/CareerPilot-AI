import streamlit as st
import os
import json
import logging
from dotenv import load_dotenv

from utils.parser import parse_resume
from utils.ai_engine import evaluate_resume_with_ai
from utils.roadmap_generator import generate_pdf_report
from utils.job_matcher import match_job_description

load_dotenv()

st.set_page_config(
    page_title="CareerPilot AI – Personalized Career Mentor",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────────────
# EXTRAORDINARY UI STYLESHEET
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ──────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;600;700;800&display=swap');

/* ── Base ──────────────────────────────────────────────────────────────── */
html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; }
h1,h2,h3,h4,h5,h6 { font-family: 'Outfit', sans-serif; font-weight: 700; }

/* ── Sidebar ───────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--secondary-background-color);
    border-right: 1px solid rgba(99,102,241,0.12);
}
[data-testid="stSidebar"]::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 260px; height: 4px;
    background: linear-gradient(90deg,#4f46e5,#06b6d4,#7c3aed);
}

/* ── HERO BANNER ───────────────────────────────────────────────────────── */
.hero-wrap {
    position: relative;
    background: linear-gradient(135deg,#1e1b4b 0%,#312e81 30%,#1e3a8a 60%,#164e63 100%);
    background-size: 300% 300%;
    animation: heroShift 18s ease infinite;
    border-radius: 28px;
    padding: 3.5rem 3rem 3rem;
    margin-bottom: 2rem;
    overflow: hidden;
    box-shadow: 0 30px 60px -20px rgba(79,70,229,0.5);
}
@keyframes heroShift {
    0%{background-position:0% 50%}
    50%{background-position:100% 50%}
    100%{background-position:0% 50%}
}
/* floating orbs */
.hero-wrap::before {
    content:'';
    position:absolute; top:-80px; right:-60px;
    width:320px;height:320px;
    background:radial-gradient(circle,rgba(139,92,246,.35),transparent 70%);
    border-radius:50%;
    animation: floatOrb1 8s ease-in-out infinite;
}
.hero-wrap::after {
    content:'';
    position:absolute; bottom:-100px; left:10%;
    width:280px;height:280px;
    background:radial-gradient(circle,rgba(6,182,212,.3),transparent 70%);
    border-radius:50%;
    animation: floatOrb2 11s ease-in-out infinite;
}
@keyframes floatOrb1 {
    0%,100%{transform:translate(0,0) scale(1)}
    50%{transform:translate(-30px,20px) scale(1.1)}
}
@keyframes floatOrb2 {
    0%,100%{transform:translate(0,0) scale(1)}
    50%{transform:translate(20px,-30px) scale(1.08)}
}
.hero-badge {
    display:inline-block;
    background:rgba(255,255,255,.12);
    border:1px solid rgba(255,255,255,.2);
    backdrop-filter:blur(8px);
    color:rgba(255,255,255,.9);
    font-size:0.78rem;
    font-weight:600;
    padding:0.3rem 0.9rem;
    border-radius:30px;
    letter-spacing:0.08em;
    text-transform:uppercase;
    margin-bottom:1rem;
}
.hero-title {
    font-size:3rem;
    font-weight:800;
    color:#fff !important;
    letter-spacing:-0.04em;
    line-height:1.1;
    margin:0 0 0.75rem;
}
.hero-title span {
    background:linear-gradient(90deg,#a5b4fc,#67e8f9);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}
.hero-sub {
    font-size:1.1rem;
    color:rgba(255,255,255,.75);
    font-weight:400;
    line-height:1.6;
    max-width:620px;
    margin:0;
}
.hero-stats {
    display:flex;
    gap:2rem;
    margin-top:2rem;
    flex-wrap:wrap;
}
.hero-stat {
    display:flex;
    flex-direction:column;
    color:rgba(255,255,255,.85);
}
.hero-stat-num {
    font-size:1.5rem;
    font-weight:800;
    color:#fff;
}
.hero-stat-label {
    font-size:0.78rem;
    opacity:.65;
    text-transform:uppercase;
    letter-spacing:0.06em;
}

/* ── GLASS CARDS ───────────────────────────────────────────────────────── */
.g-card {
    position:relative;
    background:var(--secondary-background-color);
    border:1px solid rgba(99,102,241,0.1);
    border-radius:20px;
    padding:1.75rem;
    margin-bottom:1.25rem;
    color:var(--text-color);
    transition:transform .35s cubic-bezier(.16,1,.3,1),
               box-shadow .35s cubic-bezier(.16,1,.3,1),
               border-color .35s ease;
    overflow:hidden;
}
.g-card::before {
    content:'';
    position:absolute;
    inset:0;
    border-radius:20px;
    background:linear-gradient(135deg,rgba(99,102,241,.04),rgba(6,182,212,.04));
    pointer-events:none;
}
.g-card:hover {
    transform:translateY(-6px);
    border-color:rgba(99,102,241,.35);
    box-shadow:0 24px 50px rgba(99,102,241,.13);
}
.g-card-title {
    font-size:1.05rem;
    font-weight:700;
    color:var(--text-color);
    padding-bottom:0.75rem;
    margin-bottom:0.9rem;
    border-bottom:1px solid rgba(99,102,241,.1);
    display:flex;
    align-items:center;
    gap:0.5rem;
}
.g-card-title .icon {
    width:28px;height:28px;
    background:linear-gradient(135deg,#4f46e5,#06b6d4);
    border-radius:8px;
    display:flex;align-items:center;justify-content:center;
    font-size:0.85rem;
    flex-shrink:0;
}

/* ── SCORE RING ────────────────────────────────────────────────────────── */
.score-wrap {
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    padding:2rem 1rem;
    border-radius:20px;
    background:var(--secondary-background-color);
    border:1px solid rgba(99,102,241,.15);
    transition:transform .35s ease, box-shadow .35s ease;
    position:relative;
    overflow:hidden;
}
.score-wrap::before {
    content:'';
    position:absolute;
    inset:-1px;
    border-radius:20px;
    background:linear-gradient(135deg,rgba(79,70,229,.15),rgba(6,182,212,.15));
    z-index:0;
}
.score-wrap > * { position:relative; z-index:1; }
.score-wrap:hover {
    transform:translateY(-5px);
    box-shadow:0 20px 40px rgba(99,102,241,.15);
}
.score-ring {
    position:relative;
    width:150px;height:150px;
    margin-bottom:0.75rem;
}
.score-ring svg { transform:rotate(-90deg); }
.score-ring .bg-circle { fill:none; stroke:rgba(99,102,241,.1); stroke-width:10; }
.score-ring .fg-circle {
    fill:none;
    stroke:url(#scoreGrad);
    stroke-width:10;
    stroke-linecap:round;
    transition: stroke-dashoffset 1.5s cubic-bezier(.16,1,.3,1);
}
.score-center {
    position:absolute;
    inset:0;
    display:flex;flex-direction:column;
    align-items:center;justify-content:center;
}
.score-num {
    font-size:2.2rem;
    font-weight:800;
    background:linear-gradient(135deg,#4f46e5,#06b6d4);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    line-height:1;
}
.score-pct { font-size:1rem; font-weight:600; opacity:.5; margin-top:-4px; }
.score-label {
    font-size:0.8rem;
    font-weight:700;
    text-transform:uppercase;
    letter-spacing:0.1em;
    opacity:.6;
    color:var(--text-color);
}
.score-status {
    font-size:0.95rem;
    font-weight:600;
    margin-top:0.4rem;
    padding:0.3rem 1rem;
    border-radius:30px;
}

/* ── ITEMS / CHIPS ─────────────────────────────────────────────────────── */
.item-strength {
    display:flex; align-items:flex-start; gap:0.75rem;
    background:rgba(34,197,94,.07);
    border:1px solid rgba(34,197,94,.15);
    border-left:4px solid #22c55e;
    padding:0.8rem 1rem;
    border-radius:12px;
    margin-bottom:0.6rem;
    font-size:0.92rem;
    color:var(--text-color);
    transition:transform .2s ease;
}
.item-strength:hover{transform:translateX(4px);}
.item-weakness {
    display:flex; align-items:flex-start; gap:0.75rem;
    background:rgba(239,68,68,.07);
    border:1px solid rgba(239,68,68,.15);
    border-left:4px solid #ef4444;
    padding:0.8rem 1rem;
    border-radius:12px;
    margin-bottom:0.6rem;
    font-size:0.92rem;
    color:var(--text-color);
    transition:transform .2s ease;
}
.item-weakness:hover{transform:translateX(4px);}

/* ── CHIPS ─────────────────────────────────────────────────────────────── */
.chip {
    display:inline-flex;align-items:center;gap:0.35rem;
    background:rgba(99,102,241,.08);
    color:var(--text-color);
    font-size:0.82rem; font-weight:600;
    padding:0.4rem 0.9rem;
    border-radius:30px;
    margin:0.25rem;
    border:1px solid rgba(99,102,241,.15);
    transition:all .25s ease;
    cursor:default;
}
.chip:hover {
    background:linear-gradient(135deg,#4f46e5,#06b6d4);
    color:#fff;
    border-color:transparent;
    transform:translateY(-2px);
    box-shadow:0 6px 15px rgba(79,70,229,.3);
}
.chip-green {
    background:rgba(34,197,94,.1);
    border-color:rgba(34,197,94,.2);
    color:var(--text-color);
}
.chip-red {
    background:rgba(239,68,68,.1);
    border-color:rgba(239,68,68,.2);
    color:var(--text-color);
}

/* ── GAP DETAIL ROWS ───────────────────────────────────────────────────── */
.gap-row {
    background:rgba(124,58,237,.06);
    border:1px solid rgba(124,58,237,.12);
    border-radius:12px;
    padding:0.85rem 1.1rem;
    margin-bottom:0.55rem;
    font-size:0.92rem;
    color:var(--text-color);
    transition:transform .2s ease,box-shadow .2s ease;
}
.gap-row:hover { transform:translateX(3px); box-shadow:0 4px 12px rgba(124,58,237,.1); }
.gap-dot { color:#7c3aed; font-weight:900; margin-right:0.5rem; }

/* ── TIMELINE ──────────────────────────────────────────────────────────── */
.tl-item {
    position:relative;
    padding:1.5rem 1.5rem 1.5rem 3rem;
    border-radius:16px;
    background:var(--secondary-background-color);
    border:1px solid rgba(99,102,241,.1);
    margin-bottom:1.25rem;
    color:var(--text-color);
    transition:transform .3s ease,box-shadow .3s ease;
    overflow:hidden;
}
.tl-item::before {
    content:'';
    position:absolute; left:0; top:0; bottom:0;
    width:4px;
    background:var(--tl-color,linear-gradient(180deg,#4f46e5,#06b6d4));
    border-radius:4px 0 0 4px;
}
.tl-item:hover { transform:translateX(5px); box-shadow:0 10px 25px rgba(99,102,241,.1); }
.tl-node {
    position:absolute;
    left:14px; top:50%; transform:translateY(-50%);
    width:20px;height:20px;
    border-radius:50%;
    background:var(--tl-color,#4f46e5);
    display:flex;align-items:center;justify-content:center;
    font-size:0.7rem;
    color:#fff;
    font-weight:800;
    box-shadow:0 0 0 4px rgba(99,102,241,.15);
}
.tl-phase {
    font-size:0.72rem;font-weight:700;text-transform:uppercase;
    letter-spacing:0.1em;opacity:.5;margin-bottom:0.2rem;
}
.tl-head {
    font-size:1.15rem;font-weight:700;
    background:linear-gradient(90deg,#6366f1,#0891b2);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    margin-bottom:0.6rem;
}

/* ── PROJECT CARDS ─────────────────────────────────────────────────────── */
.proj-card {
    border-radius:20px;
    border:1px solid rgba(99,102,241,.1);
    border-top:5px solid;
    border-top-color:#4f46e5;
    background:var(--secondary-background-color);
    padding:1.75rem;
    margin-bottom:1.25rem;
    color:var(--text-color);
    transition:all .35s cubic-bezier(.16,1,.3,1);
    position:relative;overflow:hidden;
}
.proj-card::after {
    content:'';
    position:absolute; top:0; right:0;
    width:80px; height:80px;
    background:radial-gradient(circle at top right,rgba(99,102,241,.08),transparent);
}
.proj-card:hover { transform:translateY(-7px); box-shadow:0 24px 50px rgba(99,102,241,.14); }
.proj-title { font-size:1.15rem;font-weight:700;margin-bottom:0.4rem; }
.proj-desc { font-size:0.9rem;opacity:.75;line-height:1.55;margin-bottom:1rem; }
.diff-badge {
    font-size:0.72rem;font-weight:700;
    padding:0.22rem 0.6rem;border-radius:6px;
    text-transform:uppercase;letter-spacing:.05em;
}
.diff-b{background:rgba(34,197,94,.15);color:#16a34a;}
.diff-i{background:rgba(234,179,8,.15);color:#d97706;}
.diff-a{background:rgba(239,68,68,.15);color:#dc2626;}

/* ── CERT CARDS ────────────────────────────────────────────────────────── */
.cert-card {
    display:flex;gap:1rem;
    padding:1.25rem;
    border-radius:16px;
    background:var(--secondary-background-color);
    border:1px solid rgba(6,182,212,.12);
    border-left:5px solid #06b6d4;
    margin-bottom:1rem;
    color:var(--text-color);
    transition:transform .25s ease;
}
.cert-card:hover { transform:translateX(5px); }
.cert-icon {
    width:44px;height:44px;flex-shrink:0;
    background:linear-gradient(135deg,rgba(6,182,212,.15),rgba(14,116,144,.1));
    border-radius:12px;
    display:flex;align-items:center;justify-content:center;
    font-size:1.3rem;
}
.cert-name{font-size:1rem;font-weight:700;margin-bottom:0.2rem;}
.cert-provider{font-size:0.8rem;color:#0891b2;font-weight:600;margin-bottom:0.4rem;}
.cert-reason{font-size:0.88rem;opacity:.75;line-height:1.4;}

/* ── QA EXPANDER OVERRIDES ─────────────────────────────────────────────── */
details summary {
    font-weight:600 !important;
    font-size:0.95rem !important;
    padding:0.75rem 0 !important;
}

/* ── JOB MATCH SCORE ───────────────────────────────────────────────────── */
.match-score-wrap {
    display:flex;flex-direction:column;
    align-items:center;justify-content:center;
    padding:2rem 1rem;
    border-radius:20px;
    background:var(--secondary-background-color);
    border:1px solid rgba(128,128,128,.15);
    text-align:center;
}
.match-num {
    font-size:3.5rem;font-weight:800;
    line-height:1;
}
.match-label {
    font-size:0.75rem;font-weight:700;text-transform:uppercase;
    letter-spacing:0.1em;opacity:.5;margin-top:0.4rem;
    color:var(--text-color);
}

/* ── LANDING FEATURE CARDS ─────────────────────────────────────────────── */
.feat-card {
    border-radius:20px;
    background:var(--secondary-background-color);
    border:1px solid rgba(99,102,241,.08);
    padding:1.75rem;
    min-height:195px;
    transition:all .35s cubic-bezier(.16,1,.3,1);
    position:relative;overflow:hidden;
    color:var(--text-color);
}
.feat-card::after {
    content:'';
    position:absolute;bottom:-20px;right:-20px;
    width:80px;height:80px;
    background:radial-gradient(circle,rgba(99,102,241,.08),transparent);
    border-radius:50%;
}
.feat-card:hover {
    transform:translateY(-7px);
    border-color:rgba(99,102,241,.3);
    box-shadow:0 20px 40px rgba(99,102,241,.1);
}
.feat-icon {
    width:46px;height:46px;
    border-radius:14px;
    background:linear-gradient(135deg,#4f46e5,#06b6d4);
    display:flex;align-items:center;justify-content:center;
    font-size:1.3rem;
    margin-bottom:1rem;
    box-shadow:0 8px 20px rgba(79,70,229,.3);
}
.feat-title{font-size:1rem;font-weight:700;margin-bottom:0.5rem;}
.feat-desc{font-size:0.88rem;opacity:.65;line-height:1.5;}

/* ── STREAMLIT BUTTON OVERRIDE ─────────────────────────────────────────── */
div.stButton > button {
    font-family:'Outfit',sans-serif !important;
    font-weight:700 !important;
    font-size:0.95rem !important;
    border-radius:14px !important;
    border:none !important;
    background:linear-gradient(135deg,#4f46e5 0%,#0891b2 100%) !important;
    color:#fff !important;
    padding:0.65rem 1.5rem !important;
    letter-spacing:0.01em !important;
    box-shadow:0 8px 20px rgba(79,70,229,.3) !important;
    transition:all .3s cubic-bezier(.16,1,.3,1) !important;
}
div.stButton > button:hover {
    transform:translateY(-3px) !important;
    box-shadow:0 14px 30px rgba(79,70,229,.45) !important;
    background:linear-gradient(135deg,#6366f1 0%,#0e7490 100%) !important;
}
div.stButton > button:active { transform:translateY(0) !important; }

/* ── DOWNLOAD BUTTON ───────────────────────────────────────────────────── */
div.stDownloadButton > button {
    font-family:'Outfit',sans-serif !important;
    font-weight:700 !important;
    border-radius:14px !important;
    border:none !important;
    background:linear-gradient(135deg,#059669 0%,#0891b2 100%) !important;
    color:#fff !important;
    padding:0.65rem 1.5rem !important;
    box-shadow:0 8px 20px rgba(5,150,105,.3) !important;
    transition:all .3s cubic-bezier(.16,1,.3,1) !important;
}
div.stDownloadButton > button:hover {
    transform:translateY(-3px) !important;
    box-shadow:0 14px 30px rgba(5,150,105,.4) !important;
}

/* ── TABS OVERRIDE ─────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap:0.3rem;
    background:var(--secondary-background-color) !important;
    padding:0.35rem !important;
    border-radius:16px !important;
    border:1px solid rgba(99,102,241,.1) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius:12px !important;
    font-weight:600 !important;
    padding:0.55rem 1rem !important;
    font-size:0.88rem !important;
    transition:all .25s ease !important;
}
.stTabs [aria-selected="true"] {
    background:linear-gradient(135deg,#4f46e5,#0891b2) !important;
    color:#fff !important;
}

/* ── FILE UPLOADER OVERRIDE ────────────────────────────────────────────── */
[data-testid="stFileUploadDropzone"] {
    border:2px dashed rgba(99,102,241,.3) !important;
    border-radius:14px !important;
    background:rgba(99,102,241,.03) !important;
    transition:border-color .2s ease !important;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color:rgba(99,102,241,.6) !important;
}

/* ── SELECTBOX / TEXT INPUT ────────────────────────────────────────────── */
.stSelectbox > div > div,
.stTextInput > div > div > input {
    border-radius:12px !important;
    border:1px solid rgba(99,102,241,.2) !important;
    transition:border-color .2s ease, box-shadow .2s ease !important;
}
.stSelectbox > div > div:focus-within,
.stTextInput > div > div > input:focus {
    border-color:rgba(99,102,241,.5) !important;
    box-shadow:0 0 0 3px rgba(99,102,241,.1) !important;
}

/* ── DIVIDERS ──────────────────────────────────────────────────────────── */
hr { border-color:rgba(99,102,241,.1) !important; }

/* ── SPINNER ───────────────────────────────────────────────────────────── */
.stSpinner > div { border-top-color:#4f46e5 !important; }

/* ── SCROLLBAR ─────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width:6px; height:6px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:rgba(99,102,241,.25); border-radius:10px; }
::-webkit-scrollbar-thumb:hover { background:rgba(99,102,241,.5); }
</style>
""", unsafe_allow_html=True)


# ─── Score ring helper (SVG) ───────────────────────────────────────────────
def render_score_ring(score: int, label: str):
    r = 65
    circ = 2 * 3.14159 * r
    dash = (score / 100) * circ
    color = "#22c55e" if score >= 80 else ("#eab308" if score >= 60 else "#ef4444")
    status = "Industry Ready" if score >= 80 else ("Transitioning" if score >= 60 else "Re-skilling Phase")
    st.markdown(f"""
    <div class="score-wrap">
        <div class="score-ring">
            <svg viewBox="0 0 150 150" width="150" height="150">
                <defs>
                    <linearGradient id="scoreGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stop-color="#4f46e5"/>
                        <stop offset="100%" stop-color="#06b6d4"/>
                    </linearGradient>
                </defs>
                <circle class="bg-circle" cx="75" cy="75" r="{r}"/>
                <circle class="fg-circle" cx="75" cy="75" r="{r}"
                    stroke-dasharray="{dash:.1f} {circ:.1f}"
                    stroke-dashoffset="0"/>
            </svg>
            <div class="score-center">
                <div class="score-num">{score}</div>
                <div class="score-pct">/ 100</div>
            </div>
        </div>
        <div class="score-label">Career Readiness</div>
        <div class="score-status" style="color:{color};background:{'rgba(34,197,94,.12)' if score>=80 else ('rgba(234,179,8,.12)' if score>=60 else 'rgba(239,68,68,.12)')};margin-top:0.5rem;">
            {'✅' if score>=80 else ('⚡' if score>=60 else '🎯')} {status}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─── Session State Init ────────────────────────────────────────────────────
for key in ['cv_text','analysis','target_role','job_match_result','pdf_report']:
    if key not in st.session_state:
        st.session_state[key] = None


# ═════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    if os.path.exists("assets/logo.png"):
        st.image("assets/logo.png", use_container_width=True)
    
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <div style="font-size:1.2rem;font-weight:800;font-family:'Outfit',sans-serif;
                    background:linear-gradient(135deg,#6366f1,#06b6d4);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            CareerPilot AI
        </div>
        <div style="font-size:0.78rem;opacity:.5;margin-top:2px;">
            Powered by FAANG-Grade AI Coach
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**🔑 API Key Override**")
    custom_key = st.text_input("Gemini API Key", type="password", 
                                placeholder="AQ.Ab8RN...", 
                                help="Leave blank to use .env key",
                                label_visibility="collapsed")
    
    st.markdown("**📄 Resume Upload**")
    uploaded_file = st.file_uploader("Upload CV", type=["pdf","docx"],
                                      label_visibility="collapsed")
    if uploaded_file:
        st.success(f"📎 {uploaded_file.name}", icon=None)
    
    st.markdown("**🎯 Target Role**")
    role_options = [
        "Software Engineer", "AI Engineer", "Data Analyst",
        "Data Scientist", "Cybersecurity Analyst", "Product Manager",
        "Custom Role..."
    ]
    selected_role_option = st.selectbox("Role", role_options, label_visibility="collapsed")
    if selected_role_option == "Custom Role...":
        target_role = st.text_input("Enter target role", placeholder="e.g., Cloud Architect", label_visibility="collapsed")
    else:
        target_role = selected_role_option
    
    st.markdown("---")
    analyze_clicked = st.button("🚀 Analyze My Career", use_container_width=True)
    
    st.markdown("""
    <div style="margin-top:2rem;padding:1rem;border-radius:14px;
                background:rgba(99,102,241,.06);border:1px solid rgba(99,102,241,.1);
                font-size:0.8rem;opacity:.65;line-height:1.5;">
        <strong>🔒 Privacy First</strong><br/>
        Your CV text is processed in-memory and never stored permanently.
    </div>
    """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ═════════════════════════════════════════════════════════════════════════════

# ── Hero Banner ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <div class="hero-badge">✦ AI-Powered Career Mentor</div>
    <div class="hero-title">
        Your path to <span>dream careers</span><br/>starts here.
    </div>
    <p class="hero-sub">
        Upload your CV, pick a target role, and get a FAANG-grade career analysis with a
        personalised 90-day roadmap — in seconds.
    </p>
    <div class="hero-stats">
        <div class="hero-stat">
            <span class="hero-stat-num">7</span>
            <span class="hero-stat-label">Dashboard Tabs</span>
        </div>
        <div class="hero-stat">
            <span class="hero-stat-num">6</span>
            <span class="hero-stat-label">Career Roles</span>
        </div>
        <div class="hero-stat">
            <span class="hero-stat-num">90</span>
            <span class="hero-stat-label">Day Roadmap</span>
        </div>
        <div class="hero-stat">
            <span class="hero-stat-num">PDF</span>
            <span class="hero-stat-label">Export Ready</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Analysis trigger ─────────────────────────────────────────────────────────
if analyze_clicked:
    if uploaded_file is None:
        st.warning("⚠️ Please upload a PDF or DOCX resume before starting the analysis.")
    elif selected_role_option == "Custom Role..." and not target_role.strip():
        st.warning("⚠️ Please enter a custom target role first.")
    else:
        with st.spinner("🔍 Reading your CV and running AI analysis..."):
            try:
                cv_text = parse_resume(uploaded_file)
                st.session_state.cv_text = cv_text
                st.session_state.target_role = target_role
                analysis = evaluate_resume_with_ai(cv_text, target_role, custom_key or None)
                st.session_state.analysis = analysis
                try:
                    st.session_state.pdf_report = generate_pdf_report(analysis, target_role)
                except Exception as ex:
                    st.session_state.pdf_report = None
                    logging.error(f"PDF generation failed: {ex}")
                st.session_state.job_match_result = None
                st.toast("✅ Analysis complete!", icon="🚀")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


# ═════════════════════════════════════════════════════════════════════════════
# RESULTS DASHBOARD
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.analysis:
    analysis  = st.session_state.analysis
    role      = st.session_state.target_role
    pdf_bytes = st.session_state.pdf_report
    score     = analysis.get("career_score", 0)

    # ── Top metrics strip ────────────────────────────────────────────────────
    c1, c2, c3 = st.columns([1.6, 2.5, 2])

    with c1:
        render_score_ring(score, role)

    with c2:
        st.markdown(f"""
        <div class="g-card" style="height:100%;margin-bottom:0;display:flex;flex-direction:column;justify-content:center;">
            <div style="font-size:0.75rem;font-weight:700;text-transform:uppercase;
                        letter-spacing:0.1em;opacity:.45;margin-bottom:0.35rem;">
                EVALUATING FOR
            </div>
            <div style="font-size:2rem;font-weight:800;
                        background:linear-gradient(135deg,#4f46e5,#06b6d4);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                        margin-bottom:0.4rem;">
                {role}
            </div>
            <div style="font-size:0.85rem;opacity:.55;">
                👤 Coached by a Senior FAANG Career Coach persona
            </div>
            <div style="display:flex;gap:1rem;margin-top:1rem;flex-wrap:wrap;">
                <span style="font-size:0.78rem;padding:0.25rem 0.7rem;border-radius:20px;
                             background:rgba(99,102,241,.1);color:var(--text-color);
                             border:1px solid rgba(99,102,241,.15);">
                    {len(analysis.get('strengths', []))} Strengths
                </span>
                <span style="font-size:0.78rem;padding:0.25rem 0.7rem;border-radius:20px;
                             background:rgba(239,68,68,.1);color:var(--text-color);
                             border:1px solid rgba(239,68,68,.15);">
                    {len(analysis.get('skill_gaps', []))} Skill Gaps
                </span>
                <span style="font-size:0.78rem;padding:0.25rem 0.7rem;border-radius:20px;
                             background:rgba(6,182,212,.1);color:var(--text-color);
                             border:1px solid rgba(6,182,212,.15);">
                    {len(analysis.get('project_ideas', []))} Projects
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="g-card" style="height:100%;margin-bottom:0;display:flex;flex-direction:column;justify-content:center;">
            <div style="font-size:0.75rem;font-weight:700;text-transform:uppercase;
                        letter-spacing:0.1em;opacity:.45;margin-bottom:0.5rem;">
                EXPORT
            </div>
            <div style="font-size:0.88rem;opacity:.6;margin-bottom:0.9rem;line-height:1.45;">
                Download your fully personalised multi-page PDF career report with roadmap, projects & certs.
            </div>
        """, unsafe_allow_html=True)
        if pdf_bytes:
            st.download_button(
                "📥 Download PDF Report",
                data=pdf_bytes,
                file_name=f"CareerPilot_{role.replace(' ','_')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="dl_pdf_main"
            )
        else:
            st.caption("PDF unavailable — check logs.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # ── Tabs ─────────────────────────────────────────────────────────────────
    t1,t2,t3,t4,t5,t6,t7 = st.tabs([
        "📊 Overview", "🔍 Skill Gaps", "📅 Roadmap",
        "💻 Projects", "🎓 Certifications", "💬 Interview Prep",
        "🎯 Job Matcher"
    ])

    # ── TAB 1: Overview ───────────────────────────────────────────────────────
    with t1:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""
            <div class="g-card">
                <div class="g-card-title">
                    <div class="icon">📋</div> Profile Summary
                </div>
                <p style="font-size:0.97rem;line-height:1.65;color:var(--text-color);margin:0;">
                    {analysis.get('summary', '')}
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col_b:
            st.markdown('<div class="g-card"><div class="g-card-title"><div class="icon">⚖️</div> Strengths vs Gaps</div>', unsafe_allow_html=True)
            st.markdown("**🟢 What you bring**")
            for s in analysis.get("strengths", []):
                st.markdown(f'<div class="item-strength">✓ {s}</div>', unsafe_allow_html=True)
            if not analysis.get("strengths"):
                st.caption("No significant strengths detected.")
            st.markdown("<br/>", unsafe_allow_html=True)
            st.markdown("**🔴 What needs work**")
            for w in analysis.get("weaknesses", []):
                st.markdown(f'<div class="item-weakness">✗ {w}</div>', unsafe_allow_html=True)
            if not analysis.get("weaknesses"):
                st.caption("No major weaknesses detected.")
            st.markdown('</div>', unsafe_allow_html=True)

    # ── TAB 2: Skill Gaps ────────────────────────────────────────────────────
    with t2:
        gaps = analysis.get("skill_gaps", [])
        st.markdown(f"""
        <div class="g-card" style="margin-bottom:1.5rem;">
            <div class="g-card-title"><div class="icon">🔍</div> Missing Competencies</div>
            <p style="font-size:0.9rem;opacity:.65;margin-bottom:1rem;">
                These technologies and skills were not detected in your CV but are standard requirements for <strong>{role}</strong>.
            </p>
            <div>
        """, unsafe_allow_html=True)
        if gaps:
            for g in gaps:
                base = g.split(":")[0].split("–")[0].strip()
                st.markdown(f'<span class="chip">⚡ {base}</span>', unsafe_allow_html=True)
        else:
            st.success("✅ No skill gaps — perfect alignment!")
        st.markdown("</div></div>", unsafe_allow_html=True)

        if gaps:
            st.markdown("#### Detailed Breakdown")
            for g in gaps:
                st.markdown(f'<div class="gap-row"><span class="gap-dot">▸</span>{g}</div>', unsafe_allow_html=True)

    # ── TAB 3: Roadmap ───────────────────────────────────────────────────────
    with t3:
        rm = analysis.get("roadmap_30_60_90", {})
        phases = [
            ("30_day","DAYS 1–30","Foundation & Learning","#4f46e5","1",
             "Acquire core knowledge, close conceptual gaps, complete targeted online courses."),
            ("60_day","DAYS 31–60","Build & Apply","#0891b2","2",
             "Translate learning into working projects. Build demonstrable portfolio pieces."),
            ("90_day","DAYS 61–90","Portfolio, Network & Apply","#7c3aed","3",
             "Polish your portfolio, optimise your resume, start applying & practising interviews."),
        ]
        for key, phase_label, head, color, num, desc in phases:
            items = rm.get(key, [])
            st.markdown(f"""
            <div class="tl-item" style="--tl-color:{color};">
                <div class="tl-node" style="background:{color};">{num}</div>
                <div class="tl-phase">{phase_label}</div>
                <div class="tl-head">{head}</div>
                <p style="font-size:0.88rem;opacity:.6;margin-bottom:0.8rem;">{desc}</p>
            """, unsafe_allow_html=True)
            for step in items:
                st.markdown(f"- {step}")
            st.markdown("</div>", unsafe_allow_html=True)

    # ── TAB 4: Projects ──────────────────────────────────────────────────────
    with t4:
        projs = analysis.get("project_ideas", [])
        top_colors = ["#4f46e5", "#0891b2", "#7c3aed"]
        if projs:
            for i, p in enumerate(projs):
                diff = p.get("difficulty","Intermediate")
                diff_cls = {"Beginner":"diff-b","Intermediate":"diff-i","Advanced":"diff-a"}.get(diff,"diff-i")
                tech_chips = "".join(f'<span class="chip">{t}</span>' for t in p.get("technologies",[]))
                color = top_colors[i % len(top_colors)]
                st.markdown(f"""
                <div class="proj-card" style="border-top-color:{color};">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.5rem;">
                        <div class="proj-title">{p.get('title')}</div>
                        <span class="diff-badge {diff_cls}">{diff}</span>
                    </div>
                    <div class="proj-desc">{p.get('description')}</div>
                    <div style="font-size:0.78rem;font-weight:700;opacity:.45;
                                text-transform:uppercase;letter-spacing:.05em;margin-bottom:0.4rem;">
                        Stack
                    </div>
                    {tech_chips}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No project suggestions available.")

    # ── TAB 5: Certifications ────────────────────────────────────────────────
    with t5:
        certs = analysis.get("certifications", [])
        cert_icons = ["🎓","📜","🏆"]
        if certs:
            for i, c in enumerate(certs):
                st.markdown(f"""
                <div class="cert-card">
                    <div class="cert-icon">{cert_icons[i % 3]}</div>
                    <div>
                        <div class="cert-name">{c.get('name')}</div>
                        <div class="cert-provider">by {c.get('provider')}</div>
                        <div class="cert-reason">{c.get('reason')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No certifications suggested.")

    # ── TAB 6: Interview Prep ────────────────────────────────────────────────
    with t6:
        st.markdown(f"""
        <div class="g-card" style="margin-bottom:1.5rem;">
            <div class="g-card-title"><div class="icon">💬</div> Interview Preparation</div>
            <p style="font-size:0.9rem;opacity:.65;margin:0;">
                Curated Q&As tailored to your skill gaps and target role. Study these to maximise
                your interview performance.
            </p>
        </div>
        """, unsafe_allow_html=True)
        qas = analysis.get("interview_prep", [])
        if qas:
            for i, qa in enumerate(qas):
                with st.expander(f"Q{i+1}  ·  {qa.get('question')}", expanded=(i==0)):
                    st.markdown("**📝 Model Answer:**")
                    st.markdown(qa.get("answer",""))
        else:
            st.info("No interview Q&As available.")

    # ── TAB 7: Job Matcher ───────────────────────────────────────────────────
    with t7:
        st.markdown(f"""
        <div class="g-card" style="margin-bottom:1rem;">
            <div class="g-card-title"><div class="icon">🎯</div> Job Description Matcher</div>
            <p style="font-size:0.9rem;opacity:.65;margin:0;">
                Paste any job description below. The system will compare it against your parsed
                CV to calculate keyword fit, surface missing skills, and give tailoring tips.
            </p>
        </div>
        """, unsafe_allow_html=True)

        jd = st.text_area("Job Description", height=220,
                           placeholder="Paste the full job posting here...",
                           key="jd_input",
                           label_visibility="collapsed")
        match_clicked = st.button("🎯 Calculate Compatibility Score", key="jd_btn")

        if match_clicked:
            if not jd.strip():
                st.warning("Please paste a job description first.")
            else:
                with st.spinner("Analysing job posting alignment..."):
                    result = match_job_description(st.session_state.cv_text, jd, custom_key or None)
                    st.session_state.job_match_result = result

        if st.session_state.job_match_result:
            res    = st.session_state.job_match_result
            ms     = res.get("match_percentage", 0)
            mc     = "#22c55e" if ms>=80 else ("#eab308" if ms>=60 else "#ef4444")
            mbg    = "rgba(34,197,94,.1)" if ms>=80 else ("rgba(234,179,8,.1)" if ms>=60 else "rgba(239,68,68,.1)")

            st.markdown("<br/>", unsafe_allow_html=True)
            mc1, mc2 = st.columns([1,2])
            with mc1:
                st.markdown(f"""
                <div class="match-score-wrap">
                    <div class="match-num" style="color:{mc};background:{mbg};padding:0.5rem 1.5rem;border-radius:16px;">{ms}%</div>
                    <div class="match-label">Match Score</div>
                </div>
                """, unsafe_allow_html=True)
            with mc2:
                st.markdown(f"""
                <div class="g-card" style="height:100%;margin-bottom:0;">
                    <div class="g-card-title"><div class="icon">📊</div> Alignment Summary</div>
                    <p style="font-size:0.95rem;line-height:1.55;color:var(--text-color);margin:0;">
                        {res.get('summary','')}
                    </p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br/>", unsafe_allow_html=True)
            md1, md2 = st.columns(2)
            with md1:
                st.markdown("**🟢 Skills You Have**")
                for sk in res.get("matched_skills",[]):
                    st.markdown(f'<span class="chip chip-green">✓ {sk}</span>', unsafe_allow_html=True)
            with md2:
                st.markdown("**🔴 Missing Requirements**")
                for sk in res.get("missing_skills",[]):
                    st.markdown(f'<span class="chip chip-red">✗ {sk}</span>', unsafe_allow_html=True)

            st.markdown("**💡 Resume Tailoring Tips**")
            for tip in res.get("resume_tailoring_tips",[]):
                st.markdown(f"- {tip}")


# ═════════════════════════════════════════════════════════════════════════════
# LANDING PAGE (no analysis yet)
# ═════════════════════════════════════════════════════════════════════════════
else:
    st.markdown("""
    <div style="padding:1rem 0 0.5rem;">
        <h3 style="font-size:1.5rem;font-weight:700;margin-bottom:0.25rem;">
            What CareerPilot AI Does For You
        </h3>
        <p style="opacity:.55;font-size:0.95rem;margin-bottom:1.75rem;">
            Upload your CV and get a complete AI-powered career assessment in seconds.
        </p>
    </div>
    """, unsafe_allow_html=True)

    features = [
        ("🔍","Skill Gap Analysis","Extracts your competencies and cross-references them with target-role industry benchmarks."),
        ("📅","30-60-90 Day Roadmap","Structured daily action plan: what to learn, what to build, how to apply."),
        ("💻","Portfolio Projects","3 tailored real-world projects to fill your gaps and impress hiring managers."),
        ("💬","Interview Prep","Role-specific Q&As coached at FAANG standard to prepare you for tough technical screens."),
        ("🎯","Job Matcher","Paste any JD and see your exact keyword fit, missing skills & tailoring suggestions."),
        ("📥","PDF Export","Download a beautifully styled career report to keep, share, or print."),
    ]

    for row_start in range(0, len(features), 3):
        cols = st.columns(3)
        for i, col in enumerate(cols):
            if row_start + i < len(features):
                icon, title, desc = features[row_start + i]
                with col:
                    st.markdown(f"""
                    <div class="feat-card">
                        <div class="feat-icon">{icon}</div>
                        <div class="feat-title">{title}</div>
                        <div class="feat-desc">{desc}</div>
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:2.5rem;padding:2rem;border-radius:20px;text-align:center;
                background:linear-gradient(135deg,rgba(79,70,229,.08),rgba(6,182,212,.08));
                border:1px solid rgba(99,102,241,.12);">
        <div style="font-size:1.5rem;font-weight:700;margin-bottom:0.5rem;">
            Ready to accelerate your career? 🚀
        </div>
        <div style="font-size:0.95rem;opacity:.6;">
            Upload your CV in the sidebar → select your target role → click Analyze.
        </div>
    </div>
    """, unsafe_allow_html=True)
