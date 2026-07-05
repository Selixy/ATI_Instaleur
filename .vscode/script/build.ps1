# .vscode/script/build.ps1
$ErrorActionPreference = "Stop"
$root = Resolve-Path "$PSScriptRoot/../.."
Set-Location $root

# Synchroniser avant build
uv sync

# Lancer PyInstaller
uv run python .vscode/script/build.py
if ($LASTEXITCODE -ne 0) {
    Write-Error "[ERREUR] Build failed with code $LASTEXITCODE"
    exit $LASTEXITCODE
}

# Lancer l’exécutable si présent
$exe = "$root/build/dist/ATI_Instaleur/ATI_Instaleur.exe"
if (Test-Path $exe) {
    Write-Host "Lancement de l'application : $exe"
    & $exe
}