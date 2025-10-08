# app_sim1.py
# Simulation #1 — Problem Discovery & Validation (ThermaLoop direction)
# Run: streamlit run app_sim1.py

import random
from copy import deepcopy
from typing import List, Dict, Any
import streamlit as st

random.seed(42)
st.set_page_config(page_title="Simulation #1 — Problem Discovery & Validation", page_icon="🎧", layout="wide")

TITLE = "Simulation #1 — Problem Discovery & Validation"
SUB   = "ThermaLoop: exploring home comfort and energy efficiency pains"

# ───────────────────────────────────────────────────────────────────────────────
# Seed market brief
# ───────────────────────────────────────────────────────────────────────────────
MARKET_BRIEF = (
    "Many homes have uneven temperatures and energy waste due to poor airflow balance. "
    "Homeowners report hot and cold rooms, high bills, and uncertainty about affordable fixes. "
    "Retrofits feel complex; installers vary in quality; comfort vs savings trade-offs are unclear."
)

# ───────────────────────────────────────────────────────────────────────────────
# Channels (no underscores). Each has yield, speed, and segment bias.
# bias weights: Homeowner, Renter, Landlord, Installer
# ───────────────────────────────────────────────────────────────────────────────
CHANNELS = {
    "Neighborhood Forums":  {"yield": 0.9, "speed": 0.8, "bias": {"Homeowner": 0.5, "Renter": 0.2, "Landlord": 0.2, "Installer": 0.1}},
    "Email Outreach":       {"yield": 0.7, "speed": 0.7, "bias": {"Homeowner": 0.3, "Renter": 0.3, "Landlord": 0.2, "Installer": 0.2}},
    "Cold Direct Messages": {"yield": 0.5, "speed": 0.6, "bias": {"Homeowner": 0.3, "Renter": 0.3, "Landlord": 0.2, "Installer": 0.2}},
    "Sidewalk Intercepts":  {"yield": 0.6, "speed": 0.9, "bias": {"Homeowner": 0.4, "Renter": 0.4, "Landlord": 0.1, "Installer": 0.1}},
    "Installer Referrals":  {"yield": 0.8, "speed": 0.5, "bias": {"Homeowner": 0.2, "Renter": 0.1, "Landlord": 0.2, "Installer": 0.5}},
}

EFFORT_TOKENS = 10

# ───────────────────────────────────────────────────────────────────────────────
# Personas (12 interview + 12 flash)
# Each persona: name, segment, bio, pains(list of dicts: text, freq 1-5, sev 1-5, material bool),
# triggers, workaround, wtp_ceiling (monthly or one-off sense), tell_threshold (0..1),
# anecdotes (list), quirks (small behavior)
# ───────────────────────────────────────────────────────────────────────────────

