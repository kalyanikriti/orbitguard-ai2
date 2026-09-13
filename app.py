import itertools
import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from skyfield.api import EarthSatellite, load


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: "Space Grotesk", sans-serif;
}
.stApp {
    background:
      radial-gradient(circle at 15% 10%, rgba(0,220,255,.12), transparent 28%),
      radial-gradient(circle at 85% 20%, rgba(140,80,255,.12), transparent 30%),
      linear-gradient(180deg, #030712 0%, #07111f 55%, #02040a 100%);
}
[data-testid="stHeader"] { background: rgba(0,0,0,0); }
.block-container { position: relative; z-index: 2; padding-top: 2rem; }
.hero {
    border: 1px solid rgba(0,220,255,.25);
    border-radius: 24px;
    padding: 28px;
    background: linear-gradient(135deg, rgba(7,18,34,.95), rgba(15,8,32,.92));
    box-shadow: 0 0 45px rgba(0,220,255,.08);
    margin-bottom: 18px;
}
.hero h1 {
    font-family: Orbitron, sans-serif;
    letter-spacing: 2px;
    margin: 0;
    font-size: clamp(28px, 4vw, 48px);
}
.hero p { color: #a9bfd4; font-size: 16px; }
.card {
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 18px;
    padding: 18px;
    background: rgba(9,17,31,.86);
    box-shadow: 0 10px 35px rgba(0,0,0,.22);
}
.kpi { font-size: 28px; font-weight: 800; margin-top: 6px; }
.label { color: #8ca3b8; font-size: 12px; text-transform: uppercase; letter-spacing: 1.2px; }
.alert {
    border: 1px solid rgba(255,80,110,.5);
    border-radius: 18px;
    padding: 16px 18px;
    background: linear-gradient(90deg, rgba(255,40,80,.14), rgba(255,40,80,.04));
}
.small { color:#91a6ba; font-size:13px; }
</style>
""", unsafe_allow_html=True)


def build_mission_report_pdf(report_data: dict) -> bytes:
    """Build a dependency-light professional mission safety PDF."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4, rightMargin=16*mm, leftMargin=16*mm,
        topMargin=15*mm, bottomMargin=15*mm
    )
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "MissionTitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=20, leading=24, alignment=TA_CENTER, spaceAfter=8
    )
    sub = ParagraphStyle(
        "Sub", parent=styles["Normal"], fontSize=9, textColor=colors.HexColor("#52606d"),
        alignment=TA_CENTER, spaceAfter=16
    )
    h2 = ParagraphStyle(
        "H2", parent=styles["Heading2"], fontSize=12, leading=15,
        textColor=colors.HexColor("#16324f"), spaceBefore=10, spaceAfter=6
    )
    body = ParagraphStyle("Body2", parent=styles["BodyText"], fontSize=9, leading=13)
    story = [
        Paragraph("ORBITGUARD — MISSION SAFETY REPORT", title),
        Paragraph(
            "Space-debris conjunction screening • generated " +
            str(report_data.get("generated_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),
            sub
        ),
        Paragraph("Executive Summary", h2),
        Paragraph(str(report_data.get("summary", "Conjunction analysis completed.")), body),
        Spacer(1, 6),
    ]

    rows = [
        ["Field", "Assessment"],
        ["Primary object", str(report_data.get("primary", "—"))],
        ["Secondary object", str(report_data.get("secondary", "—"))],
        ["Risk level", str(report_data.get("risk_level", "—"))],
        ["Risk score", str(report_data.get("risk_score", "—"))],
        ["Minimum separation", str(report_data.get("min_distance", "—"))],
        ["Relative velocity", str(report_data.get("relative_velocity", "—"))],
        ["TCA / closest approach", str(report_data.get("tca", "—"))],
        ["Orbit classification", str(report_data.get("orbit_class", "—"))],
        ["Multi-object validation", str(report_data.get("validation", "—"))],
    ]
    tbl = Table(rows, colWidths=[55*mm, 115*mm], repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#16324f")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME", (0,1), (0,-1), "Helvetica-Bold"),
        ("GRID", (0,0), (-1,-1), .35, colors.HexColor("#cbd5df")),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("FONTSIZE", (0,0), (-1,-1), 8.5),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f5f8fb")]),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story += [tbl, Paragraph("AI Maneuver Recommendation", h2),
              Paragraph(str(report_data.get("maneuver", "No maneuver recommendation available.")), body),
              Paragraph("Explainability & Method", h2),
              Paragraph(str(report_data.get("method", "Risk is a screening heuristic based on separation and relative-motion indicators.")), body),
              Paragraph("Safety Note", h2),
              Paragraph(
                  "This prototype is a decision-support/screening system, not a certified operational "
                  "collision-avoidance system. Real missions require authoritative ephemerides, covariance "
                  "and uncertainty propagation, validated force models, conjunction data, operational "
                  "constraints, and human/operator approval.",
                  body
              )]
    doc.build(story)
    return buf.getvalue()

st.set_page_config(page_title="ORBITGUARD | Collision Avoidance", page_icon="🛰️", layout="wide", initial_sidebar_state="collapsed")

# -----------------------------
# Visual system
# -----------------------------
st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root{--bg:#030712;--panel:rgba(8,16,31,.78);--line:rgba(105,150,210,.20);--cyan:#42e8ff;--blue:#4b8cff;--violet:#9b6cff;--green:#42f59b;--red:#ff5268;--amber:#ffb84d;--text:#eaf3ff;--muted:#8294ad}
html,body,[class*="css"]{font-family:'Space Grotesk',sans-serif}.stApp{background:radial-gradient(circle at 50% -15%,#132b50 0,#071120 30%,#030712 68%);color:var(--text)}
.block-container{max-width:1450px;padding:1.3rem 2.5rem 4rem;position:relative;z-index:2}
.stApp:before,.stApp:after{content:"";position:fixed;inset:0;pointer-events:none;z-index:0}.stApp:before{opacity:.55;background-image:radial-gradient(circle,#fff 0.7px,transparent .9px);background-size:97px 113px;animation:stars 24s linear infinite}.stApp:after{opacity:.25;background-image:radial-gradient(circle,#54dfff 1px,transparent 1.6px);background-size:181px 151px;animation:stars 38s linear infinite reverse}@keyframes stars{to{transform:translate3d(80px,120px,0)}}
.hero{padding:1.3rem 0 .8rem}.eyebrow{font:700 .75rem 'Orbitron';letter-spacing:.25em;color:var(--cyan);text-transform:uppercase}.hero h1{font:800 2.8rem 'Orbitron';letter-spacing:.02em;margin:.3rem 0;background:linear-gradient(90deg,#fff,#79eaff,#9d8cff);-webkit-background-clip:text;color:transparent}.hero p{max-width:850px;color:#91a5bf;font-size:1rem;margin:0}
.topbar,.panel,.metric,.alert,.telemetry,.mission{background:linear-gradient(145deg,rgba(12,25,45,.86),rgba(5,11,23,.76));border:1px solid var(--line);box-shadow:0 15px 45px rgba(0,0,0,.25),inset 0 1px rgba(255,255,255,.04);backdrop-filter:blur(14px);border-radius:18px}
.topbar{display:flex;justify-content:space-between;align-items:center;padding:.7rem 1rem;margin:.2rem 0 1.1rem}.online{color:var(--green);font-weight:700}.online span{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--green);box-shadow:0 0 14px var(--green);margin-right:7px;animation:pulse 1.4s infinite}@keyframes pulse{50%{opacity:.35;transform:scale(.75)}}
.metric{padding:1rem 1.15rem;min-height:105px}.metric .label{color:#71859e;text-transform:uppercase;font-size:.66rem;letter-spacing:.13em}.metric .value{font:700 1.8rem 'Orbitron';margin-top:.35rem}.cyan{color:var(--cyan)}.red{color:var(--red)}.green{color:var(--green)}.amber{color:var(--amber)}
.section{font:700 1rem 'Orbitron';letter-spacing:.08em;margin:1.5rem 0 .7rem}.sub{color:#71859e;font-size:.8rem;margin-bottom:.8rem}
.alert{padding:1rem 1.25rem;border-color:rgba(255,82,104,.45);background:linear-gradient(110deg,rgba(90,13,32,.65),rgba(22,10,25,.76));position:relative;overflow:hidden}.alert:before{content:"";position:absolute;inset:0;background:linear-gradient(90deg,transparent,rgba(255,82,104,.12),transparent);animation:sweep 2.8s infinite}@keyframes sweep{from{transform:translateX(-100%)}to{transform:translateX(100%)}}.alert-title{font:700 .85rem 'Orbitron';color:#ff7081;letter-spacing:.12em}.alert-main{font:700 1.25rem 'Space Grotesk';margin:.3rem 0}.alert-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:.7rem}.alert-grid b{font:700 1.05rem 'Orbitron'}.mini{color:#8d7d8a;font-size:.64rem;text-transform:uppercase;letter-spacing:.1em}
.mission{padding:1rem 1.2rem}.mission-row{display:flex;justify-content:space-between;color:#8da0b8;font-size:.78rem}.bar{height:9px;background:#0b1628;border-radius:20px;overflow:hidden;margin:.65rem 0 1rem}.fill{height:100%;background:linear-gradient(90deg,#ff5268,#ffb84d,#42f59b);border-radius:20px;box-shadow:0 0 16px rgba(66,232,255,.4)}
.telemetry{padding:1rem}.telemetry-grid{display:grid;grid-template-columns:1fr 1fr;gap:.7rem}.telemetry-cell{border:1px solid rgba(105,150,210,.13);background:rgba(3,10,21,.55);border-radius:12px;padding:.75rem}.telemetry-cell small{color:#647891;text-transform:uppercase;font-size:.6rem}.telemetry-cell b{display:block;font:600 1rem 'Orbitron';margin-top:.25rem}
.stButton>button{border:1px solid rgba(66,232,255,.28)!important;background:linear-gradient(135deg,rgba(66,232,255,.13),rgba(155,108,255,.12))!important;color:#dffaff!important;border-radius:12px!important;font-weight:700!important;transition:.2s!important}.stButton>button:hover{transform:translateY(-2px);border-color:var(--cyan)!important;box-shadow:0 0 24px rgba(66,232,255,.16)!important}.stSelectbox label,.stSlider label{color:#8ea2bb!important;font-size:.75rem!important}.stSlider [data-baseweb="slider"] div{ }
div[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:14px;overflow:hidden}.footer{color:#50647e;text-align:center;font-size:.7rem;margin-top:2rem}
@media(max-width:900px){.alert-grid{grid-template-columns:1fr 1fr}.hero h1{font-size:2rem}}
</style>
""", unsafe_allow_html=True)

# Explicit animated space background (kept above Streamlit canvas, behind content)


# -----------------------------
# Data / physics
# -----------------------------
@st.cache_resource

def load_data():
    ts = load.timescale()
    with open("tle_active.txt", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]
    objects=[]
    for i in range(0,len(lines)-2,3):
        if lines[i+1].startswith("1 ") and lines[i+2].startswith("2 "):
            objects.append((lines[i],lines[i+1],lines[i+2]))
    working=objects[:5]
    satellites={name:EarthSatellite(l1,l2,name,ts) for name,l1,l2 in working}
    start=ts.now(); minutes=np.arange(0,72*60,2); times=ts.tt_jd(start.tt+minutes/1440.0)
    positions={name:sat.at(times).position.km.T for name,sat in satellites.items()}
    return satellites,positions,minutes,len(objects)

satellites,positions,minutes,total_objects=load_data(); names=list(positions)

def relative_speed(a,b,idx):
    lo,hi=max(idx-1,0),min(idx+1,len(positions[a])-1)
    if hi==lo:return 0.0
    va=(positions[a][hi]-positions[a][lo])/((hi-lo)*120); vb=(positions[b][hi]-positions[b][lo])/((hi-lo)*120)
    return float(np.linalg.norm(va-vb))

def score(dist,speed,threshold):
    return round(.7*max(0,1-dist/threshold)+.3*min(1,speed/15),3)

def level(s):
    if s>=.6:return "CRITICAL","red"
    if s>=.4:return "HIGH","amber"
    if s>=.2:return "MEDIUM","amber"
    return "LOW","green"

def cw(delta_v,t,direction,n):
    x0,y0=(delta_v,0) if direction=="radial" else (0,delta_v)
    x=(2/n)*(1-np.cos(n*t))*y0+(np.sin(n*t)/n)*x0
    y=(1/n)*(4*np.sin(n*t)-3*n*t)*y0-(2/n)*(1-np.cos(n*t))*x0
    return x,y

def orbit_class(alt_km):
    if alt_km < 2000: return "LEO"
    if alt_km < 35786: return "MEO"
    return "GEO / HIGH"

def object_profile(name, altitude_km):
    n=name.upper()
    debris = any(k in n for k in ["DEB", "DEBRIS", "ROCKET", "R/B", "SL-", "COSMOS", "FENGYUN"])
    return ("DEBRIS / ROCKET BODY" if debris else "ACTIVE / TRACKED OBJECT",
            "HIGH" if not debris else "MONITOR")

def multi_object_validation(event, disp):
    a,b,idx=event["a"],event["b"],event["idx"]
    original=[]; post=[]
    pa=positions[a][idx]
    for other in names:
        if other==a: continue
        d0=float(np.linalg.norm(pa-positions[other][idx]))
        d1=float(np.linalg.norm((pa+disp)-positions[other][idx]))
        original.append((d0,other)); post.append((d1,other))
    original.sort(); post.sort()
    return original,post

def uncertainty_radius(score_value):
    return 0.5 + 4.0*score_value

def build_pdf_report(event, best, new_score, reduction, validation, threshold):
    a,b,idx=event["a"],event["b"],event["idx"]
    new_dist,direction,sign,dv,lead,disp=best
    mins=int(minutes[idx]); hrs,mm=divmod(mins,60)
    alt=float(np.linalg.norm(positions[a][idx])-6371)
    kind_a,priority_a=object_profile(a,alt)
    kind_b,_=object_profile(b,float(np.linalg.norm(positions[b][idx])-6371))
    level_name,_=level(event["score"])
    buf=io.BytesIO()
    doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=38,leftMargin=38,topMargin=38,bottomMargin=38)
    styles=getSampleStyleSheet()
    title=ParagraphStyle("title",parent=styles["Title"],fontName="Helvetica-Bold",fontSize=21,leading=25,textColor=colors.HexColor("#0b2340"),alignment=TA_CENTER,spaceAfter=8)
    h=ParagraphStyle("h",parent=styles["Heading2"],fontName="Helvetica-Bold",fontSize=12,textColor=colors.HexColor("#0b5e75"),spaceBefore=10,spaceAfter=6)
    body=ParagraphStyle("body",parent=styles["BodyText"],fontSize=9.5,leading=14,textColor=colors.HexColor("#25364a"))
    story=[Paragraph("ORBITGUARD — MISSION SAFETY REPORT",title),
           Paragraph(f"Automated conjunction assessment • Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",body),Spacer(1,10)]
    summary=[["STATUS","RISK","MISS DISTANCE","RELATIVE SPEED","TCA","ORBIT"],
             [level_name,f"{event['score']*100:.1f}%",f"{event['dist']:.2f} km",f"{event['speed']:.3f} km/s",f"T−{hrs:02d}h {mm:02d}m",orbit_class(alt)]]
    t=Table(summary,colWidths=[70,55,75,80,65,70]); t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0b2340")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8),("ALIGN",(0,0),(-1,-1),"CENTER"),("GRID",(0,0),(-1,-1),.4,colors.HexColor("#c7d4e0")),("BACKGROUND",(0,1),(-1,1),colors.HexColor("#eef7fb")),("BOTTOMPADDING",(0,0),(-1,-1),7),("TOPPADDING",(0,0),(-1,-1),7)]))
    story += [t, Paragraph("1. Encounter Summary",h)]
    story += [Paragraph(f"Primary encounter: <b>{a}</b> × <b>{b}</b>. The screening engine propagated the tracked objects over a 72-hour window and identified the closest approach at T−{hrs:02d}h {mm:02d}m. The current heuristic risk score is {event['score']*100:.1f}%.",body)]
    story += [Paragraph("2. Object Intelligence",h)]
    obj=[["Object","Role","Priority","Altitude"],[a,kind_a,priority_a,f"{alt:,.0f} km"],[b,kind_b,"MONITOR",f"{np.linalg.norm(positions[b][idx])-6371:,.0f} km"]]
    ot=Table(obj,colWidths=[145,130,75,80]); ot.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0b5e75")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8),("GRID",(0,0),(-1,-1),.4,colors.HexColor("#c7d4e0")),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
    story += [ot,Paragraph("3. Explainable Risk Model",h),Paragraph(f"Risk = 70% distance component + 30% relative-speed component. Distance threshold used: {threshold} km. The score is a screening heuristic and must not be interpreted as a certified probability of collision.",body)]
    story += [Paragraph("4. AI Maneuver Recommendation",h),Paragraph(f"Recommended correction: <b>{direction.replace('_',' ').upper()}</b>, {'+' if sign>0 else '-'}{dv*1000:.0f} m/s, approximately <b>{lead} minutes before closest approach</b>. Estimated separation after the modeled correction: <b>{new_dist:.2f} km</b>. Screening risk changes from {event['score']*100:.1f}% to {new_score*100:.1f}% ({reduction:.1f}% reduction).",body)]
    story += [Paragraph("5. Multi-Object Safety Check",h)]
    rows=[["Object","Pre-burn km","Post-burn km","Result"]]
    for (d0,o),(d1,_) in zip(validation[0][:5],validation[1][:5]): rows.append([o,f"{d0:.2f}",f"{d1:.2f}","OK" if d1>=d0 else "REVIEW"])
    vt=Table(rows,colWidths=[190,80,80,60]); vt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0b5e75")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8),("GRID",(0,0),(-1,-1),.4,colors.HexColor("#c7d4e0")),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
    story += [vt,Paragraph("6. Limitations & Safety Note",h),Paragraph("This prototype uses public TLE data, SGP4 propagation and Clohessy–Wiltshire relative-motion equations. It does not ingest full covariance/ephemeris uncertainty, atmospheric-drag uncertainty, operational constraints, fuel budgets, or a certified conjunction-probability model. Any real maneuver requires validation by qualified flight-dynamics personnel.",body)]
    doc.build(story)
    return buf.getvalue()

def maneuver(event):
    a,b,idx=event["a"],event["b"],event["idx"]; pa,pb=positions[a][idx],positions[b][idx]
    radial=pa/np.linalg.norm(pa); lo,hi=max(idx-1,0),min(idx+1,len(positions[a])-1)
    va=(positions[a][hi]-positions[a][lo])/((hi-lo)*120); along=va/np.linalg.norm(va)
    n=satellites[a].model.no_kozai/60
    candidates=[]
    for direction in ["radial","along_track"]:
        for sign in [1,-1]:
            for dv in [.001,.003,.005]:
                for lead in [15,30,60]:
                    x,y=cw(sign*dv,lead*60,direction,n); disp=x*radial+y*along
                    candidates.append((np.linalg.norm(pa+disp-pb),direction,sign,dv,lead,disp))
    return max(candidates,key=lambda x:x[0])

# -----------------------------
# Header
# -----------------------------
now=datetime.utcnow().strftime("%H:%M:%S UTC")
st.markdown(f'''<div class="topbar"><div><span class="online"><span></span>SYSTEM ONLINE</span>&nbsp;&nbsp; ORBITAL AI / AI-2</div><div style="color:#6f849d">SGP4 PROPAGATION · 72H WINDOW · {now}</div></div>''',unsafe_allow_html=True)
st.markdown('<div class="hero"><div class="eyebrow">ORBITGUARD // SPACE SAFETY INTELLIGENCE</div><h1>SEE THE COLLISION BEFORE IT HAPPENS.</h1><p>AI-assisted conjunction detection, orbital risk scoring and maneuver planning using real TLE data and SGP4 propagation.</p></div>',unsafe_allow_html=True)

c1,c2=st.columns([5,1])
with c1: threshold=st.slider("CONJUNCTION THRESHOLD",100,1000,500,50)
with c2:
    st.markdown("<div style='height:25px'></div>",unsafe_allow_html=True)
    if st.button("↻ REFRESH DATA",use_container_width=True): load_data.clear(); st.rerun()

# -----------------------------
# Conjunction engine
# -----------------------------
events=[]
for a,b in itertools.combinations(names,2):
    d=np.linalg.norm(positions[a]-positions[b],axis=1); idx=int(np.argmin(d)); md=float(d[idx])
    if md<threshold:
        sp=relative_speed(a,b,idx); sc=score(md,sp,threshold); events.append({"a":a,"b":b,"idx":idx,"dist":md,"speed":sp,"score":sc})
events.sort(key=lambda x:x["score"],reverse=True); top=events[0] if events else None
critical=sum(e["score"]>=.6 for e in events)

# KPI strip
cols=st.columns(5)
kpis=[("TLE OBJECTS",total_objects,"cyan"),("ACTIVE TRACKS",len(names),"cyan"),("CONJUNCTIONS",len(events),"amber"),("CRITICAL",critical,"red"),("WINDOW","72 H","green")]
for col,(lab,val,cl) in zip(cols,kpis):
    with col: st.markdown(f'<div class="metric"><div class="label">{lab}</div><div class="value {cl}">{val}</div></div>',unsafe_allow_html=True)

if not top:
    st.markdown('<div class="mission" style="margin-top:1rem">🟢 No conjunctions detected under the current threshold. Increase the threshold to explore more candidate encounters.</div>',unsafe_allow_html=True)
else:
    lvl,cl=level(top["score"]); mins=int(minutes[top["idx"]]); hrs,mm=divmod(mins,60)
    st.markdown(f'''<div class="alert" style="margin-top:1rem"><div class="alert-title">⚠ {lvl} CONJUNCTION // AUTOMATED ALERT</div><div class="alert-main">{top["a"]} <span style="color:#657891">×</span> {top["b"]}</div><div class="alert-grid"><div><div class="mini">MISS DISTANCE</div><b>{top["dist"]:.1f} km</b></div><div><div class="mini">RELATIVE VELOCITY</div><b>{top["speed"]:.2f} km/s</b></div><div><div class="mini">RISK SCORE</div><b>{top["score"]*100:.1f}%</b></div><div><div class="mini">CLOSEST APPROACH</div><b>T−{hrs:02d}h {mm:02d}m</b></div></div></div>''',unsafe_allow_html=True)

    # Select event
    labels=[f'{e["a"]}  ×  {e["b"]}  |  {e["score"]*100:.1f}% risk' for e in events]
    choice=st.selectbox("FOCUS CONJUNCTION",labels,index=0)
    event=events[labels.index(choice)]
    a,b,idx=event["a"],event["b"],event["idx"]
    best=maneuver(event); new_dist,direction,sign,dv,lead,disp=best
    new_score=score(new_dist,event["speed"],threshold); reduction=max(0,(event["score"]-new_score)/max(event["score"],1e-9)*100)

    left,right=st.columns([2.2,1])
    with left:
        st.markdown('<div class="section">◉ LIVE ORBITAL THEATER</div><div class="sub">Animated orbital segment — drag, zoom and rotate the scene. Red = original path · cyan = object B · green = AI-corrected path.</div>',unsafe_allow_html=True)
        # Build a compact animated orbital scene
        win=np.arange(max(0,idx-35),min(len(minutes),idx+36),3)
        pa=positions[a][win]; pb=positions[b][win]; corrected=pa+disp
        # Earth sphere first so every animation frame redraws all traces
        u=np.linspace(0,2*np.pi,28); v=np.linspace(0,np.pi,14); R=6371
        ex=(R*np.outer(np.cos(u),np.sin(v))); ey=(R*np.outer(np.sin(u),np.sin(v))); ez=R*np.outer(np.ones_like(u),np.cos(v))
        frames=[]
        for k in range(len(win)):
            frames.append(go.Frame(data=[
                go.Surface(x=ex,y=ey,z=ez,showscale=False,opacity=.72,colorscale=[[0,'#071a35'],[1,'#1a6c91']],hoverinfo='skip'),
                go.Scatter3d(x=pa[:,0],y=pa[:,1],z=pa[:,2]),
                go.Scatter3d(x=pb[:,0],y=pb[:,1],z=pb[:,2]),
                go.Scatter3d(x=corrected[:,0],y=corrected[:,1],z=corrected[:,2]),
                go.Scatter3d(x=[pa[k,0]],y=[pa[k,1]],z=[pa[k,2]]),
                go.Scatter3d(x=[pb[k,0]],y=[pb[k,1]],z=[pb[k,2]])],name=str(k)))
        fig=go.Figure(data=[
            go.Surface(x=ex,y=ey,z=ez,showscale=False,opacity=.72,colorscale=[[0,'#071a35'],[1,'#1a6c91']],hoverinfo='skip'),
            go.Scatter3d(x=pa[:,0],y=pa[:,1],z=pa[:,2],mode='lines',name=f'{a} ORIGINAL',line=dict(color='#ff5268',width=5)),
            go.Scatter3d(x=pb[:,0],y=pb[:,1],z=pb[:,2],mode='lines',name=f'{b}',line=dict(color='#42e8ff',width=5)),
            go.Scatter3d(x=corrected[:,0],y=corrected[:,1],z=corrected[:,2],mode='lines',name='AI MANEUVER',line=dict(color='#42f59b',width=4,dash='dash')),
            go.Scatter3d(x=[pa[0,0]],y=[pa[0,1]],z=[pa[0,2]],mode='markers',name='OBJECT A',marker=dict(size=8,color='#ff5268')),
            go.Scatter3d(x=[pb[0,0]],y=[pb[0,1]],z=[pb[0,2]],mode='markers',name='OBJECT B',marker=dict(size=8,color='#42e8ff'))],frames=frames)
        fig.update_layout(template='plotly_dark',height=610,margin=dict(l=0,r=0,t=0,b=0),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',scene=dict(bgcolor='rgba(0,0,0,0)',aspectmode='data',xaxis=dict(showgrid=False,showticklabels=False,title=''),yaxis=dict(showgrid=False,showticklabels=False,title=''),zaxis=dict(showgrid=False,showticklabels=False,title='')),legend=dict(orientation='h',y=-.02,x=.02),updatemenus=[dict(type='buttons',showactive=False,x=.02,y=.99,xanchor='left',yanchor='top',buttons=[dict(label='▶ PLAY ORBIT',method='animate',args=[None,{'frame':{'duration':100,'redraw':True},'transition':{'duration':0},'fromcurrent':True}]),dict(label='⏸ PAUSE',method='animate',args=[[None],{'mode':'immediate','frame':{'duration':0,'redraw':True}}]),dict(label='↻ RESTART',method='animate',args=[[str(0)],{'mode':'immediate','frame':{'duration':0,'redraw':True}}])])])
        st.plotly_chart(fig,use_container_width=True,config={'displaylogo':False,'scrollZoom':True})
    with right:
        st.markdown('<div class="section">⌁ MISSION TELEMETRY</div>',unsafe_allow_html=True)
        risk_pct=event["score"]*100
        st.markdown(f'''<div class="mission"><div class="mission-row"><span>COLLISION RISK</span><b>{risk_pct:.1f}%</b></div><div class="bar"><div class="fill" style="width:{min(100,risk_pct)}%"></div></div><div class="mission-row"><span>POST-MANEUVER RISK</span><b style="color:#42f59b">{new_score*100:.1f}%</b></div><div class="bar"><div class="fill" style="width:{min(100,new_score*100)}%"></div></div></div>''',unsafe_allow_html=True)
        r=positions[a][idx]; radius=np.linalg.norm(r); alt=radius-6371
        vel=event["speed"]
        st.markdown(f'''<div class="telemetry" style="margin-top:.8rem"><div style="font:700 .7rem Orbitron;color:#42e8ff;margin-bottom:.7rem">{a}</div><div class="telemetry-grid"><div class="telemetry-cell"><small>Altitude</small><b>{alt:,.0f} km</b></div><div class="telemetry-cell"><small>Rel. velocity</small><b>{vel:.2f} km/s</b></div><div class="telemetry-cell"><small>Miss distance</small><b>{event["dist"]:.1f} km</b></div><div class="telemetry-cell"><small>CA in</small><b>{hrs:02d}:{mm:02d}</b></div></div></div>''',unsafe_allow_html=True)
        st.markdown(f'''<div class="mission" style="margin-top:.8rem"><div style="font:700 .72rem Orbitron;color:#42f59b">✓ AI MANEUVER OPTIMIZED</div><div style="font:700 1.3rem Orbitron;margin:.45rem 0">{direction.replace('_',' ').upper()}</div><div style="color:#8294ad;font-size:.78rem">Burn <b style="color:#fff">{'+' if sign>0 else '-'}{dv*1000:.0f} m/s</b> · execute <b style="color:#fff">{lead} min</b> before CA</div><div style="margin-top:.7rem;color:#42f59b;font-weight:700">Risk reduction: {reduction:.1f}%</div></div>''',unsafe_allow_html=True)

    # Advanced safety intelligence
    st.markdown('<div class="section">🧠 EXPLAINABLE AI + WHAT-IF SIMULATOR</div><div class="sub">Test alternative burn magnitudes and see how the modeled separation changes before choosing the recommendation.</div>',unsafe_allow_html=True)
    sim1,sim2,sim3=st.columns(3)
    with sim1: sim_dv=st.select_slider("TEST ΔV (m/s)",options=[-5,-3,-1,0,1,3,5],value=int(sign*dv*1000))
    with sim2: sim_lead=st.select_slider("LEAD TIME (min)",options=[15,30,60],value=lead)
    with sim3:
        risk_unc=uncertainty_radius(event["score"])
        st.markdown(f'<div class="mission"><div class="mission-row"><span>UNCERTAINTY ZONE</span><b>±{risk_unc:.1f} km</b></div><div style="color:#8294ad;font-size:.72rem;margin-top:.4rem">Screening visualization around the nominal state.</div></div>',unsafe_allow_html=True)
    test_disp=np.zeros(3)
    radial=positions[a][idx]/np.linalg.norm(positions[a][idx])
    lo,hi=max(idx-1,0),min(idx+1,len(positions[a])-1)
    va=(positions[a][hi]-positions[a][lo])/((hi-lo)*120); along=va/np.linalg.norm(va)
    n=satellites[a].model.no_kozai/60
    direction_test=direction
    x,y=cw(sim_dv/1000,sim_lead*60,direction_test,n); test_disp=x*radial+y*along
    test_dist=float(np.linalg.norm((positions[a][idx]+test_disp)-positions[b][idx])); test_score=score(test_dist,event["speed"],threshold)
    test_reduction=max(0,(event["score"]-test_score)/max(event["score"],1e-9)*100)
    st.markdown(f'<div class="alert" style="border-color:rgba(66,232,255,.3);background:linear-gradient(110deg,rgba(8,47,70,.55),rgba(10,15,30,.76))"><div class="alert-title" style="color:#42e8ff">WHAT-IF RESULT</div><div class="alert-main">ΔV {sim_dv:+d} m/s · {sim_lead} min lead → modeled miss distance <b>{test_dist:.2f} km</b></div><div style="color:#8294ad;font-size:.78rem">Risk: <b style="color:#fff">{test_score*100:.1f}%</b> · change vs current: <b style="color:#42f59b">{test_reduction:.1f}% reduction</b></div></div>',unsafe_allow_html=True)

    validation=multi_object_validation(event,disp)
    closest_post=validation[1][0] if validation[1] else (float('inf'),"")
    safety_status="PASS" if closest_post[0]>=threshold else "REVIEW"
    st.markdown('<div class="section">🛡 MULTI-SATELLITE SAFETY VALIDATION</div><div class="sub">The recommended correction is checked against every other tracked object at the encounter epoch to flag a possible new close approach.</div>',unsafe_allow_html=True)
    v1,v2,v3=st.columns(3)
    with v1: st.metric("POST-MANEUVER CLOSEST",f"{closest_post[0]:.1f} km",closest_post[1])
    with v2: st.metric("SAFETY SCREEN",safety_status,"No new threshold breach" if safety_status=="PASS" else "Needs review")
    with v3: st.metric("MISSION PRIORITY",object_profile(a,float(np.linalg.norm(positions[a][idx])-6371))[1],orbit_class(float(np.linalg.norm(positions[a][idx])-6371)))

    st.markdown('<div class="section">⏱ TCA COUNTDOWN + COLLISION REPLAY</div>',unsafe_allow_html=True)
    count1,count2=st.columns(2)
    with count1:
        st.markdown(f'<div class="mission"><div style="font:700 .72rem Orbitron;color:#ffb84d">TIME TO CLOSEST APPROACH</div><div style="font:800 2rem Orbitron;margin:.35rem 0">T−{hrs:02d}:{mm:02d}:00</div><div style="color:#8294ad;font-size:.72rem">Simulation clock relative to the current propagation start.</div></div>',unsafe_allow_html=True)
    with count2:
        st.markdown(f'<div class="mission"><div style="font:700 .72rem Orbitron;color:#42e8ff">REPLAY WINDOW</div><div style="font:800 2rem Orbitron;margin:.35rem 0">{len(win)} FRAMES</div><div style="color:#8294ad;font-size:.72rem">Use ▶ PLAY ORBIT above to replay the encounter.</div></div>',unsafe_allow_html=True)

    # Professional PDF report
    st.markdown('<div class="section">📄 MISSION REPORT GENERATION</div><div class="sub">Export the selected conjunction, risk model, maneuver recommendation and multi-object safety validation.</div>',unsafe_allow_html=True)
    pdf=build_pdf_report(event,best,new_score,reduction,validation,threshold)
    st.download_button("📄 GENERATE MISSION SAFETY REPORT — PDF",data=pdf,file_name=f"OrbitGuard_{a[:18]}_{b[:18]}_Report.pdf",mime="application/pdf",use_container_width=True)

    # Risk table and trajectory analytics
    st.markdown('<div class="section">▦ CONJUNCTION INTELLIGENCE</div><div class="sub">Ranked encounters from the current 72-hour propagation window.</div>',unsafe_allow_html=True)
    table=pd.DataFrame([{"OBJECT A":e["a"],"OBJECT B":e["b"],"MISS (KM)":round(e["dist"],1),"REL. SPEED":round(e["speed"],2),"RISK":f'{e["score"]*100:.1f}%',"LEVEL":level(e["score"])[0]} for e in events])
    st.dataframe(table,use_container_width=True,hide_index=True,height=min(380,80+len(table)*38))

    st.markdown('<div class="section">⌁ ENCOUNTER SIGNATURE</div>',unsafe_allow_html=True)
    win=slice(max(0,idx-60),min(len(minutes),idx+60)); dist=np.linalg.norm(positions[a]-positions[b],axis=1)[win]
    line=go.Figure(); line.add_trace(go.Scatter(x=minutes[win],y=dist,mode='lines',line=dict(color='#42e8ff',width=3),fill='tozeroy',fillcolor='rgba(66,232,255,.06)',name='Relative distance'))
    line.add_vline(x=minutes[idx],line_dash='dot',line_color='#ff5268',annotation_text='CLOSEST APPROACH',annotation_font_color='#ff7181')
    line.add_hline(y=threshold,line_dash='dash',line_color='#ffb84d',annotation_text=f'Threshold {threshold} km',annotation_font_color='#ffcf78')
    line.update_layout(template='plotly_dark',height=330,margin=dict(l=0,r=0,t=15,b=0),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',xaxis_title='Minutes from now',yaxis_title='Distance (km)',xaxis=dict(gridcolor='rgba(120,150,190,.12)'),yaxis=dict(gridcolor='rgba(120,150,190,.12)'))
    st.plotly_chart(line,use_container_width=True,config={'displaylogo':False})

st.markdown('<div class="footer">ORBITGUARD · CelesTrak public TLE data · SGP4 via Skyfield · Risk score is a screening heuristic, not a certified probability of collision · Maneuver estimate uses Clohessy–Wiltshire relative-motion equations · Multi-object validation and report export included.</div>',unsafe_allow_html=True)

st.caption("ORBITGUARD • Prototype screening dashboard • Not for autonomous operational control")
