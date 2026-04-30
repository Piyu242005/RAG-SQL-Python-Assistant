# Project Overview & Instructions

## 🌟 Simple Explanation
This project is a **Smart AI Assistant** for SQL and Python. 
1. You ask a question.
2. It searches through local PDF handbooks.
3. It gives you a precise answer with the **exact page number** for proof.
4. **Everything stays on your computer.** No data is sent to the cloud, making it 100% private and free.

---

## 🚀 How to Run the Project

There are two ways to run this: the **Easy Way** (Docker) and the **Manual Way**.

### Method 1: The Easy Way (Docker)
If you have Docker installed, just run this one command in your main folder:
```powershell
docker-compose up --build
```
*Wait for it to finish, then open http://localhost in your browser.*

---

### Method 2: The Manual Way (Two Terminals)

**1. Start the Backend (API)**
Open a terminal and run:
```powershell
cd backend
venv\Scripts\activate
python main.py
```
*(Leave this running at http://localhost:8000)*

**2. Start the Frontend (UI)**
Open a **new** terminal tab and run:
```powershell
cd frontend
npm run dev
```
*(Open the link shown, usually http://localhost:5173)*

---

## 🧪 How to Run Evaluation (Quality Check)
To see how accurate the AI is, run:
```powershell
cd backend
python evals/runner.py
```