INTERVIEW_PERSONAS = [
    {
        "name":"Maya Chen", "segment":"Homeowner",
        "bio":"Owns a 3-bedroom townhouse; two kids; works hybrid; upstairs bedrooms run hot in summer.",
        "pains":[
            {"text":"Upstairs rooms much hotter than downstairs in summer", "freq":4, "sev":4, "material":True},
            {"text":"Energy bill spikes June–August", "freq":3, "sev":3, "material":True},
            {"text":"Confused by thermostat scheduling", "freq":3, "sev":2, "material":False},
        ],
        "triggers":["Heat waves; kids complaining at night"],
        "workaround":"Portable fans; closes downstairs vents by hand",
        "wtp_ceiling":15, "tell_threshold":0.55,
        "anecdotes":["We moved the kids downstairs to sleep last July."],
        "quirk":"Tracks bills in a spreadsheet"
    },
    {
        "name":"Sam Rodriguez", "segment":"Homeowner",
        "bio":"Single-family ranch; older HVAC; cares about comfort for elderly parent.",
        "pains":[
            {"text":"Cold draft in living room during winter", "freq":4, "sev":4, "material":True},
            {"text":"Noisy vents when furnace kicks in", "freq":2, "sev":2, "material":False},
        ],
        "triggers":["Cold snaps; parent visiting"],
        "workaround":"Space heater by sofa",
        "wtp_ceiling":10, "tell_threshold":0.6,
        "anecdotes":["We stuffed towels by the door last December."],
        "quirk":"DIY enthusiast"
    },
    {
        "name":"Aisha Patel", "segment":"Renter",
        "bio":"Top-floor apartment; can’t modify HVAC; pays electric; cares about bills.",
        "pains":[
            {"text":"Bedroom overheats; landlord slow to respond", "freq":4, "sev":4, "material":True},
            {"text":"Worried about high summer electric costs", "freq":3, "sev":3, "material":True},
        ],
        "triggers":["Heat waves; poor sleep"],
        "workaround":"Cracks window; box fan on high",
        "wtp_ceiling":8, "tell_threshold":0.5,
        "anecdotes":["I sleep with an ice pack sometimes."],
        "quirk":"Reads product reviews obsessively"
    },
    {
        "name":"Jordan Blake", "segment":"Landlord",
        "bio":"Manages 18 units across 3 buildings; fields comfort complaints.",
        "pains":[
            {"text":"Frequent tenant complaints about uneven heating", "freq":4, "sev":3, "material":True},
            {"text":"High maintenance calls in winter nights", "freq":3, "sev":3, "material":True},
        ],
        "triggers":["First cold snap; turnover season"],
        "workaround":"Tells tenants to adjust dampers; occasional duct cleaning",
        "wtp_ceiling":0, "tell_threshold":0.65,
        "anecdotes":["Three units called the same night last January."],
        "quirk":"Wants low-touch solutions"
    },
    {
        "name":"Riley Nguyen", "segment":"Installer",
        "bio":"Independent HVAC installer; busy spring/fall; skeptical of new gadgets.",
        "pains":[
            {"text":"Callbacks after installs due to comfort complaints", "freq":3, "sev":3, "material":True},
            {"text":"Customers want proofs of savings", "freq":3, "sev":3, "material":True},
        ],
        "triggers":["Season changes; equipment mismatch"],
        "workaround":"Manual damper balancing; upsell new thermostat",
        "wtp_ceiling":0, "tell_threshold":0.7,
        "anecdotes":["I’ve taped vents to force more air to back rooms."],
        "quirk":"Prefers proven gear"
    },
    {
        "name":"Priya Desai", "segment":"Homeowner",
        "bio":"Newer build; nursery runs cold at night; tech-friendly household.",
        "pains":[
            {"text":"Nursery too cold at night", "freq":4, "sev":4, "material":True},
            {"text":"Confusion over balancing multiple returns", "freq":2, "sev":2, "material":False},
        ],
        "triggers":["Baby waking; pediatrician advice"],
        "workaround":"Space heater on timer",
        "wtp_ceiling":18, "tell_threshold":0.55,
        "anecdotes":["We check room temp on a smart baby monitor."],
        "quirk":"Smart home early adopter"
    },
    {
        "name":"Marcus Lee", "segment":"Homeowner",
        "bio":"Old Victorian; leaky windows; budget-aware.",
        "pains":[
            {"text":"Heating bill too high for comfort achieved", "freq":4, "sev":4, "material":True},
            {"text":"Basement office stays cold", "freq":3, "sev":3, "material":True},
        ],
        "triggers":["Bill arrives; long work-from-home days"],
        "workaround":"Portable heater under desk; sweaters",
        "wtp_ceiling":12, "tell_threshold":0.6,
        "anecdotes":["I track the thermostat like a hawk in winter."],
        "quirk":"Likes numbers"
    },
    {
        "name":"Elena Rossi", "segment":"Renter",
        "bio":"Garden apartment; landlord controls boiler; cares about comfort more than cost.",
        "pains":[
            {"text":"Bedroom cold, living room warm", "freq":4, "sev":3, "material":True},
            {"text":"No control over thermostat", "freq":3, "sev":3, "material":True},
        ],
        "triggers":["Cold nights; exams week stress"],
        "workaround":"Heavy blanket; asks landlord monthly",
        "wtp_ceiling":5, "tell_threshold":0.5,
        "anecdotes":["Studying in a hoodie and gloves."],
        "quirk":"Time-pressed student"
    },
    {
        "name":"Derrick Owens", "segment":"Installer",
        "bio":"Regional installer; relationships with property managers; values upsells.",
        "pains":[
            {"text":"Wants upsell that reduces callbacks", "freq":3, "sev":3, "material":True},
        ],
        "triggers":["When tenants complain post-install"],
        "workaround":"Offer higher-end dampers; suggest room heaters",
        "wtp_ceiling":0, "tell_threshold":0.65,
        "anecdotes":["Callbacks kill our margins."],
        "quirk":"Sales-forward"
    },
    {
        "name":"Hannah Kim", "segment":"Homeowner",
        "bio":"Townhome; hosts often; wants quiet and comfort in guest room.",
        "pains":[
            {"text":"Guest room too hot; noisy vent", "freq":3, "sev":3, "material":True},
        ],
        "triggers":["When guests visit"],
        "workaround":"Close vent half-way; portable AC when desperate",
        "wtp_ceiling":9, "tell_threshold":0.55,
        "anecdotes":["We warn guests to bring a light blanket."],
        "quirk":"Aesthetic sensitive"
    },
    {
        "name":"Omar Farouk", "segment":"Landlord",
        "bio":"Owns 6 single-family rentals; wants fewer tenant calls.",
        "pains":[
            {"text":"Comfort complaints drive churn", "freq":3, "sev":3, "material":True},
        ],
        "triggers":["Renewal season; winter peaks"],
        "workaround":"Remind tenants to adjust vents; one-off fixes",
        "wtp_ceiling":0, "tell_threshold":0.6,
        "anecdotes":["A family left over heating issues."],
        "quirk":"Cost-focused"
    },
    {
        "name":"Zoey Park", "segment":"Homeowner",
        "bio":"Small bungalow; budget-constrained; cares about bills more than comfort.",
        "pains":[
            {"text":"Bill spikes after cold front", "freq":3, "sev":3, "material":True},
        ],
        "triggers":["Utility email; bill shock"],
        "workaround":"Lower thermostat; wear layers",
        "wtp_ceiling":6, "tell_threshold":0.5,
        "anecdotes":["I compare bills with neighbors."],
        "quirk":"Coupon clipper"
    },
]

