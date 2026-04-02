#!/usr/bin/env python3
"""
ELL Program Analysis Report Generator
Cedar Valley Unified School District
Reads 4 Excel files, produces self-contained HTML report.
"""

import openpyxl
from pathlib import Path

BASE = Path(__file__).parent.parent  # bamboo/ directory
OUT  = Path(__file__).parent / "ELL_Program_Report.html"

# ─────────────────────────────────────────────
# 1. LOAD DATA
# ─────────────────────────────────────────────

def load_sheet(fname):
    wb = openpyxl.load_workbook(BASE / fname, data_only=True)
    rows = list(wb.active.iter_rows(values_only=True))
    headers = rows[1]
    data = []
    for row in rows[2:]:
        if row[0] is None:
            continue
        if not isinstance(row[0], int):
            continue
        data.append(dict(zip(headers, row)))
    return data

access_py  = load_sheet("ACCESS_Scores_Export_PY2024-25.xlsx")
access_now = load_sheet("ACCESS_Scores_Export_Spring2026.xlsx")
rise       = load_sheet("RISE_StateTest_Results_Spring2025.xlsx")
sis        = load_sheet("SIS_Grades_Export_2025-26.xlsx")

# Normalise header names (remove newlines)
def clean_keys(records):
    out = []
    for rec in records:
        out.append({k.replace("\n","_").strip() if k else k: v for k,v in rec.items()})
    return out

access_py  = clean_keys(access_py)
access_now = clean_keys(access_now)
rise       = clean_keys(rise)
sis        = clean_keys(sis)

# Index by Student ID
def by_id(records):
    return {r["Student ID"]: r for r in records}

ap   = by_id(access_py)
an   = by_id(access_now)
ri   = by_id(rise)
si   = by_id(sis)

ALL_IDS = sorted(an.keys())

# ─────────────────────────────────────────────
# 2. COMPUTE METRICS
# ─────────────────────────────────────────────

def safe_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

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
    s["ltel"]   = str(a.get("LTEL_(5+ yrs)", a.get("LTEL\n(5+ yrs)", "No"))).strip() == "Yes"

    # ACCESS current
    s["listen"]    = safe_float(a["Listening"])
    s["speak"]     = safe_float(a["Speaking"])
    s["read"]      = safe_float(a["Reading"])
    s["write"]     = safe_float(a["Writing"])
    s["oral"]      = safe_float(a["Oral_Language"])
    s["literacy"]  = safe_float(a["Literacy"])
    s["composite"] = safe_float(a["Composite_Score"])
    s["prof_level"] = safe_float(a["Proficiency_Level"])

    # ACCESS prior
    if sid in ap:
        p = ap[sid]
        prior = safe_float(p.get("Composite_Score") or p.get("Composite\nScore"))
        s["prior_composite"] = prior  # None if Year-1
    else:
        s["prior_composite"] = None

    s["growth"] = None
    if s["composite"] is not None and s["prior_composite"] is not None:
        s["growth"] = round(s["composite"] - s["prior_composite"], 3)

    # RISE
    if sid in ri:
        r = ri[sid]
        def get_score(key_fragment):
            for k,v in r.items():
                if k and key_fragment.lower() in k.lower():
                    return v
            return None
        ela_score = get_score("ELA_Scale")
        ela_met   = get_score("ELA Met")
        math_score= get_score("Math_Scale")
        math_met  = get_score("Math Met")
        sci_score = get_score("Science_Scale")
        sci_met   = get_score("Science Met")
        s["ela_score"] = safe_float(ela_score)
        s["ela_met"]   = str(ela_met).strip() == "Yes"
        s["ela_level"] = str(get_score("ELA_Level") or "").split("—")[0].strip()
        s["math_score"]= safe_float(math_score)
        s["math_met"]  = str(math_met).strip() == "Yes"
        s["math_level"]= str(get_score("Math_Level") or "").split("—")[0].strip()
        s["sci_score"] = safe_float(sci_score)
        s["sci_met"]   = str(sci_met).strip() == "Yes"
        s["sci_level"] = str(get_score("Science_Level") or "").split("—")[0].strip()
        s["rise_eligible"] = s["ela_score"] is not None
    else:
        s["ela_score"]=s["ela_met"]=s["ela_level"]=None
        s["math_score"]=s["math_met"]=s["math_level"]=None
        s["sci_score"]=s["sci_met"]=s["sci_level"]=None
        s["rise_eligible"]=False

    # SIS
    if sid in si:
        g = si[sid]
        def gv(key_fragment):
            for k,v in g.items():
                if k and key_fragment.lower() in k.lower():
                    return v
            return None
        s["teacher"]  = gv("EL Teacher")
        s["el_status"]= str(gv("EL Status") or "")
        s["iep"]      = str(gv("IEP") or "").strip() == "Yes"
        s["ela_pct"]  = safe_float(gv("ELA_(%)") or gv("ELA\n(%)"))
        s["math_pct"] = safe_float(gv("Math_(%)") or gv("Math\n(%)"))
        s["sci_pct"]  = safe_float(gv("Science_(%)") or gv("Science\n(%)"))
        s["ss_pct"]   = safe_float(gv("Social") or gv("Social_Studies") or gv("Social\nStudies"))
        s["gpa"]      = safe_float(gv("GPA_(4.0)") or gv("GPA\n(4.0)"))
        s["absent"]   = safe_float(gv("Days_Absent") or gv("Days\nAbsent"))
    else:
        s["teacher"]=s["el_status"]=None
        s["iep"]=False
        s["ela_pct"]=s["math_pct"]=s["sci_pct"]=s["ss_pct"]=s["gpa"]=s["absent"]=None

    # Risk flags
    risks = []
    if s["composite"] is not None and s["composite"] < 2.0:
        risks.append("Very Low ACCESS")
    if s["ltel"]:
        risks.append("LTEL")
    if s["gpa"] is not None and s["gpa"] < 1.5:
        risks.append("Low GPA")
    if s["absent"] is not None and s["absent"] >= 7:
        risks.append("Chronic Absence")
    if s["iep"]:
        risks.append("IEP")
    s["risks"] = risks
    s["at_risk"] = len(risks) >= 2

    students.append(s)

# ── Aggregate stats ──────────────────────────────
n_total = len(students)
n_ltel  = sum(1 for s in students if s["ltel"])
composites = [s["composite"] for s in students if s["composite"] is not None]
avg_composite = round(sum(composites)/len(composites), 2) if composites else 0

growths = [s["growth"] for s in students if s["growth"] is not None]
avg_growth = round(sum(growths)/len(growths), 2) if growths else 0
n_improved = sum(1 for g in growths if g > 0)

rise_elig = [s for s in students if s["rise_eligible"]]
ela_met_n  = sum(1 for s in rise_elig if s["ela_met"])
math_met_n = sum(1 for s in rise_elig if s["math_met"])
ela_pct_met  = round(ela_met_n / len(rise_elig) * 100) if rise_elig else 0
math_pct_met = round(math_met_n / len(rise_elig) * 100) if rise_elig else 0

gpas = [s["gpa"] for s in students if s["gpa"] is not None]
avg_gpa = round(sum(gpas)/len(gpas), 2) if gpas else 0

at_risk_students = [s for s in students if s["at_risk"]]

# Modality averages
def modal_avg(key):
    vals = [s[key] for s in students if s[key] is not None]
    return round(sum(vals)/len(vals), 2) if vals else 0

avg_listen = modal_avg("listen")
avg_speak  = modal_avg("speak")
avg_read   = modal_avg("read")
avg_write  = modal_avg("write")

# LTEL vs non-LTEL
ltel_s = [s for s in students if s["ltel"]]
nonltel_s = [s for s in students if not s["ltel"]]
def grp_avg(group, key):
    vals = [s[key] for s in group if s[key] is not None]
    return round(sum(vals)/len(vals), 2) if vals else 0

ltel_composite  = grp_avg(ltel_s, "composite")
nonltel_composite = grp_avg(nonltel_s, "composite")
ltel_gpa   = grp_avg(ltel_s, "gpa")
nonltel_gpa= grp_avg(nonltel_s, "gpa")
ltel_rise_elig   = [s for s in ltel_s   if s["rise_eligible"]]
nonltel_rise_elig= [s for s in nonltel_s if s["rise_eligible"]]
ltel_ela_pct  = round(sum(1 for s in ltel_rise_elig   if s["ela_met"])/len(ltel_rise_elig)*100)   if ltel_rise_elig   else 0
nonltel_ela_pct= round(sum(1 for s in nonltel_rise_elig if s["ela_met"])/len(nonltel_rise_elig)*100) if nonltel_rise_elig else 0

# By school
schools = sorted(set(s["school"] for s in students))
school_abbr = {
    "Valley Ridge Elementary":     "Valley Ridge Elem",
    "Lakeshore Elementary":        "Lakeshore Elem",
    "Canyon Ridge Middle School":  "Canyon Ridge MS",
    "Pioneer Middle School":       "Pioneer MS",
}
school_data = {}
for sch in schools:
    grp = [s for s in students if s["school"] == sch]
    school_data[sch] = {
        "n": len(grp),
        "composite": grp_avg(grp, "composite"),
        "gpa": grp_avg(grp, "gpa"),
        "ltel": sum(1 for s in grp if s["ltel"]),
    }

