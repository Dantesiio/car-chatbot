import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi.testclient import TestClient
from app.main import app
from app.car_troubleshooting import CarTroubleshootingChatbot
from app.car_troubleshooting import create_bayesian_network

client = TestClient(app)

def test_get_endpoint():
    response = client.get("/api/get")
    assert response.status_code == 200
    assert "response" in response.json()
    assert response.json()["response"] == "raton"  # Asegura que el resultado es el esperado

def test_post_chat_endpoint():
    response = client.post(
        "/api/chat",
        json={"message": "not starting"}  # Mensaje representativo
    )
    assert response.status_code == 200
    assert "response" in response.json()
    assert response.json()["response"] != ""  # Asegura que hay alguna respuesta del chatbot
def test_diagnose_no_start():
    chatbot = CarTroubleshootingChatbot()
    response = chatbot.diagnose("not starting")
    assert response == "Do the Starter cranks?"  # Asegura que devuelve la primera pregunta esperada

def test_diagnose_unusual_noise():
    chatbot = CarTroubleshootingChatbot()
    response = chatbot.diagnose("unusual noise")
    assert response == "Noise on bumps only?"  # Asegura que devuelve la pregunta correcta

def test_unknown_message():
    chatbot = CarTroubleshootingChatbot()
    response = chatbot.diagnose("random text")
    assert response == "Sorry, I don't understand the problem. Could you describe it in another way?"

def test_bayesian_network_structure():
    model = create_bayesian_network()
    assert len(model.nodes()) > 0  # Asegura que hay nodos en la red
    assert len(model.edges()) > 0  # Asegura que hay conexiones en la red

def test_bayesian_network_cpds():
    model = create_bayesian_network()
    assert model.get_cpds("Battery") is not None 
    assert model.get_cpds("Ignition") is not None  