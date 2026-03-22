import streamlit as st
import os

from search import search_arxiv, search_semantic_scholar
from agent import run_research_agent
from tools_agent import query_tool_selector
from router import route_intent, synthesize_response
from wafer_journey import render_wafer_journey
from nano_chatbot import render_nano_chatbot

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="NanoLab Assistant",
    page_icon="🔬",
    layout="centered",
)

# ---------------------------------------------------------------------------
# API key
# ---------------------------------------------------------------------------

try:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

# ---------------------------------------------------------------------------
# Global CSS
# ---------------------------------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Tab labels */
button[data-baseweb="tab"] {
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
}

/* Primary buttons */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #185FA5, #2a82d8);
    color: white;
    border: none;
    border-radius: 10px;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    padding: 10px 28px;
    transition: opacity 0.15s ease;
}
.stButton > button[kind="primary"]:hover { opacity: 0.88; }

/* Secondary buttons */
.stButton > button {
    font-family: 'Space Mono', monospace;
    border-radius: 10px;
}

/* Download button */
.stDownloadButton > button {
    font-family: 'Space Mono', monospace;
    border-radius: 10px;
    font-weight: 700;
}

/* Info/success/warning boxes */
.stAlert {
    border-radius: 10px;
}

/* Paper card styling */
.paper-card {
    background: #f8faff;
    border: 1.5px solid #dce8ff;
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 10px;
}
.paper-title {
    font-weight: 600;
    font-size: 0.93rem;
    color: #1a2e6e;
    margin-bottom: 4px;
}
.paper-meta {
    font-size: 0.78rem;
    color: #666;
    margin-bottom: 6px;
}
.paper-abstract {
    font-size: 0.82rem;
    color: #444;
    line-height: 1.55;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Guard: warn if no API key
# ---------------------------------------------------------------------------

if not api_key:
    st.warning(
        "⚠️ No Anthropic API key found. "
        "Set `ANTHROPIC_API_KEY` in your Streamlit secrets or environment variables. "
        "The Research Assistant and Chat tabs require it.",
        icon="⚠️",
    )

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab1, tab2, tab3 = st.tabs(["🔬 Research Assistant", "💿 Wafer Journey", "🤖 Chat with Nano"])

# ===========================================================================
# TAB 1 — Research Assistant
# ===========================================================================

with tab1:
    st.title("🔬 NanoLab Assistant")
    st.caption(
        "Ask a research question about nanotechnology, wafer fabrication, or "
        "characterisation tools. The assistant will search ArXiv & Semantic Scholar, "
        "analyse the literature, and recommend the right instruments."
    )

    st.markdown("---")

    # ── Query input ──────────────────────────────────────────────────────
    query = st.text_area(
        "Research query",
        height=120,
        placeholder=(
            "e.g. 'What are the latest techniques for measuring thin film thickness "
            "in ALD-grown HfO2, and which characterisation tools should I use?' "
            "\n\nor: 'I want to study dopant profiles in silicon — which instrument "
            "gives the best depth resolution?'"
        ),
        label_visibility="collapsed",
    )

    col_btn, col_spacer = st.columns([2, 5])
    with col_btn:
        analyse_clicked = st.button("🔍 Analyse", type="primary", use_container_width=True)

    # ── Session state for results ─────────────────────────────────────────
    if "last_query" not in st.session_state:
        st.session_state.last_query = ""
    if "last_report" not in st.session_state:
        st.session_state.last_report = ""
    if "last_intent" not in st.session_state:
        st.session_state.last_intent = ""
    if "last_papers" not in st.session_state:
        st.session_state.last_papers = []
    if "last_tool_advice" not in st.session_state:
        st.session_state.last_tool_advice = ""
    if "last_lit_digest" not in st.session_state:
        st.session_state.last_lit_digest = ""

    # ── Main analysis pipeline ────────────────────────────────────────────
    if analyse_clicked:
        raw_query = query.strip()
        if not raw_query:
            st.warning("Please enter a research query before clicking Analyse.")
        elif not api_key:
            st.error("No API key configured — cannot run analysis.")
        else:
            st.session_state.last_query = raw_query
            st.session_state.last_report = ""
            st.session_state.last_papers = []
            st.session_state.last_tool_advice = ""
            st.session_state.last_lit_digest = ""

            # ── Step 1: Route intent ──────────────────────────────────────
            with st.spinner("Classifying your query…"):
                intent = route_intent(raw_query, api_key)
                st.session_state.last_intent = intent

            intent_labels = {
                "literature": "📚 Literature search",
                "tools": "🔧 Tool recommendation",
                "both": "📚🔧 Literature + Tool recommendation",
            }
            st.info(
                f"**Detected mode:** {intent_labels.get(intent, intent.capitalize())}",
                icon="🧭",
            )

            papers = []
            lit_digest = ""
            tool_advice = ""

            # ── Step 2a: Literature path ──────────────────────────────────
            if intent in ("literature", "both"):
                with st.spinner("Searching ArXiv and Semantic Scholar…"):
                    arxiv_results = search_arxiv(raw_query, max_results=5)
                    ss_results = search_semantic_scholar(raw_query, max_results=5)
                    papers = arxiv_results + ss_results
                    st.session_state.last_papers = papers

                if papers:
                    st.success(
                        f"Found **{len(papers)} papers** "
                        f"({len(arxiv_results)} ArXiv · {len(ss_results)} Semantic Scholar). "
                        "Generating research digest…"
                    )
                    with st.spinner("Analysing literature with Claude…"):
                        lit_digest = run_research_agent(raw_query, papers, api_key)
                        st.session_state.last_lit_digest = lit_digest
                else:
                    st.warning(
                        "No papers found for this query. "
                        "Try broadening the search terms."
                    )

            # ── Step 2b: Tool selector path ───────────────────────────────
            if intent in ("tools", "both"):
                with st.spinner("Querying NanoLab tool selector…"):
                    tool_advice = query_tool_selector(raw_query, api_key)
                    st.session_state.last_tool_advice = tool_advice

            # ── Step 3: Synthesize if both ────────────────────────────────
            if intent == "both" and lit_digest and tool_advice:
                with st.spinner("Synthesizing unified briefing…"):
                    combined = synthesize_response(
                        raw_query, lit_digest, tool_advice, api_key
                    )
                    st.session_state.last_report = combined

            elif intent == "literature":
                st.session_state.last_report = lit_digest

            elif intent == "tools":
                st.session_state.last_report = tool_advice

    # ── Display results (persists across reruns) ──────────────────────────
    intent = st.session_state.last_intent
    papers = st.session_state.last_papers
    lit_digest = st.session_state.last_lit_digest
    tool_advice = st.session_state.last_tool_advice
    report = st.session_state.last_report

    if intent and report:
        st.markdown("---")

        # ── BOTH: show combined briefing ──────────────────────────────────
        if intent == "both":
            st.markdown("## 📋 Unified Research Briefing")
            st.markdown(report)

            # Expandable raw sections
            if papers:
                with st.expander(f"📄 Source papers ({len(papers)} found)", expanded=False):
                    for i, p in enumerate(papers, 1):
                        authors_str = ", ".join(p.get("authors") or []) or "Authors not listed"
                        abstract_preview = (p.get("abstract") or "")[:300]
                        if len(p.get("abstract", "")) > 300:
                            abstract_preview += "…"
                        st.markdown(
                            f'<div class="paper-card">'
                            f'<div class="paper-title">[{i}] {p.get("title","Untitled")}</div>'
                            f'<div class="paper-meta">{authors_str} · '
                            f'<span style="color:#185FA5">{p.get("source","")}</span></div>'
                            f'<div class="paper-abstract">{abstract_preview}</div>'
                            f'<div style="margin-top:6px;">'
                            f'<a href="{p.get("url","#")}" target="_blank" '
                            f'style="font-size:0.78rem; color:#185FA5;">🔗 View paper</a></div>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

            if tool_advice:
                with st.expander("🔧 Raw tool recommendation", expanded=False):
                    st.markdown(tool_advice)

        # ── LITERATURE ONLY ───────────────────────────────────────────────
        elif intent == "literature":
            st.markdown("## 📚 Research Digest")
            st.markdown(report)

            if papers:
                st.markdown("### 📄 Source Papers")
                for i, p in enumerate(papers, 1):
                    authors_str = ", ".join(p.get("authors") or []) or "Authors not listed"
                    abstract_preview = (p.get("abstract") or "")[:300]
                    if len(p.get("abstract", "")) > 300:
                        abstract_preview += "…"
                    st.markdown(
                        f'<div class="paper-card">'
                        f'<div class="paper-title">[{i}] {p.get("title","Untitled")}</div>'
                        f'<div class="paper-meta">{authors_str} · '
                        f'<span style="color:#185FA5">{p.get("source","")}</span></div>'
                        f'<div class="paper-abstract">{abstract_preview}</div>'
                        f'<div style="margin-top:6px;">'
                        f'<a href="{p.get("url","#")}" target="_blank" '
                        f'style="font-size:0.78rem; color:#185FA5;">🔗 View paper</a></div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

        # ── TOOLS ONLY ────────────────────────────────────────────────────
        elif intent == "tools":
            st.markdown("## 🔧 Tool Recommendation")
            st.markdown(report)

        # ── Download button ───────────────────────────────────────────────
        if report:
            st.markdown("---")

            query_header = (
                f"NanoLab Assistant Report\n"
                f"{'=' * 50}\n"
                f"Query: {st.session_state.last_query}\n"
                f"Mode:  {intent.capitalize()}\n"
                f"{'=' * 50}\n\n"
            )

            papers_section = ""
            if papers:
                papers_section = "\n\nSOURCE PAPERS\n" + "-" * 40 + "\n"
                for i, p in enumerate(papers, 1):
                    authors_str = ", ".join(p.get("authors") or []) or "N/A"
                    papers_section += (
                        f"\n[{i}] {p.get('title', 'Untitled')}\n"
                        f"    Authors : {authors_str}\n"
                        f"    Source  : {p.get('source', '')}\n"
                        f"    URL     : {p.get('url', '')}\n"
                        f"    Abstract: {(p.get('abstract') or '')[:400]}{'…' if len(p.get('abstract','')) > 400 else ''}\n"
                    )

            tool_section = ""
            if tool_advice and intent == "both":
                tool_section = f"\n\nRAW TOOL RECOMMENDATION\n{'-' * 40}\n{tool_advice}\n"

            full_report_txt = query_header + report + papers_section + tool_section

            st.download_button(
                label="⬇️ Download report as .txt",
                data=full_report_txt,
                file_name="nanolab_report.txt",
                mime="text/plain",
                use_container_width=False,
            )

# ===========================================================================
# TAB 2 — Wafer Journey
# ===========================================================================

with tab2:
    render_wafer_journey()

# ===========================================================================
# TAB 3 — Chat with Nano
# ===========================================================================

with tab3:
    render_nano_chatbot(api_key)