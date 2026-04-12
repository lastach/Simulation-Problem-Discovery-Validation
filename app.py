# app_sim1.py
# Problem Discovery & Validation (ThermaLoop)
# Run: streamlit run app_sim1.py

import random
from typing import Dict, Any, List
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Problem Discovery & Validation", page_icon="🎧", layout="wide")

TITLE = "Problem Discovery & Validation"
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
     "wtp_ceiling":0,"tell_threshold":0.7,"anecdotes":["I've taped vents to force more air to back rooms."],"quirk":"Prefers proven gear"},
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
    # --- Curveball personas: teach students to distinguish signal from noise ---
    {"name":"Trent Holloway","segment":"Homeowner","bio":"New construction; good insulation; loves gadgets.",
     "pains":[{"text":"Occasionally notices slight temp difference between floors","freq":1,"sev":1,"material":False}],
     "triggers":["Reading smart-home blogs"],"workaround":"None needed; house is comfortable",
     "wtp_ceiling":25,"tell_threshold":0.4,
     "anecdotes":["I saw a TikTok about smart vents and thought it looked cool."],
     "quirk":"Enthusiastic early adopter who says yes to everything but has no real pain"},
    {"name":"Debra Cassidy","segment":"Homeowner","bio":"Thinks she has airflow issues; actually has poor attic insulation.",
     "pains":[{"text":"Upstairs bedroom warm in summer","freq":4,"sev":4,"material":False}],
     "triggers":["Summer heat"],"workaround":"Window AC unit in bedroom",
     "wtp_ceiling":12,"tell_threshold":0.55,
     "anecdotes":["We had someone look at the ducts and they said everything was fine."],
     "quirk":"Misattributes insulation problem to airflow; duct inspection already cleared"},
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
    {"name":"Flash — Tech Skeptic","segment":"Homeowner","bio":"Avoids 'smart' gadgets.",
     "note":"Needs simple, non-intrusive device with tangible savings."},
]

