import os
import google.generativeai as genai
from dotenv import load_dotenv

# Cargar el archivo .env
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY no encontrada en el .env")
    exit()

genai.configure(api_key=api_key)

print("Consultando modelos disponibles para tu API Key...\n")
try:
    # Listar todos los modelos que soportan generación de texto
    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods:
            # Quitamos el prefijo 'models/' para que veas exactamente qué poner en tu .env
            nombre_limpio = m.name.replace('models/', '')
            print(f"- {nombre_limpio}")
            
    print("\n✅ Copia UNO de los nombres de arriba y ponlo en LLM_MODEL_AGENT en tu .env")
except Exception as e:
    print(f"Error de conexión con la API: {e}")