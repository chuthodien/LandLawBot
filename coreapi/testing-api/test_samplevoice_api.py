from fastapi.testclient import TestClient
from prepare_data import *

base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
file = open(f"{base_path}\\coreapi\\testing-api\\test_file.txt", 'rb') 

def test_get_samplevoices(client: TestClient):
    response = client.get("/samplevoices", headers = {"Authorization": f"Bearer {access_token}"})
    data_read_samplevoices = response.json()[0]
    assert data_read_samplevoices["agent_id"] == 1
    assert data_read_samplevoices["file"] == "voice.wav"

def test_get_samplevoice_by_id(client: TestClient):
    response = client.get(f"/samplevoices/1", headers = {"Authorization": f"Bearer {access_token}"})
    data_read_samplevoice_by_id = response.json()
    assert data_read_samplevoice_by_id["id"] == 1
    assert data_read_samplevoice_by_id["file"] == "voice.wav"

def test_create_samplevoices(client: TestClient):
    response = client.post(
        f"/samplevoices/create/1",
        files={"file": file},
        headers = {"Authorization": f"Bearer {access_token}"}
    )
    data_create_samplevoice = response.json()
    assert  data_create_samplevoice["agent_id"] == 1
    assert  data_create_samplevoice["file"] == "/assets/voice/1/test_file.txt"

def test_update_samplevoices(client: TestClient):   
    response = client.put(
        f"/samplevoices/update/1",  
        files={"file": file},
        headers = {"Authorization": f"Bearer {access_token}"}
    )
    data_update_samplevoice = response.json()
    #assert data_update_samplevoice == 1
    assert data_update_samplevoice["file"] == "/assets/voice/1/test_file.txt"

def test_delete_samplevoice(client: TestClient):
    response = client.delete("/samplevoices/delete/1", headers = {"Authorization": f"Bearer {access_token}"})
    assert response.json() == {"result": "delete success"}