# ---------- Segment-tailored question banks (open vs leading governs trust) ----------
# Each question has a short "label" for the button and "text" for the full question shown after selection
QB = {
    "Homeowner": [
        {"key":"habit_home","label":"Heating/cooling habits","text":"Tell me about your habits for heating and cooling your home.","kind":"open"},
        {"key":"starters1","label":"Walk through an uncomfortable day","text":"Walk me through a typical day when a room feels uncomfortable.","kind":"open"},
        {"key":"starters2","label":"Last time temp felt off","text":"Tell me about the last time the temperature felt off. What happened?","kind":"open"},
        {"key":"impact","label":"Impact on daily life","text":"What does this problem stop you from doing, or make harder?","kind":"open"},
        {"key":"workarounds","label":"What you've tried","text":"What have you tried so far? How did it go?","kind":"open"},
        {"key":"frequency","label":"How often it happens","text":"How often does this happen in a typical month?","kind":"open"},
        {"key":"bill","label":"Energy bill impact","text":"How did your energy bill change when this was worst?","kind":"open"},
        {"key":"priorities","label":"Top priority right now","text":"What matters most right now: saving energy, convenience, saving money, or home comfort?","kind":"open"},
        {"key":"leading_buy","label":"Would you buy a fix?","text":"Would you buy a device to fix airflow if it was affordable?","kind":"leading"},
        {"key":"solutioning","label":"What if: smart vents?","text":"What if I built smart vents you could control by phone?","kind":"leading"},
    ],
    "Renter": [
        {"key":"habit_renter","label":"Managing without control","text":"How do you manage heating and cooling when you can't change the system?","kind":"open"},
        {"key":"last_time","label":"Last uncomfortable night","text":"Tell me about the last night it was uncomfortable. What did you do?","kind":"open"},
        {"key":"impact","label":"Impact on sleep/work/bills","text":"How does this affect sleep, work, or bills?","kind":"open"},
        {"key":"workarounds","label":"Workarounds tried","text":"What workarounds have you tried?","kind":"open"},
        {"key":"frequency","label":"How often it happens","text":"How often does this happen in a month?","kind":"open"},
        {"key":"bill","label":"Bill changes from fans/heaters","text":"How does your electric bill change when you use heaters or fans?","kind":"open"},
        {"key":"priorities","label":"What matters most","text":"Which matters most: comfort, saving money, or convenience?","kind":"open"},
        {"key":"leading_buy","label":"Pay monthly for better airflow?","text":"If it were renter-friendly, would you pay monthly for better airflow?","kind":"leading"},
        {"key":"solutioning","label":"What if: clip-on vents + app?","text":"What if there were clip-on vents with an app?","kind":"leading"},
    ],
    "Landlord": [
        {"key":"habit_land","label":"Biggest HVAC frustrations","text":"What are your biggest frustrations with heating and cooling across units?","kind":"open"},
        {"key":"last_wave","label":"Last heat/cold wave calls","text":"Tell me about the last cold or heat wave. What calls came in?","kind":"open"},
        {"key":"impact","label":"Effect on renewals/reviews","text":"How do comfort complaints affect renewals or reviews?","kind":"open"},
        {"key":"ops","label":"Current balancing process","text":"How do you currently handle balancing and follow-ups?","kind":"open"},
        {"key":"frequency","label":"Ticket frequency per season","text":"How often do these tickets appear in a season?","kind":"open"},
        {"key":"costs","label":"Where costs spike","text":"Where do costs spike: labor, equipment, or damages?","kind":"open"},
        {"key":"priorities","label":"Top ops priority","text":"What's the top priority: fewer complaints, lower ops cost, or faster response?","kind":"open"},
        {"key":"leading_buy","label":"Pay per unit for a fix?","text":"Would you pay per unit for a retrofit that reduces complaints?","kind":"leading"},
        {"key":"solutioning","label":"What if: smart vents for techs?","text":"What if techs could clip on smart vents and see fewer callbacks?","kind":"leading"},
    ],
    "Installer": [
        {"key":"habit_inst","label":"Post-install complaint patterns","text":"What patterns do you see when customers complain about comfort after installs?","kind":"open"},
        {"key":"cases","label":"A recent revisit case","text":"Tell me about a recent case you had to revisit.","kind":"open"},
        {"key":"impact","label":"Callback impact on margins","text":"How do callbacks affect your schedule or margins?","kind":"open"},
        {"key":"methods","label":"Current diagnosis methods","text":"How do you currently balance airflow or diagnose issues?","kind":"open"},
        {"key":"frequency","label":"Revisit frequency","text":"How often are revisits needed during season changes?","kind":"open"},
        {"key":"proof","label":"Proof customers want","text":"What proof do customers ask for to believe improvements?","kind":"open"},
        {"key":"priorities","label":"Install vs reliability vs upsell","text":"What matters most: simple install, reliability, or upsell potential?","kind":"open"},
        {"key":"leading_buy","label":"Recommend a reliable add-on?","text":"Would you recommend an add-on if it's reliable and profitable?","kind":"leading"},
        {"key":"solutioning","label":"What if: auto-balancing kit?","text":"What if a kit made balancing automatic. Would that help?","kind":"leading"},
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
        "leading_buy":"Maybe, if it actually works and isn't loud.",
        "solutioning":"It'd have to be simple, quiet, and safe around kids."
    },
    "Renter": {
        "habit_renter":"I open windows, use a fan; landlord controls the boiler.",
        "last_time":"Two nights ago the bedroom was way too warm; I slept on the couch.",
        "impact":"Sleep suffers; studying is harder; bill creeps up with the fan.",
        "workarounds":"Fan, window, lighter bedding; landlord is slow.",
        "frequency":"5–10 nights a month in summer.",
        "bill":"Electric bill rises $15–30 those months.",
        "priorities":"Comfort, then cost; I can't change the system.",
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
        "solutioning":"Only if it won't jam and support is solid."
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
            "who":"",
            "core_pain":"",
            "trigger":"",
            "impact":"",
            "workaround":"",
            "quantifier":"",
            "next_method":"",
            "next_target":""
        },
        "chosen_segment": None,           # learner's chosen ICP for next step
        "chosen_pain": None,              # learner's chosen primary pain
        "decision": "Proceed",            # Proceed / Narrow / Pivot
        "problem_text":"",
        "next_test_text":"",
        "submitted_draft":False,
        "score":None,
        "reasons":{},
        # Active synthesis: student guesses before seeing data
        "synth_guess_top1": None,
        "synth_guess_top2": None,
        "synth_guess_submitted": False,
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
    current_idx = STAGES.index(S["stage"])
    cols = st.columns(len(STAGES))
    for i, key in enumerate(STAGES):
        label = LABELS[key]
        if i < current_idx:
            # Completed stage: clickable, checkmark
            if cols[i].button(f"✅ {label}", key=f"nav_{key}"):
                S["stage"] = key
                st.rerun()
        elif i == current_idx:
            # Current stage: highlighted
            cols[i].button(f"👉 {label}", key=f"nav_{key}", disabled=False)
        else:
            # Future stage: grayed out, not clickable
            cols[i].button(label, key=f"nav_{key}", disabled=True)

def compute_progress():
    """Compute actual progress (0.0 to 1.0) based on stage and within-stage completion."""
    stage_idx = STAGES.index(S["stage"])
    base = stage_idx / len(STAGES)
    step = 1.0 / len(STAGES)

    if S["stage"] == "intro":
        within = 0.5  # just viewing
    elif S["stage"] == "target":
        total_alloc = sum(S["alloc"].values())
        within = min(1.0, total_alloc / EFFORT_TOKENS)
    elif S["stage"] == "live":
        booked = len(S["booked_ids"])
        if booked == 0:
            within = 0.0
        else:
            done = sum(1 for pid in S["booked_ids"] if S["interview"].get(pid, {}).get("ended", False))
            within = done / booked
    elif S["stage"] == "flash":
        within = min(1.0, len(S["flash_open"]) / 5)
    elif S["stage"] == "synth":
        within = 1.0 if S.get("analytics") else 0.3
    elif S["stage"] == "draft":
        within = 1.0 if S.get("submitted_draft") else 0.5
    elif S["stage"] == "score":
        within = 1.0
    else:
        within = 0.0

    return min(1.0, base + within * step)

# ---------- Recruitment ----------
def recruit_personas(alloc: Dict[str,int], need:int=6) -> List[int]:
    # Seed based on allocation so results are stable across reruns with same inputs
    seed_val = hash(tuple(sorted(alloc.items())))
    rng = random.Random(seed_val)
    weights=[]
    for i,p in enumerate(INTERVIEW_PERSONAS):
        seg = p["segment"]
        w=0.0
        for ch, t in alloc.items():
            if t<=0: continue
            chp=CHANNELS[ch]
            w += t * chp["yield"] * chp["bias"].get(seg,0.1) * rng.uniform(0.85,1.15)
        weights.append((i, max(0.0001,w)))
    total = sum(w for _,w in weights)
    probs = [w/total for _,w in weights]
    chosen=set()
    attempts = 0
    while len(chosen)<min(need,len(INTERVIEW_PERSONAS)) and attempts < 100:
        r=rng.random(); cum=0
        for idx,(i,w) in enumerate(weights):
            cum += probs[idx]
            if r<=cum:
                chosen.add(i); break
        attempts += 1
    return list(chosen)

# ---------- Interview engine ----------
def init_interview(pid:int):
    p = INTERVIEW_PERSONAS[pid]
    if pid in S["interview"]: return
    keys = [q["key"] for q in QB[p["segment"]]]
    random.Random(pid).shuffle(keys)
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

# Persona-specific answer overrides for curveball personas
PERSONA_OVERRIDES = {
    "Trent Holloway": {
        "habit_home": "Honestly, our house stays pretty comfortable. The system is only two years old.",
        "starters1": "I don't really have uncomfortable days. Maybe once in a while I notice the upstairs is a degree or two warmer, but nothing serious.",
        "starters2": "I can't think of a specific time recently. It's more of a 'nice to have' optimization thing for me.",
        "impact": "It doesn't really stop me from doing anything. I just like the idea of having total control over every room.",
        "workarounds": "I haven't really needed to try anything. The house is fine.",
        "frequency": "Maybe once a month I notice something? It's really not frequent.",
        "bill": "Our bills are pretty normal. No big surprises.",
        "priorities": "Honestly, I just like cool tech. If it connects to my smart home setup, I'm interested.",
        "leading_buy": "Oh absolutely, I'd buy it. I love trying new smart home stuff. Take my money!",
        "solutioning": "Yes, that sounds amazing. When can I get one? Does it work with HomeKit?",
    },
    "Debra Cassidy": {
        "habit_home": "We run the AC hard in summer but the upstairs never really cools down properly.",
        "starters1": "By 3pm the master bedroom is noticeably warm. The AC is blasting but it's like the air isn't reaching up there.",
        "starters2": "Last July we had a week where the bedroom hit 82 even with the AC set to 72. We ended up sleeping downstairs.",
        "impact": "Sleep is terrible in summer. We fight about the thermostat constantly.",
        "workarounds": "We bought a window AC unit for the bedroom. It helps but it's loud and expensive to run.",
        "frequency": "Every day from June through September, really.",
        "bill": "Summer bills are brutal. Over $300 some months. The window unit alone adds probably $40-50.",
        "priorities": "Comfort upstairs. I just want the bedroom to be cool at night.",
        "leading_buy": "If it would actually fix the upstairs, yes. We already had a duct guy look at it and he said the ducts were fine though.",
        "solutioning": "Maybe? But we already had someone check the vents and they said airflow was normal. I'm not sure vents are the problem.",
    },
}

def answer_for(pid:int, qkey:str)->str:
    p = INTERVIEW_PERSONAS[pid]
    trust = S["interview"][pid]["trust"]

    # Check for persona-specific override first
    if p["name"] in PERSONA_OVERRIDES and qkey in PERSONA_OVERRIDES[p["name"]]:
        base = PERSONA_OVERRIDES[p["name"]][qkey]
    else:
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
    if hash(f"{pid}_{qkey}") % 5 == 0:
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
        "Hot room": ["hot", "overheat", "sticky", "warm", "hotter"],
        "Cold room": ["cold", "draft", "chilly", "freezing", "cool"],
        "High bill": ["bill", "cost", "expensive", "spike", "pric"],
        "No control": ["landlord", "no control", "cannot change", "slow to respond"],
        "Noise": ["noisy", "loud", "vent noise", "quiet"],
    }
    clusters = {k: 0 for k in pain_kw}
    quotes = {k: [] for k in pain_kw}

    # segment -> cluster counts
    segments = ["Homeowner", "Renter", "Landlord", "Installer"]
    seg_cluster = {seg: {c: 0 for c in pain_kw} for seg in segments}

    # interviews: aggregate, but weight by question depth
    # Deeper interviews (more questions) contribute more signal per cluster hit
    interviews_done = 0
    total_questions_asked = 0
    for pid, stt in S["interview"].items():
        if stt["q_count"] > 0:
            interviews_done += 1
            total_questions_asked += stt["q_count"]
        seg = INTERVIEW_PERSONAS[pid]["segment"]
        # Weight: interviews with more questions yield stronger signal
        depth_weight = min(2.0, 1.0 + (stt["q_count"] - MIN_QUESTIONS_PER_INTERVIEW) * 0.25)
        depth_weight = max(0.5, depth_weight)
        for t in stt["transcript"]:
            txt = (t["q"] + " " + t["a"]).lower()
            for c, words in pain_kw.items():
                if any(w in txt for w in words):
                    clusters[c] += depth_weight
                    seg_cluster[seg][c] += depth_weight
                    if len(quotes[c]) < 3:
                        quotes[c].append(t["a"])

        # Bonus: if trust was high enough to unlock material pains, count those
        p = INTERVIEW_PERSONAS[pid]
        if stt["trust"] >= p["tell_threshold"]:
            for pain in p["pains"]:
                if pain["material"]:
                    pain_text = pain["text"].lower()
                    for c, words in pain_kw.items():
                        if any(w in pain_text for w in words):
                            clusters[c] += pain["freq"] * 0.5  # frequency-weighted
                            seg_cluster[seg][c] += pain["freq"] * 0.5

    # Round cluster counts for display
    clusters = {k: round(v, 1) for k, v in clusters.items()}
    for seg in seg_cluster:
        seg_cluster[seg] = {c: round(v, 1) for c, v in seg_cluster[seg].items()}

    # flash bursts
    flash_count = len(S["flash_open"])
    for fidx in S["flash_open"]:
        f = FLASH_PERSONAS[fidx]
        txt = (f["bio"] + " " + f["note"]).lower()
        for c, words in pain_kw.items():
            if any(w in txt for w in words):
                clusters[c] += 1
                if len(quotes[c]) < 3:
                    quotes[c].append(f["note"])

    # coverage & bias
    segs = [INTERVIEW_PERSONAS[pid]["segment"] for pid in S["booked_ids"]]
    seg_mix = {s: segs.count(s) for s in set(segs)} if segs else {}

    total_alloc = sum(S["alloc"].values())
    top_ch = max(S["alloc"], key=lambda k: S["alloc"][k]) if total_alloc > 0 else None
    bias_flag = total_alloc > 0 and top_ch and S["alloc"][top_ch] > 0.6 * total_alloc

    S["analytics"] = {
        "clusters": clusters,
        "quotes": quotes,
        "seg_mix": seg_mix,
        "bias_flag": bias_flag,
        "top_channel": top_ch,
        "seg_cluster": seg_cluster,
        "interviews_done": interviews_done,
        "flash_count": flash_count,
        "total_questions": total_questions_asked,
    }

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
    seg_base = 0.7 if seg_div>=4 else 0.5 if seg_div>=3 else 0.2 if seg_div==2 else 0.1
    coverage = clamp(seg_base + 0.3*channel_ok, 0, 1)
    coverage_score=int(100*coverage)

    # detection (less brittle): match learner-picked primary pain against top-2 clusters;
    # use text only for extra credit if numbers present
    clusters = S["analytics"]["clusters"]
    top2 = sorted(clusters.items(), key=lambda kv: kv[1], reverse=True)[:2]
    top_names = [k for k,_ in top2]
    picked = S.get("chosen_pain")
    aligned = 1 if (picked in top_names) else 0
    hypo = S["problem_text"].lower()
    quantified = 1 if any(x in hypo for x in ["%", " times", " per ", " degree", "$"]) else 0
    detection = clamp(0.75*aligned + 0.25*quantified, 0, 1)
    detection = int(100*detection)

    # problem: check for specificity and grounding in interview data
    who_ok = any(s in hypo for s in ["homeowner","renter","landlord","installer"])
    trig_ok = any(s in hypo for s in ["heat","cold","bill","complain","night","summer","winter","season","spike","draft"])
    testable_ok = any(s in hypo for s in ["measure","within","increase","reduce","by ","per month","per week","times"])
    # Bonus: references specific personas, quotes, or interview findings
    quotes_all = S["analytics"].get("quotes", {})
    verbatim_refs = 0
    for cluster_quotes in quotes_all.values():
        for q in cluster_quotes:
            # Check if any meaningful phrase from a quote appears in the hypothesis
            words = [w for w in q.lower().split() if len(w) > 5]
            if any(w in hypo for w in words):
                verbatim_refs += 1
                break
    evidence_ok = 1 if verbatim_refs > 0 else 0
    # Length check: very short statements are likely low-effort
    length_ok = 1 if len(S["problem_text"].strip()) > 80 else 0.5
    problem=int(100*clamp(0.25*who_ok + 0.25*trig_ok + 0.2*testable_ok + 0.15*evidence_ok + 0.15*length_ok, 0, 1))

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
        "Signal Detection": f"Primary pain you chose: {picked or '—'}; top cluster(s): {', '.join(top_names) or '—'}; quantification: {'yes' if quantified else 'no'}.",
        "Problem Statement": "Checked for specific who, triggers, and testable phrasing.",
        "Next Test Plan": "Checked for clear method and a measurable threshold."
    }

