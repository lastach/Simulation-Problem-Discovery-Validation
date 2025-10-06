# Startup Simulation: Problem Discovery & Validation (Streamlit)
# --------------------------------------------------------------
# pip install -r requirements.txt
# streamlit run app.py
# --------------------------------------------------------------

import random
from copy import deepcopy
import streamlit as st
import streamlit.components.v1 as components

# Optional plotting
try:
    import matplotlib.pyplot as plt
    import numpy as np
    _HAS_MPL = True
except Exception:
    _HAS_MPL = False

# Make sampling stable across reruns
random.seed(42)

# ================== Market brief ==================
SEED_MARKET_BRIEF = (
    "Independent gym owners managing acquisition volatility, churn after promos, "
    "and admin overhead. Sub-segments in this sim: Solo Studios and Multi-Site Gyms."
)

# pains (engine)
PAINS = {
    "cac_volatility": {"label": "Paid acquisition volatility"},
    "post_promo_churn": {"label": "Churn after intro promos"},
    "admin_overhead": {"label": "Admin and payroll overhead"},
    "scheduling_glitch": {"label": "Scheduling tool glitches"},
    "referral_stagnation": {"label": "Referral stagnation"},
}

SEG_LABEL = {"solo": "Solo Studio", "multi": "Multi-Site Gym"}

# ================== Personas ==================
def persona(pid, gym_name, owner, ptype, weekly_clients, staff_per, monthly_fee, known_for, pains, workarounds, tell, anecdotes):
    return {
        "pid": pid,
        "gym_name": gym_name,
        "owner": owner,
        "ptype": ptype,  # "solo" | "multi"
        "weekly_clients": weekly_clients,
        "staff_per": staff_per,
        "monthly_fee": monthly_fee,
        "known_for": known_for,
        "pains": pains,                 # weight map (0..1)
        "workarounds": workarounds,     # dict per pain
        "tell_threshold": tell,
        "anecdotes": anecdotes,
    }

def solo(budget=False, premium=False):
    if budget:
        return random.randint(120, 200), random.randint(2, 4), random.choice([35, 39, 45]), "Budget-friendly"
    if premium:
        return random.randint(160, 240), random.randint(3, 6), random.choice([99, 119, 129]), "Premium amenities"
    return random.randint(140, 220), random.randint(2, 5), random.choice([55, 69, 79]), "Great community"

def multi(budget=False, premium=False):
    if budget:
        return random.randint(250, 380), random.randint(8, 12), random.choice([49, 59, 69]), "Value for money"
    if premium:
        return random.randint(320, 520), random.randint(12, 18), random.choice([129, 149, 169]), "Premium programs"
    return random.randint(280, 460), random.randint(10, 16), random.choice([79, 99, 109]), "Well-rounded offering"

ANEC = [
    "Two weeks ago ads spiked; trial sign-ups halved.",
    "We phone bank to fill empty classes when campaigns dip.",
    "Payroll takes longer than planned—CSV exports each Friday.",
    "Intro offer folks vanish unless we personally check in.",
    "Calendar double-books at peak once in a while.",
]

