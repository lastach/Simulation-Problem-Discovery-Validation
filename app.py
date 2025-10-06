# Startup Simulation: Problem Discovery & Validation (Streamlit)
# --------------------------------------------------------------
# pip install -r requirements.txt
# streamlit run app.py
# --------------------------------------------------------------

import random, math, json
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

# pain dictionary (engine uses; UI shows friendly names)
PAINS = {
    "cac_volatility": {"label": "Paid acquisition volatility", "base_freq": 0.62, "base_severity": 0.78},
    "post_promo_churn": {"label": "Churn after intro promos", "base_freq": 0.47, "base_severity": 0.65},
    "admin_overhead": {"label": "Admin/payroll overhead", "base_freq": 0.36, "base_severity": 0.45},
    "scheduling_glitch": {"label": "Scheduling tool glitches", "base_freq": 0.22, "base_severity": 0.35},
    "referral_stagnation": {"label": "Referral stagnation", "base_freq": 0.31, "base_severity": 0.50},
}

SEG_LABEL = {"solo": "Solo Studio", "multi": "Multi-Site Gym"}

# ================== Personas ==================
def persona(pid, gym_name, owner, ptype, weekly_clients, staff_per, monthly_fee, known_for, pains, workarounds, tell, anecdotes):
    return {
        "pid": pid,
        "gym_name": gym_name,
        "owner": owner,
        "ptype": ptype,  # "solo" | "multi"  (UI shows SEG_LABEL)
        "weekly_clients": weekly_clients,
        "staff_per": staff_per,
        "monthly_fee": monthly_fee,
        "known_for": known_for,
        "pains": pains,                 # weight map (0..1)
        "workarounds": workarounds,     # dict per pain
        "tell_threshold": tell,
        "anecdotes": anecdotes,
    }

# Helpers for coherent numbers
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
    "Two weeks ago our ads spiked in cost; trial sign-ups halved.",
    "We phone bank to fill empty classes when campaigns dip.",
    "Payroll always takes longer than planned—CSV exports every Friday.",
    "Intro offer folks vanish unless we personally check in.",
    "Calendar double-books at peak once in a while.",
]

PERSONAS = []
# ---- 8 Solo Studio owners ----
PERSONAS += [
    persona("p1","Sunrise Yoga","Lena Park","solo", *solo(premium=False, budget=True),
            {"cac_volatility":0.5,"post_promo_churn":0.7,"admin_overhead":0.4},
            {"post_promo_churn":"owner texts trial members"},
            0.50,[ANEC[3],ANEC[2]]),
    persona("p2","Steel City Strength","Marco Diaz","solo", *solo(premium=False, budget=False),
            {"cac_volatility":0.8,"admin_overhead":0.3},
            {"cac_volatility":"flash discounts; IG reels"},
            0.55,[ANEC[0],ANEC[1]]),
    persona("p3","Harbor Pilates","Rina Ahmed","solo", *solo(premium=True),
            {"post_promo_churn":0.6,"referral_stagnation":0.5},
            {"referral_stagnation":"partner spa referrals"},
            0.60,[ANEC[3]]),
    persona("p4","North Loop Boxing","Caleb Brooks","solo", *solo(),
            {"cac_volatility":0.7,"scheduling_glitch":0.3},
            {"cac_volatility":"owner DM’s past members"},
            0.55,[ANEC[0],ANEC[4]]),
    persona("p5","Greenpoint Climb","Yara Cohen","solo", *solo(premium=True),
            {"admin_overhead":0.6,"referral_stagnation":0.4},
            {"admin_overhead":"manual payroll CSV"},
            0.65,[ANEC[2]]),
    persona("p6","Southside Spin","Owen Kelly","solo", *solo(budget=True),
            {"post_promo_churn":0.8,"cac_volatility":0.5},
            {"post_promo_churn":"staff follow-up calls"},
            0.55,[ANEC[3]]),
    persona("p7","Peak Performance PT","Daria Novak","solo", *solo(),
            {"referral_stagnation":0.7,"admin_overhead":0.4},
            {"referral_stagnation":"scripted ask after sessions"},
            0.60,[ANEC[2]]),
    persona("p8","Riverfront Barre","Maya Chen","solo", *solo(premium=True),
            {"scheduling_glitch":0.4,"cac_volatility":0.6},
            {"scheduling_glitch":"manual adjustments"},
            0.55,[ANEC[4]]),
]
# ---- 4 Multi-Site owners ----
PERSONAS += [
    persona("p9","Core Collective","Nate Wallace","multi", *multi(),
            {"cac_volatility":1.0,"admin_overhead":0.5},
            {"cac_volatility":"pause spend + phone outreach"},
            0.55,[ANEC[0],ANEC[1]]),
    persona("p10","MetroFit","Aisha Goyal","multi", *multi(premium=True),
            {"cac_volatility":0.9,"post_promo_churn":0.6},
            {"post_promo_churn":"tiered offers; coach callbacks"},
            0.60,[ANEC[0],ANEC[3]]),
    persona("p11","Titan Athletics","Gabe Ortiz","multi", *multi(budget=True),
            {"admin_overhead":0.7,"scheduling_glitch":0.4},
            {"admin_overhead":"ops spreadsheets each Thursday"},
            0.60,[ANEC[2],ANEC[4]]),
    persona("p12","Northside Strength","Priya Patel","multi", *multi(),
            {"referral_stagnation":0.7,"cac_volatility":0.6},
            {"referral_stagnation":"partner network push"},
            0.60,[ANEC[0]]),
]

