import sys
import os
sys.path.insert(0, r"C:\FreelancerIAOS")

import time
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from core.motor.motor_capacidades import evaluar_oferta
from core.motor.filtro_comercial import filtrar_respuesta_cliente

app = FastAPI(title="Servicio Central del Motor Universal")

PETICIONES = {}

class Limitador(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        ip = request.client.host
        ahora = time.time()
        PETICIONES[ip] = [t for t in PETICIONES.get(ip, []) if ahora - t < 60]
        if len(PETICIONES[ip]) >= 30:
            return JSONResponse({"error": "Demasiadas peticiones, espera un momento"}, status_code=429)
        PETICIONES[ip].append(ahora)
        return await call_next(request)

app.add_middleware(Limitador)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "servicio": "motor_universal"}

@app.post("/evaluar")
def evaluar(body: dict = Body(...)):
    texto = body.get("necesidad", "")
    if len(texto) > 2000:
        return {"error": "El texto no puede superar 2000 caracteres"}
    texto = texto.strip()
    if not texto:
        return {"error": "Falta el campo necesidad"}

    evaluacion = evaluar_oferta(texto)

    if evaluacion["aprobado"]:
        mensaje = "Gracias por tu solicitud. Podemos desarrollar tu proyecto. Te enviaremos una propuesta con alcance y siguientes pasos."
    else:
        mensaje = "Gracias por tu solicitud. Por ahora este tipo de proyecto esta fuera de nuestro alcance actual."

    return {
        "aprobado": evaluacion["aprobado"],
        "motivo": evaluacion.get("motivo"),
        "mensaje": filtrar_respuesta_cliente(mensaje)
    }
