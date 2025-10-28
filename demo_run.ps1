# demo_run.ps1 (AMELIORÉ)
$ErrorActionPreference = 'Stop'

Write-Host "=== DEMO: vérification et exécution du pipeline ProjetAI ==="

# Se placer dans le dossier du script
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

# Préférence : utiliser le python du .venv s'il existe, sinon fallback 'python'
$venvPy = Join-Path $root '.venv\Scripts\python.exe'
if (Test-Path $venvPy) {
    $pyExe = $venvPy
    Write-Host "Utilisation du Python local du .venv :" $pyExe
} else {
    try {
        $pyExe = (& python -c "import sys; print(sys.executable)" 2>$null).Trim()
        if (-not $pyExe) { throw "python introuvable" }
        Write-Host "Utilisation du Python global :" $pyExe
    } catch {
        Write-Host "ERREUR: Python introuvable. Active le .venv ou installe Python."
        Write-Host "Exemple (activation manuelle) : .\.venv\Scripts\Activate.ps1"
        exit 1
    }
}

# Fonction utilitaire : teste si un module Python existe (0 = ok)
function Test-PyModule {
    param([string]$moduleName)
    $cmd = "import pkgutil,sys; sys.exit(0 if pkgutil.find_loader('$moduleName') else 1)"
    & $pyExe -c $cmd
    return $LASTEXITCODE
}

# Modules à vérifier (sklearn = scikit-learn)
$modules = @("pandas","sklearn","joblib","fastapi","uvicorn","pydantic","requests")

$missingModules = @()
foreach ($m in $modules) {
    Write-Host "Vérification du module Python :" $m
    $rc = Test-PyModule -moduleName $m
    if ($rc -ne 0) {
        Write-Host " -> MANQUANT :" $m
        $missingModules += $m
    } else {
        Write-Host " -> OK :" $m
    }
}

if ($missingModules.Count -gt 0) {
    Write-Host ""
    Write-Host "Modules manquants détectés :" ($missingModules -join ", ")
    Write-Host "Installe-les avec :"
    Write-Host "  $pyExe -m pip install -r requirements.txt"
    Write-Host ("ou :  $pyExe -m pip install " + ($missingModules -join " "))
    exit 1
}

Write-Host ""
Write-Host "=== Vérification de data/courses.json ==="
$coursesPath = Join-Path $root 'data\courses.json'
if (Test-Path $coursesPath) {
    try {
        $null = Get-Content $coursesPath -Raw | ConvertFrom-Json
        Write-Host "OK - data\courses.json est valide."
    } catch {
        Write-Host "ERREUR - data\courses.json invalide JSON."
        exit 1
    }
} else {
    Write-Host "ATTENTION - data\courses.json introuvable (le pipeline continuera mais /api/courses retournera [])."
}

Write-Host ""
Write-Host "=== Exécution des scripts Python (aggregate -> train -> batch predict) ==="

$pyCommands = @(
    @($pyExe, ".\scripts\aggregate_from_sqlite.py"),
    @($pyExe, ".\scripts\train_dropout.py"),
    @($pyExe, ".\scripts\batch_predict_and_notify.py")
)

foreach ($pair in $pyCommands) {
    $exe = $pair[0]
    $arg = $pair[1]
    Write-Host "`n--- Exécution :" $exe $arg
    & $exe $arg
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERREUR lors de l'exécution de : $arg"
        exit $LASTEXITCODE
    }
}

Write-Host "`n=== DEMO COMPLETE : scripts exécutés avec succès ==="
Write-Host "Fichiers produits :"
Write-Host " - $(Join-Path $root 'data\features.csv')"
Write-Host " - $(Join-Path $root 'data\model_dropout.joblib')"
Write-Host " - $(Join-Path $root 'data\metrics.json')"
Write-Host " - $(Join-Path $root 'data\predictions_log.jsonl')"
Write-Host " - $(Join-Path $root 'data\notifications_log.jsonl')"
