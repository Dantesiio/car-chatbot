import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.endpoints import router  # Ajuste en la importación
from app.car_troubleshooting import CarTroubleshootingChatbot


app = FastAPI()

# Configurar CcleaORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar las rutas de los endpoints
app.include_router(router, prefix="/api", tags=["Chatbot"])
