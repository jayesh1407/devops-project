from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
import requests
from datetime import datetime

app = Flask(__name__)

# Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'todo.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'devops-demo-secret-key' # Required for flash messages

db = SQLAlchemy(app)

# Model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    complete = db.Column(db.Boolean, default=False)
    priority = db.Column(db.String(20), default='Medium')
    due_date = db.Column(db.String(20), nullable=True)

# Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return ".", 500

# Routes
@app.route('/')
def index():
    # Filtering Logic
    status_filter = request.args.get('status')
    priority_filter = request.args.get('priority')
    
    query = Todo.query
    
    if status_filter == 'active':
        query = query.filter_by(complete=False)
    elif status_filter == 'completed':
        query = query.filter_by(complete=True)
        
    if priority_filter and priority_filter != 'All':
        query = query.filter_by(priority=priority_filter)
        
    # Sort by complete (pending first) then priority (High > Medium > Low)
    # This is a bit complex in SQL, so we'll sort in Python for this simple demo
    todo_list = query.all()
    
    priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
    todo_list.sort(key=lambda x: (x.complete, priority_order.get(x.priority, 3)))

    return render_template('index.html', todo_list=todo_list, current_status=status_filter, current_priority=priority_filter)

@app.route('/add', methods=['POST'])
def add():
    try:
        title = request.form.get('title')
        priority = request.form.get('priority')
        due_date = request.form.get('due_date')
        
        if title:
            new_todo = Todo(title=title, complete=False, priority=priority, due_date=due_date)
            db.session.add(new_todo)
            db.session.commit()
            flash('Task added successfully!', 'success')
        else:
            flash('Task title cannot be empty!', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding task: {str(e)}', 'danger')
        
    return redirect(url_for('index'))

@app.route('/update/<int:todo_id>')
def update(todo_id):
    try:
        todo = Todo.query.filter_by(id=todo_id).first()
        if todo:
            todo.complete = not todo.complete
            db.session.commit()
            status = "completed" if todo.complete else "active"
            flash(f'Task marked as {status}!', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating task: {str(e)}', 'danger')
        
    return redirect(url_for('index'))

@app.route('/edit/<int:todo_id>', methods=['POST'])
def edit(todo_id):
    try:
        todo = Todo.query.get(todo_id)
        if todo:
            todo.title = request.form.get('title')
            todo.priority = request.form.get('priority')
            todo.due_date = request.form.get('due_date')
            db.session.commit()
            flash('Task updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error editing task: {str(e)}', 'danger')
    return redirect(url_for('index'))

@app.route('/delete/<int:todo_id>')
def delete(todo_id):
    try:
        todo = Todo.query.filter_by(id=todo_id).first()
        if todo:
            db.session.delete(todo)
            db.session.commit()
            flash('Task deleted!', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting task: {str(e)}', 'danger')
        
    return redirect(url_for('index'))

@app.route('/clear_completed', methods=['POST'])
def clear_completed():
    try:
        Todo.query.filter_by(complete=True).delete()
        db.session.commit()
        flash('All completed tasks cleared!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error clearing tasks: {str(e)}', 'danger')
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
            # flash(f'GitHub API Error: {response.status_code}', 'warning') # Optional: might be annoying
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
