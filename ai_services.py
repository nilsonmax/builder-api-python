import os
import json
import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

router = APIRouter(prefix="/api/ai", tags=["AI"])

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("⚠️ ADVERTENCIA: No se encontró la variable GEMINI_API_KEY en el archivo .env")

client = genai.Client(api_key=GEMINI_API_KEY)

class TemplateRequest(BaseModel):
    niche: str
    blocks: list

@router.post("/generate-template")
async def generate_template(payload: TemplateRequest):
    try:
        prompt = f"""
        Eres un diseñador experto en E-commerce. Recibirás una lista de bloques JSON de una tienda web.
        Tu trabajo es adaptar ÚNICAMENTE los textos (títulos, subtítulos, botones, preguntas) para el nicho: '{payload.niche}'.
        
        REGLAS ESTRICTAS:
        1. NUNCA elimines ni modifiques propiedades visuales o de estructura como 'bgColor', 'id', 'type' o URLs de imágenes.
        2. Conserva TODAS las llaves originales dentro del objeto 'props' de cada bloque.
        3. Devuelve ÚNICAMENTE un objeto JSON válido con la estructura {{ "blocks": [...] }} sin markdown.
        
        Estructura actual: {json.dumps(payload.blocks)}
        """

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        
        raw_text = response.text.strip()
        cleaned_text = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text, flags=re.IGNORECASE)
        ai_data = json.loads(cleaned_text)

        validated_blocks = []
        ai_blocks = ai_data.get("blocks", [])

        for orig_block, ai_block in zip(payload.blocks, ai_blocks):
            orig_props = orig_block.get("props", {})
            ai_props = ai_block.get("props", {})

            merged_props = {**orig_props, **ai_props}

            validated_blocks.append({
                "id": orig_block.get("id"),
                "type": orig_block.get("type"),
                "props": merged_props
            })

        return {"blocks": validated_blocks}

    except Exception as e:
        print(f"\n❌ [ERROR EN GEMINI]: {str(e)}\n")
        raise HTTPException(
            status_code=500, 
            detail=f"Error en el servicio de IA: {str(e)}"
        )