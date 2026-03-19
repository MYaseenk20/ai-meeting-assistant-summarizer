import streamlit as st
import json
import time
import sys
import os

# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MeetMind · Meeting Analyzer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --ink:    #0d0d0d;
    --paper:  #f5f0e8;
    --cream:  #ede8de;
    --accent: #c8401a;
    --muted:  #6b6560;
    --border: #d4cfc5;
    --card:   #ffffff;
    --green:  #1a6b45;
    --blue:   #1a3d6b;
    --amber:  #8a5a00;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--paper) !important;
    color: var(--ink);
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem !important; padding-bottom: 4rem !important; max-width: 960px !important; }

/* ── Hero header ── */
.hero {
    text-align: center;
    padding: 3.5rem 0 2.5rem;
    border-bottom: 2px solid var(--ink);
    margin-bottom: 3rem;
}
.hero-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.5rem;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.4rem, 5vw, 4rem);
    font-weight: 800;
    line-height: 1.05;
    margin: 0 0 0.75rem;
    letter-spacing: -0.03em;
    color: var(--ink);
}
.hero p {
    font-size: 1rem;
    color: var(--muted);
    font-weight: 300;
    max-width: 480px;
    margin: 0 auto;
    line-height: 1.6;
}

/* ── Upload zone ── */
.stFileUploader > div {
    background: var(--cream) !important;
    border: 2px dashed var(--border) !important;
    border-radius: 4px !important;
    transition: border-color 0.2s;
}
.stFileUploader > div:hover {
    border-color: var(--accent) !important;
}

/* ── Radio buttons (output format) ── */
.stRadio > label {
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    display: block;
    margin-bottom: 0.5rem;
}
.stRadio > div {
    flex-direction: row !important;
    gap: 1rem;
}
.stRadio > div > label {
    background: var(--cream);
    border: 1.5px solid var(--border);
    border-radius: 2px;
    padding: 0.4rem 1rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    cursor: pointer;
    transition: all 0.15s;
    color: var(--ink);
}
.stRadio > div > label:hover { border-color: var(--ink); }

/* ── Primary button ── */
.stButton > button {
    background: var(--ink) !important;
    color: var(--paper) !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.04em !important;
    border: none !important;
    border-radius: 3px !important;
    padding: 0.7rem 2.2rem !important;
    transition: background 0.15s !important;
    width: 100%;
}
.stButton > button:hover { background: var(--accent) !important; }

/* ── Section dividers ── */
.section-head {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--muted);
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.5rem;
    margin: 2.5rem 0 1.25rem;
}

/* ── Result cards ── */
.result-card {
    background: var(--card);
    border: 1.5px solid var(--border);
    border-radius: 4px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1.25rem;
    position: relative;
}
.result-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    border-radius: 4px 0 0 4px;
}
.card-green::before  { background: var(--green); }
.card-blue::before   { background: var(--blue); }
.card-amber::before  { background: var(--amber); }
.card-accent::before { background: var(--accent); }

.card-title {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.85rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
}
.card-green  .card-title { color: var(--green); }
.card-blue   .card-title { color: var(--blue); }
.card-amber  .card-title { color: var(--amber); }
.card-accent .card-title { color: var(--accent); }

.card-body {
    font-size: 0.92rem;
    color: var(--ink);
    line-height: 1.7;
}
.card-body ul { margin: 0; padding-left: 1.2rem; }
.card-body li { margin-bottom: 0.35rem; }

/* ── Meta badges ── */
.meta-row {
    display: flex; flex-wrap: wrap; gap: 0.6rem;
    margin-bottom: 1.25rem;
}
.meta-badge {
    background: var(--cream);
    border: 1px solid var(--border);
    border-radius: 2px;
    padding: 0.25rem 0.75rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: var(--ink);
}
.meta-badge strong {
    color: var(--muted);
    text-transform: uppercase;
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    margin-right: 0.35rem;
}

/* ── Summary block ── */
.summary-block {
    background: var(--ink);
    color: var(--paper);
    border-radius: 4px;
    padding: 2rem 2.25rem;
    margin-bottom: 1.5rem;
}
.summary-block .section-head {
    color: rgba(245,240,232,0.45);
    border-bottom-color: rgba(245,240,232,0.15);
}
.summary-block p { font-size: 1rem; line-height: 1.75; margin: 0; }

/* ── JSON output ── */
.stCodeBlock { border-radius: 4px !important; }

/* ── Error box ── */
.err-box {
    background: #fff0ee;
    border: 1.5px solid #f4b8ae;
    border-radius: 4px;
    padding: 1rem 1.25rem;
    color: var(--accent);
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
}

/* ── Spinner override ── */
.stSpinner { color: var(--accent) !important; }

