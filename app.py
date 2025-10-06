# Startup Simulation: Problem Discovery & Validation (Streamlit)
# --------------------------------------------------------------
# Run locally:
#   pip install -r requirements.txt
#   streamlit run app.py
# --------------------------------------------------------------

import json, random
from copy import deepcopy
import streamlit as st
import streamlit.components.v1 as components

# =============== Seed market & data ===============

SEED_MARKET_ID = "independent_gym_owners"
SEED_MARKET_BRIEF = (
    "Independent gym owners managing acquisition volatility, churn after promos, "
    "and admin overhead. Sub-segments: solo studios, multi-site gyms, premium PT studios."
)

PAINS = {
    "cac_volatility": {
        "key": "cac_volatility", "label": "Paid acquisition volatility",
        "base_freq": 0.62, "base_severity": 0.78,
        "notes": "Leads fluctuate with ads; weekly swings affect targets.",
    },
    "post_promo_churn": {
        "key": "post_promo_churn", "label": "Churn after intro promos",
        "base_freq": 0.47, "base_severity": 0.65,
        "notes": "Trial-to-paid conversion drops; discounts attract wrong users.",
    },
    "admin_overhead": {
        "key": "admin_overhead", "label": "Admin/payroll overhead",
        "base_freq": 0.36, "base_severity": 0.45,
        "notes": "Owner spends late nights on payroll/scheduling.",
    },
    "scheduling_glitch": {
        "key": "scheduling_glitch", "label": "Scheduling tool glitches",
        "base_freq": 0.22, "base_severity": 0.35,
        "notes": "Peak-hours hiccups; more nuisance than critical.",
    },
    "referral_stagnation": {
        "key": "referral_stagnation", "label": "Referral stagnation",
        "base_freq": 0.31, "base_severity": 0.50,
        "notes": "Word-of-mouth plateau; manual scripts required.",
    },
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
        "Owns 2 locations, 11 staff; tracks CAC weekly.",
        ["data-first", "pragmatic"],
        {"cac_volatility": 1.0, "admin_overhead": 0.3, "scheduling_glitch": 0.2},
        {"cac_volatility": "cut spend + staff outreach", "admin_overhead": "late-night ops"},
        80.0, 0.55, [ANEC[0], ANEC[1], ANEC[2]]
    ),
    make_persona(
        "p_andre", "Andre Kim", "solo_studio",
        "Single studio; relies on ClassPass & promos; conversion worries.",
        ["optimistic", "overextended"],
        {"post_promo_churn": 1.0, "cac_volatility": 0.5},
        {"post_promo_churn": "manual check-ins", "cac_volatility": "flash discounts"},
        50.0, 0.50, [ANEC[3], ANEC[1]]
    ),
    make_persona(
        "p_rita", "Rita Okoye", "premium_pt",
        "Premium PT studio; referrals plateauing.",
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
            f"Auto-generated {seg.replace('_',' ')} owner.",
            ["busy", "direct"],
            base,
            {list(base.keys())[0]: "manual workaround"},
            random.choice([50.0, 80.0, 120.0]),
            random.uniform(0.45, 0.7),
            random.sample(ANEC, 3),
        )
    )

FLASH_ITEMS = [
    {"fid":"f1","segment_hint":"multi_site","text":"Leads dropped 40% last month; team did phones all weekend.","pain_hint":"cac_volatility"},
    {"fid":"f2","segment_hint":"solo_studio","text":"Intro pass folks come twice then vanish.","pain_hint":"post_promo_churn"},
    {"fid":"f3","segment_hint":"premium_pt","text":"We used to get referrals from a physio partner—now crickets.","pain_hint":"referral_stagnation"},
    {"fid":"f4","segment_hint":"solo_studio","text":"Payroll always breaks if I add a contractor mid-cycle.","pain_hint":"admin_overhead"},
    {"fid":"f5","segment_hint":"multi_site","text":"Calendar shows double-booked slots at 6–8pm.","pain_hint":"scheduling_glitch"},
    {"fid":"f6","segment_hint":"solo_studio","text":"Google Ads CPC spike killed trial flow.","pain_hint":"cac_volatility"},
    {"fid":"f7","segment_hint":"premium_pt","text":"If I don’t text reminders, attendance dips.","pain_hint":None},
    {"fid":"f8","segment_hint":"multi_site","text":"$99 month promo—churn right after it ends.","pain_hint":"post_promo_churn"},
    {"fid":"f9","segment_hint":"solo_studio","text":"I export CSVs to fix payroll every Friday.","pain_hint":"admin_overhead"},
    {"fid":"f10","segment_hint":"premium_pt","text":"Referral script feels awkward; staff skip it.","pain_hint":"referral_stagnation"},
]

