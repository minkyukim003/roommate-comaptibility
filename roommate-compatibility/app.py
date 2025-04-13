from flask import Flask, render_template, request, redirect, url_for, session
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import io
import base64

app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey"

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

def register_user(filepath, username, password):
    data = [username, password]
    f = open(filepath, 'w')

    data_join = "|".join(data)
    data_join = data_join + "|"

    f.write(data_join)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Do something with the data — e.g., save to database
        register_user("./you.txt", username, password)
        
        return redirect(url_for("profile_setup"))  # Or redirect, flash, etc.
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")

def write_answers(filepath, answers):
    with open(filepath, 'a') as f:
        answers_join = "|".join(str(i) for i in answers)
        f.write(answers_join + "\n")  # optional newline

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    #user_id = session.get("user_id")
    #profile = user.profile
    if request.method == "POST":
        answers = [int(request.form[f"q{i}"]) for i in range(len(questions))]
        # Store answers in the profile
        write_answers("./you.txt", answers)
        return redirect(url_for("profile"))  # or dashboard, etc.
    return render_template("quiz.html", questions=questions)

def parse_sample_users(filepath):
    users = []
    with open(filepath, 'r') as f:
        for line in f:
            key, name, major, hobby, quiz = line.strip().split('|')
            users.append({
                'key': key,
                'name': name,
                'major': major,
                'hobby': hobby,
                'quiz': list(map(int, quiz.split(',')))
            })
    return users

def assign_val():
    other_users = parse_sample_users("./users.txt")
    for user in other_users:
        user[0] = None

def read_line_to_list(filepath):
    with open(filepath, 'r') as f:
        line = f.readline().strip()
        values = line.split('|')
        return values

@app.route("/profile")
def profile():
    #session['other_users'] = other_users
    value = read_line_to_list("./you.txt")
    name = value[2]
    major = value[3]
    hobby = value[4]
    return render_template("profile.html", name=name, major=major, hobby=hobby)

def parse_answers_from_file(filename):
    with open(filename, 'r') as f:
        line = f.readline().strip()  # read the first line and remove newline
        parts = line.split('|')
        
        # Assuming the quiz answers start from the 6th element (index 5 onward)
        answers = [int(value) for value in parts[5:]]
        return answers
    
def load_users_to_dict(filepath):
    users = {}
    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split('|')
            user_id = int(parts[0])
            name = parts[1]
            major = parts[2]
            hobby = parts[3]
            answers = [int(x) for x in parts[4:]]
            users[user_id] = {
                'name': name,
                'major': major,
                'hobby': hobby,
                'quiz': answers
            }
    return users


@app.route("/results", methods=["GET", "POST"])
def results():

    other_users = load_users_to_dict("./users.txt")

    answers = parse_answers_from_file("./you.txt")

    user_scores = [
        answers[0],
        answers[1],
        answers[2],
        answers[3],
        answers[4],
        answers[5],
        answers[6],
        answers[7],
        answers[8],
        answers[9]
    ]

    random_num = random.randint(0,4)

    other_scores = other_users[random_num]['quiz']
    other_name = other_users[random_num]['name']

    # Radar plot data
    labels = questions

    # Calculate Compatibility
    diffs = [abs(u - o) for u, o in zip(user_scores, other_scores)]
    compatibility = max(0, 100 - sum((u - o) ** 2 for u, o in zip(user_scores, other_scores)))

    short_labels = ["Clean", "Sleep", "Noise", "Guests", "Comm", "Fin", "Pets", "Cook", "Work", "Smoke"]
    chart = generate_radar_chart(user_scores, other_scores, short_labels)
    summary = generate_personalized_summary(user_scores, other_scores, questions)

    return render_template("results.html", other_name=other_name, compatibility=compatibility, chart=chart, summary=summary)

def add_attributes(filepath, name, major, hobby):
    f = open(filepath, 'a')
    data = [name, major, hobby]
    data_join = "|".join(data)
    data_join = data_join + "|"
    f.write(data_join)

@app.route("/profile-setup", methods=["GET", "POST"])
def profile_setup():
    if request.method == "POST":
        name = request.form["name"]
        major = request.form["major"]
        hobby = request.form["hobby"]
        add_attributes("./you.txt", name, major, hobby)
        return redirect(url_for("quiz"))
    return render_template("profile_setup.html")

def generate_radar_chart(user, other, labels):
    num_vars = len(user)  # should be 10
    # Create angles for the 10 points
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    # For plotting, complete the loop by appending the first point
    values1 = user + [user[0]]
    values2 = other + [other[0]]
    angles_loop = angles + [angles[0]]

    fig, ax = plt.subplots(subplot_kw={'polar': True})
    ax.plot(angles_loop, values1, label='You')
    ax.plot(angles_loop, values2, label='Other')
    ax.fill(angles_loop, values1, alpha=0.25)
    ax.fill(angles_loop, values2, alpha=0.25)

    ax.set_xticks(angles)
    ax.set_xticklabels(labels, fontsize=10, ha='center') 
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
