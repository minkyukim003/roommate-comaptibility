# Roommate Compatibility
for Bitcamp 2025 
by Alex and Jake

from flask import Flask, render_template, request, redirect, url_for, session  
//import random  
//import matplotlib  
//matplotlib.use('Agg')  
//import matplotlib.pyplot as plt  
//import numpy as np  
//import io  
//import base64  

Roomlytics was inspired by our own college experiences, where we realized how challenging it can be to live with new roommates. From loud snorers and messy kitchens to mismatched sleep schedules, we saw firsthand how difficult cohabitation can be without real compatibility. Traditional roommate matching often only considers surface-level traits or availability, overlooking deeper lifestyle alignment. With Roomlytics, we wanted to build a more thoughtful, data-driven solution that analyzes user preferences across key lifestyle dimensions to provide insight and improve harmony in shared living spaces.

Our project allows users to record their lifestyle preferences and housing criteria through a brief questionnaire. Once submitted, the system compares their responses with other profiles and calculates compatibility rates. Users then receive a visual representation—specifically, a radar chart—that clearly highlights areas of compatibility and potential friction, making it easier to evaluate shared living potential with another person.

We built Roomlytics using Flask (Python) for the backend, and HTML/CSS with Jinja templating on the frontend. User data and quiz results are stored in a SQLite database, managed via SQLAlchemy and Flask-Migrate. For visualization, we used Matplotlib to generate radar charts that compare individual user responses with those of sample or matched profiles. These charts are encoded using base64 and rendered dynamically in the HTML templates.

We faced several challenges along the way. One major hurdle was designing radar charts that were readable and visually clean despite long axis labels. Another was mapping quiz responses accurately to database profiles and ensuring the data could be stored and retrieved without issues. Embedding Matplotlib images into the web app also took some experimentation with image buffers and encoding. Handling session data and protecting result routes from unauthorized access was another key challenge during development.

Despite the obstacles, we’re proud of having built a full-stack application from the ground up in a limited timeframe. We successfully created an intuitive radar chart that presents multidimensional compatibility data in a user-friendly format, and we implemented a system for storing and comparing actual quiz data between users.

Through this project, we learned how to structure a Flask application effectively, how to visualize complex data using radar charts, and how to pass data securely and efficiently between backend and frontend. We also gained insight into the importance of thoughtful UI decisions and clear labeling in helping users understand the data.

Looking ahead, we plan to expand Roomlytics with a full roommate matching algorithm, support for real user profiles with photos and bios, messaging features, and an admin dashboard for analyzing user trends. We also aim to create a mobile-friendly version to improve accessibility. The tools we used include Flask, SQLAlchemy, Flask-Migrate, Matplotlib, HTML/CSS, Jinja2, and SQLite.
