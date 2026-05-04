# 🐳 Docker Run Guide

This guide provides step-by-step instructions to run the **RAG-SQL-Python-Assistant** project using Docker.

## Prerequisites

Before running the Docker commands, ensure you have the following ready on your machine:

1. **Docker Desktop**: Make sure it is installed and running. You should see the Docker icon in your system tray.
2. **Ollama**: The Docker backend connects to a local Ollama instance (via `host.docker.internal`). Ensure Ollama is installed and running on your host machine.
3. **Pull the Model**: Ensure you have pulled the required local model in Ollama. Open a terminal and run:
   ```bash
   ollama pull llama3.2
   ```

---

## Step-by-Step Instructions

### 1. Open a Terminal in Your Project Directory
Open PowerShell or Command Prompt and navigate to the root folder of your project:
```powershell
cd c:\Users\Piyu\Downloads\RAG-SQL-Python-Assistant
```

### 2. Build and Start the Docker Containers
Run the following command to build the Docker images and start all services in detached mode (in the background):
```powershell
docker compose up --build -d
```
> **Note:** If you have an older version of Docker, you might need to use `docker-compose` (with a hyphen) instead of `docker compose`.

This command automatically provisions:
- A **Redis** container for caching and conversational memory.
- The **FastAPI Backend** container (exposed on port `8000`).
- The **React/Vite Frontend** container (exposed on port `80`).

### 3. Access the Application
Once the containers are successfully up and running, you can access your application:
- **Frontend UI**: Open your browser and navigate to [http://localhost](http://localhost) (or `http://localhost:80`).
- **Backend API Docs**: To access the FastAPI Swagger UI, go to [http://localhost:8000/docs](http://localhost:8000/docs).

---

## Helpful Docker Commands

### Viewing Logs
If you want to monitor what is happening in the background or debug an issue, you can view the live logs for all services:
```powershell
docker compose logs -f
```
*(Press `Ctrl+C` to stop viewing the logs)*

### Stopping the Application
When you are done using the application, you can safely stop and remove the containers by running:
```powershell
docker compose down
```

### Rebuilding After Code Changes
If you make changes to the code (in `backend/` or `frontend/`), you will need to rebuild the images:
```powershell
docker compose up --build -d
```
