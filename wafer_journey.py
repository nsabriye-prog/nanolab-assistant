import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------------------------------------------------
# Stage data
# ---------------------------------------------------------------------------

STAGES = [
    {
        "name": "Clean",
        "icon": "🧼",
        "color": "#185FA5",
        "bg": "#E6F1FB",
        "analogy": "Like scrubbing your hands before surgery — one speck of dust ruins everything.",
        "what_happens": (
            "The silicon wafer is immersed in a series of chemical baths (RCA clean) "
            "to strip organic residues, metallic contaminants, and native oxide layers. "
            "High-purity deionized water rinses follow each chemical step. "
            "Even a single particle smaller than 100 nm can cause a device to fail, "
            "so cleanroom air quality (Class 10–1000) and gowning protocols are strictly enforced."
        ),
        "what_goes_wrong": [
            "Particulate contamination from operator clothing or tools causes pinholes in gate oxide",
            "Incomplete organic removal leaves a carbon 'shadow' that blocks subsequent film growth",
            "Metallic ions (Fe, Cu, Na) diffuse into silicon and poison carrier lifetime",
        ],
        "tools": [
            "RCA wet bench (SC-1 and SC-2 chemical baths)",
            "Megasonic cleaning tank (high-frequency agitation)",
            "Particle counter / surface scan (KLA Surfscan SP3)",
        ],
        "fun_fact": (
            "A modern fab keeps its cleanroom 1,000× cleaner than a hospital operating theatre. "
            "The air is exchanged 600 times per hour, and engineers wear full bunny suits "
            "so that human skin flakes never reach the wafer."
        ),
    },
    {
        "name": "Deposit",
        "icon": "⬇️",
        "color": "#0F6E56",
        "bg": "#E1F5EE",
        "analogy": "Like spray-painting an extremely thin, perfectly even coat — one atom at a time.",
        "what_happens": (
            "A thin film (oxide, nitride, metal, or semiconductor) is grown or deposited "
            "on the wafer surface. Techniques include Chemical Vapour Deposition (CVD), "
            "Atomic Layer Deposition (ALD), Physical Vapour Deposition (PVD/sputtering), "
            "and thermal oxidation. ALD grows films one atomic monolayer at a time using "
            "alternating precursor pulses, giving angstrom-level thickness control. "
            "Film thickness, uniformity, stress, and density are critical outputs."
        ),
        "what_goes_wrong": [
            "Non-uniform deposition creates thickness variation across the wafer (poor within-wafer uniformity)",
            "Voids or seams form when filling high-aspect-ratio trenches (pinch-off effect in CVD)",
            "Residual film stress causes wafer bow or even delamination during subsequent heating steps",
        ],
        "tools": [
            "ALD reactor (e.g., ASM Pulsar 3000) for angstrom-precise oxide/nitride growth",
            "Sputter deposition system (PVD) for metals like TiN, W, Cu",
            "Spectroscopic ellipsometer for non-contact thickness and refractive-index measurement",
        ],
        "fun_fact": (
            "ALD films are so conformal that they coat the inside of a straw with perfectly uniform "
            "thickness — the technique is used to line the nanochannel pores of fuel-cell membranes "
            "and even to waterproof woven fabric at the atomic scale."
        ),
    },
    {
        "name": "Lithography",
        "icon": "🔆",
        "color": "#E65100",
        "bg": "#FFF3E0",
        "analogy": "Like projecting a microscopic stencil onto light-sensitive paint, then washing away what you don't need.",
        "what_happens": (
            "A light-sensitive polymer (photoresist) is spin-coated onto the wafer. "
            "A mask containing the circuit pattern is then aligned with nanometre precision "
            "and UV (or EUV) light exposes selected regions. Exposed regions either harden "
            "(negative resist) or become soluble (positive resist) and are washed away in developer. "
            "The remaining resist acts as a temporary etch mask. "
            "EUV lithography uses 13.5 nm wavelength light to print features below 5 nm."
        ),
        "what_goes_wrong": [
            "Focus/dose variation across the exposure field creates critical-dimension (CD) errors",
            "Mask misalignment (overlay error) shifts layers out of registration, short-circuiting transistors",
            "Standing waves in the resist from reflective substrates cause scalloped line-edge roughness",
        ],
        "tools": [
            "EUV scanner (ASML NXE:3600D) or ArF immersion stepper for production",
            "Spin-coat and develop track (TEL CLEAN TRACK ACT) for resist processing",
            "CD-SEM (critical-dimension SEM) for measuring printed feature widths",
        ],
        "fun_fact": (
            "The ASML EUV machine required to print leading-edge chips costs over €180 million, "
            "weighs 180 tonnes, and is so complex it must be shipped in three Boeing 747 cargo planes. "
            "Only one company in the world builds it."
        ),
    },
    {
        "name": "Etch",
        "icon": "⚡",
        "color": "#A32D2D",
        "bg": "#FCE8E8",
        "analogy": "Like a tiny sandblaster guided by a stencil — carving precise channels into rock.",
        "what_happens": (
            "Material is selectively removed from unmasked areas using plasma (dry etch) "
            "or wet chemicals. Reactive ion etching (RIE) bombards the surface with chemically "
            "reactive plasma ions that simultaneously sputter and react with exposed material, "
            "enabling near-vertical sidewalls with aspect ratios above 50:1. "
            "Etch selectivity (how fast the target etches vs. the mask or underlying layer) "
            "and etch uniformity across the wafer are the critical process metrics."
        ),
        "what_goes_wrong": [
            "Over-etching punches through the target layer into the layer below (loss of selectivity)",
            "Micro-loading effect: densely patterned regions etch faster than isolated features",
            "Sidewall notching or bowing distorts the transistor gate shape and degrades electrical performance",
        ],
        "tools": [
            "Inductively Coupled Plasma (ICP-RIE) etcher for high-aspect-ratio silicon structures",
            "Wet etch bench (BHF for SiO2, KOH for anisotropic silicon etching)",
            "Optical emission spectroscopy (OES) for real-time etch endpoint detection",
        ],
        "fun_fact": (
            "Deep reactive ion etching (DRIE) can carve silicon trenches 500 µm deep with walls "
            "so vertical they deviate less than 1° — the same process is used to make the "
            "microscopic accelerometers inside every smartphone that detects your screen orientation."
        ),
    },
    {
        "name": "Anneal",
        "icon": "🔥",
        "color": "#B45309",
        "bg": "#FEF3C7",
        "analogy": "Like firing pottery in a kiln — heat locks in the structure and activates what was implanted.",
        "what_happens": (
            "The wafer is heated in a controlled atmosphere (N₂, O₂, or forming gas) to repair "
            "crystal damage, activate implanted dopants, densify deposited films, or drive "
            "interdiffusion at metal contacts. Rapid Thermal Processing (RTP) ramps to 1000 °C "
            "in seconds to minimize unwanted dopant redistribution. "
            "Laser spike anneal can heat only the top few nanometres in microseconds, "
            "activating dopants without moving them at all."
        ),
        "what_goes_wrong": [
            "Dopant diffusion during long/hot anneals blurs the abrupt junction profiles needed for fast transistors",
            "Silicide agglomeration at high temperatures increases contact resistance",
            "Thermal stress at film interfaces causes delamination or cracking in brittle dielectric layers",
        ],
        "tools": [
            "Rapid Thermal Processor (RTP, e.g., Applied Materials RadiancePlus) for spike anneals",
            "Horizontal diffusion furnace for thick-oxide growth and batch dopant drives",
            "4-point probe for measuring sheet resistance before and after anneal to verify dopant activation",
        ],
        "fun_fact": (
            "A modern laser anneal heats a 300 mm wafer surface to over 1300 °C and cools it back "
            "down in under a millisecond — faster than a camera flash. The silicon underneath "
            "never even feels it; it stays near room temperature the whole time."
        ),
    },
    {
        "name": "Characterize",
        "icon": "🔬",
        "color": "#534AB7",
        "bg": "#EEEDFE",
        "analogy": "Like the final quality-control inspection — measuring every dimension and property before shipping.",
        "what_happens": (
            "A battery of physical, chemical, and electrical measurements verifies that every "
            "previous process step performed correctly. Scanning electron microscopy (SEM) images "
            "critical dimensions. XPS and SIMS probe surface chemistry and dopant profiles. "
            "Electrical parametric tests on in-line test structures check transistor threshold voltage, "
            "leakage current, and contact resistance. Data from all these tools feeds statistical "
            "process control (SPC) dashboards that trigger alarms if any metric drifts out of spec."
        ),
        "what_goes_wrong": [
            "Electron-beam damage from SEM or TEM alters ultrathin gate oxides during cross-section imaging",
            "Sample contamination during FIB lamella preparation introduces gallium implant artefacts in TEM analysis",
            "Incorrect optical model in ellipsometry fitting gives a wrong thickness for high-k/metal-gate stacks",
        ],
        "tools": [
            "Field-emission SEM (FE-SEM) with EDS for morphology and elemental mapping",
            "X-ray photoelectron spectroscopy (XPS) for surface bonding state and composition (top ~10 nm)",
            "Secondary Ion Mass Spectrometry (SIMS) for dopant depth profiling down to ppb concentrations",
        ],
        "fun_fact": (
            "A single 300 mm production wafer can carry over 700 individual chips, and every one "
            "is electrically tested by a robotic prober before dicing. A leading-edge fab runs "
            "more than 1,000 parametric measurements per wafer — automatically, in under 60 seconds."
        ),
    },
]

