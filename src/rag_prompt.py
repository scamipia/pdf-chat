import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama
import langdetect

os.environ["ANONYMIZED_TELEMETRY"] = "False"

llm = ChatOllama(model="gemma:2b")

loader = TextLoader("data/ai-discussion.txt")
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(documents)

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma.from_documents(chunks, embeddings)
retriever = vectorstore.as_retriever()

question = input("Enter your question: ")

if question:
    lang = langdetect.detect(question)
    if lang == "es":
        language_instruction = "Responde en español."
    else:
        language_instruction = "Keep your answer in English."

    system_prompt = (
        "Sos un asistente útil para responder preguntas basadas en el contexto proporcionado. "
        "Respondé de forma concisa y clara. "
        "Si la pregunta no está relacionada con el contexto, decí 'No lo sé'. "
        "Si la pregunta no es clara, pedí más información. "
        f"{language_instruction}"
        "\n\nContexto:\n{context}"
    )

    prompt = ChatPromptTemplate.from_template(
        "Sistema: " + system_prompt + "\n\nUsuario: {input}"
    )

    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = create_retrieval_chain(retriever, question_answer_chain)


    response = retrieval_chain.invoke({"input": question})
    print("\nRespuesta:")
    print(response["answer"])
else:
    print("No question provided.")