/* ── Transcript preview ── */
.transcript-preview {
    background: var(--cream);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1rem 1.25rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    color: var(--muted);
    line-height: 1.75;
    max-height: 220px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-word;
}
</style>
""", unsafe_allow_html=True)

# ─── Hero ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-label">Powered by LangGraph</div>
    <h1>MeetMind</h1>
    <p>Drop in a transcript. Walk out with action items, decisions, and a crisp summary.</p>
</div>
""", unsafe_allow_html=True)

# ─── Import graph (graceful fallback) ───────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_graph():
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from langgraph.checkpoint.memory import MemorySaver
        from graph import build_graph          # your build_graph module
        memory = MemorySaver()
        return build_graph().compile(checkpointer=memory)
    except Exception as e:
        return None, str(e)

graph_result = load_graph()
graph_obj    = graph_result if not isinstance(graph_result, tuple) else None
graph_err    = None if not isinstance(graph_result, tuple) else graph_result[1]

# ─── Input columns ──────────────────────────────────────────────────────────
col_upload, col_opts = st.columns([3, 2], gap="large")

with col_upload:
    st.markdown('<div class="section-head">Transcript</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Upload a .txt file",
        type=["txt"],
        label_visibility="collapsed",
    )

    sample_transcript = """[09:00] Sarah Chen: Let's kick off Q4 planning. We need the product roadmap finalized this week.
[09:02] Marcus Rodriguez: I'll own the mobile push notifications spec. Will have it done by Wednesday EOD.
[09:04] Lisa Park: We've decided to migrate to the new Kubernetes cluster in November.
[09:06] James Wu: I'll prepare the board stakeholder deck — ready by Thursday 5pm.
[09:08] Sarah Chen: Official decision: product launch moves from Oct 28 to Nov 15 to give legal more time.
[09:10] Lisa Park: I'll have staging ready for QA by Monday. Coordinating with DevOps.
[09:12] James Wu: I'll set up the design agency kickoff call — confirm by tomorrow EOD.
[09:14] Sarah Chen: Everyone submit sprint estimates to me by Friday noon."""

    use_sample = st.checkbox("Use sample transcript instead", value=False)

    transcript_text = ""
    if use_sample:
        transcript_text = sample_transcript
    elif uploaded:
        transcript_text = uploaded.read().decode("utf-8", errors="replace")

    if transcript_text:
        st.markdown('<div class="section-head" style="margin-top:1.25rem;">Preview</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="transcript-preview">{transcript_text[:1200]}{"…" if len(transcript_text) > 1200 else ""}</div>', unsafe_allow_html=True)

with col_opts:
    st.markdown('<div class="section-head">Output Format</div>', unsafe_allow_html=True)
    output_target = st.radio(
        "Output format",
        options=["slack", "notion", "json"],
        label_visibility="collapsed",
        horizontal=True,
    )

    st.markdown('<div class="section-head" style="margin-top:1.75rem;">Thread ID</div>', unsafe_allow_html=True)
    thread_id = st.text_input(
        "Thread ID",
        value="meeting-001",
        label_visibility="collapsed",
        placeholder="meeting-001",
        help="LangGraph checkpoint thread identifier",
    )

    st.markdown('<div style="margin-top:1.75rem;"></div>', unsafe_allow_html=True)
    run_btn = st.button("Analyze Transcript →", disabled=not bool(transcript_text))