FLASH_PERSONAS = [
    {
        "name":"Flash — Property Manager",
        "segment":"Landlord",
        "bio":"30 units across two 1970s buildings; central HVAC.",
        "note":"Tenant comfort tickets cluster after first cold week; balancing vents room-by-room is manual and slow."
    },
    {
        "name":"Flash — Parent of Infant",
        "segment":"Homeowner",
        "bio":"New baby; nursery temperature swings at night.",
        "note":"Tried tape-over vent and space heater; worried about safety and bills."
    },
    {
        "name":"Flash — Student Renter",
        "segment":"Renter",
        "bio":"Basement room; landlord controls temperature.",
        "note":"Studies in living room for warmth; pays electric for space heater."
    },
    {
        "name":"Flash — Retiree",
        "segment":"Homeowner",
        "bio":"On fixed income; values bill predictability.",
        "note":"Wants proof that a retrofit will pay back within a year."
    },
    {
        "name":"Flash — Short-Term Rental Host",
        "segment":"Landlord",
        "bio":"Hosts year-round; reviews mention comfort.",
        "note":"Would pay for something that reduces guest complaints."
    },
    {
        "name":"Flash — Installer Crew Lead",
        "segment":"Installer",
        "bio":"Trains techs; hates callbacks.",
        "note":"Wants simple add-on that reduces rework and has clear margin."
    },
    {
        "name":"Flash — Remote Worker",
        "segment":"Homeowner",
        "bio":"Works from a cold basement office.",
        "note":"Portable heater helps but hikes bill; wants smarter airflow."
    },
    {
        "name":"Flash — Eco Enthusiast",
        "segment":"Homeowner",
        "bio":"Solar + smart thermostat household.",
        "note":"Comfort is fine; wants measurable energy savings to justify add-ons."
    },
    {
        "name":"Flash — Building Superintendent",
        "segment":"Installer",
        "bio":"Oversees maintenance for a condo block.",
        "note":"Asks for clear install steps and warranty handling."
    },
    {
        "name":"Flash — Budget-Conscious Couple",
        "segment":"Homeowner",
        "bio":"Watching every expense this year.",
        "note":"Open to DIY if upfront cost under $150 and payback <12 months."
    },
    {
        "name":"Flash — Pet Owner",
        "segment":"Homeowner",
        "bio":"Dog sleeps in the warmest room.",
        "note":"Wants quieter airflow at night; noise matters."
    },
    {
        "name":"Flash — Tech Skeptic",
        "segment":"Homeowner",
        "bio":"Avoids ‘smart’ gadgets.",
        "note":"Needs a simple, non-intrusive device with tangible savings."
    },
]

# ───────────────────────────────────────────────────────────────────────────────
# Interview question set (clickable options). Mark open vs leading to drive trust.
# After each selection, remove that question from options for that persona.
# ───────────────────────────────────────────────────────────────────────────────
QUESTION_BANK = [
    {"key":"day_walk", "text":"Walk me through a typical day when the room feels uncomfortable.", "kind":"open"},
    {"key":"last_time", "text":"Tell me about the last time the temperature felt off. What happened?", "kind":"open"},
    {"key":"impact", "text":"What does this problem stop you from doing, or make harder?", "kind":"open"},
    {"key":"workarounds", "text":"What have you tried so far? How did it go?", "kind":"open"},
    {"key":"frequency", "text":"How often does this happen in a typical month?", "kind":"open"},
    {"key":"bill_spike", "text":"How did your bill change when this was worst?", "kind":"open"},
    {"key":"leading_buy", "text":"Would you buy a device to fix airflow if it was affordable?", "kind":"leading"},
    {"key":"leading_price", "text":"Would you pay ten dollars a month to control vents?", "kind":"leading"},
    {"key":"solutioning", "text":"What if I built smart vents you could control by phone?", "kind":"leading"},
]

