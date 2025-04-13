from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from models import db, User
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

questions = [
    "Cleanliness",
    "Sleep schedule",
    "Noise Tolerance",
    "Guest Frequency",
    "Communication Style",
    "Financial Habits",
    "Pet Friendliness",
    "Cooking frequency",
    "Work/Study hours",
    "Smoking Preferences"
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            return "Username already exists"

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session["user_id"] = user.id
            return redirect(url_for("quiz"))
        else:
            return "Invalid credentials"

    return render_template("login.html")

@app.route("/quiz")
def quiz():
    return render_template("quiz.html", questions = questions)

@app.route("/results", methods=["POST"])
def results():
    user_scores = [int(request.form[f"user_{i}"]) for i in range(len(questions))]
    other_scores = [int(request.form[f"other_{i}"]) for i in range(len(questions))]

    diffs = [abs(u - o) for u, o in zip(user_scores, other_scores)]
    compatibility = max(0, 100 - sum((u - o) ** 2 for u, o in zip(user_scores, other_scores)))

    
    chart = generate_radar_chart(user_scores, other_scores)
    summary = generate_personalized_summary(user_scores, other_scores, questions) 

    return render_template("results.html", compatibility=compatibility, chart=chart, summary=summary)


def generate_radar_chart(user, other):
    num_vars = len(user)  # This will be 10
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]  # Close the loop

    values1 = user + [user[0]]
    values2 = other + [other[0]]
    labels = questions + [questions[0]]  

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
