# app_sim1.py
# Simulation #1 — Problem Discovery & Validation (ThermaLoop)
# Run: streamlit run app_sim1.py

import random
from typing import Dict, Any, List
import streamlit as st

random.seed(42)
st.set_page_config(page_title="Simulation #1 — Problem Discovery & Validation", page_icon="🎧", layout="wide")

TITLE = "Simulation #1 — Problem Discovery & Validation"
SUB   = "ThermaLoop: exploring home comfort and energy efficiency pains"

MARKET_BRIEF = (
    "Many homes have uneven temperatures and energy waste due to poor airflow balance. "
    "Homeowners report hot and cold rooms, high bills, and uncertainty about affordable fixes. "
    "Retrofits feel complex; installers vary in quality; comfort vs savings trade-offs are unclear."
)

# ---------- Channels (no underscores). yield/speed only used conceptually; allocation drives sampling bias ----------
CHANNELS = {
    "Neighborhood Forums":  {"yield": 0.9, "speed": 0.8, "bias": {"Homeowner": 0.5, "Renter": 0.2, "Landlord": 0.2, "Installer": 0.1}},
    "Email Outreach":       {"yield": 0.7, "speed": 0.7, "bias": {"Homeowner": 0.3, "Renter": 0.3, "Landlord": 0.2, "Installer": 0.2}},
    "Cold Direct Messages": {"yield": 0.5, "speed": 0.6, "bias": {"Homeowner": 0.3, "Renter": 0.3, "Landlord": 0.2, "Installer": 0.2}},
    "Sidewalk Intercepts":  {"yield": 0.6, "speed": 0.9, "bias": {"Homeowner": 0.4, "Renter": 0.4, "Landlord": 0.1, "Installer": 0.1}},
    "Installer Referrals":  {"yield": 0.8, "speed": 0.5, "bias": {"Homeowner": 0.2, "Renter": 0.1, "Landlord": 0.2, "Installer": 0.5}},
}
EFFORT_TOKENS = 10