# Persona-specific answer templates (by key). Open answers richer with higher trust.
# If not defined per persona, fall back to segment generic answers.
SEGMENT_ANSWERS = {
    "Homeowner": {
        "day_walk": "Mornings are fine, but by late afternoon the upstairs gets sticky. Bedtime is the worst in summer.",
        "last_time": "Last week during a warm spell, the nursery hit 79°F while downstairs was 72°F.",
        "impact": "Kids wake up, we move fans around, and everyone’s cranky the next day.",
        "workarounds": "We half-close some vents and run box fans; it helps a bit but feels hacky.",
        "frequency": "Maybe 8–12 times a month in summer.",
        "bill_spike": "Bills jump by about 20–25% in July and August.",
        "leading_buy": "Maybe, if it actually works and isn’t loud.",
        "leading_price": "Depends; ten dollars is okay if we see real comfort and savings.",
        "solutioning": "I’d need it to be simple and not ugly. What happens when it breaks?"
    },
    "Renter": {
        "day_walk": "I can’t change much; I open windows and use a fan. Nights are the worst.",
        "last_time": "Two nights ago, the bedroom was 78°F; landlord didn’t respond.",
        "impact": "Poor sleep, harder to focus; I work and study from home.",
        "workarounds": "Fan, window cracked, sometimes sleep on the couch.",
        "frequency": "5–10 nights a month in summer.",
        "bill_spike": "I notice the electric bill goes up $15–30 those months.",
        "leading_buy": "If it’s renter-friendly and I can take it when I move—maybe.",
        "leading_price": "Under ten dollars if it really helps.",
        "solutioning": "Landlord approval might be an issue—how would that work?"
    },
    "Landlord": {
        "day_walk": "I hear about it after the first cold week—phones light up.",
        "last_time": "Three units called on the same night; top-floor bedrooms too cold.",
        "impact": "Complaints, bad reviews, sometimes lost renewals.",
        "workarounds": "Tell tenants to adjust dampers, send techs to rebalance—costly.",
        "frequency": "Every season change, then a few times per month.",
        "bill_spike": "Maintenance overtime is the bigger spike than utilities.",
        "leading_buy": "If it cuts complaints without adding complexity, yes.",
        "leading_price": "Monthly per unit is tough; one-time per unit is easier to budget.",
        "solutioning": "I need clear install steps, durability, and warranty."
    },
    "Installer": {
        "day_walk": "Usually the return is far, or ducts are unbalanced after a renovation.",
        "last_time": "New furnace install—customer wanted back room warmer; had to revisit.",
        "impact": "Callbacks kill margins and schedule.",
        "workarounds": "Manual damper balancing; suggest better filters or a new thermostat.",
        "frequency": "Weekly during season changes.",
        "bill_spike": "Not my bill—but labor costs spike on rework.",
        "leading_buy": "If it’s reliable and upsell-ready, sure.",
        "leading_price": "Subscription is a hard sell—add-on kit pricing works.",
        "solutioning": "I’d need easy install and proof it won’t jam."
    }
}

# ───────────────────────────────────────────────────────────────────────────────
# State
# ───────────────────────────────────────────────────────────────────────────────
def init_state():
    st.session_state.s1 = {
        "stage":"intro",
        "tokens":EFFORT_TOKENS,
        "alloc":{k:0 for k in CHANNELS.keys()},
        "booked_ids":[],
        "interview_state":{},  # pid -> dict(question_keys_left, q_count, trust, transcript[list], tags[set])
        "flash_open":[],
        "codes":[],            # list of dict(tag, persona_or_flash, text)
        "analytics":{},        # computed in synthesis
        "problem_hypo":"",
        "next_test":"",
        "score":None,
        "reasons":{},
    }
if "s1" not in st.session_state:
    init_state()
S = st.session_state.s1

# Helpers
def clamp(x, lo, hi): return max(lo, min(hi, x))

def header():
    st.title(TITLE)
    st.caption(SUB)

# ───────────────────────────────────────────────────────────────────────────────
# Recruitment logic
# ───────────────────────────────────────────────────────────────────────────────
def recruit_personas(alloc: Dict[str,int], pool: List[Dict[str,Any]], need:int=6) -> List[int]:
    # Build weighted list by segment bias and yield
    weights = []
    for i,p in enumerate(pool):
        seg = p["segment"]
        # weight = sum over channels of (alloc * yield * bias[seg]) with randomness
        w = 0.0
        for ch, t in alloc.items():
            if t<=0: continue
            chp = CHANNELS[ch]
            w += t * chp["yield"] * chp["bias"].get(seg,0.1) * random.uniform(0.8,1.2)
        weights.append((i, w))
    # normalize & sample without replacement
    total = sum(max(0.0001,w) for _,w in weights)
    probs = [max(0.0001,w)/total for _,w in weights]
    # draw up to 'need' distinct ids by roulette wheel
    chosen = set()
    for _ in range(min(need, len(pool))):
        r = random.random()
        cum = 0
        for idx,(i,w) in enumerate(weights):
            cum += probs[idx]
            if r <= cum:
                chosen.add(i)
                break
    # if not enough variety, add randoms
    while len(chosen)<min(need, len(pool)):
        chosen.add(random.randrange(len(pool)))
    return list(chosen)

