# backend/main.py
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from typing import Optional
from datetime import datetime, timedelta
import glob

# Importar el motor TTS
from tts_engine import synthesize_speech, OUTPUT_DIR

app = FastAPI(title="FastSpeech2 TTS API")

# Configuración CORS
origins = [
    "http://localhost:3000",
    "localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Función para limpiar archivos antiguos
def cleanup_old_files():
    """Limpia archivos de audio más antiguos que 1 hora."""
    try:
        current_time = datetime.now()
        for file_path in glob.glob(os.path.join(OUTPUT_DIR, "*.wav")):
            file_time = datetime.fromtimestamp(os.path.getctime(file_path))
            if current_time - file_time > timedelta(hours=1):
                os.remove(file_path)
                print(f"Archivo eliminado: {file_path}")
    except Exception as e:
        print(f"Error al limpiar archivos: {str(e)}")

@app.post("/api/tts")
async def text_to_speech_endpoint(
    text_payload: dict,
    background_tasks: BackgroundTasks
):
    """
    Endpoint for text-to-speech conversion.
    
    Args:
        text_payload: Dictionary containing the text to convert
            {
                "text": "Text to convert to speech"
            }
    """
    try:
        # Validate input
        text = text_payload.get("text")
        if not text:
            raise HTTPException(
                status_code=400,
                detail="No text provided for conversion"
            )
        
        if len(text) > 500:  # Reasonable character limit
            raise HTTPException(
                status_code=400,
                detail="Text exceeds the 500 character limit"
            )

        print(f"Text received for TTS: {text}")

        # Generate audio using default model parameters
        audio_file_path = synthesize_speech(text)
        
        if not audio_file_path or not os.path.exists(audio_file_path):
            raise HTTPException(
                status_code=500,
                detail="Error generating audio"
            )

        # Schedule cleanup of old files
        background_tasks.add_task(cleanup_old_files)

        # Return the audio file
        return FileResponse(
            path=audio_file_path,
            media_type="audio/wav",
            filename=os.path.basename(audio_file_path)
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Unexpected error in /api/tts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/api/health")
async def health_check():
    """Endpoint para verificar el estado del servidor."""
    try:
        # Verificar que el directorio de salida existe
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        
        return JSONResponse({
            "status": "ok",
            "message": "El servidor TTS está funcionando correctamente",
            "output_dir": OUTPUT_DIR,
            "available_space": shutil.disk_usage(OUTPUT_DIR).free
        })
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en el servidor: {str(e)}"
        )

@app.get("/")
def read_root():
    """Endpoint raíz con información básica de la API."""
    return {
        "message": "FastSpeech2 TTS API está funcionando!",
        "endpoints": {
            "/api/tts": "POST - Convierte texto a voz",
            "/api/health": "GET - Verifica el estado del servidor"
        },
        "version": "1.0.0"
    }