# ─── Run pipeline ────────────────────────────────────────────────────────────
if run_btn and transcript_text:

    if graph_obj is None:
        # ── DEMO MODE (graph not importable) ──
        st.markdown('<div class="section-head" style="margin-top:2rem;">Demo Output</div>', unsafe_allow_html=True)
        st.info("⚡ **Demo mode** — graph modules not found. Showing simulated output.", icon="ℹ️")

        demo_result = {
            "meeting_meta": {
                "title": "Q4 Planning Kickoff",
                "date": "2024-10-21",
                "participants": ["Sarah Chen", "Marcus Rodriguez", "Lisa Park", "James Wu"],
                "duration_minutes": 14,
            },
            "action_items": [
                {"owner": "Marcus Rodriguez", "task": "Complete mobile push notifications spec", "due": "Wednesday EOD"},
                {"owner": "James Wu",          "task": "Prepare board stakeholder deck",          "due": "Thursday 5pm"},
                {"owner": "Lisa Park",          "task": "Have staging ready for QA",               "due": "Monday"},
                {"owner": "James Wu",          "task": "Set up design agency kickoff call",        "due": "Tomorrow EOD"},
                {"owner": "All",               "task": "Submit sprint estimates to Sarah",         "due": "Friday noon"},
            ],
            "decisions": [
                "Migrate to new Kubernetes cluster in November",
                "Product launch moved from Oct 28 → Nov 15 (legal review buffer)",
            ],
            "follow_ups": [
                "Lisa Park to coordinate with DevOps on staging environment",
                "Sarah Chen to confirm all sprint estimates received",
            ],
            "summary": (
                "The Q4 planning kickoff aligned the team on key deadlines and two major decisions: "
                "the product launch shifts to Nov 15, and the Kubernetes migration is scheduled for November. "
                "Five concrete action items were assigned with clear owners and due dates. "
                "Staging preparation and sprint estimation are the immediate next steps."
            ),
        }
        result = demo_result

    else:
        initial_state = {
            "raw_transcript": transcript_text,
            "output_target": output_target,
            "meeting_meta": None,
            "action_items": [],
            "decisions": [],
            "follow_ups": [],
            "summary": None,
            "final_output": None,
            "errors": [],
        }
        config = {"configurable": {"thread_id": thread_id}}

        with st.spinner("Running pipeline…"):
            try:
                result = graph_obj.invoke(initial_state, config=config)
            except Exception as e:
                st.markdown(f'<div class="err-box">Pipeline error: {e}</div>', unsafe_allow_html=True)
                st.stop()

    # ── Render errors (if any) ───────────────────────────────────────────────
    if result.get("errors"):
        for err in result["errors"]:
            st.markdown(f'<div class="err-box">⚠ {err}</div>', unsafe_allow_html=True)

    # ── Summary ─────────────────────────────────────────────────────────────
    if result.get("summary"):
        st.markdown(f"""
        <div class="summary-block">
            <div class="section-head">Executive Summary</div>
            <p>{result["summary"]}</p>
        </div>
        """, unsafe_allow_html=True)

    # ── Metadata ────────────────────────────────────────────────────────────
    meta = result.get("meeting_meta") or {}
    if meta:
        parts  = meta.get("participants") or []
        badges = "".join([
            f'<span class="meta-badge"><strong>Title</strong>{meta.get("title","—")}</span>',
            f'<span class="meta-badge"><strong>Date</strong>{meta.get("date","—")}</span>',
            f'<span class="meta-badge"><strong>Duration</strong>{meta.get("duration_minutes","—")} min</span>',
        ] + [f'<span class="meta-badge">{p}</span>' for p in parts])
        st.markdown(f'<div class="meta-row">{badges}</div>', unsafe_allow_html=True)

    # ── Three columns: actions / decisions / follow-ups ──────────────────────
    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        items = result.get("action_items") or []
        def _action_row(a):
            due = (" <em>(" + a.get("due") + ")</em>") if isinstance(a, dict) and a.get("due") else ""
            if isinstance(a, dict):
                return f"<li><strong>{a.get('owner', '?')}</strong> — {a.get('task', '')}{due}</li>"
            return f"<li>{a}</li>"
        rows = "".join(_action_row(a) for a in items)
        st.markdown(f"""
        <div class="result-card card-blue">
            <div class="card-title">Action Items ({len(items)})</div>
            <div class="card-body"><ul>{rows or "<li>None found</li>"}</ul></div>
        </div>""", unsafe_allow_html=True)

    with c2:
        decisions = result.get("decisions") or []
        rows = "".join(
            f"<li>{d.get('decision') if isinstance(d, dict) else d}</li>"
            for d in decisions
        )
        st.markdown(f"""
        <div class="result-card card-accent">
            <div class="card-title">Decisions ({len(decisions)})</div>
            <div class="card-body"><ul>{rows or "<li>None found</li>"}</ul></div>
        </div>""", unsafe_allow_html=True)

    with c3:
        follow_ups = result.get("follow_ups") or []
        rows = "".join(
            f"<li>{f.get('item') if isinstance(f, dict) else f}</li>"
            for f in follow_ups
        )
        st.markdown(f"""
        <div class="result-card card-green">
            <div class="card-title">Follow-ups ({len(follow_ups)})</div>
            <div class="card-body"><ul>{rows or "<li>None found</li>"}</ul></div>
        </div>""", unsafe_allow_html=True)

    # ── Raw JSON (if json mode or user wants it) ─────────────────────────────
    st.markdown('<div class="section-head" style="margin-top:2rem;">Raw Output</div>', unsafe_allow_html=True)
    with st.expander("View full JSON result"):
        st.json(result)

    # ── Download ─────────────────────────────────────────────────────────────
    st.download_button(
        label="⬇ Download JSON",
        data=json.dumps(result, indent=2, default=str),
        file_name=f"meeting_summary_{thread_id}.json",
        mime="application/json",
    )

elif not transcript_text:
    st.markdown("""
    <div style="text-align:center; padding: 3rem 0; color: var(--muted, #6b6560);">
        <div style="font-size:2.5rem; margin-bottom:0.75rem;">📄</div>
        <div style="font-family:'DM Mono',monospace; font-size:0.8rem; letter-spacing:0.15em; text-transform:uppercase;">
            Upload a transcript or enable the sample to get started
        </div>
    </div>
    """, unsafe_allow_html=True)