# ───────────────────────────────────────────────────────────────────────────────
# Interview engine
# ───────────────────────────────────────────────────────────────────────────────
def init_interview_state(pid:int):
    persona = INTERVIEW_PERSONAS[pid]
    # questions left = copy of keys; we'll display 3–5 at a time
    keys = [q["key"] for q in QUESTION_BANK]
    random.shuffle(keys)
    S["interview_state"][pid] = {
        "left": keys,
        "q_count": 0,
        "trust": 0.4 if persona["segment"] in ["Landlord","Installer"] else 0.5,
        "transcript": [],
        "asked": set(),
        "ended": False
    }

def answer_for(persona, qkey, trust):
    # Prefer persona-specific by segment
    seg_answers = SEGMENT_ANSWERS.get(persona["segment"], {})
    base = seg_answers.get(qkey, "Not sure.")
    # Enrich answer with disclosures gated by trust
    # When trust exceeds tell_threshold, include a material pain detail or WTP mention
    extra = ""
    if trust >= persona["tell_threshold"]:
        material = [p for p in persona["pains"] if p["material"]]
        if qkey in ["impact","workarounds","last_time"] and material:
            top = max(material, key=lambda p: p["sev"]+p["freq"])
            extra = f" Also, the key issue is: {top['text']}."
        if qkey in ["bill_spike","leading_price","leading_buy"] and persona["wtp_ceiling"]>0:
            extra += f" I could see up to around ${persona['wtp_ceiling']}/month if it truly helps."
    # Add mild noise/variation
    if random.random()<0.2:
        extra += " Honestly, it varies week to week."
    return base + ((" " + extra) if extra else "")

def classify_question(qkey)->str:
    kind = next(q["kind"] for q in QUESTION_BANK if q["key"]==qkey)
    return kind

def apply_trust(trust:float, q_kind:str)->float:
    if q_kind=="open":
        trust += 0.06
    else:
        trust -= 0.08
    return clamp(trust, 0.0, 1.0)

def selectable_questions(pid:int)->List[Dict[str,Any]]:
    stt = S["interview_state"][pid]
    # show up to 5 options from those left, prioritizing opens if trust is low
    left = [k for k in stt["left"] if k not in stt["asked"]]
    # map to objects
    opts = [q for q in QUESTION_BANK if q["key"] in left]
    # keep consistent order: open first
    opts.sort(key=lambda q: 0 if q["kind"]=="open" else 1)
    return opts[:5]

def record_qna(pid:int, qkey:str, qtext:str, atext:str):
    S["interview_state"][pid]["transcript"].append({"q":qtext, "a":atext})
    S["interview_state"][pid]["asked"].add(qkey)
    S["interview_state"][pid]["q_count"] += 1
    # simple inline capture for synthesis suggestions
    lower = (qtext + " " + atext).lower()
    tags = []
    for t in ["pain","workaround","trigger","frequency","cost","wtp","segment","severity"]:
        if t in lower:
            tags.append(t)
    for tg in tags:
        S["codes"].append({"tag":tg, "persona":INTERVIEW_PERSONAS[pid]["name"], "text":atext})

# ───────────────────────────────────────────────────────────────────────────────
# Analysis (Synthesis)
# ───────────────────────────────────────────────────────────────────────────────
def run_synthesis():
    # Count pains by cluster words from transcripts and flash notes
    pain_keywords = {
        "Hot room": ["hot", "overheat", "sticky"],
        "Cold room": ["cold", "draft", "chilly"],
        "High bill": ["bill", "cost", "expensive"],
        "No control": ["landlord", "no control", "cannot change"],
        "Noise": ["noisy", "loud", "vent noise"],
    }
    cluster_counts = {k:0 for k in pain_keywords}
    cluster_quotes = {k:[] for k in pain_keywords}
    # interviews
    for pid, stt in S["interview_state"].items():
        for turn in stt["transcript"]:
            txt = (turn["q"] + " " + turn["a"]).lower()
            for cluster, words in pain_keywords.items():
                if any(w in txt for w in words):
                    cluster_counts[cluster]+=1
                    if len(cluster_quotes[cluster])<3:
                        cluster_quotes[cluster].append(turn["a"])
    # flash
    for fidx in S["flash_open"]:
        f = FLASH_PERSONAS[fidx]
        txt = (f["bio"] + " " + f["note"]).lower()
        for cluster, words in pain_keywords.items():
            if any(w in txt for w in words):
                cluster_counts[cluster]+=1
                if len(cluster_quotes[cluster])<3:
                    cluster_quotes[cluster].append(f["note"])
    # Coverage / channel bias
    # approximate coverage by segments interviewed
    segs = []
    for pid in S["booked_ids"]:
        segs.append(INTERVIEW_PERSONAS[pid]["segment"])
    seg_mix = {s:segs.count(s) for s in set(segs)}
    top_ch = max(S["alloc"], key=lambda k:S["alloc"][k])
    total_alloc = sum(S["alloc"].values())
    bias_flag = (total_alloc>0 and S["alloc"][top_ch] > 0.6*total_alloc)
    S["analytics"] = {
        "clusters":cluster_counts,
        "quotes":cluster_quotes,
        "seg_mix":seg_mix,
        "bias_flag": bias_flag,
        "top_channel": top_ch
    }