# ---------- Personas (12 interview + 12 flash) ----------
INTERVIEW_PERSONAS = [
    {"name":"Maya Chen","segment":"Homeowner","bio":"3-bed townhouse; two kids; upstairs hot in summer.",
     "pains":[{"text":"Upstairs rooms hotter than downstairs in summer","freq":4,"sev":4,"material":True},
              {"text":"Energy bill spikes June–August","freq":3,"sev":3,"material":True}],
     "triggers":["Heat waves; kids up at night"],"workaround":"Portable fans; close downstairs vents",
     "wtp_ceiling":15,"tell_threshold":0.55,"anecdotes":["We moved the kids downstairs to sleep last July."],"quirk":"Tracks bills in a spreadsheet"},
    {"name":"Sam Rodriguez","segment":"Homeowner","bio":"Older HVAC; cares for elderly parent; wants comfort.",
     "pains":[{"text":"Cold draft in living room in winter","freq":4,"sev":4,"material":True}],
     "triggers":["Cold snaps"],"workaround":"Space heater by sofa","wtp_ceiling":10,"tell_threshold":0.6,
     "anecdotes":["We stuffed towels by the door last December."],"quirk":"DIY enthusiast"},
    {"name":"Aisha Patel","segment":"Renter","bio":"Top-floor apartment; pays electric; landlord slow to respond.",
     "pains":[{"text":"Bedroom overheats; poor sleep","freq":4,"sev":4,"material":True}],
     "triggers":["Heat waves"],"workaround":"Cracked window; box fan","wtp_ceiling":8,"tell_threshold":0.5,
     "anecdotes":["I sleep with an ice pack sometimes."],"quirk":"Reads product reviews obsessively"},
    {"name":"Jordan Blake","segment":"Landlord","bio":"Manages 18 units; fields comfort complaints.",
     "pains":[{"text":"Frequent tenant complaints about uneven heating","freq":4,"sev":3,"material":True}],
     "triggers":["First cold snap"],"workaround":"Tell tenants to adjust dampers; duct cleaning",
     "wtp_ceiling":0,"tell_threshold":0.65,"anecdotes":["Three units called the same night last January."],"quirk":"Wants low-touch solutions"},
    {"name":"Riley Nguyen","segment":"Installer","bio":"Independent HVAC installer; skeptical of new gadgets.",
     "pains":[{"text":"Callbacks after installs due to comfort complaints","freq":3,"sev":3,"material":True}],
     "triggers":["Season changes"],"workaround":"Manual damper balancing; upsell thermostat",
     "wtp_ceiling":0,"tell_threshold":0.7,"anecdotes":["I’ve taped vents to force more air to back rooms."],"quirk":"Prefers proven gear"},
    {"name":"Priya Desai","segment":"Homeowner","bio":"Newer build; nursery cold at night; tech-friendly.",
     "pains":[{"text":"Nursery too cold at night","freq":4,"sev":4,"material":True}],
     "triggers":["Baby waking"],"workaround":"Space heater on timer","wtp_ceiling":18,"tell_threshold":0.55,
     "anecdotes":["We check room temp on a smart baby monitor."],"quirk":"Smart home early adopter"},
    {"name":"Marcus Lee","segment":"Homeowner","bio":"Old Victorian; leaky windows; budget-aware.",
     "pains":[{"text":"Heating bill too high for comfort achieved","freq":4,"sev":4,"material":True},
              {"text":"Basement office stays cold","freq":3,"sev":3,"material":True}],
     "triggers":["Bill arrival; WFH days"],"workaround":"Heater under desk; sweaters","wtp_ceiling":12,"tell_threshold":0.6,
     "anecdotes":["I track the thermostat closely in winter."],"quirk":"Likes numbers"},
    {"name":"Elena Rossi","segment":"Renter","bio":"Garden apartment; landlord controls boiler; wants comfort.",
     "pains":[{"text":"Bedroom cold, living room warm","freq":4,"sev":3,"material":True}],
     "triggers":["Cold nights"],"workaround":"Heavy blanket; asks landlord","wtp_ceiling":5,"tell_threshold":0.5,
     "anecdotes":["Studying in a hoodie and gloves."],"quirk":"Time-pressed student"},
    {"name":"Derrick Owens","segment":"Installer","bio":"Regional installer; partners with property managers.",
     "pains":[{"text":"Wants upsell that reduces callbacks","freq":3,"sev":3,"material":True}],
     "triggers":["Post-install complaints"],"workaround":"Higher-end dampers; room heaters",
     "wtp_ceiling":0,"tell_threshold":0.65,"anecdotes":["Callbacks kill our margins."],"quirk":"Sales-forward"},
    {"name":"Hannah Kim","segment":"Homeowner","bio":"Townhome; hosts often; wants quiet comfort in guest room.",
     "pains":[{"text":"Guest room too hot; vent noise","freq":3,"sev":3,"material":True}],
     "triggers":["When guests visit"],"workaround":"Close vent; portable AC","wtp_ceiling":9,"tell_threshold":0.55,
     "anecdotes":["We warn guests to bring a light blanket."],"quirk":"Aesthetic sensitive"},
    {"name":"Omar Farouk","segment":"Landlord","bio":"Owns 6 single-family rentals; wants fewer tenant calls.",
     "pains":[{"text":"Comfort complaints drive churn","freq":3,"sev":3,"material":True}],
     "triggers":["Renewal season"],"workaround":"Remind to adjust vents; one-off fixes","wtp_ceiling":0,"tell_threshold":0.6,
     "anecdotes":["A family left over heating issues."],"quirk":"Cost-focused"},
    {"name":"Zoey Park","segment":"Homeowner","bio":"Small bungalow; budget constrained; cares about bills.",
     "pains":[{"text":"Bill spikes after cold front","freq":3,"sev":3,"material":True}],
     "triggers":["Utility email; bill shock"],"workaround":"Lower thermostat; layers","wtp_ceiling":6,"tell_threshold":0.5,
     "anecdotes":["I compare bills with neighbors."],"quirk":"Coupon clipper"},
]

FLASH_PERSONAS = [
    {"name":"Flash — Property Manager","segment":"Landlord","bio":"30 units; central HVAC.",
     "note":"Comfort tickets spike after first cold week; room-by-room balancing is slow."},
    {"name":"Flash — Parent of Infant","segment":"Homeowner","bio":"Nursery swings at night.",
     "note":"Tried taping vent and space heater; worried about safety and bills."},
    {"name":"Flash — Student Renter","segment":"Renter","bio":"Basement room; landlord controls temperature.",
     "note":"Studies in living room for warmth; electric bill rises with space heater."},
    {"name":"Flash — Retiree","segment":"Homeowner","bio":"Fixed income; wants payback.",
     "note":"Wants proof a retrofit pays back within a year."},
    {"name":"Flash — Short-Term Rental Host","segment":"Landlord","bio":"Reviews mention comfort.",
     "note":"Would pay for something that reduces guest complaints."},
    {"name":"Flash — Installer Crew Lead","segment":"Installer","bio":"Trains techs.",
     "note":"Seeks add-on that reduces rework with clear margin."},
    {"name":"Flash — Remote Worker","segment":"Homeowner","bio":"Cold basement office.",
     "note":"Heater helps but hikes bill; wants smarter airflow."},
    {"name":"Flash — Eco Enthusiast","segment":"Homeowner","bio":"Solar + smart thermostat.",
     "note":"Comfort fine; wants measurable energy savings."},
    {"name":"Flash — Building Superintendent","segment":"Installer","bio":"Condo block maintenance.",
     "note":"Needs clear install steps and warranty handling."},
    {"name":"Flash — Budget-Conscious Couple","segment":"Homeowner","bio":"Watching expenses.",
     "note":"Open to DIY if upfront under $150 and payback <12 months."},
    {"name":"Flash — Pet Owner","segment":"Homeowner","bio":"Dog sleeps in warmest room.",
     "note":"Wants quieter airflow at night; noise matters."},
    {"name":"Flash — Tech Skeptic","segment":"Homeowner","bio":"Avoids ‘smart’ gadgets.",
     "note":"Needs simple, non-intrusive device with tangible savings."},
]

