# CS50 FINAL PROJECT: American dream
# Author: Madi Tattybay
# All code and logic written by me.
# AI tools were used only for small suggestions and review.

from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import timedelta, datetime
import json, sqlite3, random
from pathlib import Path

DB_PATH = Path(__file__).with_name("american_dream.db")

app=Flask(__name__)
app.secret_key = "american-dream-final"
app.permanent_session_lifetime = timedelta(days=7)

RENT_COST = 30
RENT_MOOD = -2
LOW_ENERGY_HINT = 10

SUPPORT = [
    "When it feels like everything is falling apart, your strength is being built.",
    "You didn't fail - you're learning. Every day you grow stronger.",
    "Immigration is a marathon, not a sprint. Keep moving.",
    "You're not alone. Millions walk this path and reach their dreams.",
    "Even if today is hard, tomorrow you'll try again. That's your power.",
    "Small steps count. Keep showing up - your future self will thank you.",
]

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def inflate(row):
    return {
        "id": row["id"],
        "name": row["name"],
        "day": row["day"],
        "money": row["money"],
        "english": row["english"],
        "energy": row["energy"],
        "mood": row["mood"],
        "achievements": json.loads(row["achievements"]),
        "log": json.loads(row["log"]),
        "updated_at": row["updated_at"],
    }

def get_player(name):
    with db() as conn:
        row = conn.execute("SELECT * FROM players WHERE name = ?", (name,)).fetchone()
    return row

def create_or_load_player(name):
    row = get_player(name)
    if row:
        return row
    with db() as conn:
        conn.execute("INSERT INTO players (name) VALUES (?)", (name,))
        conn.commit()
    return get_player(name)

def load_player_by_id(pid):
    with db() as conn:
        row = conn.execute("SELECT * FROM players WHERE id=?", (pid,)).fetchone()
    return inflate(row) if row else None

def save_player(p):
    with db() as conn:
        conn.execute(
            """UPDATE players
             SET day=?, money=?, english=?, energy=?, mood=?, achievements=?, log=?, updated_at=CURRENT_TIMESTAMP
              WHERE id=?""",
            (p["day"], p["money"], p["english"], p["energy"], p["mood"],
              json.dumps(p["achievements"]), json.dumps(p["log"]), p["id"])
        )
        conn.commit()

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def apply_change(p, *, money=0, english=0, energy=0, mood=0, note=None):
    p["money"] = max(0, p["money"] + money)
    p["english"] = clamp(p["english"] + english, 0, 100)
    p["energy"] = clamp(p["energy"] + energy, 0, 100)
    p["mood"] = clamp(p["mood"] + mood, 0, 100)
    if note:
        stamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        p["log"].append(f"[{stamp}] {note}")

def is_success(p):
    return p["money"] >= 200 and p["english"] >= 50 and p["mood"] >= 55

def is_burnout(p):
    return p["energy"] <= 5 or p["mood"] <= 5

def daily_scene(day):
    scenes = {
        1: {
            "title": "Day 1 - Arrival",
            "text": "Welcome to America! You’ve legally immigrated and now begin your new life. Your first goal is to get your documents ready.",
            "choices": [
                ("ssn", "Get your Social Security Number"),
                ("license", "Get your Driver’s License / ID"),
                ("explore", "Explore the city")
            ],
        },
        2: {
            "title": "Day 2 - Finding Direction",
            "text": "You start to plan your path.",
            "choices": [("resume", "Work on resume"), ("oddjob", "Find any job"), ("community", "Go to community center")],
        },
        3: {
            "title": "Day 3 - Small progress",
            "text": "Each day matters",
            "choices": [("paidtask", "Do paid job"), ("intern", "Internship for skills"), ("rest", "Rest a bit")],
        },
        4: {
            "title": "Day 4 - Paperwork",
            "text": "Getting ID and basics done.",
            "choices": [("id", "Get local ID"), ("bank", "Open bank account"), ("library", "Study at library")],
        },
        5: {
            "title": "Day 5 - Confidence",
            "text": "Your English improves.",
            "choices": [("mock", "Mock interview"), ("apply10", "Apply to jobs"), ("partner", "Talk with language partner")],
        },
        6: {
            "title": "Day 6 - First Success",
            "text": "A first paycheck or progress.",
            "choices": [("firstpay", "First paycheck"), ("goodservice", "Good service"), ("volunteer", "Volunteer")],
        },
        7: {
            "title": "Day 7 - Momentum",
            "text": "Now you move with rhythm and hope",
            "choices": [("negotiate", "Negotiate rate"), ("shortcourse", "Take a course"), ("mentor", "Find a mentor")],
        },
    }
    return scenes[day]



@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        if not name:
            flash("Please enter your name.")
            return redirect(url_for("index"))
        player = create_or_load_player(name)
        session["player_id"] = player["id"]
        return redirect(url_for("day"))

    if session.get("player_id"):
        p = load_player_by_id(session["player_id"])
        if p:
            return render_template("index.html", p=p, msg=random.choice(SUPPORT))
    return render_template("index.html", p=None, msg=random.choice(SUPPORT))

