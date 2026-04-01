# Start All Services Script
# Start sequence: Redis -> Celery Worker -> API Server

param(
    [switch]$SkipRedis,
    [switch]$SkipWorker,
    [switch]$DevMode
)

$redisPath = "C:\Program Files\Redis\redis-server.exe"
$redisConfig = "C:\Program Files\Redis\redis.windows.conf"

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Universal Q&A Framework - Start All Services" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Check if in project directory
if (-not (Test-Path "app")) {
    Write-Host "Error: Please run this script from project root directory" -ForegroundColor Red
    exit 1
}

# Check Python environment
Write-Host "Checking Python environment..." -ForegroundColor Yellow

# Try to check environment
try {
    $checkResult = python check_env.py 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Environment check failed"
    }
    Write-Host "Environment check passed" -ForegroundColor Green
} catch {
    Write-Host "Error: Python environment check failed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible reasons:" -ForegroundColor Yellow
    Write-Host "1. Not in the correct conda environment (rag_env)" -ForegroundColor White
    Write-Host "2. Dependencies not installed" -ForegroundColor White
    Write-Host ""
    Write-Host "Solutions:" -ForegroundColor Cyan
    Write-Host "1. Activate environment: conda activate rag_env" -ForegroundColor White
    Write-Host "2. Install dependencies: pip install -r requirements.txt" -ForegroundColor White
    Write-Host ""
    Write-Host "Current Python: $(python --version)" -ForegroundColor Gray
    Write-Host "Python path: $(python -c 'import sys; print(sys.executable)')" -ForegroundColor Gray
    exit 1
}

Write-Host ""

# Start Redis
if (-not $SkipRedis -and -not $DevMode) {
    if (Test-Path $redisPath) {
        Write-Host "[1/3] Starting Redis..." -ForegroundColor Yellow
        
        # Check if Redis is already running
        $redisProcess = Get-Process -Name "redis-server" -ErrorAction SilentlyContinue
        if ($redisProcess) {
            Write-Host "      Redis is already running" -ForegroundColor Green
        } else {
            # Start Redis in background
            Start-Process -FilePath $redisPath -ArgumentList $redisConfig -WindowStyle Minimized
            Start-Sleep -Seconds 2
            
            # Verify Redis started successfully
            $redisProcess = Get-Process -Name "redis-server" -ErrorAction SilentlyContinue
            if ($redisProcess) {
                Write-Host "      Redis started successfully" -ForegroundColor Green
            } else {
                Write-Host "      Error: Failed to start Redis" -ForegroundColor Red
                exit 1
            }
        }
    } else {
        Write-Host "Error: Redis not found" -ForegroundColor Red
        Write-Host "Redis Path: $redisPath" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Solutions:" -ForegroundColor Cyan
        Write-Host "1. Install Redis for Windows" -ForegroundColor White
        Write-Host "2. Or use dev mode: .\start_all.ps1 -DevMode" -ForegroundColor White
        exit 1
    }
} else {
    if ($DevMode) {
        Write-Host "[1/3] Dev Mode: Skipping Redis (using fakeredis)" -ForegroundColor Gray
    } else {
        Write-Host "[1/3] Skipping Redis" -ForegroundColor Gray
    }
}

Write-Host ""

# Start Celery Worker
if (-not $SkipWorker -and -not $DevMode) {
    Write-Host "[2/3] Starting Celery Worker..." -ForegroundColor Yellow
    
    # Check if Worker is already running
    $workerProcess = Get-Process -Name "python" | Where-Object { $_.CommandLine -like "*celery*" } -ErrorAction SilentlyContinue
    if ($workerProcess) {
        Write-Host "      Celery Worker is already running" -ForegroundColor Green
    } else {
        # Start Worker in new window
        Start-Process powershell -ArgumentList "-Command", "cd '$PWD'; python start_celery_worker.py" -WindowStyle Normal
        Start-Sleep -Seconds 2
        Write-Host "      Celery Worker started successfully" -ForegroundColor Green
    }
} else {
    if ($DevMode) {
        Write-Host "[2/3] Dev Mode: Skipping Celery Worker (tasks run synchronously)" -ForegroundColor Gray
    } else {
        Write-Host "[2/3] Skipping Celery Worker" -ForegroundColor Gray
    }
}

Write-Host ""

# Start API Server
Write-Host "[3/3] Starting API Server..." -ForegroundColor Yellow

if ($DevMode) {
    $env:DEV_MODE = "true"
    Write-Host "      Dev Mode: Using fakeredis" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Services Started!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan

if ($DevMode) {
    Write-Host "Mode: Development (fakeredis)" -ForegroundColor Cyan
} else {
    Write-Host "Mode: Production (Redis)" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Yellow
Write-Host "  - Web UI: http://localhost:8000" -ForegroundColor White
Write-Host "  - API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""

# Start API Server (in current window)
python start_api_server.py
