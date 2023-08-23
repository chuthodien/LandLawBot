from fastapi.testclient import TestClient
from prepare_data import *

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
CLIENT_ID = os.getenv('LINE_CHANNEL_ACCESS_TOKEN_LOGIN')
CLIENT_SECRET = os.getenv('LINE_CHANNEL_SECRET_LOGIN')
REDIRECT_URI = os.getenv('LOGIN_REDIRECT_URI')

def test_line_login(client: TestClient):
    response = client.get('/api/line/authorize')
    authorization_url = f"https://access.line.me/oauth2/v2.1/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&state=state&scope=openid%20profile"
    assert response.json() == {"url": authorization_url}

def test_line_callback(client: TestClient):
    response = client.post('/v1/login', params={"code": "z3jvemVYt9c3gWyEWMEL"})
    assert response.json()["id"] == 2
    assert response.json()["refresh_token"] == "refresh_token"

def test_log_out(client: TestClient):
    response = client.post('/logout', headers = {"Authorization": f"Bearer {access_token}"})
    assert response.json() == {'detail': 'Log out account admin success'}