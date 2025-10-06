# Startup Simulation: Problem Discovery & Validation (Streamlit)
# --------------------------------------------------------------
# Run locally:
#   pip install -r requirements.txt
#   streamlit run app.py
# --------------------------------------------------------------

import json, random, math
from copy import deepcopy
import streamlit as st
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
import numpy as np

# =============== Seed market & data (IDs internal, UI shows clean labels) ===============

SEED_MARKET_ID = "independent_gym_owners"
SEED_MARKET_BRIEF = (
    "Independent gym owners managing acquisition volatility, churn after promos, "
    "and admin overhead. Sub-segments: Solo Studios, Multi-Site Gyms, Premium PT Studios."
)

PAINS = {
    "cac_volatility": {
        "key": "cac_volatility", "label": "Paid acquisition volatility",
        "base_freq": 0.62, "base_severity": 0.78,
    },
    "post_promo_churn": {
        "key": "post_promo_churn", "label": "Churn after intro promos",
        "base_freq": 0.47, "base_severity": 0.65,
    },
    "admin_overhead": {
        "key": "admin_overhead", "label": "Admin/payroll overhead",
        "base_freq": 0.36, "base_severity": 0.45,
    },
    "scheduling_glitch": {
        "key": "scheduling_glitch", "label": "Scheduling tool glitches",
        "base_freq": 0.22, "base_severity": 0.35,
    },
    "referral_stagnation": {
        "key": "referral_stagnation", "label": "Referral stagnation",
        "base_freq": 0.31, "base_severity": 0.50,
    },
}

SEG_LABEL = {
    "solo_studio": "Solo Studio",
    "multi_site": "Multi-Site Gym",
    "premium_pt": "Premium PT Studio",
}

ANEC = [
    "Two weeks ago our Meta ads tanked; leads halved.",
    "Staff did manual outreach for trial passes to backfill.",
    "Payroll runs late night once a week; always some reconciliation.",
    "Intro offer folks ghost after week two unless we call them.",
    "Peak-hour calendar shows duplicate bookings sometimes.",
]

def make_persona(pid, name, segment, bio, quirks, pains, workaround, spend_ceiling, tell_threshold, anecdotes):
    return {
        "pid": pid, "name": name, "segment": segment, "bio": bio, "quirks": quirks,
        "pains": pains, "workaround": workaround, "spend_ceiling": float(spend_ceiling),
        "tell_threshold": float(tell_threshold), "anecdotes": anecdotes
    }

PERSONAS = [
    make_persona(
        "p_maya", "Maya Santos", "multi_site",
        "Owns two locations, 11 staff; tracks CAC weekly; pragmatic with budgets.",
        ["data-first", "pragmatic"],
        {"cac_volatility": 1.0, "admin_overhead": 0.3, "scheduling_glitch": 0.2},
        {"cac_volatility": "cut ad spend + staff outreach", "admin_overhead": "late-night ops"},
        80.0, 0.55, [ANEC[0], ANEC[1], ANEC[2]]
    ),
    make_persona(
        "p_andre", "Andre Kim", "solo_studio",
        "Single studio; relies on ClassPass & promos; often overextended.",
        ["optimistic", "overextended"],
        {"post_promo_churn": 1.0, "cac_volatility": 0.5},
        {"post_promo_churn": "manual check-ins", "cac_volatility": "flash discounts"},
        50.0, 0.50, [ANEC[3], ANEC[1]]
    ),
    make_persona(
        "p_rita", "Rita Okoye", "premium_pt",
        "High-touch PT studio; referral pipeline has plateaued.",
        ["meticulous", "relationship-led"],
        {"referral_stagnation": 1.0, "admin_overhead": 0.4},
        {"referral_stagnation": "scripted ask + partner salons"},
        120.0, 0.60, [ANEC[4], ANEC[2]]
    ),
]