PERSONAS = []
# 8 Solo
PERSONAS += [
    persona("p1","Sunrise Yoga","Lena Park","solo", *solo(budget=True),
            {"cac_volatility":0.5,"post_promo_churn":0.7,"admin_overhead":0.4},
            {"post_promo_churn":"Owner texts trial members"}, 0.50,[ANEC[3],ANEC[2]]),
    persona("p2","Steel City Strength","Marco Diaz","solo", *solo(),
            {"cac_volatility":0.8,"admin_overhead":0.3},
            {"cac_volatility":"Flash discounts; IG reels"}, 0.55,[ANEC[0],ANEC[1]]),
    persona("p3","Harbor Pilates","Rina Ahmed","solo", *solo(premium=True),
            {"post_promo_churn":0.6,"referral_stagnation":0.5},
            {"referral_stagnation":"Partner spa referrals"}, 0.60,[ANEC[3]]),
    persona("p4","North Loop Boxing","Caleb Brooks","solo", *solo(),
            {"cac_volatility":0.7,"scheduling_glitch":0.3},
            {"cac_volatility":"DMs to past members"}, 0.55,[ANEC[0],ANEC[4]]),
    persona("p5","Greenpoint Climb","Yara Cohen","solo", *solo(premium=True),
            {"admin_overhead":0.6,"referral_stagnation":0.4},
            {"admin_overhead":"Manual payroll CSV"}, 0.65,[ANEC[2]]),
    persona("p6","Southside Spin","Owen Kelly","solo", *solo(budget=True),
            {"post_promo_churn":0.8,"cac_volatility":0.5},
            {"post_promo_churn":"Staff follow-up calls"}, 0.55,[ANEC[3]]),
    persona("p7","Peak Performance PT","Daria Novak","solo", *solo(),
            {"referral_stagnation":0.7,"admin_overhead":0.4},
            {"referral_stagnation":"Scripted ask after sessions"}, 0.60,[ANEC[2]]),
    persona("p8","Riverfront Barre","Maya Chen","solo", *solo(premium=True),
            {"scheduling_glitch":0.4,"cac_volatility":0.6},
            {"scheduling_glitch":"Manual adjustments"}, 0.55,[ANEC[4]]),
]
# 4 Multi
PERSONAS += [
    persona("p9","Core Collective","Nate Wallace","multi", *multi(),
            {"cac_volatility":1.0,"admin_overhead":0.5},
            {"cac_volatility":"Pause spend + phone outreach"}, 0.55,[ANEC[0],ANEC[1]]),
    persona("p10","MetroFit","Aisha Goyal","multi", *multi(premium=True),
            {"cac_volatility":0.9,"post_promo_churn":0.6},
            {"post_promo_churn":"Tiered offers; coach callbacks"}, 0.60,[ANEC[0],ANEC[3]]),
    persona("p11","Titan Athletics","Gabe Ortiz","multi", *multi(budget=True),
            {"admin_overhead":0.7,"scheduling_glitch":0.4},
            {"admin_overhead":"Ops spreadsheets each Thursday"}, 0.60,[ANEC[2],ANEC[4]]),
    persona("p12","Northside Strength","Priya Patel","multi", *multi(),
            {"referral_stagnation":0.7,"cac_volatility":0.6},
            {"referral_stagnation":"Partner network push"}, 0.60,[ANEC[0]]),
]

# ================== Flash items (10) ==================
def flash_from_persona(p):
    primary = max(p["pains"], key=lambda k: p["pains"][k])
    status = {
        "cac_volatility": "Demand swings when ad costs spike.",
        "post_promo_churn": "Trial-to-paid conversion is inconsistent.",
        "admin_overhead": "Owner time drained by payroll/admin fixes.",
        "scheduling_glitch": "Occasional double-bookings at peak.",
        "referral_stagnation": "Referral partners cooled off this year."
    }[primary]
    challenges = {
        "cac_volatility": "Predictable lead flow; keep peak classes full.",
        "post_promo_churn": "Improve onboarding; retain beyond intro offers.",
        "admin_overhead": "Reduce manual ops; streamline payroll.",
        "scheduling_glitch": "Eliminate calendar glitches at peak.",
        "referral_stagnation": "Rebuild partner pipeline; boost referrals."
    }[primary]
    return {
        "title": f"{p['gym_name']} — {SEG_LABEL[p['ptype']]}",
        "ptype": SEG_LABEL[p["ptype"]],
        "weekly_clients": p["weekly_clients"],
        "staff_per": p["staff_per"],
        "monthly_fee": p["monthly_fee"],
        "known_for": p["known_for"],
        "status": status,
        "challenges": challenges,
        "primary_pain": primary
    }
FLASH_ITEMS = [flash_from_persona(p) for p in PERSONAS][:10]