# ---------- Segment-tailored question banks (open vs leading governs trust) ----------
QB = {
    "Homeowner": [
        {"key":"habit_home","text":"Tell me about your habits for heating and cooling your home.","kind":"open"},
        {"key":"starters1","text":"Walk me through a typical day when a room feels uncomfortable.","kind":"open"},
        {"key":"starters2","text":"Tell me about the last time the temperature felt off. What happened?","kind":"open"},
        {"key":"impact","text":"What does this problem stop you from doing, or make harder?","kind":"open"},
        {"key":"workarounds","text":"What have you tried so far? How did it go?","kind":"open"},
        {"key":"frequency","text":"How often does this happen in a typical month?","kind":"open"},
        {"key":"bill","text":"How did your energy bill change when this was worst?","kind":"open"},
        {"key":"priorities","text":"What matters most right now: saving energy, convenience, saving money, or home comfort?","kind":"open"},
        {"key":"leading_buy","text":"Would you buy a device to fix airflow if it was affordable?","kind":"leading"},
        {"key":"solutioning","text":"What if I built smart vents you could control by phone?","kind":"leading"},
    ],
    "Renter": [
        {"key":"habit_renter","text":"How do you manage heating and cooling when you can’t change the system?","kind":"open"},
        {"key":"last_time","text":"Tell me about the last night it was uncomfortable. What did you do?","kind":"open"},
        {"key":"impact","text":"How does this affect sleep, work, or bills?","kind":"open"},
        {"key":"workarounds","text":"What workarounds have you tried?","kind":"open"},
        {"key":"frequency","text":"How often does this happen in a month?","kind":"open"},
        {"key":"bill","text":"How does your electric bill change when you use heaters or fans?","kind":"open"},
        {"key":"priorities","text":"Which matters most: comfort, saving money, or convenience?","kind":"open"},
        {"key":"leading_buy","text":"If it were renter-friendly, would you pay monthly for better airflow?","kind":"leading"},
        {"key":"solutioning","text":"What if there were clip-on vents with an app?","kind":"leading"},
    ],
    "Landlord": [
        {"key":"habit_land","text":"What are your biggest frustrations with heating and cooling across units?","kind":"open"},
        {"key":"last_wave","text":"Tell me about the last cold or heat wave—what calls came in?","kind":"open"},
        {"key":"impact","text":"How do comfort complaints affect renewals or reviews?","kind":"open"},
        {"key":"ops","text":"How do you currently handle balancing and follow-ups?","kind":"open"},
        {"key":"frequency","text":"How often do these tickets appear in a season?","kind":"open"},
        {"key":"costs","text":"Where do costs spike—labor, equipment, or damages?","kind":"open"},
        {"key":"priorities","text":"What’s the top priority: fewer complaints, lower ops cost, or faster response?","kind":"open"},
        {"key":"leading_buy","text":"Would you pay per unit for a retrofit that reduces complaints?","kind":"leading"},
        {"key":"solutioning","text":"What if techs could clip on smart vents and see fewer callbacks?","kind":"leading"},
    ],
    "Installer": [
        {"key":"habit_inst","text":"What patterns do you see when customers complain about comfort after installs?","kind":"open"},
        {"key":"cases","text":"Tell me about a recent case you had to revisit.","kind":"open"},
        {"key":"impact","text":"How do callbacks affect your schedule or margins?","kind":"open"},
        {"key":"methods","text":"How do you currently balance airflow or diagnose issues?","kind":"open"},
        {"key":"frequency","text":"How often are revisits needed during season changes?","kind":"open"},
        {"key":"proof","text":"What proof do customers ask for to believe improvements?","kind":"open"},
        {"key":"priorities","text":"What matters most: simple install, reliability, or upsell potential?","kind":"open"},
        {"key":"leading_buy","text":"Would you recommend an add-on if it’s reliable and profitable?","kind":"leading"},
        {"key":"solutioning","text":"What if a kit made balancing automatic—would that help?","kind":"leading"},
    ],
}

