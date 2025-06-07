# DS RPC 01: Internal chatbot with role based access control

# Problem Statement:
This project is a role-based chatbot application built using FastAPI, Streamlit, and LangChain + Groq LLM. It restricts users to ask questions only within their role-based access level. For example, an HR user can only query HR-related documents, while Engineering can only access Engineering-related data.

Visit the challenge page to learn more: [DS RPC-01](https://codebasics.io/challenge/codebasics-gen-ai-data-science-resume-project-challenge)
![alt text](resources/RPC_01_Thumbnail.jpg)
### Roles Provided
 - **engineering**
 - **finance**
 - **general**
 - **hr**
 - **marketing**

# This is Project Structure:

```
project/
│
├── app/
│ └── services.py ← Core LLM + VectorDB logic
│
├── main.py ← FastAPI API (login, chat endpoints)
├── streamlit_app.py ← Streamlit UI (frontend)
│
├── resources/
│ └── data/ ← Department-wise document sources
│ ├── engineering/
│ ├── hr/
│ ├── finance/
│ └── marketing/
│
└── resource/
└── vectorstore/ ← Vector database for Chroma
```


🚀 Project Flow Overview

📁 1. Document Preparation and Processing
All documents are stored in the resources/data folder, organized by department (e.g., hr, marketing, engineering).

The process() function:
- Loads all department-wise files (Markdown/CSV).
- Splits them into smaller chunks using LangChain's RecursiveCharacterTextSplitter.
- Adds metadata like department name and allowed roles.
- Stores them in Chroma vector store after generating embeddings using HuggingFace.

🧠 2. LLM and Vector Store Initialization
On the first question or document processing:
- The Groq API (LLaMA 3 model) is initialized.
- Vector store is created using ChromaDB.
- Embeddings are generated using all-MiniLM-L6-v2.
- Then we can filter the documents based on the metadata , inorder to restrict the role based questions

🔐 3. FastAPI Backend (main.py)
FastAPI server handles:
- User Login (/login) using basic HTTP authentication.
- Protected Chat Route (/chat):
- Checks the user's role.
- Runs a similarity search on documents using ChromaDB.
- Filters results based on user role.
- Sends allowed documents to the LLM to generate an answer.

💻 4. Streamlit Frontend (app.py)
Simple login page where users can enter their username and password.
On successful login:
- They are redirected to a chatbot interface and asks to enter the username and password to check the credentials , I have a dummy user database , so i restricted upto some few people
- Users can enter questions and receive role-based answers.
- Supports logout to switch between user roles.

📮 Postman Testing (Backend API)
You can use Postman to test the HTTP endpoints like /login and /chat.
🔸 Screenshot: Testing /login endpoint using Postman:
![Image](https://github.com/user-attachments/assets/acaf1a4c-6aef-469f-a6de-1363460b9e9b)
![Image](https://github.com/user-attachments/assets/5f0eeebb-c51d-4b32-a295-1ce7655301e4)

🔸 Screenshot: checking wheather engineering team person can access finantial questions:
![Image](https://github.com/user-attachments/assets/d81172c2-232d-4b3d-b9f4-0a365f81280f)


🖥️ Streamlit Frontend (Chatbot UI)
Once the backend is running, you can launch the chatbot interface via Streamlit.
🔸 Screenshot: Streamlit UI after successful login
![Image](https://github.com/user-attachments/assets/a195508e-ac0c-4520-bb61-cfb9c8edc006)

🔸 Screenshot: checking wheather engineering team person can access finantial questions:
![Image](https://github.com/user-attachments/assets/c976f9c5-785e-4199-a536-adb67347f08c)

✨ Tech Stack
- Frontend: Streamlit
- Backend: FastAPI
- LLM: LLaMA-3.3 70B via Groq API
- Vector Store: ChromaDB
- Embeddings: HuggingFace Transformers
- LangChain: Document loading, QA chain, chunking
- Postman: Manual API testing
- Dotenv: Secure API key loading

## Setup Instructions

1. **Clone the repository**:
   ```bash
   https://github.com/siddu28/ds-rpc-01

2. **Install dependencies:**:   
   ```commandline
    pip install -r requirements.txt
   ```

3. **Run the fastapi server:**:   
   ```commandline
    uvicorn app.main:app --reload
   ```
   
3. **Run the streamlit app:**:   
   ```commandline
    streamlit run streamlit_app.py
   ```

