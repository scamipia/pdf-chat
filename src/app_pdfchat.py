import os
import shutil
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.chat_message_histories import ChatMessageHistory
import langdetect

# Fix para Windows: usar ProactorEventLoop en lugar del default
# Esto es necesario para que asyncio.create_subprocess_exec funcione correctamente
# El ProactorEventLoop es necesario para crear subprocesos en Windows
if sys.platform == "win32":
    import asyncio
    # Establecer la política de event loop para Windows
    # Esto debe hacerse ANTES de crear cualquier event loop
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


# Usamos imports relativos porque estamos en src/ 
from utils import process_document_file

os.environ["ANONYMIZED_TELEMETRY"] = "False"


app = FastAPI(title="PDF Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Estado global
chat_history = ChatMessageHistory()
retriever_global = None
conversational_rag_chain = None


@app.post("/upload")
async def upload_file(file: UploadFile):
    """
    Endpoint para subir un archivo mediante formulario multipart.
    
    El archivo se guarda en data/uploads/ y luego se procesa usando
    la función común process_document_file().
    """
    print(f"\n📂 [UPLOAD] Recibido archivo: {file.filename}")

    # Guardar el archivo subido
    upload_dir = "data/uploads/"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Procesar el archivo usando la función común
    try:
        global conversational_rag_chain, retriever_global
        conversational_rag_chain, retriever_global, info = await process_document_file(
            file_path, file.filename, chat_history
        )
        print("✅ [UPLOAD] Pipeline listo para usar")
        print(f"📊 [UPLOAD] Chunks: {info['chunks_count']}, Retriever docs: {info['retriever_docs']}")
        return {"message": f"Archivo {file.filename} cargado y procesado exitosamente"}
    except ValueError as e:
        return {"error": str(e)}


@app.post("/chat")
async def chat(question: str = Form(...)):
    print(f"\n💬 [CHAT] Pregunta recibida: {question}")

    if conversational_rag_chain is None:
        print("🚫 No hay chain cargada aún.")
        return {"error": "Primero subí un documento."}

    try:
        lang = langdetect.detect(question)
        language_instruction = "Responde en español." if lang == "es" else "Keep your answer in English."
    except Exception:
        language_instruction = "Keep your answer concise."

    # Ejecutar consulta
    response = conversational_rag_chain.invoke(
        {"input": f"{language_instruction} {question}"},
        config={"configurable": {"session_id": "default"}}
    )

    print("🧠 Respuesta generada correctamente")
    return {"answer": response["answer"]}


@app.post("/clear_history")
async def clear_history():
    chat_history.clear()
    print("🧹 Historial limpiado")
    return {"message": "Historial del chat eliminado"}