# ───────────────────────────────────────────────────────────────────────────────
# Scoring
# ───────────────────────────────────────────────────────────────────────────────
def compute_score():
    # Interview craft
    total_q=0; open_q=0; leading_q=0; avg_trust=0; sessions=0
    for pid, stt in S["interview_state"].items():
        if stt["q_count"]==0: continue
        sessions+=1
    # We infer open vs leading from asked keys
    for pid, stt in S["interview_state"].items():
        for t in stt["transcript"]:
            total_q+=1
            # find kind by matching text back to bank (simple match)
            kind="open"
            for q in QUESTION_BANK:
                if q["text"]==t["q"]:
                    kind=q["kind"]
                    break
            if kind=="open": open_q+=1
            else: leading_q+=1
        avg_trust += stt["trust"]
    avg_trust = (avg_trust/max(1,sessions)) if sessions>0 else 0
    craft_score = 0
    if total_q>0:
        open_pct = open_q/total_q
        lead_pct = leading_q/total_q
        craft = 0.5*min(1.0, open_pct/0.7) + 0.3*max(0, 1 - max(0, (lead_pct-0.15)/0.85)) + 0.2*min(1.0, avg_trust/0.6)
        craft_score = round(100*craft)

    # Coverage
    seg_div = len(S["analytics"].get("seg_mix",{}))
    channel_ok = 0 if not S["analytics"] else (0 if S["analytics"]["bias_flag"] else 1)
    coverage = clamp((0.6 if seg_div>=3 else 0.35 if seg_div==2 else 0.15) + (0.4*channel_ok),0,1)
    coverage_score = round(100*coverage)

    # Signal detection: top cluster plausibility — pick most frequent cluster from synthesis and compare with learner statement
    clusters = S["analytics"]["clusters"]
    top_cluster = max(clusters, key=lambda k:clusters[k]) if clusters else None
    learner = S["problem_hypo"].lower()
    aligned = 1 if (top_cluster and any(w in learner for w in top_cluster.lower().split())) else 0
    quantified = 1 if any(x in learner for x in ["%", " times", " per ", " degree", "$"]) else 0
    detection = clamp(0.6*aligned + 0.4*quantified, 0, 1)
    detection_score = round(100*detection)

    # Problem statement quality
    quality = 0
    if len(S["problem_hypo"].strip())>20:
        includes_who = any(s in S["problem_hypo"].lower() for s in ["homeowner","renter","landlord","installer"])
        includes_trigger = any(s in S["problem_hypo"].lower() for s in ["heat", "cold", "bill", "complain", "night", "summer", "winter"])
        testable = any(s in S["problem_hypo"].lower() for s in ["measure","within","increase","reduce","by "])
        quality = clamp(0.35*includes_who + 0.35*includes_trigger + 0.3*testable, 0, 1)
    problem_score = round(100*quality)

    # Next test plan
    nxt = S["next_test"].lower()
    has_method = any(s in nxt for s in ["landing", "preorder", "pilot", "trial", "survey", "interview", "prototype", "a/b"])
    has_threshold = any(x in nxt for x in ["target", ">=", "<=", "%", " signups", " conversions", " complaints"])
    next_score = round(100*clamp(0.5*has_method + 0.5*has_threshold, 0, 1))

    # Weighted total
    total = round(0.30*craft_score + 0.15*coverage_score + 0.30*detection_score + 0.15*problem_score + 0.10*next_score)

    # Reasons
    reasons = {
        "Interview Craft": f"Open questions {int((open_q/max(1,total_q))*100)}%, leading {int((leading_q/max(1,total_q))*100)}%, average trust {S['interview_state'][S['booked_ids'][0]]['trust'] if S['booked_ids'] else 0:.2f} (target: ≥70% open, ≤15% leading, trust ≥0.6).",
        "Coverage": f"Segments covered: {', '.join(S['analytics'].get('seg_mix',{}).keys()) or 'none'}. Channel bias: {'high' if S['analytics'].get('bias_flag') else 'balanced'}.",
        "Signal Detection": f"Your hypothesis aligned with top cluster '{top_cluster}' — {'yes' if aligned else 'no'}; quantification present — {'yes' if quantified else 'no'}.",
        "Problem Statement": "Checked for specific who, triggers, and testable phrasing.",
        "Next Test Plan": "Checked for clear method and success threshold."
    }

    S["score"] = {
        "total": total,
        "components": {
            "Interview Craft": craft_score,
            "Coverage": coverage_score,
            "Signal Detection": detection_score,
            "Problem Statement Quality": problem_score,
            "Next Test Plan": next_score
        }
    }
    S["reasons"] = reasons