@app.route("/reset")
def reset():
    session.pop("player_id", None)
    return redirect(url_for("index"))

@app.route("/day", methods=["GET", "POST"])
def day():
    pid = session.get("player_id")
    if not pid:
        return redirect(url_for("index"))
    p = load_player_by_id(pid)
    if not p:
        return redirect(url_for("index"))

    if request.method == "POST":
        action = request.form.get("action")
        if not action:
            flash("Choose an option.")
            return redirect(url_for("day"))

        if action == "ssn":
            apply_change(p, english=+2, energy=-5, mood=+5, note="You received your Social Security Number.")
        elif action == "license":
            apply_change(p, english=+3, energy=-6, mood=+6, note="You got your Driver’s License / ID.")
        elif action == "explore":
            apply_change(p, energy=-10, mood=+10, note="You explored the city and felt inspired.")
        if action == "shift":
            apply_change(p, money=50, energy=-10, mood=+2, note="Worked a shift.")
        elif action == "esl":
            apply_change(p, english=+8, energy=-6, mood=+5, note="Attended English class.")
        elif action == "deliver":
            apply_change(p, money=70, energy=-15, mood=-2, note="Did deliveries.")
        elif action == "resume":
            apply_change(p, english=+4, energy=-5, mood=+4, note="Improved your resume.")
        elif action == "oddjob":
            apply_change(p, money=80, energy=-12, mood=+1, note="Took an odd job.")
        elif action == "community":
            apply_change(p, english=+4, energy=+10, mood=+10, note="Connected with people at the community center.")
        elif action == "paidtask":
            apply_change(p, money=60, energy=-15, mood=+7, note="Completed a paid task.")
        elif action == "intern":
            apply_change(p, money=20, english=+12, energy=-8, mood=+7, note="Internship boosted your career.")
        elif action == "rest":
            apply_change(p, energy=+25, mood=+12, note="You rested and recharged.")
        elif action == "id":
            apply_change(p, english=+3, energy=-6, mood=+3, note="Handled essential ID paperwork.")
        elif action == "bank":
            apply_change(p, english=+2, energy=-4, mood=+3, note="Opened a bank account and set a budget.")
        elif action == "library":
            apply_change(p, english=+7, energy=-5, mood=+3, note="Studied in the library.")
        elif action == "mock":
            apply_change(p, english=+8, energy=-7, mood=+6, note="Mock interviews built confidence.")
        elif action == "apply10":
            apply_change(p, english=+3, energy=-10, mood=+4, note="You sent 10 applications today.")
        elif action == "partner":
            apply_change(p, english=+10, energy=-6, mood=+7, note="Language partner helped fluency.")
        elif action == "firstpay":
            apply_change(p, money=90, energy=-12, mood=+10, note="Your first proper paycheck. It feels real.")
        elif action == "goodservice":
            apply_change(p, money=70, energy=-10, mood=+9, note="Good service brought positive feedback.")
        elif action == "volunteer":
            apply_change(p, english=+6, energy=-6, mood=+8, note="Volunteering expanded your network.")
        elif action == "negotiate":
            apply_change(p, money=35, energy=-6, mood=+6, note="Negotiated a better rate/shift.")
        elif action == "shortcourse":
            apply_change(p, money=-30, english=+18, energy=-5, mood=+10, note="Completed a professional course.")
        elif action == "mentor":
            apply_change(p, english=+5, energy=-5, mood=+12, note="A mentor offered practical guidance.")
        else:
            apply_change(p, mood=+3, note="You moved forward.")
        if is_burnout(p):
            save_player(p)
            return redirect(url_for("pause"))
        if is_success(p):
            save_player(p)
            return redirect(url_for("success"))
        p["energy"] = clamp(p["energy"] + 3, 0, 100)
        p["mood"]   = clamp(p["mood"]   + 1, 0, 100)

        p["day"] = min(7, p["day"] + 1)
        save_player(p)
        return redirect(url_for("day"))

    scene = daily_scene(p["day"])
    return render_template("day.html", p=p, scene=scene, msg=random.choice(SUPPORT))

@app.route("/pause")
def pause():
    pid = session.get("player_id")
    if not pid:
        return redirect(url_for("index"))
    p = load_player_by_id(pid)
    return render_template("pause.html", p=p, msg=random.choice(SUPPORT))

@app.route("/rest", methods=["POST"])
def rest():
    """User takes a long rest (5 days) and recovers energy/mood."""
    pid = session.get("player_id")
    if not pid:
        return redirect(url_for("index"))
    p = load_player_by_id(pid)
    if not p:
        return redirect(url_for("index"))

    apply_change(p, energy=+50, mood=+10, note="You took a 5-day rest and recovered.")

    save_player(p)
    return redirect(url_for("day"))

@app.route("/success")
def success():
    pid = session.get("player_id")
    if not pid:
        return redirect(url_for("index"))
    p = load_player_by_id(pid)
    return render_template("success.html", p=p, msg=random.choice(SUPPORT))

if __name__== "__main__":
    app.run(debug=True)









