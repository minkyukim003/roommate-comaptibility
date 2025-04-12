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
    labels = questions + [questions[0]]
    values1 = user + [user[0]]
    values2 = other + [other[0]]

    angles = np.linspace(0, 2 * np.pi, len(values1), endpoint=False).tolist()

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


if __name__ == "__main__":
    app.run(debug=True)
