# Nettoyage de l'écran
Clear-Host
for ($i = 0; $i -lt 100; $i++) { Write-Output "" }
Clear-Host

# ─────────────────────────────────────────────
# Aller à la racine du projet (2 niveaux au-dessus de .vscode\script)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Resolve-Path (Join-Path $ScriptDir "..\..")
Set-Location $Root

# ─────────────────────────────────────────────
# Vérifier que le venv existe et l'activer
uv run python -m app
$ExitCode = $LASTEXITCODE

exit $ExitCode
