from fastapi.testclient import TestClient
from fastapi.responses import FileResponse
from prepare_data import *

def test_read_file(client: TestClient):
    response = client.get("/assets/pdf/1/", headers = {"Authorization": f"Bearer {access_token}"})
    assert response.json() == {'detail': 'Not Found'}