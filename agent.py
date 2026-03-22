import anthropic


def run_research_agent(topic: str, papers: list[dict], api_key: str) -> str:
    """
    Generate a structured research digest for a given topic using a list of papers.

    Args:
        topic (str): The research topic or query the user is investigating.
        papers (list[dict]): List of paper dicts, each containing:
            - title (str)
            - abstract (str)
            - url (str)
            - authors (list[str])
            - source (str)
        api_key (str): Anthropic API key.

    Returns:
        str: Markdown-formatted research digest produced by Claude.
    """
    client = anthropic.Anthropic(api_key=api_key)

    # Cap at 10 papers and truncate each abstract to 800 characters
    selected_papers = papers[:10]

    if not selected_papers:
        return (
            "## Summary\n\nNo papers were provided. "
            "Please run a literature search before generating a research digest."
        )

    # Build the numbered paper block for the prompt
    paper_lines = []
    for i, paper in enumerate(selected_papers, 1):
        title = (paper.get("title") or "Untitled").strip()
        abstract = (paper.get("abstract") or "No abstract available.").strip()
        url = (paper.get("url") or "No URL").strip()
        authors = paper.get("authors") or []
        source = (paper.get("source") or "Unknown").strip()

        abstract_truncated = abstract[:800] + ("..." if len(abstract) > 800 else "")
        authors_str = ", ".join(authors) if authors else "Authors not listed"

        paper_lines.append(
            f"[{i}] Title: {title}\n"
            f"    Authors: {authors_str}\n"
            f"    Source: {source}\n"
            f"    URL: {url}\n"
            f"    Abstract: {abstract_truncated}"
        )

    papers_block = "\n\n".join(paper_lines)

    prompt = f"""You are an expert nanoscience and materials characterization researcher. \
A user is investigating the following topic:

**Topic:** {topic}

Below are up to {len(selected_papers)} recent papers retrieved from ArXiv and Semantic Scholar. \
Read them carefully and produce a concise, technically accurate research digest strictly \
following the markdown structure specified below. Do not add extra top-level sections.

---
{papers_block}
---

Write the research digest now using exactly these five markdown sections:

## Key Findings
Summarise the most important scientific results and conclusions across the papers. \
Use bullet points. Be specific — include numbers, materials, or techniques where relevant.

## Methods & Techniques
Describe the experimental, computational, or analytical methods used across the papers. \
Group related approaches together. Use bullet points.

## Open Questions
Identify gaps, unresolved problems, or areas of active debate highlighted by the papers. \
Use bullet points.

## Recommended Papers
List the top 3 most relevant or impactful papers from the set above. \
For each, provide the title, authors, and URL in this exact format:

1. **[Title]** — [Authors] — [URL]
2. **[Title]** — [Authors] — [URL]
3. **[Title]** — [Authors] — [URL]

## Summary
Write 3–5 sentences giving a high-level overview of the state of research on this topic \
based on the papers above. This should be accessible to a graduate student new to the field.
"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )

    # Extract the text content from the response
    response_text = ""
    for block in message.content:
        if hasattr(block, "text"):
            response_text += block.text

    return response_text.strip()


if __name__ == "__main__":
    import os

    # Minimal smoke-test with two synthetic papers
    dummy_papers = [
        {
            "title": "High-Resolution SEM Characterisation of TiO2 Thin Films",
            "abstract": (
                "We report scanning electron microscopy studies of TiO2 thin films "
                "deposited by atomic layer deposition at 200°C. Films of 20–100 nm "
                "thickness were characterised for grain size, surface roughness, and "
                "crystallinity. Cross-sectional imaging revealed columnar growth with "
                "grain widths of 8–15 nm. EDS confirmed stoichiometric Ti:O ratios "
                "within 2% across all samples."
            ),
            "url": "https://arxiv.org/abs/2401.00001",
            "authors": ["A. Smith", "B. Jones"],
            "source": "ArXiv",
        },
        {
            "title": "AFM Nanomechanical Mapping of ALD Oxide Films",
            "abstract": (
                "Atomic force microscopy in PeakForce Tapping mode was used to map "
                "the Young's modulus of Al2O3 and HfO2 films grown by ALD. Modulus "
                "values of 165 ± 12 GPa and 210 ± 18 GPa were obtained respectively, "
                "consistent with bulk values. Surface roughness (Rq) remained below "
                "0.3 nm for films up to 50 nm thick."
            ),
            "url": "https://www.semanticscholar.org/paper/example123",
            "authors": ["C. Lee", "D. Patel", "E. Nguyen"],
            "source": "Semantic Scholar",
        },
    ]

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("Set the ANTHROPIC_API_KEY environment variable to run the smoke test.")
    else:
        result = run_research_agent(
            topic="SEM and AFM characterisation of ALD thin films",
            papers=dummy_papers,
            api_key=api_key,
        )
        print(result)