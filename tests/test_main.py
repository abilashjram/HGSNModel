import os
import pytest

from main import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True

    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    client = app.test_client()

    cleanup()

    db.create_all()

    yield client

def cleanup():
    db.drop_all()

def test_index_not_logged_in(client):
    response = client.get('/')
    assert b'Enter your name' in response.data


def test_index_logged_in(client):
    client.post('/login', data={"user-name" : "Test", "user-email" : "test@testing.com" , "user-password" : "test123"},
                follow_redirects = True)

    response = client.get('/')
    assert b'Enter your guess' in response.data

def test_profile(client):
    client.post('/login', data={"user-name" : "Test", "user-email" : "test@testing.com" , "user-password" : "test123"},
                follow_redirects = True)

    response = client.get('/profile')
    assert b'test@testing.com' in response.data

def test_profile_edit(client):
    client.post('/login', data={"user-name": "Test", "user-email": "test@testing.com", "user-password": "test123"},
                follow_redirects=True)

    # get the edit profile page
    response = client.get('/profile/edit')
    assert b'Edit your profile' in response.data

    #change the data and post in /profile/edit

    response = client.post('/profile/edit', data={"profile-name": "TestUser", "profile-email": "testuser@testing.com"},
                follow_redirects=True)

    assert b'TestUser' in response.data
    assert b'testuser@testing.com' in response.data