# By home language
languages = sorted(set(s["lang"] for s in students))
lang_data = {}
for lang in languages:
    grp = [s for s in students if s["lang"] == lang]
    lang_data[lang] = {
        "n": len(grp),
        "composite": grp_avg(grp, "composite"),
        "gpa": grp_avg(grp, "gpa"),
    }

# RISE level distribution (for RISE-eligible only)
def level_dist(subject_key):
    counts = {"1":0, "2":0, "3":0, "4":0, "ineligible":0}
    for s in students:
        lv = s.get(subject_key)
        lv = str(lv).strip() if lv else ""
        if lv in ("1","2","3","4"):
            counts[lv] += 1
        elif not s["rise_eligible"]:
            counts["ineligible"] += 1
    return counts

ela_dist  = level_dist("ela_level")
math_dist = level_dist("math_level")
sci_dist  = level_dist("sci_level")

# Reclassification candidates
reclass_ready     = [s for s in students if s["composite"] is not None and s["composite"] >= 4.5]
reclass_approach  = [s for s in students if s["composite"] is not None and 4.2 <= s["composite"] < 4.5]

# Sort students by growth for chart
growth_students = sorted([s for s in students if s["growth"] is not None],
                          key=lambda x: x["growth"], reverse=True)

# ─────────────────────────────────────────────
# 3. SVG CHART HELPERS
# ─────────────────────────────────────────────

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def bar(x, y, w, h, color, rx=3, opacity=1.0):
    w = max(w, 0)
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{color}" opacity="{opacity}"/>'

def text_el(x, y, content, size=12, color="#1c1917", weight="normal", anchor="start", dy=0):
    content = str(content).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    return f'<text x="{x:.1f}" y="{y:.1f}" dy="{dy}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{content}</text>'

def line_el(x1,y1,x2,y2,color="#e5e7eb",width=1,dash=""):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{width}"{dash_attr}/>'

CHART_BG   = "#faf8f5"
GREEN      = "#2d6a4f"
MID_GREEN  = "#52b788"
LIGHT_GREEN= "#95d5b2"
TERRACOTTA = "#e76f51"
AMBER      = "#f4a261"
NEUTRAL    = "#a8a29e"
BLUE       = "#457b9d"
PURPLE     = "#7b5ea7"

LEVEL_COLORS = {"1": TERRACOTTA, "2": AMBER, "3": MID_GREEN, "4": GREEN}
LANG_COLORS  = {
    "Spanish":    "#457b9d",
    "Somali":     "#e76f51",
    "Tongan":     "#7b5ea7",
    "Arabic":     "#2d6a4f",
    "Portuguese": "#f4a261",
}

# ─── Chart: ACCESS YoY Growth (dumbbell) ─────
def chart_yoy_growth():
    W, PAD_L, PAD_R, PAD_T, PAD_B = 760, 160, 80, 30, 20
    ROW_H = 34
    n = len(growth_students)
    H = PAD_T + n * ROW_H + PAD_B + 40
    INNER_W = W - PAD_L - PAD_R
    MIN_V, MAX_V = 1.0, 5.0
    def scale(v):
        return PAD_L + (v - MIN_V) / (MAX_V - MIN_V) * INNER_W

    els = []
    els.append(f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:{W}px;font-family:\'DM Sans\',sans-serif">')
    els.append(f'<rect width="{W}" height="{H}" fill="{CHART_BG}"/>')

    # grid lines + labels
    for v in [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]:
        x = scale(v)
        els.append(line_el(x, PAD_T-10, x, H - PAD_B - 20, "#e2ddd8", 1, "4 3"))
        els.append(text_el(x, H - PAD_B - 5, str(v), 11, NEUTRAL, anchor="middle"))

    # exit threshold line
    x45 = scale(4.5)
    els.append(line_el(x45, PAD_T-10, x45, H-PAD_B-20, TERRACOTTA, 1.5, "6 3"))
    els.append(text_el(x45+4, PAD_T+4, "Exit threshold", 9.5, TERRACOTTA, anchor="start"))

    # rows
    for i, s in enumerate(growth_students):
        y_center = PAD_T + i * ROW_H + ROW_H/2
        prior = s["prior_composite"]
        curr  = s["composite"]
        growth= s["growth"]
        x_prior = scale(prior)
        x_curr  = scale(curr)
        color = GREEN if growth >= 0 else TERRACOTTA
        ltel_mark = " ●" if s["ltel"] else ""

        # connecting line
        els.append(line_el(x_prior, y_center, x_curr, y_center, "#d6d3ce", 1.5))
        # prior dot (hollow)
        els.append(f'<circle cx="{x_prior:.1f}" cy="{y_center:.1f}" r="6" fill="{CHART_BG}" stroke="{NEUTRAL}" stroke-width="1.5"/>')
        # current dot (filled)
        els.append(f'<circle cx="{x_curr:.1f}" cy="{y_center:.1f}" r="7" fill="{color}"/>')
        # growth label
        sign = "+" if growth >= 0 else ""
        els.append(text_el(max(x_prior, x_curr) + 12, y_center, f"{sign}{growth:.2f}", 11, color, "600", dy=4))
        # name
        abbr = f"{s['first'][0]}. {s['last']}{ltel_mark}"
        els.append(text_el(PAD_L - 8, y_center, abbr, 12, "#3d3530", anchor="end", dy=4))

    # legend
    ly = H - 8
    els.append(f'<circle cx="{PAD_L}" cy="{ly}" r="6" fill="{GREEN}"/>')
    els.append(text_el(PAD_L+10, ly, "Current (2025-26)", 11, NEUTRAL, anchor="start", dy=4))
    els.append(f'<circle cx="{PAD_L+150}" cy="{ly}" r="6" fill="{CHART_BG}" stroke="{NEUTRAL}" stroke-width="1.5"/>')
    els.append(text_el(PAD_L+162, ly, "Prior (2024-25)", 11, NEUTRAL, anchor="start", dy=4))
    els.append(text_el(PAD_L+310, ly, "● = LTEL student", 11, NEUTRAL, anchor="start", dy=4))

    els.append("</svg>")
    return "\n".join(els)

# ─── Chart: Modality Averages ─────────────────
def chart_modalities():
    W, H = 480, 220
    PAD_L, PAD_R, PAD_T, PAD_B = 110, 60, 20, 30
    INNER_W = W - PAD_L - PAD_R
    modals = [
        ("Listening",  avg_listen,  "#457b9d"),
        ("Speaking",   avg_speak,   "#2d6a4f"),
        ("Reading",    avg_read,    "#7b5ea7"),
        ("Writing",    avg_write,   TERRACOTTA),
    ]
    MAX_V = 4.0
    BAR_H = 32
    GAP   = 8
    MIN_V = 0

    els = []
    total_h = len(modals)*(BAR_H+GAP) + PAD_T + PAD_B + 20
    els.append(f'<svg viewBox="0 0 {W} {total_h}" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:{W}px;font-family:\'DM Sans\',sans-serif">')
    els.append(f'<rect width="{W}" height="{total_h}" fill="{CHART_BG}"/>')

    def scale(v):
        return PAD_L + v / MAX_V * INNER_W

    for i, (label, val, color) in enumerate(modals):
        y = PAD_T + i*(BAR_H+GAP)
        w = val / MAX_V * INNER_W
        # track bg
        els.append(bar(PAD_L, y, INNER_W, BAR_H, "#ede9e4", rx=4))
        # value bar
        els.append(bar(PAD_L, y, w, BAR_H, color, rx=4))
        # label
        els.append(text_el(PAD_L-8, y+BAR_H/2, label, 13, "#3d3530", anchor="end", dy=5))
        # value
        els.append(text_el(PAD_L + w + 8, y+BAR_H/2, f"{val:.2f}", 13, color, "700", dy=5))

    # scale ticks
    yt = PAD_T + len(modals)*(BAR_H+GAP) + 8
    for v in [0, 1, 2, 3, 4]:
        x = scale(v)
        els.append(line_el(x, PAD_T-4, x, PAD_T + len(modals)*(BAR_H+GAP), "#d6d3ce", 0.5))
        els.append(text_el(x, yt+14, str(v), 10, NEUTRAL, anchor="middle"))

    els.append("</svg>")
    return "\n".join(els)