# ================== Channels (with yield + bias) ==================
CHANNELS = {
    "email_list": {"label":"Email List", "yield":0.6, "bias":{"multi":0.5, "solo":0.5}},
    "cold_dm":    {"label":"Cold DMs", "yield":0.4, "bias":{"multi":0.4, "solo":0.6}},
    "forums":     {"label":"Industry Forums", "yield":0.5, "bias":{"multi":0.3, "solo":0.7}},
    "sidewalk":   {"label":"Sidewalk Intercepts", "yield":0.3, "bias":{"multi":0.2, "solo":0.8}},
}
CHANNEL_ORDER = ["email_list","cold_dm","forums","sidewalk"]

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

def answers_for(p):
    seg = p["ptype"]
    premium = p["monthly_fee"] >= 100 or p["known_for"].startswith("Premium")
    return {
        "typical_day": (
            f"I open {p['gym_name']} by 6am, review rosters, handle member messages, "
            "then coach or do admin before evening peak."
        ),
        "biggest_challenges": (
            "Keeping classes full mid-week and staying on top of admin without late nights."
            if seg=="multi" else
            "Balancing coaching time with manual follow-ups and payroll."
        ),
        "new_clients_problem": (
            "When ad costs spike, trial sign-ups dip; we scramble with staff outreach."
            if seg=="multi" else
            "Some months yes—ads get pricey and word-of-mouth stalls."
        ),
        "staff_happy": (
            "Generally yes, but last-minute schedule shuffles frustrate coaches."
            if seg=="multi" else
            "They like the community; paperwork and last-minute changes annoy them."
        ),
        "brand_image_problem": (
            "Not really—we’re known for programs and coaching quality."
            if premium else
            "We’re seen as friendly and affordable; brand is fine, resources are tight."
        ),
        "pricing_happy": (
            "Premium members expect concierge touches; most are fine, newcomers push back."
            if premium else
            "Price-sensitive crowd—discounts work but churn rises afterward."
        ),
        "acquisition_channels": (
            "Paid social, search, and partnerships; we use the list for promos."
            if seg=="multi" else
            "Instagram reels, local groups, and simple referral cards."
        ),
        "loyal_customers": (
            "Long-time members who book coach-led programs; they refer friends."
            if seg=="multi" else
            "Regulars who love the vibe; they bring friends and buy class packs."
        ),
        "growth_constraints": (
            "Predictable demand; staffing new time slots; ad volatility."
            if seg=="multi" else
            "Owner capacity and inconsistent trial-to-paid conversion."
        ),
        "use_social_media": (
            "Yes—IG and TikTok for highlights; LinkedIn for corporate wellness leads."
            if seg=="multi" else
            "Yes—Instagram mainly; TikTok experiments when time allows."
        ),
    }

# ================== Sim state & helpers ==================
def init_state():
    st.session_state.sim = {
        "started": False,
        "start_jump": False,   # for reliable intro → target tab switch
        "tokens": 10,
        "booked": [],
        "interviews": {},  # pid -> {log:[{q,a}], step:int, finished:bool, asked:set, learnings:str}
        "coverage": {"channel_counts": {}},
        "flash_opened": [],
        "flash_counts": {},   # pain -> count from flash openings
        "synthesis": None,
        "go_to_live": False,
        "go_to_score": False,
        "drafts": {"ph":"", "ntp":""}
    }

def sample_by_allocation(allocation):
    """Channels matter:
       - # booked = sum over tokens of Bernoulli(channel_yield)
       - Segment chosen using channel bias weighted by tokens
    """
    # successes by yield
    successes = 0
    for ch, n in allocation.items():
        y = CHANNELS[ch]["yield"]
        for _ in range(int(n)):
            if random.random() < y:
                successes += 1
    draws = max(1, min(8, successes))  # keep at least 1, cap at 8

    # segment weights from bias
    seg_weight = {"solo":0.0,"multi":0.0}
    for ch,toks in allocation.items():
        for seg,w in CHANNELS[ch]["bias"].items():
            seg_weight[seg] += w * toks
    if seg_weight["solo"]==0 and seg_weight["multi"]==0:
        seg_weight = {"solo":1.0,"multi":1.0}
    total = seg_weight["solo"] + seg_weight["multi"]
    probs = {"solo": seg_weight["solo"]/total, "multi": seg_weight["multi"]/total}

    # choose personas by segment probability
    pool = PERSONAS[:]
    chosen = []
    for _ in range(draws):
        seg_pick = random.choices(["solo","multi"], weights=[probs["solo"], probs["multi"]])[0]
        cand = [p for p in pool if p["ptype"]==seg_pick and p["pid"] not in chosen] or [p for p in pool if p["pid"] not in chosen]
        if not cand: break
        chosen.append(cand[0]["pid"])
    return chosen