# Channel IDs (internal) → nice labels (UI)
CHANNELS = {
    "email_list": {"label": "Email list", "yield": 0.6, "bias": {"premium_pt": 0.1, "multi_site": 0.5, "solo_studio": 0.4}},
    "cold_dm":    {"label": "Cold DMs", "yield": 0.4, "bias": {"premium_pt": 0.2, "multi_site": 0.4, "solo_studio": 0.4}},
    "forums":     {"label": "Industry forums", "yield": 0.5, "bias": {"premium_pt": 0.2, "multi_site": 0.3, "solo_studio": 0.5}},
    "sidewalk":   {"label": "Sidewalk intercepts", "yield": 0.3, "bias": {"premium_pt": 0.1, "multi_site": 0.2, "solo_studio": 0.7}},
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
        "interviews": {},     # pid -> {log, trust, evidence, tags, persona}
        "coverage": {"channel_counts": {}, "segment_counts": {}},
        "flashes_opened": [],
        "flash_followups": {},
        "synthesis": {},
        "started": False,
    }

def get_persona(pid):
    for p in PERSONAS:
        if p["pid"] == pid: return p
    raise KeyError("persona not found")

def sample_personas_by_allocation(allocation):
    """Robust channel-biased sampling that never crashes."""
    draws = max(0, int(sum(allocation.values())))
    if draws == 0:
        return []

    # accumulate segment weights from channel biases
    segment_bias = {k: 0.0 for k in ("solo_studio","multi_site","premium_pt")}
    for ch, toks in allocation.items():
        if toks <= 0:
            continue
        ch_cfg = CHANNELS.get(ch, {})
        for seg, w in ch_cfg.get("bias", {}).items():
            segment_bias[seg] = segment_bias.get(seg, 0.0) + float(w) * float(toks)

    # fallback if all zeros
    if all(v == 0.0 for v in segment_bias.values()):
        segment_bias = {k: 1.0 for k in ("solo_studio","multi_site","premium_pt")}

    total = sum(max(v, 0.01) for v in segment_bias.values()) or 1.0
    # BUG FIX: include v in the comprehension!
    weights = {seg: max(v, 0.01)/total for seg, v in segment_bias.items()}
    segments = list(weights.keys())

    pool = PERSONAS[:]
    random.shuffle(pool)
    chosen = []
    for _ in range(min(8, draws)):
        seg_pick = random.choices(segments, weights=[weights[s] for s in segments])[0]
        cand = [p for p in pool if p["segment"] == seg_pick and p["pid"] not in chosen]
        if not cand:
            cand = [p for p in pool if p["pid"] not in chosen]
        if not cand:
            break
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
        "confidence": round(trust,2),
    }
    return resp, structured

def ask_question(pid, question_text):
    s = st.session_state.sim
    entry = s["interviews"][pid]
    p = entry["persona"]
    qmeta = classify_question(question_text)
    trust = entry["trust"]
    trust += 0.06 if qmeta["is_open"] else -0.04
    trust += 0.06 if qmeta["is_past_behavior"] else 0
    trust -= 0.08 if qmeta["is_leading"] else 0
    trust -= 0.08 if qmeta["is_solutioning"] else 0
    trust = max(0.0, min(1.0, trust))
    entry["trust"] = trust
    evid = entry["evidence"] + (0.08 if qmeta["is_open"] else 0.02)
    entry["evidence"] = min(1.0, evid)
    resp, strip = gen_response(p, trust, qmeta)
    entry["log"].append({"q": question_text, "meta": qmeta, "a": resp, "structured": strip})
    return resp, strip, round(trust,2)

