import pytest
from app import app, db, Todo
from unittest.mock import patch

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test'
    
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'DevOps Project' in response.data

def test_add_todo(client):
    response = client.post('/add', data={
        'title': 'Test Task',
        'priority': 'High',
        'due_date': '2023-12-31'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Test Task' in response.data
    assert b'High' in response.data

def test_edit_todo(client):
    """Test editing a task."""
    client.post('/add', data={'title': 'Old Title', 'priority': 'Low'}, follow_redirects=True)
    
    with app.app_context():
        todo_id = Todo.query.first().id
        
    response = client.post(f'/edit/{todo_id}', data={
        'title': 'New Title',
        'priority': 'High',
        'due_date': '2024-01-01'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'New Title' in response.data
    assert b'High' in response.data

def test_clear_completed(client):
    """Test clearing completed tasks."""
    # Add two tasks
    client.post('/add', data={'title': 'Task 1'}, follow_redirects=True)
    client.post('/add', data={'title': 'Task 2'}, follow_redirects=True)
    
    # Mark Task 1 as complete
    with app.app_context():
        todo_id = Todo.query.filter_by(title='Task 1').first().id
    client.get(f'/update/{todo_id}', follow_redirects=True)
    
    # Clear completed
    response = client.post('/clear_completed', follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Task 1' not in response.data
    assert b'Task 2' in response.data

def test_filter_logic(client):
    """Test filtering by priority."""
    client.post('/add', data={'title': 'High Task', 'priority': 'High'}, follow_redirects=True)
    client.post('/add', data={'title': 'Low Task', 'priority': 'Low'}, follow_redirects=True)
    
    # Filter for High
    response = client.get('/?priority=High')
    assert b'High Task' in response.data
    assert b'Low Task' not in response.data

def test_404_page(client):
    """Test that 404 page renders."""
    response = client.get('/nonexistent_page')
    assert response.status_code == 404
    assert b'Page Not Found' in response.data

@patch('requests.get')
def test_dashboard(mock_get, client):
    mock_response = {
        'workflow_runs': [
            {
                'name': 'CI Pipeline',
                'conclusion': 'success',
                'status': 'completed',
                'head_commit': {'message': 'Test commit'},
                'head_sha': 'abcdef123',
                'head_branch': 'main',
                'created_at': '2023-01-01T12:00:00Z',
                'html_url': 'http://github.com'
            }
        ]
    }
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b'CI Pipeline' in response.data