# ─── Chart: LTEL vs Non-LTEL ─────────────────
def chart_ltel_comparison():
    W, H = 480, 200
    PAD_L, PAD_R, PAD_T, PAD_B = 120, 60, 40, 30
    INNER_W = W - PAD_L - PAD_R
    metrics = [
        ("ACCESS Composite", ltel_composite, nonltel_composite, 4.0),
        ("GPA (4.0)",        ltel_gpa,       nonltel_gpa,       4.0),
        ("ELA% Met Standard",ltel_ela_pct/100, nonltel_ela_pct/100, 1.0),
    ]
    BAR_H = 18
    GROUP_H = 50
    els = []
    total_h = PAD_T + len(metrics)*GROUP_H + PAD_B + 20
    els.append(f'<svg viewBox="0 0 {W} {total_h}" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:{W}px;font-family:\'DM Sans\',sans-serif">')
    els.append(f'<rect width="{W}" height="{total_h}" fill="{CHART_BG}"/>')

    # legend at top
    els.append(bar(PAD_L, 12, 16, 12, TERRACOTTA, rx=2))
    els.append(text_el(PAD_L+20, 12, f"LTEL (n={len(ltel_s)})", 11, "#3d3530", dy=10))
    els.append(bar(PAD_L+130, 12, 16, 12, GREEN, rx=2))
    els.append(text_el(PAD_L+150, 12, f"Active EL (n={len(nonltel_s)})", 11, "#3d3530", dy=10))

    for i, (label, ltel_val, nonltel_val, max_v) in enumerate(metrics):
        y_base = PAD_T + i*GROUP_H
        els.append(text_el(PAD_L-8, y_base+BAR_H/2, label, 11.5, "#3d3530", anchor="end", dy=5))
        # LTEL bar
        w1 = ltel_val / max_v * INNER_W
        els.append(bar(PAD_L, y_base, INNER_W, BAR_H, "#ede9e4", rx=3))
        els.append(bar(PAD_L, y_base, w1, BAR_H, TERRACOTTA, rx=3))
        disp1 = f"{ltel_val:.2f}" if max_v <= 4 else f"{int(ltel_val*100)}%"
        els.append(text_el(PAD_L+w1+6, y_base+BAR_H/2, disp1, 11, TERRACOTTA, "700", dy=5))
        # non-LTEL bar
        w2 = nonltel_val / max_v * INNER_W
        y2 = y_base + BAR_H + 4
        els.append(bar(PAD_L, y2, INNER_W, BAR_H, "#ede9e4", rx=3))
        els.append(bar(PAD_L, y2, w2, BAR_H, GREEN, rx=3))
        disp2 = f"{nonltel_val:.2f}" if max_v <= 4 else f"{int(nonltel_val*100)}%"
        els.append(text_el(PAD_L+w2+6, y2+BAR_H/2, disp2, 11, GREEN, "700", dy=5))

    els.append("</svg>")
    return "\n".join(els)

# ─── Chart: RISE Performance Levels ──────────
def chart_rise():
    W, H = 580, 200
    PAD_L, PAD_R, PAD_T, PAD_B = 100, 120, 30, 20
    INNER_W = W - PAD_L - PAD_R
    BAR_H = 32
    GAP   = 14
    total = n_total  # use all students as denominator for transparency

    subjects = [
        ("ELA",     ela_dist),
        ("Math",    math_dist),
        ("Science", sci_dist),
    ]
    levels = ["1","2","3","4"]
    level_labels = {"1":"Below Prof.","2":"Approaching","3":"Proficient","4":"Advanced"}

    total_h = PAD_T + len(subjects)*(BAR_H+GAP) + PAD_B + 40
    els = []
    els.append(f'<svg viewBox="0 0 {W} {total_h}" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:{W}px;font-family:\'DM Sans\',sans-serif">')
    els.append(f'<rect width="{W}" height="{total_h}" fill="{CHART_BG}"/>')

    for i, (subj, dist) in enumerate(subjects):
        y = PAD_T + i*(BAR_H+GAP)
        tested = sum(dist.get(lv,0) for lv in levels)
        els.append(text_el(PAD_L-8, y+BAR_H/2, subj, 13, "#3d3530", "600", anchor="end", dy=5))
        if tested == 0:
            els.append(bar(PAD_L, y, INNER_W, BAR_H, "#ede9e4", rx=4))
            els.append(text_el(PAD_L+INNER_W/2, y+BAR_H/2, "Not assessed at these grades", 11, NEUTRAL, anchor="middle", dy=5))
            continue
        x_cur = PAD_L
        for lv in levels:
            cnt = dist.get(lv, 0)
            w = (cnt/total) * INNER_W if total > 0 else 0
            if w > 0:
                els.append(bar(x_cur, y, w, BAR_H, LEVEL_COLORS[lv], rx=0))
                if w > 22:
                    els.append(text_el(x_cur+w/2, y+BAR_H/2, str(cnt), 11, "white", "700", anchor="middle", dy=5))
            x_cur += w
        # ineligible
        inelig = dist.get("ineligible", 0)
        if inelig > 0:
            w_i = inelig/total * INNER_W
            els.append(bar(x_cur, y, w_i, BAR_H, "#ddd9d4", rx=0))
            if w_i > 22:
                els.append(text_el(x_cur+w_i/2, y+BAR_H/2, f"N/A ({inelig})", 10, NEUTRAL, anchor="middle", dy=5))
        # % met standard label
        met_pct = ela_pct_met if subj=="ELA" else (math_pct_met if subj=="Math" else
                  round(sum(1 for s in students if s["rise_eligible"] and s.get("sci_met"))/
                  max(len([s for s in students if s["rise_eligible"] and s["sci_score"] is not None]),1)*100))
        els.append(text_el(W-PAD_R+8, y+BAR_H/2, f"{met_pct}% met std", 11, GREEN, "600", anchor="start", dy=5))

    # Legend
    ly = total_h - 22
    lx = PAD_L
    for lv, label in level_labels.items():
        els.append(bar(lx, ly, 14, 12, LEVEL_COLORS[lv], rx=2))
        els.append(text_el(lx+18, ly, label, 10, NEUTRAL, dy=10))
        lx += 90
    els.append(bar(lx, ly, 14, 12, "#ddd9d4", rx=2))
    els.append(text_el(lx+18, ly, "Not assessed", 10, NEUTRAL, dy=10))

    els.append("</svg>")
    return "\n".join(els)

# ─── Chart: By School ────────────────────────
def chart_by_school():
    W = 580
    PAD_L, PAD_R, PAD_T, PAD_B = 145, 60, 20, 30
    INNER_W = W - PAD_L - PAD_R
    BAR_H = 18
    GAP   = 4
    GROUP_GAP = 20
    MAX_COMP = 4.0
    MAX_GPA  = 4.0
    school_list = sorted(schools, key=lambda s: school_data[s]["composite"], reverse=True)
    n_schools = len(school_list)
    total_h = PAD_T + n_schools*(2*BAR_H+GAP+GROUP_GAP) + PAD_B + 30

    els = []
    els.append(f'<svg viewBox="0 0 {W} {total_h}" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:{W}px;font-family:\'DM Sans\',sans-serif">')
    els.append(f'<rect width="{W}" height="{total_h}" fill="{CHART_BG}"/>')

    # legend
    els.append(bar(PAD_L, 6, 14, 10, GREEN, rx=2))
    els.append(text_el(PAD_L+18, 6, "ACCESS Composite", 10.5, "#3d3530", dy=8))
    els.append(bar(PAD_L+155, 6, 14, 10, BLUE, rx=2))
    els.append(text_el(PAD_L+173, 6, "GPA", 10.5, "#3d3530", dy=8))

    for i, sch in enumerate(school_list):
        d = school_data[sch]
        y = PAD_T + 10 + i*(2*BAR_H+GAP+GROUP_GAP)
        abbr = school_abbr.get(sch, sch)
        els.append(text_el(PAD_L-8, y+BAR_H/2, abbr, 11.5, "#3d3530", anchor="end", dy=5))
        els.append(text_el(PAD_L-8, y+BAR_H+GAP+BAR_H/2, f"n={d['n']}", 10, NEUTRAL, anchor="end", dy=5))

        # composite
        w1 = d["composite"] / MAX_COMP * INNER_W
        els.append(bar(PAD_L, y, INNER_W, BAR_H, "#ede9e4", rx=3))
        els.append(bar(PAD_L, y, w1, BAR_H, GREEN, rx=3))
        els.append(text_el(PAD_L+w1+6, y+BAR_H/2, f"{d['composite']:.2f}", 11, GREEN, "700", dy=5))

        # gpa
        w2 = d["gpa"] / MAX_GPA * INNER_W
        y2 = y + BAR_H + GAP
        els.append(bar(PAD_L, y2, INNER_W, BAR_H, "#ede9e4", rx=3))
        els.append(bar(PAD_L, y2, w2, BAR_H, BLUE, rx=3))
        els.append(text_el(PAD_L+w2+6, y2+BAR_H/2, f"{d['gpa']:.2f}", 11, BLUE, "700", dy=5))

    els.append("</svg>")
    return "\n".join(els)

