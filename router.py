import anthropic

VALID_INTENTS = {"literature", "tools", "both"}


def route_intent(user_input: str, api_key: str) -> str:
    """
    Classify a user query into one of three intent categories.

    Args:
        user_input (str): The raw query string from the user.
        api_key (str):    Anthropic API key.

    Returns:
        str: One of 'literature', 'tools', or 'both' (lowercase).
             Falls back to 'both' if the model returns an unexpected value
             or if the API call fails.
    """
    client = anthropic.Anthropic(api_key=api_key)

    prompt = (
        "Classify this query. Reply with ONLY one word: literature, tools, or both.\n"
        "- literature = user wants papers or research findings\n"
        "- tools = user wants lab instrument recommendations\n"
        "- both = user wants papers AND instrument advice\n\n"
        f"Query: {user_input}"
    )

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=10,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )

        raw = ""
        for block in message.content:
            if hasattr(block, "text"):
                raw += block.text

        intent = raw.strip().lower()

        # Strip punctuation that might appear at end of single-word reply
        intent = intent.rstrip(".,!?;:")

        return intent if intent in VALID_INTENTS else "both"

    except Exception:
        return "both"


def synthesize_response(
    topic: str,
    lit_digest: str,
    tool_advice: str,
    api_key: str,
) -> str:
    """
    Combine a literature digest and tool recommendations into a single unified briefing.

    Args:
        topic (str):      The research topic or original user query.
        lit_digest (str): Markdown research digest produced by the literature agent.
        tool_advice (str): Plain-text or markdown tool recommendations from the tool selector.
        api_key (str):    Anthropic API key.

    Returns:
        str: A unified markdown research briefing as a plain text string.
             Returns a graceful error message if the API call fails.
    """
    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""You are an expert nanoscience research advisor. A researcher has asked about the following topic:

**Topic:** {topic}

You have been provided with two separate pieces of analysis:

---
### LITERATURE DIGEST
{lit_digest}

---
### CHARACTERISATION TOOL RECOMMENDATIONS
{tool_advice}

---

Your task is to merge these two inputs into ONE unified research briefing. \
Do not simply concatenate them — synthesise the information so the tool recommendations \
are directly tied to what the literature says. Use exactly the following markdown structure:

## Overview
Write exactly 2 sentences summarising what this topic is about and why it matters.

## Key Findings from Literature
Bullet-point summary of the most important results from the literature digest. \
Be specific and technical where the literature supports it.

## Recommended Characterisation Tools
For each recommended tool, explain WHY the literature supports using it for this topic. \
Link each tool to at least one finding or method mentioned in the literature digest. \
Use bullet points in the format:
- **[Tool Name]**: [Why this tool is relevant given what the literature shows]

## Actionable Next Steps
List exactly 2–3 concrete actions the researcher should take next, combining insights \
from both the literature and the tool recommendations. Number them 1, 2, 3. \
Each step should be specific enough to act on immediately.
"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )

        response_text = ""
        for block in message.content:
            if hasattr(block, "text"):
                response_text += block.text

        return response_text.strip()

    except anthropic.APIConnectionError:
        return (
            "## Error\n\n"
            "Could not connect to the Anthropic API. "
            "Please check your internet connection and try again."
        )
    except anthropic.AuthenticationError:
        return (
            "## Error\n\n"
            "Invalid Anthropic API key. "
            "Please verify your API key in the app settings."
        )
    except anthropic.RateLimitError:
        return (
            "## Error\n\n"
            "Anthropic API rate limit reached. "
            "Please wait a moment before generating another briefing."
        )
    except anthropic.APIStatusError as e:
        return (
            f"## Error\n\n"
            f"The Anthropic API returned an error (HTTP {e.status_code}). "
            "Please try again shortly."
        )
    except Exception as e:
        return (
            f"## Error\n\n"
            f"An unexpected error occurred while generating the briefing: {e}"
        )


if __name__ == "__main__":
    import os

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("Set the ANTHROPIC_API_KEY environment variable to run the smoke test.")
    else:
        # --- Test route_intent ---
        test_queries = [
            "What papers exist on SEM imaging of TiO2 nanoparticles?",
            "Which instrument should I use to measure thin film thickness?",
            "I want to study graphene — what tools and papers are relevant?",
        ]
        print("=== route_intent smoke test ===\n")
        for q in test_queries:
            intent = route_intent(q, api_key)
            print(f"Query : {q}")
            print(f"Intent: {intent}\n")

        # --- Test synthesize_response ---
        dummy_lit = (
            "## Key Findings\n- TiO2 films grown by ALD show columnar grain structure.\n"
            "- Grain widths of 8–15 nm measured by cross-sectional SEM.\n\n"
            "## Methods & Techniques\n- SEM with EDS for morphology and composition.\n"
            "- XRD for phase identification (anatase vs rutile).\n\n"
            "## Summary\nALD-grown TiO2 is well-characterised by electron microscopy "
            "and diffraction techniques."
        )
        dummy_tools = (
            "For thin film morphology, SEM is the recommended first tool. "
            "XRD is advised for crystalline phase identification. "
            "Ellipsometry can provide non-destructive thickness measurements."
        )

        print("=== synthesize_response smoke test ===\n")
        result = synthesize_response(
            topic="ALD-grown TiO2 thin films for photocatalysis",
            lit_digest=dummy_lit,
            tool_advice=dummy_tools,
            api_key=api_key,
        )
        print(result)