# add 9 lightweight to reach 12
for i in range(9):
    seg = random.choice(["solo_studio", "multi_site", "premium_pt"])
    base = {
        "solo_studio": {"post_promo_churn": 0.8, "admin_overhead": 0.4},
        "multi_site": {"cac_volatility": 0.9, "admin_overhead": 0.4, "scheduling_glitch": 0.2},
        "premium_pt": {"referral_stagnation": 0.8, "admin_overhead": 0.3},
    }[seg]
    PERSONAS.append(
        make_persona(
            f"p_auto_{i}", f"Auto Persona {i+1}", seg,
            f"Owner of a {SEG_LABEL[seg]}; pragmatic and time-strapped.",
            ["busy", "direct"],
            base,
            {list(base.keys())[0]: "manual workaround"},
            random.choice([50.0, 80.0, 120.0]),
            random.uniform(0.45, 0.7),
            random.sample(ANEC, 3),
        )
    )

FLASH_ITEMS = [
    {
        "fid":"f1","segment_hint":"multi_site",
        "bio":"Two-site gym serving suburban families.",
        "status":"Revenue steady but demand swings with ads; team often backfills with phones.",
        "challenges":"Managing volatile lead flow; keeping classes full across both sites."
    },
    {
        "fid":"f2","segment_hint":"solo_studio",
        "bio":"One-room studio with owner-operator.",
        "status":"Intro offer sells well; few convert to paid.",
        "challenges":"Post-promo churn; too many discount-seekers."
    },
    {
        "fid":"f3","segment_hint":"premium_pt",
        "bio":"High-end PT boutique; 6 trainers.",
        "status":"Referral partners cooled off this year.",
        "challenges":"Referral stagnation; pipeline feels fragile."
    },
    {
        "fid":"f4","segment_hint":"solo_studio",
        "bio":"Yoga-pilates hybrid studio.",
        "status":"Manual payroll corrections every week.",
        "challenges":"Admin overhead drains owner time."
    },
    {
        "fid":"f5","segment_hint":"multi_site",
        "bio":"Urban gym with peak-hour crunch.",
        "status":"Occasional double-bookings in calendar tool at 6–8pm.",
        "challenges":"Minor scheduling glitches; reputation risk if visible to members."
    },
    {
        "fid":"f6","segment_hint":"solo_studio",
        "bio":"Bootcamp studio popular in spring/summer.",
        "status":"CPC spikes killed trial flow last month.",
        "challenges":"Paid acquisition volatility, seasonality."
    },
    {
        "fid":"f7","segment_hint":"premium_pt",
        "bio":"Trainer-led semi-private sessions; high retention once onboarded.",
        "status":"Attendance dips without reminders.",
        "challenges":"Keeping show-up rates high; consistent referrals."
    },
    {
        "fid":"f8","segment_hint":"multi_site",
        "bio":"City + suburbs locations.",
        "status":"$99 promo pulls volume but many cancel after it ends.",
        "challenges":"Post-promo churn; matching offer to the right audience."
    },
    {
        "fid":"f9","segment_hint":"solo_studio",
        "bio":"Pilates studio with 3 part-time contractors.",
        "status":"Owner exports CSVs to fix payroll each Friday.",
        "challenges":"Admin overhead; brittle workflows."
    },
    {
        "fid":"f10","segment_hint":"premium_pt",
        "bio":"Boutique PT; relies on word-of-mouth.",
        "status":"Staff skip referral script; feels awkward.",
        "challenges":"Referral stagnation; team enablement."
    },
]

# Channel IDs (internal) → nice labels (UI)
CHANNELS = {
    "email_list": {"label": "Email List", "yield": 0.6, "bias": {"premium_pt": 0.1, "multi_site": 0.5, "solo_studio": 0.4}},
    "cold_dm":    {"label": "Cold DMs", "yield": 0.4, "bias": {"premium_pt": 0.2, "multi_site": 0.4, "solo_studio": 0.4}},
    "forums":     {"label": "Industry Forums", "yield": 0.5, "bias": {"premium_pt": 0.2, "multi_site": 0.3, "solo_studio": 0.5}},
    "sidewalk":   {"label": "Sidewalk Intercepts", "yield": 0.3, "bias": {"premium_pt": 0.1, "multi_site": 0.2, "solo_studio": 0.7}},
}
CHANNEL_ORDER = ["email_list", "cold_dm", "forums", "sidewalk"]

# =============== Core engine ===============

