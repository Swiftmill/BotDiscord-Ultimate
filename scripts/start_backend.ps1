$ScriptDir = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
$RootDir = Resolve-Path "$ScriptDir/.."
$venv = Join-Path $RootDir "venv_backend"
& "$venv/Scripts/activate.ps1"
uvicorn backend.app:app --host 0.0.0.0 --port 8000