def synthesis():
    s = st.session_state.sim
    counts, sev, quotes, segments = {}, {}, {}, {}
    for pid, rec in s["interviews"].items():
        p = rec["persona"]
        segments[p["segment"]] = segments.get(p["segment"], 0) + 1
        for e in rec["log"]:
            stp = e.get("structured") or {}
            k = stp.get("pain_key")
            if not k: continue
            counts[k] = counts.get(k,0)+1
            sev[k] = sev.get(k,0.0) + float(stp.get("severity",0))
            quotes.setdefault(k, []).append(e.get("a",""))
    avg_sev = {k: round(sev[k]/max(counts[k],1),2) for k in counts}
    top5 = sorted(counts.keys(), key=lambda k:(counts[k], avg_sev[k]), reverse=True)[:5]
    channel_counts = s["coverage"].get("channel_counts", {})
    alerts, total = [], (sum(channel_counts.values()) or 1)
    for ch, n in channel_counts.items():
        if n/total > 0.6:
            alerts.append(f"Over-reliance on {ch} ({int(100*n/total)}%)")
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
    qs = []
    for rec in s["interviews"].values():
        for e in rec["log"]:
            qs.append(e["meta"])
    if qs:
        open_rate = sum(1 for m in qs if m["is_open"]) / len(qs)
        leading_rate = sum(1 for m in qs if m["is_leading"] or m["is_solutioning"]) / len(qs)
    else:
        open_rate = 0.0; leading_rate = 1.0
    avg_trust = sum(rec["trust"] for rec in s["interviews"].values()) / max(len(s["interviews"]),1)
    channels = s["coverage"].get("channel_counts", {})
    coverage_channels = len([c for c,n in channels.items() if n>0])
    largest_share = max((n for n in channels.values()), default=0) / max(sum(channels.values()) or 1, 1)
    score = (
        0.30 * (1.0 if open_rate >= 0.7 else open_rate/0.7)
             * (1.0 if leading_rate <= 0.15 else max(0.0, 1 - (leading_rate-0.15)/0.35))
             * (avg_trust)
        + 0.15 * (1.0 if (coverage_channels >= 3 and largest_share <= 0.6) else 0.6)
        + 0.30 * signal_detection
        + 0.15 * (0.8 if ("trigger" in problem_statement.lower() and "impact" in problem_statement.lower()) else 0.5)
        + 0.10 * (0.8 if ("assumption" in next_test_plan.lower() and "threshold" in next_test_plan.lower()) else 0.5)
    )
    score = round(100 * min(max(score,0.0), 1.0))
    return {
        "score": score,
        "open_rate": round(open_rate,2),
        "leading_rate": round(leading_rate,2),
        "avg_trust": round(avg_trust,2),
        "channels_used": coverage_channels,
        "largest_channel_share": round(largest_share,2),
        "chosen_top": chosen_top, "true_top": true_top
    }

# =============== UI ===============

st.set_page_config(page_title="Startup Simulation: Problem Discovery & Validation", page_icon="🧪", layout="wide")

if "sim" not in st.session_state:
    init_session()

st.title("Startup Simulation: Problem Discovery & Validation")

# Tabs (we’ll auto-jump to Target & Recruit when Start is clicked)
tabs = st.tabs(["Intro", "Target & Recruit", "Live Interviews", "Flash Bursts", "Synthesis", "Decide & Score"])

