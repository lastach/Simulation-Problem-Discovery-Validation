# Startup Simulation: Problem Discovery & Validation (Streamlit)
# --------------------------------------------------------------
# pip install -r requirements.txt
# streamlit run app.py
# --------------------------------------------------------------

import random, json
from copy import deepcopy
import streamlit as st
import streamlit.components.v1 as components

# optional plotting (so the app won’t crash if matplotlib isn’t ready yet)
try:
    import matplotlib.pyplot as plt
    import numpy as np
    _HAS_MPL = True
except Exception:
    _HAS_MPL = False

# ================== Market brief ==================
SEED_MARKET_BRIEF = (
    "Independent gym owners managing acquisition volatility, churn after promos, "
    "and admin overhead. Sub-segments used in this sim: Solo Studios and Multi-Site Gyms."
)

PAINS = {
    "cac_volatility": {"label": "Paid acquisition volatility"},
    "post_promo_churn": {"label": "Churn after intro promos"},
    "admin_overhead": {"label": "Admin/payroll overhead"},
    "scheduling_glitch": {"label": "Scheduling tool glitches"},
    "referral_stagnation": {"label": "Referral stagnation"},
}
SEG_LABEL = {"solo": "Solo Studio", "multi": "Multi-Site Gym"}

# ================== Personas ==================
def persona(pid, gym_name, owner, ptype, weekly_clients, staff_per, monthly_fee, known_for,
            pains, workarounds, tell, anecdotes):
    return {
        "pid": pid, "gym_name": gym_name, "owner": owner, "ptype": ptype,
        "weekly_clients": weekly_clients, "staff_per": staff_per,
        "monthly_fee": monthly_fee, "known_for": known_for,
        "pains": pains, "workarounds": workarounds, "tell_threshold": tell, "anecdotes": anecdotes
    }

def solo(budget=False, premium=False):
    if budget:   return random.randint(120,200), random.randint(2,4), random.choice([35,39,45]), "Budget-friendly"
    if premium:  return random.randint(160,240), random.randint(3,6), random.choice([99,119,129]), "Premium amenities"
    return random.randint(140,220), random.randint(2,5), random.choice([55,69,79]), "Great community"

def multi(budget=False, premium=False):
    if budget:   return random.randint(250,380), random.randint(8,12), random.choice([49,59,69]), "Value for money"
    if premium:  return random.randint(320,520), random.randint(12,18), random.choice([129,149,169]), "Premium programs"
    return random.randint(280,460), random.randint(10,16), random.choice([79,99,109]), "Well-rounded offering"

ANEC = [
    "Two weeks ago our ads spiked in cost; trial sign-ups halved.",
    "We phone bank to fill empty classes when campaigns dip.",
    "Payroll takes longer than planned—CSV exports every Friday.",
    "Intro offer folks vanish unless we personally check in.",
    "Calendar double-books at peak once in a while.",
]

