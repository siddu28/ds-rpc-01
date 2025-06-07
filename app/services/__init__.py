## loading the necessary libraries

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

## loading the groq api key inorder to access the LLM model
load_dotenv()


## defined role_map to restrict the question level according to the users role 
role_map = {
    "engineering": ["engineering", "c-level"],
    "finance": ["finance", "c-level"],
    "marketing": ["marketing", "c-level"],
    "hr": ["hr", "c-level"],
    "general": ["employee", "finance", "marketing", "engineering", "hr", "c-level"]
}


## defining chunk size and the collection name for the vector store chromadb
CHUNK_SIZE=1000
COLLECTION_NAME="contents"
VECTORSTORE_DIR = Path(__file__).parent / "resource/vectorstore"

## initialized LLM and vector_store globally so that no need to rerun again and again if you enter the question, LLM will be already initialized
llm=None
vector_store=None

## loading the documents present in the resources/data - as the base path
def load_all_documents(base_path="resources/data"):
    
    ## storing all the loaded documents in the all_docs library
    all_docs = []

    ## using recussivecharacter text splitter we will split the documents in to chunks without exceeding the chunk size
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    ## as the main resources are present in this base directory , iterate through it and load it individually
    for department in os.listdir(base_path):

        ## join the department name with the basepath because deapartment name is the folder and the actual content is proveided inside that folder
        dep_path = os.path.join(base_path, department)

        ## iterate through the folder and join the path to get the total path of the source file
        for file in os.listdir(dep_path):
            file_path = os.path.join(dep_path, file)

            # Handle markdown files 
            if file_path.endswith(".md"):
                text = Path(file_path).read_text(encoding="utf-8", errors="ignore")

            # Handle CSV (only for hr) using pandas dataframe
            elif file_path.endswith(".csv"):
                df = pd.read_csv(file_path).fillna("")
                text = df.to_string(index=False)


            # Split text into chunks using recussive character text splitter
            chunks = splitter.split_text(text)
            for chunk in chunks:
                doc = Document(
                    page_content=chunk,
                    metadata={      ## based on the metadata you can filter or restrict the question based on their roles
                        "department": department,
                        "roles": ", ".join(role_map[department]),
                        "source": file
                    }
                )
                all_docs.append(doc)

    return all_docs


## initializing the components such as LLM, vector_store and hugging face embeddings
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

## function to initializing all components and adding docuemnts to the vector store chromadb
def process():
    print("Initializing components....")
    initialize_components()

    print("Resetting vector store....")
    vector_store.reset_collection()

    print("Loading all documents...")
    documents = load_all_documents()

    print("Storing documents in vector store......")
    vector_store.add_documents(documents)


## generating the final answer by passing the related context to the LLM
def generate_answer(query, user_role):
    if not vector_store:
        raise RuntimeError("Vector database is not initialized")

    ## searching the relevant context simliar to the user question and taking the top 4 similar chunks
    results = vector_store.similarity_search(query, k=4)

    ## checking wheather the role of user is accepted for the question using metadata filtering 
    allowed_docs = [
        doc for doc in results
        if user_role.lower() in [r.strip().lower() for r in doc.metadata["roles"].split(",")]
    ]

    ## if the current user role is not there in the allowed_docs then you can return unauthorized access ,so that you can restrict role based questions here
    if not allowed_docs:
        return "You are not authorized to access this information."

    ## passing the relevant documents to the LLM and summarize it and it will produce the output
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


