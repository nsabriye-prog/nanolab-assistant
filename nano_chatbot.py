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
        "color": "#5B3A8E",
        "bg": "#F3EEFF",
        "bubble": "#EDE0FF",
        "greeting": (
            "Hoot hoot! Welcome to the NanoLab! I'm Professor Nova, your wise guide "
            "to the microscopic world of nanotechnology. Whether it's quantum dots, "
            "wafer fabrication, or characterisation instruments — I've seen it all from "
            "my perch in the cleanroom. So, what tiny mystery shall we explore today?"
        ),
        "system": (
            "You are Professor Nova, a wise and enthusiastic owl professor who teaches "
            "nanotechnology, semiconductor wafer fabrication, and materials characterisation "
            "tools (SEM, TEM, AFM, XRD, XPS, SIMS, Raman, ellipsometry, FTIR, 4-point probe). "
            "Speak warmly and use the occasional owl pun ('hoot', 'wise', 'perch'). "
            "Give accurate, educational answers in a friendly professor tone. "
            "Keep every reply under 120 words. Always end with one follow-up question "
            "to deepen the student's understanding."
        ),
        "anim": "OWL",
    },
    "Dr Foxy": {
        "label": "Dr Foxy",
        "color": "#C15A1A",
        "bg": "#FFF4EC",
        "bubble": "#FFE8D1",
        "greeting": (
            "Hey there! Dr Foxy here — research scientist and self-confessed "
            "nanofab addict. I've spent more hours in a cleanroom than outside one, "
            "so ask me anything about deposition, etching, lithography, or "
            "characterisation. I'll give you the real-world lab perspective. "
            "What experiment are you planning?"
        ),
        "system": (
            "You are Dr Foxy, a sharp and energetic fox scientist specialising in "
            "nanofabrication: thin film deposition, lithography, etching, annealing, "
            "and characterisation (SEM, TEM, AFM, XRD, XPS, SIMS, Raman, ellipsometry, "
            "FTIR, 4-point probe). Speak with quick wit and practical lab insight. "
            "Use casual but technically precise language. Occasionally reference real "
            "lab scenarios or gotchas. Keep every reply under 120 words. "
            "Always end with one follow-up question."
        ),
        "anim": "FOX",
    },
    "Pixel": {
        "label": "Pixel",
        "color": "#6A3B8F",
        "bg": "#F5EEFF",
        "bubble": "#EAD9FF",
        "greeting": (
            "Mrrrow! I'm Pixel, the NanoLab's most curious cat — and believe me, "
            "I've knocked over enough beakers to learn my lesson. I love exploring "
            "the weird and wonderful world of nanoscale materials. Got a question "
            "about crystal structures, surface chemistry, or how an AFM tip works? "
            "Let's sniff it out together! What has your curiosity piqued today?"
        ),
        "system": (
            "You are Pixel, a curious and playful purple cat who loves nanotechnology, "
            "materials science, and characterisation tools (SEM, TEM, AFM, XRD, XPS, "
            "SIMS, Raman spectroscopy, ellipsometry, FTIR, 4-point probe). "
            "Use a warm, curious tone with occasional cat mannerisms ('purrfect', "
            "'paws', 'sniff out'). Make complex topics approachable and fun. "
            "Keep every reply under 120 words. Always end with one follow-up question "
            "to keep the conversation going."
        ),
        "anim": "CAT",
    },
    "Nano": {
        "label": "Nano",
        "color": "#1A6644",
        "bg": "#E8FFF4",
        "bubble": "#D1FFE9",
        "greeting": (
            "BEEP BOOP — Nano online! I am your robotic NanoLab assistant, "
            "optimised for precision answers on nanotechnology, semiconductor "
            "fabrication processes, and analytical instrumentation. My databanks "
            "contain detailed specifications for SEM, TEM, AFM, XRD, XPS, SIMS, "
            "Raman, ellipsometry, FTIR, and 4-point probe systems. Query received. "
            "How can I assist you today?"
        ),
        "system": (
            "You are Nano, a friendly robot assistant in a NanoLab who specialises in "
            "nanotechnology, semiconductor wafer fabrication (clean, deposit, lithography, "
            "etch, anneal), and characterisation instruments (SEM, TEM, AFM, XRD, XPS, "
            "SIMS, Raman, ellipsometry, FTIR, 4-point probe). Speak in a helpful, "
            "precise robot style with occasional 'BEEP', 'BOOP', or 'PROCESSING' "
            "interjections. Give accurate technical answers. Keep every reply under "
            "120 words. Always end with one follow-up question."
        ),
        "anim": "ROBOT",
    },
}

# ---------------------------------------------------------------------------
# Starter questions (shown early in chat)
# ---------------------------------------------------------------------------

STARTER_QUESTIONS = [
    "What is the difference between SEM and TEM?",
    "How does atomic layer deposition work?",
    "Why do we clean a wafer before depositing a film?",
    "What does an AFM actually measure?",
    "How small can lithography features get today?",
]

# ---------------------------------------------------------------------------
# SVG character animations
# ---------------------------------------------------------------------------