# ---------- Segment-level default answers ----------
SEGMENT_ANSWERS = {
    "Homeowner": {
        "habit_home":"We try to keep a steady set point, but afternoons heat up upstairs.",
        "starters1":"By evening the nursery hits high 70s; downstairs stays cooler.",
        "starters2":"Last week during a warm spell, the bedroom hit 79°F at 10pm.",
        "impact":"Poor sleep for kids; we move fans and argue over the thermostat.",
        "workarounds":"We half-close vents, run a box fan, sometimes a space heater.",
        "frequency":"Maybe 8–12 times a month in summer.",
        "bill":"Bills go up 20–25% mid-summer.",
        "priorities":"Comfort first at night, but bills matter too.",
        "leading_buy":"Maybe, if it actually works and isn’t loud.",
        "solutioning":"It’d have to be simple, quiet, and safe around kids."
    },
    "Renter": {
        "habit_renter":"I open windows, use a fan; landlord controls the boiler.",
        "last_time":"Two nights ago the bedroom was way too warm; I slept on the couch.",
        "impact":"Sleep suffers; studying is harder; bill creeps up with the fan.",
        "workarounds":"Fan, window, lighter bedding; landlord is slow.",
        "frequency":"5–10 nights a month in summer.",
        "bill":"Electric bill rises $15–30 those months.",
        "priorities":"Comfort, then cost; I can’t change the system.",
        "leading_buy":"If renter-friendly and I can take it with me—maybe.",
        "solutioning":"Landlord approval could be an issue—how would that work?"
    },
    "Landlord": {
        "habit_land":"Complaints cluster on first cold week—phones light up.",
        "last_wave":"Three units called same night; top floors too cold.",
        "impact":"Bad reviews and sometimes lost renewals.",
        "ops":"We ask tenants to adjust dampers; sometimes send techs to rebalance.",
        "frequency":"At season change, then a few times per month.",
        "costs":"Labor overtime is the big hit; not utilities.",
        "priorities":"Fewer complaints with minimal complexity.",
        "leading_buy":"If it cuts complaints without extra headaches, yes.",
        "solutioning":"Needs clear install steps, durability, and warranty."
    },
    "Installer": {
        "habit_inst":"Often renovations leave ducts unbalanced; returns far from rooms.",
        "cases":"New furnace; back room still cold; had to revisit to balance.",
        "impact":"Callbacks wreck the schedule and margins.",
        "methods":"Manual damper balancing; sometimes recommend new thermostat.",
        "frequency":"Weekly during season changes.",
        "proof":"Customers want before/after temps or energy data.",
        "priorities":"Simple install and reliability; upsell helps.",
        "leading_buy":"If reliable and upsell-ready, sure.",
        "solutioning":"Only if it won’t jam and support is solid."
    },
}

# ---------- State ----------
def init_state():
    st.session_state.s1 = {
        "stage":"intro",
        "alloc":{k:0 for k in CHANNELS},
        "booked_ids":[],
        "current_idx":0,           # walk through interviews one by one
        "interview":{},            # pid -> dict: asked set, q_count, trust, transcript, ended
        "flash_open":[],
        "analytics":{},
        "draft_struct":{           # structured inputs for hypothesis and test
            "who":"Homeowner",
            "core_pain":"Uneven room temperatures at night",
            "trigger":"Heat waves / bedtime",
            "impact":"Poor sleep and family stress",
            "workaround":"Fans and manual vent adjustments",
            "quantifier":"Happens 8–12 nights per month; bills +20–25%",
            "next_method":"Landing page A/B (comfort vs savings)",
            "next_target":"Signups ≥ 4% of unique visitors"
        },
        "problem_text":"",
        "next_test_text":"",
        "submitted_draft":False,
        "score":None,
        "reasons":{}
    }
if "s1" not in st.session_state:
    init_state()
S = st.session_state.s1

def clamp(x,a,b): return max(a, min(b, x))

# ---------- Stage bar ----------
STAGES = ["intro","target","live","flash","synth","draft","score"]
LABELS = {
    "intro":"Intro",
    "target":"Target & Recruit",
    "live":"Live Interviews",
    "flash":"Flash Bursts",
    "synth":"Synthesis",
    "draft":"Decide & Draft",
    "score":"Feedback & Score"
}
def stage_bar():
    cols = st.columns(len(STAGES))
    for i, key in enumerate(STAGES):
        label = LABELS[key]
        style = "✅ " if STAGES.index(S["stage"])>i else ("👉 " if S["stage"]==key else "")
        if cols[i].button(f"{style}{label}", key=f"nav_{key}"):
            # Only allow backward navigation or same-stage, not forward skipping
            if STAGES.index(key) <= STAGES.index(S["stage"]):
                S["stage"] = key
                st.rerun()

# ---------- Recruitment ----------
def recruit_personas(alloc: Dict[str,int], need:int=6) -> List[int]:
    weights=[]
    for i,p in enumerate(INTERVIEW_PERSONAS):
        seg = p["segment"]
        w=0.0
        for ch, t in alloc.items():
            if t<=0: continue
            chp=CHANNELS[ch]
            w += t * chp["yield"] * chp["bias"].get(seg,0.1) * random.uniform(0.85,1.15)
        weights.append((i, max(0.0001,w)))
    total = sum(w for _,w in weights)
    probs = [w/total for _,w in weights]
    chosen=set()
    while len(chosen)<min(need,len(INTERVIEW_PERSONAS)):
        r=random.random(); cum=0
        for idx,(i,w) in enumerate(weights):
            cum += probs[idx]
            if r<=cum:
                chosen.add(i); break
    return list(chosen)

