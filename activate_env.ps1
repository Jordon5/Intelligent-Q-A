# Activate rag_env environment and run command
param(
    [Parameter(ValueFromRemainingArguments=$true)]
    $Arguments
)

# Check if conda is available
$condaPath = Get-Command conda -ErrorAction SilentlyContinue
if (-not $condaPath) {
    Write-Host "Error: Conda not found" -ForegroundColor Red
    Write-Host "Please ensure Anaconda or Miniconda is installed" -ForegroundColor Yellow
    exit 1
}

# Initialize conda for PowerShell
& conda shell.powershell hook | Out-String | Invoke-Expression

# Activate environment
Write-Host "Activating rag_env environment..." -ForegroundColor Cyan
conda activate rag_env

if ($Arguments) {
    # Run the provided command
    & $Arguments
} else {
    # Start a new PowerShell session with environment activated
    Write-Host "Environment activated. Starting new shell..." -ForegroundColor Green
    $env:CONDA_DEFAULT_ENV = "rag_env"
}