# ---------- Header ----------
def header():
    st.title(TITLE)
    st.caption(SUB)
    st.markdown(f"**Market brief:** {MARKET_BRIEF}")
    stage_bar()
    st.progress(compute_progress())
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

MIN_QUESTIONS_PER_INTERVIEW = 4

def rapport_indicator(trust: float) -> str:
    """Return a visual rapport level based on trust score."""
    if trust >= 0.7:
        return "🟢 Strong rapport"
    elif trust >= 0.5:
        return "🟡 Building rapport"
    else:
        return "🔴 Low rapport"

def page_live():
    st.subheader("Live interviews")
    st.caption("Interview everyone you booked. Open questions build trust; leading or solution-focused questions can reduce it.")
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
        st.success("You've finished all booked interviews.")
        if st.button("Go to Flash Bursts"):
            S["stage"]="flash"; st.rerun()
        return

    pid = S["booked_ids"][idx]
    p = INTERVIEW_PERSONAS[pid]
    stt=S["interview"][pid]

    # Header with rapport indicator
    hcol1, hcol2 = st.columns([3, 1])
    with hcol1:
        st.markdown(f"### Interview {idx+1} of {len(S['booked_ids'])}: **{p['name']}** — {p['segment']}")
    with hcol2:
        st.markdown(f"**{rapport_indicator(stt['trust'])}**")

    st.write(f"**Bio:** {p['bio']}")
    st.write(f"**Known workaround:** {p['workaround']}")
    st.divider()

    if not stt["ended"]:
        # Show available questions with short labels; distinguish open vs leading
        opts = selectable(pid)
        st.markdown(f"**Choose your next question** ({stt['q_count']}/{MIN_QUESTIONS_PER_INTERVIEW} minimum)")
        for row in [opts[i:i+3] for i in range(0, len(opts), 3)]:
            cols = st.columns(len(row))
            for i,q in enumerate(row):
                # Leading questions get a subtle warning style via label
                btn_label = q["label"]
                if q["kind"] == "leading":
                    btn_label = f"⚠️ {btn_label}"
                if cols[i].button(btn_label, key=f"q_{pid}_{q['key']}", help=q["text"]):
                    ask(pid, q["key"], q["text"])
                    st.rerun()

        # Only allow ending after minimum questions
        if stt["q_count"] >= MIN_QUESTIONS_PER_INTERVIEW:
            if st.button("Thank and end interview"):
                stt["ended"]=True; S["interview"][pid]=stt; st.rerun()
        elif stt["q_count"] > 0:
            remaining = MIN_QUESTIONS_PER_INTERVIEW - stt["q_count"]
            st.caption(f"Ask at least {remaining} more question{'s' if remaining > 1 else ''} before ending this interview.")
    else:
        st.success("Interview ended for this persona.")
        if st.button("Next interview"):
            S["current_idx"] += 1
            st.rerun()

    st.markdown("#### Transcript")
    if stt["transcript"]:
        for turn in stt["transcript"]:
            kind_tag = " *(leading)*" if turn["kind"] == "leading" else ""
            st.write(f"**You:** {turn['q']}{kind_tag}")
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
    a = S["analytics"]
    if not a:
        st.warning("No analytics yet. Run synthesis first.")
        return

    cluster_names = list(a["clusters"].keys())

    # --- Phase 1: Student guesses before seeing data ---
    if not S["synth_guess_submitted"]:
        st.markdown("Before we show you the data, **what patterns did you notice?**")
        st.caption("Based on your interviews and flash bursts, which pain themes came up most? Pick your top two.")

        gc1, gc2 = st.columns(2)
        with gc1:
            S["synth_guess_top1"] = st.selectbox(
                "Strongest pain theme",
                cluster_names,
                index=cluster_names.index(S["synth_guess_top1"]) if S["synth_guess_top1"] in cluster_names else 0,
                key="guess_top1"
            )
        with gc2:
            remaining = [c for c in cluster_names if c != S["synth_guess_top1"]]
            S["synth_guess_top2"] = st.selectbox(
                "Second strongest pain theme",
                remaining,
                index=remaining.index(S["synth_guess_top2"]) if S["synth_guess_top2"] in remaining else 0,
                key="guess_top2"
            )

        st.caption("Once you submit your guesses, you'll see the actual data and how your intuition compared.")
        if st.button("Lock in my guesses and show data"):
            S["synth_guess_submitted"] = True
            st.rerun()
        return

    # --- Phase 2: Reveal data with comparison ---
    # Compare student guesses to actual top-2 clusters
    sorted_clusters = sorted(a["clusters"].items(), key=lambda kv: kv[1], reverse=True)
    actual_top2 = [k for k, _ in sorted_clusters[:2]]
    guess_top2 = [S["synth_guess_top1"], S["synth_guess_top2"]]

    match_count = len(set(guess_top2) & set(actual_top2))

    if match_count == 2:
        st.success("Your intuition matched the data perfectly. You identified both top pain clusters correctly.")
    elif match_count == 1:
        st.info(f"You got one right. You picked **{guess_top2[0]}** and **{guess_top2[1]}**; the data shows **{actual_top2[0]}** and **{actual_top2[1]}** as the strongest. Look at where the gap was and ask yourself what signals you might have over- or under-weighted.")
    else:
        st.warning(f"Your intuition diverged from the data. You picked **{guess_top2[0]}** and **{guess_top2[1]}**, but the data points to **{actual_top2[0]}** and **{actual_top2[1]}**. This is a valuable learning moment. Were you anchored by a vivid anecdote? Did you hear from a narrow set of segments?")

    st.divider()

    # Full data reveal
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Top pain clusters (signal strength)**")
        for k, v in sorted_clusters:
            marker = " **<< your pick**" if k in guess_top2 else ""
            st.write(f"- {k}: {v}{marker}")
        st.markdown("**Representative quotes**")
        for k, qs in a["quotes"].items():
            if qs:
                st.write(f"- *{k}*")
                for q in qs:
                    st.caption(f'"{q}"')

    with c2:
        st.markdown("**Coverage & bias**")
        st.write(f"Interviews completed: **{a.get('interviews_done', 0)}**")
        st.write(f"Flash bursts opened: **{a.get('flash_count', 0)}**")
        segs = a["seg_mix"]
        if segs:
            st.write("Segments interviewed: " + ", ".join([f"{k} ({v})" for k, v in segs.items()]))
        else:
            st.write("No interviews recorded.")
        if a["bias_flag"]:
            st.warning(f"Channel bias detected. Heavy reliance on {a['top_channel']}.")
        else:
            st.success("Channel mix looks balanced.")

        # Visualization: pains by customer segment
        st.markdown("**Pains by segment**")
        df = pd.DataFrame(a["seg_cluster"]).T  # rows=segments, cols=clusters
        st.bar_chart(df)

    st.divider()
    sc1, sc2 = st.columns(2)
    if sc1.button("Redo my guesses"):
        S["synth_guess_submitted"] = False
        st.rerun()
    if sc2.button("Next: Decide & draft"):
        S["stage"] = "draft"; st.rerun()