# ---------- Interview engine ----------
def init_interview(pid:int):
    p = INTERVIEW_PERSONAS[pid]
    if pid in S["interview"]: return
    keys = [q["key"] for q in QB[p["segment"]]]
    random.shuffle(keys)
    S["interview"][pid] = {
        "asked":set(), "left":keys, "q_count":0,
        "trust": 0.4 if p["segment"] in ["Landlord","Installer"] else 0.5,
        "transcript":[], "ended":False
    }

def selectable(pid:int)->List[Dict[str,Any]]:
    stt=S["interview"][pid]
    seg = INTERVIEW_PERSONAS[pid]["segment"]
    bank = {q["key"]:q for q in QB[seg]}
    left=[k for k in stt["left"] if k not in stt["asked"]]
    # sort: open first
    objs=[bank[k] for k in left]
    objs.sort(key=lambda q: 0 if q["kind"]=="open" else 1)
    return objs[:5]

def answer_for(pid:int, qkey:str)->str:
    p = INTERVIEW_PERSONAS[pid]
    trust = S["interview"][pid]["trust"]
    base = SEGMENT_ANSWERS[p["segment"]].get(qkey, "Not sure.")
    extra=""
    if trust >= p["tell_threshold"]:
        mats=[x for x in p["pains"] if x["material"]]
        if mats:
            top=max(mats, key=lambda d:d["freq"]+d["sev"])
            if qkey in ["impact","workarounds","starters2","last_time","ops","methods"]:
                extra += f" The key issue is: {top['text']}."
        if qkey in ["bill","costs"]:
            extra += " We see a noticeable jump during peak months."
        if p["wtp_ceiling"]>0 and qkey in ["leading_buy","solutioning"]:
            extra += f" I might pay up to about ${p['wtp_ceiling']}/month if it really helps."
    if random.random()<0.2:
        extra += " It does vary week to week."
    return base + ((" " + extra) if extra else "")

def ask(pid:int, qkey:str, qtext:str):
    stt=S["interview"][pid]
    seg = INTERVIEW_PERSONAS[pid]["segment"]
    kind = next(q["kind"] for q in QB[seg] if q["key"]==qkey)
    # trust dynamics
    stt["trust"] = clamp(stt["trust"] + (0.06 if kind=="open" else -0.08), 0, 1)
    ans = answer_for(pid, qkey)
    stt["transcript"].append({"q":qtext,"a":ans,"kind":kind})
    stt["asked"].add(qkey)
    stt["q_count"] += 1
    S["interview"][pid]=stt

# ---------- Synthesis ----------
def run_synthesis():
    pain_kw = {
        "Hot room":["hot","overheat","sticky"],
        "Cold room":["cold","draft","chilly"],
        "High bill":["bill","cost","expensive"],
        "No control":["landlord","no control","cannot change"],
        "Noise":["noisy","loud","vent"],
    }
    clusters={k:0 for k in pain_kw}
    quotes={k:[] for k in pain_kw}
    # interviews
    for pid, stt in S["interview"].items():
        for t in stt["transcript"]:
            txt=(t["q"]+" "+t["a"]).lower()
            for c,words in pain_kw.items():
                if any(w in txt for w in words):
                    clusters[c]+=1
                    if len(quotes[c])<3: quotes[c].append(t["a"])
    # flash
    for fidx in S["flash_open"]:
        f=FLASH_PERSONAS[fidx]; txt=(f["bio"]+" "+f["note"]).lower()
        for c,words in pain_kw.items():
            if any(w in txt for w in words):
                clusters[c]+=1
                if len(quotes[c])<3: quotes[c].append(f["note"])
    # coverage & bias
    segs=[INTERVIEW_PERSONAS[pid]["segment"] for pid in S["booked_ids"]]
    seg_mix={s:segs.count(s) for s in set(segs)}
    total_alloc=sum(S["alloc"].values())
    top_ch=max(S["alloc"], key=lambda k:S["alloc"][k]) if total_alloc>0 else None
    bias = total_alloc>0 and S["alloc"][top_ch] > 0.6*total_alloc
    S["analytics"]={"clusters":clusters,"quotes":quotes,"seg_mix":seg_mix,"bias_flag":bias,"top_channel":top_ch}

