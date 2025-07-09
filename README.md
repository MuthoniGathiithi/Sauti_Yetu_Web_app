# Sauti Yetu 🗣️

**Sauti Yetu** (Swahili for *"Our Voice"*) is a web-based platform designed to allow users to anonymously report issues affecting their communities and enable administrators to track, analyze, and respond to those issues efficiently.

## 📌 Project Overview

This project is built using **Django** (backend) and will incorporate a user-friendly frontend for both **public users** and **system administrators**. It prioritizes **anonymity**, **security**, and **data-driven decision-making** for social impact.

## 🔥 Features

- 🧑‍🤝‍🧑 **Anonymous Reporting**  
  Users can submit voice/text-based reports without revealing personal identity.

- 📊 **Admin Dashboard**  
  Admins can manage, track, and respond to reports, view analytics, and monitor trends.

- 🔐 **Security & Privacy**  
  Data is securely stored and access is restricted to authorized personnel.

- 🌍 **Localized Design**  
  Built with Kenyan communities in mind, supporting local languages and relevant categories.

## 🛠️ Tech Stack

- **Backend:** Django 5
- **Frontend:** HTML, CSS (add JS or frameworks later)
- **Database:** SQLite (development) / PostgreSQL (production)
- **Hosting:** To be decided (e.g. Render, Heroku, or DigitalOcean)
- **Version Control:** Git & GitHub

## 📂 Project Structure

sauti_backend/
│
├── users/ # User and admin models, views, auth
├── reports/ # Report models, audio uploads
├── templates/ # HTML templates
├── static/ # CSS/JS/images
├── sauti_backend/ # Main Django config
└── manage.py # Django entry point

bash
Copy
Edit

## 🚀 How to Run Locally

1. **Clone the repo**
   ```bash
   git clone https://github.com/MuthoniGathiithi/SautiYetu.git
   cd SautiYetu
Create and activate a virtual environment

bash
Copy
Edit
python -m venv venv
venv\Scripts\activate  # On Windows
Install dependencies

bash
Copy
Edit
pip install -r requirements.txt
Run migrations

bash
Copy
Edit
python manage.py makemigrations
python manage.py migrate
Run the server

bash
Copy
Edit
python manage.py runserver
Open http://127.0.0.1:8000 in your browser.

📈 Future Goals
Integrate voice transcription

Add machine learning for trend analysis

Create a public data insights page

Mobile support / PWA version

🙋🏽‍♀️ Author
Joyce Muthoni Gathiithi
GitHub Profile
