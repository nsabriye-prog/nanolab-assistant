import os
import glob
import anthropic

KNOWLEDGE_BASE_DIR = os.environ.get(
    "KNOWLEDGE_BASE_DIR",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge_base"),
)

_KB_CACHE: dict[str, str] = {}


def _load_knowledge_base() -> dict[str, str]:
    """Load all .txt files from the knowledge base directory into memory."""
    if _KB_CACHE:
        return _KB_CACHE

    pattern = os.path.join(KNOWLEDGE_BASE_DIR, "*.txt")
    files = glob.glob(pattern)

    if not files:
        print(
            f"[tools_agent] WARNING: No .txt files found in '{KNOWLEDGE_BASE_DIR}'. "
            "Set the KNOWLEDGE_BASE_DIR environment variable to your knowledge_base folder path."
        )
        return {}

    for filepath in files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                name = os.path.splitext(os.path.basename(filepath))[0]
                _KB_CACHE[name] = f.read()
        except Exception as e:
            print(f"[tools_agent] Could not read {filepath}: {e}")

    print(
        f"[tools_agent] Loaded {len(_KB_CACHE)} knowledge base files: "
        f"{list(_KB_CACHE.keys())}"
    )
    return _KB_CACHE


def _retrieve_relevant_chunks(question: str, kb: dict[str, str], top_k: int = 4) -> str:
    """
    Keyword-based retrieval — score each file by how many question words
    appear in its content, then return the top_k most relevant files.
    """
    question_words = set(question.lower().split())
    stopwords = {
        "a","an","the","is","are","was","were","be","been","being",
        "have","has","had","do","does","did","will","would","could",
        "should","may","might","shall","can","to","of","in","for",
        "on","with","at","by","from","as","it","its","this","that",
        "i","my","we","our","you","your","what","which","how","why",
        "and","or","but","if","so","not","no","any","all","more",
        "want","need","use","used","using","measure","measuring","sample",
    }
    keywords = question_words - stopwords

    scored = []
    for name, content in kb.items():
        content_lower = content.lower()
        score = sum(1 for kw in keywords if kw in content_lower)
        # Boost if keyword matches the tool filename itself
        if any(kw in name.lower() for kw in keywords):
            score += 3
        scored.append((score, name, content))

    scored.sort(reverse=True, key=lambda x: x[0])
    top = scored[:top_k]

    chunks = []
    for score, name, content in top:
        chunks.append(f"=== {name}.txt (relevance score: {score}) ===\n{content}")

    return "\n\n".join(chunks) if chunks else "No relevant tool files found."


def query_tool_selector(question: str, api_key: str = "") -> str:
    """
    Search the local knowledge base and use Claude to recommend
    the best characterisation tool for the user's question.

    This function is a drop-in replacement for the previous Flowise-based
    version. No external service or running Flowise instance is required.

    Args:
        question (str): The user's natural-language question about which
                        characterisation tool to use.
        api_key (str):  Anthropic API key. Falls back to ANTHROPIC_API_KEY
                        environment variable if not supplied.

    Returns:
        str: A structured tool recommendation string.
    """
    resolved_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
    if not resolved_key:
        return (
            "Tool selector is not configured. "
            "Please set the ANTHROPIC_API_KEY environment variable."
        )

    kb = _load_knowledge_base()
    if not kb:
        return (
            f"No knowledge base files found in: {KNOWLEDGE_BASE_DIR}\n\n"
            "Please make sure your 10 .txt files (SEM.txt, TEM.txt, etc.) "
            "are in a folder called 'knowledge_base' inside your project directory:\n"
            "  A:\\Projects\\Projects\\nanolab-assistant\\knowledge_base\\\n\n"
            "Or set the KNOWLEDGE_BASE_DIR environment variable to the correct path."
        )

    context = _retrieve_relevant_chunks(question, kb, top_k=4)

    prompt = f"""You are NanoTool Advisor, an expert who helps researchers choose the right \
nanoscale characterisation tool. Use ONLY the tool data sheets provided below to answer.

TOOL DATA SHEETS:
{context}

USER QUESTION:
{question}

Based strictly on the data sheets above, provide your recommendation using EXACTLY this format:

RECOMMENDED TOOL: [tool name and abbreviation]
WHY THIS TOOL: [2-3 sentences explaining why this tool matches the user's need]
SAMPLE PREP: [numbered list of 2-4 preparation steps]
EXPECTED OUTPUT: [1-2 sentences describing what the user will see or receive]
ALTERNATIVE IF UNAVAILABLE: [one alternative tool name and one sentence why]

Be specific, accurate, and friendly. If no tool in the data sheets is a good match, say so clearly."""

    try:
        client = anthropic.Anthropic(api_key=resolved_key)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        response_text = ""
        for block in message.content:
            if hasattr(block, "text"):
                response_text += block.text
        return response_text.strip() or "No recommendation returned."

    except anthropic.APIConnectionError:
        return (
            "Could not connect to the Anthropic API. "
            "Please check your internet connection and try again."
        )
    except anthropic.AuthenticationError:
        return (
            "Invalid Anthropic API key. "
            "Please verify your ANTHROPIC_API_KEY is correct."
        )
    except anthropic.RateLimitError:
        return "Rate limit reached — please wait a moment and try again."
    except Exception as e:
        return f"An unexpected error occurred in the tool selector: {e}"


if __name__ == "__main__":
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        print("Set the ANTHROPIC_API_KEY environment variable to run the smoke test.")
    else:
        tests = [
            "I have a silicon wafer and want to measure surface roughness",
            "I need to identify crystalline phases in my powder sample",
            "Which tool measures the top 10 nm of surface chemistry?",
        ]
        for q in tests:
            print(f"\nQuestion: {q}")
            print("-" * 60)
            print(query_tool_selector(q, key))
            print()