# Build the roster ONCE; we’ll freeze it in session_state to prevent changes on rerun.
def build_personas():
    P = []
    # 8 solo
    P += [
        persona("p1","Sunrise Yoga","Lena Park","solo", *solo(budget=True),
                {"cac_volatility":0.5,"post_promo_churn":0.7,"admin_overhead":0.4},
                {"post_promo_churn":"owner texts trial members"}, 0.50,[ANEC[3],ANEC[2]]),
        persona("p2","Steel City Strength","Marco Diaz","solo", *solo(),
                {"cac_volatility":0.8,"admin_overhead":0.3},
                {"cac_volatility":"flash discounts; IG reels"}, 0.55,[ANEC[0],ANEC[1]]),
        persona("p3","Harbor Pilates","Rina Ahmed","solo", *solo(premium=True),
                {"post_promo_churn":0.6,"referral_stagnation":0.5},
                {"referral_stagnation":"partner spa referrals"}, 0.60,[ANEC[3]]),
        persona("p4","North Loop Boxing","Caleb Brooks","solo", *solo(),
                {"cac_volatility":0.7,"scheduling_glitch":0.3},
                {"cac_volatility":"owner DM’s past members"}, 0.55,[ANEC[0],ANEC[4]]),
        persona("p5","Greenpoint Climb","Yara Cohen","solo", *solo(premium=True),
                {"admin_overhead":0.6,"referral_stagnation":0.4},
                {"admin_overhead":"manual payroll CSV"}, 0.65,[ANEC[2]]),
        persona("p6","Southside Spin","Owen Kelly","solo", *solo(budget=True),
                {"post_promo_churn":0.8,"cac_volatility":0.5},
                {"post_promo_churn":"staff follow-up calls"}, 0.55,[ANEC[3]]),
        persona("p7","Peak Performance Studio","Daria Novak","solo", *solo(),
                {"referral_stagnation":0.7,"admin_overhead":0.4},
                {"referral_stagnation":"script ask after sessions"}, 0.60,[ANEC[2]]),
        persona("p8","Riverfront Barre","Maya Chen","solo", *solo(premium=True),
                {"scheduling_glitch":0.4,"cac_volatility":0.6},
                {"scheduling_glitch":"manual adjustments"}, 0.55,[ANEC[4]]),
    ]
    # 4 multi
    P += [
        persona("p9","Core Collective","Nate Wallace","multi", *multi(),
                {"cac_volatility":1.0,"admin_overhead":0.5},
                {"cac_volatility":"pause spend + phone outreach"}, 0.55,[ANEC[0],ANEC[1]]),
        persona("p10","MetroFit","Aisha Goyal","multi", *multi(premium=True),
                {"cac_volatility":0.9,"post_promo_churn":0.6},
                {"post_promo_churn":"tiered offers; coach callbacks"}, 0.60,[ANEC[0],ANEC[3]]),
        persona("p11","Titan Athletics","Gabe Ortiz","multi", *multi(budget=True),
                {"admin_overhead":0.7,"scheduling_glitch":0.4},
                {"admin_overhead":"ops spreadsheets each Thursday"}, 0.60,[ANEC[2],ANEC[4]]),
        persona("p12","Northside Strength","Priya Patel","multi", *multi(),
                {"referral_stagnation":0.7,"cac_volatility":0.6},
                {"referral_stagnation":"partner network push"}, 0.60,[ANEC[0]])
    ]
    return P

# ================== Flash items (12, with metrics + pain_key) ==================
def build_flash():
    return [
        {"title":"Core Collective — Multi-Site Gym","ptype":"multi","weekly":360,"staff":14,"fee":99,
         "status":"Revenue steady; CPC spikes create mid-week dips.","challenges":"Volatile paid acquisition","pain_key":"cac_volatility"},
        {"title":"Sunrise Yoga — Solo Studio","ptype":"solo","weekly":170,"staff":3,"fee":39,
         "status":"Intro offers convert inconsistently.","challenges":"Churn after promos","pain_key":"post_promo_churn"},
        {"title":"Harbor Pilates — Solo Studio","ptype":"solo","weekly":210,"staff":4,"fee":119,
         "status":"Partner spa changed owners; referrals slowed.","challenges":"Referral stagnation","pain_key":"referral_stagnation"},
        {"title":"MetroFit — Multi-Site Gym","ptype":"multi","weekly":420,"staff":16,"fee":149,
         "status":"CPC spikes reduce trial volume.","challenges":"Paid acquisition volatility","pain_key":"cac_volatility"},
        {"title":"Southside Spin — Solo Studio","ptype":"solo","weekly":160,"staff":3,"fee":45,
         "status":"Good trial volume; poor conversion to monthly.","challenges":"Churn after promos","pain_key":"post_promo_churn"},
        {"title":"Greenpoint Climb — Solo Studio","ptype":"solo","weekly":200,"staff":4,"fee":129,
         "status":"Owner fixes payroll with CSV exports.","challenges":"Admin overhead","pain_key":"admin_overhead"},
        {"title":"North Loop Boxing — Solo Studio","ptype":"solo","weekly":190,"staff":3,"fee":69,
         "status":"Occasional double-booking at peak.","challenges":"Scheduling glitches","pain_key":"scheduling_glitch"},
        {"title":"Titan Athletics — Multi-Site Gym","ptype":"multi","weekly":320,"staff":12,"fee":59,
         "status":"Heavy spreadsheet workflows in ops.","challenges":"Admin overhead","pain_key":"admin_overhead"},
        {"title":"Peak Performance Studio — Solo Studio","ptype":"solo","weekly":180,"staff":3,"fee":79,
         "status":"Referrals plateauing this quarter.","challenges":"Referral stagnation","pain_key":"referral_stagnation"},
        {"title":"Riverfront Barre — Solo Studio","ptype":"solo","weekly":230,"staff":5,"fee":119,
         "status":"Calendar needs manual adjustments at peak.","challenges":"Scheduling glitches","pain_key":"scheduling_glitch"},
        {"title":"Northside Strength — Multi-Site Gym","ptype":"multi","weekly":380,"staff":15,"fee":109,
         "status":"Partner referrals inconsistent.","challenges":"Referral stagnation","pain_key":"referral_stagnation"},
        {"title":"Steel City Strength — Solo Studio","ptype":"solo","weekly":200,"staff":4,"fee":69,
         "status":"IG reels help but ads still fluctuate.","challenges":"Paid acquisition volatility","pain_key":"cac_volatility"},
    ]