def get_animal_svg(anim_type: str, is_thinking: bool = False) -> str:
    """Return an animated SVG character for the given anim_type."""

    think_speed = "0.5s" if is_thinking else "1.8s"
    think_dots = ""
    if is_thinking:
        think_dots = """
        <g>
          <circle cx="58" cy="168" r="5" fill="#aaa">
            <animate attributeName="opacity" values="0.2;1;0.2" dur="0.8s"
                     begin="0s" repeatCount="indefinite"/>
          </circle>
          <circle cx="80" cy="168" r="5" fill="#aaa">
            <animate attributeName="opacity" values="0.2;1;0.2" dur="0.8s"
                     begin="0.27s" repeatCount="indefinite"/>
          </circle>
          <circle cx="102" cy="168" r="5" fill="#aaa">
            <animate attributeName="opacity" values="0.2;1;0.2" dur="0.8s"
                     begin="0.54s" repeatCount="indefinite"/>
          </circle>
        </g>"""

    # -----------------------------------------------------------------------
    # OWL – Professor Nova
    # -----------------------------------------------------------------------
    if anim_type == "OWL":
        bob_dur = "0.7s" if is_thinking else "2.2s"
        return f"""<svg viewBox="0 0 160 180" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .owl-body {{ animation: owlBob {bob_dur} ease-in-out infinite alternate; transform-origin: 80px 140px; }}
      @keyframes owlBob {{
        0%   {{ transform: translateY(0px) rotate(-1.5deg); }}
        100% {{ transform: translateY(-8px) rotate(1.5deg); }}
      }}
      .owl-blink {{
        animation: owlBlink 4s ease-in-out infinite;
        transform-origin: center;
      }}
      @keyframes owlBlink {{
        0%,44%,56%,100% {{ transform: scaleY(1); }}
        48%,52%          {{ transform: scaleY(0.05); }}
      }}
      .wing-l {{ animation: wingL 2.8s ease-in-out infinite alternate; transform-origin: 52px 115px; }}
      .wing-r {{ animation: wingR 2.8s ease-in-out infinite alternate; transform-origin: 108px 115px; }}
      @keyframes wingL {{
        0%   {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(-8deg); }}
      }}
      @keyframes wingR {{
        0%   {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(8deg); }}
      }}
    </style>
  </defs>
  <!-- Mortar board hat (static, stays at top) -->
  <rect x="45" y="28" width="70" height="8" rx="2" fill="#2c1a4a"/>
  <rect x="60" y="18" width="40" height="12" rx="3" fill="#2c1a4a"/>
  <line x1="80" y1="18" x2="96" y2="10" stroke="#2c1a4a" stroke-width="2"/>
  <circle cx="98" cy="9" r="4" fill="#FFD700"/>
  <!-- Animated body group -->
  <g class="owl-body">
    <!-- Body -->
    <ellipse cx="80" cy="125" rx="38" ry="48" fill="#8B5E3C"/>
    <!-- Belly -->
    <ellipse cx="80" cy="132" rx="22" ry="30" fill="#C8956A"/>
    <!-- Feather tufts -->
    <polygon points="56,82 62,68 68,82" fill="#6B4423"/>
    <polygon points="92,82 98,68 104,82" fill="#6B4423"/>
    <!-- Wings -->
    <ellipse class="wing-l" cx="52" cy="120" rx="16" ry="28" fill="#7A5030" transform="rotate(-8,52,120)"/>
    <ellipse class="wing-r" cx="108" cy="120" rx="16" ry="28" fill="#7A5030" transform="rotate(8,108,120)"/>
    <!-- Eye whites -->
    <circle cx="68" cy="100" r="13" fill="white" stroke="#4a3020" stroke-width="1.5"/>
    <circle cx="92" cy="100" r="13" fill="white" stroke="#4a3020" stroke-width="1.5"/>
    <!-- Irises -->
    <circle cx="68" cy="100" r="9" fill="#4A90D9"/>
    <circle cx="92" cy="100" r="9" fill="#4A90D9"/>
    <!-- Pupils -->
    <circle cx="68" cy="100" r="5" fill="#1a1a1a"/>
    <circle cx="92" cy="100" r="5" fill="#1a1a1a"/>
    <!-- Eye shine -->
    <circle cx="71" cy="97" r="2" fill="white"/>
    <circle cx="95" cy="97" r="2" fill="white"/>
    <!-- Blink overlay -->
    <rect class="owl-blink" x="55" y="89" width="26" height="22" rx="11" fill="#8B5E3C"/>
    <rect class="owl-blink" x="79" y="89" width="26" height="22" rx="11" fill="#8B5E3C"/>
    <!-- Beak -->
    <polygon points="76,110 84,110 80,120" fill="#E8A020"/>
    <!-- Feet -->
    <ellipse cx="68" cy="170" rx="10" ry="5" fill="#C8781A"/>
    <ellipse cx="92" cy="170" rx="10" ry="5" fill="#C8781A"/>
    <!-- Talon lines -->
    <line x1="60" y1="170" x2="57" y2="175" stroke="#C8781A" stroke-width="2"/>
    <line x1="68" y1="172" x2="68" y2="177" stroke="#C8781A" stroke-width="2"/>
    <line x1="76" y1="170" x2="79" y2="175" stroke="#C8781A" stroke-width="2"/>
    <line x1="84" y1="170" x2="81" y2="175" stroke="#C8781A" stroke-width="2"/>
    <line x1="92" y1="172" x2="92" y2="177" stroke="#C8781A" stroke-width="2"/>
    <line x1="100" y1="170" x2="103" y2="175" stroke="#C8781A" stroke-width="2"/>
  </g>
  {think_dots}
</svg>"""

    # -----------------------------------------------------------------------
    # FOX – Dr Foxy
    # -----------------------------------------------------------------------
    elif anim_type == "FOX":
        bounce_dur = "0.55s" if is_thinking else "1.6s"
        return f"""<svg viewBox="0 0 160 180" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .fox-body {{ animation: foxBounce {bounce_dur} ease-in-out infinite alternate; transform-origin: 80px 130px; }}
      @keyframes foxBounce {{
        0%   {{ transform: translateY(0px) rotate(-1deg); }}
        100% {{ transform: translateY(-7px) rotate(1deg); }}
      }}
      .fox-tail {{ animation: tailWag 0.9s ease-in-out infinite alternate; transform-origin: 40px 148px; }}
      @keyframes tailWag {{
        0%   {{ transform: rotate(-25deg); }}
        100% {{ transform: rotate(20deg); }}
      }}
      .fox-blink {{ animation: foxBlink 3.5s ease-in-out infinite; }}
      @keyframes foxBlink {{
        0%,42%,58%,100% {{ transform: scaleY(1); }}
        48%,52%          {{ transform: scaleY(0.06); }}
      }}
      .ear-l {{ animation: earTwitch 4s ease-in-out infinite; transform-origin: 58px 62px; }}
      .ear-r {{ animation: earTwitchR 4.5s ease-in-out infinite; transform-origin: 102px 62px; }}
      @keyframes earTwitch  {{ 0%,90%,100% {{ transform:rotate(0); }} 93% {{ transform:rotate(-8deg); }} }}
      @keyframes earTwitchR {{ 0%,85%,100% {{ transform:rotate(0); }} 88% {{ transform:rotate(8deg);  }} }}
    </style>
  </defs>
  <!-- Tail (behind body) -->
  <g class="fox-tail">
    <ellipse cx="38" cy="145" rx="20" ry="36" fill="#D4581A" transform="rotate(-30,38,145)"/>
    <ellipse cx="32" cy="132" rx="10" ry="18" fill="white" transform="rotate(-30,32,132)"/>
  </g>
  <!-- Body group -->
  <g class="fox-body">
    <!-- Ears -->
    <polygon class="ear-l" points="55,68 46,40 72,60" fill="#D4581A"/>
    <polygon points="57,66 50,47 68,62" fill="#F0A070"/>
    <polygon class="ear-r" points="105,68 114,40 88,60" fill="#D4581A"/>
    <polygon points="103,66 110,47 92,62" fill="#F0A070"/>
    <!-- Head -->
    <ellipse cx="80" cy="90" rx="36" ry="34" fill="#D4581A"/>
    <!-- White face mask -->
    <ellipse cx="80" cy="98" rx="22" ry="24" fill="#F5E0CC"/>
    <!-- Body -->
    <ellipse cx="80" cy="138" rx="30" ry="38" fill="#D4581A"/>
    <!-- Chest -->
    <ellipse cx="80" cy="144" rx="18" ry="24" fill="#F5E0CC"/>
    <!-- Eyes -->
    <ellipse cx="67" cy="88" rx="9" ry="9" fill="#1a1a1a"/>
    <ellipse cx="93" cy="88" rx="9" ry="9" fill="#1a1a1a"/>
    <!-- Eye shine -->
    <circle cx="70" cy="85" r="3" fill="white"/>
    <circle cx="96" cy="85" r="3" fill="white"/>
    <!-- Blink -->
    <rect class="fox-blink" x="58" y="80" width="18" height="16" rx="8" fill="#D4581A" style="transform-origin:67px 88px;"/>
    <rect class="fox-blink" x="84" y="80" width="18" height="16" rx="8" fill="#D4581A" style="transform-origin:93px 88px;"/>
    <!-- Nose -->
    <ellipse cx="80" cy="103" rx="6" ry="4.5" fill="#2a1010"/>
    <!-- Snout line -->
    <line x1="80" y1="107" x2="80" y2="112" stroke="#2a1010" stroke-width="1.5"/>
    <path d="M 72 112 Q 80 118 88 112" fill="none" stroke="#2a1010" stroke-width="1.5"/>
    <!-- Lab coat collar / tie -->
    <polygon points="74,162 80,172 86,162 80,158" fill="#3a6fc4"/>
    <rect x="66" y="158" width="14" height="6" rx="1" fill="white" transform="rotate(-8,73,161)"/>
    <rect x="80" y="158" width="14" height="6" rx="1" fill="white" transform="rotate(8,87,161)"/>
    <!-- Paws -->
    <ellipse cx="62" cy="170" rx="12" ry="7" fill="#D4581A"/>
    <ellipse cx="98" cy="170" rx="12" ry="7" fill="#D4581A"/>
  </g>
  {think_dots}
</svg>"""

    # -----------------------------------------------------------------------
    # CAT – Pixel
    # -----------------------------------------------------------------------
    elif anim_type == "CAT":
        sway_dur = "0.6s" if is_thinking else "2.5s"
        return f"""<svg viewBox="0 0 160 180" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .cat-body {{ animation: catSway {sway_dur} ease-in-out infinite alternate; transform-origin: 80px 130px; }}
      @keyframes catSway {{
        0%   {{ transform: rotate(-2deg) translateY(0px); }}
        100% {{ transform: rotate(2deg) translateY(-6px); }}
      }}
      .cat-tail {{ animation: tailSway 1.8s ease-in-out infinite; transform-origin: 115px 152px; }}
      @keyframes tailSway {{
        0%   {{ transform: rotate(-30deg); }}
        50%  {{ transform: rotate(20deg); }}
        100% {{ transform: rotate(-30deg); }}
      }}
      .cat-blink {{
        animation: catBlink 5s ease-in-out infinite;
        transform-origin: center;
      }}
      @keyframes catBlink {{
        0%,46%,54%,100% {{ transform: scaleY(1); }}
        49%,51%          {{ transform: scaleY(0.05); }}
      }}
      .ear-twitch-l {{ animation: catEarL 3s ease-in-out infinite; transform-origin: 56px 58px; }}
      .ear-twitch-r {{ animation: catEarR 3.7s ease-in-out infinite; transform-origin: 104px 58px; }}
      @keyframes catEarL {{ 0%,88%,100% {{ transform:rotate(0); }} 92% {{ transform:rotate(-10deg); }} }}
      @keyframes catEarR {{ 0%,80%,100% {{ transform:rotate(0); }} 84% {{ transform:rotate(10deg); }} }}
    </style>
  </defs>
  <!-- Tail -->
  <g class="cat-tail">
    <path d="M 115 152 Q 148 130 145 100 Q 148 80 135 75" fill="none"
          stroke="#7B4BB0" stroke-width="10" stroke-linecap="round"/>
    <path d="M 115 152 Q 148 130 145 100 Q 148 80 135 75" fill="none"
          stroke="#9B6BD0" stroke-width="6" stroke-linecap="round"/>
    <!-- Tail tip -->
    <ellipse cx="134" cy="73" rx="10" ry="8" fill="#D0A8FF" transform="rotate(-20,134,73)"/>
  </g>
  <!-- Body group -->
  <g class="cat-body">
    <!-- Ears -->
    <polygon class="ear-twitch-l" points="52,70 42,38 72,62" fill="#7B4BB0"/>
    <polygon points="54,68 46,46 68,63" fill="#D0A8FF"/>
    <polygon class="ear-twitch-r" points="108,70 118,38 88,62" fill="#7B4BB0"/>
    <polygon points="106,68 114,46 92,63" fill="#D0A8FF"/>
    <!-- Head -->
    <ellipse cx="80" cy="92" rx="38" ry="36" fill="#8B55C0"/>
    <!-- Face marking (lighter muzzle) -->
    <ellipse cx="80" cy="104" rx="20" ry="16" fill="#B080E0"/>
    <!-- Body -->
    <ellipse cx="80" cy="142" rx="32" ry="36" fill="#8B55C0"/>
    <!-- Belly -->
    <ellipse cx="80" cy="148" rx="18" ry="22" fill="#C090F0"/>
    <!-- Collar with tag -->
    <rect x="57" y="156" width="46" height="9" rx="4" fill="#FF7BAC"/>
    <circle cx="80" cy="165" r="6" fill="#FFD700" stroke="#E0A000" stroke-width="1"/>
    <text x="80" y="168" text-anchor="middle" font-family="monospace" font-size="6" fill="#8B6000">N</text>
    <!-- Eyes — almond shaped -->
    <ellipse cx="67" cy="89" rx="11" ry="10" fill="#F0E0FF"/>
    <ellipse cx="93" cy="89" rx="11" ry="10" fill="#F0E0FF"/>
    <!-- Slit pupils -->
    <ellipse cx="67" cy="89" rx="5" ry="9" fill="#1a0a2a"/>
    <ellipse cx="93" cy="89" rx="5" ry="9" fill="#1a0a2a"/>
    <!-- Iris ring -->
    <ellipse cx="67" cy="89" rx="8" ry="9" fill="none" stroke="#8040C0" stroke-width="1.5"/>
    <ellipse cx="93" cy="89" rx="8" ry="9" fill="none" stroke="#8040C0" stroke-width="1.5"/>
    <!-- Eye shine -->
    <circle cx="70" cy="86" r="2.5" fill="white"/>
    <circle cx="96" cy="86" r="2.5" fill="white"/>
    <!-- Blink (slow) -->
    <rect class="cat-blink" x="56" y="80" width="22" height="18" rx="9" fill="#8B55C0" style="transform-origin:67px 89px;"/>
    <rect class="cat-blink" x="82" y="80" width="22" height="18" rx="9" fill="#8B55C0" style="transform-origin:93px 89px;"/>
    <!-- Nose -->
    <polygon points="80,105 75,110 85,110" fill="#FF80B0"/>
    <!-- Whiskers -->
    <line x1="44" y1="106" x2="70" y2="110" stroke="#D0B0F0" stroke-width="1.2"/>
    <line x1="44" y1="112" x2="70" y2="112" stroke="#D0B0F0" stroke-width="1.2"/>
    <line x1="44" y1="118" x2="70" y2="114" stroke="#D0B0F0" stroke-width="1.2"/>
    <line x1="116" y1="106" x2="90" y2="110" stroke="#D0B0F0" stroke-width="1.2"/>
    <line x1="116" y1="112" x2="90" y2="112" stroke="#D0B0F0" stroke-width="1.2"/>
    <line x1="116" y1="118" x2="90" y2="114" stroke="#D0B0F0" stroke-width="1.2"/>
    <!-- Smile -->
    <path d="M 73 116 Q 80 122 87 116" fill="none" stroke="#8040C0" stroke-width="1.5"/>
    <!-- Paws -->
    <ellipse cx="60" cy="172" rx="14" ry="8" fill="#8B55C0"/>
    <ellipse cx="100" cy="172" rx="14" ry="8" fill="#8B55C0"/>
    <!-- Paw toes -->
    <ellipse cx="54" cy="172" rx="4" ry="3" fill="#9B65D0"/>
    <ellipse cx="60" cy="174" rx="4" ry="3" fill="#9B65D0"/>
    <ellipse cx="66" cy="172" rx="4" ry="3" fill="#9B65D0"/>
    <ellipse cx="94" cy="172" rx="4" ry="3" fill="#9B65D0"/>
    <ellipse cx="100" cy="174" rx="4" ry="3" fill="#9B65D0"/>
    <ellipse cx="106" cy="172" rx="4" ry="3" fill="#9B65D0"/>
  </g>
  {think_dots}
</svg>"""

    # -----------------------------------------------------------------------
    # ROBOT – Nano
    # -----------------------------------------------------------------------
    else:  # ROBOT
        pulse_dur = "0.4s" if is_thinking else "2.0s"
        gear_dur = "1.5s" if is_thinking else "5s"
        return f"""<svg viewBox="0 0 160 180" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .robot-body {{ animation: robotPulse {pulse_dur} ease-in-out infinite alternate; transform-origin: 80px 130px; }}
      @keyframes robotPulse {{
        0%   {{ transform: translateY(0px); }}
        100% {{ transform: translateY(-5px); }}
      }}
      .led-l {{ animation: ledBlink 2.4s step-end infinite; }}
      .led-r {{ animation: ledBlink 2.4s step-end infinite 1.2s; }}
      @keyframes ledBlink {{
        0%,45%,55%,100% {{ fill: #00FF88; }}
        48%,52%          {{ fill: #003322; }}
      }}
      .gear {{ animation: gearSpin {gear_dur} linear infinite; transform-origin: 126px 72px; }}
      @keyframes gearSpin {{ 0% {{ transform:rotate(0deg); }} 100% {{ transform:rotate(360deg); }} }}
      .antenna {{ animation: antennaPing 3s ease-in-out infinite; transform-origin: 80px 22px; }}
      @keyframes antennaPing {{
        0%,100% {{ transform: rotate(-4deg); }}
        50%      {{ transform: rotate(4deg); }}
      }}
      .panel-glow {{ animation: panelPulse 2s ease-in-out infinite; }}
      @keyframes panelPulse {{
        0%,100% {{ opacity:0.6; }}
        50%      {{ opacity:1; }}
      }}
      .arm-l {{ animation: armSwingL 1.8s ease-in-out infinite alternate; transform-origin: 46px 120px; }}
      .arm-r {{ animation: armSwingR 1.8s ease-in-out infinite alternate; transform-origin: 114px 120px; }}
      @keyframes armSwingL {{ 0% {{ transform:rotate(-8deg); }} 100% {{ transform:rotate(8deg); }} }}
      @keyframes armSwingR {{ 0% {{ transform:rotate(8deg); }} 100% {{ transform:rotate(-8deg); }} }}
    </style>
  </defs>
  <!-- Antenna -->
  <g class="antenna">
    <line x1="80" y1="36" x2="80" y2="16" stroke="#2a6644" stroke-width="3"/>
    <circle cx="80" cy="13" r="6" fill="#00CC66" stroke="#1a4433" stroke-width="1.5"/>
    <circle cx="80" cy="13" r="3" fill="#00FF88">
      <animate attributeName="opacity" values="0.5;1;0.5" dur="1.2s" repeatCount="indefinite"/>
    </circle>
  </g>
  <!-- Gear (top right) -->
  <g class="gear">
    <circle cx="126" cy="72" r="14" fill="none" stroke="#1a6644" stroke-width="4"
            stroke-dasharray="6 4"/>
    <circle cx="126" cy="72" r="6" fill="#1a6644"/>
    <circle cx="126" cy="72" r="3" fill="#00FF88" opacity="0.7"/>
  </g>
  <!-- Body group -->
  <g class="robot-body">
    <!-- Head / box -->
    <rect x="44" y="36" width="72" height="62" rx="10" fill="#1A3D2A" stroke="#2a6644" stroke-width="2.5"/>
    <!-- Head rivets -->
    <circle cx="52" cy="44" r="3" fill="#2a6644"/>
    <circle cx="108" cy="44" r="3" fill="#2a6644"/>
    <circle cx="52" cy="90" r="3" fill="#2a6644"/>
    <circle cx="108" cy="90" r="3" fill="#2a6644"/>
    <!-- Eye panels -->
    <rect x="52" y="52" width="22" height="22" rx="5" fill="#0a1f14" stroke="#1a6644" stroke-width="1.5"/>
    <rect x="86" y="52" width="22" height="22" rx="5" fill="#0a1f14" stroke="#1a6644" stroke-width="1.5"/>
    <!-- LED eyes -->
    <rect class="led-l" x="56" y="56" width="14" height="14" rx="3" fill="#00FF88"/>
    <rect class="led-r" x="90" y="56" width="14" height="14" rx="3" fill="#00FF88"/>
    <!-- Scan line in eyes -->
    <line x1="56" y1="63" x2="70" y2="63" stroke="#003322" stroke-width="2" opacity="0.6"/>
    <line x1="90" y1="63" x2="104" y2="63" stroke="#003322" stroke-width="2" opacity="0.6"/>
    <!-- Speaker grill / mouth -->
    <rect x="56" y="82" width="48" height="10" rx="3" fill="#0a1f14" stroke="#1a6644" stroke-width="1"/>
    <line x1="62" y1="87" x2="62" y2="87" stroke="#00FF88" stroke-width="2"/>
    <line x1="68" y1="84" x2="68" y2="90" stroke="#00FF88" stroke-width="2"/>
    <line x1="74" y1="85" x2="74" y2="89" stroke="#00FF88" stroke-width="2"/>
    <line x1="80" y1="83" x2="80" y2="91" stroke="#00FF88" stroke-width="2"/>
    <line x1="86" y1="85" x2="86" y2="89" stroke="#00FF88" stroke-width="2"/>
    <line x1="92" y1="84" x2="92" y2="90" stroke="#00FF88" stroke-width="2"/>
    <line x1="98" y1="87" x2="98" y2="87" stroke="#00FF88" stroke-width="2"/>
    <!-- Neck -->
    <rect x="70" y="98" width="20" height="10" rx="3" fill="#152d1e" stroke="#1a6644" stroke-width="1.5"/>
    <!-- Torso -->
    <rect x="42" y="108" width="76" height="56" rx="8" fill="#1A3D2A" stroke="#2a6644" stroke-width="2"/>
    <!-- Chest panel -->
    <rect x="52" y="116" width="56" height="38" rx="5" fill="#0a1f14" stroke="#1a6644" stroke-width="1.5"/>
    <!-- Status LEDs -->
    <circle cx="62" cy="124" r="4" fill="#00FF88" class="panel-glow"/>
    <circle cx="74" cy="124" r="4" fill="#FFD700" class="panel-glow" style="animation-delay:0.4s"/>
    <circle cx="86" cy="124" r="4" fill="#00AAFF" class="panel-glow" style="animation-delay:0.8s"/>
    <circle cx="98" cy="124" r="4" fill="#FF4444" class="panel-glow" style="animation-delay:1.2s"/>
    <!-- Data display bar -->
    <rect x="56" y="132" width="48" height="6" rx="3" fill="#001a0d"/>
    <rect x="56" y="132" width="32" height="6" rx="3" fill="#00FF88" opacity="0.8">
      <animate attributeName="width" values="10;44;10" dur="2.5s" repeatCount="indefinite"/>
    </rect>
    <!-- Nano logo -->
    <text x="80" y="148" text-anchor="middle" font-family="monospace" font-size="9"
          fill="#00FF88" opacity="0.8">NANO v1</text>
    <!-- Arms -->
    <rect class="arm-l" x="22" y="108" width="20" height="44" rx="8" fill="#1A3D2A" stroke="#2a6644" stroke-width="1.5"/>
    <rect class="arm-r" x="118" y="108" width="20" height="44" rx="8" fill="#1A3D2A" stroke="#2a6644" stroke-width="1.5"/>
    <!-- Hands -->
    <ellipse cx="32" cy="158" rx="11" ry="9" fill="#152d1e" stroke="#2a6644" stroke-width="1.5"/>
    <ellipse cx="128" cy="158" rx="11" ry="9" fill="#152d1e" stroke="#2a6644" stroke-width="1.5"/>
    <!-- Legs -->
    <rect x="56" y="164" width="18" height="14" rx="4" fill="#152d1e" stroke="#1a6644" stroke-width="1.5"/>
    <rect x="86" y="164" width="18" height="14" rx="4" fill="#152d1e" stroke="#1a6644" stroke-width="1.5"/>
    <!-- Feet -->
    <rect x="52" y="173" width="26" height="8" rx="4" fill="#0a1f14" stroke="#1a6644" stroke-width="1"/>
    <rect x="82" y="173" width="26" height="8" rx="4" fill="#0a1f14" stroke="#1a6644" stroke-width="1"/>
  </g>
  {think_dots}
</svg>"""


