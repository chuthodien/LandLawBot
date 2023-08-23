from fastapi.testclient import TestClient
from prepare_data import *

def test_verify_webhook(client: TestClient):
    response = client.get("/webhook/1", headers = {"Authorization": f"Bearer {access_token}"})
    assert response.json() == {"AIME": "AIME"}

def test_line_chat(client: TestClient):
    response = client.post('/webhook/1', headers = {"X-Line-Signature": f"Bearer {access_token}"})
    assert response.json() == 'Invalid signature'
    