# ================== Guided interview Q&A ==================
STARTERS = [
    ("typical_day","Walk me through a typical day."),
    ("biggest_challenges","What are some of your biggest challenges?"),
    ("new_clients_problem","Do you have a problem getting new clients?"),
    ("staff_happy","Is your staff happy?"),
    ("brand_image_problem","Do you have a problem with brand image?"),
]
FOLLOWUPS = [
    ("pricing_happy","Are customers happy with your pricing?"),
    ("acquisition_channels","How do you go about acquiring customers?"),
    ("loyal_customers","Tell me about your most loyal customers."),
    ("growth_constraints","What is keeping you from being able to grow to double or triple your current size?"),
    ("use_social_media","Do you use social media?"),
]

# Persona-specific answer bank returns text AND the dominant pain_key for synthesis.
def answers_for(p):
    seg = p["ptype"]
    premium = p["monthly_fee"] >= 100 or "Premium" in p["known_for"]
    budget = p["monthly_fee"] <= 60 or "Budget" in p["known_for"]
    A = {}
    A["typical_day"] = ("I’m in by 6am to review rosters, coach mornings, then admin and staff check-ins. "
                        "Evenings are peak classes."), None
    A["biggest_challenges"] = (
        ("Keeping classes full mid-week while not drowning in admin.") if seg=="multi"
        else ("Balancing coaching with manual follow-ups and payroll.")
    ), ("cac_volatility" if seg=="multi" else "post_promo_churn")
    A["new_clients_problem"] = (
        ("When ad costs spike, trials dip; we scramble with outreach.") if seg=="multi"
        else ("Some months yes—ads get pricey and word-of-mouth stalls.")
    ), "cac_volatility"
    A["staff_happy"] = (
        ("Generally yes, but schedule changes at peak frustrate coaches.") if seg=="multi"
        else ("They like the community; paperwork and last-minute changes annoy them.")
    ), ("scheduling_glitch" if seg=="multi" else "admin_overhead")
    A["brand_image_problem"] = (
        ("Not really—we’re known for programs and coaching quality.") if premium
        else ("Brand is fine and friendly; resources are tight.")
    ), None
    A["pricing_happy"] = (
        ("Premium members expect more touches; most are fine, newcomers push back.") if premium
        else ("Price sensitive crowd—discounts help, but churn rises afterward.")
    ), ("post_promo_churn" if not premium else None)
    A["acquisition_channels"] = (
        ("Paid social, search, partnerships; email list for promos.") if seg=="multi"
        else ("Instagram reels, local groups, and referral cards.")
    ), "cac_volatility"
    A["loyal_customers"] = (
        ("Long-time members who book coach-led programs; they refer friends.") if seg=="multi"
        else ("Regulars who love the vibe; they bring friends and buy packs.")
    ), "referral_stagnation"
    A["growth_constraints"] = (
        ("Predictable demand and coach capacity; ads volatility.") if seg=="multi"
        else ("Owner capacity and inconsistent trial-to-paid conversion.")
    ), ("cac_volatility" if seg=="multi" else "post_promo_churn")
    A["use_social_media"] = (
        ("Yes—IG/TikTok for highlights; LinkedIn for corporate wellness leads.") if seg=="multi"
        else ("Yes—Instagram mainly; TikTok experiments when there’s time.")
    ), None
    return A

# ================== Sim state & helpers ==================
def init_state():
    st.session_state.sim = {
        "started": False,
        "tokens": 10,
        "personas": build_personas(),      # frozen
        "flash": build_flash(),            # frozen
        "booked": [],
        "interviews": {},                  # pid -> {log:[{q,a,pain_key}], step:int, finished:bool, asked:set, learnings:str, saved:bool}
        "coverage": {"channel_counts": {}},
        "flash_opened": [],
        "synthesis": None,
        "advance_to_live": False,
        "advance_to_score": False,
        "drafts": {"ph":"", "ntp":""}
    }

