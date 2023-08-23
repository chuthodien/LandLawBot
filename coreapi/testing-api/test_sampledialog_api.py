from fastapi.testclient import TestClient
from prepare_data import *

def test_get_sampledialogs(client: TestClient):
    response = client.get("/sampledialogs", headers = {"Authorization": f"Bearer {access_token}"})
    data_read_sampledialogs = response.json()[0]
    assert data_read_sampledialogs["agent_id"] == 1
    assert data_read_sampledialogs["content"] == "Dialog1"

def test_get_sampledialog_by_id(client: TestClient):
    response = client.get(f"/sampledialogs/1", headers = {"Authorization": f"Bearer {access_token}"})
    data_read_sample_dialog_by_id = response.json()
    assert data_read_sample_dialog_by_id["id"] == 1
    assert data_read_sample_dialog_by_id["content"] == "Dialog1"

def test_create_sampledialog(client: TestClient):
    response = client.post(
        f"/sampledialogs/create/1", 
        data={"content": "chien"}, 
        headers = {"Authorization": f"Bearer {access_token}"}
    )
    data_create_sampledialogs = response.json()
    assert  data_create_sampledialogs["agent_id"] == 1
    assert  data_create_sampledialogs["content"] == "chien"

def test_update_sampledialog(client: TestClient):
    response = client.put(
        f"/sampledialogs/update/1",  
        data={"content": "chiendo"}, 
        headers = {"Authorization": f"Bearer {access_token}"}
    )
    data_update_sampledialog = response.json()
    assert data_update_sampledialog["id"] == 1
    assert data_update_sampledialog["content"] == "chiendo"

def test_delete_sampledialog(client: TestClient):
    response = client.delete("/sampledialogs/delete/1", headers = {"Authorization": f"Bearer {access_token}"})
    assert response.json() == {"result": "delete oke"}