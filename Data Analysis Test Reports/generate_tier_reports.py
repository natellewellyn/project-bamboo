#!/usr/bin/env python3
"""
ELL Tier Reports Generator
Cedar Valley Unified School District
Produces two self-contained HTML files:
  1. ELL_Grouping_Plan.html   — class-level instructional tier dashboard
  2. ELL_Individual_Plans.html — per-student one-page profiles
"""

import math
import openpyxl
from pathlib import Path

BASE = Path(__file__).parent.parent  # bamboo/ directory
OUT_DIR = Path(__file__).parent

# ─────────────────────────────────────────────
# 1. LOAD DATA (mirrors generate_report.py)
# ─────────────────────────────────────────────

def load_sheet(fname):
    wb = openpyxl.load_workbook(BASE / fname, data_only=True)
    rows = list(wb.active.iter_rows(values_only=True))
    headers = rows[1]
    data = []
    for row in rows[2:]:
        if row[0] is None or not isinstance(row[0], int):
            continue
        data.append(dict(zip(headers, row)))
    return data

def clean_keys(records):
    out = []
    for rec in records:
        out.append({k.replace("\n","_").strip() if k else k: v for k,v in rec.items()})
    return out

def by_id(records):
    return {r["Student ID"]: r for r in records}

access_py  = clean_keys(load_sheet("ACCESS_Scores_Export_PY2024-25.xlsx"))
access_now = clean_keys(load_sheet("ACCESS_Scores_Export_Spring2026.xlsx"))
rise       = clean_keys(load_sheet("RISE_StateTest_Results_Spring2025.xlsx"))
sis        = clean_keys(load_sheet("SIS_Grades_Export_2025-26.xlsx"))

ap = by_id(access_py)
an = by_id(access_now)
ri = by_id(rise)
si = by_id(sis)
ALL_IDS = sorted(an.keys())

def safe_float(v):
    try: return float(v)
    except (TypeError, ValueError): return None

# Build merged student records
students = []
for sid in ALL_IDS:
    s = {}
    s["id"] = sid
    a = an[sid]
    s["first"] = a["First Name"]
    s["last"]  = a["Last Name"]
    s["name"]  = f"{a['First Name']} {a['Last Name']}"
    s["school"] = a["School"]
    s["grade"]  = a["Grade"]
    s["lang"]   = a["Home Language"]
    s["years_el"] = a.get("Years in_EL Program", a.get("Years in\nEL Program", 0))
    s["ltel"] = str(a.get("LTEL_(5+ yrs)", a.get("LTEL\n(5+ yrs)", "No"))).strip() == "Yes"

    s["listen"]    = safe_float(a["Listening"])
    s["speak"]     = safe_float(a["Speaking"])
    s["read"]      = safe_float(a["Reading"])
    s["write"]     = safe_float(a["Writing"])
    s["composite"] = safe_float(a.get("Composite_Score"))
    s["prof_level"] = safe_float(a.get("Proficiency_Level"))

    # Prior year
    if sid in ap:
        p = ap[sid]
        s["prior_listen"] = safe_float(p.get("Listening"))
        s["prior_speak"]  = safe_float(p.get("Speaking"))
        s["prior_read"]   = safe_float(p.get("Reading"))
        s["prior_write"]  = safe_float(p.get("Writing"))
        s["prior_composite"] = safe_float(p.get("Composite_Score"))
    else:
        s["prior_listen"] = s["prior_speak"] = s["prior_read"] = s["prior_write"] = None
        s["prior_composite"] = None

    s["growth"] = None
    if s["composite"] is not None and s["prior_composite"] is not None:
        s["growth"] = round(s["composite"] - s["prior_composite"], 3)

    # RISE
    if sid in ri:
        r = ri[sid]
        def get_score(key_fragment):
            for k,v in r.items():
                if k and key_fragment.lower() in k.lower(): return v
            return None
        s["ela_score"] = safe_float(get_score("ELA_Scale"))
        s["ela_met"]   = str(get_score("ELA Met")).strip() == "Yes"
        s["ela_level"] = str(get_score("ELA_Level") or "").split("—")[0].strip()
        s["math_score"]= safe_float(get_score("Math_Scale"))
        s["math_met"]  = str(get_score("Math Met")).strip() == "Yes"
        s["math_level"]= str(get_score("Math_Level") or "").split("—")[0].strip()
        s["sci_score"] = safe_float(get_score("Science_Scale"))
        s["sci_met"]   = str(get_score("Science Met")).strip() == "Yes"
        s["sci_level"] = str(get_score("Science_Level") or "").split("—")[0].strip()
        s["rise_eligible"] = s["ela_score"] is not None
    else:
        for k in ["ela_score","ela_met","ela_level","math_score","math_met","math_level","sci_score","sci_met","sci_level"]:
            s[k] = None
        s["ela_met"] = s["math_met"] = s["sci_met"] = False
        s["rise_eligible"] = False

    # SIS
    if sid in si:
        g = si[sid]
        def gv(key_fragment):
            for k,v in g.items():
                if k and key_fragment.lower() in k.lower(): return v
            return None
        s["teacher"]   = gv("EL Teacher")
        s["el_status"] = str(gv("EL Status") or "")
        s["iep"]       = str(gv("IEP") or "").strip() == "Yes"
        s["ela_pct"]   = safe_float(gv("ELA"))
        s["math_pct"]  = safe_float(gv("Math"))
        s["sci_pct"]   = safe_float(gv("Science"))
        s["ss_pct"]    = safe_float(gv("Social"))
        s["gpa"]       = safe_float(gv("GPA"))
        s["absent"]    = safe_float(gv("Days"))
    else:
        s["teacher"]=s["el_status"]=None; s["iep"]=False
        s["ela_pct"]=s["math_pct"]=s["sci_pct"]=s["ss_pct"]=s["gpa"]=s["absent"]=None

    # Risk flags
    risks = []
    if s["composite"] is not None and s["composite"] < 2.0: risks.append("Very Low ACCESS")
    if s["ltel"]: risks.append("LTEL")
    if s["gpa"] is not None and s["gpa"] < 1.5: risks.append("Low GPA")
    if s["absent"] is not None and s["absent"] >= 7: risks.append("Chronic Absence")
    if s["iep"]: risks.append("IEP")
    s["risks"] = risks
    s["at_risk"] = len(risks) >= 2

    students.append(s)

# ─────────────────────────────────────────────
# 2. TIER CLASSIFICATION
# ─────────────────────────────────────────────