OPEN_PREFIXES = (
    "tell me about", "walk me through", "how did", "what happened", "when was the last",
    "why", "what else", "how do you", "how often"
)
LEADING_PHRASES = ("would you", "if i built", "don’t you think", "shouldn’t", "isn’t it")
FUTUREY = ("would you pay", "will you", "would you use")

def classify_question(q: str):
    s = (q or "").strip().lower()
    return {
        "is_open": any(s.startswith(p) for p in OPEN_PREFIXES) or (s.endswith("?") and not s.startswith("do ") and not s.startswith("is ")),
        "is_leading": any(p in s for p in LEADING_PHRASES),
        "is_solutioning": ("if i built" in s) or ("my product" in s) or ("our app" in s),
        "is_past_behavior": any(k in s for k in ("last time","how did you","what happened","walk me through")),
        "is_future_hypo": any(p in s for p in FUTUREY),
    }

def init_session():
    st.session_state.sim = {
        "market": SEED_MARKET_ID,
        "tokens": 10,
        "booked": [],
        "interviews": {},     # pid -> {log, trust, evidence, persona, step, finished, learnings}
        "coverage": {"channel_counts": {}, "segment_counts": {}},
        "flashes_opened": [],
        "synthesis": {},
        "started": False,
    }

def get_persona(pid):
    for p in PERSONAS:
        if p["pid"] == pid: return p
    raise KeyError("persona not found")

def sample_personas_by_allocation(allocation):
    draws = max(0, int(sum(allocation.values())))
    if draws == 0:
        return []
    segment_bias = {k: 0.0 for k in ("solo_studio","multi_site","premium_pt")}
    for ch, toks in allocation.items():
        if toks <= 0: continue
        for seg, w in CHANNELS.get(ch, {}).get("bias", {}).items():
            segment_bias[seg] += float(w) * float(toks)
    if all(v == 0.0 for v in segment_bias.values()):
        segment_bias = {k: 1.0 for k in ("solo_studio","multi_site","premium_pt")}
    total = sum(max(v, 0.01) for v in segment_bias.values()) or 1.0
    weights = {seg: max(v, 0.01)/total for seg, v in segment_bias.items()}
    segments = list(weights.keys())
    pool = PERSONAS[:]; random.shuffle(pool)
    chosen = []
    for _ in range(min(8, draws)):
        seg_pick = random.choices(segments, weights=[weights[s] for s in segments])[0]
        cand = [p for p in pool if p["segment"] == seg_pick and p["pid"] not in chosen] or [p for p in pool if p["pid"] not in chosen]
        if not cand: break
        chosen.append(cand[0]["pid"])
    return chosen

def gen_response(p, trust, qmeta):
    keys = list(PAINS.keys())
    weights = []
    for k in keys:
        base = PAINS[k]["base_freq"] * 0.6 + p["pains"].get(k, 0.0) * 0.4
        weights.append(max(0.01, base))
    pain_key = random.choices(keys, weights=weights)[0]
    pain = PAINS[pain_key]
    noise = 1 - trust
    sev = max(0, min(1, pain["base_severity"] * (0.6 + 0.7 * p["pains"].get(pain_key, 0.6)) + random.uniform(-0.2, 0.2) * noise))
    freq_bins = ["ad-hoc","monthly","weekly","daily"]
    base_idx = 1 + (1 if pain["base_freq"]>0.45 else 0) + (1 if p["pains"].get(pain_key,0)>0.7 else 0)
    idx = max(0, min(3, base_idx + (1 if random.random() < (0.2*noise) else 0) - (1 if random.random()< (0.1*trust) else 0)))
    freq = freq_bins[idx]
    reveals_cost = trust >= p["tell_threshold"]
    spend_hint = f"${int(p['spend_ceiling'])} cap" if reveals_cost else "unclear"
    workaround = p["workaround"].get(pain_key, "manual work")
    anecdote = random.choice(p["anecdotes"]) if p.get("anecdotes") else ""
    if qmeta.get("is_past_behavior") or trust >= p["tell_threshold"]:
        resp = f"{anecdote} Pain: {pain['label']}. Happens {freq}. We do {workaround}."
    else:
        resp = f"{anecdote}" if random.random() > 0.4 else f"Yeah, {pain['label']} shows up sometimes."
    structured = {
        "pain_key": pain_key, "pain_label": pain["label"], "frequency": freq,
        "severity": round(sev,2), "workaround": workaround, "spend_hint": spend_hint,
    }
    return resp, structured

