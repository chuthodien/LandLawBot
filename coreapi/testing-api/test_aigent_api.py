from fastapi.testclient import TestClient
from prepare_data import *

base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
file = open(f"{base_path}\\coreapi\\testing-api\\test_file.txt", 'rb') 

def test_get_agents(client: TestClient):
    response = client.get("/aiagents", headers = {"Authorization": f"Bearer {access_token}"})
    data_read_aiagents = response.json()[0]
    assert data_read_aiagents["user_id"] == 1
    assert data_read_aiagents["name"] == "Gon Freecss"

def test_get_agents_by_user_id(client: TestClient):
    response = client.get(f"/aiagents/user/1", headers = {"Authorization": f"Bearer {access_token}"})
    data_get_aiagent_by_user_id = response.json()[0]
    assert data_get_aiagent_by_user_id["user_id"] == 1
    assert data_get_aiagent_by_user_id["name"] == "Gon Freecss"

def test_get_agent_by_id(client: TestClient):
    response = client.get(f"/aiagents/1", headers = {"Authorization": f"Bearer {access_token}"})
    data_read_aiagent_by_id = response.json()
    assert data_read_aiagent_by_id["id"] == 1
    assert data_read_aiagent_by_id["name"] == "Gon Freecss"

def test_create_agent(client: TestClient):
    response = client.post(
        "/aiagents/create/1",
        data = {
            "name": "chien",
            "introduction": "Hunter of the 287th generation. Enhancer-type Nen user. Birthday is May 5th. Height is 154cm. Weight is 49kg. Blood type is B.",
            "pinecone_namespace": "pinecone name",
            "age": "15",
            "first_person_pronoun": "I (ore)",
            "second_person_pronoun": "you (kimi)",
            "activity": "Taking the Hunter Exam",
            "hobbies": "Fighting",
            "occupation": "Hunter",
            "speaking_style": "A quiet boy of around 12 years old",
            "sampledialogs": '[{"content": "Dialog1"}, {"content": "Dialog2"}]',
        },
        files = {
            "pdf_file": file,
            "icon_file": file,
            "voice_model_file": file,
            "sample_voices": file
        },
        headers = {"Authorization": f"Bearer {access_token}"}
    )
    assert response.json()["name"] == "chien"
    assert response.json()["pdf_file"] == "/assets/pdf/2/test_file.txt"   
    assert response.json()["icon_file"] == "/assets/avatar/2/test_file.txt"  
    assert response.json()["voice_model_file"] == "/assets/model/2/test_file.txt"

def test_update_agent(client: TestClient):
    response = client.put(
        f"/aiagents/update/1",
        data={"name": "chien"}, 
        headers = {"Authorization": f"Bearer {access_token}"}
    )
    data_update_aiagent = response.json()
    assert data_update_aiagent["name"] == "chien"

def test_delete_agent(client: TestClient):
    response = client.delete(f"/aiagents/delete/1", headers = {"Authorization": f"Bearer {access_token}"})
    assert response.json() == {"result": "delete success"}