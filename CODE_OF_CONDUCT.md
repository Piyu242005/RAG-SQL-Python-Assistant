# Code of Conduct

## How to Run the Application

If you are contributing or testing the application locally, please follow these steps to run the servers correctly:

**1. Open Terminal 1 (Backend)**
Copy and paste this:
```powershell
cd "c:\Users\Piyu\Downloads\RAG (Retrieval-Augmented Generation) system using SQL + Python PDFs\backend"
.\venv\Scripts\python.exe -m uvicorn main:app --reload
```
*(Leave this window open and running)*

**2. Open Terminal 2 (Frontend)**
Open a new tab/window and paste this:
```powershell
cd "c:\Users\Piyu\Downloads\RAG (Retrieval-Augmented Generation) system using SQL + Python PDFs\frontend"
npm run dev
```
*(Leave this window open too)*

Once both are running, open your browser to http://localhost:5173. The new UI and chat history will be working perfectly!