# ───────────────────────────────────────────────────────────────────────────────
# UI Pages
# ───────────────────────────────────────────────────────────────────────────────
def page_intro():
    st.subheader("Welcome")
    st.markdown(f"**Market brief:** {MARKET_BRIEF}")
    st.markdown("""
**What you will do (75–90 min):**  
1) Pick a target and recruit interviewees.  
2) Conduct short live interviews (branching questions).  
3) Open flash snippets to broaden coverage.  
4) Tag and synthesize patterns.  
5) Draft a problem hypothesis and next test.  
6) Get feedback and a score.
""")
    if st.button("Start simulation"):
        S["stage"]="target"; st.rerun()

def page_target():
    st.subheader("Define target and choose channels")
    st.info("Allocate 10 effort tokens across outreach channels. Each channel varies in yield, speed, and who you’ll reach.")
    left, right = st.columns([2,1])
    total = 0
    with left:
        for ch in CHANNELS.keys():
            S["alloc"][ch] = st.slider(ch, 0, 5, S["alloc"][ch])
            total += S["alloc"][ch]
    with right:
        st.metric("Tokens allocated", f"{total}/{EFFORT_TOKENS}")
        st.caption("Tip: Balance channels to reduce sampling bias. Forums skew to power users; intercepts skew local; installer referrals reach pros.")
    if total>EFFORT_TOKENS:
        st.error("You allocated more than 10 tokens. Reduce some sliders.")
    if st.button("Book personas"):
        if total<=EFFORT_TOKENS:
            S["booked_ids"] = recruit_personas(S["alloc"], INTERVIEW_PERSONAS, need=6)
            # initialize interview state
            S["interview_state"].clear()
            for pid in S["booked_ids"]:
                init_interview_state(pid)
            S["stage"]="live"; st.rerun()
        else:
            st.warning("Fix token allocation before booking.")

def render_booked_sidebar():
    st.markdown("### Booked personas")
    for pid in S["booked_ids"]:
        p = INTERVIEW_PERSONAS[pid]
        st.markdown(f"- **{p['name']}** — {p['segment']}  \n  _{p['bio']}_")

def page_live():
    st.subheader("Live interviews")
    st.caption("Pick a persona and click questions. Open-ended questions build trust and reveal more signal. Avoid leading and solution talk early.")
    cols = st.columns([2,1])
    with cols[1]:
        render_booked_sidebar()
    with cols[0]:
        # choose persona to interview
        options = [f"{INTERVIEW_PERSONAS[pid]['name']} — {INTERVIEW_PERSONAS[pid]['segment']}" for pid in S["booked_ids"]]
        if not options:
            st.warning("No personas booked. Go back and recruit.")
            return
        choice = st.selectbox("Choose a persona to interview", options, index=0)
        pid = S["booked_ids"][options.index(choice)]
        p = INTERVIEW_PERSONAS[pid]
        st.write(f"**Bio:** {p['bio']}")
        st.write(f"**Known workaround:** {p['workaround']}")
        st.divider()

        stt = S["interview_state"][pid]
        if not stt["ended"]:
            # show 3–5 clickable questions
            qopts = selectable_questions(pid)
            btn_cols = st.columns(min(3, len(qopts)) or 1)
            # render buttons in rows of 3
            rows = [qopts[i:i+3] for i in range(0, len(qopts), 3)]
            for row in rows:
                rcols = st.columns(len(row))
                for i,q in enumerate(row):
                    if rcols[i].button(q["text"], key=f"q_{pid}_{q['key']}"):
                        q_kind = classify_question(q["key"])
                        prev_trust = stt["trust"]
                        stt["trust"] = apply_trust(prev_trust, q_kind)
                        ans = answer_for(p, q["key"], stt["trust"])
                        record_qna(pid, q["key"], q["text"], ans)
                        S["interview_state"][pid] = stt
                        st.rerun()

            # End interview button after 2 questions
            if stt["q_count"]>=2:
                if st.button("Thank and end interview"):
                    stt["ended"]=True
                    S["interview_state"][pid]=stt
                    st.rerun()
        else:
            st.success("Interview ended for this persona.")

        st.markdown("#### Transcript")
        if stt["transcript"]:
            for turn in stt["transcript"]:
                st.write(f"**You:** {turn['q']}")
                st.write(f"**{p['name']}:** {turn['a']}")
        else:
            st.caption("No questions asked yet.")

    c1, c2 = st.columns(2)
    if c1.button("Go to Flash Bursts"):
        S["stage"]="flash"; st.rerun()
    if c2.button("Back to channels"):
        S["stage"]="target"; st.rerun()

