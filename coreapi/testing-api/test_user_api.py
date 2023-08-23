from fastapi.testclient import TestClient
from prepare_data import *

def test_get_users(client: TestClient):
    response = client.get("/users", headers = {"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200, response.text
    get_users = response.json()[0]
    assert get_users["id"] == 1
    assert get_users["email"] == "admin@example.com"

def test_get_user_by_id(client: TestClient):
    response = client.get(f"/users/1", headers = {"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200, response.text
    assert response.json()["id"] == 1
    assert response.json()["email"] == "admin@example.com"

def test_create_user(client: TestClient):
    response  = client.post(
        "/users/create", 
        data = {
            "name": "123",
            "email": "123@example.com",
            "line_id": 123456,
            "pinecone_index": "index",
            "access_token": "access_token",
            "refresh_token": "refresh_token"
        },
        headers = {"Authorization": f"Bearer {access_token}"}
    )
    assert response.json()["name"] == "123"

def test_update_user(client: TestClient):
    response = client.put(
        f"/users/update/1",
        data = {
            "name": "123",
            "email": "123@example.com",
            "line_id": 123456,
            "pinecone_index": "index",
            "access_token": "access_token",
            "refresh_token": "refresh_token",
        },
        headers = {"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200, response.text
    assert response.json()["id"] == 1
    assert response.json()["name"] == "123"
    assert response.json()["email"] == "123@example.com"

def test_delete_user(client: TestClient):
    response = client.delete(f"/users/delete/1", headers = {"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200, response.text
    assert response.json() == {"result": "delete success"}