from dotenv import load_dotenv
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain.chains.qa_with_sources.loading import load_qa_with_sources_chain
from langchain.schema import Document
from pathlib import Path
import os
import pandas as pd

load_dotenv()

role_map = {
    "engineering": ["engineering", "c-level"],
    "finance": ["finance", "c-level"],
    "marketing": ["marketing", "c-level"],
    "hr": ["hr", "c-level"],
    "general": ["employee", "finance", "marketing", "engineering", "hr", "c-level"]
}


CHUNK_SIZE=1000
COLLECTION_NAME="contents"
VECTORSTORE_DIR = Path(__file__).parent / "resource/vectorstore"

llm=None
vector_store=None

def load_all_documents(base_path="resources/data"):
    all_docs = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    for department in os.listdir(base_path):
        dep_path = os.path.join(base_path, department)
        if os.path.isdir(dep_path):
            for file in os.listdir(dep_path):
                file_path = os.path.join(dep_path, file)

                # Handle markdown files
                if file_path.endswith(".md"):
                    text = Path(file_path).read_text(encoding="utf-8", errors="ignore")

                # Handle CSV (only for hr)
                elif file_path.endswith(".csv"):
                    df = pd.read_csv(file_path).fillna("")
                    text = df.to_string(index=False)


                # Split text into chunks
                chunks = splitter.split_text(text)
                for chunk in chunks:
                    doc = Document(
                        page_content=chunk,
                        metadata={
                            "department": department,
                            "roles": ", ".join(role_map[department]),
                            "source": file
                        }
                    )
                    all_docs.append(doc)

    return all_docs



def initialize_components():
    global llm,vector_store
    api_key = os.getenv("GROQ_API_KEY")

    if llm is None:
        llm=ChatGroq(model="llama-3.3-70b-versatile",temperature=0.9,max_tokens=500,api_key=api_key)

    if vector_store is None:
        ef = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs = {"trust_remote_code":True}
        )

        vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=ef,
            persist_directory=str(VECTORSTORE_DIR)
        )

def process():
    print("Initializing components....")
    initialize_components()

    print("Resetting vector store....")
    vector_store.reset_collection()

    print("Loading all documents...")
    documents = load_all_documents()

    print("Storing documents in vector store......")
    vector_store.add_documents(documents)


def generate_answer(query, user_role):
    if not vector_store:
        raise RuntimeError("Vector database is not initialized")

    results = vector_store.similarity_search(query, k=4)

    allowed_docs = [
        doc for doc in results
        if user_role.lower() in [r.strip().lower() for r in doc.metadata["roles"].split(",")]
    ]

    if not allowed_docs:
        return "You are not authorized to access this information."

    chain = load_qa_with_sources_chain(llm, chain_type="stuff")
    response = chain({"input_documents": allowed_docs, "question": query}, return_only_outputs=True)

    return response["output_text"]


# if __name__ == "__main__":
#     process()
    
#     query = "Who are the employees with performance rating 5?"
#     user_role = "hr"
    
#     print("Querying now...")
#     answer = generate_answer(query, user_role)
#     print("Answer:\n", answer)