# ─── Chart: By Home Language ─────────────────
def chart_by_language():
    W = 480
    PAD_L, PAD_R, PAD_T, PAD_B = 100, 100, 20, 20
    INNER_W = W - PAD_L - PAD_R
    BAR_H = 28
    GAP   = 10
    MAX_V = 4.0
    lang_list = sorted(languages, key=lambda l: lang_data[l]["composite"], reverse=True)

    total_h = PAD_T + len(lang_list)*(BAR_H+GAP) + PAD_B + 20
    els = []
    els.append(f'<svg viewBox="0 0 {W} {total_h}" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:{W}px;font-family:\'DM Sans\',sans-serif">')
    els.append(f'<rect width="{W}" height="{total_h}" fill="{CHART_BG}"/>')

    for i, lang in enumerate(lang_list):
        d = lang_data[lang]
        y = PAD_T + i*(BAR_H+GAP)
        w = d["composite"] / MAX_V * INNER_W
        color = LANG_COLORS.get(lang, GREEN)
        els.append(bar(PAD_L, y, INNER_W, BAR_H, "#ede9e4", rx=4))
        els.append(bar(PAD_L, y, w, BAR_H, color, rx=4))
        els.append(text_el(PAD_L-8, y+BAR_H/2, lang, 12.5, "#3d3530", anchor="end", dy=5))
        els.append(text_el(PAD_L+w+8, y+BAR_H/2, f"{d['composite']:.2f}  (n={d['n']})", 11.5, color, "700", dy=5))

    els.append("</svg>")
    return "\n".join(els)

# ─── Chart: Attendance vs GPA scatter ────────
def chart_attendance():
    W, H = 480, 300
    PAD_L, PAD_R, PAD_T, PAD_B = 50, 20, 20, 50
    INNER_W = W - PAD_L - PAD_R
    INNER_H = H - PAD_T - PAD_B
    MAX_ABS = 16
    MAX_GPA = 4.0

    els = []
    els.append(f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:{W}px;font-family:\'DM Sans\',sans-serif">')
    els.append(f'<rect width="{W}" height="{H}" fill="{CHART_BG}"/>')

    # axes
    els.append(line_el(PAD_L, PAD_T, PAD_L, H-PAD_B, "#c9c5c0"))
    els.append(line_el(PAD_L, H-PAD_B, W-PAD_R, H-PAD_B, "#c9c5c0"))
    # labels
    els.append(text_el(W/2, H-6, "Days Absent", 12, NEUTRAL, anchor="middle"))
    els.append(text_el(12, H/2, "GPA", 12, NEUTRAL, anchor="middle"))

    # gridlines
    for g in [0, 1, 2, 3, 4]:
        y = H - PAD_B - (g / MAX_GPA) * INNER_H
        els.append(line_el(PAD_L-4, y, W-PAD_R, y, "#e2ddd8", 0.8, "3 3"))
        els.append(text_el(PAD_L-8, y, str(g), 10, NEUTRAL, anchor="end", dy=4))
    for a in [0, 4, 8, 12, 16]:
        x = PAD_L + (a / MAX_ABS) * INNER_W
        els.append(line_el(x, PAD_T, x, H-PAD_B+4, "#e2ddd8", 0.8, "3 3"))
        els.append(text_el(x, H-PAD_B+16, str(a), 10, NEUTRAL, anchor="middle"))

    # risk zone (abs >= 7, gpa < 2)
    rx = PAD_L + (7 / MAX_ABS) * INNER_W
    ry = H - PAD_B - (2 / MAX_GPA) * INNER_H
    els.append(f'<rect x="{rx:.1f}" y="{ry:.1f}" width="{W-PAD_R-rx:.1f}" height="{H-PAD_B-ry:.1f}" fill="{TERRACOTTA}" opacity="0.07"/>')
    els.append(text_el(rx+6, ry+14, "High-risk zone", 10, TERRACOTTA))

    for s in students:
        if s["absent"] is None or s["gpa"] is None:
            continue
        cx = PAD_L + (min(s["absent"], MAX_ABS) / MAX_ABS) * INNER_W
        cy = H - PAD_B - (min(s["gpa"], MAX_GPA) / MAX_GPA) * INNER_H
        color = TERRACOTTA if s["at_risk"] else (AMBER if s["ltel"] else GREEN)
        r_size = 6
        els.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r_size}" fill="{color}" opacity="0.85"/>')
        if s["at_risk"] or s["absent"] >= 7:
            initials = f"{s['first'][0]}{s['last'][0]}"
            els.append(text_el(cx+8, cy, initials, 9, color, anchor="start", dy=4))

    # legend
    ly = H - 14
    els.append(f'<circle cx="{PAD_L}" cy="{ly}" r="5" fill="{TERRACOTTA}"/>')
    els.append(text_el(PAD_L+10, ly, "At-risk", 10, NEUTRAL, dy=4))
    els.append(f'<circle cx="{PAD_L+70}" cy="{ly}" r="5" fill="{AMBER}"/>')
    els.append(text_el(PAD_L+82, ly, "LTEL", 10, NEUTRAL, dy=4))
    els.append(f'<circle cx="{PAD_L+120}" cy="{ly}" r="5" fill="{GREEN}"/>')
    els.append(text_el(PAD_L+132, ly, "Active EL", 10, NEUTRAL, dy=4))

    els.append("</svg>")
    return "\n".join(els)

# ─────────────────────────────────────────────
# 4. TABLE HELPERS
# ─────────────────────────────────────────────

def risk_badge(risks):
    if not risks:
        return ""
    badges = []
    for r in risks:
        color_map = {
            "Very Low ACCESS": "var(--terracotta)",
            "LTEL":            "var(--amber)",
            "Low GPA":         "var(--terracotta)",
            "Chronic Absence": "var(--terracotta)",
            "IEP":             "var(--blue)",
        }
        c = color_map.get(r, "var(--neutral)")
        badges.append(f'<span class="badge" style="background:{c}20;color:{c};border:1px solid {c}40">{r}</span>')
    return " ".join(badges)

def gpa_color(gpa):
    if gpa is None: return "var(--neutral)"
    if gpa >= 3.0: return "var(--green)"
    if gpa >= 2.0: return "var(--mid-green)"
    if gpa >= 1.0: return "var(--amber)"
    return "var(--terracotta)"

def composite_color(c):
    if c is None: return "var(--neutral)"
    if c >= 4.3: return "var(--green)"
    if c >= 3.0: return "var(--mid-green)"
    if c >= 2.0: return "var(--amber)"
    return "var(--terracotta)"

def pct_color(p):
    if p is None: return "var(--neutral)"
    if p >= 80: return "var(--green)"
    if p >= 70: return "var(--mid-green)"
    if p >= 60: return "var(--amber)"
    return "var(--terracotta)"

def absent_color(a):
    if a is None: return "var(--neutral)"
    if a >= 10: return "var(--terracotta)"
    if a >= 7:  return "var(--amber)"
    return "var(--neutral)"

def level_badge(lv):
    txt = str(lv).strip()
    if txt == "1": return f'<span class="lvl-badge lvl-1">L1</span>'
    if txt == "2": return f'<span class="lvl-badge lvl-2">L2</span>'
    if txt == "3": return f'<span class="lvl-badge lvl-3">L3</span>'
    if txt == "4": return f'<span class="lvl-badge lvl-4">L4</span>'
    return f'<span class="lvl-badge lvl-na">—</span>'

# ─────────────────────────────────────────────
# 5. GENERATE HTML
# ─────────────────────────────────────────────

# Pre-compute some inline values
weakest_modal = min([("Listening", avg_listen),("Speaking", avg_speak),("Reading", avg_read),("Writing", avg_write)], key=lambda x:x[1])
strongest_modal = max([("Listening", avg_listen),("Speaking", avg_speak),("Reading", avg_read),("Writing", avg_write)], key=lambda x:x[1])

# RISE science eligible students
sci_elig = [s for s in students if s["rise_eligible"] and s["sci_score"] is not None]
sci_met_n = sum(1 for s in sci_elig if s["sci_met"])
sci_pct_met = round(sci_met_n/len(sci_elig)*100) if sci_elig else 0

# Sort at-risk by number of risks
at_risk_sorted = sorted(students, key=lambda s: (-len(s["risks"]), -(s["absent"] or 0)))
at_risk_sorted = [s for s in at_risk_sorted if s["risks"]]

# All students for grades table, sorted by composite desc
all_sorted = sorted(students, key=lambda s: s["composite"] or 0, reverse=True)

# Best/worst schools
best_sch  = max(schools, key=lambda s: school_data[s]["composite"])
worst_sch = min(schools, key=lambda s: school_data[s]["composite"])

# Students with growth data sorted
top_growers  = sorted(growth_students, key=lambda s: s["growth"], reverse=True)[:3]
concern_students = [s for s in students if s["growth"] is not None and s["growth"] < 0.2]

