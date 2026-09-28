import streamlit as st
from datetime import date, datetime
from agent import parse_student_message, generate_agent_response
from tools import (
    calculate_priorities,
    build_study_plan,
    replan_schedule,
    start_focus_timer,
    get_current_plan,
)

st.set_page_config(page_title="PrepAgent", page_icon="🤖", layout="wide")

# ---------- Styling ----------
st.markdown("""
<style>
.stApp { background: #07111f; color: #e8eef8; }
.block-container { padding-top: 1.2rem; max-width: 1250px; }
h1,h2,h3 { letter-spacing: -0.02em; }
.small-muted { color:#91a0b5; font-size:.9rem; }
.metric-card { background:#0d1a2b; border:1px solid #1b304a; border-radius:14px; padding:18px; }
.priority-card { background:#0c1928; border:1px solid #20364f; border-radius:14px; padding:16px; margin:8px 0; }
.chat-user { background:#0f5ec7; padding:13px 16px; border-radius:14px 14px 4px 14px; margin:8px 0; }
.chat-agent { background:#101f31; border:1px solid #20364f; padding:13px 16px; border-radius:14px 14px 14px 4px; margin:8px 0; }
</style>
""", unsafe_allow_html=True)

# ---------- State ----------
if "profile" not in st.session_state:
    st.session_state.profile = None
if "priorities" not in st.session_state:
    st.session_state.priorities = []
if "plan" not in st.session_state:
    st.session_state.plan = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "focus" not in st.session_state:
    st.session_state.focus = None
if "last_update" not in st.session_state:
    st.session_state.last_update = ""

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 🤖 PrepAgent")
    st.caption("AI Placement Preparation Agent")
    page = st.radio(
        "Navigation",
        ["Chat", "Dashboard", "Study Plan", "Focus Timer", "Mock Test", "Progress"],
        label_visibility="collapsed",
    )
    st.divider()
    if st.session_state.profile:
        p = st.session_state.profile
        st.markdown("**Current profile**")
        st.write(f"**Target:** {p['target_role']}")
        st.write(f"**Study time:** {p['available_hours']} hr/day")
        st.write(f"**Online test:** {p['online_test_days']} days")
        st.write(f"**Interview:** {p['interview_days']} days")
    else:
        st.info("Describe your placement situation in Chat to create a profile.")

def ensure_plan():
    if st.session_state.profile is None:
        return
    if not st.session_state.priorities:
        st.session_state.priorities = calculate_priorities(st.session_state.profile)
    if not st.session_state.plan:
        st.session_state.plan = build_study_plan(
            st.session_state.priorities,
            st.session_state.profile["available_hours"]
        )