# ---------------------------------------------------------------------------
# SVG animations
# ---------------------------------------------------------------------------

def get_stage_svg(stage_index: int) -> str:
    """Return an animated SVG string for the given wafer process stage."""

    svgs = [
        # ------------------------------------------------------------------
        # Stage 0 – Clean: bubbles rising in a chemical bath
        # ------------------------------------------------------------------
        """<svg viewBox="0 0 400 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bathGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#aee6ff" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#1a8fc1" stop-opacity="0.95"/>
    </linearGradient>
    <linearGradient id="waferGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#e8f4fc"/>
      <stop offset="100%" stop-color="#b0cfe8"/>
    </linearGradient>
    <style>
      .bubble { animation: rise linear infinite; opacity: 0; }
      @keyframes rise {
        0%   { transform: translateY(0px);   opacity: 0; }
        10%  { opacity: 0.75; }
        80%  { opacity: 0.6; }
        100% { transform: translateY(-110px); opacity: 0; }
      }
      .b1 { animation-duration: 2.4s; animation-delay: 0.0s; }
      .b2 { animation-duration: 3.1s; animation-delay: 0.7s; }
      .b3 { animation-duration: 2.7s; animation-delay: 1.3s; }
      .b4 { animation-duration: 2.1s; animation-delay: 0.4s; }
      .b5 { animation-duration: 3.4s; animation-delay: 1.8s; }
      .b6 { animation-duration: 2.9s; animation-delay: 0.9s; }
      .b7 { animation-duration: 2.2s; animation-delay: 2.1s; }
      .b8 { animation-duration: 3.6s; animation-delay: 0.2s; }
      @keyframes shimmer {
        0%,100% { opacity: 0.15; }
        50% { opacity: 0.35; }
      }
      .shimmer { animation: shimmer 3s ease-in-out infinite; }
      @keyframes wobble {
        0%,100% { rx: 62; ry: 18; }
        50% { rx: 65; ry: 16; }
      }
    </style>
  </defs>
  <!-- Bath container -->
  <rect x="40" y="50" width="320" height="140" rx="8" fill="url(#bathGrad)" stroke="#0d6b9c" stroke-width="2"/>
  <!-- Chemical ripple overlays -->
  <ellipse cx="200" cy="58" rx="130" ry="10" fill="white" opacity="0.18" class="shimmer"/>
  <!-- Wafer submerged in bath -->
  <rect x="120" y="115" width="160" height="28" rx="5" fill="url(#waferGrad)" stroke="#185FA5" stroke-width="1.5"/>
  <rect x="128" y="121" width="144" height="4" rx="2" fill="white" opacity="0.5"/>
  <!-- Bubbles – positioned along bottom of wafer -->
  <circle class="bubble b1" cx="140" cy="143" r="5"  fill="white" stroke="#aaddff" stroke-width="0.8"/>
  <circle class="bubble b2" cx="165" cy="143" r="4"  fill="white" stroke="#aaddff" stroke-width="0.8"/>
  <circle class="bubble b3" cx="190" cy="143" r="6"  fill="white" stroke="#aaddff" stroke-width="0.8"/>
  <circle class="bubble b4" cx="215" cy="143" r="3.5" fill="white" stroke="#aaddff" stroke-width="0.8"/>
  <circle class="bubble b5" cx="240" cy="143" r="5"  fill="white" stroke="#aaddff" stroke-width="0.8"/>
  <circle class="bubble b6" cx="155" cy="143" r="3"  fill="white" stroke="#aaddff" stroke-width="0.8"/>
  <circle class="bubble b7" cx="228" cy="143" r="4.5" fill="white" stroke="#aaddff" stroke-width="0.8"/>
  <circle class="bubble b8" cx="203" cy="143" r="3"  fill="white" stroke="#aaddff" stroke-width="0.8"/>
  <!-- Bath surface glint -->
  <rect x="40" y="50" width="320" height="10" rx="4" fill="white" opacity="0.25"/>
  <!-- Label -->
  <text x="200" y="30" text-anchor="middle" font-family="monospace" font-size="13"
        fill="#185FA5" font-weight="bold">RCA Chemical Bath Clean</text>
  <text x="200" y="45" text-anchor="middle" font-family="monospace" font-size="10"
        fill="#2a7fbf">H₂O₂ / NH₄OH / HCl / DI water</text>
</svg>""",

        # ------------------------------------------------------------------
        # Stage 1 – Deposit: green particles raining onto a wafer
        # ------------------------------------------------------------------
        """<svg viewBox="0 0 400 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="chamberGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#1a2e22"/>
      <stop offset="100%" stop-color="#0d1f15"/>
    </linearGradient>
    <linearGradient id="waferD" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#c8e8d8"/>
      <stop offset="100%" stop-color="#7abfa0"/>
    </linearGradient>
    <style>
      .particle { animation: fall linear infinite; }
      @keyframes fall {
        0%   { transform: translateY(-30px); opacity: 0; }
        15%  { opacity: 1; }
        85%  { opacity: 0.9; }
        100% { transform: translateY(90px);  opacity: 0; }
      }
      .p1  { animation-duration:1.6s; animation-delay:0.0s; }
      .p2  { animation-duration:2.1s; animation-delay:0.3s; }
      .p3  { animation-duration:1.8s; animation-delay:0.7s; }
      .p4  { animation-duration:2.3s; animation-delay:1.1s; }
      .p5  { animation-duration:1.5s; animation-delay:0.5s; }
      .p6  { animation-duration:2.0s; animation-delay:0.9s; }
      .p7  { animation-duration:1.9s; animation-delay:1.4s; }
      .p8  { animation-duration:2.4s; animation-delay:0.2s; }
      .p9  { animation-duration:1.7s; animation-delay:1.6s; }
      .p10 { animation-duration:2.2s; animation-delay:0.6s; }
      @keyframes growfilm {
        0%,100% { height: 5px; }
        50%      { height: 8px; }
      }
      .film { animation: growfilm 4s ease-in-out infinite; }
      @keyframes glowpulse {
        0%,100% { opacity:0.4; }
        50%      { opacity:0.9; }
      }
      .glow { animation: glowpulse 2s ease-in-out infinite; }
    </style>
  </defs>
  <!-- Vacuum chamber background -->
  <rect x="30" y="20" width="340" height="165" rx="12" fill="url(#chamberGrad)" stroke="#1a6644" stroke-width="2"/>
  <!-- Precursor nozzle top -->
  <rect x="155" y="20" width="90" height="18" rx="4" fill="#2e7d52" stroke="#0F6E56" stroke-width="1.5"/>
  <text x="200" y="33" text-anchor="middle" font-family="monospace" font-size="9" fill="#a8e6c2">PRECURSOR INLET</text>
  <!-- Particles raining -->
  <circle class="particle p1"  cx="145" cy="60" r="3.5" fill="#34d47a"/>
  <circle class="particle p2"  cx="163" cy="55" r="2.5" fill="#5be891"/>
  <circle class="particle p3"  cx="181" cy="62" r="3"   fill="#34d47a"/>
  <circle class="particle p4"  cx="199" cy="57" r="4"   fill="#1abf5c"/>
  <circle class="particle p5"  cx="217" cy="60" r="2.5" fill="#5be891"/>
  <circle class="particle p6"  cx="235" cy="54" r="3.5" fill="#34d47a"/>
  <circle class="particle p7"  cx="153" cy="58" r="2"   fill="#a3f0c0"/>
  <circle class="particle p8"  cx="172" cy="63" r="3"   fill="#1abf5c"/>
  <circle class="particle p9"  cx="210" cy="56" r="2.5" fill="#5be891"/>
  <circle class="particle p10" cx="225" cy="61" r="4"   fill="#34d47a"/>
  <!-- Wafer -->
  <rect x="100" y="148" width="200" height="22" rx="5" fill="url(#waferD)" stroke="#0F6E56" stroke-width="1.5"/>
  <!-- Growing film on wafer -->
  <rect class="film" x="100" y="143" width="200" height="5" rx="2" fill="#0F6E56" opacity="0.85"/>
  <!-- Chamber glow -->
  <ellipse cx="200" cy="120" rx="100" ry="40" fill="#34d47a" opacity="0.05" class="glow"/>
  <!-- Labels -->
  <text x="200" y="14" text-anchor="middle" font-family="monospace" font-size="12"
        fill="#0F6E56" font-weight="bold">ALD / CVD Thin Film Deposition</text>
  <text x="310" y="158" text-anchor="middle" font-family="monospace" font-size="8" fill="#7abfa0">wafer</text>
  <text x="310" y="148" text-anchor="middle" font-family="monospace" font-size="8" fill="#34d47a">film ↑</text>
</svg>""",

        # ------------------------------------------------------------------
        # Stage 2 – Lithography: UV beam scanning through a mask
        # ------------------------------------------------------------------
        """<svg viewBox="0 0 400 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bgLitho" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#1a1020"/>
      <stop offset="100%" stop-color="#0c0810"/>
    </linearGradient>
    <linearGradient id="beamGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#ff9a1a" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#ff6600" stop-opacity="0.3"/>
    </linearGradient>
    <style>
      @keyframes scan {
        0%   { transform: translateX(-70px); }
        100% { transform: translateX(70px); }
      }
      .scanbeam { animation: scan 2.8s ease-in-out infinite alternate; }
      @keyframes expose {
        0%,100% { opacity: 0.15; }
        50% { opacity: 0.7; }
      }
      .exposed { animation: expose 2.8s ease-in-out infinite alternate; }
      @keyframes flicker {
        0%,100% { opacity: 1; }
        45% { opacity: 0.7; }
        55% { opacity: 1; }
      }
      .source { animation: flicker 1.4s ease-in-out infinite; }
    </style>
  </defs>
  <!-- Dark chamber -->
  <rect x="20" y="10" width="360" height="180" rx="10" fill="url(#bgLitho)"/>
  <!-- UV Source -->
  <ellipse cx="200" cy="30" rx="28" ry="12" fill="#E65100" class="source"/>
  <text x="200" y="34" text-anchor="middle" font-family="monospace" font-size="9"
        fill="white" font-weight="bold">EUV / ArF</text>
  <!-- Mask plate -->
  <rect x="100" y="55" width="200" height="16" rx="3" fill="#444" stroke="#888" stroke-width="1"/>
  <!-- Mask openings (clear slots) -->
  <rect x="120" y="56" width="20" height="14" rx="1" fill="#1a1020"/>
  <rect x="155" y="56" width="15" height="14" rx="1" fill="#1a1020"/>
  <rect x="185" y="56" width="25" height="14" rx="1" fill="#1a1020"/>
  <rect x="225" y="56" width="18" height="14" rx="1" fill="#1a1020"/>
  <rect x="258" y="56" width="12" height="14" rx="1" fill="#1a1020"/>
  <text x="200" y="52" text-anchor="middle" font-family="monospace" font-size="8" fill="#aaa">PHOTOMASK</text>
  <!-- Scanning UV beam (cone) -->
  <g class="scanbeam">
    <polygon points="200,67 180,130 220,130" fill="url(#beamGrad)" opacity="0.75"/>
    <line x1="200" y1="67" x2="200" y2="130" stroke="#ffcc44" stroke-width="1" opacity="0.6"/>
  </g>
  <!-- Resist layer on wafer -->
  <rect x="80" y="152" width="240" height="10" rx="3" fill="#ff8c42" opacity="0.6"/>
  <!-- Exposed resist highlight that scans -->
  <rect class="exposed" x="170" y="152" width="60" height="10" rx="2" fill="#ffe066"/>
  <!-- Wafer -->
  <rect x="80" y="162" width="240" height="18" rx="4" fill="#3a2a18" stroke="#E65100" stroke-width="1.5"/>
  <text x="200" y="175" text-anchor="middle" font-family="monospace" font-size="8" fill="#ff9a60">SILICON WAFER</text>
  <!-- Labels -->
  <text x="200" y="10" text-anchor="middle" font-family="monospace" font-size="12"
        fill="#E65100" font-weight="bold" dy="5">Photolithography — UV Exposure</text>
  <text x="83" y="158" font-family="monospace" font-size="7" fill="#ffcc44">resist</text>
</svg>""",

        # ------------------------------------------------------------------
        # Stage 3 – Etch: red plasma bolts striking the surface
        # ------------------------------------------------------------------
        """<svg viewBox="0 0 400 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="plasmaGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#3a0808"/>
      <stop offset="100%" stop-color="#1a0404"/>
    </linearGradient>
    <linearGradient id="plasmaCloud" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#ff2200" stop-opacity="0.7"/>
      <stop offset="100%" stop-color="#ff6600" stop-opacity="0.2"/>
    </linearGradient>
    <style>
      @keyframes bolt {
        0%,100% { opacity: 0; transform: scaleY(0.2); }
        40%,60% { opacity: 1; transform: scaleY(1); }
      }
      .bolt1 { animation: bolt 1.3s ease-in-out infinite; animation-delay: 0.0s; transform-origin: top; }
      .bolt2 { animation: bolt 1.7s ease-in-out infinite; animation-delay: 0.5s; transform-origin: top; }
      .bolt3 { animation: bolt 1.5s ease-in-out infinite; animation-delay: 0.9s; transform-origin: top; }
      .bolt4 { animation: bolt 1.9s ease-in-out infinite; animation-delay: 0.2s; transform-origin: top; }
      .bolt5 { animation: bolt 1.4s ease-in-out infinite; animation-delay: 1.1s; transform-origin: top; }
      @keyframes plasmaglow {
        0%,100% { opacity:0.5; ry:22; }
        50%      { opacity:0.85; ry:26; }
      }
      .pglow { animation: plasmaglow 1.2s ease-in-out infinite; }
      @keyframes craterPulse {
        0%,100% { width:14px; x:143px; }
        50%      { width:18px; x:141px; }
      }
    </style>
  </defs>
  <!-- Chamber -->
  <rect x="25" y="15" width="350" height="170" rx="10" fill="url(#plasmaGrad)" stroke="#8b0000" stroke-width="2"/>
  <!-- Plasma cloud at top -->
  <ellipse cx="200" cy="62" rx="140" ry="24" fill="url(#plasmaCloud)" class="pglow"/>
  <text x="200" y="38" text-anchor="middle" font-family="monospace" font-size="9" fill="#ff6644">PLASMA (F• Cl• radicals)</text>
  <!-- Plasma bolts (lightning-style polylines) -->
  <polyline class="bolt1" points="145,86 140,100 148,108 143,125 148,140"
            fill="none" stroke="#ff3300" stroke-width="2.5" stroke-linecap="round"/>
  <polyline class="bolt2" points="175,86 172,102 179,112 174,128 178,140"
            fill="none" stroke="#ff6600" stroke-width="2" stroke-linecap="round"/>
  <polyline class="bolt3" points="200,86 196,105 203,115 198,130 202,140"
            fill="none" stroke="#ff2200" stroke-width="3" stroke-linecap="round"/>
  <polyline class="bolt4" points="225,86 228,100 222,110 227,125 224,140"
            fill="none" stroke="#ff5500" stroke-width="2" stroke-linecap="round"/>
  <polyline class="bolt5" points="255,86 258,103 252,113 256,128 253,140"
            fill="none" stroke="#ff3300" stroke-width="2.5" stroke-linecap="round"/>
  <!-- Mask on wafer (dark blocks = protected) -->
  <rect x="80"  y="140" width="40" height="10" rx="2" fill="#555"/>
  <rect x="155" y="140" width="30" height="10" rx="2" fill="#555"/>
  <rect x="215" y="140" width="35" height="10" rx="2" fill="#555"/>
  <rect x="280" y="140" width="40" height="10" rx="2" fill="#555"/>
  <!-- Exposed resist (etched trenches) -->
  <rect x="120" y="140" width="35" height="10" rx="1" fill="#8b0000" opacity="0.9"/>
  <rect x="185" y="140" width="30" height="10" rx="1" fill="#8b0000" opacity="0.9"/>
  <rect x="250" y="140" width="30" height="10" rx="1" fill="#8b0000" opacity="0.9"/>
  <!-- Wafer substrate -->
  <rect x="80"  y="150" width="240" height="18" rx="4" fill="#4a1515" stroke="#A32D2D" stroke-width="1.5"/>
  <text x="200" y="163" text-anchor="middle" font-family="monospace" font-size="8" fill="#e07070">SILICON SUBSTRATE</text>
  <!-- Labels -->
  <text x="200" y="12" text-anchor="middle" font-family="monospace" font-size="12"
        fill="#A32D2D" font-weight="bold" dy="5">Reactive Ion Etch (RIE/ICP)</text>
  <text x="87"  y="138" font-family="monospace" font-size="7" fill="#aaa">mask</text>
</svg>""",

        # ------------------------------------------------------------------
        # Stage 4 – Anneal: heat waves rising inside a furnace
        # ------------------------------------------------------------------
        """<svg viewBox="0 0 400 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="furnGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#2a1200"/>
      <stop offset="100%" stop-color="#1a0a00"/>
    </linearGradient>
    <linearGradient id="glowOrange" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#ff8800" stop-opacity="0"/>
      <stop offset="60%" stop-color="#ff4400" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#ff2200" stop-opacity="0.6"/>
    </linearGradient>
    <style>
      @keyframes wave {
        0%   { d: path("M 120 145 Q 150 130 180 145 Q 210 160 240 145 Q 270 130 300 145"); opacity:0.9; transform:translateY(0); }
        50%  { d: path("M 120 145 Q 150 158 180 145 Q 210 132 240 145 Q 270 158 300 145"); opacity:0.6; transform:translateY(-12px); }
        100% { d: path("M 120 145 Q 150 130 180 145 Q 210 160 240 145 Q 270 130 300 145"); opacity:0; transform:translateY(-35px); }
      }
      .w1 { animation: wave 2.0s ease-in-out infinite; animation-delay: 0.0s; }
      .w2 { animation: wave 2.0s ease-in-out infinite; animation-delay: 0.6s; }
      .w3 { animation: wave 2.0s ease-in-out infinite; animation-delay: 1.2s; }
      @keyframes coilpulse {
        0%,100% { stroke: #ff4400; stroke-width:4; }
        50%      { stroke: #ffaa00; stroke-width:5; }
      }
      .coil { animation: coilpulse 1.5s ease-in-out infinite; fill:none; }
      @keyframes tempRise {
        0%,100% { fill: #ff6600; }
        50%      { fill: #ffcc00; }
      }
      .temptext { animation: tempRise 1.5s ease-in-out infinite; }
    </style>
  </defs>
  <!-- Furnace body -->
  <rect x="30" y="20" width="340" height="165" rx="15" fill="url(#furnGrad)" stroke="#8b4000" stroke-width="2.5"/>
  <!-- Inner glow at bottom (heat source) -->
  <rect x="30" y="120" width="340" height="65" rx="15" fill="url(#glowOrange)"/>
  <!-- Heating coils -->
  <polyline class="coil" points="60,160 80,148 100,160 120,148 140,160 160,148 180,160 200,148 220,160 240,148 260,160 280,148 300,160 320,148 340,160"
            stroke="#ff4400" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
  <!-- Wafer boat with wafers -->
  <rect x="90"  y="128" width="8" height="28" rx="2" fill="#c87820" stroke="#804000" stroke-width="1"/>
  <rect x="120" y="128" width="8" height="28" rx="2" fill="#c87820" stroke="#804000" stroke-width="1"/>
  <rect x="150" y="128" width="8" height="28" rx="2" fill="#c87820" stroke="#804000" stroke-width="1"/>
  <rect x="180" y="128" width="8" height="28" rx="2" fill="#c87820" stroke="#804000" stroke-width="1"/>
  <rect x="210" y="128" width="8" height="28" rx="2" fill="#c87820" stroke="#804000" stroke-width="1"/>
  <rect x="240" y="128" width="8" height="28" rx="2" fill="#c87820" stroke="#804000" stroke-width="1"/>
  <rect x="270" y="128" width="8" height="28" rx="2" fill="#c87820" stroke="#804000" stroke-width="1"/>
  <rect x="300" y="128" width="8" height="28" rx="2" fill="#c87820" stroke="#804000" stroke-width="1"/>
  <!-- Heat wave paths -->
  <path class="w1" d="M 120 145 Q 150 130 180 145 Q 210 160 240 145 Q 270 130 300 145"
        fill="none" stroke="#ff6600" stroke-width="2.5" stroke-linecap="round"/>
  <path class="w2" d="M 120 145 Q 150 130 180 145 Q 210 160 240 145 Q 270 130 300 145"
        fill="none" stroke="#ff9900" stroke-width="2" stroke-linecap="round"/>
  <path class="w3" d="M 120 145 Q 150 130 180 145 Q 210 160 240 145 Q 270 130 300 145"
        fill="none" stroke="#ffcc00" stroke-width="1.5" stroke-linecap="round"/>
  <!-- Temperature display -->
  <rect x="300" y="25" width="60" height="32" rx="5" fill="#1a0a00" stroke="#8b4000" stroke-width="1"/>
  <text x="330" y="38" text-anchor="middle" font-family="monospace" font-size="8" fill="#ff6600">TEMP</text>
  <text class="temptext" x="330" y="51" text-anchor="middle" font-family="monospace"
        font-size="10" font-weight="bold">1050°C</text>
  <!-- N₂ atmosphere label -->
  <text x="60" y="40" font-family="monospace" font-size="9" fill="#c87820">N₂ atmosphere</text>
  <!-- Title -->
  <text x="175" y="14" text-anchor="middle" font-family="monospace" font-size="12"
        fill="#B45309" font-weight="bold" dy="5">Rapid Thermal Anneal (RTP)</text>
</svg>""",

        # ------------------------------------------------------------------
        # Stage 5 – Characterize: SEM probe scanning across a wafer surface
        # ------------------------------------------------------------------
        """<svg viewBox="0 0 400 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bgChar" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#100e1f"/>
      <stop offset="100%" stop-color="#0a0815"/>
    </linearGradient>
    <linearGradient id="screenGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#1a1060"/>
      <stop offset="100%" stop-color="#0d0830"/>
    </linearGradient>
    <style>
      @keyframes probescan {
        0%   { transform: translateX(-90px); }
        100% { transform: translateX(90px); }
      }
      .probe { animation: probescan 3s ease-in-out infinite alternate; }
      @keyframes scanline {
        0%   { transform: translateX(-90px); opacity:1; }
        100% { transform: translateX(90px);  opacity:1; }
      }
      .scanbeamSEM { animation: scanline 3s ease-in-out infinite alternate; }
      @keyframes screenDraw {
        0%   { stroke-dashoffset: 400; }
        100% { stroke-dashoffset: 0;   }
      }
      .waveform {
        stroke-dasharray: 400;
        animation: screenDraw 3s ease-in-out infinite;
      }
      @keyframes blinkCursor {
        0%,100% { opacity:1; }
        50% { opacity:0; }
      }
      .cursor { animation: blinkCursor 1s step-end infinite; }
      @keyframes detectorFlash {
        0%,100% { fill:#534AB7; }
        45%,55% { fill:#a89fff; }
      }
      .detector { animation: detectorFlash 3s ease-in-out infinite; }
    </style>
  </defs>
  <!-- Dark background -->
  <rect x="15" y="10" width="370" height="180" rx="10" fill="url(#bgChar)"/>
  <!-- SEM column on left -->
  <rect x="25" y="20" width="45" height="110" rx="5" fill="#1e1a3a" stroke="#534AB7" stroke-width="1.5"/>
  <rect x="33" y="28" width="30" height="12" rx="3" fill="#534AB7" opacity="0.7"/>
  <text x="48" y="37" text-anchor="middle" font-family="monospace" font-size="7" fill="white">GUN</text>
  <rect x="33" y="46" width="30" height="8" rx="2" fill="#3a347a" stroke="#534AB7" stroke-width="0.8"/>
  <rect x="33" y="60" width="30" height="8" rx="2" fill="#3a347a" stroke="#534AB7" stroke-width="0.8"/>
  <rect x="36" y="74" width="24" height="40" rx="3" fill="#2a2460" stroke="#534AB7" stroke-width="0.8"/>
  <text x="48" y="100" text-anchor="middle" font-family="monospace" font-size="7" fill="#8882cc">LENS</text>
  <!-- Moving probe tip & beam -->
  <g class="probe">
    <polygon points="48,130 44,145 52,145" fill="#7a74dd" opacity="0.9"/>
    <line x1="48" y1="145" x2="48" y2="163" stroke="#a89fff" stroke-width="1.5" opacity="0.8"/>
  </g>
  <!-- Scanning beam on wafer surface -->
  <g class="scanbeamSEM">
    <line x1="48" y1="163" x2="44" y2="168" stroke="#ff0" stroke-width="1" opacity="0.5"/>
    <circle cx="48" cy="168" r="3" fill="#ffee44" opacity="0.6"/>
  </g>
  <!-- Wafer surface with texture -->
  <rect x="30" y="163" width="200" height="18" rx="4" fill="#2a2248" stroke="#534AB7" stroke-width="1.5"/>
  <!-- Wafer surface features -->
  <rect x="50"  y="163" width="8"  height="6"  rx="1" fill="#534AB7" opacity="0.7"/>
  <rect x="72"  y="163" width="12" height="8"  rx="1" fill="#534AB7" opacity="0.7"/>
  <rect x="98"  y="163" width="7"  height="5"  rx="1" fill="#534AB7" opacity="0.7"/>
  <rect x="120" y="163" width="10" height="9"  rx="1" fill="#534AB7" opacity="0.7"/>
  <rect x="148" y="163" width="8"  height="6"  rx="1" fill="#534AB7" opacity="0.7"/>
  <rect x="170" y="163" width="14" height="7"  rx="1" fill="#534AB7" opacity="0.7"/>
  <rect x="198" y="163" width="7"  height="5"  rx="1" fill="#534AB7" opacity="0.7"/>
  <!-- Detector (BSE/SE) -->
  <rect class="detector" x="255" y="155" width="22" height="18" rx="4" stroke="#534AB7" stroke-width="1.5"/>
  <text x="266" y="167" text-anchor="middle" font-family="monospace" font-size="7" fill="white">SE</text>
  <!-- SEM screen / waveform display -->
  <rect x="255" y="20" width="118" height="128" rx="6" fill="url(#screenGrad)" stroke="#534AB7" stroke-width="1.5"/>
  <text x="314" y="33" text-anchor="middle" font-family="monospace" font-size="8" fill="#8882cc">SEM IMAGE</text>
  <polyline class="waveform"
            points="265,100 273,88 281,108 289,80 297,102 305,75 313,95 321,70 329,92 337,78 345,98 353,72 361,90"
            fill="none" stroke="#a89fff" stroke-width="1.5" stroke-linecap="round"/>
  <!-- Scan cursor on screen -->
  <line class="cursor" x1="313" y1="50" x2="313" y2="130" stroke="#00ff88" stroke-width="1" opacity="0.7"/>
  <!-- EDS spectrum mini-panel -->
  <rect x="255" y="88" width="118" height="55" rx="3" fill="#0d0830" opacity="0.7"/>
  <text x="314" y="99" text-anchor="middle" font-family="monospace" font-size="7" fill="#6662bb">EDS SPECTRUM</text>
  <rect x="268" y="128" width="5"  height="10" fill="#ff6644"/>
  <rect x="278" y="120" width="5"  height="18" fill="#44aaff"/>
  <rect x="288" y="110" width="5"  height="28" fill="#ff6644"/>
  <rect x="298" y="125" width="5"  height="13" fill="#44ff88"/>
  <rect x="308" y="115" width="5"  height="23" fill="#44aaff"/>
  <rect x="318" y="122" width="5"  height="16" fill="#ff6644"/>
  <rect x="328" y="118" width="5"  height="20" fill="#44ff88"/>
  <rect x="338" y="126" width="5"  height="12" fill="#44aaff"/>
  <rect x="348" y="112" width="5"  height="26" fill="#ff6644"/>
  <!-- Title -->
  <text x="200" y="10" text-anchor="middle" font-family="monospace" font-size="12"
        fill="#534AB7" font-weight="bold" dy="5">SEM / EDS Characterisation</text>
</svg>""",
    ]

    return svgs[stage_index]