def rows_at_risk():
    rows = []
    for s in at_risk_sorted[:12]:
        rec_map = {
            "Very Low ACCESS": "Intensive EL intervention; daily small-group pull-out",
            "LTEL":            "LTEL-specific redesignation plan; content literacy focus",
            "Low GPA":         "Academic support / tutoring coordination with classroom teacher",
            "Chronic Absence": "Family outreach, attendance team referral",
            "IEP":             "EL-SPED co-planning; coordinate push-in/pull-out support",
        }
        recs = list({rec_map[r] for r in s["risks"] if r in rec_map})
        rec_html = "<br>".join(f"• {r}" for r in recs[:2])
        rows.append(f"""
        <tr>
          <td><strong>{s['name']}</strong><br><small>{s['school'].replace(' Elementary','').replace(' Middle School',' MS')}</small></td>
          <td style="color:{composite_color(s['composite'])};font-weight:700">{s['composite']:.2f}</td>
          <td style="color:{gpa_color(s['gpa'])};font-weight:700">{s['gpa'] if s['gpa'] is not None else '—'}</td>
          <td style="color:{absent_color(s['absent'])};font-weight:700">{int(s['absent']) if s['absent'] is not None else '—'}</td>
          <td>{s['teacher'] or '—'}</td>
          <td>{risk_badge(s['risks'])}</td>
          <td class="rec-cell">{rec_html}</td>
        </tr>""")
    return "\n".join(rows)

def rows_all_students():
    rows = []
    for s in all_sorted:
        growth_html = ""
        if s["growth"] is not None:
            sign = "+" if s["growth"] >= 0 else ""
            col  = "#2d6a4f" if s["growth"] >= 0 else "#e76f51"
            growth_html = f'<span style="color:{col};font-weight:600">{sign}{s["growth"]:.2f}</span>'
        else:
            growth_html = '<span style="color:#a8a29e">New</span>'
        ltel_mark = '<span class="badge" style="background:#f4a26120;color:#c17b2e;border:1px solid #f4a26140">LTEL</span>' if s["ltel"] else ""
        rows.append(f"""
        <tr>
          <td><strong>{s['first']} {s['last']}</strong> {ltel_mark}<br><small style="color:var(--neutral)">{s['lang']} · Yr {s['years_el']}</small></td>
          <td><small>{s['school'].replace('Elementary','Elem').replace('Middle School','MS')}</small></td>
          <td style="color:{composite_color(s['composite'])};font-weight:700">{s['composite']:.2f}</td>
          <td>{growth_html}</td>
          <td>{level_badge(s['ela_level'])}</td>
          <td>{level_badge(s['math_level'])}</td>
          <td style="color:{gpa_color(s['gpa'])};font-weight:700">{s['gpa'] if s['gpa'] is not None else '—'}</td>
          <td style="color:{absent_color(s['absent'])};font-weight:700">{int(s['absent']) if s['absent'] is not None else '—'}</td>
        </tr>""")
    return "\n".join(rows)

def rows_reclass():
    rows = []
    for s in sorted(reclass_ready + reclass_approach, key=lambda x: x["composite"], reverse=True):
        ready = s["composite"] >= 4.5
        status_html = '<span class="badge" style="background:#2d6a4f20;color:#2d6a4f;border:1px solid #2d6a4f40">✓ Ready to evaluate</span>' if ready else \
                      '<span class="badge" style="background:#f4a26120;color:#c17b2e;border:1px solid #f4a26140">Approaching threshold</span>'
        rows.append(f"""
        <tr>
          <td><strong>{s['name']}</strong><br><small>{s['school'].replace('Elementary','Elem').replace('Middle School','MS')}</small></td>
          <td style="color:{composite_color(s['composite'])};font-weight:700;font-size:1.1em">{s['composite']:.2f}</td>
          <td>{int(s['prof_level']) if s['prof_level'] else '—'}</td>
          <td>{s['teacher'] or '—'}</td>
          <td>{status_html}</td>
          <td class="rec-cell">{'Submit for reclassification review; gather teacher input and academic evidence per R277-716' if ready else 'Monitor ACCESS score next cycle; begin pre-reclassification documentation'}</td>
        </tr>""")
    return "\n".join(rows)

def _school_rows_html():
    rows = []
    for sch in sorted(schools, key=lambda s: school_data[s]['composite'], reverse=True):
        d = school_data[sch]
        rows.append(
            f'<div style="padding:.5rem 0;border-bottom:1px solid var(--border);'
            f'display:grid;grid-template-columns:auto 1fr auto auto;gap:.5rem 1rem;align-items:center">'
            f'<strong style="font-size:.95em">{school_abbr.get(sch,sch)}</strong>'
            f'<span style="color:var(--neutral);font-size:.82rem">n={d["n"]} · {d["ltel"]} LTEL</span>'
            f'<span style="color:var(--green);font-weight:700">{d["composite"]:.2f}</span>'
            f'<span style="color:var(--blue);font-weight:700">GPA {d["gpa"]:.2f}</span>'
            f'</div>'
        )
    return "\n".join(rows)

def _subjects_met(s):
    parts = []
    if s["ela_met"]:  parts.append("ELA")
    if s["math_met"]: parts.append("Math")
    if s["sci_met"]:  parts.append("Science")
    return " &amp; ".join(parts) if parts else "none"

def _rise_standouts_html(sorted_list):
    items = [s for s in sorted_list if s["ela_met"] or s["math_met"] or s.get("sci_met")]
    return "".join(
        f'<div style="margin-bottom:.6rem;padding-bottom:.6rem;border-bottom:1px solid var(--border)">'
        f'<strong style="color:var(--green)">{s["name"]}</strong>'
        f' — met standard in {_subjects_met(s)}.'
        f' ACCESS composite: {s["composite"]:.2f}</div>'
        for s in items
    )

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ELL Program Analysis — Cedar Valley USD · Spring 2026</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap" rel="stylesheet">
<style>
:root {{
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
}}

*, *::before, *::after {{ box-sizing:border-box; margin:0; padding:0; }}

html {{ scroll-behavior:smooth; }}

body {{
  font-family: 'DM Sans', sans-serif;
  background: var(--bg);
  color: var(--text);
  font-size: 15px;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}}

/* ── HEADER ── */
.site-header {{
  background: var(--green);
  color: white;
  padding: 3.5rem 2rem 3rem;
  position: relative;
  overflow: hidden;
}}
.site-header::before {{
  content: "";
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 80% 60% at 110% 50%, #1b4332 0%, transparent 60%);
}}
.header-inner {{
  max-width: 1100px;
  margin: 0 auto;
  position: relative;
}}
.header-eyebrow {{
  font-size: .8rem;
  letter-spacing: .12em;
  text-transform: uppercase;
  opacity: .7;
  margin-bottom: .6rem;
}}
.header-title {{
  font-family: 'DM Serif Display', serif;
  font-size: clamp(2rem, 5vw, 3.2rem);
  font-weight: 400;
  line-height: 1.15;
  margin-bottom: .9rem;
}}
.header-sub {{
  opacity: .8;
  font-size: 1rem;
  max-width: 560px;
}}
.header-meta {{
  display: flex;
  gap: 2rem;
  margin-top: 2rem;
  flex-wrap: wrap;
}}
.header-stat {{
  display: flex;
  flex-direction: column;
}}
.header-stat-num {{
  font-family: 'DM Serif Display', serif;
  font-size: 2.2rem;
  line-height: 1;
}}
.header-stat-label {{
  font-size: .78rem;
  opacity: .7;
  text-transform: uppercase;
  letter-spacing: .08em;
  margin-top: .2rem;
}}

/* ── NAV ── */
/* ── SIDEBAR NAV ── */
.page-body {{
  display: grid;
  grid-template-columns: 11rem 1fr;
  max-width: 1280px;
  margin: 0 auto;
}}
.sidebar-nav {{
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  padding: 2.2rem .5rem 3rem 1.5rem;
  border-right: 1px solid var(--border);
  scrollbar-width: none;
}}
.sidebar-nav::-webkit-scrollbar {{ display: none; }}
.nav-label {{
  font-size: .6rem;
  letter-spacing: .1em;
  text-transform: uppercase;
  color: var(--neutral);
  padding: 0 .5rem .8rem;
  margin-bottom: .2rem;
  border-bottom: 1px solid var(--border);
}}
.nav-link {{
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
}}
.nav-link:hover {{
  color: var(--text);
  background: var(--bg2);
}}
.nav-link.active {{
  color: var(--green);
  background: #2d6a4f0c;
  font-weight: 600;
}}
.nav-num {{
  font-family: 'DM Serif Display', serif;
  font-size: .7rem;
  opacity: .5;
  min-width: 1.1rem;
  font-weight: 400;
}}
.nav-link.active .nav-num {{
  opacity: 1;
  color: var(--green);
}}

@media (max-width: 900px) {{
  .page-body {{
    grid-template-columns: 1fr;
  }}
  .sidebar-nav {{
    position: relative;
    height: auto;
    border-right: none;
    border-bottom: 1px solid var(--border);
    padding: 1rem 1.5rem;
    display: flex;
    flex-wrap: wrap;
    gap: .2rem .6rem;
  }}
  .nav-label {{
    width: 100%;
    border-bottom: none;
    padding-bottom: .4rem;
  }}
  .nav-num {{ display: none; }}
}}

/* ── MAIN ── */
.main-content {{
  max-width: 960px;
  padding: 3rem 2.5rem 6rem;
}}

