$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontend = Join-Path $root "frontend"
$venvPython = Join-Path $root ".venv\Scripts\python.exe"
$python = if (Test-Path $venvPython) { $venvPython } else { "python" }

$apiCommand = "cd `"$root`"; & `"$python`" -m uvicorn api.app:app --host 127.0.0.1 --port 8000"
$frontendCommand = "cd `"$frontend`"; if (-not (Test-Path node_modules)) { npm install }; npm run dev -- --host localhost --port 5173"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $apiCommand
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCommand

Write-Host "App iniciando..."
Write-Host "Abra: http://localhost:5173"
