import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.car_troubleshooting import CarTroubleshootingChatbot  # Ajuste en la importación

# Inicializamos el router de la API
router = APIRouter()

# Instancia del sistema experto
chatbot = CarTroubleshootingChatbot()

# Modelo para validar el mensaje del usuario
class UserMessage(BaseModel):
    message: str


@router.get("/get")
async def simple_get():
    print("Endpoint GET funcionando correctamente")
    return {"message": "El endpoint GET está funcionando correctamente"}


@router.post("/chat")
async def chat_with_bot(user_message: UserMessage):
    try:
        print(f"Received message: {user_message.message}")
        
        # Diagnosing the issue
        response = chatbot.diagnose(user_message.message)
        
        print(f"Chatbot response: {response}")
        return {"response": response}
    except Exception as e:
        print(f"Error in /chat endpoint: {e}")  # Log the error for debugging
        raise HTTPException(status_code=500, detail="An internal server error occurred.")