# ---------------------------------------------------------------------------
# Main render function
# ---------------------------------------------------------------------------

def render_wafer_journey():
    """Render the full interactive Wafer Journey Streamlit app."""

    # ── Page config & custom CSS ──────────────────────────────────────────
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@400;500;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .journey-title {
            font-family: 'Space Mono', monospace;
            font-size: 2rem;
            font-weight: 700;
            letter-spacing: -0.5px;
            margin-bottom: 0;
        }

        .stage-nav-btn {
            display: inline-block;
            padding: 6px 14px;
            margin: 3px;
            border-radius: 20px;
            font-family: 'Space Mono', monospace;
            font-size: 0.72rem;
            font-weight: 700;
            cursor: pointer;
            border: 2px solid transparent;
            transition: all 0.2s ease;
        }

        .analogy-box {
            background: linear-gradient(135deg, #f0f4ff, #e8ecff);
            border-left: 4px solid #534AB7;
            padding: 12px 18px;
            border-radius: 0 10px 10px 0;
            font-style: italic;
            font-size: 0.95rem;
            margin: 12px 0 18px 0;
            color: #3d3472;
        }

        .info-card {
            background: white;
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.07);
            height: 100%;
            border-top: 4px solid var(--card-accent, #534AB7);
        }

        .info-card h4 {
            font-family: 'Space Mono', monospace;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
            color: var(--card-accent, #534AB7);
        }

        .fun-fact-box {
            border-radius: 12px;
            padding: 16px 20px;
            margin-top: 18px;
            font-size: 0.9rem;
            line-height: 1.6;
        }

        .stButton>button {
            font-family: 'Space Mono', monospace;
            font-weight: 700;
            border-radius: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ── Title ──────────────────────────────────────────────────────────────
    st.markdown(
        '<p class="journey-title">🔬 The Wafer Journey</p>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Follow a silicon wafer through the 6 key stages of semiconductor nanofabrication — "
        "from spotless clean room to fully characterised device."
    )

    st.divider()

    # ── Session state ──────────────────────────────────────────────────────
    if "journey_stage" not in st.session_state:
        st.session_state.journey_stage = 0

    current = st.session_state.journey_stage
    stage = STAGES[current]

    # ── Stage navigation row ───────────────────────────────────────────────
    st.markdown("**Navigate stages:**")
    nav_cols = st.columns(len(STAGES))
    for i, (col, s) in enumerate(zip(nav_cols, STAGES)):
        with col:
            is_active = i == current
            label = f"{s['icon']} {s['name']}"
            if is_active:
                st.markdown(
                    f'<div style="text-align:center; padding:6px 4px; border-radius:10px; '
                    f'background:{s["color"]}; color:white; font-family:Space Mono,monospace; '
                    f'font-size:0.72rem; font-weight:700; border:2px solid {s["color"]};">'
                    f'{label}</div>',
                    unsafe_allow_html=True,
                )
            else:
                if st.button(label, key=f"nav_{i}", use_container_width=True):
                    st.session_state.journey_stage = i
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Stage header ───────────────────────────────────────────────────────
    st.markdown(
        f'<h2 style="font-family:Space Mono,monospace; color:{stage["color"]}; margin-bottom:2px;">'
        f'Stage {current + 1} / {len(STAGES)} &nbsp;·&nbsp; {stage["icon"]} {stage["name"]}'
        f'</h2>',
        unsafe_allow_html=True,
    )

    # ── Analogy ────────────────────────────────────────────────────────────
    st.markdown(
        f'<div class="analogy-box">💡 {stage["analogy"]}</div>',
        unsafe_allow_html=True,
    )

    # ── SVG animation ──────────────────────────────────────────────────────
    svg_html = f"""
    <div style="background:{stage['bg']}; border-radius:14px; padding:10px;
                border:2px solid {stage['color']}33; text-align:center;">
        {get_stage_svg(current)}
    </div>
    """
    components.html(svg_html, height=220)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Three-column info cards ────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f'<div class="info-card" style="--card-accent:{stage["color"]};">'
            f'<h4>⚗️ What Happens</h4>'
            f'<p style="font-size:0.88rem; line-height:1.6; color:#333;">{stage["what_happens"]}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with col2:
        wrongs_html = "".join(
            f'<li style="margin-bottom:7px;">{w}</li>'
            for w in stage["what_goes_wrong"]
        )
        st.markdown(
            f'<div class="info-card" style="--card-accent:#c0392b;">'
            f'<h4>⚠️ What Goes Wrong</h4>'
            f'<ul style="font-size:0.85rem; line-height:1.55; color:#444; '
            f'padding-left:18px; margin:0;">{wrongs_html}</ul>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with col3:
        tools_html = "".join(
            f'<li style="margin-bottom:7px;">{t}</li>'
            for t in stage["tools"]
        )
        st.markdown(
            f'<div class="info-card" style="--card-accent:#0F6E56;">'
            f'<h4>🔧 Key Tools</h4>'
            f'<ul style="font-size:0.85rem; line-height:1.55; color:#444; '
            f'padding-left:18px; margin:0;">{tools_html}</ul>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Fun fact ───────────────────────────────────────────────────────────
    st.markdown(
        f'<div class="fun-fact-box" style="background:{stage["bg"]}; '
        f'border:1.5px solid {stage["color"]}44;">'
        f'<span style="font-family:Space Mono,monospace; font-size:0.78rem; '
        f'color:{stage["color"]}; font-weight:700; text-transform:uppercase; '
        f'letter-spacing:1px;">⚡ Fun Fact</span><br><br>'
        f'<span style="color:#333;">{stage["fun_fact"]}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Navigation buttons ─────────────────────────────────────────────────
    btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])

    with btn_col1:
        if current > 0:
            prev = STAGES[current - 1]
            if st.button(
                f"← {prev['icon']} {prev['name']}",
                key="prev_btn",
                use_container_width=True,
            ):
                st.session_state.journey_stage -= 1
                st.rerun()

    with btn_col2:
        # Progress bar
        progress_pct = (current + 1) / len(STAGES)
        st.markdown(
            f'<div style="text-align:center; font-family:Space Mono,monospace; '
            f'font-size:0.75rem; color:#666; margin-bottom:4px;">'
            f'Stage {current + 1} of {len(STAGES)}</div>',
            unsafe_allow_html=True,
        )
        st.progress(progress_pct)

    with btn_col3:
        if current < len(STAGES) - 1:
            nxt = STAGES[current + 1]
            if st.button(
                f"{nxt['icon']} {nxt['name']} →",
                key="next_btn",
                use_container_width=True,
            ):
                st.session_state.journey_stage += 1
                st.rerun()

    # ── Completion message ─────────────────────────────────────────────────
    if current == len(STAGES) - 1:
        st.markdown("<br>", unsafe_allow_html=True)
        st.success(
            "🎉 **You completed the full wafer journey!** "
            "You've followed a silicon wafer from clean-room prep all the way through "
            "characterisation — the same path every modern microchip takes."
        )
        if st.button("🔄 Start Over", key="restart_btn"):
            st.session_state.journey_stage = 0
            st.rerun()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    st.set_page_config(
        page_title="NanoLab · Wafer Journey",
        page_icon="🔬",
        layout="wide",
    )
    render_wafer_journey()