# ---------- Scoring ----------
def compute_score():
    # craft
    total_q=open_q=lead_q=0; trusts=[]
    for pid, stt in S["interview"].items():
        if stt["q_count"]>0: trusts.append(stt["trust"])
        for t in stt["transcript"]:
            total_q+=1
            if t["kind"]=="open": open_q+=1
            else: lead_q+=1
    open_pct = open_q/max(1,total_q)
    lead_pct = lead_q/max(1,total_q)
    avg_trust = sum(trusts)/max(1,len(trusts))
    craft = 0.5*min(1.0, open_pct/0.7) + 0.3*max(0, 1 - max(0,(lead_pct-0.15)/0.85)) + 0.2*min(1.0, avg_trust/0.6)
    craft_score=int(100*craft)

    # coverage
    seg_div=len(S["analytics"].get("seg_mix",{}))
    channel_ok = 0 if S["analytics"].get("bias_flag") else 1
    coverage = clamp((0.6 if seg_div>=3 else 0.35 if seg_div==2 else 0.15) + 0.4*channel_ok,0,1)
    coverage_score=int(100*coverage)

    # detection
    clusters=S["analytics"]["clusters"]
    top = max(clusters, key=lambda k:clusters[k]) if clusters else None
    hypo=S["problem_text"].lower()
    aligned = 1 if (top and any(w in hypo for w in top.lower().split())) else 0
    quantified = 1 if any(x in hypo for x in ["%", " times", " per ", " degree", "$"]) else 0
    detection=int(100*clamp(0.6*aligned+0.4*quantified,0,1))

    # problem
    who_ok = any(s in hypo for s in ["homeowner","renter","landlord","installer"])
    trig_ok = any(s in hypo for s in ["heat","cold","bill","complain","night","summer","winter"])
    testable_ok = any(s in hypo for s in ["measure","within","increase","reduce","by "])
    problem=int(100*clamp(0.35*who_ok+0.35*trig_ok+0.3*testable_ok,0,1))

    # next test
    nxt=S["next_test_text"].lower()
    method_ok = any(s in nxt for s in ["landing","preorder","pilot","trial","survey","interview","prototype","a/b"])
    threshold_ok = any(x in nxt for x in ["target", ">=", "<=", "%", " signups", " conversions", " complaints"])
    next_score=int(100*clamp(0.5*method_ok+0.5*threshold_ok,0,1))

    total=int(0.30*craft_score + 0.15*coverage_score + 0.30*detection + 0.15*problem + 0.10*next_score)

    S["score"]={"total":total,"components":{
        "Interview Craft":craft_score,"Coverage":coverage_score,
        "Signal Detection":detection,"Problem Statement Quality":problem,
        "Next Test Plan":next_score}}
    S["reasons"]={
        "Interview Craft": f"Open {int(open_pct*100)}%, leading {int(lead_pct*100)}%, avg trust {avg_trust:.2f} (targets: ≥70% open, ≤15% leading, trust ≥0.6).",
        "Coverage": f"Segments: {', '.join(S['analytics'].get('seg_mix',{}).keys()) or 'none'}. Channel bias: {'high' if S['analytics'].get('bias_flag') else 'balanced'}.",
        "Signal Detection": f"Top cluster match: {'yes' if aligned else 'no'}; quantification: {'yes' if quantified else 'no'}.",
        "Problem Statement": "Checked for specific who, triggers, and testable phrasing.",
        "Next Test Plan": "Checked for clear method and a measurable threshold."
    }

# ---------- Header ----------
def header():
    st.title(TITLE)
    st.caption(SUB)
    st.markdown(f"**Market brief:** {MARKET_BRIEF}")
    stage_bar()
    st.progress((STAGES.index(S["stage"])+1)/len(STAGES))
    st.divider()

# ---------- Pages ----------
def page_intro():
    st.subheader("How this simulation works")
    st.markdown("""
1) **Target & recruit** with 10 effort tokens.  
2) **Interview** your booked personas (guided questions, one by one).  
3) Open **flash bursts** to broaden coverage.  
4) **Synthesize** patterns (clusters, quotes, bias).  
5) **Draft** a problem hypothesis & next test (with structured fields).  
6) Submit and view **feedback & score**.
""")
    if st.button("Start simulation"):
        S["stage"]="target"; st.rerun()

def page_target():
    st.subheader("Target & recruit")
    st.info("Allocate 10 effort tokens across outreach channels. Click the number fields to adjust. Balance channels to reduce sampling bias.")
    c1, c2 = st.columns([2,1])
    with c1:
        total=0
        for ch in CHANNELS:
            S["alloc"][ch] = st.number_input(ch, min_value=0, max_value=5, step=1, value=S["alloc"][ch], key=f"alloc_{ch}")
            total += S["alloc"][ch]
    with c2:
        st.metric("Tokens allocated", f"{total}/{EFFORT_TOKENS}")
        if total>EFFORT_TOKENS:
            st.error("You allocated more than 10 tokens. Reduce some numbers.")
    if st.button("Book personas"):
        if total<=EFFORT_TOKENS:
            S["booked_ids"]=recruit_personas(S["alloc"], need=6)
            S["interview"].clear()
            for pid in S["booked_ids"]:
                init_interview(pid)
            S["current_idx"]=0
            S["stage"]="live"; st.rerun()
        else:
            st.warning("Fix token allocation before booking.")

