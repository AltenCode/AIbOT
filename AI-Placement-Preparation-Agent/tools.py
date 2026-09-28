from datetime import datetime, timedelta

AREAS = {
    "DSA": {"role": 100},
    "Aptitude": {"role": 70},
    "Core Subjects": {"role": 80},
    "Resume and HR": {"role": 50},
}

def calculate_priorities(profile):
    rows = []
    confidence = profile.get("confidence", {})
    test_days = profile.get("online_test_days", 30)
    interview_days = profile.get("interview_days", 30)

    urgency_map = {
        "DSA": min(100, max(10, 100 - (test_days - 1) * 5)),
        "Aptitude": min(100, max(10, 100 - (test_days - 1) * 5)),
        "Core Subjects": min(100, max(10, 100 - (interview_days - 1) * 3)),
        "Resume and HR": min(100, max(10, 100 - (interview_days - 1) * 3)),
    }

    for area, meta in AREAS.items():
        skill_gap = 100 - int(confidence.get(area, 50))
        urgency = urgency_map[area]
        role_importance = meta["role"]
        score = 0.40 * urgency + 0.35 * skill_gap + 0.25 * role_importance
        rows.append({
            "area": area,
            "urgency": urgency,
            "skill_gap": skill_gap,
            "role_importance": role_importance,
            "score": round(score, 1),
        })
    return sorted(rows, key=lambda x: x["score"], reverse=True)

def build_study_plan(priorities, available_hours):
    total = max(0, int(round(float(available_hours) * 60)))
    if total == 0 or not priorities:
        return []
    usable = priorities[:3]
    weights = [max(1, x["score"]) for x in usable]
    total_weight = sum(weights)
    allocations = [int(total * w / total_weight) for w in weights]
    while sum(allocations) < total:
        allocations[allocations.index(min(allocations))] += 1

    now = datetime.now().replace(second=0, microsecond=0)
    cursor = now
    plan = []
    topics = {
        "DSA": "Arrays, Binary Search & Problem Solving",
        "Aptitude": "Quantitative Aptitude Practice",
        "Core Subjects": "Operating Systems & Computer Networks",
        "Resume and HR": "Resume + HR Interview Practice",
    }
    for row, minutes in zip(usable, allocations):
        if minutes < 5:
            continue
        end = cursor + timedelta(minutes=minutes)
        plan.append({
            "time": f"{cursor.strftime('%I:%M %p')} – {end.strftime('%I:%M %p')}",
            "area": row["area"],
            "topic": topics[row["area"]],
            "minutes": minutes,
        })
        cursor = end
    return plan

def start_focus_timer(topic, minutes):
    return {"topic": topic, "minutes": int(minutes), "status": "Running", "started_at": datetime.now().isoformat()}

def replan_schedule(profile, priorities, plan, feedback):
    text = feedback.lower()
    confidence = dict(profile.get("confidence", {}))
    if "skipped aptitude" in text or "missed aptitude" in text:
        confidence["Aptitude"] = max(0, confidence.get("Aptitude", 50) - 10)
    if "skipped dsa" in text or "missed dsa" in text:
        confidence["DSA"] = max(0, confidence.get("DSA", 50) - 10)
    profile = dict(profile)
    profile["confidence"] = confidence
    new_priorities = calculate_priorities(profile)
    new_plan = build_study_plan(new_priorities, profile["available_hours"])
    return new_plan, new_priorities

def get_current_plan(profile, priorities, plan):
    return {"profile": profile, "priorities": priorities, "plan": plan}
