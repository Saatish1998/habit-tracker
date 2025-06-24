from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from flask import Blueprint, current_app
from app.models import User, Habit, HabitLog, SmartwatchData
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Try another.', 'danger')
            return redirect(url_for('register'))
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Try again.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        name = request.form['name']
        frequency = request.form['frequency']
        reminder_time = request.form.get('reminder_time')
        non_productive = True if request.form.get('non_productive') else False

        new_habit = Habit(
            name=name,
            frequency=frequency,
            reminder_time=reminder_time,
            non_productive=non_productive,
            user_id=current_user.id
        )
        db.session.add(new_habit)
        db.session.commit()
        flash('✅ Habit added successfully!', 'success')
        return redirect(url_for('dashboard'))

    habits = Habit.query.filter_by(user_id=current_user.id).all()

    logs_by_habit = {
        habit.id: HabitLog.query.filter_by(habit_id=habit.id)
                    .order_by(HabitLog.timestamp.desc()).all()
        for habit in habits
    }

    chart_data = {
        'labels': [habit.name for habit in habits],
        'counts': [len(logs_by_habit[habit.id]) for habit in habits]
    }

    all_logs = HabitLog.query.join(Habit).filter(Habit.user_id == current_user.id).all()
    productive = sum(1 for log in all_logs if not log.habit.non_productive)
    non_productive = sum(1 for log in all_logs if log.habit.non_productive)
    summary = {
        'productive': productive,
        'non_productive': non_productive
    }

    suggestions = []
    total_logs = summary['productive'] + summary['non_productive']

    if total_logs == 0:
        suggestions.append("🕒 You haven't logged any habits yet. Start with one productive habit today.")
    else:
        ratio = summary['productive'] / total_logs

        if ratio >= 0.8:
            suggestions.append("🔥 Amazing! Most of your habits are productive. Keep the streak going!")
        elif ratio >= 0.5:
            suggestions.append("👍 You're doing decent! Try shifting focus to a few more productive habits.")
        else:
            suggestions.append("⚠️ You're logging too many non-productive habits. Try replacing one with something more goal-oriented.")

        if summary['non_productive'] >= 3:
            suggestions.append("💡 Consider reducing non-productive habits to maintain a balanced day.")

    # 🔁 Get latest smartwatch data for user
    latest_data = SmartwatchData.query.filter_by(user_id=current_user.id).order_by(SmartwatchData.timestamp.desc()).first()

    if latest_data:
        watch_data = {
            "steps": latest_data.steps,
            "sleep": latest_data.sleep,
            "heart_rate": latest_data.heart_rate
        }
    else:
        watch_data = {"steps": 0, "sleep": 0, "heart_rate": 0}

    return render_template(
        'dashboard.html',
        habits=habits,
        habit_logs=logs_by_habit,
        chart_data=chart_data,
        summary=summary,
        suggestions=suggestions,
        watch_data=watch_data
    )

@app.route('/log/<int:habit_id>', methods=['POST'])
@login_required
def log_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    today = datetime.utcnow().date()

    already_logged = HabitLog.query.filter(
        HabitLog.habit_id == habit.id,
        db.func.date(HabitLog.timestamp) == today
    ).first()

    if already_logged:
        flash('⚠️ You already logged this habit today!', 'warning')
    else:
        log = HabitLog(habit_id=habit.id)
        db.session.add(log)
        db.session.commit()

        if habit.reminder_time:
            flash(f"⏰ Reminder was set for {habit.reminder_time}.", 'info')

        flash('✅ Habit logged successfully!', 'success')

    return redirect(url_for('dashboard'))

@app.route('/edit/<int:habit_id>', methods=['GET', 'POST'])
@login_required
def edit_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    if request.method == 'POST':
        habit.name = request.form['name']
        habit.frequency = request.form['frequency']
        habit.reminder_time = request.form.get('reminder_time')
        habit.non_productive = True if request.form.get('non_productive') else False
        db.session.commit()
        flash('Habit updated successfully.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('edit_habit.html', habit=habit)

@app.route('/delete/<int:habit_id>', methods=['POST'])
@login_required
def delete_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    db.session.delete(habit)
    db.session.commit()
    flash('Habit deleted successfully.', 'info')
    return redirect(url_for('dashboard'))

@app.route('/watch-data', methods=['POST'])
def receive_watch_data():
    try:
        data = request.get_json()
        print("⌚ Smartwatch data received:", data)

        steps = data.get('steps')
        sleep = data.get('sleep')
        heart_rate = data.get('heart_rate')

        print(f"Parsed values → steps: {steps}, sleep: {sleep}, heart_rate: {heart_rate}")

        user_id = 2  # hardcoded for test/demo purposes

        # Save smartwatch data
        sw_data = SmartwatchData(user_id=user_id, steps=steps, sleep=sleep, heart_rate=heart_rate)
        db.session.add(sw_data)

        habit_names = ["Walking", "Running", "Jogging"]
        today = datetime.utcnow().date()

        for name in habit_names:
            habit = Habit.query.filter_by(user_id=user_id, name=name).first()
            print(f"🔍 Checking habit: {name} → {habit}")
            if habit:
                already_logged = HabitLog.query.filter(
                    HabitLog.habit_id == habit.id,
                    db.func.date(HabitLog.timestamp) == today
                ).first()
                if not already_logged:
                    db.session.add(HabitLog(habit_id=habit.id))
                    print(f"✅ Auto-logged '{name}'")
                else:
                    print(f"⚠️ Already logged '{name}' today.")

        db.session.commit()

        return jsonify({"status": "success", "message": "Smartwatch data stored"}), 200

    except Exception as e:
        print("🔥 ERROR:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500
