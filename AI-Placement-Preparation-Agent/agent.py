import re

def _number(text, patterns, default):
    for pattern in patterns:
        m = re.search(pattern, text, re.I)
        if m:
            return int(m.group(1))
    return default

def parse_student_message(text):
    t = text.lower()
    target = "Software Developer (SDE)"
    if "data scientist" in t or "data science" in t:
        target = "Data Scientist"
    elif "web developer" in t:
        target = "Web Developer"

    online_days = _number(text, [r"test in (\d+)\s*days?", r"online test.*?(\d+)\s*days?"], 5)
    interview_days = _number(text, [r"interview in (\d+)\s*days?", r"interview.*?(\d+)\s*days?"], 12)
    hours = _number(text, [r"(\d+(?:\.\d+)?)\s*hours?", r"study for (\d+(?:\.\d+)?)"], 3)

    def conf(area, aliases, default):
        for a in aliases:
            m = re.search(a + r".{0,30}?(\d{1,3})\s*%", text, re.I)
            if m:
                return min(100, int(m.group(1)))
        return default

    confidence = {
        "DSA": conf("DSA", ["DSA", "data structures"], 40),
        "Aptitude": conf("Aptitude", ["aptitude"], 65),
        "Core Subjects": conf("Core Subjects", ["core subjects", "core"], 50),
        "Resume and HR": conf("Resume", ["resume", "HR"], 70),
    }
    return {
        "target_role": target,
        "online_test_days": online_days,
        "interview_days": interview_days,
        "available_hours": float(hours),
        "confidence": confidence,
        "source_message": text,
    }

def generate_agent_response(profile, priorities, plan):
    top = priorities[0]
    plan_text = ", ".join(f"{x['area']} {x['minutes']} min" for x in plan)
    return (
        f"Got it. I extracted your placement situation and built a time-boxed plan. "
        f"**{top['area']}** is currently the highest-priority area with a score of "
        f"{top['score']:.1f}/100. Today's plan: {plan_text}. "
        f"The priority is calculated from urgency, skill gap and role importance rather than invented by the chat model."
    )