def get_persona(pid):
    return next(p for p in st.session_state.sim["personas"] if p["pid"]==pid)

def sample_by_allocation(allocation):
    draws = max(0, int(sum(allocation.values())))
    if draws == 0: return []
    seg_weight = {"solo":0.0,"multi":0.0}
    for ch,toks in allocation.items():
        if toks<=0: continue
        if ch=="email_list":  seg_weight["solo"] += 0.5*toks; seg_weight["multi"] += 0.5*toks
        if ch=="cold_dm":     seg_weight["solo"] += 0.6*toks; seg_weight["multi"] += 0.4*toks
        if ch=="forums":      seg_weight["solo"] += 0.7*toks; seg_weight["multi"] += 0.3*toks
        if ch=="sidewalk":    seg_weight["solo"] += 0.8*toks; seg_weight["multi"] += 0.2*toks
    if seg_weight["solo"]==0 and seg_weight["multi"]==0:
        seg_weight = {"solo":1.0,"multi":1.0}
    total = seg_weight["solo"] + seg_weight["multi"]
    p_solo, p_multi = seg_weight["solo"]/total, seg_weight["multi"]/total
    pool = st.session_state.sim["personas"][:]
    random.shuffle(pool)
    chosen = []
    for _ in range(min(8, draws)):
        seg_pick = "solo" if random.random()<p_solo else "multi"
        cand = [p for p in pool if p["ptype"]==seg_pick and p["pid"] not in chosen] or [p for p in pool if p["pid"] not in chosen]
        if not cand: break
        chosen.append(cand[0]["pid"])
    return chosen

def synthesis():
    S = st.session_state.sim
    counts, quotes, by_seg = {}, {}, {}
    # interviews
    for pid, rec in S["interviews"].items():
        seg = rec["persona"]["ptype"]
        by_seg[seg] = by_seg.get(seg,0)+1
        for turn in rec["log"]:
            pk = turn.get("pain_key")
            if not pk: continue
            counts[pk] = counts.get(pk,0)+1
            quotes.setdefault(pk, []).append(turn["a"])
    # flash
    for ftitle in S["flash_opened"]:
        f = next(x for x in S["flash"] if x["title"]==ftitle)
        pk = f["pain_key"]
        counts[pk] = counts.get(pk,0)+1
        quotes.setdefault(pk, []).append(f"{f['title']}: {f['challenges']}")
    # top list
    top = sorted(counts.keys(), key=lambda k: counts[k], reverse=True)[:5]
    # channel bias alert
    cc = S["coverage"]["channel_counts"]; total = sum(cc.values()) or 1
    alerts = [f"Over-reliance on {label} ({int(100*n/total)}%)"
              for (label,n) in [( "Email List",cc.get("email_list",0) ),
                                ( "Cold DMs",cc.get("cold_dm",0) ),
                                ( "Industry Forums",cc.get("forums",0) ),
                                ( "Sidewalk Intercepts",cc.get("sidewalk",0) )] if n/total>0.6]
    out = {"counts":counts, "quotes":{k:quotes.get(k,[])[:3] for k in top}, "top":top, "segments":by_seg, "alerts":alerts}
    S["synthesis"]=out
    return out

def quality_heuristics(ph_text, ntp_text, top_pain_label):
    # PH: reward clarity/length and mention of any pain keywords; bonus if aligned with top pain label words.
    L = len(ph_text.strip())
    has_pain_word = any(x in ph_text.lower() for x in ["problem","struggle","challenge","churn","acquisition","overhead","referral","schedule"])
    aligned = top_pain_label and any(w in ph_text.lower() for w in top_pain_label.lower().split())
    phq = 0.5
    phq += 0.2 if L >= 140 else (0.1 if L >= 80 else 0.0)
    phq += 0.15 if has_pain_word else 0.0
    phq += 0.15 if aligned else 0.0
    phq = min(1.0, max(0.0, phq))
    # NTP: look for assumption/method/metric/threshold hints (not strict wording)
    ntp_lower = ntp_text.lower()
    parts = sum([
        any(w in ntp_lower for w in ["assumption","bet","we believe"]),
        any(w in ntp_lower for w in ["method","run","concierge","pilot","ads"]),
        any(w in ntp_lower for w in ["metric","measure","kpi","conversion","variance","on-time"]),
        any(w in ntp_lower for w in ["threshold","target","success","goal"]),
    ])
    ntpq = 0.4 + 0.15*parts
    return min(1.0, ntpq), phq