def get_persona(pid):
    return next(p for p in PERSONAS if p["pid"]==pid)

def synthesis():
    S = st.session_state.sim
    counts, quotes = {}, {}

    # Interviews
    for pid, rec in S["interviews"].items():
        p = rec["persona"]
        primary = max(p["pains"], key=lambda k: p["pains"][k])
        counts[primary] = counts.get(primary, 0) + max(1, len(rec["log"])//2)  # weight by depth
        for e in rec["log"][:2]:
            quotes.setdefault(primary, []).append(e["a"])

    # Flash contributions
    for pain, c in S["flash_counts"].items():
        counts[pain] = counts.get(pain, 0) + c

    top = sorted(counts.keys(), key=lambda k: counts[k], reverse=True)[:5]

    # channel bias alert
    cc = S["coverage"]["channel_counts"]
    total = sum(cc.values()) or 1
    alerts = [f"Over-reliance on {CHANNELS[ch]['label']} ({int(100*n/total)}%)" for ch,n in cc.items() if n/total>0.6]

    out = {"counts":counts,"top":top,"quotes":{k:quotes.get(k,[])[:3] for k in top},"alerts":alerts}
    S["synthesis"]=out
    return out

def decide_and_score(ph, ntp):
    S = st.session_state.sim
    syn = S["synthesis"] or synthesis()
    true_top = "cac_volatility"
    chosen_top = syn["top"][0] if syn["top"] else None
    signal = 1.0 if chosen_top==true_top else (0.7 if true_top in syn["top"] else 0.3)

    total_qs = sum(len(r["log"]) for r in S["interviews"].values())
    craft = min(1.0, 0.4 + min(total_qs,10)/20)  # proxy; more thoughtful turns → better
    channels_used = len([1 for n in S["coverage"]["channel_counts"].values() if n>0])
    largest_share = max(S["coverage"]["channel_counts"].values() or [0])/(sum(S["coverage"]["channel_counts"].values()) or 1)
    coverage = 1.0 if (channels_used>=3 and largest_share<=0.6) else 0.6

    # Softer PS/Plan scoring: clarity & alignment (no required words)
    def clarity(s):
        words = len((s or "").split())
        return max(0.3, min(1.0, words/40.0))
    def aligned(s):
        txt = (s or "").lower()
        labels = [PAINS[k]["label"].lower() for k in syn["top"]]
        return 1.0 if any(lbl.split()[0] in txt for lbl in labels) else 0.6

    psq = 0.5*clarity(ph) + 0.5*aligned(ph)
    ntpq = 0.6*clarity(ntp) + 0.4*(1.0 if "threshold" in (ntp or "").lower() or "metric" in (ntp or "").lower() else 0.6)

    score = round(100*(0.30*craft+0.15*coverage+0.30*signal+0.15*psq+0.10*ntpq))
    components = {
        "Interview Craft": round(craft,2),
        "Coverage": round(coverage,2),
        "Signal Detection": round(signal,2),
        "Problem Statement Quality": round(psq,2),
        "Next Test Plan": round(ntpq,2)
    }
    explanations = {
        "Interview Craft": "Based on number of meaningful turns; thoughtful follow-ons raise this.",
        "Coverage": "Diverse channels reduce sampling bias; aim for ≥3 and avoid one dominant source.",
        "Signal Detection": f"Whether your inferred top issue matches the emphasized market signal. "
                            f"Your top signal: **{PAINS.get(chosen_top, {'label':'—'}).get('label','—')}**; "
                            f"Ground-truth emphasis: **{PAINS['cac_volatility']['label']}**.",
        "Problem Statement Quality": "Clarity and alignment with surfaced pains.",
        "Next Test Plan": "Clarity of steps and whether success criteria are explicit (metric/threshold).",
    }
    return {"score":score,"components":components,"explanations":explanations}

# ================== Streamlit app ==================
st.set_page_config(page_title="Startup Simulation: Problem Discovery & Validation", page_icon="🧪", layout="wide")
if "sim" not in st.session_state: init_state()
S = st.session_state.sim

st.title("Startup Simulation: Problem Discovery & Validation")
tabs = st.tabs(["Intro","Target & Recruit","Live Interviews","Flash Bursts","Synthesis + Decide","Score"])

# After tabs are created, honor any pending auto-switches
if S.get("start_jump"):
    components.html("<script>const t=window.parent.document.querySelectorAll('button[role=tab]'); if(t[1]){t[1].click(); setTimeout(()=>t[1].click(),80);}</script>", height=0)
    S["start_jump"]=False

# ---- Intro ----
with tabs[0]:
    st.subheader("Welcome")
    st.markdown("""
**How the simulation works:** You’ll practice the discovery loop — **target → recruit → interview → synthesize → decide**.

**Time:** ~75–90 minutes (solo, one sitting).

**What you’ll do:**
1) Pick a target and allocate **10 effort tokens** across channels.  
2) Conduct short **live interviews** (4–10 questions each).  
3) Open **Flash Bursts** to broaden coverage.  
4) Run **Synthesis** and draft a **Problem Hypothesis** and **Next Test Plan**.  
5) Get a **Score** and a short debrief.

**Objectives:** Improve interview craft, detect real signals, and plan an evidence-based next step.
""")
    if not S["started"]:
        if st.button("Start Simulation"):
            S["started"] = True
            S["start_jump"] = True
            # double nudge for reliability
            components.html("<script>const t=window.parent.document.querySelectorAll('button[role=tab]'); if(t[1]){t[1].click(); setTimeout(()=>t[1].click(),80);}</script>", height=0)
            st.rerun()
    else:
        st.success("Simulation started — moving you to Target & Recruit…")
        S["start_jump"] = True
        components.html("<script>const t=window.parent.document.querySelectorAll('button[role=tab]'); if(t[1]){t[1].click(); setTimeout(()=>t[1].click(),80);}</script>", height=0)

# ---- Target & Recruit ----
with tabs[1]:
    if not S["started"]:
        st.info("Start on the Intro tab first.")
    else:
        st.subheader("Market Brief")
        st.info(SEED_MARKET_BRIEF)
        st.markdown("""
**You have 10 effort tokens** to recruit across channels.  
Each channel differs in **yield**, **bias**, and **speed**.  
**Trade-off:** cover segments vs. depth. Avoid over-reliance on a single channel.
""")
        cols = st.columns(4)
        alloc = {}
        for i,ch in enumerate(CHANNEL_ORDER):
            with cols[i]:
                alloc[ch] = st.number_input(
                    CHANNELS[ch]["label"],
                    min_value=0, max_value=10, value=0, step=1, key=f"alloc_{ch}"
                )
        total = sum(alloc.values())
        st.caption(f"Allocated: **{total}/10** tokens")
        if st.button("Book Personas", disabled=(total!=10)):
            S["tokens"] = max(0, S["tokens"]-10)
            booked = sample_by_allocation(alloc)
            S["booked"] = booked
            for ch,n in alloc.items():
                S["coverage"]["channel_counts"][ch]=S["coverage"]["channel_counts"].get(ch,0)+n
            for pid in booked:
                p = get_persona(pid)
                S["interviews"][pid]={"log":[], "persona":deepcopy(p), "step":0, "finished":False, "asked":set(), "learnings":""}
            S["go_to_live"]=True
            components.html("<script>setTimeout(()=>{const t=window.parent.document.querySelectorAll('button[role=tab]'); if(t[2]) t[2].click();},60)</script>", height=0)
            st.rerun()

# ---- Live Interviews ----
with tabs[2]:
    if S.get("go_to_live"):
        components.html("<script>const t=window.parent.document.querySelectorAll('button[role=tab]'); if(t[2]){t[2].click(); setTimeout(()=>t[2].click(),60);}</script>", height=0)
        S["go_to_live"]=False
    st.subheader("Live Interviews")
    if not S["booked"]:
        st.info("Book personas in **Target & Recruit** first.")
    else:
        booked_cards = [get_persona(pid) for pid in S["booked"]]
        with st.expander(f"Booked Personas ({len(booked_cards)})", expanded=True):
            for p in booked_cards:
                st.markdown(
                    f"**{p['owner']} — {p['gym_name']}**  \n"
                    f"{SEG_LABEL[p['ptype']]} • ~{p['weekly_clients']} weekly clients/studio • {p['staff_per']} staff/studio • ${p['monthly_fee']}/mo  \n"
                    f"_Known for: {p['known_for']}_"
                )
        pid = st.selectbox(
            "Choose who to interview",
            S["booked"],
            format_func=lambda x: get_persona(x)["owner"] + " — " + get_persona(x)["gym_name"]
        )
        rec = S["interviews"][pid]; p = rec["persona"]; name = p["owner"]

        st.markdown("#### Transcript")
        if rec["log"]:
            st.markdown("\n\n".join([f"**You:** {t['q']}\n\n**{name}:** {t['a']}" for t in rec["log"]]))
        else:
            st.caption("_No questions yet. Pick a conversation starter below._")

        answered = rec["asked"]
        if not rec["finished"]:
            st.markdown("#### Ask a question")
            if rec["step"]==0:
                pool = [q for q in STARTERS if q[0] not in answered]
            elif rec["step"]==1:
                rem_starters = [q for q in STARTERS if q[0] not in answered]
                pool = rem_starters[:3] + [q for q in FOLLOWUPS if q[0] not in answered][:2]
            else:
                pool = [q for q in FOLLOWUPS if q[0] not in answered]
                if len(pool)<3:
                    pool += [q for q in STARTERS if q[0] not in answered]
            A = answers_for(p)
            pool = pool[:5]
            cols = st.columns(len(pool)) if pool else [st]
            for i,(qkey,qtext) in enumerate(pool):
                with cols[i]:
                    if st.button(qtext, key=f"{pid}_q_{rec['step']}_{qkey}"):
                        ans = A.get(qkey, "It depends on the week, but it does come up.")
                        rec["log"].append({"q": qtext, "a": ans})
                        rec["asked"].add(qkey)
                        rec["step"] += 1
                        st.rerun()
            if rec["step"]>=2:
                st.info("You can end the interview when ready.")
                if st.button("Thank the person and end interview", key=f"end_{pid}"):
                    rec["finished"]=True
                    st.rerun()
        else:
            st.success("Interview finished.")
            rec["learnings"]=st.text_area(
                "Summarize your key learnings from this interview",
                value=rec.get("learnings",""),
                placeholder="Top pain, frequency, severity, triggers, workarounds, early willingness to pay…"
            )
            if st.button("Submit learnings", key=f"submit_{pid}"):
                st.toast("Learnings saved.")

# ---- Flash Bursts ----
with tabs[3]:
    st.subheader("Flash Bursts")
    openable = [f["title"] for f in FLASH_ITEMS if f["title"] not in S["flash_opened"]]
    picks = st.multiselect("Pick up to 5 to open", openable, max_selections=5)
    if st.button("Open Selected") and picks:
        for title in picks:
            if title not in S["flash_opened"]:
                S["flash_opened"].append(title)
                f = next(x for x in FLASH_ITEMS if x["title"]==title)
                key = f["primary_pain"]
                S["flash_counts"][key] = S["flash_counts"].get(key,0)+1
        st.rerun()
    for title in S["flash_opened"]:
        f = next(x for x in FLASH_ITEMS if x["title"]==title)
        st.info(
            f"**{f['title']}**  \n"
            f"{f['ptype']} • ~{f['weekly_clients']} weekly clients/studio • {f['staff_per']} staff/studio • ${f['monthly_fee']}/mo  \n"
            f"_Known for: {f['known_for']}_  \n\n"
            f"**How they’re doing:** {f['status']}  \n"
            f"**Biggest challenges:** {f['challenges']}"
        )

# ---- Synthesis + Decide ----
with tabs[4]:
    st.subheader("Synthesis")
    if st.button("Run Synthesis") or S.get("synthesis"):
        syn = synthesis()
        c1,c2 = st.columns(2)
        with c1:
            st.markdown("**Top pains (counts)**")
            if not syn["top"]:
                st.write("_No signal yet. Ask more questions and open more flashes._")
            for k in syn["top"]:
                st.write(f"- {PAINS[k]['label']}: {syn['counts'][k]}")
        with c2:
            st.markdown("**Bias alerts**")
            if syn["alerts"]:
                for a in syn["alerts"]: st.warning(a)
            else:
                st.success("No major channel bias detected.")
        st.markdown("**Sample quotes**")
        for k in syn["top"]:
            for q in syn["quotes"].get(k,[]):
                st.caption(f"• {q}")

    st.markdown("---")
    st.subheader("Decide & Draft")

    # Examples (neutral domain) restored
    with st.expander("See examples (for structure only)"):
        st.markdown("**Problem Hypothesis example**  \n"
                    "_Operations managers in mid-size logistics firms, when weather disrupts shipments, "
                    "struggle with **manual rescheduling**, causing missed SLAs and overtime costs. "
                    "They currently juggle spreadsheets and phone calls._")
        st.markdown("**Next Test Plan example**  \n"
                    "_Assumption: managers will adopt a daily ETA risk alert if it cuts rework.  \n"
                    "Method: concierge alerts for 8 customers over 3 weeks.  \n"
                    "Metric: rework hours/week and % on-time.  \n"
                    "Success threshold: ≥30% rework reduction and ≥5/8 ask to continue._")

    S["drafts"]["ph"]=st.text_area("Your Problem Hypothesis", value=S["drafts"]["ph"])
    S["drafts"]["ntp"]=st.text_area("Your Next Test Plan", value=S["drafts"]["ntp"])
    if st.button("Submit"):
        if not S.get("synthesis"): synthesis()
        S["go_to_score"]=True
        components.html("<script>const t=window.parent.document.querySelectorAll('button[role=tab]'); if(t[5]){t[5].click(); setTimeout(()=>t[5].click(),80);}</script>", height=0)
        st.rerun()

# ---- Score ----
with tabs[5]:
    st.subheader("Score")
    if S.get("go_to_score"):
        components.html("<script>const t=window.parent.document.querySelectorAll('button[role=tab]'); if(t[5]){t[5].click(); setTimeout(()=>t[5].click(),60);}</script>", height=0)
        S["go_to_score"]=False
    if st.button("Compute Score"):
        res = decide_and_score(S["drafts"].get("ph",""), S["drafts"].get("ntp",""))

        else:
            st.table({"Component":labels,"Score (0–1)":values})

        st.metric("Total Score", f"{res['score']}/100")

        st.markdown("### Component breakdown")
        for k,v in res["components"].items():
            pct = int(round(v*100))
            verdict = "Excellent" if pct>=80 else "Good" if pct>=60 else "Mixed" if pct>=40 else "Needs work"
            why = res["explanations"][k]
            st.write(f"- **{k}:** {pct}/100 — {verdict}. {why}")
        st.markdown("### Key Lessons")
        st.markdown("""
- **When interviewing,** use open-ended, empathetic questions. Avoid leading or solution-focused phrasing.
- **When recruiting,** balance your channel mix to avoid bias; don’t rely too heavily on a single source.
- **When synthesizing,** look for patterns in pains across segments, not just frequency counts.
- **When drafting,** ensure your problem statement is specific, evidence-based, and aligned with surfaced pains.
- **When planning tests,** define a clear assumption, method, and explicit success threshold.
""")
