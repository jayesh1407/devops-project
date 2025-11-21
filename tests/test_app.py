import pytest
from app import app, db, Todo
from unittest.mock import patch

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_index_page(client):
    """Test that the index page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'DevOps Project' in response.data

def test_add_todo(client):
    """Test adding a new todo item with priority."""
    response = client.post('/add', data={
        'title': 'Test Task',
        'priority': 'High',
        'due_date': '2023-12-31'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Test Task' in response.data
    assert b'High' in response.data

def test_complete_todo(client):
    """Test marking a todo item as complete."""
    client.post('/add', data={'title': 'Task to Complete'}, follow_redirects=True)
    
    with app.app_context():
        todo = Todo.query.first()
        todo_id = todo.id

    response = client.get(f'/update/{todo_id}', follow_redirects=True)
    assert response.status_code == 200
    
    with app.app_context():
        todo = Todo.query.get(todo_id)
        assert todo.complete is True

def test_delete_todo(client):
    """Test deleting a todo item."""
    client.post('/add', data={'title': 'Task to Delete'}, follow_redirects=True)
    
    with app.app_context():
        todo = Todo.query.first()
        todo_id = todo.id

    response = client.get(f'/delete/{todo_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Task to Delete' not in response.data

@patch('requests.get')
def test_dashboard(mock_get, client):
    """Test the dashboard route with mocked GitHub API response."""
    # Mock the API response
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
    assert b'Test commit' in response.data
