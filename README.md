# Smart Habit Tracker 

A modern Flask web app that helps users record, visualise and improve their daily habits.  
Features include secure authentication, habit CRUD, duplicate-free logging, pie-chart summaries and a calendar heat-map — all wrapped in a handsome Bootstrap UI.

---

## Features
* **User auth** – register / login / logout (Flask-Login, hashed passwords)
* **Add habits** – name + rich frequency dropdown
* **Log habits** – one-click “Log”, timestamped, prevents duplicates per day
* **Edit / delete** habits
* **Charts** – Chart.js doughnut summarising log counts
* **Calendar view** – FullCalendar event grid of habit logs
* **Responsive UI** – Bootstrap 5, gradient headers, reusable logo
* **Flash messages** – live feedback on every action

---

## Tech Stack
| Layer        | Tooling                          |
|--------------|----------------------------------|
| Backend      | Python 3.13, Flask 3, Flask-SQLAlchemy |
| Auth         | Flask-Login, Werkzeug security   |
| Front-End    | Bootstrap 5, Chart.js, FullCalendar |
| Database     | SQLite (Migrate ready)           |

---

## Quick Start

```bash
git clone <repo> habit_tracker
cd habit_tracker
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
# —— first-time only ——
flask shell -c "from app import db; db.create_all()"

export FLASK_APP=run.py
export FLASK_ENV=development
flask run