# --- Intro ---
with tabs[0]:
    st.subheader("Welcome")
    st.markdown(
        """
**What this is:** A hands-on simulation to practice the discovery habit loop:
**target → recruit → interview → code insights → decide**.

**Session length:** 75–90 minutes (solo). One sitting is ideal.

**What you'll do:**
1. Choose who to target and how to recruit (allocate effort tokens).
2. Conduct short, live interviews (5–6 minutes each).
3. Open flash data snippets to boost segment coverage.
4. Synthesize: tag/code, review heatmaps, quotes, and bias alerts.
5. Decide: draft a **Problem Hypothesis** and a **Next Test Plan**; get a score.

**Objectives:** Improve interview craft, detect real signals (not noise), and make evidence-based next steps.
        """
    )
    if not st.session_state.sim["started"]:
        if st.button("Start Simulation"):
            st.session_state.sim["started"] = True
            # Inject tiny JS to click the second tab automatically.
            components.html(
                """
                <script>
                const tick = () => {
                  const tabs = window.parent.document.querySelectorAll('button[role="tab"]');
                  if (tabs && tabs.length > 1) { tabs[1].click(); }
                };
                setTimeout(tick, 50);
                </script>
                """,
                height=0,
            )
            st.rerun()
    else:
        st.success("Simulation started — moving you to Target & Recruit…")
        components.html(
            """
            <script>
            const tabs = window.parent.document.querySelectorAll('button[role="tab"]');
            if (tabs && tabs.length > 1) { tabs[1].click(); }
            </script>
            """,
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

**Trade-off:** spread tokens to cover segments, or concentrate for depth. Avoid over-reliance on a single channel.
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
            # init interviews
            for pid in booked:
                p = get_persona(pid)
                s["interviews"][pid] = {"log":[], "trust":0.5, "evidence":0.0, "tags":[], "persona": deepcopy(p)}
            st.success(f"Booked {len(booked)} personas.")
            if not booked:
                st.warning("No bookings yet — try redistributing tokens across more channels.")

        if st.session_state.sim["booked"]:
            st.markdown("**Booked personas:**")
            for pid in st.session_state.sim["booked"]:
                p = get_persona(pid)
                st.write(f"- {p['name']} ({p['segment']}) — {p['bio']}")

# --- 2) Live Interviews ---
with tabs[2]:
    st.subheader("Run your live micro-interviews (5–6 min each)")
    s = st.session_state.sim
    if not s["booked"]:
        st.info("Book personas in **Target & Recruit** first.")
    else:
        pid = st.selectbox("Pick persona", s["booked"], format_func=lambda x: get_persona(x)["name"])
        q = st.text_input("Ask a question (e.g., 'Walk me through the last time …')")
        c1, c2, c3 = st.columns([1,1,2])
        if c1.button("Ask"):
            if q.strip():
                resp, strip, trust = ask_question(pid, q)
                st.session_state.setdefault("transcripts", {}).setdefault(pid, "")
                name = get_persona(pid)['name']
                st.session_state["transcripts"][pid] += (
                    f"\n\n**You:** {q}\n\n**{name}:** {resp}\n*Trust:* {trust} — *Strip:* {strip}"
                )
        tag = c2.selectbox("Quick Tag", ["(choose)","pain","workaround","trigger","frequency","severity","cost","wtp","segment"])
        if c2.button("Add Tag") and tag != "(choose)":
            s["interviews"][pid]["tags"].append(tag)
            st.toast(f"Tagged: {tag}")
        st.markdown("#### Transcript")
        st.markdown(st.session_state.get("transcripts", {}).get(pid, "_Start asking to see transcript..._"))

# --- 3) Flash Bursts ---
with tabs[3]:
    st.subheader("Open 5 flash snippets (pick any)")
    s = st.session_state.sim
    if "flash_deck" not in s:
        deck = FLASH_ITEMS[:]
        random.shuffle(deck)
        s["flash_deck"] = deck[:10]

    choices = st.multiselect(
        "Choose up to 5 to open",
        [f["fid"] for f in s["flash_deck"]],
        format_func=lambda fid: f"{fid} ({next(f['segment_hint'] for f in s['flash_deck'] if f['fid']==fid)})",
        max_selections=5
    )

    if choices:
        for fid in choices:
            f = next(x for x in s["flash_deck"] if x["fid"] == fid)
            st.info(f"**{fid}** — {f['segment_hint']}\n\n> {f['text']}")
        st.markdown("---")
        st.caption("Optional: pick up to 3 opened items for one follow-up question each.")
        follow_targets = st.multiselect("Follow-up targets (max 3)", choices, max_selections=3, key="fu_targets")
        for i, fid in enumerate(follow_targets):
            with st.expander(f"Follow-up: {fid}"):
                fuq = st.text_input(f"Question {i+1}", key=f"fuq_{fid}")
                if st.button(f"Ask follow-up {i+1}", key=f"btn_fuq_{fid}"):
                    meta = classify_question(fuq)
                    clar = {}
                    if meta["is_open"] and ("how often" in fuq.lower() or meta["is_past_behavior"]):
                        clar["frequency"] = random.choice(["weekly","monthly","ad-hoc"])
                    if "pay" in fuq.lower() or "cost" in fuq.lower():
                        clar["wtp_band"] = random.choice(["$30–50","$50–70","$70–100","unclear"])
                    st.session_state.sim["flash_followups"][fid] = {"q": fuq, "meta": meta, "clar": clar}
                    st.success(f"Clarified: {clar}")

# --- 4) Synthesis ---
with tabs[4]:
    st.subheader("Synthesis Sprint")
    if st.button("Run Synthesis"):
        syn = synthesis()
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Top pains**")
            if not syn["top5"]:
                st.write("_No signal yet. Ask more questions._")
            for k in syn["top5"]:
                st.write(f"- {PAINS[k]['label']} ({k}): {syn['counts'].get(k,0)} hits | avg severity {syn['avg_sev'].get(k,0)}")
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

# --- 5) Decide & Score ---
with tabs[5]:
    st.subheader("Decide & Draft")
    ps = st.text_area("Problem Hypothesis",
                      placeholder="Segment with trigger struggle with pain causing impact. They currently workaround ... (WTP hint ...)")
    ntp = st.text_area("Next Test Plan",
                       placeholder="Assumption → Method (offer/concierge/ads) → Metric → Sample size → Success threshold")
    if st.button("Score"):
        if not st.session_state.sim.get("synthesis"):
            synthesis()
        res = decide_and_score(ps or "", ntp or "")
        st.metric("Total Score", f"{res['score']}/100")
        c1, c2, c3 = st.columns(3)
        c1.write(f"Open-question rate: **{res['open_rate']}**")
        c1.write(f"Leading/solutioning rate: **{res['leading_rate']}**")
        c1.write(f"Avg trust: **{res['avg_trust']}**")
        c2.write(f"Channels used: **{res['channels_used']}**")
        c2.write(f"Largest channel share: **{res['largest_channel_share']}**")
        c3.write(f"Chosen top: **{res['chosen_top']}** | True top: **{res['true_top']}**")
        st.download_button("Download session JSON",
                           data=json.dumps(st.session_state.sim, indent=2),
                           file_name="sim_session.json",
                           mime="application/json")
