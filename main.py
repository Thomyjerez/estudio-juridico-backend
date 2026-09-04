import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Backend Estudio Jurídico")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://estudio-juridico-two-kappa.vercel.app"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

class LeadJuridico(BaseModel):
    nombre: str
    email: str
    telefono: str
    area: str
    resumen: str

@app.post("/api/contacto")
async def recibir_contacto(lead: LeadJuridico):

    try:
        data = supabase.table("leads_juridicos").insert({
            "nombre": lead.nombre,
            "email": lead.email,
            "telefono": lead.telefono,
            "area": lead.area,
            "resumen": lead.resumen
        }).execute()
    except Exception as e:
        print(f"Error en Supabase: {e}")
        raise HTTPException(status_code=500, detail="Error al guardar en la base de datos")

    mensaje_telegram = (
        "<b>NUEVA CONSULTA - ESTUDIO JURIDICO</b>\n\n"
        f"<b> Cliente:</b> {lead.nombre}\n"
        f"<b> Teléfono:</b> {lead.telefono}\n"
        f"<b> Email:</b> {lead.email}\n"
        f"<b> Área Legal:</b> {lead.area.capitalize()}\n\n"
        f"<b> Resumen del caso:</b>\n<i>{lead.resumen}</i>"
    )

    url_telegram = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensaje_telegram,
        "parse_mode": "HTML"
    }
    
    try:
        requests.post(url_telegram, json=payload)
    except Exception as e:
        print(f"Error enviando Telegram: {e}")

    return {"status": "success", "message": "Consulta agendada con éxito"}