TIERS = [
    {
        "key": "exit_ready",
        "name": "Exit-Ready",
        "color": "#2d6a4f",
        "color_bg": "#2d6a4f12",
        "icon": "5",
        "description": "Approaching or meeting Utah reclassification criteria. Composite ≥ 4.4, RISE proficient in at least one subject, GPA ≥ 3.0.",
        "focus": "Reclassification prep, monitor in mainstream classes, build academic independence, reduce pull-out time.",
        "strategies": [
            "Transition to mainstream content with light language monitoring",
            "Academic vocabulary in grade-level texts without simplification",
            "Self-advocacy skills for requesting clarification independently",
            "Reclassification portfolio preparation"
        ]
    },
    {
        "key": "newcomer",
        "name": "Newcomer Intensive",
        "color": "#c0392b",
        "color_bg": "#c0392b12",
        "icon": "1",
        "description": "Recently arrived students with composite < 2.2 and significant academic gaps. GPA below 1.0, often with high absences.",
        "focus": "Survival English, L1 scaffolding, family engagement, building foundational literacy and school routines.",
        "strategies": [
            "L1 scaffolding — use home language for concept introduction",
            "Visual supports, realia, and Total Physical Response (TPR)",
            "Survival vocabulary: school routines, social phrases, content essentials",
            "Family engagement in home language — translated communication",
            "Buddy system with bilingual peers"
        ]
    },
    {
        "key": "developing_literacy",
        "name": "Developing — Literacy Gap",
        "color": "#e76f51",
        "color_bg": "#e76f5112",
        "icon": "2",
        "description": "Long-term English Learners with composite 2.9–3.35 where Writing lags 0.5+ points below Listening. Oral fluency masks academic literacy needs.",
        "focus": "Academic writing, content vocabulary, reading fluency. Close the gap between oral and written proficiency.",
        "strategies": [
            "Explicit academic writing instruction — paragraph frames, sentence stems",
            "Content-area vocabulary journals with visual + L1 definitions",
            "Guided reading at instructional level with comprehension checks",
            "Writer's workshop with peer revision and teacher conferencing",
            "Reading fluency practice with grade-level informational text"
        ]
    },
    {
        "key": "developing_ontrack",
        "name": "Developing — On Track",
        "color": "#c17b2e",
        "color_bg": "#c17b2e12",
        "icon": "3",
        "description": "Steady growth trajectory with composite 3.3–3.75. Making expected progress across modalities.",
        "focus": "Push toward proficiency — structured academic discussion, paragraph-level writing, content-area language.",
        "strategies": [
            "Structured academic discussion protocols (Think-Pair-Share, Socratic)",
            "Multi-paragraph writing with evidence from content-area texts",
            "Content-area language objectives alongside academic standards",
            "Collaborative projects requiring both oral and written output",
            "Gradual release of scaffolds as proficiency increases"
        ]
    },
    {
        "key": "accelerating",
        "name": "Accelerating",
        "color": "#52b788",
        "color_bg": "#52b78812",
        "icon": "4",
        "description": "Strong growth with composite 3.8–4.2, grades ≥ 75%. On pace to reach proficiency within 1–2 years.",
        "focus": "Grade-level content with embedded language support; reduce pull-out time, increase mainstream exposure.",
        "strategies": [
            "Grade-level content with embedded (not separate) language support",
            "Reduce pull-out time — prioritize in-class push-in model",
            "Advanced academic vocabulary and complex sentence structures",
            "Independent reading with text complexity progression",
            "Prepare for mainstream-only instruction"
        ]
    },
]

def classify_tiers(students):
    tiers = {t["key"]: [] for t in TIERS}
    assigned = set()

    for s in students:
        c = s["composite"]
        if c is None:
            continue

        # Exit-Ready
        if c >= 4.4 and (s["ela_met"] or s["math_met"]) and s["gpa"] is not None and s["gpa"] >= 3.0:
            tiers["exit_ready"].append(s)
            assigned.add(s["id"])
            continue

        # Newcomer Intensive
        if c <= 2.2:
            tiers["newcomer"].append(s)
            assigned.add(s["id"])
            continue

        # Developing — Literacy Gap (LTEL with writing gap)
        if s["ltel"] and s["listen"] is not None and s["write"] is not None:
            if s["listen"] - s["write"] >= 0.5:
                tiers["developing_literacy"].append(s)
                assigned.add(s["id"])
                continue

        # Accelerating
        if c >= 3.8 and s["growth"] is not None and s["growth"] > 0.3:
            grade_ok = any(p is not None and p >= 75 for p in [s["ela_pct"], s["math_pct"], s["sci_pct"], s["ss_pct"]])
            if grade_ok:
                tiers["accelerating"].append(s)
                assigned.add(s["id"])
                continue

        # Developing — On Track (catch remaining in the 3.3-3.75 range or slightly above)
        if 3.0 <= c <= 3.8:
            tiers["developing_ontrack"].append(s)
            assigned.add(s["id"])
            continue

    # Remaining students go to developing on track
    for s in students:
        if s["id"] not in assigned and s["composite"] is not None:
            tiers["developing_ontrack"].append(s)
            assigned.add(s["id"])

    return tiers

tier_groups = classify_tiers(students)

# Print tier assignments for verification
print("=== Tier Assignments ===")
for t in TIERS:
    names = [s["name"] for s in tier_groups[t["key"]]]
    print(f"  {t['name']}: {', '.join(names) or '(none)'}")
print()

# ─────────────────────────────────────────────
# 3. STUDENT PLAN COMPUTATIONS
# ─────────────────────────────────────────────

def compute_student_plan(s):
    """Compute projected targets, goals, and strategy recommendations."""
    plan = {}

    # Projected composite
    if s["growth"] is not None and s["growth"] > 0:
        plan["projected"] = round(s["composite"] + s["growth"] * 0.8, 2)
    elif s["composite"] is not None:
        plan["projected"] = round(s["composite"] + 0.5, 2)
    else:
        plan["projected"] = None

    # Modality analysis
    modalities = {"Listening": s["listen"], "Speaking": s["speak"], "Reading": s["read"], "Writing": s["write"]}
    valid = {k: v for k, v in modalities.items() if v is not None}
    if valid:
        plan["weakest"] = min(valid, key=valid.get)
        plan["strongest"] = max(valid, key=valid.get)
        plan["max_gap"] = round(max(valid.values()) - min(valid.values()), 1)
        plan["gap_pair"] = f"{plan['strongest']} ({valid[plan['strongest']]}) → {plan['weakest']} ({valid[plan['weakest']]})"
    else:
        plan["weakest"] = plan["strongest"] = None
        plan["max_gap"] = 0
        plan["gap_pair"] = "N/A"

    # Specific goals
    goals = []
    if valid:
        weakest_val = valid[plan["weakest"]]
        target_val = round(weakest_val + 0.5, 1)
        goals.append(f"Raise {plan['weakest']} from {weakest_val} → {target_val} by Spring 2027")

    if s["composite"] is not None and plan["projected"]:
        goals.append(f"Reach composite {plan['projected']} by Spring 2027 (from {s['composite']})")

    if s["rise_eligible"] and not s["ela_met"]:
        ela_lv = s["ela_level"] or "1"
        next_lv = str(min(int(ela_lv) + 1, 4)) if ela_lv.isdigit() else "2"
        goals.append(f"Achieve RISE ELA Level {ela_lv} → Level {next_lv}")

    if s["composite"] is not None and s["composite"] >= 4.0 and s["gpa"] is not None and s["gpa"] >= 3.0:
        goals.append("Prepare for reclassification review (R277-716)")

    plan["goals"] = goals

    # Content-area insights
    insights = []
    if s["math_pct"] is not None and s["math_pct"] >= 70 and s["ela_pct"] is not None and s["ela_pct"] < 70:
        insights.append("Strong math reasoning suggests content knowledge — academic language in ELA is the barrier")
    if s["rise_eligible"] and s["ela_level"] and s["ela_level"].isdigit() and int(s["ela_level"]) <= 1:
        insights.append("Below proficient on RISE ELA — academic language limiting content-area performance")
    if s["gpa"] is not None and s["gpa"] >= 2.5 and s["composite"] is not None and s["composite"] < 3.5:
        insights.append("Classroom grades outpace ACCESS proficiency — may benefit from more rigorous language targets")
    plan["content_insights"] = insights

    # Strategy recommendations based on modality profile + language
    strategies = []
    lang = s["lang"]

    if plan["weakest"] == "Writing":
        strategies.append("Targeted written output practice — daily journaling, paragraph frames, process writing")
        if lang == "Spanish" or lang == "Portuguese":
            strategies.append("Leverage L1 cognates for academic vocabulary in writing (Latin-root words)")
        elif lang == "Arabic":
            strategies.append("Explicit instruction on left-to-right text organization and English paragraph structure")
        elif lang == "Somali":
            strategies.append("Build English print literacy — Somali has limited written tradition; model text structures")
        elif lang == "Tongan":
            strategies.append("Scaffold English writing conventions — Tongan sentence structure differs significantly")

    elif plan["weakest"] == "Reading":
        strategies.append("Guided reading at instructional level with gradual text complexity increase")
        strategies.append("Vocabulary pre-teaching before content-area reading assignments")

    elif plan["weakest"] == "Listening":
        strategies.append("Audio-supported instruction with visual anchors and repeated exposure")
        strategies.append("Slow, clear teacher speech with comprehension checks (not just 'Do you understand?')")

    elif plan["weakest"] == "Speaking":
        strategies.append("Structured oral practice — Think-Pair-Share, sentence frames for academic discussion")
        strategies.append("Low-stakes speaking opportunities before whole-class participation")

    if s["ltel"]:
        strategies.append("LTEL-specific intervention: reclassify oral fluency vs. academic literacy needs")

    if s["iep"]:
        strategies.append("Coordinate with SPED team — differentiate language learning needs from disability-related needs")

    if s["absent"] is not None and s["absent"] >= 7:
        strategies.append("Attendance intervention: family outreach, identify barriers, provide make-up support")

    plan["strategies"] = strategies

    return plan

