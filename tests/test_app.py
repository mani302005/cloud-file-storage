import os
import tempfile
import io
import pytest
from app import create_app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv('APP_USER', 'testuser')
    monkeypatch.setenv('APP_PASS', 'testpass')
    monkeypatch.delenv('GCS_BUCKET', raising=False)
    tmpdir = tempfile.mkdtemp()
    monkeypatch.setenv('LOCAL_UPLOAD_DIR', tmpdir)
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_login_logout(client):
    # login with wrong creds
    rv = client.post('/login', data={'username': 'foo', 'password': 'bar'}, follow_redirects=True)
    assert b'Invalid credentials' in rv.data
    # login with correct creds
    rv = client.post('/login', data={'username': 'testuser', 'password': 'testpass'}, follow_redirects=True)
    assert b'Files' in rv.data
    # logout
    rv = client.get('/logout', follow_redirects=True)
    assert b'Login' in rv.data


def test_upload_download_delete(client):
    # login first
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'}, follow_redirects=True)
    data = {'file': (io.BytesIO(b'hello world'), 'hello.txt')}
    rv = client.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert b'Uploaded successfully' in rv.data
    rv = client.get('/')
    assert b'hello.txt' in rv.data
    dv = client.get('/download/hello.txt')
    assert dv.status_code == 200
    delv = client.get('/delete/hello.txt', follow_redirects=True)
    assert b'Deleted successfully' in delv.data
