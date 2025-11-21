from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import requests
from datetime import datetime

app = Flask(__name__)

# Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'todo.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    complete = db.Column(db.Boolean, default=False)
    priority = db.Column(db.String(20), default='Medium')
    due_date = db.Column(db.String(20), nullable=True)

# Routes
@app.route('/')
def index():
    todo_list = Todo.query.all()
    return render_template('index.html', todo_list=todo_list)

@app.route('/add', methods=['POST'])
def add():
    title = request.form.get('title')
    priority = request.form.get('priority')
    due_date = request.form.get('due_date')
    
    if title:
        new_todo = Todo(title=title, complete=False, priority=priority, due_date=due_date)
        db.session.add(new_todo)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/update/<int:todo_id>')
def update(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    if todo:
        todo.complete = not todo.complete
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:todo_id>')
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    if todo:
        db.session.delete(todo)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    # HARDCODED FOR DEMO: Replace with your actual repo details
    # If rate limited, you might need a token: headers={'Authorization': 'token YOUR_TOKEN'}
    GITHUB_USER = "jayesh1407" 
    GITHUB_REPO = "devops-project"
    
    api_url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/actions/runs"
    
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            runs = data.get('workflow_runs', [])[:10] # Get last 10 runs
        else:
            runs = []
            print(f"Error fetching GitHub data: {response.status_code}")
    except Exception as e:
        runs = []
        print(f"Exception: {e}")

    return render_template('dashboard.html', runs=runs, repo=f"{GITHUB_USER}/{GITHUB_REPO}")

if __name__ == "__main__":
    with app.app_context():
        # Simple migration: Drop all and recreate if schema changes (for demo purposes)
        # In production, use Flask-Migrate
        db.create_all()
    app.run(host='0.0.0.0', port=5001, debug=True)