def page_draft():
    st.subheader("Decide & draft")
    st.caption("Pick your focus segment and primary pain, fill a few fields, and we'll compose a draft you can edit before submitting.")

    a = S.get("analytics", {})
    # Suggest segments seen; fall back to all
    seen_segments = list(a.get("seg_mix", {}).keys()) or ["Homeowner", "Renter", "Landlord", "Installer"]
    cluster_counts = a.get("clusters", {}) or {"Hot room":0,"Cold room":0,"High bill":0,"No control":0,"Noise":0}
    top2 = sorted(cluster_counts.items(), key=lambda kv: kv[1], reverse=True)[:2]
    suggested_pains = [k for k,_ in top2] or list(cluster_counts.keys())

    # Decisions
    dc1, dc2, dc3 = st.columns(3)
    with dc1:
        S["chosen_segment"] = st.selectbox("Choose your focus segment", seen_segments, index=0 if S["chosen_segment"] is None else seen_segments.index(S["chosen_segment"]))
    with dc2:
        S["chosen_pain"] = st.selectbox("Primary pain to address", suggested_pains, index=0 if (S["chosen_pain"] is None or S["chosen_pain"] not in suggested_pains) else suggested_pains.index(S["chosen_pain"]))
    with dc3:
        S["decision"] = st.selectbox("Decision", ["Proceed", "Narrow", "Pivot"], index=["Proceed","Narrow","Pivot"].index(S["decision"]))

    ds = S["draft_struct"]
    col1, col2 = st.columns(2)
    with col1:
        ds["core_pain"]  = st.text_input("Core pain (short)", value=ds.get("core_pain",""))
        ds["trigger"]    = st.text_input("When does it happen? (trigger)", value=ds.get("trigger",""))
        ds["impact"]     = st.text_input("Impact on life/business", value=ds.get("impact",""))
        ds["workaround"] = st.text_input("Current workaround", value=ds.get("workaround",""))
        ds["quantifier"] = st.text_input("Any numbers that quantify it", value=ds.get("quantifier",""))
    with col2:
        ds["next_method"] = st.text_input("Next test method", value=ds.get("next_method",""))
        ds["next_target"] = st.text_input("Success threshold (target)", value=ds.get("next_target",""))

    # Compose suggestions (not forced)
    suggested_hypo = (
        f"For {S['chosen_segment'].lower()}s, {ds['core_pain']} occurs around {ds['trigger']}, causing {ds['impact']}. "
        f"They currently {ds['workaround']}. Evidence so far: {ds['quantifier']}."
    ).strip()

    suggested_next = (
        f"Run a {ds['next_method']} targeting {S['chosen_segment'].lower()}s for 2–4 weeks. "
        f"Success if {ds['next_target']}."
    ).strip()

    st.markdown("**Problem Hypothesis (editable)**")
    S["problem_text"] = st.text_area("Problem Hypothesis", value=S["problem_text"] or suggested_hypo, height=110)
    st.markdown("**Next Test Plan (editable)**")
    S["next_test_text"] = st.text_area("Next Test Plan", value=S["next_test_text"] or suggested_next, height=100)

    # Require key structured fields to be filled
    struct_filled = all([
        ds.get("core_pain","").strip(),
        ds.get("trigger","").strip(),
        ds.get("impact","").strip(),
    ])
    can_submit = all([
        S["chosen_segment"],
        S["chosen_pain"],
        struct_filled,
        len(S["problem_text"].strip()) > 20,
        len(S["next_test_text"].strip()) > 10
    ])

    st.caption("You must submit before scoring.")
    if st.button("Submit"):
        if can_submit:
            run_synthesis()   # ensure analytics are fresh
            S["submitted_draft"] = True
            S["stage"] = "score"   # auto-advance after submit
            st.rerun()
        else:
            if not struct_filled:
                st.warning("Please fill in Core pain, Trigger, and Impact before submitting.")
            else:
                st.warning("Please choose a segment and pain, and write a problem hypothesis (>20 chars) and next test plan (>10 chars).")

    st.divider()
    colA, colB = st.columns(2)
    if colA.button("Back to Synthesis"):
        S["stage"] = "synth"; st.rerun()
    if colB.button("Go to Feedback & Score"):
        if S["submitted_draft"]:
            S["stage"] = "score"; st.rerun()
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

    st.markdown("#### Key lessons for you")
    comps = sc["components"]

    # Prioritize lessons based on weakest areas
    lessons = []
    if comps["Interview Craft"] < 60:
        lessons.append("**Interview craft needs work.** You used too many leading or solution-focused questions, which can bias responses and reduce trust. Next time, start broad and open; save solution ideas for later conversations.")
    elif comps["Interview Craft"] >= 80:
        lessons.append("**Strong interview technique.** You built good rapport with open-ended questions. Keep it up, and consider going even deeper on follow-up questions in future interviews.")

    if comps["Coverage"] < 60:
        lessons.append("**Coverage gaps detected.** Your channel allocation or persona mix was too narrow. Spread effort tokens across more channels and aim for at least 3 different segments to reduce sampling bias.")
    elif comps["Coverage"] >= 80:
        lessons.append("**Excellent coverage.** You reached a diverse set of personas across multiple segments. This gives you more confidence in the patterns you found.")

    if comps["Signal Detection"] < 60:
        lessons.append("**Signal detection needs sharpening.** The primary pain you identified didn't match the strongest patterns in your data. Review your interview transcripts for the most frequently mentioned and most severe issues.")
    elif comps["Signal Detection"] >= 80:
        lessons.append("**Sharp signal detection.** You correctly identified the dominant pain cluster from your interviews and backed it with numbers. This is what investors and mentors want to see.")

    if comps["Problem Statement Quality"] < 60:
        lessons.append("**Problem statement could be stronger.** A great problem statement names a specific who, describes the trigger, quantifies the impact, and is testable. Try referencing specific findings from your interviews.")
    elif comps["Problem Statement Quality"] >= 80:
        lessons.append("**Well-crafted problem statement.** You grounded it in a specific segment and trigger with testable language. This kind of clarity accelerates everything downstream.")

    if comps["Next Test Plan"] < 60:
        lessons.append("**Next test plan needs a method and threshold.** Specify what you'll do (landing page, prototype, survey, etc.) and what success looks like (a number). Without a measurable target, you can't tell if you passed.")

    # Always show at least 3 lessons
    if len(lessons) < 3:
        if "coverage" not in " ".join(lessons).lower():
            lessons.append("**For coverage,** balance channels and include multiple segments to reduce bias.")
        if "test" not in " ".join(lessons).lower():
            lessons.append("**Design tests** with a crisp method and success threshold tied to the riskiest assumption.")
        if "signal" not in " ".join(lessons).lower():
            lessons.append("**Detect signal** by quantifying pains (frequency, severity, or dollars) and citing verbatims.")

    for lesson in lessons[:5]:
        st.write(f"- {lesson}")

    # --- Channel-to-segment causality (#5) ---
    st.markdown("#### How your channels shaped your sample")
    st.caption("Each outreach channel reaches different customer segments at different rates. Here's what your token allocation produced:")

    # Build a channel -> segment reach matrix based on allocation and bias weights
    alloc = S["alloc"]
    ch_seg_data = {}
    for ch, tokens in alloc.items():
        if tokens > 0:
            bias = CHANNELS[ch]["bias"]
            ch_seg_data[ch] = {seg: round(tokens * weight, 1) for seg, weight in bias.items()}

    if ch_seg_data:
        import altair as alt
        df_ch = pd.DataFrame(ch_seg_data).T
        df_ch.index.name = "Channel"
        df_ch = df_ch.reset_index()
        df_melted = df_ch.melt(id_vars="Channel", var_name="Segment", value_name="Reach")
        _chart = alt.Chart(df_melted).mark_bar().encode(
            x=alt.X("Channel:N", axis=alt.Axis(labelAngle=-35, labelLimit=200), sort=None),
            y=alt.Y("Reach:Q", stack="zero"),
            color=alt.Color("Segment:N", scale=alt.Scale(
                domain=["Homeowner","Installer","Landlord","Renter"],
                range=["#1f77b4","#7fbbdb","#d62728","#f4a0a0"]
            )),
            tooltip=["Channel","Segment","Reach"]
        ).properties(height=350)
        st.altair_chart(_chart, use_container_width=True)

        # Highlight the lesson
        booked_segs = [INTERVIEW_PERSONAS[pid]["segment"] for pid in S["booked_ids"]]
        seg_counts = {s: booked_segs.count(s) for s in set(booked_segs)}
        missing_segs = [s for s in ["Homeowner", "Renter", "Landlord", "Installer"] if s not in seg_counts]
        if missing_segs:
            st.info(f"Your sample didn't include any **{', '.join(missing_segs)}** personas. "
                    f"To reach them, try allocating tokens to channels with higher reach into those segments.")
        else:
            st.success("Your sample covered all four segments. Strong diversity.")
    else:
        st.caption("No tokens were allocated.")

    st.divider()

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

    st.divider()

    # --- Discovery Brief export (#3) ---
    st.markdown("#### Your Discovery Brief")
    st.caption("A portable summary of your findings. Copy this or use it as input for the next simulation.")

    ds = S["draft_struct"]
    a = S.get("analytics", {})
    seg_mix = a.get("seg_mix", {})
    clusters = a.get("clusters", {})
    sorted_clusters = sorted(clusters.items(), key=lambda kv: kv[1], reverse=True)
    top_pains = ", ".join([f"{k} ({v})" for k, v in sorted_clusters[:3]]) if sorted_clusters else "None"
    booked_names = ", ".join([f"{INTERVIEW_PERSONAS[pid]['name']} ({INTERVIEW_PERSONAS[pid]['segment']})" for pid in S["booked_ids"]])

    # Collect top quotes, deduplicating by base answer (before "The key issue is:" suffix)
    import re as _re
    top_quotes = []
    _seen_bases = set()
    for _, qs in a.get("quotes", {}).items():
        for q in qs:
            base = _re.split(r"\s*The key issue is:", q)[0].strip()
            if base not in _seen_bases:
                _seen_bases.add(base)
                top_quotes.append(q)
            if len(top_quotes) >= 3:
                break
        if len(top_quotes) >= 3:
            break
    quotes_text = "\n".join([f'  - "{q}"' for q in top_quotes]) if top_quotes else "  - (none captured)"

    brief_text = f"""DISCOVERY BRIEF: ThermaLoop
{'='*40}

TARGET SEGMENT: {S.get('chosen_segment', '(not set)')}
PRIMARY PAIN: {S.get('chosen_pain', '(not set)')}
DECISION: {S.get('decision', 'Proceed')}

PROBLEM HYPOTHESIS:
{S['problem_text']}

EVIDENCE SUMMARY:
- Interviews conducted: {a.get('interviews_done', 0)}
- Flash bursts reviewed: {a.get('flash_count', 0)}
- Segments covered: {', '.join([f'{k} ({v})' for k, v in seg_mix.items()]) if seg_mix else 'None'}
- Top pain clusters: {top_pains}
- Key quotes:
{quotes_text}

NEXT TEST PLAN:
{S['next_test_text']}

STRUCTURED FIELDS:
- Core pain: {ds.get('core_pain', '')}
- Trigger: {ds.get('trigger', '')}
- Impact: {ds.get('impact', '')}
- Current workaround: {ds.get('workaround', '')}
- Quantification: {ds.get('quantifier', '')}
- Test method: {ds.get('next_method', '')}
- Success threshold: {ds.get('next_target', '')}

SCORE: {sc['total']}/100
{'='*40}
"""

    st.code(brief_text, language=None)
    st.download_button(
        label="Download Discovery Brief (.txt)",
        data=brief_text,
        file_name="discovery_brief_thermaloop.txt",
        mime="text/plain"
    )

    st.divider()

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
