import streamlit as st
import os

from search import search_arxiv, search_semantic_scholar
from agent import run_research_agent
from tools_agent import query_tool_selector
from router import route_intent, synthesize_response
from wafer_journey import render_wafer_journey
from nano_chatbot import render_nano_chatbot, get_global_background_css

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="NanoLab Assistant",
    page_icon="🔬",
    layout="centered",
)

# ---------------------------------------------------------------------------
# Global backgrounds + CSS (dark teal molecular aesthetic)
# ---------------------------------------------------------------------------

st.markdown(get_global_background_css(), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# API key
# ---------------------------------------------------------------------------

try:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

# ---------------------------------------------------------------------------
# API key guard
# ---------------------------------------------------------------------------

if not api_key:
    st.warning(
        "No Anthropic API key found. "
        "Set ANTHROPIC_API_KEY in your Streamlit secrets or environment variables.",
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
        "characterisation tools. The assistant searches ArXiv & Semantic Scholar, "
        "analyses the literature, and recommends the right instruments."
    )

    st.markdown("---")

    query = st.text_area(
        "Research query",
        height=120,
        placeholder=(
            "e.g. 'What are the latest techniques for measuring thin film thickness "
            "in ALD-grown HfO2, and which characterisation tools should I use?'\n\n"
            "or: 'I want to study dopant profiles in silicon — which instrument "
            "gives the best depth resolution?'"
        ),
        label_visibility="collapsed",
    )

    col_btn, col_spacer = st.columns([2, 5])
    with col_btn:
        analyse_clicked = st.button("🔍 Analyse", type="primary", use_container_width=True)

    # Session state
    for key in ["last_query", "last_report", "last_intent", "last_papers",
                "last_tool_advice", "last_lit_digest"]:
        if key not in st.session_state:
            st.session_state[key] = "" if key != "last_papers" else []

    if analyse_clicked:
        raw_query = query.strip()
        if not raw_query:
            st.warning("Please enter a research query before clicking Analyse.")
        elif not api_key:
            st.error("No API key configured — cannot run analysis.")
        else:
            st.session_state.last_query = raw_query
            for k in ["last_report", "last_tool_advice", "last_lit_digest"]:
                st.session_state[k] = ""
            st.session_state.last_papers = []

            with st.spinner("Classifying your query…"):
                intent = route_intent(raw_query, api_key)
                st.session_state.last_intent = intent

            intent_labels = {
                "literature": "📚 Literature search",
                "tools": "🔧 Tool recommendation",
                "both": "📚🔧 Literature + Tool recommendation",
            }
            st.info(f"**Detected mode:** {intent_labels.get(intent, intent.capitalize())}", icon="🧭")

            papers, lit_digest, tool_advice = [], "", ""

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
                    st.warning("No papers found. Try broadening the search terms.")

            if intent in ("tools", "both"):
                with st.spinner("Querying NanoLab tool selector…"):
                    tool_advice = query_tool_selector(raw_query, api_key)
                    st.session_state.last_tool_advice = tool_advice

            if intent == "both" and lit_digest and tool_advice:
                with st.spinner("Synthesizing unified briefing…"):
                    combined = synthesize_response(raw_query, lit_digest, tool_advice, api_key)
                    st.session_state.last_report = combined
            elif intent == "literature":
                st.session_state.last_report = lit_digest
            elif intent == "tools":
                st.session_state.last_report = tool_advice

    # Display results
    intent = st.session_state.last_intent
    papers = st.session_state.last_papers
    lit_digest = st.session_state.last_lit_digest
    tool_advice = st.session_state.last_tool_advice
    report = st.session_state.last_report

    if intent and report:
        st.markdown("---")

        if intent == "both":
            st.markdown("## 📋 Unified Research Briefing")
            st.markdown(report)
            if papers:
                with st.expander(f"📄 Source papers ({len(papers)} found)", expanded=False):
                    for i, p in enumerate(papers, 1):
                        authors_str = ", ".join(p.get("authors") or []) or "Authors not listed"
                        abstract_preview = (p.get("abstract") or "")[:300]
                        if len(p.get("abstract", "")) > 300:
                            abstract_preview += "…"
                        st.markdown(
                            f"**[{i}] {p.get('title','Untitled')}**\n\n"
                            f"*{authors_str}* · {p.get('source','')}  \n"
                            f"{abstract_preview}  \n"
                            f"[View paper]({p.get('url','#')})"
                        )
            if tool_advice:
                with st.expander("🔧 Raw tool recommendation", expanded=False):
                    st.markdown(tool_advice)

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
                        f"**[{i}] {p.get('title','Untitled')}**\n\n"
                        f"*{authors_str}* · {p.get('source','')}  \n"
                        f"{abstract_preview}  \n"
                        f"[View paper]({p.get('url','#')})"
                    )

        elif intent == "tools":
            st.markdown("## 🔧 Tool Recommendation")
            st.markdown(report)

        if report:
            st.markdown("---")
            query_header = (
                f"NanoLab Assistant Report\n{'='*50}\n"
                f"Query: {st.session_state.last_query}\n"
                f"Mode:  {intent.capitalize()}\n{'='*50}\n\n"
            )
            papers_section = ""
            if papers:
                papers_section = "\n\nSOURCE PAPERS\n" + "-"*40 + "\n"
                for i, p in enumerate(papers, 1):
                    authors_str = ", ".join(p.get("authors") or []) or "N/A"
                    papers_section += (
                        f"\n[{i}] {p.get('title','Untitled')}\n"
                        f"    Authors : {authors_str}\n"
                        f"    Source  : {p.get('source','')}\n"
                        f"    URL     : {p.get('url','')}\n"
                        f"    Abstract: {(p.get('abstract') or '')[:400]}"
                        f"{'…' if len(p.get('abstract',''))>400 else ''}\n"
                    )
            tool_section = ""
            if tool_advice and intent == "both":
                tool_section = f"\n\nRAW TOOL RECOMMENDATION\n{'-'*40}\n{tool_advice}\n"

            st.download_button(
                label="⬇️ Download report as .txt",
                data=query_header + report + papers_section + tool_section,
                file_name="nanolab_report.txt",
                mime="text/plain",
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