# ============================================================
#   RAG-SQL-Python-Assistant - One-Click Startup Script
#   Order: Ollama -> Embeddings (if needed) -> Backend -> Frontend -> Browser
# ============================================================

$ROOT     = $PSScriptRoot
$BACKEND  = Join-Path $ROOT "backend"
$FRONTEND = Join-Path $ROOT "frontend"
$VENV     = Join-Path $BACKEND "venv\Scripts\Activate.ps1"
$CHROMA   = Join-Path $BACKEND "chroma_db\chroma.sqlite3"

function Write-Step($msg) {
    Write-Host ""
    Write-Host ("=" * 55) -ForegroundColor Cyan
    Write-Host "  $msg" -ForegroundColor Cyan
    Write-Host ("=" * 55) -ForegroundColor Cyan
}
function Write-OK($msg)   { Write-Host "  [OK] $msg" -ForegroundColor Green  }
function Write-WARN($msg) { Write-Host "  [!]  $msg" -ForegroundColor Yellow }
function Write-ERR($msg)  { Write-Host "  [X]  $msg" -ForegroundColor Red    }

# ── STEP 1: Start Ollama ─────────────────────────────────
Write-Step "STEP 1 - Starting Ollama"

$ollamaRunning = $false
try {
    Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 3 -ErrorAction Stop | Out-Null
    $ollamaRunning = $true
    Write-OK "Ollama is already running"
} catch {
    Write-WARN "Ollama not detected - launching ollama serve..."
    Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Minimized
    Write-Host "  Waiting for Ollama to start" -NoNewline
    for ($i = 0; $i -lt 20; $i++) {
        Start-Sleep -Seconds 1
        Write-Host "." -NoNewline
        try {
            Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction Stop | Out-Null
            $ollamaRunning = $true
            Write-Host " Ready!" -ForegroundColor Green
            break
        } catch {}
    }
    if (-not $ollamaRunning) {
        Write-ERR "Ollama failed to start. Make sure 'ollama' is installed and in PATH."
        Write-Host "  Install from: https://ollama.com/download" -ForegroundColor Yellow
        pause
        exit 1
    }
}

# Check / pull llama3.2 model
Write-Host "  Checking llama3.2 model..." -NoNewline
try {
    $tags = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 5
    $hasModel = ($tags.models | Where-Object { $_.name -like "llama3.2*" }).Count -gt 0
    if ($hasModel) {
        Write-Host " Found!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-WARN "llama3.2 not found - pulling model (first-time only, may take a few minutes)..."
        Start-Process -FilePath "ollama" -ArgumentList "pull", "llama3.2" -Wait -WindowStyle Normal
        Write-OK "llama3.2 pulled successfully"
    }
} catch {
    Write-WARN "Could not verify model list, continuing..."
}

# ── STEP 2: Embeddings (only if ChromaDB missing) ────────
Write-Step "STEP 2 - Vector Database / Embeddings"

if (Test-Path $CHROMA) {
    Write-OK "ChromaDB already exists - skipping embedding"
} else {
    Write-WARN "ChromaDB not found - running initialize_db.py (takes ~40s first time)..."

    $activateAndRun = "& '$VENV'; Set-Location '$BACKEND'; python initialize_db.py"
    $initProc = Start-Process -FilePath "powershell" `
        -ArgumentList "-NoProfile", "-Command", $activateAndRun `
        -PassThru -Wait -WindowStyle Normal

    if ($initProc.ExitCode -eq 0) {
        Write-OK "Embeddings created and indexed into ChromaDB"
    } else {
        Write-ERR "Embedding initialization failed (exit $($initProc.ExitCode)) - app may have limited functionality"
        Start-Sleep -Seconds 2
    }
}

# ── STEP 3: FastAPI Backend ───────────────────────────────
Write-Step "STEP 3 - Starting FastAPI Backend (port 8000)"

$backendCmd = "Write-Host 'RAG Backend' -ForegroundColor Cyan; & '$VENV'; Set-Location '$BACKEND'; python main.py"
Start-Process "powershell" -ArgumentList "-NoProfile", "-NoExit", "-Command", $backendCmd

Write-Host "  Waiting for backend" -NoNewline
$backendReady = $false
for ($i = 0; $i -lt 35; $i++) {
    Start-Sleep -Seconds 1
    Write-Host "." -NoNewline
    try {
        Invoke-RestMethod -Uri "http://localhost:8000/api/health" -TimeoutSec 2 -ErrorAction Stop | Out-Null
        $backendReady = $true
        Write-Host " Ready!" -ForegroundColor Green
        break
    } catch {}
}
if (-not $backendReady) { Write-WARN "Backend is slow to start - continuing anyway..." }

# ── STEP 4: Vite Frontend ─────────────────────────────────
Write-Step "STEP 4 - Starting Vite Frontend (port 5173)"

$frontendCmd = "Write-Host 'RAG Frontend' -ForegroundColor Magenta; Set-Location '$FRONTEND'; npm run dev"
Start-Process "powershell" -ArgumentList "-NoProfile", "-NoExit", "-Command", $frontendCmd

Write-Host "  Waiting for frontend" -NoNewline
$frontendReady = $false
for ($i = 0; $i -lt 20; $i++) {
    Start-Sleep -Seconds 1
    Write-Host "." -NoNewline
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        if ($r.StatusCode -eq 200) {
            $frontendReady = $true
            Write-Host " Ready!" -ForegroundColor Green
            break
        }
    } catch {}
}
if (-not $frontendReady) {
    Write-WARN "Frontend not confirmed yet - opening browser anyway..."
    Start-Sleep -Seconds 2
}

# ── STEP 5: Open Browser ─────────────────────────────────
Write-Step "STEP 5 - Opening App in Browser"
Start-Process "http://localhost:5173"

Write-Host ""
Write-Host ("=" * 55) -ForegroundColor Green
Write-Host "  ALL SYSTEMS RUNNING!" -ForegroundColor Green
Write-Host ("=" * 55) -ForegroundColor Green
Write-Host ""
Write-Host "  App URL  :  http://localhost:5173" -ForegroundColor White
Write-Host "  API Docs :  http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Ollama   :  http://localhost:11434" -ForegroundColor White
Write-Host ""
Write-Host "  Close this window to stop the launcher" -ForegroundColor DarkGray
Write-Host ("=" * 55) -ForegroundColor Green
Write-Host ""

# Keep launcher alive
while ($true) { Start-Sleep -Seconds 60 }