def decide_and_score(ph, ntp):
    S = st.session_state.sim
    syn = S["synthesis"] or synthesis()
    true_top = "cac_volatility"
    chosen_top = syn["top"][0] if syn["top"] else None
    signal = 1.0 if chosen_top==true_top else (0.7 if true_top in syn["top"] else 0.3)
    total_qs = sum(len(r["log"]) for r in S["interviews"].values())
    craft = min(1.0, 0.35 + min(total_qs,10)/15)  # more thoughtful turns → better
    channels_used = len([1 for n in S["coverage"]["channel_counts"].values() if n>0])
    largest_share = max(S["coverage"]["channel_counts"].values() or [0])/(sum(S["coverage"]["channel_counts"].values()) or 1)
    coverage = 1.0 if (channels_used>=3 and largest_share<=0.6) else 0.6
    ntpq, phq = quality_heuristics(ph, ntp, PAINS.get(chosen_top,{"label":""})["label"] if chosen_top else "")
    score = round(100*(0.30*craft+0.15*coverage+0.30*signal+0.15*phq+0.10*ntpq))
    components = {
        "Interview Craft": craft,
        "Coverage": coverage,
        "Signal Detection": signal,
        "Problem Statement Quality": phq,
        "Next Test Plan": ntpq
    }
    explanations = {
        "Interview Craft": "Based on useful questions asked across interviews (more thoughtful turns increases this).",
        "Coverage": "Diverse channels reduce sampling bias; aim for ≥3 channels and avoid one source dominating.",
        "Signal Detection": "Whether the top issue you inferred matches the strongest signal in this market.",
        "Problem Statement Quality": "Assessed by clarity/length and alignment with pains you uncovered.",
        "Next Test Plan": "Credit for stating a bet, a concrete method, what you’ll measure, and a success target.",
    }
    return {"score":score,"components":components,"explanations":explanations,"chosen_top":chosen_top,"true_top":true_top}

# ================== Streamlit app ==================
st.set_page_config(page_title="Startup Simulation: Problem Discovery & Validation", page_icon="🧪", layout="wide")
if "sim" not in st.session_state: init_state()
S = st.session_state.sim

st.title("Startup Simulation: Problem Discovery & Validation")
tabs = st.tabs(["Intro","Target & Recruit","Live Interviews","Flash Bursts","Synthesis + Decide","Score"])

# ---- Intro (kept simple; no copy changes beyond original intent) ----
with tabs[0]:
    st.subheader("Welcome")
    st.markdown(
        """
**How this works**: Practice the discovery loop — **target → recruit → interview → synthesize → decide**.  
**Time**: ~75–90 minutes (solo).  
**What you’ll do**: allocate effort across channels, run short interviews, open flash profiles, synthesize, then draft a problem hypothesis and next test plan.  
**Goal**: Ask better questions, detect real signals, and choose an evidence-based next test.
        """
    )
    if not S["started"]:
        if st.button("Start Simulation"):
            S["started"] = True
            S["advance_to_live"] = False
            components.html("<script>setTimeout(()=>{const t=window.parent.document.querySelectorAll('button[role=tab]'); if(t[1]) t[1].click();},60)</script>", height=0)
            st.rerun()

# ---- Target & Recruit ----
with tabs[1]:
    if not S["started"]:
        st.info("Start on the Intro tab first.")
    else:
        st.subheader("Market Brief")
        st.info(SEED_MARKET_BRIEF)
        st.markdown(
            "**You have 10 effort tokens** to recruit across channels. "
            "Each channel differs in yield, bias, and speed. "
            "**Trade-off**: cover segments vs. depth. Avoid over-reliance on one source."
        )
        CHANNELS = {
            "email_list": "Email List",
            "cold_dm": "Cold DMs",
            "forums": "Industry Forums",
            "sidewalk": "Sidewalk Intercepts",
        }
        cols = st.columns(4)
        alloc = {}
        for i,ch in enumerate(["email_list","cold_dm","forums","sidewalk"]):
            with cols[i]:
                alloc[ch]=st.number_input(CHANNELS[ch],0,10,0,1
