import os
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader, UnstructuredPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_models import ChatOllama
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory

# Modelo LLM
llm = ChatOllama(model="mistral:latest")

# Prompts base
contextualize_prompt = ChatPromptTemplate.from_messages([
    ("system", """Dado un historial de conversación y la última pregunta del usuario,
    que podría hacer referencia a mensajes anteriores, reformulá la pregunta
    para que sea comprensible por sí sola. No respondas la pregunta."""),
    MessagesPlaceholder("chat_history"),
    ("user", "{input}")
])

# chat_history se pasa como parámetro ahora, no es una variable global aquí

system_prompt = (
    "Sos un asistente útil para responder preguntas basadas en el contexto proporcionado. "
    "Respondé de forma concisa y clara. "
    "Si la pregunta no está relacionada con el contexto, decí 'No lo sé'. "
    "Si la pregunta no es clara, pedí más información. "
    "\n\nContexto:\n{context}"
)

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder("chat_history"),
    ("user", "{input}")
])

question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

# ============================================
# FUNCIONES AUXILIARES
# ============================================

def load_document(file_path: str, filename: str):
    """
    Carga un documento según su extensión usando el loader apropiado.
    
    Esta función detecta el tipo de archivo y usa el loader correspondiente:
    - PDF: PyPDFLoader (con fallback a UnstructuredPDFLoader)
    - DOCX: Docx2txtLoader
    - TXT: TextLoader
    
    Args:
        file_path: Ruta completa del archivo a cargar
        filename: Nombre del archivo (para detectar la extensión)
        
    Returns:
        Lista de documentos de LangChain (Document objects)
        
    Raises:
        ValueError: Si el formato del archivo no es soportado
    """
    if filename.endswith(".pdf"):
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            print("📘 PyPDFLoader OK")
        except Exception:
            print("⚠️ PyPDFLoader falló, usando UnstructuredPDFLoader")
            loader = UnstructuredPDFLoader(file_path)
            documents = loader.load()
    elif filename.endswith(".docx"):
        loader = Docx2txtLoader(file_path)
        documents = loader.load()
    elif filename.endswith(".txt"):
        loader = TextLoader(file_path)
        documents = loader.load()
    else:
        raise ValueError("Formato de archivo no soportado")
    
    return documents


def create_rag_pipeline(documents, chat_history_instance):
    """
    Crea el pipeline RAG completo a partir de documentos cargados.
    
    Esta función:
    1. Divide los documentos en chunks
    2. Crea embeddings y vectorstore
    3. Configura el retriever
    4. Crea las chains conversacionales
    
    Args:
        documents: Lista de documentos de LangChain
        chat_history_instance: Instancia de ChatMessageHistory a usar para el historial
        
    Returns:
        Tupla con (conversational_rag_chain, retriever, info_dict)
        donde info_dict contiene chunks_count y retriever_docs
    """
    # Dividir documentos en chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)
    print(f"📑 Total chunks generados: {len(chunks)}")
    
    # Crear embeddings y vectorstore con persistencia en disco
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    persist_directory = "data/chroma_store"
    os.makedirs(persist_directory, exist_ok=True)
    
    # Crear o reemplazar el vectorstore persistente
    vectorstore = Chroma.from_documents(
        chunks, 
        embeddings,
        persist_directory=persist_directory
    )
    print(f"💾 Vectorstore guardado en: {persist_directory}")
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    # Test rápido del retriever
    test_docs = retriever.invoke("test")
    print(f"🧩 Retriever test → {len(test_docs)} documentos recuperados")
    
    # Crear chain conversacional
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    
    # Crear la chain conversacional con el historial proporcionado
    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        lambda session_id: chat_history_instance,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
    
    info_dict = {
        "chunks_count": len(chunks),
        "retriever_docs": len(test_docs)
    }
    
    return conversational_rag_chain, retriever, info_dict


async def process_document_file(file_path: str, filename: str, chat_history_instance) -> tuple:
    """
    Procesa un archivo de documento y crea el pipeline RAG.
    
    Esta función orquesta el proceso completo:
    1. Carga el documento usando load_document()
    2. Crea el pipeline RAG usando create_rag_pipeline()
    
    Args:
        file_path: Ruta completa del archivo a procesar
        filename: Nombre del archivo (para mensajes informativos)
        chat_history_instance: Instancia de ChatMessageHistory a usar para el historial
        
    Returns:
        Tupla con (conversational_rag_chain, retriever, info_dict)
        donde info_dict contiene información del procesamiento
        
    Raises:
        ValueError: Si el formato del archivo no es soportado
    """
    # Paso 1: Cargar el documento
    documents = load_document(file_path, filename)
    
    # Paso 2: Crear el pipeline RAG
    conversational_rag_chain, retriever, info_dict = create_rag_pipeline(documents, chat_history_instance)
    
    return conversational_rag_chain, retriever, info_dict