# ---------- Chat ----------
if page == "Chat":
    st.title("Chat with your AI Agent")
    st.caption("Describe your placement situation in natural language. PrepAgent will extract the details, calculate priorities and build a plan.")

    for m in st.session_state.messages:
        cls = "chat-user" if m["role"] == "user" else "chat-agent"
        st.markdown(f'<div class="{cls}">{m["content"]}</div>', unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        msg = st.text_area(
            "Your message",
            placeholder="Example: I have an online test in 5 days and an interview in 12. My DSA confidence is 40% and I can study 3 hours today. What should I do?",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Send ➜", use_container_width=True)

    if submitted and msg.strip():
        st.session_state.messages.append({"role": "user", "content": msg.strip()})
        profile = parse_student_message(msg)
        st.session_state.profile = profile
        st.session_state.priorities = calculate_priorities(profile)
        st.session_state.plan = build_study_plan(
            st.session_state.priorities, profile["available_hours"]
        )
        response = generate_agent_response(profile, st.session_state.priorities, st.session_state.plan)
        st.session_state.messages.append({"role": "agent", "content": response})
        st.rerun()

    if st.session_state.profile:
        st.subheader("Understood profile")
        p = st.session_state.profile
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Target role", p["target_role"])
        c2.metric("Online test", f"{p['online_test_days']} days")
        c3.metric("Interview", f"{p['interview_days']} days")
        c4.metric("Study time", f"{p['available_hours']} hr")

# ---------- Dashboard / priorities ----------
elif page == "Dashboard":
    ensure_plan()
    st.title("Preparation Priorities")
    st.caption("Areas are ranked using urgency, skill gap and role importance.")
    if not st.session_state.profile:
        st.warning("Start in Chat with a natural-language placement situation.")
    else:
        for i, row in enumerate(st.session_state.priorities, 1):
            cols = st.columns([.5, 2.4, 1, 1, 1, .8])
            cols[0].write(f"**{i}**")
            cols[1].write(f"**{row['area']}**")
            cols[2].write(row["urgency"])
            cols[3].write(row["skill_gap"])
            cols[4].write(row["role_importance"])
            cols[5].markdown(f"**{row['score']:.1f}**")
        st.divider()
        st.info("Score = 0.40 × Urgency + 0.35 × Skill gap + 0.25 × Role importance")
        st.subheader("Why these priorities?")
        for r in st.session_state.priorities:
            st.markdown(
                f"**{r['area']} — {r['score']:.1f}/100**  \n"
                f"Urgency {r['urgency']}, skill gap {r['skill_gap']}, role importance {r['role_importance']}."
            )

# ---------- Study plan ----------
elif page == "Study Plan":
    ensure_plan()
    st.title(f"Your {st.session_state.profile['available_hours'] if st.session_state.profile else 0}-Hour Study Plan (Today)")
    if not st.session_state.plan:
        st.warning("Create a profile from Chat first.")
    else:
        for item in st.session_state.plan:
            st.markdown(
                f"""<div class="priority-card">
                <b>{item['time']}</b> &nbsp; <b>{item['area']}</b><br>
                <span class="small-muted">{item['topic']} · {item['minutes']} minutes</span>
                </div>""",
                unsafe_allow_html=True,
            )
        st.caption("The plan never allocates more time than the student's available hours.")

# ---------- Focus ----------
elif page == "Focus Timer":
    ensure_plan()
    st.title("Focus Session")
    st.caption("Stay focused and productive.")
    topic = st.selectbox(
        "Topic",
        [x["area"] for x in st.session_state.priorities] if st.session_state.priorities else ["DSA Practice"]
    )
    minutes = st.slider("Session length (minutes)", 5, 120, 25, 5)
    c1,c2,c3 = st.columns(3)
    if c1.button("▶ Start", use_container_width=True):
        st.session_state.focus = start_focus_timer(topic, minutes)
    if c2.button("⏸ Pause", use_container_width=True) and st.session_state.focus:
        st.session_state.focus["status"] = "Paused"
    if c3.button("↻ Reset", use_container_width=True):
        st.session_state.focus = None
    if st.session_state.focus:
        f = st.session_state.focus
        st.markdown(f"<h1 style='text-align:center;font-size:72px'>{f['minutes']:02d}:00</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:center'>{f['topic']} · {f['status']}</h3>", unsafe_allow_html=True)
    else:
        st.info("Choose a topic and start a focus session.")

# ---------- Mock test ----------
elif page == "Mock Test":
    st.title("Aptitude Mock Test")
    st.caption("Timed practice session")
    area = st.selectbox("Area", ["Aptitude", "Coding"])
    level = st.selectbox("Level", ["Easy", "Medium", "Hard"])
    if "mock_q" not in st.session_state:
        st.session_state.mock_q = 1
    if st.button("Start / Restart Mock Test"):
        st.session_state.mock_q = 1
    st.markdown(f"### Question {st.session_state.mock_q} of 10")
    if area == "Aptitude":
        st.write("A can complete a task in 12 days and B in 18 days. If they work together, approximately how many days will the task take?")
        ans = st.radio("Answer", ["6 days", "7.2 days", "8 days", "9 days"])
    else:
        st.write("Which data structure provides average O(1) lookup by key?")
        ans = st.radio("Answer", ["Stack", "Queue", "Hash table", "Linked list"])
    if st.button("Next →"):
        st.session_state.mock_q = min(10, st.session_state.mock_q + 1)
        st.rerun()

# ---------- Progress / replanning ----------
elif page == "Progress":
    ensure_plan()
    st.title("Update & Replan")
    st.caption("Tell the agent what happened and it will carry over missed work.")
    update = st.text_area(
        "Progress update",
        placeholder="Example: I only finished 30 minutes of DSA and skipped aptitude.",
    )
    if st.button("Replan Schedule"):
        if not st.session_state.profile:
            st.error("Create a profile first.")
        else:
            st.session_state.plan, st.session_state.priorities = replan_schedule(
                st.session_state.profile,
                st.session_state.priorities,
                st.session_state.plan,
                update,
            )
            st.session_state.last_update = update
            st.success("Plan updated. Missed work was carried over and priorities recalculated.")
    if st.session_state.last_update:
        st.info(f"Latest update: {st.session_state.last_update}")
    if st.session_state.plan:
        st.subheader("Updated plan")
        for item in st.session_state.plan:
            st.markdown(f"**{item['time']} — {item['area']}** · {item['topic']} · {item['minutes']} min")

st.divider()
st.caption("Prototype implementation for Fundamentals of Artificial Intelligence — Assignment I")