def page_live():
    st.subheader("Live interviews")
    st.caption("Interview everyone you booked. Open questions build trust; avoid leading or solution talk early.")
    st.markdown(f"**Interviews booked:** {len(S['booked_ids'])}")
    # Top summary of booked
    with st.expander("Booked personas (bios)"):
        for pid in S["booked_ids"]:
            p=INTERVIEW_PERSONAS[pid]
            st.markdown(f"- **{p['name']}** — {p['segment']}  \n  _{p['bio']}_")

    if not S["booked_ids"]:
        st.warning("No personas booked. Go back to Target & recruit.")
        return

    # Guided one-by-one
    idx = S["current_idx"]
    if idx >= len(S["booked_ids"]):
        st.success("You’ve finished all booked interviews.")
        if st.button("Go to Flash Bursts"):
            S["stage"]="flash"; st.rerun()
        return

    pid = S["booked_ids"][idx]
    p = INTERVIEW_PERSONAS[pid]
    st.markdown(f"### Interview {idx+1} of {len(S['booked_ids'])}: **{p['name']}** — {p['segment']}")
    st.write(f"**Bio:** {p['bio']}")
    st.write(f"**Known workaround:** {p['workaround']}")
    st.divider()

    stt=S["interview"][pid]
    if not stt["ended"]:
        # show up to 5 options tailored to segment
        opts = selectable(pid)
        # render 3 per row
        for row in [opts[i:i+3] for i in range(0, len(opts), 3)]:
            cols = st.columns(len(row))
            for i,q in enumerate(row):
                if cols[i].button(q["text"], key=f"q_{pid}_{q['key']}"):
                    ask(pid, q["key"], q["text"])
                    st.rerun()
        if stt["q_count"]>=2:
            if st.button("Thank and end interview"):
                stt["ended"]=True; S["interview"][pid]=stt; st.rerun()
    else:
        st.success("Interview ended for this persona.")
        if st.button("Next interview"):
            S["current_idx"] += 1
            st.rerun()

    st.markdown("#### Transcript")
    if stt["transcript"]:
        for turn in stt["transcript"]:
            st.write(f"**You:** {turn['q']}")
            st.write(f"**{p['name']}:** {turn['a']}")
    else:
        st.caption("No questions asked yet.")

    st.divider()
    c1, c2 = st.columns(2)
    if c1.button("Back to Target"):
        S["stage"]="target"; st.rerun()
    if c2.button("Go to Flash Bursts"):
        S["stage"]="flash"; st.rerun()

def page_flash():
    st.subheader("Flash bursts — quick coverage")
    st.caption("Open up to five flash profiles to broaden coverage beyond your live interviews.")
    opened=len(S["flash_open"])
    st.write(f"Opened: **{opened}/5**")
    cols=st.columns(3)
    for i,f in enumerate(FLASH_PERSONAS):
        with cols[i%3]:
            st.markdown(f"**{f['name']}**  \n_{f['segment']}_")
            st.caption(f"{f['bio']}")
            if i in S["flash_open"]:
                st.info(f["note"])
            else:
                if opened<5 and st.button("Open", key=f"f_{i}"):
                    S["flash_open"].append(i); st.rerun()
    if st.button("Run synthesis"):
        run_synthesis(); S["stage"]="synth"; st.rerun()

def page_synth():
    st.subheader("Synthesis sprint")
    a=S["analytics"]
    if not a:
        st.warning("No analytics yet. Run synthesis first.")
        return
    c1,c2=st.columns(2)
    with c1:
        st.markdown("**Top pain clusters (counts)**")
        for k,v in sorted(a["clusters"].items(), key=lambda kv: kv[1], reverse=True):
            st.write(f"- {k}: {v}")
        st.markdown("**Representative quotes**")
        for k,qs in a["quotes"].items():
            if qs:
                st.write(f"- *{k}*")
                for q in qs:
                    st.caption(f"“{q}”")
    with c2:
        st.markdown("**Coverage & bias**")
        segs=a["seg_mix"]
        if segs:
            st.write("Segments interviewed: " + ", ".join([f"{k} ({v})" for k,v in segs.items()]))
        else:
            st.write("No interviews recorded.")
        if a["bias_flag"]:
            st.warning(f"Channel bias detected — heavy reliance on {a['top_channel']}.")
        else:
            st.success("Channel mix looks balanced.")
    if st.button("Next: Decide & draft"):
        S["stage"]="draft"; st.rerun()