/* ── SECTION ── */
.section {{
  margin-bottom: 4.5rem;
  opacity: 0;
  transform: translateY(24px);
  transition: opacity .5s ease, transform .5s ease;
}}
.section.visible {{
  opacity: 1;
  transform: none;
}}
.section-header {{
  display: flex;
  align-items: baseline;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding-bottom: .8rem;
  border-bottom: 1.5px solid var(--border);
}}
.section-num {{
  font-family: 'DM Serif Display', serif;
  font-size: 3rem;
  color: var(--border);
  line-height: 1;
  flex-shrink: 0;
}}
.section-title {{
  font-family: 'DM Serif Display', serif;
  font-size: 1.55rem;
  font-weight: 400;
  color: var(--text);
}}
.section-subtitle {{
  font-size: .88rem;
  color: var(--text2);
  margin-top: .15rem;
}}

/* ── INSIGHT CALLOUT ── */
.insight {{
  background: var(--bg2);
  border-left: 3.5px solid var(--green);
  padding: .9rem 1.2rem;
  border-radius: 0 6px 6px 0;
  font-size: .92rem;
  color: var(--text2);
  margin-bottom: 1.5rem;
  line-height: 1.5;
}}
.insight strong {{ color: var(--green); }}
.insight.warning {{
  border-left-color: var(--terracotta);
}}
.insight.warning strong {{ color: var(--terracotta); }}

/* ── KPI GRID ── */
.kpi-grid {{
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}}
@media (max-width: 800px) {{
  .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
}}
.kpi-card {{
  background: white;
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1.25rem 1.4rem;
  display: flex;
  flex-direction: column;
  gap: .3rem;
  box-shadow: var(--shadow);
}}
.kpi-card.accent {{
  background: var(--green);
  color: white;
  border-color: var(--green);
}}
.kpi-card.warning {{
  background: #fff7f5;
  border-color: #f5c7bd;
}}
.kpi-label {{
  font-size: .75rem;
  text-transform: uppercase;
  letter-spacing: .07em;
  color: var(--neutral);
}}
.kpi-card.accent .kpi-label {{ color: rgba(255,255,255,.65); }}
.kpi-value {{
  font-family: 'DM Serif Display', serif;
  font-size: 2.4rem;
  line-height: 1;
  color: var(--text);
}}
.kpi-card.accent .kpi-value {{ color: white; }}
.kpi-card.warning .kpi-value {{ color: var(--terracotta); }}
.kpi-delta {{
  font-size: .8rem;
  color: var(--neutral);
}}
.kpi-delta.pos {{ color: var(--mid-green); }}
.kpi-delta.neg {{ color: var(--terracotta); }}

/* ── TWO COLUMN ── */
.two-col {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2.5rem;
  align-items: start;
}}
@media (max-width: 700px) {{
  .two-col {{ grid-template-columns: 1fr; }}
}}