for s in students:
    s["plan"] = compute_student_plan(s)

# ─────────────────────────────────────────────
# 4. SVG CHART HELPERS
# ─────────────────────────────────────────────

def esc(content):
    return str(content).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def bar(x, y, w, h, color, rx=3, opacity=1.0):
    w = max(w, 0)
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{color}" opacity="{opacity}"/>'

def text_el(x, y, content, size=12, color="#1c1917", weight="normal", anchor="start", dy=0):
    content = esc(content)
    return f'<text x="{x:.1f}" y="{y:.1f}" dy="{dy}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{content}</text>'

def line_el(x1,y1,x2,y2,color="#e5e7eb",width=1,dash=""):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{width}"{dash_attr}/>'

GREEN      = "#2d6a4f"
MID_GREEN  = "#52b788"
TERRACOTTA = "#e76f51"
AMBER      = "#f4a261"
BLUE       = "#457b9d"
PURPLE     = "#7b5ea7"
NEUTRAL    = "#a8a29e"
CHART_BG   = "#faf8f5"
MODALITY_COLORS = {"Listening": BLUE, "Speaking": GREEN, "Reading": PURPLE, "Writing": TERRACOTTA}

# ─── Radar Chart ───────────────────────────────
def radar_point(cx, cy, radius, value, max_val, angle_deg):
    r = (value / max_val) * radius
    angle_rad = math.radians(angle_deg - 90)
    return (cx + r * math.cos(angle_rad), cy + r * math.sin(angle_rad))

