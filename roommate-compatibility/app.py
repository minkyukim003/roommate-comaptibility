from flask import Flask, render_template, request
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import io
import base64

app = Flask(__name__)

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
    return render_template("index.html", questions = questions)

@app.route("/results", methods=["POST"])
def results():
    user_scores = [int(request.form[f"user_{i}"]) for i in range(len(questions))]
    other_scores = [int(request.form[f"other_{i}"]) for i in range(len(questions))]

    diffs = [abs(u - o) for u, o in zip(user_scores,other_scores)]
    compatibility = max(0, 100 - sum(diffs) * 2)
    
    chart = generate_radar_chart(user_scores, other_scores)

    return render_template("results.html", compatibility=compatibility, chart=chart)

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
    ax.set_xticklabels(questions)
    ax.set_yticklabels([])

    ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return chart

def generate_personalized_summary(user, other):
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


if __name__ == "__main__":
    app.run(debug=True)
