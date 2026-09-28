# AIbOT
AI Placement Preparation Agent
An agentic AI prototype for adaptive placement preparation. The system accepts a student's placement situation in natural language, converts it into a structured profile, ranks preparation areas, builds a time-boxed plan, starts focused practice, and replans when progress changes.

Features
Natural-language student input
Structured profile extraction
Readiness/priority scoring
Time-boxed daily study plan
Focus timer
Aptitude/coding mock-test interface
Progress updates and automatic replanning
Reasoning display for priority scores
Controlled Python tool layer
Architecture
Student → Streamlit Interface → Agent Logic → Tool Layer → Scoring/Scheduling → Result → Agent → Next Action

Priority Formula
Score = 0.40 × Urgency + 0.35 × Skill gap + 0.25 × Role importance

The application code is authoritative for the numerical score and schedule.

Run locally
python -m venv .venv
Windows:

.venv\Scripts\activate
Install dependencies:

pip install -r requirements.txt
Start:

streamlit run app.py
The prototype runs locally in a browser.

Project structure
app.py — Streamlit interface and session state
agent.py — natural-language profile extraction and agent response
tools.py — controlled scoring, planning, focus and replanning functions
requirements.txt — dependencies
Academic prototype
This repository implements the prototype described in the Fundamentals of Artificial Intelligence — Assignment I project description.
