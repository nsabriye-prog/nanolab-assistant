import streamlit as st
import streamlit.components.v1 as components
import anthropic
import os

# ---------------------------------------------------------------------------
# Character definitions
# ---------------------------------------------------------------------------

CHARACTERS = {
    "Professor Nova": {
        "label": "Professor Nova",
        "color": "#4A90D9",
        "bg": "#E8F4FF",
        "bubble": "#D6ECFF",
        "greeting": (
            "Hoot hoot! Welcome to NanoLab! I'm Professor Nova — your wise owl guide "
            "to the microscopic world. Whether it's wafer fabrication, quantum dots, "
            "or characterisation tools, I've perched in the cleanroom long enough "
            "to know the answers. What tiny mystery shall we explore today?"
        ),
        "system": (
            "You are Professor Nova, a warm and encouraging owl professor who teaches "
            "nanotechnology, wafer fabrication, and characterisation tools (SEM, TEM, "
            "AFM, XRD, XPS, SIMS, Raman, ellipsometry, FTIR, 4-point probe). "
            "Speak with warmth and gentle humour. Use simple analogies. "
            "Give accurate, friendly answers under 120 words. "
            "Always end with exactly one curious follow-up question."
        ),
        "anim": "OWL",
        "voice_pitch": 1.1,
        "voice_rate": 0.88,
    },
    "Dr Foxy": {
        "label": "Dr Foxy",
        "color": "#E07B2A",
        "bg": "#FFF4EC",
        "bubble": "#FFE8D0",
        "greeting": (
            "Hey! Dr Foxy here — lab scientist and nanofab enthusiast. "
            "I have spent more hours in a cleanroom than outside one, so ask me "
            "anything: deposition, etching, lithography, or characterisation. "
            "I give you the real-world lab perspective. What are you working on?"
        ),
        "system": (
            "You are Dr Foxy, an energetic fox scientist specialising in nanofabrication: "
            "thin film deposition, lithography, etching, annealing, and characterisation "
            "(SEM, TEM, AFM, XRD, XPS, SIMS, Raman, ellipsometry, FTIR, 4-point probe). "
            "Speak with quick wit and practical insight. Be friendly and technically precise. "
            "Keep replies under 120 words. Always end with one follow-up question."
        ),
        "anim": "FOX",
        "voice_pitch": 1.0,
        "voice_rate": 0.95,
    },
    "Pixel": {
        "label": "Pixel",
        "color": "#7B52C4",
        "bg": "#F5EEFF",
        "bubble": "#EAD9FF",
        "greeting": (
            "Mrrrow! I am Pixel, NanoLab's most curious cat. I love exploring the "
            "weird and wonderful world of nanoscale materials. Crystal structures, "
            "surface chemistry, how an AFM tip works — let us sniff it out together! "
            "What has your curiosity piqued today?"
        ),
        "system": (
            "You are Pixel, a curious and playful purple cat who loves nanotechnology, "
            "materials science, and characterisation tools (SEM, TEM, AFM, XRD, XPS, "
            "SIMS, Raman, ellipsometry, FTIR, 4-point probe). "
            "Use a warm tone with occasional cat mannerisms. Make topics approachable and fun. "
            "Keep replies under 120 words. Always end with one follow-up question."
        ),
        "anim": "CAT",
        "voice_pitch": 1.15,
        "voice_rate": 0.90,
    },
    "Nano": {
        "label": "Nano",
        "color": "#1A9E6A",
        "bg": "#E4FFF4",
        "bubble": "#CDFAEB",
        "greeting": (
            "BEEP BOOP — Nano online! I am your robotic NanoLab assistant, "
            "optimised for precise answers on nanotechnology, semiconductor "
            "fabrication, and analytical instrumentation. My databanks contain "
            "specifications for SEM, TEM, AFM, XRD, XPS, SIMS, Raman, "
            "ellipsometry, FTIR, and 4-point probe. How can I assist you today?"
        ),
        "system": (
            "You are Nano, a friendly robot assistant in a NanoLab specialising in "
            "nanotechnology, semiconductor wafer fabrication, and characterisation "
            "instruments (SEM, TEM, AFM, XRD, XPS, SIMS, Raman, ellipsometry, "
            "FTIR, 4-point probe). Speak with precision and occasional robot flair. "
            "Keep replies under 120 words. Always end with one follow-up question."
        ),
        "anim": "ROBOT",
        "voice_pitch": 0.85,
        "voice_rate": 0.92,
    },
}

STARTER_QUESTIONS = [
    "What is the difference between SEM and TEM?",
    "How does atomic layer deposition work?",
    "Why do we clean a wafer before depositing a film?",
    "What does an AFM actually measure?",
    "How small can lithography features get today?",
]

# ---------------------------------------------------------------------------
# Background CSS — molecular network aesthetic (matches uploaded image style)
# ---------------------------------------------------------------------------

