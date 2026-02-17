from flask import Flask, render_template, request
import csv
import os
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt

# Machine Learning imports
from sklearn.linear_model import LinearRegression
import numpy as np

app = Flask(__name__)


# ---------------- HOME PAGE ---------------- #

@app.route('/', methods=['GET', 'POST'])
def index():

    score = None
    level = None
    suggestion = None

    if request.method == 'POST':

        study = float(request.form['study'])
        sleep = float(request.form['sleep'])
        phone = float(request.form['phone'])
        exercise = float(request.form['exercise'])

        # -------- MACHINE LEARNING MODEL -------- #

        # Training data (example dataset)
        training_X = np.array([
            [6, 7, 2, 1],
            [4, 6, 4, 0],
            [8, 8, 1, 1],
            [2, 5, 6, 0],
            [7, 7, 2, 1],
            [3, 6, 5, 0]
        ])

        training_y = np.array([80, 55, 95, 30, 85, 45])

        model = LinearRegression()
        model.fit(training_X, training_y)

        new_data = np.array([[study, sleep, phone, exercise]])

        score = model.predict(new_data)[0]

        # Limit score between 0 and 100
        score = round(score, 2)

        if score > 100:
            score = 100
        elif score < 0:
            score = 0

        # -------- LEVEL -------- #

        if score >= 75:
            level = "High Productivity"
            suggestion = "Excellent work! Keep maintaining your habits."

        elif score >= 50:
            level = "Medium Productivity"
            suggestion = "Good, but try reducing phone usage and increase study time."

        else:
            level = "Low Productivity"
            suggestion = "Focus more on studying and reduce distractions."

        # -------- SAVE DATA -------- #

        date = datetime.now().strftime("%Y-%m-%d %H:%M")

        file_exists = os.path.isfile('data.csv')

        with open('data.csv', 'a', newline='') as file:

            writer = csv.writer(file)

            if not file_exists:
                writer.writerow([
                    'Date',
                    'Study Hours',
                    'Sleep Hours',
                    'Phone Hours',
                    'Exercise Hours',
                    'Score',
                    'Level'
                ])

            writer.writerow([
                date,
                study,
                sleep,
                phone,
                exercise,
                score,
                level
            ])

    return render_template(
        'index.html',
        score=score,
        level=level,
        suggestion=suggestion
    )


# ---------------- GRAPH PAGE ---------------- #

@app.route('/graph')
def graph():

    if not os.path.exists('data.csv'):
        return "No data available."

    data = pd.read_csv('data.csv')

    dates = data['Date']
    scores = data['Score']

    plt.figure(figsize=(8,5))

    plt.plot(dates, scores, marker='o')

    plt.title("Productivity Trend")

    plt.xlabel("Date")

    plt.ylabel("Score")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig('static/graph.png')

    plt.close()

    return render_template('graph.html')


# ---------------- DASHBOARD ---------------- #

@app.route('/dashboard')
def dashboard():

    if not os.path.exists('data.csv'):
        return "No data available."

    data = pd.read_csv('data.csv')

    avg_score = round(data['Score'].mean(), 2)

    max_score = data['Score'].max()

    min_score = data['Score'].min()

    total_entries = len(data)

    return render_template(
        'dashboard.html',
        avg_score=avg_score,
        max_score=max_score,
        min_score=min_score,
        total_entries=total_entries
    )


# ---------------- RESET DATA ---------------- #

@app.route('/reset')
def reset():

    if os.path.exists('data.csv'):
        os.remove('data.csv')

    return """
    <h3>Data reset successful.</h3>
    <a href="/">Go Back</a>
    """


# ---------------- RUN APP ---------------- #

if __name__ == '__main__':
    app.run(debug=True)
