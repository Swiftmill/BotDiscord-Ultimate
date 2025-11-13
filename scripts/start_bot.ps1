$ScriptDir = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
$RootDir = Resolve-Path "$ScriptDir/.."
$venv = Join-Path $RootDir "venv_bot"
& "$venv/Scripts/activate.ps1"
Set-Location "$RootDir/bot"
python main.py