def get_global_background_css() -> str:
    """
    Returns CSS that injects a dark teal molecular-network background for all
    three tab panels, with a distinct colour accent per tab.
    Call this once from app.py via st.markdown(..., unsafe_allow_html=True).
    """

    # Shared SVG node-network pattern — tiny, tiled
    network_svg_tab1 = (
        "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
        "width='320' height='180'%3E"
        "%3Ccircle cx='40' cy='60' r='3' fill='%2300c8c8' fill-opacity='.18'/%3E"
        "%3Ccircle cx='160' cy='30' r='4' fill='%2300c8c8' fill-opacity='.22'/%3E"
        "%3Ccircle cx='280' cy='70' r='3' fill='%2300c8c8' fill-opacity='.18'/%3E"
        "%3Ccircle cx='100' cy='140' r='3.5' fill='%2300c8c8' fill-opacity='.15'/%3E"
        "%3Ccircle cx='220' cy='150' r='3' fill='%2300c8c8' fill-opacity='.15'/%3E"
        "%3Cline x1='40' y1='60' x2='160' y2='30' stroke='%2300c8c8' "
        "stroke-opacity='.10' stroke-width='1'/%3E"
        "%3Cline x1='160' y1='30' x2='280' y2='70' stroke='%2300c8c8' "
        "stroke-opacity='.10' stroke-width='1'/%3E"
        "%3Cline x1='40' y1='60' x2='100' y2='140' stroke='%2300c8c8' "
        "stroke-opacity='.08' stroke-width='1'/%3E"
        "%3Cline x1='280' y1='70' x2='220' y2='150' stroke='%2300c8c8' "
        "stroke-opacity='.08' stroke-width='1'/%3E"
        "%3Cpath d='M0 90 Q80 50 160 90 Q240 130 320 90' fill='none' "
        "stroke='%2300d4d4' stroke-opacity='.08' stroke-width='1.5'/%3E"
        "%3C/svg%3E"
    )

    network_svg_tab2 = (
        "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
        "width='300' height='160'%3E"
        "%3Ccircle cx='60' cy='80' r='5' fill='%2300bfa0' fill-opacity='.22'/%3E"
        "%3Ccircle cx='150' cy='40' r='3' fill='%2300bfa0' fill-opacity='.18'/%3E"
        "%3Ccircle cx='240' cy='80' r='4' fill='%2300bfa0' fill-opacity='.20'/%3E"
        "%3Ccircle cx='150' cy='130' r='3' fill='%2300bfa0' fill-opacity='.15'/%3E"
        "%3Cline x1='60' y1='80' x2='150' y2='40' stroke='%2300bfa0' "
        "stroke-opacity='.12' stroke-width='1'/%3E"
        "%3Cline x1='150' y1='40' x2='240' y2='80' stroke='%2300bfa0' "
        "stroke-opacity='.12' stroke-width='1'/%3E"
        "%3Cline x1='60' y1='80' x2='150' y2='130' stroke='%2300bfa0' "
        "stroke-opacity='.10' stroke-width='1'/%3E"
        "%3Cline x1='240' y1='80' x2='150' y2='130' stroke='%2300bfa0' "
        "stroke-opacity='.10' stroke-width='1'/%3E"
        "%3Cellipse cx='150' cy='85' rx='55' ry='55' fill='none' "
        "stroke='%2300c8a0' stroke-opacity='.06' stroke-width='1'/%3E"
        "%3C/svg%3E"
    )

    network_svg_tab3 = (
        "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
        "width='280' height='180'%3E"
        "%3Ccircle cx='70' cy='50' r='4' fill='%236a7fff' fill-opacity='.22'/%3E"
        "%3Ccircle cx='210' cy='50' r='3' fill='%236a7fff' fill-opacity='.18'/%3E"
        "%3Ccircle cx='140' cy='90' r='5' fill='%236a7fff' fill-opacity='.28'/%3E"
        "%3Ccircle cx='60' cy='140' r='3' fill='%236a7fff' fill-opacity='.15'/%3E"
        "%3Ccircle cx='220' cy='140' r='4' fill='%236a7fff' fill-opacity='.18'/%3E"
        "%3Cline x1='70' y1='50' x2='140' y2='90' stroke='%236a7fff' "
        "stroke-opacity='.14' stroke-width='1.2'/%3E"
        "%3Cline x1='210' y1='50' x2='140' y2='90' stroke='%236a7fff' "
        "stroke-opacity='.14' stroke-width='1.2'/%3E"
        "%3Cline x1='140' y1='90' x2='60' y2='140' stroke='%236a7fff' "
        "stroke-opacity='.10' stroke-width='1'/%3E"
        "%3Cline x1='140' y1='90' x2='220' y2='140' stroke='%236a7fff' "
        "stroke-opacity='.10' stroke-width='1'/%3E"
        "%3Cpath d='M0 100 Q70 60 140 100 Q210 140 280 100' fill='none' "
        "stroke='%238090ff' stroke-opacity='.08' stroke-width='1.5'/%3E"
        "%3C/svg%3E"
    )

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@400;500;600&display=swap');