# ---------------------------------------------------------------------------
# Chat bubble renderer
# ---------------------------------------------------------------------------

def render_chat_bubble(
    role: str,
    text: str,
    char_data: dict,
    is_thinking: bool = False,
) -> str:
    """
    Return an HTML string for a single chat message bubble.
    Assistant messages: SVG avatar left, bubble right.
    User messages: bubble right-aligned with gray background.
    """
    if role == "user":
        return f"""
<div style="display:flex; justify-content:flex-end; margin:10px 0; align-items:flex-end; gap:8px;">
  <div style="
    background:#E9EBEE;
    color:#1a1a2e;
    border-radius:16px 16px 4px 16px;
    padding:12px 16px;
    max-width:72%;
    font-size:0.93rem;
    line-height:1.55;
    box-shadow:0 1px 3px rgba(0,0,0,0.08);
    font-family:'Inter',sans-serif;
  ">{text}</div>
  <div style="
    width:36px; height:36px;
    background:#CBD2DA;
    border-radius:50%;
    display:flex; align-items:center; justify-content:center;
    font-size:1.1rem; flex-shrink:0;
  ">🧑‍🔬</div>
</div>"""

    # Assistant message
    svg_content = get_animal_svg(char_data["anim"], is_thinking=is_thinking)
    if is_thinking:
        bubble_content = """
<div style="display:flex; gap:5px; align-items:center; padding:4px 2px;">
  <span style="width:9px;height:9px;border-radius:50%;background:#888;display:inline-block;
    animation:dotPulse 0.8s ease-in-out infinite;"></span>
  <span style="width:9px;height:9px;border-radius:50%;background:#888;display:inline-block;
    animation:dotPulse 0.8s ease-in-out 0.27s infinite;"></span>
  <span style="width:9px;height:9px;border-radius:50%;background:#888;display:inline-block;
    animation:dotPulse 0.8s ease-in-out 0.54s infinite;"></span>
</div>"""
    else:
        bubble_content = f'<span style="font-size:0.93rem;line-height:1.6;">{text}</span>'

    return f"""
<div style="display:flex; justify-content:flex-start; margin:10px 0; align-items:flex-end; gap:10px;">
  <div style="
    width:70px; height:80px;
    background:{char_data['bg']};
    border-radius:12px;
    border:2px solid {char_data['color']}44;
    flex-shrink:0;
    overflow:hidden;
    display:flex; align-items:center; justify-content:center;
  ">
    <div style="width:60px; height:70px; overflow:hidden;">{svg_content}</div>
  </div>
  <div style="
    background:{char_data['bubble']};
    color:#1a1a2e;
    border-radius:16px 16px 16px 4px;
    padding:13px 17px;
    max-width:70%;
    box-shadow:0 1px 4px rgba(0,0,0,0.1);
    border:1.5px solid {char_data['color']}22;
    font-family:'Inter',sans-serif;
  ">{bubble_content}</div>
</div>"""