def chart_radar(listen, speak, read, write, size=240, color="#2d6a4f", show_labels=True, annotation=None):
    """SVG radar/diamond chart for 4 modalities. Axes: L=top, S=right, R=bottom, W=left."""
    # Generous padding so labels never clip
    pad = 55
    total = size + pad * 2
    cx, cy = total / 2, total / 2
    radius = size / 2 - 8
    MAX_V = 6.0
    angles = [0, 90, 180, 270]  # Listening, Speaking, Reading, Writing
    labels = ["Listening", "Speaking", "Reading", "Writing"]
    values = [listen, speak, read, write]
    mod_colors = [BLUE, GREEN, PURPLE, TERRACOTTA]

    els = []
    els.append(f'<svg viewBox="0 0 {total} {total}" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:{total}px;font-family:\'DM Sans\',sans-serif">')

    # Grid rings — prominent at 2, 4, 6; subtle at 1, 3, 5
    for level in [2, 4, 6]:
        pts = []
        for ang in angles:
            px, py = radar_point(cx, cy, radius, level, MAX_V, ang)
            pts.append(f"{px:.1f},{py:.1f}")
        fill = "#f5f2ee" if level == 2 else "none"
        els.append(f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke="#e2ddd8" stroke-width="0.8"/>')
    for level in [1, 3, 5]:
        pts = []
        for ang in angles:
            px, py = radar_point(cx, cy, radius, level, MAX_V, ang)
            pts.append(f"{px:.1f},{py:.1f}")
        els.append(f'<polygon points="{" ".join(pts)}" fill="none" stroke="#ece8e3" stroke-width="0.5" stroke-dasharray="3 3"/>')

    # Axis lines — color-coded per modality
    for i, ang in enumerate(angles):
        ex, ey = radar_point(cx, cy, radius, MAX_V, MAX_V, ang)
        els.append(line_el(cx, cy, ex, ey, mod_colors[i], 1.2, "4 3"))

    # Scale numbers — placed between top and right axes (45 deg) to avoid overlap
    for level in [2, 4, 6]:
        sx, sy = radar_point(cx, cy, radius, level, MAX_V, 45)
        els.append(text_el(sx + 3, sy - 3, str(level), 8.5, NEUTRAL, anchor="start"))

    # Data polygon
    valid = all(v is not None for v in values)
    if valid:
        pts = []
        for i, ang in enumerate(angles):
            px, py = radar_point(cx, cy, radius, values[i], MAX_V, ang)
            pts.append(f"{px:.1f},{py:.1f}")
        els.append(f'<polygon points="{" ".join(pts)}" fill="{color}" fill-opacity="0.12" stroke="{color}" stroke-width="2.5"/>')

        # Data points + value labels — color-coded per modality
        for i, ang in enumerate(angles):
            v = values[i]
            mc = mod_colors[i]
            px, py = radar_point(cx, cy, radius, v, MAX_V, ang)
            els.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5" fill="white" stroke="{mc}" stroke-width="2.5"/>')
            # Value label offset outward from center
            offsets = [(0, -14), (14, 5), (0, 18), (-14, 5)]
            ox, oy = offsets[i]
            anchor = ["middle", "start", "middle", "end"][i]
            els.append(text_el(px + ox, py + oy, f"{v:.1f}", 12, mc, "700", anchor))

    # Axis labels — placed in the padding zone, well outside the chart
    if show_labels:
        label_pos = [
            (cx, pad * 0.45, "middle"),              # Listening — top
            (total - pad * 0.45, cy, "middle"),      # Speaking — right
            (cx, total - pad * 0.35, "middle"),      # Reading — bottom
            (pad * 0.45, cy, "middle"),              # Writing — left
        ]
        for i, (lx, ly, anch) in enumerate(label_pos):
            mc = mod_colors[i]
            els.append(text_el(lx, ly, labels[i], 12, mc, "600", anch, dy=4))

    # Annotation — below the Writing label on the left
    if annotation:
        els.append(f'<text x="{pad * 0.45}" y="{cy + 22}" font-size="10" fill="{TERRACOTTA}" text-anchor="middle" font-weight="600" font-style="italic">{esc(annotation)}</text>')

    els.append("</svg>")
    return "\n".join(els)


# ─── Mini Modality Bars ───────────────────────
def chart_mini_modalities(listen, speak, read, write, w=180, h=60):
    """Compact horizontal bars for tier cards."""
    MAX_V = 6.0
    bar_h = 9
    gap = 6
    pad_l = 14
    bar_w = w - pad_l - 30
    labels = ["L", "S", "R", "W"]
    values = [listen, speak, read, write]
    colors = [BLUE, GREEN, PURPLE, TERRACOTTA]

    els = []
    els.append(f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:{w}px;font-family:\'DM Sans\',sans-serif">')

    for i, (lbl, val, clr) in enumerate(zip(labels, values, colors)):
        y = i * (bar_h + gap) + 2
        els.append(text_el(0, y + bar_h - 1, lbl, 9, NEUTRAL, "600"))
        # Background bar
        els.append(bar(pad_l, y, bar_w, bar_h, "#e8e4df", rx=4))
        if val is not None:
            bw = (val / MAX_V) * bar_w
            els.append(bar(pad_l, y, bw, bar_h, clr, rx=4, opacity=0.85))
            els.append(text_el(pad_l + bw + 4, y + bar_h - 1, f"{val:.1f}", 9, clr, "600"))

    els.append("</svg>")
    return "\n".join(els)


# ─── Growth Trajectory Chart ──────────────────
def chart_growth_trajectory(prior, current, projected, w=280, h=100):
    """Small line chart: prior → current → projected."""
    pad_l, pad_r, pad_t, pad_b = 35, 25, 18, 28
    inner_w = w - pad_l - pad_r
    inner_h = h - pad_t - pad_b

    vals = [v for v in [prior, current, projected] if v is not None]
    if not vals:
        return '<svg viewBox="0 0 280 100" xmlns="http://www.w3.org/2000/svg"><text x="140" y="50" text-anchor="middle" font-size="12" fill="#a8a29e">No data</text></svg>'

    v_min = max(0, min(vals) - 0.5)
    v_max = min(6, max(vals) + 0.5)
    if v_max - v_min < 1:
        v_min = max(0, v_min - 0.5)
        v_max = min(6, v_max + 0.5)

    def scale_y(v):
        return pad_t + inner_h - ((v - v_min) / (v_max - v_min)) * inner_h

    # X positions
    points = []
    x_labels = []
    if prior is not None:
        points.append(("prior", pad_l, scale_y(prior), prior))
        x_labels.append((pad_l, "'24-25"))
    points.append(("current", pad_l + inner_w * (0.5 if prior is not None else 0), scale_y(current), current))
    x_labels.append((points[-1][1], "'25-26"))
    if projected is not None:
        points.append(("projected", pad_l + inner_w, scale_y(projected), projected))
        x_labels.append((pad_l + inner_w, "Target"))

    els = []
    els.append(f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:{w}px;font-family:\'DM Sans\',sans-serif">')

    # Grid lines
    for gv in range(int(v_min), int(v_max) + 1):
        if v_min <= gv <= v_max:
            gy = scale_y(gv)
            els.append(line_el(pad_l - 5, gy, w - pad_r, gy, "#e2ddd8", 0.7, "3 3"))
            els.append(text_el(pad_l - 8, gy, str(gv), 9, NEUTRAL, anchor="end", dy=3))

    # Connecting lines
    for i in range(len(points) - 1):
        _, x1, y1, _ = points[i]
        kind, x2, y2, _ = points[i + 1]
        dash = "5 3" if kind == "projected" else ""
        els.append(line_el(x1, y1, x2, y2, GREEN, 2, dash))

    # Dots + labels
    for kind, x, y, v in points:
        if kind == "prior":
            els.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{CHART_BG}" stroke="{NEUTRAL}" stroke-width="1.5"/>')
        elif kind == "projected":
            els.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{CHART_BG}" stroke="{GREEN}" stroke-width="1.5" stroke-dasharray="3 2"/>')
        else:
            els.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{GREEN}"/>')
        els.append(text_el(x, y - 10, f"{v:.1f}", 10, GREEN, "600", "middle"))

    # X labels
    for x, lbl in x_labels:
        els.append(text_el(x, h - 4, lbl, 9, NEUTRAL, anchor="middle"))

    els.append("</svg>")
    return "\n".join(els)


# ─── Content-Area Bars ────────────────────────
def chart_content_bars(s, w=260, h=80):
    """Horizontal bars for classroom grade percentages."""
    pad_l, bar_w = 60, 180
    bar_h, gap = 12, 5
    subjects = [("ELA", s["ela_pct"], BLUE), ("Math", s["math_pct"], GREEN), ("Science", s["sci_pct"], PURPLE), ("Soc. Studies", s["ss_pct"], AMBER)]

    els = []
    els.append(f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:{w}px;font-family:\'DM Sans\',sans-serif">')

    for i, (lbl, val, clr) in enumerate(subjects):
        y = i * (bar_h + gap) + 2
        els.append(text_el(pad_l - 4, y + bar_h - 2, lbl, 10, "#57534e", anchor="end"))
        els.append(bar(pad_l, y, bar_w, bar_h, "#e8e4df", rx=4))
        if val is not None:
            bw = (val / 100) * bar_w
            clr_actual = "#c0392b" if val < 70 else (MID_GREEN if val >= 90 else clr)
            els.append(bar(pad_l, y, bw, bar_h, clr_actual, rx=4, opacity=0.85))
            els.append(text_el(pad_l + bw + 4, y + bar_h - 2, f"{val:.0f}%", 9, clr_actual, "600"))
        else:
            els.append(text_el(pad_l + 8, y + bar_h - 2, "N/A", 9, NEUTRAL))

    els.append("</svg>")
    return "\n".join(els)


# ─────────────────────────────────────────────
# 5. SHARED CSS
# ─────────────────────────────────────────────

SHARED_CSS = """
:root {
  --bg:         #faf8f5;
  --bg2:        #f3efe9;
  --text:       #1c1917;
  --text2:      #57534e;
  --green:      #2d6a4f;
  --mid-green:  #52b788;
  --light-green:#95d5b2;
  --terracotta: #e76f51;
  --amber:      #c17b2e;
  --amber-bg:   #f4a261;
  --neutral:    #a8a29e;
  --blue:       #457b9d;
  --purple:     #7b5ea7;
  --border:     #e2ddd8;
  --shadow:     0 2px 12px rgba(28,25,23,.07);
  --tier-newcomer:  #c0392b;
  --tier-literacy:  #e76f51;
  --tier-ontrack:   #c17b2e;
  --tier-accel:     #52b788;
  --tier-exit:      #2d6a4f;
}

*, *::before, *::after { box-sizing:border-box; margin:0; padding:0; }
html { scroll-behavior:smooth; }
body {
  font-family: 'DM Sans', sans-serif;
  background: var(--bg);
  color: var(--text);
  font-size: 15px;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}

.site-header {
  background: var(--green);
  color: white;
  padding: 3.5rem 2rem 3rem;
  position: relative;
  overflow: hidden;
}
.site-header::before {
  content: "";
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 80% 60% at 110% 50%, #1b4332 0%, transparent 60%);
}
.header-inner {
  max-width: 1100px;
  margin: 0 auto;
  position: relative;
}
.header-eyebrow {
  font-size: .8rem;
  letter-spacing: .12em;
  text-transform: uppercase;
  opacity: .7;
  margin-bottom: .6rem;
}
.header-title {
  font-family: 'DM Serif Display', serif;
  font-size: clamp(2rem, 5vw, 3.2rem);
  font-weight: 400;
  line-height: 1.15;
  margin-bottom: .9rem;
}
.header-sub {
  opacity: .8;
  font-size: 1rem;
  max-width: 560px;
}
.header-meta {
  display: flex;
  gap: 2rem;
  margin-top: 2rem;
  flex-wrap: wrap;
}
.header-stat { display: flex; flex-direction: column; }
.header-stat-num {
  font-family: 'DM Serif Display', serif;
  font-size: 2.2rem;
  line-height: 1;
}
.header-stat-label {
  font-size: .78rem;
  opacity: .7;
  text-transform: uppercase;
  letter-spacing: .08em;
  margin-top: .2rem;
}

.page-body {
  display: grid;
  grid-template-columns: 11rem 1fr;
  max-width: 1280px;
  margin: 0 auto;
}
.sidebar-nav {
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  padding: 2.2rem .5rem 3rem 1.5rem;
  border-right: 1px solid var(--border);
  scrollbar-width: none;
}
.sidebar-nav::-webkit-scrollbar { display: none; }
.nav-label {
  font-size: .6rem;
  letter-spacing: .1em;
  text-transform: uppercase;
  color: var(--neutral);
  padding: 0 .5rem .8rem;
  margin-bottom: .2rem;
  border-bottom: 1px solid var(--border);
}
.nav-link {
  display: flex;
  align-items: baseline;
  gap: .45rem;
  padding: .4rem .5rem;
  border-radius: 5px;
  font-size: .78rem;
  line-height: 1.3;
  text-decoration: none;
  color: var(--neutral);
  transition: color .2s, background .2s;
}
.nav-link:hover { color: var(--text); background: var(--bg2); }
.nav-num {
  font-family: 'DM Serif Display', serif;
  font-size: .7rem;
  opacity: .5;
  min-width: 1.1rem;
}

.main-content {
  max-width: 960px;
  padding: 3rem 2.5rem 6rem;
}

.section { margin-bottom: 4rem; }
.section-head {
  display: flex;
  align-items: baseline;
  gap: .7rem;
  margin-bottom: 1.8rem;
  padding-bottom: .7rem;
  border-bottom: 2px solid var(--border);
}
.section-num {
  font-family: 'DM Serif Display', serif;
  font-size: 1.5rem;
  color: var(--green);
}
.section-title {
  font-family: 'DM Serif Display', serif;
  font-size: 1.4rem;
  color: var(--text);
}

.card {
  background: white;
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1.4rem;
  box-shadow: var(--shadow);
  margin-bottom: 1.2rem;
}
.card-title {
  font-family: 'DM Serif Display', serif;
  font-size: 1.1rem;
  margin-bottom: .8rem;
  color: var(--text);
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}
.kpi-card {
  background: white;
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1.2rem;
  box-shadow: var(--shadow);
  text-align: center;
}
.kpi-num {
  font-family: 'DM Serif Display', serif;
  font-size: 2rem;
  line-height: 1;
  color: var(--green);
}
.kpi-label {
  font-size: .75rem;
  color: var(--text2);
  text-transform: uppercase;
  letter-spacing: .06em;
  margin-top: .3rem;
}
.kpi-card.accent .kpi-num { color: var(--terracotta); }

.badge {
  display: inline-block;
  font-size: .7rem;
  font-weight: 600;
  letter-spacing: .03em;
  padding: .2rem .55rem;
  border-radius: 4px;
  text-transform: uppercase;
}
.badge-risk { background: #c0392b18; color: #c0392b; }
.badge-ltel { background: #e76f5118; color: #e76f51; }
.badge-iep  { background: #457b9d18; color: #457b9d; }
.badge-ok   { background: #2d6a4f14; color: #2d6a4f; }

.insight-box {
  background: var(--bg2);
  border-left: 3px solid var(--green);
  border-radius: 0 8px 8px 0;
  padding: .9rem 1.2rem;
  margin: 1rem 0;
  font-size: .88rem;
  color: var(--text2);
}
.insight-box.warn { border-left-color: var(--terracotta); }

.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

@media (max-width: 900px) {
  .page-body { grid-template-columns: 1fr; }
  .sidebar-nav {
    position: relative; height: auto; border-right: none;
    border-bottom: 1px solid var(--border);
    padding: 1rem 1.5rem; display: flex; flex-wrap: wrap; gap: .2rem .6rem;
  }
  .nav-label { width: 100%; border-bottom: none; padding-bottom: .4rem; }
  .nav-num { display: none; }
  .two-col { grid-template-columns: 1fr; }
}
@media (max-width: 700px) {
  .main-content { padding: 2rem 1.2rem 4rem; }
  .kpi-grid { grid-template-columns: 1fr 1fr; }
}
"""

FONTS_LINK = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap" rel="stylesheet">'

# ─────────────────────────────────────────────
# 6. FILE 1: GROUPING PLAN
# ─────────────────────────────────────────────

# Progression order: Newcomer → Literacy Gap → On Track → Accelerating → Exit-Ready
TIERS_PROGRESSION = [TIERS[1], TIERS[2], TIERS[3], TIERS[4], TIERS[0]]

def _tier_dist_row(t, n_total):
    group = tier_groups[t["key"]]
    count = len(group)
    pct = round(count / n_total * 100)
    names = ", ".join(s["first"] for s in group)
    return f"""<div style="margin-bottom:1rem">
      <div style="display:flex;align-items:center;gap:.6rem;margin-bottom:.3rem">
        <div style="width:10px;height:10px;border-radius:3px;background:{t['color']};flex-shrink:0"></div>
        <div style="font-size:.88rem;font-weight:600">{esc(t['name'])}</div>
        <div style="font-family:'DM Serif Display',serif;font-size:1.05rem;color:{t['color']};margin-left:auto">{count}</div>
        <div style="font-size:.78rem;color:var(--text2);min-width:32px">({pct}%)</div>
      </div>
      <div style="height:10px;background:#e8e4df;border-radius:5px;overflow:hidden;margin-bottom:.3rem">
        <div style="width:{pct}%;height:100%;background:{t['color']};border-radius:5px;transition:width .3s"></div>
      </div>
      <div style="font-size:.75rem;color:var(--neutral);padding-left:16px">{esc(names)}</div>
    </div>"""

def _tier_roster_row(s):
    comp = f"{s['composite']:.1f}" if s['composite'] is not None else "—"
    if s['growth'] is not None:
        sign = "+" if s['growth'] >= 0 else ""
        g_str = f"{sign}{s['growth']:.2f}"
        g_color = "var(--green)" if s['growth'] > 0 else "var(--terracotta)"
    else:
        g_str = "—"
        g_color = "var(--neutral)"
    gpa = f"{s['gpa']:.1f}" if s['gpa'] else "—"
    return f"""<tr style="border-bottom:1px solid #f0ece7">
      <td style="padding:.3rem .4rem;font-weight:500">{esc(s['first'])} {esc(s['last'][0])}.</td>
      <td style="text-align:center;padding:.3rem .2rem">{comp}</td>
      <td style="text-align:center;padding:.3rem .2rem;color:{g_color}">{g_str}</td>
      <td style="text-align:center;padding:.3rem .2rem">{gpa}</td>
    </tr>"""

def generate_grouping_plan():
    # Aggregates
    composites = [s["composite"] for s in students if s["composite"] is not None]
    avg_composite = round(sum(composites)/len(composites), 2)
    avg_listen = round(sum(s["listen"] for s in students if s["listen"] is not None) / sum(1 for s in students if s["listen"] is not None), 2)
    avg_speak  = round(sum(s["speak"] for s in students if s["speak"] is not None)  / sum(1 for s in students if s["speak"] is not None), 2)
    avg_read   = round(sum(s["read"] for s in students if s["read"] is not None)   / sum(1 for s in students if s["read"] is not None), 2)
    avg_write  = round(sum(s["write"] for s in students if s["write"] is not None)  / sum(1 for s in students if s["write"] is not None), 2)

    n_total = len(students)
    n_ltel = sum(1 for s in students if s["ltel"])

    # Build sidebar nav
    nav_items = '<div class="nav-label">Sections</div>\n'
    nav_items += '<a class="nav-link" href="#overview"><span class="nav-num">0</span> Cohort Overview</a>\n'
    for i, t in enumerate(TIERS):
        count = len(tier_groups[t["key"]])
        nav_items += f'<a class="nav-link" href="#{t["key"]}"><span class="nav-num">{i+1}</span> {esc(t["name"])} ({count})</a>\n'

    # Build tier sections
    tier_sections = ""
    for idx, t in enumerate(TIERS):
        group = tier_groups[t["key"]]
        if not group:
            continue

        # Tier averages for radar
        t_listen = round(sum(s["listen"] for s in group if s["listen"] is not None) / max(1, sum(1 for s in group if s["listen"] is not None)), 2) if any(s["listen"] for s in group) else 0
        t_speak  = round(sum(s["speak"] for s in group if s["speak"] is not None) / max(1, sum(1 for s in group if s["speak"] is not None)), 2) if any(s["speak"] for s in group) else 0
        t_read   = round(sum(s["read"] for s in group if s["read"] is not None) / max(1, sum(1 for s in group if s["read"] is not None)), 2) if any(s["read"] for s in group) else 0
        t_write  = round(sum(s["write"] for s in group if s["write"] is not None) / max(1, sum(1 for s in group if s["write"] is not None)), 2) if any(s["write"] for s in group) else 0

        # Student cards
        cards_html = ""
        for s in group:
            # Risk badges
            badges = ""
            for risk in s["risks"]:
                cls = "badge-ltel" if risk == "LTEL" else ("badge-iep" if risk == "IEP" else "badge-risk")
                badges += f'<span class="badge {cls}">{esc(risk)}</span> '

            # Growth indicator
            growth_str = ""
            if s["growth"] is not None:
                sign = "+" if s["growth"] >= 0 else ""
                g_color = "var(--green)" if s["growth"] > 0 else "var(--terracotta)"
                growth_str = f'<span style="font-size:.85rem;font-weight:600;color:{g_color}">{sign}{s["growth"]:.2f}</span>'
            elif s["composite"] is not None:
                growth_str = '<span style="font-size:.78rem;color:var(--neutral)">Year 1</span>'

            # Callout for unusual profiles
            callout = ""
            plan = s["plan"]
            if plan["max_gap"] >= 1.0 and plan["weakest"] and plan["strongest"]:
                w_val = {"Listening": s["listen"], "Speaking": s["speak"], "Reading": s["read"], "Writing": s["write"]}
                strong_v = w_val.get(plan["strongest"], 0) or 0
                weak_v = w_val.get(plan["weakest"], 0) or 0
                callout = f'<div class="insight-box warn" style="margin-top:.6rem;padding:.5rem .8rem;font-size:.78rem">{plan["max_gap"]:.1f}-pt gap: {plan["strongest"]} ({strong_v:.1f}) vs {plan["weakest"]} ({weak_v:.1f}) — needs targeted {plan["weakest"].lower()} practice</div>'

            composite_str = f'{s["composite"]:.1f}' if s["composite"] is not None else "—"
            gpa_str = f'{s["gpa"]:.1f}' if s["gpa"] is not None else "—"

            cards_html += f"""
            <div class="card student-card" style="border-top: 3px solid {t['color']}">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:.6rem">
                <div>
                  <div style="font-weight:600;font-size:1rem">{esc(s['name'])}</div>
                  <div style="font-size:.78rem;color:var(--text2)">{esc(s['school'])} · Grade {s['grade']} · {esc(s['lang'])}</div>
                </div>
                <div style="text-align:right">
                  <div style="font-family:'DM Serif Display',serif;font-size:1.4rem;color:{t['color']}">{composite_str}</div>
                  <div style="font-size:.7rem;color:var(--text2);text-transform:uppercase">Composite</div>
                </div>
              </div>
              <div style="display:flex;gap:1rem;align-items:center;margin-bottom:.5rem">
                <div style="flex:1">{chart_mini_modalities(s['listen'], s['speak'], s['read'], s['write'])}</div>
                <div style="text-align:center;min-width:60px">
                  <div style="font-size:.7rem;color:var(--text2);text-transform:uppercase;margin-bottom:.2rem">Growth</div>
                  {growth_str}
                  <div style="font-size:.7rem;color:var(--text2);margin-top:.2rem">GPA {gpa_str}</div>
                </div>
              </div>
              <div style="display:flex;gap:.3rem;flex-wrap:wrap">{badges}</div>
              {callout}
            </div>
            """

        # Strategy list
        strat_html = ""
        for strat in t["strategies"]:
            strat_html += f'<li style="margin-bottom:.3rem">{esc(strat)}</li>'

        tier_sections += f"""
        <div class="section" id="{t['key']}">
          <div class="section-head">
            <span class="section-num" style="color:{t['color']}">{idx+1}</span>
            <span class="section-title">{esc(t['name'])}</span>
            <span class="badge" style="background:{t['color']}18;color:{t['color']};margin-left:auto">{len(group)} student{"s" if len(group) != 1 else ""}</span>
          </div>

          <div class="card" style="border-left:4px solid {t['color']};margin-bottom:1.5rem">
            <div class="card-title" style="color:{t['color']}">{esc(t['name'])} — Instructional Focus</div>
            <p style="font-size:.9rem;color:var(--text2);margin-bottom:.8rem">{esc(t['description'])}</p>
            <div style="font-size:.85rem;font-weight:600;margin-bottom:.3rem">Focus: {esc(t['focus'])}</div>
            <ul style="font-size:.85rem;color:var(--text2);padding-left:1.2rem;margin-top:.5rem">{strat_html}</ul>
          </div>

          <div class="two-col" style="margin-bottom:1.5rem">
            <div>
              <div style="font-size:.85rem;font-weight:600;margin-bottom:.6rem;color:var(--text2);text-transform:uppercase;letter-spacing:.05em">Tier Modality Profile</div>
              {chart_radar(t_listen, t_speak, t_read, t_write, size=220, color=t['color'])}
            </div>
            <div>
              <div style="font-size:.85rem;font-weight:600;margin-bottom:.6rem;color:var(--text2);text-transform:uppercase;letter-spacing:.05em">Student Roster</div>
              <table style="width:100%;font-size:.82rem;border-collapse:collapse">
                <tr style="border-bottom:1px solid var(--border)">
                  <th style="text-align:left;padding:.3rem .4rem;color:var(--text2);font-weight:600">Name</th>
                  <th style="text-align:center;padding:.3rem .2rem;color:var(--text2);font-weight:600">Comp.</th>
                  <th style="text-align:center;padding:.3rem .2rem;color:var(--text2);font-weight:600">Growth</th>
                  <th style="text-align:center;padding:.3rem .2rem;color:var(--text2);font-weight:600">GPA</th>
                </tr>
                {''.join(_tier_roster_row(s) for s in group)}
              </table>
            </div>
          </div>

          <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1rem">
            {cards_html}
          </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Instructional Grouping Plan — Cedar Valley USD · Spring 2026</title>
{FONTS_LINK}
<style>
{SHARED_CSS}

.student-card {{
  transition: transform .15s ease, box-shadow .15s ease;
}}
.student-card:hover {{
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(28,25,23,.12);
}}
</style>
</head>
<body>
<header class="site-header">
  <div class="header-inner">
    <div class="header-eyebrow">Cedar Valley Unified School District · EL Program</div>
    <h1 class="header-title">Instructional Grouping Plan</h1>
    <p class="header-sub">Class-level tier assignments based on ACCESS proficiency, growth trajectory, RISE performance, and classroom grades. Spring 2026.</p>
    <div class="header-meta">
      <div class="header-stat"><span class="header-stat-num">{n_total}</span><span class="header-stat-label">EL Students</span></div>
      <div class="header-stat"><span class="header-stat-num">5</span><span class="header-stat-label">Tiers</span></div>
      <div class="header-stat"><span class="header-stat-num">{avg_composite}</span><span class="header-stat-label">Avg Composite</span></div>
      <div class="header-stat"><span class="header-stat-num">{n_ltel}</span><span class="header-stat-label">LTEL</span></div>
    </div>
  </div>
</header>

<div class="page-body">
  <nav class="sidebar-nav">
    {nav_items}
  </nav>
  <main class="main-content">

    <div class="section" id="overview">
      <div class="section-head">
        <span class="section-num">0</span>
        <span class="section-title">Cohort Overview</span>
      </div>

      <div class="kpi-grid">
        <div class="kpi-card"><div class="kpi-num">{avg_listen}</div><div class="kpi-label">Avg Listening</div></div>
        <div class="kpi-card"><div class="kpi-num">{avg_speak}</div><div class="kpi-label">Avg Speaking</div></div>
        <div class="kpi-card"><div class="kpi-num">{avg_read}</div><div class="kpi-label">Avg Reading</div></div>
        <div class="kpi-card accent"><div class="kpi-num">{avg_write}</div><div class="kpi-label">Avg Writing</div></div>
      </div>

      <div class="two-col">
        <div class="card">
          <div class="card-title">Cohort Modality Profile</div>
          <p style="font-size:.82rem;color:var(--text2);margin-bottom:.4rem">Average ACCESS scores across all 22 students. Each axis represents one language modality on a 0–6 scale. A perfectly balanced student would form a symmetrical diamond.</p>
          {chart_radar(avg_listen, avg_speak, avg_read, avg_write, size=260, color=GREEN, annotation="Writing is weakest")}
        </div>
        <div class="card">
          <div class="card-title">Tier Distribution</div>
          <p style="font-size:.82rem;color:var(--text2);margin-bottom:.8rem">Ordered by proficiency level, lowest → highest. Each bar shows the share of the 22-student caseload.</p>
          <div style="margin-top:.5rem">
            {''.join(_tier_dist_row(t, n_total) for t in TIERS_PROGRESSION)}
          </div>
        </div>
      </div>

      <div class="insight-box" style="margin-top:1.5rem">
        <strong>Key finding:</strong> Writing is the weakest domain cohort-wide (avg {avg_write}), trailing Listening ({avg_listen}) by {round(avg_listen - avg_write, 1)} points.
        However, individual students have different profiles — modality-specific intervention is more effective than blanket Writing instruction.
      </div>
    </div>

    {tier_sections}

  </main>
</div>
</body>
</html>"""

    return html


# ─────────────────────────────────────────────
# 7. FILE 2: INDIVIDUAL STUDENT PLANS
# ─────────────────────────────────────────────

def generate_individual_plans():
    # Find each student's tier
    student_tier = {}
    for t in TIERS:
        for s in tier_groups[t["key"]]:
            student_tier[s["id"]] = t

    # Build student selector options
    options = ""
    for s in students:
        options += f'<option value="s{s["id"]}">{esc(s["name"])} — Grade {s["grade"]}, {esc(s["school"])}</option>\n'

    # Build student pages
    pages = ""
    for i, s in enumerate(students):
        t = student_tier.get(s["id"], TIERS[3])  # default to developing on track
        plan = s["plan"]
        display = "block" if i == 0 else "none"

        # Risk badges
        badges = ""
        for risk in s["risks"]:
            cls = "badge-ltel" if risk == "LTEL" else ("badge-iep" if risk == "IEP" else "badge-risk")
            badges += f'<span class="badge {cls}">{esc(risk)}</span> '
        if not s["risks"]:
            badges = '<span class="badge badge-ok">No risk flags</span>'

        # Tier badge
        tier_badge = f'<span class="badge" style="background:{t["color"]}18;color:{t["color"]}">{esc(t["name"])}</span>'

        # RISE performance section
        rise_html = ""
        if s["rise_eligible"]:
            level_colors = {"1": "#c0392b", "2": AMBER, "3": MID_GREEN, "4": GREEN}
            for subj, lv, met in [("ELA", s["ela_level"], s["ela_met"]),
                                   ("Math", s["math_level"], s["math_met"]),
                                   ("Science", s["sci_level"], s["sci_met"])]:
                if lv and lv in ("1","2","3","4"):
                    lv_color = level_colors.get(lv, NEUTRAL)
                    met_txt = "Proficient" if met else "Not Yet"
                    rise_html += f'<div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.4rem"><span style="font-size:.85rem;min-width:60px;font-weight:500">{subj}</span><span class="badge" style="background:{lv_color}18;color:{lv_color}">Level {lv}</span><span style="font-size:.78rem;color:var(--text2)">{met_txt}</span></div>'
                elif lv and "not" in str(lv).lower():
                    rise_html += f'<div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.4rem"><span style="font-size:.85rem;min-width:60px;font-weight:500">{subj}</span><span style="font-size:.78rem;color:var(--neutral)">Not assessed</span></div>'
        else:
            rise_html = '<div style="font-size:.85rem;color:var(--neutral)">Not yet in RISE-eligible grade</div>'

        # Goals
        goals_html = ""
        for gi, goal in enumerate(plan["goals"]):
            goals_html += f'<li style="margin-bottom:.4rem;font-size:.88rem">{esc(goal)}</li>'
        if not plan["goals"]:
            goals_html = '<li style="font-size:.88rem;color:var(--neutral)">Goals will be set after baseline assessment</li>'

        # Strategies
        strat_html = ""
        for strat in plan["strategies"]:
            strat_html += f'<li style="margin-bottom:.3rem;font-size:.85rem">{esc(strat)}</li>'

        # Content insights
        insights_html = ""
        for ins in plan["content_insights"]:
            insights_html += f'<div class="insight-box" style="margin-bottom:.6rem;font-size:.85rem">{esc(ins)}</div>'

        # Attendance
        absent_str = f'{int(s["absent"])} days' if s["absent"] is not None else "N/A"
        absent_color = "var(--terracotta)" if s["absent"] is not None and s["absent"] >= 7 else "var(--text2)"

        composite_str = f'{s["composite"]:.1f}' if s["composite"] is not None else "—"
        gpa_str = f'{s["gpa"]:.2f}' if s["gpa"] is not None else "—"
        years_str = str(s["years_el"]) if s["years_el"] else "< 1"

        pages += f"""
        <div class="student-page" id="s{s['id']}" style="display:{display}">
          <!-- Student Header -->
          <div class="card" style="border-top:4px solid {t['color']};margin-bottom:1.5rem">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:1rem">
              <div>
                <h2 style="font-family:'DM Serif Display',serif;font-size:1.8rem;font-weight:400;margin-bottom:.3rem">{esc(s['name'])}</h2>
                <div style="font-size:.9rem;color:var(--text2)">{esc(s['school'])} · Grade {s['grade']} · {esc(s['lang'])}-speaking · {years_str} yr{"s" if s['years_el'] != 1 else ""} in EL</div>
                <div style="font-size:.85rem;color:var(--text2);margin-top:.2rem">Teacher: {esc(s['teacher'] or 'N/A')}</div>
                <div style="margin-top:.5rem;display:flex;gap:.3rem;flex-wrap:wrap">{tier_badge} {badges}</div>
              </div>
              <div style="text-align:right">
                <div style="font-family:'DM Serif Display',serif;font-size:2.8rem;line-height:1;color:{t['color']}">{composite_str}</div>
                <div style="font-size:.75rem;color:var(--text2);text-transform:uppercase;letter-spacing:.05em">Composite Score</div>
              </div>
            </div>
          </div>

          <!-- Row 2: Radar + Growth -->
          <div class="two-col" style="margin-bottom:1.5rem">
            <div class="card">
              <div class="card-title">Modality Profile</div>
              <div style="display:flex;justify-content:center">
                {chart_radar(s['listen'], s['speak'], s['read'], s['write'], size=260, color=t['color'])}
              </div>
              {f'<div class="insight-box warn" style="margin-top:.8rem;font-size:.82rem">{plan["max_gap"]:.1f}-point gap: {plan["gap_pair"]}</div>' if plan['max_gap'] >= 0.8 else ''}
            </div>
            <div class="card">
              <div class="card-title">Growth Trajectory</div>
              <div style="display:flex;justify-content:center;margin:.5rem 0">
                {chart_growth_trajectory(s['prior_composite'], s['composite'], plan['projected'])}
              </div>
              <div style="display:flex;gap:1.5rem;justify-content:center;margin-top:.5rem">
                <div style="text-align:center">
                  <div style="font-size:.7rem;color:var(--neutral);text-transform:uppercase">GPA</div>
                  <div style="font-family:'DM Serif Display',serif;font-size:1.2rem">{gpa_str}</div>
                </div>
                <div style="text-align:center">
                  <div style="font-size:.7rem;color:var(--neutral);text-transform:uppercase">Absent</div>
                  <div style="font-family:'DM Serif Display',serif;font-size:1.2rem;color:{absent_color}">{absent_str}</div>
                </div>
                <div style="text-align:center">
                  <div style="font-size:.7rem;color:var(--neutral);text-transform:uppercase">IEP</div>
                  <div style="font-family:'DM Serif Display',serif;font-size:1.2rem">{'Yes' if s['iep'] else 'No'}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Row 3: Content Performance + Goals -->
          <div class="two-col">
            <div class="card">
              <div class="card-title">Content-Area Performance</div>
              <div style="margin-bottom:1rem">
                <div style="font-size:.8rem;font-weight:600;color:var(--text2);text-transform:uppercase;letter-spacing:.04em;margin-bottom:.5rem">RISE State Assessment (Spring 2025)</div>
                {rise_html}
              </div>
              <div>
                <div style="font-size:.8rem;font-weight:600;color:var(--text2);text-transform:uppercase;letter-spacing:.04em;margin-bottom:.5rem">Classroom Grades (2025-26)</div>
                {chart_content_bars(s)}
              </div>
              {insights_html}
            </div>
            <div class="card">
              <div class="card-title">Goals & Recommended Strategies</div>
              <div style="margin-bottom:1rem">
                <div style="font-size:.8rem;font-weight:600;color:var(--text2);text-transform:uppercase;letter-spacing:.04em;margin-bottom:.4rem">Specific Goals</div>
                <ol style="padding-left:1.2rem;color:var(--text)">{goals_html}</ol>
              </div>
              <div>
                <div style="font-size:.8rem;font-weight:600;color:var(--text2);text-transform:uppercase;letter-spacing:.04em;margin-bottom:.4rem">Recommended Strategies</div>
                <ul style="padding-left:1.2rem;color:var(--text2)">{strat_html}</ul>
              </div>
            </div>
          </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Individual Student Plans — Cedar Valley USD · Spring 2026</title>
{FONTS_LINK}
<style>
{SHARED_CSS}

.student-selector {{
  position: sticky;
  top: 0;
  z-index: 100;
  background: white;
  border-bottom: 1px solid var(--border);
  padding: .8rem 2rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 8px rgba(28,25,23,.06);
}}
.student-selector select {{
  font-family: 'DM Sans', sans-serif;
  font-size: .9rem;
  padding: .45rem .8rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--bg);
  color: var(--text);
  flex: 1;
  max-width: 400px;
  cursor: pointer;
}}
.student-selector select:focus {{
  outline: none;
  border-color: var(--green);
  box-shadow: 0 0 0 2px rgba(45,106,79,.15);
}}
.nav-btn {{
  font-family: 'DM Sans', sans-serif;
  font-size: .82rem;
  font-weight: 600;
  padding: .4rem .9rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: white;
  color: var(--text2);
  cursor: pointer;
  transition: all .15s;
}}
.nav-btn:hover {{
  background: var(--bg2);
  color: var(--text);
  border-color: var(--green);
}}
.student-count {{
  font-size: .78rem;
  color: var(--neutral);
  white-space: nowrap;
}}

@media print {{
  .site-header {{ padding: 1.5rem 1rem 1rem; }}
  .site-header::before {{ display: none; }}
  .student-selector {{ display: none !important; }}
  .student-page {{ display: block !important; page-break-before: always; }}
  .student-page:first-child {{ page-break-before: avoid; }}
  .page-body {{ display: block; }}
  .sidebar-nav {{ display: none; }}
  .main-content {{ padding: 1rem; max-width: 100%; }}
  body {{ background: white; font-size: 11pt; }}
  .card {{ box-shadow: none; border: 1px solid #ddd; page-break-inside: avoid; }}
  .two-col {{ gap: 1rem; }}
  @page {{ margin: 0.6in; size: letter; }}
}}
</style>
</head>
<body>
<header class="site-header">
  <div class="header-inner">
    <div class="header-eyebrow">Cedar Valley Unified School District · EL Program</div>
    <h1 class="header-title">Individual Student Plans</h1>
    <p class="header-sub">Detailed proficiency profiles, growth projections, and personalized strategy recommendations for each EL student. Spring 2026.</p>
  </div>
</header>

<div class="student-selector">
  <label style="font-size:.82rem;font-weight:600;color:var(--text2);white-space:nowrap">Student:</label>
  <select id="studentSelect" onchange="showStudent(this.value)">
    {options}
  </select>
  <button class="nav-btn" onclick="navStudent(-1)">Prev</button>
  <button class="nav-btn" onclick="navStudent(1)">Next</button>
  <span class="student-count"><span id="currentIdx">1</span> of {len(students)}</span>
</div>

<div style="max-width:960px;margin:0 auto;padding:2rem 2.5rem 6rem">
  {pages}
</div>

<script>
const ids = [{','.join(f'"s{s["id"]}"' for s in students)}];
const sel = document.getElementById('studentSelect');
const idxEl = document.getElementById('currentIdx');

function showStudent(id) {{
  ids.forEach(sid => {{
    document.getElementById(sid).style.display = sid === id ? 'block' : 'none';
  }});
  sel.value = id;
  idxEl.textContent = ids.indexOf(id) + 1;
  window.scrollTo({{ top: 0, behavior: 'smooth' }});
}}

function navStudent(dir) {{
  let idx = ids.indexOf(sel.value);
  idx = (idx + dir + ids.length) % ids.length;
  showStudent(ids[idx]);
}}

document.addEventListener('keydown', e => {{
  if (e.key === 'ArrowLeft') navStudent(-1);
  if (e.key === 'ArrowRight') navStudent(1);
}});
</script>
</body>
</html>"""

    return html


# ─────────────────────────────────────────────
# 8. GENERATE FILES
# ─────────────────────────────────────────────

print("Generating Grouping Plan...")
with open(OUT_DIR / "ELL_Grouping_Plan.html", "w") as f:
    f.write(generate_grouping_plan())
print(f"  Written: {OUT_DIR / 'ELL_Grouping_Plan.html'}")

print("Generating Individual Plans...")
with open(OUT_DIR / "ELL_Individual_Plans.html", "w") as f:
    f.write(generate_individual_plans())
print(f"  Written: {OUT_DIR / 'ELL_Individual_Plans.html'}")

print("\nDone!")
