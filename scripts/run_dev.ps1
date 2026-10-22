<#
.SYNOPSIS
    Local development orchestrator for Punjab GrainWatch.
.DESCRIPTION
    Starts the FastAPI backend (port 8000) and Astro frontend (port 4321),
    or executes test suites.
.PARAMETER Mode
    Execution mode: 'all' (default), 'backend', 'frontend', 'test', 'build'.
.EXAMPLE
    .\scripts\run_dev.ps1 -Mode all
    .\scripts\run_dev.ps1 -Mode backend
    .\scripts\run_dev.ps1 -Mode frontend
    .\scripts\run_dev.ps1 -Mode test
#>

param (
    [ValidateSet("all", "backend", "frontend", "test", "build")]
    [string]$Mode = "all"
)

$ErrorActionPreference = "Stop"
$WorkspaceRoot = Split-Path -Parent $PSScriptRoot

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "   Punjab GrainWatch — Local Development Runner (Windows/PS)" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "Workspace Root: $WorkspaceRoot"
Write-Host "Mode:           $Mode`n"

# Verify Phase 1 Catalog Exists
$CatalogPath = Join-Path $WorkspaceRoot "data\manifests\dataset_catalog.json"
if (-not (Test-Path $CatalogPath)) {
    Write-Host "[!] Warning: Dataset catalog not found. Running Phase 1 validation pipeline..." -ForegroundColor Yellow
    python (Join-Path $WorkspaceRoot "scripts\run_validation_pipeline.py")
}

if ($Mode -eq "test") {
    Write-Host "[*] Running complete test suite (Data Integrity + Backend API)..." -ForegroundColor Green
    pytest -v
    exit $LASTEXITCODE
}

if ($Mode -eq "build") {
    Write-Host "[*] Building frontend static distribution..." -ForegroundColor Green
    if (Test-Path "B:\temp") {
        $env:TEMP = "B:\temp"
        $env:TMP = "B:\temp"
    }
    $env:NODE_OPTIONS = "--max-old-space-size=4096"
    npm run build --prefix (Join-Path $WorkspaceRoot "frontend")
    exit $LASTEXITCODE
}

if ($Mode -eq "backend") {
    Write-Host "[*] Starting FastAPI Backend on http://127.0.0.1:8000..." -ForegroundColor Green
    Write-Host "    Swagger Docs: http://127.0.0.1:8000/docs"
    Write-Host "    Health Endpoint: http://127.0.0.1:8000/api/v1/health`n"
    python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
    exit $LASTEXITCODE
}

if ($Mode -eq "frontend") {
    Write-Host "[*] Starting Astro Frontend on http://localhost:4321..." -ForegroundColor Green
    npm run dev --prefix (Join-Path $WorkspaceRoot "frontend")
    exit $LASTEXITCODE
}

if ($Mode -eq "all") {
    Write-Host "[*] Starting Backend (Port 8000) and Frontend (Port 4321)..." -ForegroundColor Green
    Write-Host "    Backend will launch in background; Frontend will run in current terminal." -ForegroundColor Gray
    Write-Host "    Press Ctrl+C to terminate.`n"

    # Start backend in a background process
    $BackendProcess = Start-Process python -ArgumentList "-m uvicorn backend.main:app --host 127.0.0.1 --port 8000" -PassThru -NoNewWindow
    
    try {
        # Start frontend in foreground
        npm run dev --prefix (Join-Path $WorkspaceRoot "frontend")
    }
    finally {
        Write-Host "`n[*] Stopping backend process..." -ForegroundColor Yellow
        if ($BackendProcess -and -not $BackendProcess.HasExited) {
            Stop-Process -Id $BackendProcess.Id -Force
        }
        Write-Host "[*] Development session ended." -ForegroundColor Gray
    }
}
