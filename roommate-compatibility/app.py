from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, User, UserProfile
from werkzeug.security import generate_password_hash, check_password_hash
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import io
import base64

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///roommate.db"
app.config["SECRET_KEY"] = "supersecretkey"

db.init_app(app)
migrate = Migrate(app, db)

questions = [
        "How clean are you?",
        "When do you usually go to sleep?",
        "How tolerant are you of noise?",
        "How often do you like having guests over?",
        "How direct is your communication style?",
        "How do you handle finances?",
        "Do you want pets around?",
        "How often do you cook?",
        "How many hours do you work/study?",
        "Do you smoke or mind smoking?"
    ]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    user = User.query.get(user_id)

    # Ensure the user has a profile before proceeding to quiz
    if not user.profile:
        return redirect(url_for("profile_setup"))

    profile = user.profile

    if request.method == "POST":
        answers = [int(request.form[f"q{i}"]) for i in range(len(questions))]

        # Store answers in the profile
        profile.cleanliness = answers[0]
        profile.sleep_schedule = answers[1]
        profile.noise_tolerance = answers[2]
        profile.guest_frequency = answers[3]
        profile.communication_style = answers[4]
        profile.financial_habits = answers[5]
        profile.pet_friendliness = answers[6]
        profile.cooking_frequency = answers[7]
        profile.work_study_hours = answers[8]
        profile.smoking_preferences = answers[9]

        db.session.commit()
        return redirect(url_for("results"))  # or dashboard, etc.

    return render_template("quiz.html", questions=questions)

@app.route("/results")
def results():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    user = User.query.get(user_id)
    user_profile = user.profile

    if not user_profile:
        return "Please complete the quiz before viewing results."

    # Always compare with a random user who has a profile and is not the current user
    other_user = User.query.filter(User.id != user_id).join(UserProfile).first()
    if not other_user:
        return "No other users with profiles available for comparison yet."

    other_profile = other_user.profile

    # Scores
    user_scores = [
        user_profile.cleanliness,
        user_profile.sleep_schedule,
        user_profile.noise_tolerance,
        user_profile.guest_frequency,
        user_profile.communication_style,
        user_profile.financial_habits,
        user_profile.pet_friendliness,
        user_profile.cooking_frequency,
        user_profile.work_study_hours,
        user_profile.smoking_preferences
    ]

    other_scores = [10] * 10

    compatibility = max(0, 100 - sum((u - o) ** 2 for u, o in zip(user_scores, other_scores)))
    chart = generate_radar_chart(user_scores, other_scores)
    summary = generate_personalized_summary(user_scores, other_scores, questions)

    return render_template("results.html", compatibility=compatibility, chart=chart, summary=summary)


@app.route("/profile-setup", methods=["GET", "POST"])
def profile_setup():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    if request.method == "POST":
        name = request.form["name"]
        major = request.form["major"]
        hobbies = request.form["hobbies"]

        user = User.query.get(session["user_id"])
        profile = UserProfile(name=name, major=major, hobbies=hobbies, user=user)
        db.session.add(profile)
        db.session.commit()
        return redirect(url_for("quiz"))

    return render_template("profile_setup.html")

def generate_radar_chart(user, other):
    num_vars = len(user)  # This will be 10
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]  # Close the loop

    values1 = user + [user[0]]
    values2 = other + [other[0]]
    labels = questions + [questions[0]]  # Ensure the labels match the question list

    fig, ax = plt.subplots(subplot_kw={'polar': True})
    ax.plot(angles, values1, label='You')
    ax.plot(angles, values2, label='Other')
    ax.fill(angles, values1, alpha=0.25)
    ax.fill(angles, values2, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(questions, fontsize=10, ha='center') 
    ax.set_yticklabels([])

    ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return chart

def generate_personalized_summary(user, other, questions):
    diffs = [abs(u - o) for u, o in zip(user, other)]
    paired_scores = list(zip(questions, user, other, diffs))
    paired_scores.sort(key=lambda x: x[3], reverse=True)

    summary = ""

    # Top 3 biggest differences
    biggest_diffs = paired_scores[:3]
    if any(d[3] >= 4 for d in biggest_diffs):
        summary += "You and your potential roommate have notable differences in:\n"
        for q, u, o, d in biggest_diffs:
            summary += f"- **{q}**: You rated {u}, they rated {o}.\n"
    else:
        summary += "You and your potential roommate don’t have any major red flags in your preferences.\n"

    # Top 3 strongest alignments
    strongest_alignments = [x for x in paired_scores if x[3] <= 2][:3]
    if strongest_alignments:
        summary += "\nYou’re especially well-aligned on:\n"
        for q, u, o, d in strongest_alignments:
            summary += f"- **{q}**: You rated {u}, they rated {o}.\n"

    # Overall take
    total_diff = sum(diffs)
    if total_diff <= 15:
        summary += "\n🌟 You’re highly compatible overall — this could be a great match!"
    elif total_diff <= 25:
        summary += "\n⚖️ You have a few areas to work through, but nothing major. Communication is key!"
    else:
        summary += "\n🚨 There are some significant lifestyle differences — a good conversation beforehand is strongly recommended."

    return summary


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
