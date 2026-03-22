import os
import time
import requests
import xml.etree.ElementTree as ET


def search_arxiv(topic, max_results=5):
    """
    Search ArXiv for papers matching the given topic.

    Args:
        topic (str): Search query string.
        max_results (int): Maximum number of results to return (default 5).

    Returns:
        list[dict]: Each dict contains:
            - title (str)
            - abstract (str)
            - url (str)
            - authors (list[str])  — up to 3
            - source (str)         — always 'ArXiv'
    """
    base_url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{topic}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }

    try:
        response = requests.get(base_url, params=params, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[ArXiv] Request failed: {e}")
        return []

    namespace = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }

    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        print(f"[ArXiv] XML parse error: {e}")
        return []

    results = []
    for entry in root.findall("atom:entry", namespace):
        title_el = entry.find("atom:title", namespace)
        summary_el = entry.find("atom:summary", namespace)
        id_el = entry.find("atom:id", namespace)

        title = title_el.text.strip().replace("\n", " ") if title_el is not None else ""
        abstract = summary_el.text.strip().replace("\n", " ") if summary_el is not None else ""
        url = id_el.text.strip() if id_el is not None else ""

        # Prefer the HTML abstract page over the raw API id when possible
        if url.startswith("http://arxiv.org/abs/") or url.startswith("https://arxiv.org/abs/"):
            pass  # already in the right format
        elif "/abs/" not in url:
            # Convert API-style id to abstract page URL
            arxiv_id = url.split("/")[-1]
            url = f"https://arxiv.org/abs/{arxiv_id}"

        author_els = entry.findall("atom:author", namespace)
        authors = []
        for author_el in author_els[:3]:
            name_el = author_el.find("atom:name", namespace)
            if name_el is not None and name_el.text:
                authors.append(name_el.text.strip())

        if title:
            results.append(
                {
                    "title": title,
                    "abstract": abstract,
                    "url": url,
                    "authors": authors,
                    "source": "ArXiv",
                }
            )

    return results


def search_semantic_scholar(topic, max_results=5):
    """
    Search Semantic Scholar for papers matching the given topic.

    Automatically retries up to 3 times with exponential backoff on 429 rate-limit
    responses. Reads an optional API key from the SEMANTIC_SCHOLAR_API_KEY
    environment variable to increase rate limits (free key available at
    https://www.semanticscholar.org/product/api).

    Args:
        topic (str): Search query string.
        max_results (int): Maximum number of results to return (default 5).

    Returns:
        list[dict]: Each dict contains:
            - title (str)
            - abstract (str)
            - url (str)
            - authors (list[str])  — up to 3
            - source (str)         — always 'Semantic Scholar'

    Papers without abstracts are skipped.
    Returns an empty list (never raises) so callers can always continue with
    ArXiv-only results if Semantic Scholar is unavailable.
    """
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": topic,
        "limit": min(max_results * 2, 100),  # fetch extra to allow skipping abstract-less papers
        "fields": "title,abstract,authors,url",
    }

    headers = {
        "Accept": "application/json",
        "User-Agent": "NanoLabAssistant/1.0",
    }

    # Optional free API key — raises the default rate limit significantly.
    # Get one at: https://www.semanticscholar.org/product/api
    ss_api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "").strip()
    if ss_api_key:
        headers["x-api-key"] = ss_api_key

    max_attempts = 3

    for attempt in range(max_attempts):
        try:
            response = requests.get(base_url, params=params, headers=headers, timeout=15)

            # ── Handle 429 Rate Limit with exponential backoff ──────────────
            if response.status_code == 429:
                wait_seconds = 2 ** attempt  # 1 s, 2 s, 4 s
                print(
                    f"[Semantic Scholar] Rate limited (429). "
                    f"Waiting {wait_seconds}s before retry "
                    f"{attempt + 1}/{max_attempts}…"
                )
                time.sleep(wait_seconds)
                continue  # retry

            response.raise_for_status()  # raise on any other 4xx / 5xx

        except requests.RequestException as e:
            print(f"[Semantic Scholar] Request failed: {e}")
            return []  # non-429 network/HTTP error — don't retry

        # ── Parse JSON ────────────────────────────────────────────────────
        try:
            data = response.json()
        except ValueError as e:
            print(f"[Semantic Scholar] JSON parse error: {e}")
            return []

        papers = data.get("data", [])
        results = []

        for paper in papers:
            if len(results) >= max_results:
                break

            abstract = (paper.get("abstract") or "").strip()
            if not abstract:
                continue  # skip papers without abstracts

            title = (paper.get("title") or "").strip()
            url = (paper.get("url") or "").strip()

            # Fall back to constructing a URL from paperId if the url field is empty
            if not url:
                paper_id = paper.get("paperId", "")
                if paper_id:
                    url = f"https://www.semanticscholar.org/paper/{paper_id}"

            raw_authors = paper.get("authors") or []
            authors = [
                a["name"].strip()
                for a in raw_authors[:3]
                if isinstance(a, dict) and a.get("name")
            ]

            if title:
                results.append(
                    {
                        "title": title,
                        "abstract": abstract,
                        "url": url,
                        "authors": authors,
                        "source": "Semantic Scholar",
                    }
                )

        return results  # success — return immediately

    # All retry attempts exhausted (only reachable after 3× 429 responses)
    print(
        "[Semantic Scholar] All retry attempts exhausted after repeated rate limiting. "
        "Returning empty results. Tip: set the SEMANTIC_SCHOLAR_API_KEY environment "
        "variable for a higher rate limit (free key at semanticscholar.org/product/api)."
    )
    return []


if __name__ == "__main__":
    # Quick smoke-test for both functions
    test_topic = "SEM characterization thin films"

    print("=" * 60)
    print(f"ArXiv results for: '{test_topic}'")
    print("=" * 60)
    arxiv_results = search_arxiv(test_topic, max_results=3)
    for i, paper in enumerate(arxiv_results, 1):
        print(f"\n[{i}] {paper['title']}")
        print(f"    Authors : {', '.join(paper['authors']) or 'N/A'}")
        print(f"    URL     : {paper['url']}")
        print(f"    Abstract: {paper['abstract'][:120]}...")
        print(f"    Source  : {paper['source']}")

    print("\n" + "=" * 60)
    print(f"Semantic Scholar results for: '{test_topic}'")
    print("=" * 60)
    ss_results = search_semantic_scholar(test_topic, max_results=3)
    for i, paper in enumerate(ss_results, 1):
        print(f"\n[{i}] {paper['title']}")
        print(f"    Authors : {', '.join(paper['authors']) or 'N/A'}")
        print(f"    URL     : {paper['url']}")
        print(f"    Abstract: {paper['abstract'][:120]}...")
        print(f"    Source  : {paper['source']}")