# -------- Guided Interview Flow --------
# At each step we show a mix of open vs. closed options. We track step count and finish at 4–10 Qs.
OPEN_BANK = [
    "Walk me through the last time this was painful.",
    "Tell me about your member acquisition in the past month.",
    "Why does that happen, in your view?",
    "What else have you tried when this happens?",
    "How often does this come up in a typical week?",
]
CLOSED_BANK = [
    "Would you pay $99 for a tool to fix this?",
    "Is scheduling your biggest problem?",
    "Do ads work well for you?",
    "Shouldn’t you just increase discounts?",
]

def next_question_options(step):
    # Early steps: more open. Later steps: mix changes.
    random.shuffle(OPEN_BANK); random.shuffle(CLOSED_BANK)
    if step <= 2:
        opts = OPEN_BANK[:2] + CLOSED_BANK[:2] + OPEN_BANK[2:3]
    else:
        opts = OPEN_BANK[:2] + CLOSED_BANK[:3]
    random.shuffle(opts)
    return opts[:5]

def handle_question(sim, pid, q_text):
    entry = sim["interviews"][pid]
    p = entry["persona"]
    meta = classify_question(q_text)
    # trust dynamics (hidden)
    t = entry["trust"]
    t += 0.06 if meta["is_open"] else -0.04
    t += 0.06 if meta["is_past_behavior"] else 0
    t -= 0.08 if meta["is_leading"] else 0
    t -= 0.08 if meta["is_solutioning"] else 0
    entry["trust"] = max(0.0, min(1.0, t))
    # response
    resp, structured = gen_response(p, entry["trust"], meta)
    entry["log"].append({"q": q_text, "a": resp})
    entry["step"] += 1
    # mark finish if long enough
    if entry["step"] >= random.randint(4, 10):
        entry["finished"] = True
    return resp

def synthesis():
    s = st.session_state.sim
    counts, sev, quotes, segments = {}, {}, {}, {}
    for pid, rec in s["interviews"].items():
        p = rec["persona"]
        segments[p["segment"]] = segments.get(p["segment"], 0) + 1
        for e in rec["log"]:
            # very light extraction: infer pain mention from canned generator
            # (already picked inside gen_response => we can’t see which; fake with CAC/referral churn split from text)
            # For MVP we weight by most common label from persona pains
            top_keys = sorted(p["pains"].keys(), key=lambda k: p["pains"][k], reverse=True)[:1]
            for k in top_keys:
                counts[k] = counts.get(k,0)+1
                sev[k] = sev.get(k,0.0) + (0.6 + 0.4 * p["pains"][k])
                quotes.setdefault(k, []).append(e["a"])
    avg_sev = {k: round(sev[k]/max(counts[k],1),2) for k in counts}
    top5 = sorted(counts.keys(), key=lambda k:(counts[k], avg_sev[k]), reverse=True)[:5]
    # channel bias
    channel_counts = s["coverage"].get("channel_counts", {})
    alerts, total = [], (sum(channel_counts.values()) or 1)
    for ch, n in channel_counts.items():
        if n/total > 0.6:
            label = CHANNELS[ch]["label"]
            alerts.append(f"Over-reliance on {label} ({int(100*n/total)}%)")
    out = {
        "counts": counts, "avg_sev": avg_sev, "top5": top5,
        "segments": segments, "quotes": {k: quotes.get(k,[])[:3] for k in top5},
        "alerts": alerts,
    }
    s["synthesis"] = out
    return out