def page_flash():
    st.subheader("Flash bursts — quick coverage")
    st.caption("Open up to five flash profiles to broaden coverage beyond your live interviews.")
    opened = len(S["flash_open"])
    st.write(f"Opened: **{opened}/5**")
    cols = st.columns(3)
    for i,f in enumerate(FLASH_PERSONAS):
        with cols[i%3]:
            st.markdown(f"**{f['name']}**  \n_{f['segment']}_")
            st.caption(f"{f['bio']}")
            if i in S["flash_open"]:
                st.info(f["note"])
            else:
                if opened<5 and st.button("Open", key=f"f_{i}"):
                    S["flash_open"].append(i)
                    st.rerun()
    if st.button("Run synthesis"):
        run_synthesis()
        S["stage"]="synth"; st.rerun()

def page_synth():
    st.subheader("Synthesis sprint")
    a = S["analytics"]
    if not a:
        st.warning("No analytics yet. Run synthesis first from the previous step.")
        return
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Top pain clusters (counts)**")
        if a["clusters"]:
            items = sorted(a["clusters"].items(), key=lambda kv: kv[1], reverse=True)
            for k,v in items:
                st.write(f"- {k}: {v}")
        else:
            st.write("No data yet.")
        st.markdown("**Representative quotes**")
        for k,qs in a["quotes"].items():
            if qs:
                st.write(f"- *{k}*")
                for q in qs:
                    st.caption(f"“{q}”")
    with c2:
        st.markdown("**Coverage & bias**")
        segs = a["seg_mix"]
        if segs:
            st.write("Segments interviewed: " + ", ".join([f"{k} ({v})" for k,v in segs.items()]))
        else:
            st.write("No interviews recorded.")
        if a["bias_flag"]:
            st.warning(f"Channel bias detected — you relied heavily on {a['top_channel']}.")
        else:
            st.success("Channel mix looks balanced.")
    if st.button("Next: Decide and draft"):
        S["stage"]="draft"; st.rerun()

def page_draft():
    st.subheader("Decide and draft")
    st.caption("Write your Problem Hypothesis and Next Test Plan. Keep them specific and testable.")
    with st.expander("Example formats (generic, for inspiration)"):
        st.write("**Problem Hypothesis (example):**")
        st.caption("For [who], [pain] occurs [how often/when], causing [impact]. They currently [workaround]. A solution that [core outcome] would be valuable if it [threshold].")
        st.write("**Next Test Plan (example):**")
        st.caption("Run a [method] targeting [segment] for [duration]. Success if [metric] ≥ [target] (e.g., signups, replies, preorders, quotes).")
    S["problem_hypo"] = st.text_area("Problem Hypothesis", value=S["problem_hypo"], height=120, placeholder="Describe who, pain, triggers, impact, and why it matters.")
    S["next_test"]    = st.text_area("Next Test Plan", value=S["next_test"], height=100, placeholder="Describe the method, audience, and a clear success threshold.")
    proceed = st.selectbox("Decision", ["Proceed", "Narrow", "Pivot"], index=0)
    if st.button("Submit and score"):
        run_synthesis()
        compute_score()
        S["stage"]="score"; st.rerun()

def page_score():
    st.subheader("Feedback and score")
    sc = S["score"]
    if not sc:
        st.warning("No score yet.")
        return
    st.metric("Total score", f"{sc['total']}/100")
    st.markdown("#### Components")
    for k,v in sc["components"].items():
        label = "Excellent" if v>=80 else ("Good" if v>=60 else "Needs work")
        st.write(f"- **{k}:** {v}/100 — {label}")
        st.caption(S["reasons"].get(k,""))
    st.markdown("#### Key lessons")
    st.write("- **When interviewing,** favor open-ended, past-behavior questions; avoid leading or solution talk early.")
    st.write("- **For coverage,** balance channels and include at least three segments to reduce bias.")
    st.write("- **For signal detection,** quantify pains with frequency, severity, or dollar impact and cite real quotes.")
    st.write("- **In problem statements,** be specific about who and when the pain occurs; make it testable.")
    st.write("- **For next tests,** pick a scrappy method and a clear success threshold tied to the risk you’re reducing.")
    if st.button("Restart simulation"):
        init_state(); st.rerun()

# ───────────────────────────────────────────────────────────────────────────────
# Flow
# ───────────────────────────────────────────────────────────────────────────────
def main():
    header()
    stage = S["stage"]
    steps = ["intro","target","live","flash","synth","draft","score"]
    st.progress((steps.index(stage)+1)/len(steps))
    if stage=="intro":
        page_intro()
    elif stage=="target":
        page_target()
    elif stage=="live":
        page_live()
    elif stage=="flash":
        page_flash()
    elif stage=="synth":
        page_synth()
    elif stage=="draft":
        page_draft()
    else:
        page_score()

main()