def page_draft():
    st.subheader("Decide & draft")
    st.caption("Fill the fields below — we’ll auto-compose a Problem Hypothesis and a Next Test Plan. You can edit the generated text before submitting.")
    ds=S["draft_struct"]
    col1,col2=st.columns(2)
    with col1:
        ds["who"]=st.selectbox("Customer segment", ["Homeowner","Renter","Landlord","Installer"], index=["Homeowner","Renter","Landlord","Installer"].index(ds["who"]))
        ds["core_pain"]=st.text_input("Core pain (short)", value=ds["core_pain"])
        ds["trigger"]=st.text_input("When does it happen? (trigger)", value=ds["trigger"])
        ds["impact"]=st.text_input("Impact on life/business", value=ds["impact"])
        ds["workaround"]=st.text_input("Current workaround", value=ds["workaround"])
        ds["quantifier"]=st.text_input("Any numbers that quantify it", value=ds["quantifier"])
    with col2:
        ds["next_method"]=st.text_input("Next test method", value=ds["next_method"])
        ds["next_target"]=st.text_input("Success threshold (target)", value=ds["next_target"])

    # Compose drafts
    composed_hypo = (
        f"For {ds['who'].lower()}s, {ds['core_pain']} occurs around {ds['trigger']}, causing {ds['impact']}. "
        f"They currently {ds['workaround']}. We believe a retrofit that improves airflow/comfort would be valuable; "
        f"evidence so far suggests: {ds['quantifier']}."
    )
    composed_next = (
        f"Run a {ds['next_method']} targeting {ds['who'].lower()}s for 2–4 weeks. "
        f"Success if {ds['next_target']}."
    )

    st.markdown("**Generated Problem Hypothesis (editable)**")
    S["problem_text"] = st.text_area("Problem Hypothesis", value=S["problem_text"] or composed_hypo, height=110)
    st.markdown("**Generated Next Test Plan (editable)**")
    S["next_test_text"] = st.text_area("Next Test Plan", value=S["next_test_text"] or composed_next, height=100)

    can_submit = len(S["problem_text"].strip())>20 and len(S["next_test_text"].strip())>10
    if st.checkbox("I’m satisfied with my hypothesis and next test."):
        S["submitted_draft"]=True
    st.caption("You must submit before scoring. You can come back and edit later, but scoring unlocks only after submit.")
    if st.button("Submit"):
        if can_submit:
            run_synthesis()  # ensure latest analytics
            S["submitted_draft"]=True
            st.success("Submitted. You can now view Feedback & Score.")
        else:
            st.warning("Please complete both fields with sufficient detail before submitting.")
    st.divider()
    colA,colB=st.columns(2)
    if colA.button("Back to Synthesis"):
        S["stage"]="synth"; st.rerun()
    if colB.button("Go to Feedback & Score"):
        if S["submitted_draft"]:
            S["stage"]="score"; st.rerun()
        else:
            st.warning("Submit your hypothesis and next test first.")

def page_score():
    st.subheader("Feedback & score")
    if not S["submitted_draft"]:
        st.warning("Submit your hypothesis and next test before scoring.")
        return
    if not S.get("analytics"):
        run_synthesis()
    compute_score()
    sc=S["score"]
    st.metric("Total score", f"{sc['total']}/100")
    st.markdown("#### Components")
    for k,v in sc["components"].items():
        label = "Excellent" if v>=80 else ("Good" if v>=60 else "Needs work")
        st.write(f"- **{k}:** {v}/100 — {label}")
        st.caption(S["reasons"].get(k,""))

    st.markdown("#### Key lessons")
    st.write("- **When interviewing,** start broad and open; avoid leading or solution talk early.")
    st.write("- **For coverage,** balance channels and include multiple segments to reduce bias.")
    st.write("- **Detect signal** by quantifying pains (frequency, severity, or dollars) and citing verbatims.")
    st.write("- **Write problems** with a clear who, when, and impact; make them testable.")
    st.write("- **Design tests** with a crisp method and success threshold tied to the riskiest assumption.")

    st.markdown("#### Your decisions recap")
    with st.expander("Recruiting channels & allocation"):
        total=sum(S["alloc"].values())
        st.write(", ".join([f"{k}: {v}" for k,v in S["alloc"].items() if v>0]) or "None")
        st.caption(f"Total tokens: {total}/{EFFORT_TOKENS}")
    with st.expander("Booked personas & segments"):
        for pid in S["booked_ids"]:
            p=INTERVIEW_PERSONAS[pid]
            st.write(f"- {p['name']} — {p['segment']} | {p['bio']}")
    with st.expander("Your problem hypothesis & next test"):
        st.write(S["problem_text"])
        st.markdown("---")
        st.write(S["next_test_text"])

    c1,c2=st.columns(2)
    if c1.button("Restart simulation"):
        init_state(); st.rerun()
    if c2.button("Back to Decide & Draft"):
        S["stage"]="draft"; st.rerun()

# ---------- Router ----------
def main():
    header()
    if S["stage"]=="intro":   page_intro()
    elif S["stage"]=="target":page_target()
    elif S["stage"]=="live":  page_live()
    elif S["stage"]=="flash": page_flash()
    elif S["stage"]=="synth": page_synth()
    elif S["stage"]=="draft": page_draft()
    else:                     page_score()

main()