def decide_and_score(problem_statement, next_test_plan):
    s = st.session_state.sim
    synth = s.get("synthesis") or {}
    true_top = "cac_volatility"
    chosen_top = synth.get("top5", [None])[0]
    signal_detection = 1.0 if chosen_top == true_top else (0.7 if true_top in synth.get("top5",[]) else 0.3)

    # interview craft proxies
    logs = sum((rec["log"] for rec in s["interviews"].values()), [])
    if logs:
        # assume ~60% open chosen if learner tends to click opens
        # give small boost for >6 total Qs
        total_qs = len(logs)
        open_ratio_guess = 0.6  # we don't store meta now; assume balance
    else:
        total_qs, open_ratio_guess = 0, 0.0
    craft = min(1.0, 0.7*open_ratio_guess + 0.3*(1.0 if total_qs >= 8 else total_qs/8))

    channels = s["coverage"].get("channel_counts", {})
    coverage_channels = len([c for c,n in channels.items() if n>0])
    largest_share = max((n for n in channels.values()), default=0) / max(sum(channels.values()) or 1, 1)
    coverage = 1.0 if (coverage_channels >= 3 and largest_share <= 0.6) else 0.6

    psq = 0.8 if ("trigger" in problem_statement.lower() and "impact" in problem_statement.lower()) else 0.5
    ntp = 0.8 if ("assumption" in next_test_plan.lower() and "threshold" in next_test_plan.lower()) else 0.5

    total = (
        0.30 * craft +
        0.15 * coverage +
        0.30 * signal_detection +
        0.15 * psq +
        0.10 * ntp
    )
    score = round(100 * min(max(total,0.0), 1.0))
    return {
        "score": score,
        "components": {
            "Interview Craft": round(craft,2),
            "Coverage": round(coverage,2),
            "Signal Detection": round(signal_detection,2),
            "Problem Statement Quality": round(psq,2),
            "Next Test Plan": round(ntp,2)
        },
        "chosen_top": chosen_top, "true_top": true_top
    }

# =============== UI ===============

st.set_page_config(page_title="Startup Simulation: Problem Discovery & Validation", page_icon="🧪", layout="wide")

if "sim" not in st.session_state:
    init_session()

st.title("Startup Simulation: Problem Discovery & Validation")

tabs = st.tabs(["Intro", "Target & Recruit", "Live Interviews", "Flash Bursts", "Synthesis + Decide", "Score"])

# --- Intro ---
with tabs[0]:
    st.subheader("Welcome")
    st.markdown(
        """
**What this is:** A hands-on simulation to practice the discovery habit loop:
**target → recruit → interview → code insights → decide**.

**Session length:** 75–90 minutes (solo).

**What you'll do:**
1. Choose who to target and how to recruit (allocate effort tokens).
2. Conduct short, live interviews (4–10 questions each).
3. Open flash data snippets to broaden coverage.
4. Synthesize signals; draft a **Problem Hypothesis** and a **Next Test Plan**.
5. Get a score and key lessons.

**Objectives:** Improve interview craft, detect real signals, and plan evidence-based next steps.
        """
    )
    if not st.session_state.sim["started"]:
        if st.button("Start Simulation"):
            st.session_state.sim["started"] = True
            # Auto-advance to Target & Recruit
            components.html(
                "<script>setTimeout(()=>{const t=window.parent.document.querySelectorAll('button[role=tab]'); if(t[1]) t[1].click();},60)</script>",
                height=0,
            )
            st.rerun()
    else:
        st.success("Simulation started — taking you to Target & Recruit…")
        components.html(
            "<script>const t=window.parent.document.querySelectorAll('button[role=tab]'); if(t[1]) t[1].click();</script>",
            height=0,
        )