# ---------------------------------------------------------------------------
# Main chatbot render function
# ---------------------------------------------------------------------------

def render_nano_chatbot(api_key: str):
    """Render the full NanoLab character chatbot Streamlit app."""

    # ── Page styling ───────────────────────────────────────────────────────
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .chat-title {
        font-family: 'Space Mono', monospace;
        font-size: 1.9rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    .char-card {
        border-radius: 16px;
        padding: 18px 14px;
        text-align: center;
        cursor: pointer;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        border: 2px solid transparent;
    }

    .char-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    }

    .char-name {
        font-family: 'Space Mono', monospace;
        font-weight: 700;
        font-size: 0.95rem;
        margin-top: 6px;
    }

    .starter-chip {
        display:inline-block;
        padding:7px 14px;
        border-radius:20px;
        font-size:0.82rem;
        cursor:pointer;
        margin:4px;
        border:1.5px solid;
        font-family:'Inter',sans-serif;
    }

    .stTextInput input {
        font-family: 'Inter', sans-serif;
        border-radius: 10px !important;
    }

    .stButton>button {
        font-family: 'Space Mono', monospace;
        font-weight: 700;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Session state init ─────────────────────────────────────────────────
    if "selected_character" not in st.session_state:
        st.session_state.selected_character = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # ── Title ──────────────────────────────────────────────────────────────
    st.markdown(
        '<p class="chat-title">🔬 NanoLab Chat</p>',
        unsafe_allow_html=True,
    )
    st.caption("Ask your NanoLab guide anything about nanotechnology, wafer fabrication, and characterisation tools.")

    # ── CHARACTER SELECTION SCREEN ─────────────────────────────────────────
    if st.session_state.selected_character is None:
        st.markdown("### Choose your guide")
        st.markdown("Each guide has a different personality — pick the one you vibe with!")
        st.markdown("<br>", unsafe_allow_html=True)

        char_keys = list(CHARACTERS.keys())
        cols = st.columns(4)

        for col, key in zip(cols, char_keys):
            char = CHARACTERS[key]
            with col:
                svg = get_animal_svg(char["anim"], is_thinking=False)
                st.markdown(
                    f"""<div class="char-card" style="background:{char['bg']};
                        border-color:{char['color']}44;">
                      <div style="width:100%; height:130px; overflow:hidden;
                                  display:flex; align-items:center; justify-content:center;">
                        <div style="width:110px; height:130px; overflow:hidden;">{svg}</div>
                      </div>
                      <div class="char-name" style="color:{char['color']};">{char['label']}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
                st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
                if st.button(f"Choose {char['label']}", key=f"choose_{key}", use_container_width=True):
                    st.session_state.selected_character = key
                    st.session_state.chat_history = [
                        {"role": "assistant", "content": char["greeting"]}
                    ]
                    st.rerun()
        return

    # ── CHAT SCREEN ────────────────────────────────────────────────────────
    char_key = st.session_state.selected_character
    char = CHARACTERS[char_key]

    # Header row
    header_col1, header_col2 = st.columns([5, 1])
    with header_col1:
        st.markdown(
            f'<div style="display:flex; align-items:center; gap:12px;">'
            f'<div style="width:48px;height:48px;background:{char["bg"]};border-radius:12px;'
            f'border:2px solid {char["color"]}44; overflow:hidden; display:flex; '
            f'align-items:center; justify-content:center;">'
            f'<div style="width:44px;height:52px;overflow:hidden;">'
            f'{get_animal_svg(char["anim"])}</div></div>'
            f'<div><div style="font-family:Space Mono,monospace; font-weight:700; '
            f'font-size:1.1rem; color:{char["color"]};">{char["label"]}</div>'
            f'<div style="font-size:0.78rem; color:#666;">NanoLab Guide · Nanotechnology & Fabrication</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
    with header_col2:
        if st.button("↩ Change\nguide", key="change_guide"):
            st.session_state.selected_character = None
            st.session_state.chat_history = []
            st.rerun()

    st.divider()

    # ── Build chat HTML ────────────────────────────────────────────────────
    history = st.session_state.chat_history
    bubble_html_parts = []

    for msg in history:
        bubble_html_parts.append(
            render_chat_bubble(msg["role"], msg["content"], char, is_thinking=False)
        )

    dot_anim_css = """
    <style>
    @keyframes dotPulse {
      0%,100% { opacity:0.2; transform:scale(0.8); }
      50% { opacity:1; transform:scale(1.1); }
    }
    </style>
    """

    full_chat_html = f"""
    <!DOCTYPE html><html><head>
    {dot_anim_css}
    <style>
      * {{ box-sizing:border-box; margin:0; padding:0; }}
      body {{
        font-family:'Inter',sans-serif;
        background:#FAFBFC;
        padding:12px;
        overflow-y:auto;
        height:450px;
      }}
      ::-webkit-scrollbar {{ width:5px; }}
      ::-webkit-scrollbar-track {{ background:#f0f0f0; border-radius:4px; }}
      ::-webkit-scrollbar-thumb {{ background:#ccc; border-radius:4px; }}
    </style>
    </head><body>
    {''.join(bubble_html_parts)}
    <div id="chat-bottom"></div>
    <script>
      document.getElementById('chat-bottom').scrollIntoView({{behavior:'smooth'}});
    </script>
    </body></html>"""

    components.html(full_chat_html, height=450, scrolling=True)

    # ── Starter question chips (shown when ≤1 message in history) ─────────
    if len(history) <= 1:
        st.markdown("**Suggested questions:**")
        chip_cols = st.columns(len(STARTER_QUESTIONS))
        for i, (chip_col, question) in enumerate(zip(chip_cols, STARTER_QUESTIONS)):
            with chip_col:
                if st.button(
                    question,
                    key=f"starter_{i}",
                    use_container_width=True,
                    help=question,
                ):
                    st.session_state.chat_history.append(
                        {"role": "user", "content": question}
                    )
                    _call_claude_and_append(char, api_key)
                    st.rerun()

    # ── Chat input form ────────────────────────────────────────────────────
    with st.form(key="chat_form", clear_on_submit=True):
        input_col, btn_col = st.columns([6, 1])
        with input_col:
            user_input = st.text_input(
                "Your question",
                placeholder=f"Ask {char['label']} anything about nanotechnology...",
                label_visibility="collapsed",
            )
        with btn_col:
            submitted = st.form_submit_button("Send ➤", use_container_width=True)

    if submitted and user_input.strip():
        st.session_state.chat_history.append(
            {"role": "user", "content": user_input.strip()}
        )
        _call_claude_and_append(char, api_key)
        st.rerun()


# ---------------------------------------------------------------------------
# Internal helper — calls Claude and appends assistant reply
# ---------------------------------------------------------------------------

def _call_claude_and_append(char: dict, api_key: str):
    """
    Call Claude with the current chat history and append the reply.

    The Anthropic API requires the messages array to begin with a 'user' role
    message. The chat history may start with the character greeting (role =
    'assistant'), so we skip any leading assistant turns before sending.
    """
    client = anthropic.Anthropic(api_key=api_key)

    history = st.session_state.chat_history

    # Build the messages array from history
    messages = [{"role": msg["role"], "content": msg["content"]} for msg in history]

    # ── FIX: Anthropic API requires messages to start with 'user' role ──────
    # The greeting is stored as an assistant message at index 0.  Drop any
    # leading assistant turns so the first message sent to the API is always
    # from the user.
    while messages and messages[0]["role"] == "assistant":
        messages = messages[1:]

    if not messages:
        # Nothing to send — this shouldn't happen in normal flow
        return

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            system=char["system"],
            messages=messages,
        )
        reply_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                reply_text += block.text
        reply_text = reply_text.strip() or "Hmm, something went quiet in the NanoLab — try again!"
    except anthropic.APIConnectionError:
        reply_text = "⚠️ Connection error — I can't reach the Anthropic API right now. Check your internet and try again."
    except anthropic.AuthenticationError:
        reply_text = "⚠️ Invalid API key. Please check your Anthropic API key in the app settings."
    except anthropic.RateLimitError:
        reply_text = "⚠️ Rate limit reached — give me a moment to catch my breath and try again!"
    except anthropic.BadRequestError as e:
        # Surface the actual API error message for easier debugging
        reply_text = f"⚠️ API request error: {e}"
    except Exception as e:
        reply_text = f"⚠️ Something went wrong: {e}"

    st.session_state.chat_history.append(
        {"role": "assistant", "content": reply_text}
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    st.set_page_config(
        page_title="NanoLab Chat",
        page_icon="🔬",
        layout="wide",
    )
    _api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not _api_key:
        st.error(
            "No Anthropic API key found. "
            "Set the `ANTHROPIC_API_KEY` environment variable and restart."
        )
        st.stop()
    render_nano_chatbot(_api_key)