/* ── TABLES ── */
.table-wrap {{
  overflow-x: auto;
  border-radius: 10px;
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
}}
table {{
  width: 100%;
  border-collapse: collapse;
  font-size: .88rem;
  background: white;
}}
thead tr {{
  background: var(--bg2);
  border-bottom: 2px solid var(--border);
}}
th {{
  padding: .65rem 1rem;
  text-align: left;
  font-size: .75rem;
  letter-spacing: .06em;
  text-transform: uppercase;
  color: var(--text2);
  font-weight: 600;
  white-space: nowrap;
}}
td {{
  padding: .7rem 1rem;
  border-bottom: 1px solid var(--border);
  vertical-align: top;
}}
tr:last-child td {{ border-bottom: none; }}
tr:hover td {{ background: #faf7f3; }}
.rec-cell {{
  font-size: .82rem;
  color: var(--text2);
  min-width: 200px;
  line-height: 1.45;
}}

/* ── BADGES ── */
.badge {{
  display: inline-block;
  padding: .15em .55em;
  border-radius: 4px;
  font-size: .75rem;
  font-weight: 600;
  white-space: nowrap;
  margin: 1px;
}}
.lvl-badge {{
  display: inline-block;
  width: 28px;
  height: 22px;
  border-radius: 4px;
  font-size: .75rem;
  font-weight: 700;
  text-align: center;
  line-height: 22px;
}}
.lvl-1 {{ background:#fde8e3; color:#c0392b; }}
.lvl-2 {{ background:#fef3e2; color:#c17b2e; }}
.lvl-3 {{ background:#e6f4ed; color:#2d6a4f; }}
.lvl-4 {{ background:#d4eddf; color:#1b4332; }}
.lvl-na {{ background:#f0ede9; color:#a8a29e; }}

/* ── CHART WRAPPER ── */
.chart-wrap {{
  background: white;
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1.4rem 1.2rem 1rem;
  box-shadow: var(--shadow);
  overflow: hidden;
}}
.chart-title {{
  font-size: .8rem;
  text-transform: uppercase;
  letter-spacing: .08em;
  color: var(--neutral);
  margin-bottom: 1rem;
}}

/* ── FOOTER ── */
.site-footer {{
  border-top: 1px solid var(--border);
  padding: 2rem;
  text-align: center;
  font-size: .8rem;
  color: var(--neutral);
}}
</style>
</head>
<body>

<!-- ══════════════════════════════════════════
     HEADER
══════════════════════════════════════════ -->
<header class="site-header">
  <div class="header-inner">
    <p class="header-eyebrow">Cedar Valley Unified School District · EL Program</p>
    <h1 class="header-title">English Language Learner<br>Program Analysis</h1>
    <p class="header-sub">A comprehensive review of ACCESS proficiency, RISE state assessments, and classroom performance for the 2025–26 cohort — with actionable recommendations.</p>
    <div class="header-meta">
      <div class="header-stat">
        <span class="header-stat-num">{n_total}</span>
        <span class="header-stat-label">Active EL Students</span>
      </div>
      <div class="header-stat">
        <span class="header-stat-num">4</span>
        <span class="header-stat-label">Schools</span>
      </div>
      <div class="header-stat">
        <span class="header-stat-num">5</span>
        <span class="header-stat-label">Home Languages</span>
      </div>
      <div class="header-stat">
        <span class="header-stat-num">Spring 2026</span>
        <span class="header-stat-label">Report Period</span>
      </div>
    </div>
  </div>
</header>

<!-- ══════════════════════════════════════════
     STICKY NAV
══════════════════════════════════════════ -->
<!-- ══════════════════════════════════════════
     PAGE BODY (sidebar + main)
══════════════════════════════════════════ -->
<div class="page-body">

<nav class="sidebar-nav" aria-label="Report sections">
  <p class="nav-label">Sections</p>
  <a class="nav-link active" href="#s1"><span class="nav-num">01</span> Overview</a>
  <a class="nav-link" href="#s2"><span class="nav-num">02</span> ACCESS Growth</a>
  <a class="nav-link" href="#s3"><span class="nav-num">03</span> Modalities</a>
  <a class="nav-link" href="#s4"><span class="nav-num">04</span> LTEL Analysis</a>
  <a class="nav-link" href="#s5"><span class="nav-num">05</span> RISE Results</a>
  <a class="nav-link" href="#s6"><span class="nav-num">06</span> Schools</a>
  <a class="nav-link" href="#s7"><span class="nav-num">07</span> Language</a>
  <a class="nav-link" href="#s8"><span class="nav-num">08</span> Attendance</a>
  <a class="nav-link" href="#s9"><span class="nav-num">09</span> At-Risk</a>
  <a class="nav-link" href="#s10"><span class="nav-num">10</span> Reclass</a>
  <a class="nav-link" href="#s11"><span class="nav-num">11</span> Roster</a>
</nav>

<main class="main-content">

<!-- ── Section 1: Executive Summary ── -->
<section class="section" id="s1">
  <div class="section-header">
    <span class="section-num">01</span>
    <div>
      <h2 class="section-title">Executive Summary</h2>
      <p class="section-subtitle">Key performance indicators across all data sources</p>
    </div>
  </div>

  <div class="kpi-grid">
    <div class="kpi-card accent">
      <span class="kpi-label">Avg ACCESS Composite</span>
      <span class="kpi-value">{avg_composite}</span>
      <span class="kpi-delta pos">Proficiency Level 3 cohort average</span>
    </div>
    <div class="kpi-card">
      <span class="kpi-label">Avg YoY Growth</span>
      <span class="kpi-value" style="color:var(--green)">+{avg_growth}</span>
      <span class="kpi-delta pos">{n_improved} of {len(growths)} returning students improved</span>
    </div>
    <div class="kpi-card">
      <span class="kpi-label">LTEL Students</span>
      <span class="kpi-value" style="color:var(--amber)">{n_ltel}</span>
      <span class="kpi-delta">{round(n_ltel/n_total*100)}% of cohort · 5+ years in EL</span>
    </div>
    <div class="kpi-card warning">
      <span class="kpi-label">At-Risk Students</span>
      <span class="kpi-value">{len(at_risk_students)}</span>
      <span class="kpi-delta neg">2+ simultaneous risk factors</span>
    </div>
  </div>

  <div class="kpi-grid">
    <div class="kpi-card">
      <span class="kpi-label">RISE ELA Met Standard</span>
      <span class="kpi-value" style="color:{'var(--mid-green)' if ela_pct_met >= 25 else 'var(--terracotta)'}">{ela_pct_met}%</span>
      <span class="kpi-delta">{ela_met_n} of {len(rise_elig)} RISE-eligible students</span>
    </div>
    <div class="kpi-card">
      <span class="kpi-label">RISE Math Met Standard</span>
      <span class="kpi-value" style="color:{'var(--mid-green)' if math_pct_met >= 25 else 'var(--amber)'}">{math_pct_met}%</span>
      <span class="kpi-delta">{math_met_n} of {len(rise_elig)} RISE-eligible students</span>
    </div>
    <div class="kpi-card">
      <span class="kpi-label">Average Cohort GPA</span>
      <span class="kpi-value" style="color:var(--mid-green)">{avg_gpa}</span>
      <span class="kpi-delta">On 4.0 scale · current semester</span>
    </div>
    <div class="kpi-card">
      <span class="kpi-label">Reclassification Ready</span>
      <span class="kpi-value" style="color:var(--green)">{len(reclass_ready)}</span>
      <span class="kpi-delta">ACCESS composite ≥ 4.5 · +{len(reclass_approach)} approaching</span>
    </div>
  </div>

  <div class="insight">
    <strong>Key takeaway:</strong> All {len(growths)} returning students showed positive ACCESS growth averaging <strong>+{avg_growth} points</strong>, indicating program-wide momentum. However, critical gaps remain: only <strong>{ela_pct_met}% of RISE-eligible students meet ELA standard</strong> and <strong>{len(at_risk_students)} students carry multiple simultaneous risk factors</strong> requiring immediate intervention.
  </div>
</section>

<!-- ── Section 2: ACCESS YoY Growth ── -->
<section class="section" id="s2">
  <div class="section-header">
    <span class="section-num">02</span>
    <div>
      <h2 class="section-title">ACCESS Proficiency Growth</h2>
      <p class="section-subtitle">Year-over-year composite score change · 2024-25 → 2025-26 · sorted by growth</p>
    </div>
  </div>
  <div class="insight">
    <strong>Every returning student grew</strong> — {n_improved} of {len(growths)} students with prior-year data improved their composite score. Top performers:
    {''.join(f" <strong>{s['name']}</strong> (+{s['growth']:.2f}){',' if i < len(top_growers)-1 else '.'}" for i, s in enumerate(top_growers))}
    Five Year-1 newcomers (Amina Hassan, Omar Mohamed, Yusuf Ahmed, Aisha Nasser) have baseline scores this year only.
  </div>
  <div class="chart-wrap">
    <p class="chart-title">Composite Score — Prior Year (hollow) vs Current Year (filled) · sorted by growth</p>
    {chart_yoy_growth()}
  </div>
</section>

<!-- ── Section 3: Modality Breakdown ── -->
<section class="section" id="s3">
  <div class="section-header">
    <span class="section-num">03</span>
    <div>
      <h2 class="section-title">Language Domain Analysis</h2>
      <p class="section-subtitle">Average 2025-26 ACCESS scores by skill domain · cohort-wide</p>
    </div>
  </div>
  <div class="two-col">
    <div>
      <div class="insight {'warning' if weakest_modal[1] < 2.5 else ''}">
        <strong>{weakest_modal[0]} is the weakest domain</strong> at an average of <strong>{weakest_modal[1]:.2f}</strong>, compared to the strongest domain ({strongest_modal[0]}: {strongest_modal[1]:.2f}).
        The Listening–Writing gap of <strong>{avg_listen - avg_write:.2f} points</strong> signals students understand English better than they can produce written text — a common pattern suggesting the program should prioritize <strong>structured writing practice</strong> across all grade levels.
      </div>
      <div class="insight">
        <strong>Action:</strong> Target explicit writing instruction — sentence frames, paragraph organization, and academic vocabulary — especially for LTEL and mid-level students (composite 2.5–3.5).
      </div>
    </div>
    <div class="chart-wrap">
      <p class="chart-title">Average Domain Score · All Students · 2025-26 · (max 6.0 scale, displayed to 4.0)</p>
      {chart_modalities()}
    </div>
  </div>
</section>

<!-- ── Section 4: LTEL Comparison ── -->
<section class="section" id="s4">
  <div class="section-header">
    <span class="section-num">04</span>
    <div>
      <h2 class="section-title">LTEL vs Active EL Performance</h2>
      <p class="section-subtitle">Long-term EL students (5+ years) compared to general cohort</p>
    </div>
  </div>
  <div class="two-col">
    <div class="chart-wrap">
      <p class="chart-title">Avg ACCESS Composite · Avg GPA · ELA % Met Standard</p>
      {chart_ltel_comparison()}
    </div>
    <div>
      <div class="insight warning">
        <strong>LTEL students are significantly underperforming</strong> across all metrics. Their avg composite is <strong>{ltel_composite:.2f}</strong> vs <strong>{nonltel_composite:.2f}</strong> for the broader cohort, and their avg GPA is <strong>{ltel_gpa:.2f}</strong> vs <strong>{nonltel_gpa:.2f}</strong>. Not one LTEL student met the ELA standard on RISE.
      </div>
      <div class="insight">
        <strong>Recommendations for LTEL students:</strong><br>
        • Develop individualized LTEL redesignation plans with annual benchmarks<br>
        • Shift instruction toward <em>content-area academic language</em>, not basic conversational EL support<br>
        • Prioritize oral reading fluency and academic writing — the domains where LTEL students most lag<br>
        • Involve families in goal-setting meetings; chronic absence (common in this group) is a compounding factor
      </div>
      <div style="margin-top:1rem;padding:1rem;background:white;border:1px solid var(--border);border-radius:8px;font-size:.88rem;">
        <strong style="display:block;margin-bottom:.5rem;color:var(--text2);font-size:.75rem;text-transform:uppercase;letter-spacing:.07em">LTEL Student Detail</strong>
        {''.join(f'<div style="padding:.35rem 0;border-bottom:1px solid var(--border);display:flex;justify-content:space-between"><span>{s["name"]}</span><span style="color:var(--neutral);font-size:.85rem">Yr {s["years_el"]} · Composite {s["composite"]:.2f} · GPA {s["gpa"] if s["gpa"] is not None else "—"}</span></div>' for s in ltel_s)}
      </div>
    </div>
  </div>
</section>

<!-- ── Section 5: RISE ── -->
<section class="section" id="s5">
  <div class="section-header">
    <span class="section-num">05</span>
    <div>
      <h2 class="section-title">RISE State Assessment Results</h2>
      <p class="section-subtitle">Spring 2025 · ELA, Math &amp; Science performance levels for all 23 students</p>
    </div>
  </div>
  <div class="insight warning">
    <strong>ELA proficiency is the most urgent gap.</strong> Only <strong>{ela_pct_met}%</strong> of RISE-eligible students met the ELA standard — compared to <strong>{math_pct_met}%</strong> in Math and <strong>{sci_pct_met}%</strong> in Science. The majority of tested students score at Level 2 (Approaching), suggesting they are <em>close to the threshold</em> but not yet crossing it. 6 students in grades 1–2 are not yet RISE-eligible.
  </div>
  <div class="two-col">
    <div class="chart-wrap">
      <p class="chart-title">Performance level distribution across all 23 students · N/A = not yet RISE-eligible grade</p>
      {chart_rise()}
    </div>
    <div>
      <div style="background:white;border:1px solid var(--border);border-radius:8px;padding:1.1rem;font-size:.88rem;box-shadow:var(--shadow)">
        <strong style="display:block;margin-bottom:.8rem;color:var(--text2);font-size:.75rem;text-transform:uppercase;letter-spacing:.07em">RISE Standouts</strong>
        {_rise_standouts_html(all_sorted)}
        <strong style="display:block;margin-top:.8rem;margin-bottom:.6rem;color:var(--text2);font-size:.75rem;text-transform:uppercase;letter-spacing:.07em">Priority for ELA intervention</strong>
        {''.join(f'<div style="margin-bottom:.4rem"><span style="color:var(--terracotta);font-weight:600">{s["name"]}</span> <span style="color:var(--neutral);font-size:.82rem">ELA L{s["ela_level"]} · Scale {int(s["ela_score"])}</span></div>' for s in sorted(rise_elig, key=lambda x: x["ela_score"] or 999) if s["ela_level"] == "1")}
      </div>
    </div>
  </div>
</section>

<!-- ── Section 6: By School ── -->
<section class="section" id="s6">
  <div class="section-header">
    <span class="section-num">06</span>
    <div>
      <h2 class="section-title">Performance by School</h2>
      <p class="section-subtitle">Average ACCESS composite and GPA across all four sites</p>
    </div>
  </div>
  <div class="two-col">
    <div class="chart-wrap">
      <p class="chart-title">Avg ACCESS Composite (green) · Avg GPA (blue) · sorted by composite</p>
      {chart_by_school()}
    </div>
    <div>
      <div class="insight">
        <strong>{school_abbr.get(best_sch, best_sch)}</strong> leads on ACCESS composite ({school_data[best_sch]['composite']:.2f}) and is home to the program's strongest performers. <strong>{school_abbr.get(worst_sch, worst_sch)}</strong> has the lowest avg composite ({school_data[worst_sch]['composite']:.2f}) and serves the highest concentration of newcomer students — context that should frame support prioritization.
      </div>
      <div style="background:white;border:1px solid var(--border);border-radius:8px;padding:1rem;font-size:.88rem;box-shadow:var(--shadow)">
        {_school_rows_html()}
      </div>
      <div class="insight" style="margin-top:1rem">
        <strong>Action:</strong> Facilitate cross-site teacher collaboration — have {school_abbr.get(best_sch)} staff share instructional strategies with {school_abbr.get(worst_sch)} counterparts, particularly around academic language scaffolding for newcomers.
      </div>
    </div>
  </div>
</section>

<!-- ── Section 7: By Language ── -->
<section class="section" id="s7">
  <div class="section-header">
    <span class="section-num">07</span>
    <div>
      <h2 class="section-title">Home Language Breakdown</h2>
      <p class="section-subtitle">ACCESS composite by primary home language · n shown per group</p>
    </div>
  </div>
  <div class="two-col">
    <div>
      <div class="insight warning">
        <strong>Somali-speaking students have the lowest avg composite ({lang_data['Somali']['composite']:.2f})</strong> — reflecting that the three Somali-speaking newcomers (Amina Hassan, Omar Mohamed, Yusuf Ahmed) are in their first year. Their Year-1 baseline scores pull the group average down sharply. This is expected for new arrivals, but warrants careful monitoring in Year 2.
      </div>
      <div class="insight">
        <strong>Arabic-speaking students lead the cohort</strong> at {lang_data['Arabic']['composite']:.2f} avg composite — driven by Layla Khalil's exceptional score of 4.5. Portuguese (Ana Silva, n=1) and Spanish speakers also perform solidly. The program should investigate whether any language groups have access barriers to supplemental support resources.
      </div>
    </div>
    <div class="chart-wrap">
      <p class="chart-title">Avg ACCESS Composite 2025-26 · sorted by performance</p>
      {chart_by_language()}
    </div>
  </div>
</section>

<!-- ── Section 8: Attendance ── -->
<section class="section" id="s8">
  <div class="section-header">
    <span class="section-num">08</span>
    <div>
      <h2 class="section-title">Attendance &amp; Academic Risk</h2>
      <p class="section-subtitle">Days absent vs GPA — current semester · shaded zone = high-risk</p>
    </div>
  </div>
  <div class="two-col">
    <div class="chart-wrap">
      <p class="chart-title">Each dot = one student · initials shown for highest-absence students</p>
      {chart_attendance()}
    </div>
    <div>
      <div class="insight warning">
        <strong>Chronic absenteeism is concentrated in the lowest-performing students.</strong> Tala Latu has <strong>14 absences</strong> this semester — chronic by any definition — with a GPA of 1.0. Omar Mohamed (11 absences, GPA 0.0) and Yusuf Ahmed (9 absences, GPA 0.0) are in crisis territory. These students need family outreach <em>now</em>, not at semester end.
      </div>
      <div style="background:white;border:1px solid var(--border);border-radius:8px;padding:1rem;font-size:.88rem;box-shadow:var(--shadow)">
        <strong style="display:block;margin-bottom:.6rem;color:var(--text2);font-size:.75rem;text-transform:uppercase;letter-spacing:.07em">Students with 5+ Absences</strong>
        {''.join(f'<div style="padding:.35rem 0;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center"><span><strong>{s["name"]}</strong></span><span><span style="color:{"var(--terracotta)" if (s["absent"] or 0)>=10 else "var(--amber)"};font-weight:700">{int(s["absent"])} days</span> &nbsp; <span style="color:{gpa_color(s["gpa"])}">GPA {s["gpa"] if s["gpa"] is not None else "—"}</span></span></div>' for s in sorted(students, key=lambda x: x["absent"] or 0, reverse=True) if (s["absent"] or 0) >= 5)}
      </div>
    </div>
  </div>
</section>

<!-- ── Section 9: At-Risk Watch List ── -->
<section class="section" id="s9">
  <div class="section-header">
    <span class="section-num">09</span>
    <div>
      <h2 class="section-title">At-Risk Student Watch List</h2>
      <p class="section-subtitle">Students with one or more active risk factors · sorted by severity · with recommended actions</p>
    </div>
  </div>
  <div class="insight warning">
    <strong>{len([s for s in students if len(s['risks'])>=2])} students carry 2 or more simultaneous risk factors.</strong> Immediate coordination between EL teachers, classroom teachers, counselors, and families is needed. Use this table as the foundation for your next Student Support Team (SST) agenda.
  </div>
  <div class="table-wrap">
    <table>
      <thead><tr>
        <th>Student</th>
        <th>ACCESS</th>
        <th>GPA</th>
        <th>Absent</th>
        <th>EL Teacher</th>
        <th>Risk Flags</th>
        <th>Recommended Actions</th>
      </tr></thead>
      <tbody>
        {rows_at_risk()}
      </tbody>
    </table>
  </div>
</section>

<!-- ── Section 10: Reclassification ── -->
<section class="section" id="s10">
  <div class="section-header">
    <span class="section-num">10</span>
    <div>
      <h2 class="section-title">Reclassification Readiness</h2>
      <p class="section-subtitle">Students at or approaching Utah EL exit threshold (ACCESS composite ≥ 4.5 + academic criteria, per R277-716)</p>
    </div>
  </div>
  <div class="insight">
    <strong>Layla Khalil has reached the ACCESS composite exit threshold</strong> at 4.5. Per Utah rule R277-716, reclassification also requires academic performance evidence and teacher input. Two additional students (Rosa Hernandez at 4.4, Maria Rodriguez at 4.175) are approaching threshold and may be ready next cycle if growth continues.
  </div>
  <div class="table-wrap">
    <table>
      <thead><tr>
        <th>Student</th>
        <th>Composite</th>
        <th>Prof. Level</th>
        <th>EL Teacher</th>
        <th>Status</th>
        <th>Next Steps</th>
      </tr></thead>
      <tbody>
        {rows_reclass()}
      </tbody>
    </table>
  </div>
</section>

<!-- ── Section 11: Full Roster ── -->
<section class="section" id="s11">
  <div class="section-header">
    <span class="section-num">11</span>
    <div>
      <h2 class="section-title">Full Student Roster</h2>
      <p class="section-subtitle">All {n_total} students · ACCESS composite · YoY growth · RISE performance levels · GPA · sorted by composite score</p>
    </div>
  </div>
  <div class="table-wrap">
    <table>
      <thead><tr>
        <th>Student</th>
        <th>School</th>
        <th>Composite</th>
        <th>Growth</th>
        <th>ELA</th>
        <th>Math</th>
        <th>GPA</th>
        <th>Absent</th>
      </tr></thead>
      <tbody>
        {rows_all_students()}
      </tbody>
    </table>
  </div>
</section>

<footer class="site-footer">
  <p>Cedar Valley Unified School District · EL Program · Generated April 2, 2026</p>
  <p style="margin-top:.4rem">Data sources: WIDA ACCESS Spring 2026 · RISE Spring 2025 · SIS 2025-26 · ACCESS PY2024-25</p>
</footer>

</main>
</div><!-- .page-body -->

<script>
// Intersection Observer for section fade-in
const io = new IntersectionObserver((entries) => {{
  entries.forEach(e => {{
    if (e.isIntersecting) {{ e.target.classList.add('visible'); }}
  }});
}}, {{ threshold: 0.05 }});
document.querySelectorAll('.section').forEach(s => io.observe(s));

// Activate first section immediately
document.querySelectorAll('.section')[0]?.classList.add('visible');

// Nav highlighting
const sections = document.querySelectorAll('.section[id]');
const navLinks  = document.querySelectorAll('.nav-link');
const ioNav = new IntersectionObserver((entries) => {{
  entries.forEach(e => {{
    if (e.isIntersecting) {{
      navLinks.forEach(l => l.classList.remove('active'));
      const link = document.querySelector(`.nav-link[href="#${{e.target.id}}"]`);
      if (link) link.classList.add('active');
    }}
  }});
}}, {{ threshold: 0.3 }});
sections.forEach(s => ioNav.observe(s));
</script>
</body>
</html>"""

OUT.write_text(HTML, encoding="utf-8")
print(f"Report written → {OUT}")
print(f"  Students: {n_total}  |  Avg composite: {avg_composite}  |  Avg growth: +{avg_growth}")
print(f"  At-risk: {len(at_risk_students)}  |  LTEL: {n_ltel}  |  Reclassification ready: {len(reclass_ready)}")