# --- 1) Target & Recruit ---
with tabs[1]:
    if not st.session_state.sim["started"]:
        st.info("Go to the Intro tab and click **Start Simulation**.")
    else:
        st.subheader("Market Brief")
        st.info(SEED_MARKET_BRIEF)

        st.markdown(
            """
**You have 10 effort tokens** to recruit interviewees across channels.
Each channel differs in:
- **yield**: how likely you are to reach people quickly  
- **bias**: which sub-segments you’ll over-sample  
- **speed**: how fast responses land  

**Trade-off:** Spread tokens to cover segments, or concentrate for depth. Avoid over-reliance on a single channel.
            """
        )

        cols = st.columns(4)
        alloc = {}
        for i, ch_id in enumerate(CHANNEL_ORDER):
            with cols[i]:
                label = CHANNELS[ch_id]["label"]
                alloc[ch_id] = st.number_input(label, min_value=0, max_value=10, step=1, value=0, key=f"alloc_{ch_id}")

        total = sum(alloc.values())
        st.caption(f"Allocated: **{total}/10** tokens")
        book_btn = st.button("Book Personas", disabled=(total != 10))

        if book_btn:
            s = st.session_state.sim
            s["tokens"] = max(0, s["tokens"] - 10)
            booked = sample_personas_by_allocation(alloc)
            s["booked"] = booked
            for ch_id, n in alloc.items():
                s["coverage"]["channel_counts"][ch_id] = s["coverage"]["channel_counts"].get(ch_id, 0) + n
            # initialize interview state
            for pid in booked:
                p = get_persona(pid)
                s["interviews"][pid] = {
                    "log":[], "trust":0.5, "persona": deepcopy(p),
                    "step": 0, "finished": False, "learnings": ""
                }
            # Auto-advance to Live Interviews
            components.html(
                "<script>setTimeout(()=>{const t=window.parent.document.querySelectorAll('button[role=tab]'); if(t[2]) t[2].click();},80)</script>",
                height=0,
            )
            st.rerun()

# --- 2) Live Interviews ---
with tabs[2]:
    s = st.session_state.sim
    st.subheader("Live Interviews")
    if not s["booked"]:
        st.info("Book personas in **Target & Recruit** first.")
    else:
        # show booked personas summary at top
        with st.expander(f"Booked Personas ({len(s['booked'])})", expanded=True):
            for pid in s["booked"]:
                p = get_persona(pid)
                st.markdown(f"**{p['name']}** — {SEG_LABEL[p['segment']]}  \n_{p['bio']}_")

        pid = st.selectbox("Choose who to interview", s["booked"], format_func=lambda x: get_persona(x)["name"])
        entry = s["interviews"][pid]
        name = get_persona(pid)["name"]

        # show transcript (conversation only)
        st.markdown("#### Transcript")
        if entry["log"]:
            t = []
            for turn in entry["log"]:
                t.append(f"**You:** {turn['q']}")
                t.append(f"**{name}:** {turn['a']}")
            st.markdown("\n\n".join(t))
        else:
            st.caption("_No questions yet. Pick a question below to begin._")

        # question options (3–5 buttons)
        if not entry["finished"]:
            st.markdown("#### Ask a question")
            opts = next_question_options(entry["step"])
            cols = st.columns(len(opts))
            for i, q in enumerate(opts):
                with cols[i]:
                    if st.button(q, key=f"ask_{pid}_{entry['step']}_{i}"):
                        resp = handle_question(s, pid, q)
                        st.rerun()
            st.button("Thank person and end interview", key=f"end_{pid}",
                      on_click=lambda: s["interviews"][pid].update({"finished": True}))
        else:
            st.success("Interview finished.")
            # learnings summary
            entry["learnings"] = st.text_area("Summarize your key learnings from this interview",
                                              value=entry.get("learnings",""),
                                              placeholder="What was the top pain? How often does it occur? Any triggers or workarounds?")
            st.caption("You can switch personas at the top to run another interview.")

# --- 3) Flash Bursts (no follow-ups now)---
with tabs[3]:
    st.subheader("Flash Bursts (pick up to 5)")
    s = st.session_state.sim
    if "flash_deck" not in s:
        deck = FLASH_ITEMS[:]; random.shuffle(deck); s["flash_deck"] = deck[:10]
    choices = st.multiselect(
        "Choose items to open (max 5)",
        [f["fid"] for f in s["flash_deck"]],
        format_func=lambda fid: f"{fid} — {next(f['segment_hint'] for f in s['flash_deck'] if f['fid']==fid).replace('_',' ').title()}",
        max_selections=5
    )
    if choices:
        for fid in choices:
            f = next(x for x in s["flash_deck"] if x["fid"] == fid)
            st.info(f"**{fid}** — {SEG_LABEL[f['segment_hint']]}\n\n"
                    f"**Studio:** {f['bio']}\n\n"
                    f"**How they’re doing:** {f['status']}\n\n"
                    f"**Biggest challenges:** {f['challenges']}")

