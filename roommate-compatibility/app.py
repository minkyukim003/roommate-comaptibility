from flask import Flask, render_template, request
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
    "Work/Study hours"
    "Smoking Preferences"
]