# ================== Flash items (name + type) ==================
FLASH_ITEMS = [
    {"title":"Core Collective — Multi-Site Gym","bio":"Two urban locations serving young professionals.",
     "status":"Revenue steady but ads volatility causes mid-week dips.",
     "challenges":"Balancing spend vs. staff time; keeping peak classes full."},
    {"title":"Sunrise Yoga — Solo Studio","bio":"Neighborhood studio with loyal early-morning crowd.",
     "status":"Intro offers convert inconsistently.",
     "challenges":"Post-promo churn; limited time for manual follow-ups."},
    {"title":"Harbor Pilates — Solo Studio","bio":"Premium reformer classes with boutique feel.",
     "status":"Referrals slowed as partner spa changed owners.",
     "challenges":"Referral stagnation; rebuilding partner pipeline."},
    {"title":"MetroFit — Multi-Site Gym","bio":"Flagship plus a suburban site.",
     "status":"CPC spikes reduce trial volume; premium programs carry margins.",
     "challenges":"Paid acquisition volatility; keeping CAC predictable."},
    {"title":"Southside Spin — Solo Studio","bio":"Budget-friendly spin classes; community-driven.",
     "status":"Good trial volume; poor conversion to monthly.",
     "challenges":"Churn after promos; better onboarding needed."},
]