# --- 4) Synthesis + Decide ---
with tabs[4]:
    st.subheader("Synthesis")
    syn_btn = st.button("Run Synthesis")
    if syn_btn or st.session_state.sim.get("synthesis"):
        syn = synthesis()
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Top pains (counts | avg severity)**")
            if not syn["top5"]:
                st.write("_No signal yet. Ask more questions._")
            for k in syn["top5"]:
                st.write(f"- {PAINS[k]['label']}: {syn['counts'].get(k,0)} | {syn['avg_sev'].get(k,0)}")
        with col2:
            st.markdown("**Bias alerts**")
            if syn["alerts"]:
                for a in syn["alerts"]:
                    st.warning(a)
            else:
                st.success("No major channel bias detected.")
        st.markdown("**Evidence (sample quotes)**")
        for k in syn["top5"]:
            for q in syn["quotes"].get(k, []):
                st.caption(f"• {q}")

    st.markdown("---")
    st.subheader("Decide & Draft")
    st.caption("Use these examples as a guide—not a template to copy blindly.")
    st.markdown("**Problem Hypothesis example**  \n"
                "_Multi-Site Gym owners (who review ad performance weekly) experience **volatile paid acquisition** after CPC spikes, triggered by seasonality or platform changes. This causes empty classes mid-week and revenue misses; they currently rely on staff phone-banks as a workaround._")
    st.markdown("**Next Test Plan example**  \n"
                "_Assumption: owners will pre-commit to a weekly ‘volatility guardrail’ report if it prevents missed classes.  \n"
                "Method: concierge report for 10 gyms over 3 weeks.  \n"
                "Metric: % weeks with <10% variance vs. target; % owners asking to continue.  \n"
                "Success threshold: ≥70% hit the variance target AND ≥5/10 request a paid pilot._")

    if "drafts" not in st.session_state:
        st.session_state.drafts = {"ph": "", "ntp": ""}

    st.session_state.drafts["ph"] = st.text_area(
        "Your Problem Hypothesis",
        value=st.session_state.drafts["ph"],
        placeholder="Segment with trigger struggle with pain causing impact. They currently workaround ..."
    )
    st.session_state.drafts["ntp"] = st.text_area(
        "Your Next Test Plan",
        value=st.session_state.drafts["ntp"],
        placeholder="Assumption → Method → Metric → Sample size → Success threshold"
    )

# --- 5) Score (visual + written) ---
with tabs[5]:
    st.subheader("Score")
    if st.button("Compute Score"):
        # ensure synthesis is current
        if not st.session_state.sim.get("synthesis"):
            synthesis()
        res = decide_and_score(st.session_state.drafts.get("ph",""), st.session_state.drafts.get("ntp",""))

        # Spider chart
        labels = list(res["components"].keys())
        values = [res["components"][k] for k in labels]
        angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
        values += values[:1]
        angles += angles[:1]

        fig = plt.figure()
        ax = plt.subplot(111, polar=True)
        ax.plot(angles, values, linewidth=2)
        ax.fill(angles, values, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels)
        ax.set_yticklabels([])
        st.pyplot(fig)

        st.metric("Total Score", f"{res['score']}/100")
        st.markdown(f"**Chosen top signal:** {PAINS.get(res['chosen_top'],{'label':'—'}).get('label','—')}  "
                    f"| **Ground truth emphasis:** {PAINS['cac_volatility']['label']}")

        # Written breakdown
        st.markdown("### Component breakdown")
        for k, v in res["components"].items():
            pct = int(round(v*100))
            if pct >= 80:
                note = "Excellent"
            elif pct >= 60:
                note = "Good"
            elif pct >= 40:
                note = "Mixed"
            else:
                note = "Needs work"
            st.write(f"- **{k}:** {pct}/100 — {note}")

        st.markdown("### Key Lessons")
        st.markdown(
            """
- Favor past-behavior, open prompts early; avoid pitching.
- Balance channels to avoid sample bias; aim for ≥3 sources.
- Quantify the top problem with frequency + severity + quotes.
- Draft hypotheses with **who/trigger/consequence/workaround**; keep next tests narrow with clear thresholds.
            """
        )