/* ── Global app background ─────────────────────────────── */
.stApp {{
    background: linear-gradient(160deg, #050d1a 0%, #081828 40%, #060f20 100%) !important;
    background-attachment: fixed !important;
}}
.main .block-container {{
    background: transparent !important;
}}
[data-testid="stHeader"] {{
    background: rgba(5,13,26,0.85) !important;
    backdrop-filter: blur(8px);
}}
[data-testid="stSidebar"] {{
    background: rgba(5,13,26,0.9) !important;
}}

/* ── Tab bar styling ───────────────────────────────────── */
[data-baseweb="tab-list"] {{
    background: rgba(8,20,40,0.7) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1px solid rgba(0,200,200,0.15) !important;
}}
button[data-baseweb="tab"] {{
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 0.78rem !important;
    color: rgba(140,200,220,0.7) !important;
    border-radius: 8px !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    background: rgba(0,180,200,0.18) !important;
    color: #00e5e5 !important;
}}

/* ── Tab 1 panel — Research (teal wave) ────────────────── */
[data-testid="stTabsContent"] > div:nth-child(1) {{
    background:
        url("{network_svg_tab1}") repeat,
        linear-gradient(160deg, #060e1e 0%, #0a1f38 60%, #061525 100%);
    min-height: 100vh;
    border-radius: 12px;
    padding: 8px;
}}

/* ── Tab 2 panel — Wafer Journey (emerald circuit) ─────── */
[data-testid="stTabsContent"] > div:nth-child(2) {{
    background:
        url("{network_svg_tab2}") repeat,
        linear-gradient(160deg, #050f14 0%, #0a2030 60%, #061a20 100%);
    min-height: 100vh;
    border-radius: 12px;
    padding: 8px;
}}

/* ── Tab 3 panel — Chat (deep indigo molecular) ────────── */
[data-testid="stTabsContent"] > div:nth-child(3) {{
    background:
        url("{network_svg_tab3}") repeat,
        linear-gradient(160deg, #07081e 0%, #0d1245 60%, #080a28 100%);
    min-height: 100vh;
    border-radius: 12px;
    padding: 8px;
}}

/* ── General text / widget overrides ──────────────────── */
h1, h2, h3, .chat-title {{
    font-family: 'Space Mono', monospace !important;
    color: #c8f0ff !important;
}}
p, li, label, .stMarkdown p {{
    color: #a8c8d8 !important;
}}
.stTextArea textarea, .stTextInput input {{
    background: rgba(10,25,50,0.8) !important;
    border: 1px solid rgba(0,200,200,0.25) !important;
    color: #d0eeff !important;
    border-radius: 10px !important;
}}
.stButton > button {{
    font-family: 'Space Mono', monospace !important;
    border-radius: 10px !important;
    background: rgba(0,180,200,0.12) !important;
    border: 1px solid rgba(0,200,200,0.30) !important;
    color: #80e8ff !important;
    transition: all .15s ease;
}}
.stButton > button:hover {{
    background: rgba(0,180,200,0.25) !important;
    border-color: rgba(0,220,220,0.5) !important;
}}
.stDownloadButton > button {{
    font-family: 'Space Mono', monospace !important;
    border-radius: 10px !important;
}}
.stProgress > div > div {{
    background: rgba(0,200,200,0.3) !important;
}}
.stProgress > div > div > div {{
    background: linear-gradient(90deg,#00c8c8,#0080ff) !important;
}}
div[data-testid="stAlert"] {{
    background: rgba(0,180,200,0.10) !important;
    border: 1px solid rgba(0,200,200,0.25) !important;
    color: #a0e0f0 !important;
    border-radius: 10px !important;
}}
.stSuccess {{
    background: rgba(0,160,100,0.15) !important;
    border-color: rgba(0,200,120,0.3) !important;
}}
.stInfo {{
    background: rgba(0,120,200,0.12) !important;
    border-color: rgba(0,160,220,0.3) !important;
}}
hr {{
    border-color: rgba(0,200,200,0.18) !important;
}}
</style>
"""


# ---------------------------------------------------------------------------
# Animated SVG characters
# ---------------------------------------------------------------------------

def get_animal_svg(anim_type: str, is_thinking: bool = False) -> str:
    think_speed = "0.5s" if is_thinking else "1.8s"
    think_dots = ""
    if is_thinking:
        think_dots = """
        <g>
          <circle cx="58" cy="168" r="5" fill="#aaa">
            <animate attributeName="opacity" values="0.2;1;0.2" dur="0.8s" begin="0s" repeatCount="indefinite"/>
          </circle>
          <circle cx="80" cy="168" r="5" fill="#aaa">
            <animate attributeName="opacity" values="0.2;1;0.2" dur="0.8s" begin="0.27s" repeatCount="indefinite"/>
          </circle>
          <circle cx="102" cy="168" r="5" fill="#aaa">
            <animate attributeName="opacity" values="0.2;1;0.2" dur="0.8s" begin="0.54s" repeatCount="indefinite"/>
          </circle>
        </g>"""

    if anim_type == "OWL":
        bob_dur = "0.7s" if is_thinking else "2.2s"
        return f"""<svg viewBox="0 0 160 180" xmlns="http://www.w3.org/2000/svg">
  <defs><style>
    .owl-body{{animation:owlBob {bob_dur} ease-in-out infinite alternate;transform-origin:80px 140px;}}
    @keyframes owlBob{{0%{{transform:translateY(0px) rotate(-1.5deg);}}100%{{transform:translateY(-8px) rotate(1.5deg);}}}}
    .owl-blink{{animation:owlBlink 4s ease-in-out infinite;transform-origin:center;}}
    @keyframes owlBlink{{0%,44%,56%,100%{{transform:scaleY(1);}}48%,52%{{transform:scaleY(0.05);}}}}
    .wing-l{{animation:wingL 2.8s ease-in-out infinite alternate;transform-origin:52px 115px;}}
    .wing-r{{animation:wingR 2.8s ease-in-out infinite alternate;transform-origin:108px 115px;}}
    @keyframes wingL{{0%{{transform:rotate(0deg);}}100%{{transform:rotate(-8deg);}}}}
    @keyframes wingR{{0%{{transform:rotate(0deg);}}100%{{transform:rotate(8deg);}}}}
  </style></defs>
  <rect x="45" y="28" width="70" height="8" rx="2" fill="#2c1a4a"/>
  <rect x="60" y="18" width="40" height="12" rx="3" fill="#2c1a4a"/>
  <line x1="80" y1="18" x2="96" y2="10" stroke="#2c1a4a" stroke-width="2"/>
  <circle cx="98" cy="9" r="4" fill="#FFD700"/>
  <g class="owl-body">
    <ellipse cx="80" cy="125" rx="38" ry="48" fill="#5a82c4"/>
    <ellipse cx="80" cy="132" rx="22" ry="30" fill="#8ab4e8"/>
    <polygon points="56,82 62,68 68,82" fill="#4a6da0"/>
    <polygon points="92,82 98,68 104,82" fill="#4a6da0"/>
    <ellipse class="wing-l" cx="52" cy="120" rx="16" ry="28" fill="#4a6da0" transform="rotate(-8,52,120)"/>
    <ellipse class="wing-r" cx="108" cy="120" rx="16" ry="28" fill="#4a6da0" transform="rotate(8,108,120)"/>
    <circle cx="68" cy="100" r="13" fill="white" stroke="#2a4070" stroke-width="1.5"/>
    <circle cx="92" cy="100" r="13" fill="white" stroke="#2a4070" stroke-width="1.5"/>
    <circle cx="68" cy="100" r="9" fill="#4A90D9"/>
    <circle cx="92" cy="100" r="9" fill="#4A90D9"/>
    <circle cx="68" cy="100" r="5" fill="#1a1a1a"/>
    <circle cx="92" cy="100" r="5" fill="#1a1a1a"/>
    <circle cx="71" cy="97" r="2" fill="white"/>
    <circle cx="95" cy="97" r="2" fill="white"/>
    <rect class="owl-blink" x="55" y="89" width="26" height="22" rx="11" fill="#5a82c4"/>
    <rect class="owl-blink" x="79" y="89" width="26" height="22" rx="11" fill="#5a82c4"/>
    <polygon points="76,110 84,110 80,120" fill="#E8A020"/>
    <ellipse cx="68" cy="170" rx="10" ry="5" fill="#3a6090"/>
    <ellipse cx="92" cy="170" rx="10" ry="5" fill="#3a6090"/>
  </g>{think_dots}
</svg>"""

    elif anim_type == "FOX":
        bounce_dur = "0.55s" if is_thinking else "1.6s"
        return f"""<svg viewBox="0 0 160 180" xmlns="http://www.w3.org/2000/svg">
  <defs><style>
    .fox-body{{animation:foxBounce {bounce_dur} ease-in-out infinite alternate;transform-origin:80px 130px;}}
    @keyframes foxBounce{{0%{{transform:translateY(0px) rotate(-1deg);}}100%{{transform:translateY(-7px) rotate(1deg);}}}}
    .fox-tail{{animation:tailWag 0.9s ease-in-out infinite alternate;transform-origin:40px 148px;}}
    @keyframes tailWag{{0%{{transform:rotate(-25deg);}}100%{{transform:rotate(20deg);}}}}
    .fox-blink{{animation:foxBlink 3.5s ease-in-out infinite;}}
    @keyframes foxBlink{{0%,42%,58%,100%{{transform:scaleY(1);}}48%,52%{{transform:scaleY(0.06);}}}}
  </style></defs>
  <g class="fox-tail">
    <ellipse cx="38" cy="145" rx="20" ry="36" fill="#D4581A" transform="rotate(-30,38,145)"/>
    <ellipse cx="32" cy="132" rx="10" ry="18" fill="white" transform="rotate(-30,32,132)"/>
  </g>
  <g class="fox-body">
    <polygon points="55,68 46,40 72,60" fill="#D4581A"/>
    <polygon points="57,66 50,47 68,62" fill="#F0A070"/>
    <polygon points="105,68 114,40 88,60" fill="#D4581A"/>
    <polygon points="103,66 110,47 92,62" fill="#F0A070"/>
    <ellipse cx="80" cy="90" rx="36" ry="34" fill="#D4581A"/>
    <ellipse cx="80" cy="98" rx="22" ry="24" fill="#F5E0CC"/>
    <ellipse cx="80" cy="138" rx="30" ry="38" fill="#D4581A"/>
    <ellipse cx="80" cy="144" rx="18" ry="24" fill="#F5E0CC"/>
    <ellipse cx="67" cy="88" rx="9" ry="9" fill="#1a1a1a"/>
    <ellipse cx="93" cy="88" rx="9" ry="9" fill="#1a1a1a"/>
    <circle cx="70" cy="85" r="3" fill="white"/>
    <circle cx="96" cy="85" r="3" fill="white"/>
    <rect class="fox-blink" x="58" y="80" width="18" height="16" rx="8" fill="#D4581A" style="transform-origin:67px 88px;"/>
    <rect class="fox-blink" x="84" y="80" width="18" height="16" rx="8" fill="#D4581A" style="transform-origin:93px 88px;"/>
    <ellipse cx="80" cy="103" rx="6" ry="4.5" fill="#2a1010"/>
    <line x1="80" y1="107" x2="80" y2="112" stroke="#2a1010" stroke-width="1.5"/>
    <path d="M 72 112 Q 80 118 88 112" fill="none" stroke="#2a1010" stroke-width="1.5"/>
    <polygon points="74,162 80,172 86,162 80,158" fill="#3a6fc4"/>
    <ellipse cx="62" cy="170" rx="12" ry="7" fill="#D4581A"/>
    <ellipse cx="98" cy="170" rx="12" ry="7" fill="#D4581A"/>
  </g>{think_dots}
</svg>"""

    elif anim_type == "CAT":
        sway_dur = "0.6s" if is_thinking else "2.5s"
        return f"""<svg viewBox="0 0 160 180" xmlns="http://www.w3.org/2000/svg">
  <defs><style>
    .cat-body{{animation:catSway {sway_dur} ease-in-out infinite alternate;transform-origin:80px 130px;}}
    @keyframes catSway{{0%{{transform:rotate(-2deg) translateY(0px);}}100%{{transform:rotate(2deg) translateY(-6px);}}}}
    .cat-tail{{animation:tailSway 1.8s ease-in-out infinite;transform-origin:115px 152px;}}
    @keyframes tailSway{{0%{{transform:rotate(-30deg);}}50%{{transform:rotate(20deg);}}100%{{transform:rotate(-30deg);}}}}
    .cat-blink{{animation:catBlink 5s ease-in-out infinite;transform-origin:center;}}
    @keyframes catBlink{{0%,46%,54%,100%{{transform:scaleY(1);}}49%,51%{{transform:scaleY(0.05);}}}}
  </style></defs>
  <g class="cat-tail">
    <path d="M 115 152 Q 148 130 145 100 Q 148 80 135 75" fill="none" stroke="#7B4BB0" stroke-width="10" stroke-linecap="round"/>
    <path d="M 115 152 Q 148 130 145 100 Q 148 80 135 75" fill="none" stroke="#9B6BD0" stroke-width="6" stroke-linecap="round"/>
    <ellipse cx="134" cy="73" rx="10" ry="8" fill="#D0A8FF" transform="rotate(-20,134,73)"/>
  </g>
  <g class="cat-body">
    <polygon points="52,70 42,38 72,62" fill="#7B4BB0"/>
    <polygon points="54,68 46,46 68,63" fill="#D0A8FF"/>
    <polygon points="108,70 118,38 88,62" fill="#7B4BB0"/>
    <polygon points="106,68 114,46 92,63" fill="#D0A8FF"/>
    <ellipse cx="80" cy="92" rx="38" ry="36" fill="#8B55C0"/>
    <ellipse cx="80" cy="104" rx="20" ry="16" fill="#B080E0"/>
    <ellipse cx="80" cy="142" rx="32" ry="36" fill="#8B55C0"/>
    <ellipse cx="80" cy="148" rx="18" ry="22" fill="#C090F0"/>
    <rect x="57" y="156" width="46" height="9" rx="4" fill="#FF7BAC"/>
    <circle cx="80" cy="165" r="6" fill="#FFD700" stroke="#E0A000" stroke-width="1"/>
    <ellipse cx="67" cy="89" rx="11" ry="10" fill="#F0E0FF"/>
    <ellipse cx="93" cy="89" rx="11" ry="10" fill="#F0E0FF"/>
    <ellipse cx="67" cy="89" rx="5" ry="9" fill="#1a0a2a"/>
    <ellipse cx="93" cy="89" rx="5" ry="9" fill="#1a0a2a"/>
    <ellipse cx="67" cy="89" rx="8" ry="9" fill="none" stroke="#8040C0" stroke-width="1.5"/>
    <ellipse cx="93" cy="89" rx="8" ry="9" fill="none" stroke="#8040C0" stroke-width="1.5"/>
    <circle cx="70" cy="86" r="2.5" fill="white"/>
    <circle cx="96" cy="86" r="2.5" fill="white"/>
    <rect class="cat-blink" x="56" y="80" width="22" height="18" rx="9" fill="#8B55C0" style="transform-origin:67px 89px;"/>
    <rect class="cat-blink" x="82" y="80" width="22" height="18" rx="9" fill="#8B55C0" style="transform-origin:93px 89px;"/>
    <polygon points="80,105 75,110 85,110" fill="#FF80B0"/>
    <line x1="44" y1="106" x2="70" y2="110" stroke="#D0B0F0" stroke-width="1.2"/>
    <line x1="44" y1="112" x2="70" y2="112" stroke="#D0B0F0" stroke-width="1.2"/>
    <line x1="116" y1="106" x2="90" y2="110" stroke="#D0B0F0" stroke-width="1.2"/>
    <line x1="116" y1="112" x2="90" y2="112" stroke="#D0B0F0" stroke-width="1.2"/>
    <path d="M 73 116 Q 80 122 87 116" fill="none" stroke="#8040C0" stroke-width="1.5"/>
    <ellipse cx="60" cy="172" rx="14" ry="8" fill="#8B55C0"/>
    <ellipse cx="100" cy="172" rx="14" ry="8" fill="#8B55C0"/>
  </g>{think_dots}
</svg>"""

    else:  # ROBOT
        pulse_dur = "0.4s" if is_thinking else "2.0s"
        gear_dur = "1.5s" if is_thinking else "5s"
        return f"""<svg viewBox="0 0 160 180" xmlns="http://www.w3.org/2000/svg">
  <defs><style>
    .robot-body{{animation:robotPulse {pulse_dur} ease-in-out infinite alternate;transform-origin:80px 130px;}}
    @keyframes robotPulse{{0%{{transform:translateY(0px);}}100%{{transform:translateY(-5px);}}}}
    .led-l{{animation:ledBlink 2.4s step-end infinite;}}
    .led-r{{animation:ledBlink 2.4s step-end infinite 1.2s;}}
    @keyframes ledBlink{{0%,45%,55%,100%{{fill:#00FF88;}}48%,52%{{fill:#003322;}}}}
    .gear{{animation:gearSpin {gear_dur} linear infinite;transform-origin:126px 72px;}}
    @keyframes gearSpin{{0%{{transform:rotate(0deg);}}100%{{transform:rotate(360deg);}}}}
    .antenna{{animation:antennaPing 3s ease-in-out infinite;transform-origin:80px 22px;}}
    @keyframes antennaPing{{0%,100%{{transform:rotate(-4deg);}}50%{{transform:rotate(4deg);}}}}
    .panel-glow{{animation:panelPulse 2s ease-in-out infinite;}}
    @keyframes panelPulse{{0%,100%{{opacity:0.6;}}50%{{opacity:1;}}}}
  </style></defs>
  <g class="antenna">
    <line x1="80" y1="36" x2="80" y2="16" stroke="#1a9e6a" stroke-width="3"/>
    <circle cx="80" cy="13" r="6" fill="#00CC88" stroke="#1a4433" stroke-width="1.5"/>
    <circle cx="80" cy="13" r="3" fill="#00FF88">
      <animate attributeName="opacity" values="0.5;1;0.5" dur="1.2s" repeatCount="indefinite"/>
    </circle>
  </g>
  <g class="gear">
    <circle cx="126" cy="72" r="14" fill="none" stroke="#1a9e6a" stroke-width="4" stroke-dasharray="6 4"/>
    <circle cx="126" cy="72" r="6" fill="#1a9e6a"/>
    <circle cx="126" cy="72" r="3" fill="#00FF88" opacity="0.7"/>
  </g>
  <g class="robot-body">
    <rect x="44" y="36" width="72" height="62" rx="10" fill="#0d2a1e" stroke="#1a9e6a" stroke-width="2.5"/>
    <circle cx="52" cy="44" r="3" fill="#1a9e6a"/>
    <circle cx="108" cy="44" r="3" fill="#1a9e6a"/>
    <rect x="52" y="52" width="22" height="22" rx="5" fill="#051a10" stroke="#1a9e6a" stroke-width="1.5"/>
    <rect x="86" y="52" width="22" height="22" rx="5" fill="#051a10" stroke="#1a9e6a" stroke-width="1.5"/>
    <rect class="led-l" x="56" y="56" width="14" height="14" rx="3" fill="#00FF88"/>
    <rect class="led-r" x="90" y="56" width="14" height="14" rx="3" fill="#00FF88"/>
    <rect x="56" y="82" width="48" height="10" rx="3" fill="#051a10" stroke="#1a9e6a" stroke-width="1"/>
    <line x1="68" y1="84" x2="68" y2="90" stroke="#00FF88" stroke-width="2"/>
    <line x1="74" y1="85" x2="74" y2="89" stroke="#00FF88" stroke-width="2"/>
    <line x1="80" y1="83" x2="80" y2="91" stroke="#00FF88" stroke-width="2"/>
    <line x1="86" y1="85" x2="86" y2="89" stroke="#00FF88" stroke-width="2"/>
    <line x1="92" y1="84" x2="92" y2="90" stroke="#00FF88" stroke-width="2"/>
    <rect x="70" y="98" width="20" height="10" rx="3" fill="#051a10" stroke="#1a9e6a" stroke-width="1.5"/>
    <rect x="42" y="108" width="76" height="56" rx="8" fill="#0d2a1e" stroke="#1a9e6a" stroke-width="2"/>
    <rect x="52" y="116" width="56" height="38" rx="5" fill="#051a10" stroke="#1a9e6a" stroke-width="1.5"/>
    <circle cx="62" cy="124" r="4" fill="#00FF88" class="panel-glow"/>
    <circle cx="74" cy="124" r="4" fill="#FFD700" class="panel-glow" style="animation-delay:0.4s"/>
    <circle cx="86" cy="124" r="4" fill="#00AAFF" class="panel-glow" style="animation-delay:0.8s"/>
    <circle cx="98" cy="124" r="4" fill="#FF4444" class="panel-glow" style="animation-delay:1.2s"/>
    <rect x="56" y="132" width="48" height="6" rx="3" fill="#001a0d"/>
    <rect x="56" y="132" width="32" height="6" rx="3" fill="#00FF88" opacity="0.8">
      <animate attributeName="width" values="10;44;10" dur="2.5s" repeatCount="indefinite"/>
    </rect>
    <text x="80" y="148" text-anchor="middle" font-family="monospace" font-size="9" fill="#00FF88" opacity="0.8">NANO v1</text>
    <rect x="22" y="108" width="20" height="44" rx="8" fill="#0d2a1e" stroke="#1a9e6a" stroke-width="1.5"/>
    <rect x="118" y="108" width="20" height="44" rx="8" fill="#0d2a1e" stroke="#1a9e6a" stroke-width="1.5"/>
    <ellipse cx="32" cy="158" rx="11" ry="9" fill="#051a10" stroke="#1a9e6a" stroke-width="1.5"/>
    <ellipse cx="128" cy="158" rx="11" ry="9" fill="#051a10" stroke="#1a9e6a" stroke-width="1.5"/>
    <rect x="56" y="164" width="18" height="14" rx="4" fill="#051a10" stroke="#1a9e6a" stroke-width="1.5"/>
    <rect x="86" y="164" width="18" height="14" rx="4" fill="#051a10" stroke="#1a9e6a" stroke-width="1.5"/>
    <rect x="52" y="173" width="26" height="8" rx="4" fill="#051a10" stroke="#1a9e6a" stroke-width="1"/>
    <rect x="82" y="173" width="26" height="8" rx="4" fill="#051a10" stroke="#1a9e6a" stroke-width="1"/>
  </g>{think_dots}
</svg>"""


# ---------------------------------------------------------------------------
# Voice control component HTML
# ---------------------------------------------------------------------------

def get_voice_component_html(
    text: str,
    voice_on: bool,
    auto_speak: bool,
    should_stop: bool,
    char_color: str,
    voice_pitch: float = 1.0,
    voice_rate: float = 0.9,
) -> str:
    """
    Returns a self-contained HTML block with:
    - Web Speech API integration
    - Auto-speak when auto_speak=True
    - Pause / Resume / Stop HTML buttons (no Streamlit rerun)
    - Preferred voice selection (natural, friendly voices)
    - Visual speaking indicator
    """
    safe_text = (
        text.replace("\\", "\\\\")
            .replace("`", "\\`")
            .replace("$", "\\$")
    )
    auto_speak_js = "true" if auto_speak else "false"
    stop_js = "true" if should_stop else "false"
    visible = "flex" if voice_on else "none"

    return f"""
<!DOCTYPE html><html><head>
<style>
*{{box-sizing:border-box;margin:0;padding:0;font-family:'Segoe UI',sans-serif;}}
body{{background:transparent;display:{visible};align-items:center;
     gap:10px;padding:8px 12px;height:56px;overflow:hidden;}}
.vc-bar{{display:flex;align-items:center;gap:8px;
         background:rgba(0,180,160,0.12);border:1px solid rgba(0,220,200,0.25);
         border-radius:28px;padding:6px 14px;width:100%;}}
.vc-icon{{width:28px;height:28px;border-radius:50%;
          background:{char_color};display:flex;align-items:center;
          justify-content:center;font-size:13px;flex-shrink:0;}}
.vc-status{{font-size:11px;color:#80e0d0;flex:1;min-width:0;
            white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
.vc-btn{{padding:4px 12px;border-radius:16px;border:1px solid rgba(0,200,180,0.35);
         background:rgba(0,180,160,0.15);color:#80e8d8;font-size:11px;
         font-weight:600;cursor:pointer;transition:all .15s;white-space:nowrap;}}
.vc-btn:hover{{background:rgba(0,200,180,0.28);border-color:rgba(0,220,200,0.5);}}
.vc-btn.stop{{border-color:rgba(255,80,80,0.35);color:#ff9090;
              background:rgba(200,60,60,0.12);}}
.vc-btn.stop:hover{{background:rgba(200,60,60,0.25);}}
.wave{{display:flex;gap:2px;align-items:center;height:16px;margin-right:4px;}}
.bar{{width:3px;border-radius:2px;background:#00e0c8;animation:wave 0.8s ease-in-out infinite;}}
.bar:nth-child(2){{animation-delay:0.1s;}}
.bar:nth-child(3){{animation-delay:0.2s;}}
.bar:nth-child(4){{animation-delay:0.15s;}}
.bar.paused{{animation-play-state:paused;height:3px!important;}}
@keyframes wave{{
  0%,100%{{height:4px;}}50%{{height:14px;}}
}}
</style></head><body>
<div class="vc-bar" id="vc-bar">
  <div class="vc-icon" id="vc-icon">🔊</div>
  <div class="wave" id="wave-anim">
    <div class="bar" id="b1"></div>
    <div class="bar" id="b2"></div>
    <div class="bar" id="b3"></div>
    <div class="bar" id="b4"></div>
  </div>
  <div class="vc-status" id="vc-status">Ready</div>
  <button class="vc-btn" id="pause-btn" onclick="togglePause()">⏸ Pause</button>
  <button class="vc-btn stop" onclick="stopAll()">⏹ Stop</button>
</div>

<script>
const TEXT = `{safe_text}`;
const AUTO_SPEAK = {auto_speak_js};
const SHOULD_STOP = {stop_js};
const PITCH = {voice_pitch};
const RATE = {voice_rate};

const statusEl = document.getElementById('vc-status');
const pauseBtn = document.getElementById('pause-btn');
const bars = document.querySelectorAll('.bar');

let isSpeaking = false;
let isPaused = false;

function setStatus(txt) {{ statusEl.textContent = txt; }}
function setWave(active) {{
  bars.forEach(b => b.classList.toggle('paused', !active));
}}

function selectVoice() {{
  const voices = speechSynthesis.getVoices();
  const preferred = [
    'Samantha','Karen','Moira','Fiona','Victoria','Tessa',
    'Google UK English Female','Google US English',
    'Microsoft Zira','Microsoft Eva','Microsoft Jenny',
    'Alex','Daniel','Oliver'
  ];
  for (const name of preferred) {{
    const v = voices.find(v => v.name && v.name.includes(name));
    if (v) return v;
  }}
  return voices.find(v => v.lang && v.lang.startsWith('en')) || (voices.length ? voices[0] : null);
}}

function speak(text) {{
  speechSynthesis.cancel();
  if (!text.trim()) return;
  const utter = new SpeechSynthesisUtterance(text);
  const voice = selectVoice();
  if (voice) utter.voice = voice;
  utter.pitch = PITCH;
  utter.rate = RATE;
  utter.volume = 1.0;
  utter.onstart = () => {{
    isSpeaking = true; isPaused = false;
    setStatus('Speaking...');
    setWave(true);
    pauseBtn.textContent = '⏸ Pause';
  }};
  utter.onend = () => {{
    isSpeaking = false; isPaused = false;
    setStatus('Done');
    setWave(false);
    pauseBtn.textContent = '⏸ Pause';
  }};
  utter.onerror = () => {{
    isSpeaking = false;
    setStatus('Error — try again');
    setWave(false);
  }};
  speechSynthesis.speak(utter);
}}

function togglePause() {{
  if (isSpeaking && !isPaused) {{
    speechSynthesis.pause();
    isPaused = true;
    setStatus('Paused');
    setWave(false);
    pauseBtn.textContent = '▶ Resume';
  }} else if (isPaused) {{
    speechSynthesis.resume();
    isPaused = false;
    setStatus('Speaking...');
    setWave(true);
    pauseBtn.textContent = '⏸ Pause';
  }}
}}

function stopAll() {{
  speechSynthesis.cancel();
  isSpeaking = false; isPaused = false;
  setStatus('Stopped');
  setWave(false);
  pauseBtn.textContent = '⏸ Pause';
}}

if (SHOULD_STOP) {{
  stopAll();
}} else if (AUTO_SPEAK) {{
  if (speechSynthesis.getVoices().length === 0) {{
    speechSynthesis.onvoiceschanged = () => speak(TEXT);
  }} else {{
    setTimeout(() => speak(TEXT), 250);
  }}
}} else {{
  setStatus('Voice ready');
  setWave(false);
}}
</script>
</body></html>"""


# ---------------------------------------------------------------------------
# Chat bubble renderer
# ---------------------------------------------------------------------------

def render_chat_bubble(
    role: str,
    text: str,
    char_data: dict,
    is_thinking: bool = False,
) -> str:
    if role == "user":
        return f"""
<div style="display:flex;justify-content:flex-end;margin:10px 0;align-items:flex-end;gap:8px;">
  <div style="background:rgba(0,140,180,0.18);color:#c0eeff;
              border:1px solid rgba(0,180,220,0.25);
              border-radius:16px 16px 4px 16px;padding:12px 16px;max-width:72%;
              font-size:0.92rem;line-height:1.6;font-family:'Inter',sans-serif;">
    {text}
  </div>
  <div style="width:36px;height:36px;background:rgba(0,140,180,0.25);border-radius:50%;
              display:flex;align-items:center;justify-content:center;font-size:1.1rem;flex-shrink:0;">
    🧑‍🔬
  </div>
</div>"""

    svg_content = get_animal_svg(char_data["anim"], is_thinking=is_thinking)
    if is_thinking:
        bubble_body = """
<div style="display:flex;gap:5px;align-items:center;padding:4px 2px;">
  <span style="width:9px;height:9px;border-radius:50%;background:rgba(0,200,200,0.6);display:inline-block;
    animation:dotP 0.8s ease-in-out infinite;"></span>
  <span style="width:9px;height:9px;border-radius:50%;background:rgba(0,200,200,0.6);display:inline-block;
    animation:dotP 0.8s ease-in-out 0.27s infinite;"></span>
  <span style="width:9px;height:9px;border-radius:50%;background:rgba(0,200,200,0.6);display:inline-block;
    animation:dotP 0.8s ease-in-out 0.54s infinite;"></span>
</div>"""
    else:
        bubble_body = f'<span style="font-size:0.92rem;line-height:1.65;color:#d8f0ff;">{text}</span>'

    return f"""
<div style="display:flex;justify-content:flex-start;margin:10px 0;align-items:flex-end;gap:10px;">
  <div style="width:70px;height:80px;background:rgba(10,30,60,0.7);
              border-radius:12px;border:1px solid {char_data['color']}44;
              flex-shrink:0;overflow:hidden;display:flex;align-items:center;justify-content:center;">
    <div style="width:60px;height:70px;overflow:hidden;">{svg_content}</div>
  </div>
  <div style="background:rgba(10,30,60,0.75);color:#d0eeff;
              border-radius:16px 16px 16px 4px;padding:13px 17px;max-width:70%;
              border:1px solid {char_data['color']}30;font-family:'Inter',sans-serif;">
    {bubble_body}
  </div>
</div>"""


# ---------------------------------------------------------------------------
# Main chatbot render function
# ---------------------------------------------------------------------------

def render_nano_chatbot(api_key: str):
    """Render the full NanoLab character chatbot Streamlit app (Tab 3)."""

    # ── Base page CSS ──────────────────────────────────────────────────────
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@400;500;600&display=swap');
    .chat-title{font-family:'Space Mono',monospace;font-size:1.8rem;font-weight:700;
                color:#80e8ff;letter-spacing:-0.5px;}
    .char-name{font-family:'Space Mono',monospace;font-weight:700;font-size:0.9rem;}
    @keyframes dotP{0%,100%{opacity:0.2;transform:scale(0.8);}50%{opacity:1;transform:scale(1.1);}}
    </style>
    """, unsafe_allow_html=True)

    # ── Session state init ─────────────────────────────────────────────────
    if "selected_character" not in st.session_state:
        st.session_state.selected_character = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "voice_enabled" not in st.session_state:
        st.session_state.voice_enabled = False
    if "last_spoken_idx" not in st.session_state:
        st.session_state.last_spoken_idx = -1
    if "stop_voice" not in st.session_state:
        st.session_state.stop_voice = False

    # ── Title ──────────────────────────────────────────────────────────────
    st.markdown('<p class="chat-title">NanoLab Chat</p>', unsafe_allow_html=True)
    st.caption("Choose a guide and ask anything about nanotechnology, wafer fabrication, and characterisation tools.")

    # ── CHARACTER SELECTION ────────────────────────────────────────────────
    if st.session_state.selected_character is None:
        st.markdown("### Choose your guide")
        st.markdown(
            '<p style="color:#80c8d8;font-size:0.9rem;">Each guide has a unique personality — pick your favourite!</p>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        cols = st.columns(4)
        for col, (key, char) in zip(cols, CHARACTERS.items()):
            with col:
                svg = get_animal_svg(char["anim"])
                st.markdown(
                    f"""<div style="background:rgba(10,25,55,0.8);border:1px solid {char['color']}44;
                        border-radius:16px;padding:16px 10px;text-align:center;
                        transition:all .2s;">
                      <div style="width:100%;height:130px;overflow:hidden;display:flex;
                                  align-items:center;justify-content:center;">
                        <div style="width:110px;height:130px;overflow:hidden;">{svg}</div>
                      </div>
                      <div class="char-name" style="color:{char['color']};margin-top:6px;">{char['label']}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
                st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
                if st.button(f"Choose {char['label']}", key=f"choose_{key}", use_container_width=True):
                    st.session_state.selected_character = key
                    st.session_state.chat_history = [
                        {"role": "assistant", "content": char["greeting"]}
                    ]
                    st.session_state.last_spoken_idx = -1
                    st.session_state.stop_voice = False
                    st.rerun()
        return

    # ── CHAT VIEW ──────────────────────────────────────────────────────────
    char_key = st.session_state.selected_character
    char = CHARACTERS[char_key]
    history = st.session_state.chat_history

    # Header row
    h1, h2 = st.columns([5, 1])
    with h1:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:4px;">'
            f'<div style="width:48px;height:52px;background:rgba(10,25,55,0.8);'
            f'border-radius:12px;border:1px solid {char["color"]}44;overflow:hidden;'
            f'display:flex;align-items:center;justify-content:center;">'
            f'<div style="width:44px;height:52px;overflow:hidden;">{get_animal_svg(char["anim"])}</div></div>'
            f'<div><div style="font-family:Space Mono,monospace;font-weight:700;'
            f'font-size:1.05rem;color:{char["color"]};">{char["label"]}</div>'
            f'<div style="font-size:0.76rem;color:rgba(120,180,200,0.7);">NanoLab Guide · Nanotechnology & Fabrication</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
    with h2:
        if st.button("↩ Change\nguide", key="change_guide"):
            st.session_state.selected_character = None
            st.session_state.chat_history = []
            st.session_state.last_spoken_idx = -1
            st.session_state.stop_voice = True   # stop voice immediately
            st.rerun()

    st.divider()

    # ── Voice toggle ───────────────────────────────────────────────────────
    vc1, vc2, vc3 = st.columns([1, 1, 5])
    with vc1:
        voice_label = "🔊 Voice ON" if st.session_state.voice_enabled else "🔇 Voice OFF"
        if st.button(voice_label, key="voice_toggle", use_container_width=True):
            st.session_state.voice_enabled = not st.session_state.voice_enabled
            if not st.session_state.voice_enabled:
                st.session_state.stop_voice = True
            st.rerun()

    # ── Compute voice trigger ──────────────────────────────────────────────
    latest_assistant_text = ""
    latest_assistant_idx = -1
    for i, msg in enumerate(history):
        if msg["role"] == "assistant":
            latest_assistant_text = msg["content"]
            latest_assistant_idx = i

    auto_speak = (
        st.session_state.voice_enabled
        and latest_assistant_idx > st.session_state.last_spoken_idx
        and latest_assistant_text != ""
    )
    if auto_speak:
        st.session_state.last_spoken_idx = latest_assistant_idx

    stop_now = st.session_state.get("stop_voice", False)
    if stop_now:
        st.session_state.stop_voice = False

    # ── Voice control bar ──────────────────────────────────────────────────
    if st.session_state.voice_enabled or stop_now:
        voice_html = get_voice_component_html(
            text=latest_assistant_text,
            voice_on=st.session_state.voice_enabled,
            auto_speak=auto_speak,
            should_stop=stop_now,
            char_color=char["color"],
            voice_pitch=char.get("voice_pitch", 1.0),
            voice_rate=char.get("voice_rate", 0.9),
        )
        components.html(voice_html, height=60, scrolling=False)

    # ── Chat messages ──────────────────────────────────────────────────────
    dot_css = """<style>
    @keyframes dotP{0%,100%{opacity:0.2;transform:scale(0.8);}50%{opacity:1;transform:scale(1.1);}}
    body{background:transparent;margin:0;padding:10px 4px;}
    ::-webkit-scrollbar{width:4px;}
    ::-webkit-scrollbar-track{background:rgba(0,80,120,0.2);border-radius:4px;}
    ::-webkit-scrollbar-thumb{background:rgba(0,180,200,0.4);border-radius:4px;}
    </style>"""

    bubbles = "".join(
        render_chat_bubble(m["role"], m["content"], char, is_thinking=False)
        for m in history
    )

    full_chat = f"""<!DOCTYPE html><html><head>{dot_css}</head>
<body>{bubbles}<div id="bottom"></div>
<script>document.getElementById('bottom').scrollIntoView({{behavior:'smooth'}});</script>
</body></html>"""

    components.html(full_chat, height=450, scrolling=True)

    # ── Starter question chips ─────────────────────────────────────────────
    if len(history) <= 1:
        st.markdown(
            '<p style="font-size:0.82rem;color:rgba(0,200,200,0.7);margin:8px 0 4px;">Suggested questions:</p>',
            unsafe_allow_html=True,
        )
        q_cols = st.columns(len(STARTER_QUESTIONS))
        for i, (qcol, question) in enumerate(zip(q_cols, STARTER_QUESTIONS)):
            with qcol:
                if st.button(question, key=f"starter_{i}", use_container_width=True):
                    st.session_state.chat_history.append({"role": "user", "content": question})
                    _call_claude_and_append(char, api_key)
                    st.rerun()

    # ── Chat input form ────────────────────────────────────────────────────
    with st.form(key="chat_form", clear_on_submit=True):
        ic, bc = st.columns([6, 1])
        with ic:
            user_input = st.text_input(
                "Your question",
                placeholder=f"Ask {char['label']} about nanotechnology…",
                label_visibility="collapsed",
            )
        with bc:
            submitted = st.form_submit_button("Send ➤", use_container_width=True)

    if submitted and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
        _call_claude_and_append(char, api_key)
        st.rerun()


# ---------------------------------------------------------------------------
# Claude API helper
# ---------------------------------------------------------------------------

def _call_claude_and_append(char: dict, api_key: str):
    client = anthropic.Anthropic(api_key=api_key)
    messages = [{"role": m["role"], "content": m["content"]}
                for m in st.session_state.chat_history]
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            system=char["system"],
            messages=messages,
        )
        reply = ""
        for block in response.content:
            if hasattr(block, "text"):
                reply += block.text
        reply = reply.strip() or "Something went quiet in the NanoLab — please try again!"
    except anthropic.APIConnectionError:
        reply = "Connection error — cannot reach the Anthropic API. Please check your internet."
    except anthropic.AuthenticationError:
        reply = "Invalid API key. Please check your ANTHROPIC_API_KEY."
    except anthropic.RateLimitError:
        reply = "Rate limit reached — please wait a moment and try again!"
    except Exception as e:
        reply = f"Unexpected error: {e}"

    st.session_state.chat_history.append({"role": "assistant", "content": reply})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    st.set_page_config(page_title="NanoLab Chat", page_icon="🔬", layout="wide")
    st.markdown(get_global_background_css(), unsafe_allow_html=True)
    _api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not _api_key:
        st.error("Set the ANTHROPIC_API_KEY environment variable and restart.")
        st.stop()
    render_nano_chatbot(_api_key)