# ================== Channels (UI labels only) ==================
CHANNELS = {
    "email_list": {"label":"Email List", "bias":{"multi":0.5, "solo":0.5}},
    "cold_dm":    {"label":"Cold DMs", "bias":{"multi":0.4, "solo":0.6}},
    "forums":     {"label":"Industry Forums", "bias":{"multi":0.3, "solo":0.7}},
    "sidewalk":   {"label":"Sidewalk Intercepts", "bias":{"multi":0.2, "solo":0.8}},
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

# Unique answer map per persona (q_key -> answer). Keep it short & distinct.
def answers_for(p):
    seg = p["ptype"]
    premium = p["monthly_fee"] >= 100 or p["known_for"].startswith("Premium")
    budget = p["monthly_fee"] <= 60 or "Budget" in p["known_for"]
    return {
        "typical_day": (
            f"I open {p['gym_name']} by 6am, review class rosters, then handle member messages before sessions. "
            "Afternoons are admin and coaching; evenings are peak classes."
        ),
        "biggest_challenges": (
            "Keeping classes full mid-week and staying on top of admin without burning nights."
            if seg=="multi" else
            "Balancing coaching time with manual follow-ups and payroll."
        ),
        "new_clients_problem": (
            "When ad costs spike, trial sign-ups dip; we scramble with staff outreach."
            if seg=="multi" else
            "Some months yes—ads get pricey and word-of-mouth stalls."
        ),
        "staff_happy": (
            "Generally yes, but schedule changes at peak frustrate coaches."
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
            "Price sensitive segment—discounts work but churn rises afterward."
        ),
        "acquisition_channels": (
            "Paid social, Google search, and partnerships; email list for promos."
            if seg=="multi" else
            "Instagram reels, local groups, and referral cards."
        ),
        "loyal_customers": (
            "Long-time members who book coach-led programs; they refer friends."
            if seg=="multi" else
            "Regulars who love the vibe; they bring friends and buy class packs."
        ),
        "growth_constraints": (
            "Predictable demand; finding coaches for new time slots; ad volatility."
            if seg=="multi" else
            "Owner capacity and inconsistent trial-to-paid conversion."
        ),
        "use_social_media": (
            "Yes—IG and TikTok for highlights; LinkedIn for corporate wellness leads."
            if seg=="multi" else
            "Yes—Instagram mainly; TikTok experiments when we have time."
        ),
    }

# ================== Sim state & helpers ==================
def init_state():
    st.session_state.sim = {
        "started": False,
        "tokens": 10,
        "booked": [],
        "interviews": {},  # pid -> {log:[{q,a}], step:int, finished:bool, asked:set, learnings:str}
        "coverage": {"channel_counts": {}},
        "flash_opened": [],
        "synthesis": None,
        "go_to_live": False,
        "go_to_score": False,
        "drafts": {"ph":"", "ntp":""}
    }

def sample_by_allocation(allocation):
    draws = max(0, int(sum(allocation.values())))
    if draws == 0: return []
    seg_weight = {"solo":0.0,"multi":0.0}
    for ch,toks in allocation.items():
        if toks<=0: continue
        for seg,w in CHANNELS[ch]["bias"].items():
            seg_weight[seg] += w * toks
    if seg_weight["solo"]==0 and seg_weight["multi"]==0:
        seg_weight = {"solo":1.0,"multi":1.0}
    total = seg_weight["solo"] + seg_weight["multi"]
    probs = {"solo": seg_weight["solo"]/total, "multi": seg_weight["multi"]/total}
    pool = PERSONAS[:]
    random.shuffle(pool)
    chosen = []
    for _ in range(min(8, draws)):
        seg_pick = random.choices(["solo","multi"], weights=[probs["solo"], probs["multi"]])[0]
        cand = [p for p in pool if p["ptype"]==seg_pick and p["pid"] not in chosen] or [p for p in pool if p["pid"] not in chosen]
        if not cand: break
        chosen.append(cand[0]["pid"])
    return chosen

def get_persona(pid):
    return next(p for p in PERSONAS if p["pid"]==pid)

def synthesis():
    s = st.session_state.sim
    counts, sev, quotes, segments = {}, {}, {}, {}
    for pid, rec in s["interviews"].items():
        p = rec["persona"]
        segments[p["ptype"]] = segments.get(p["ptype"],0)+1
        # attribute to persona's strongest pain to keep MVP simple
        main_k = max(p["pains"], key=lambda k: p["pains"][k])
        counts[main_k] = counts.get(main_k,0)+1
        sev[main_k] = sev.get(main_k,0.0) + (0.6 + 0.4*p["pains"][main_k])
        for e in rec["log"][:2]:
            quotes.setdefault(main_k, []).append(e["a"])
    avg_sev = {k: round(sev[k]/max(counts[k],1),2) for k in counts}
    top = sorted(counts.keys(), key=lambda k:(counts[k],avg_sev[k]), reverse=True)[:5]
    # channel bias alert
    cc = s["coverage"]["channel_counts"]; total = sum(cc.values()) or 1
    alerts = [f"Over-reliance on {CHANNELS[ch]['label']} ({int(100*n/total)}%)" for ch,n in cc.items() if n/total>0.6]
    out = {"counts":counts,"avg_sev":avg_sev,"top":top,"quotes":{k:quotes.get(k,[])[:3] for k in top},"segments":segments,"alerts":alerts}
    s["synthesis"]=out
    return out

def decide_and_score(ph, ntp):
    s = st.session_state.sim
    syn = s["synthesis"] or synthesis()
    true_top = "cac_volatility"
    chosen_top = syn["top"][0] if syn["top"] else None
    signal = 1.0 if chosen_top==true_top else (0.7 if true_top in syn["top"] else 0.3)
    total_qs = sum(len(r["log"]) for r in s["interviews"].values())
    craft = min(1.0, 0.4 + min(total_qs,10)/20)  # simple proxy; more Qs → better, capped
    channels_used = len([1 for n in s["coverage"]["channel_counts"].values() if n>0])
    largest_share = max(s["coverage"]["channel_counts"].values() or [0])/(sum(s["coverage"]["channel_counts"].values()) or 1)
    coverage = 1.0 if (channels_used>=3 and largest_share<=0.6) else 0.6
    psq = 0.8 if ("trigger" in ph.lower() and "impact" in ph.lower()) else 0.5
    ntpq = 0.8 if ("assumption" in ntp.lower() and "threshold" in ntp.lower()) else 0.5
    score = round(100*(0.30*craft+0.15*coverage+0.30*signal+0.15*psq+0.10*ntpq))
    components = {
        "Interview Craft": craft,
        "Coverage": coverage,
        "Signal Detection": signal,
        "Problem Statement Quality": psq,
        "Next Test Plan": ntpq
    }
    explanations = {
        "Interview Craft": "Based on total useful Qs asked (more thoughtful turns tends to raise this).",
        "Coverage": "Diverse channels reduce sampling bias; aim for ≥3 channels and avoid any single one dominating.",
        "Signal Detection": "Whether the top issue you inferred matches the underlying signal emphasized in this market.",
        "Problem Statement Quality": "Clear who/trigger/consequence/workaround; include ‘trigger’ and ‘impact’ wording.",
        "Next Test Plan": "A narrow assumption, concrete method, metric, sample size, and ‘success threshold’.",
    }
    return {"score":score,"components":components,"explanations":explanations,"chosen_top":chosen_top,"true_top":true_top}

# ================== Streamlit app ==================
st.set_page_config(page_title="Startup Simulation: Problem Discovery & Validation", page_icon="🧪", layout="wide")
if "sim" not in st.session_state: init_state()
S = st.session_state.sim

st.title("Startup Simulation: Problem Discovery & Validation")
tabs = st.tabs(["Intro","Target & Recruit","Live Interviews","Flash Bursts","Synthesis + Decide","Score"])

# ---- Intro ----
with tabs[0]:
    st.subheader("Welcome")
    st.markdown("""
**How it works**: Practice the discovery loop — **target → recruit → interview → synthesize → decide**.  
**Time**: ~75–90 minutes (solo).  
**Your objectives**: Ask better questions, detect real signals, and choose an evidence-based next test.
""")
    if not S["started"]:
        if st.button("Start Simulation"):
            S["started"] = True
            components.html("<script>setTimeout(()=>{const t=window.parent.document.querySelectorAll('button[role=tab]'); if(t[1]) t[1].click();},60)</script>", height=0)
            st.rerun()
    else:
        st.success("Simulation started — go to **Target & Recruit**.")

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
**Trade-off**: cover segments vs. depth. Avoid over-reliance on one source.
""")
        cols = st.columns(4)
        alloc = {}
        for i,ch in enumerate(CHANNEL_ORDER):
            with cols[i]:
                alloc[ch]=st.number_input(CHANNELS[ch]["label"],0,10,0,1,key=f"alloc_{ch}")
        total = sum(alloc.values())
        st.caption(f"Allocated: **{total}/10** tokens")
        if st.button("Book Personas", disabled=(total!=10)):
            S["tokens"] = max(0, S["tokens"]-10)
            booked = sample_by_allocation(alloc)
            S["booked"]=booked
            for ch,n in alloc.items():
                S["coverage"]["channel_counts"][ch]=S["coverage"]["channel_counts"].get(ch,0)+n
            for pid in booked:
                p = get_persona(pid)
                S["interviews"][pid]={"log":[], "persona":deepcopy(p), "step":0, "finished":False, "asked":set(), "learnings":""}
            S["go_to_live"]=True
            components.html("<script>setTimeout(()=>{const t=window.parent.document.querySelectorAll('button[role=tab]'); if(t[2]) t[2].click();},80)</script>", height=0)
            st.rerun()

# ---- Live Interviews ----
with tabs[2]:
    if S.get("go_to_live"):
        components.html("<script>const t=window.parent.document.querySelectorAll('button[role=tab]'); if(t[2]) t[2].click();</script>", height=0)
        S["go_to_live"]=False
    st.subheader("Live Interviews")
    if not S["booked"]:
        st.info("Book personas in **Target & Recruit** first.")
    else:
        with st.expander(f"Booked Personas ({len(S['booked'])})", expanded=True):
            for pid in S["booked"]:
                p = get_persona(pid)
                st.markdown(
                    f"**{p['owner']} — {p['gym_name']}**  \n"
                    f"{SEG_LABEL[p['ptype']]} • ~{p['weekly_clients']} weekly clients/studio • {p['staff_per']} staff/studio • ${p['monthly_fee']}/mo  \n"
                    f"_Known for: {p['known_for']}_"
                )
        pid = st.selectbox("Choose who to interview", S["booked"], format_func=lambda x: get_persona(x)["owner"] + " — " + get_persona(x)["gym_name"])
        rec = S["interviews"][pid]; p = rec["persona"]; name = p["owner"]

        # Transcript (conversation only)
        st.markdown("#### Transcript")
        if rec["log"]:
            st.markdown("\n\n".join([f"**You:** {t['q']}\n\n**{name}:** {t['a']}" for t in rec["log"]]))
        else:
            st.caption("_No questions yet. Pick a conversation starter below._")

        # Build options pool (hide already-asked)
        answered = rec["asked"]
        if not rec["finished"]:
            st.markdown("#### Ask a question")
            if rec["step"]==0:
                pool = [q for q in STARTERS if q[0] not in answered]
            elif rec["step"]==1:
                # mix of remaining starters and a couple follow-ups
                rem_starters = [q for q in STARTERS if q[0] not in answered]
                pool = rem_starters[:3] + [q for q in FOLLOWUPS if q[0] not in answered][:2]
            else:
                pool = [q for q in FOLLOWUPS if q[0] not in answered]
                if len(pool)<3:
                    pool += [q for q in STARTERS if q[0] not in answered]
            # unique answers per persona
            A = answers_for(p)
            # Render buttons (max 5 options)
            pool = pool[:5]
            cols = st.columns(len(pool)) if pool else [st]
            for i,(qkey,qtext) in enumerate(pool):
                with cols[i]:
                    if st.button(qtext, key=f"{pid}_q_{rec['step']}_{qkey}"):
                        # answer & update state
                        ans = A.get(qkey, "Hmm—depends on the week, but it does come up.")
                        rec["log"].append({"q": qtext, "a": ans})
                        rec["asked"].add(qkey)
                        rec["step"] += 1
                        # End option appears only after 2 questions
                        st.rerun()
            if rec["step"]>=2:
                if st.button("Thank the person and end interview", key=f"end_{pid}"):
                    rec["finished"]=True
                    st.rerun()
        else:
            st.success("Interview finished.")
            rec["learnings"]=st.text_area("Summarize your key learnings from this interview",
                                          value=rec.get("learnings",""),
                                          placeholder="Top pain, frequency, severity, triggers, workarounds, early WTP cues…")

# ---- Flash Bursts ----
with tabs[3]:
    st.subheader("Flash Bursts")
    if "flash_opened" not in S: S["flash_opened"]=[]
    openable = [f["title"] for f in FLASH_ITEMS if f["title"] not in S["flash_opened"]]
    picks = st.multiselect("Pick up to 5 to open", openable, max_selections=5)
    if st.button("Open Selected") and picks:
        S["flash_opened"] += picks
        st.rerun()
    for title in S["flash_opened"]:
        f = next(x for x in FLASH_ITEMS if x["title"]==title)
        st.info(f"**{f['title']}**\n\n**Studio:** {f['bio']}\n\n**How they’re doing:** {f['status']}\n\n**Biggest challenges:** {f['challenges']}")

# ---- Synthesis + Decide ----
with tabs[4]:
    st.subheader("Synthesis")
    if st.button("Run Synthesis") or S.get("synthesis"):
        syn = synthesis()
        c1,c2 = st.columns(2)
        with c1:
            st.markdown("**Top pains (counts | avg severity)**")
            if not syn["top"]:
                st.write("_No signal yet. Ask more questions._")
            for k in syn["top"]:
                st.write(f"- {PAINS[k]['label']}: {syn['counts'][k]} | {syn['avg_sev'][k]}")
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
    st.caption("Examples below are intentionally outside fitness so you craft your own:")
    st.markdown("**Problem Hypothesis example**  \n"
                "_Operations managers in mid-size logistics firms, when weather disrupts shipments, struggle with **manual rescheduling**, causing missed SLAs and overtime costs. They currently juggle spreadsheets and phone calls._")
    st.markdown("**Next Test Plan example**  \n"
                "_Assumption: managers will adopt a daily ETA risk alert if it cuts rework.  \n"
                "Method: concierge alerts for 8 customers over 3 weeks.  \n"
                "Metric: rework hours/week and % on-time.  \n"
                "Success threshold: ≥30% rework reduction and ≥5/8 ask to continue._")

    S["drafts"]["ph"]=st.text_area("Your Problem Hypothesis", value=S["drafts"]["ph"])
    S["drafts"]["ntp"]=st.text_area("Your Next Test Plan", value=S["drafts"]["ntp"])
    if st.button("Submit"):
        # ensure synthesis exists
        if not S.get("synthesis"): synthesis()
        S["go_to_score"]=True
        components.html("<script>const t=window.parent.document.querySelectorAll('button[role=tab]'); if(t[5]) t[5].click();</script>", height=0)
        st.rerun()

# ---- Score ----
with tabs[5]:
    st.subheader("Score")
    if S.get("go_to_score"):
        components.html("<script>const t=window.parent.document.querySelectorAll('button[role=tab]'); if(t[5]) t[5].click();</script>", height=0)
        S["go_to_score"]=False
    if st.button("Compute Score"):
        res = decide_and_score(S["drafts"].get("ph",""), S["drafts"].get("ntp",""))

        # Spider chart or fallback table
        labels = list(res["components"].keys())
        values = [res["components"][k] for k in labels]
        if _HAS_MPL:
            angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
            angles += angles[:1]; values_plot = values + values[:1]
            fig = plt.figure()
            ax = plt.subplot(111, polar=True)
            ax.plot(angles, values_plot, linewidth=2)
            ax.fill(angles, values_plot, alpha=0.25)
            ax.set_xticks(angles[:-1]); ax.set_xticklabels(labels); ax.set_yticklabels([])
            st.pyplot(fig)
        else:
            st.table({"Component":labels,"Score (0–1)":values})

        st.metric("Total Score", f"{res['score']}/100")
        st.markdown(f"**Your top signal:** {PAINS.get(res['chosen_top'],{'label':'—'}).get('label','—')}  "
                    f"| **Ground-truth emphasis:** {PAINS['cac_volatility']['label']}")

        st.markdown("### Component breakdown")
        for k,v in res["components"].items():
            pct = int(round(v*100))
            if pct>=80: verdict="Excellent"
            elif pct>=60: verdict="Good"
            elif pct>=40: verdict="Mixed"
            else: verdict="Needs work"
            why = res["explanations"][k]
            st.write(f"- **{k}:** {pct}/100 — {verdict}. {why}")

        st.markdown("### Key Lessons")
        st.markdown("""
- **When interviewing,** favor past-behavior, open prompts early; avoid yes/no and solution-pitching.
- **When recruiting,** balance channels to reduce bias; aim for at least three distinct sources.
- **When synthesizing,** quantify with frequency + severity + quotes; watch for channel skew.
- **When drafting hypotheses,** include who, trigger, consequence, and workaround.
- **When planning next tests,** pick one narrow assumption with a clear success threshold.
""")
