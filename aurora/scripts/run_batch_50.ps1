# ========================================
# Название: Запуск пакетной генерации AURORA
# Описание: Запуск из MindForge_Studio
# ========================================

$studioPath = "G:\1\MindForge_Studio"
$scriptPath = "$studioPath\aurora\scripts\batch_gen_50.py"

Write-Host " AURORA Batch Generator" -ForegroundColor Cyan
Write-Host ("=" * 60)

if (!(Test-Path $scriptPath)) {
    Write-Host " Скрипт не найден: $scriptPath" -ForegroundColor Red
    exit 1
}

Write-Host " Проверка ComfyUI..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8188" -TimeoutSec 5 -UseBasicParsing
    Write-Host " ComfyUI доступен" -ForegroundColor Green
} catch {
    Write-Host " ComfyUI не запущен!" -ForegroundColor Red
    exit 1
}

$venvPath = "$studioPath\.venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    & $venvPath
    Write-Host " venv активирован" -ForegroundColor Green
}

Write-Host " Запуск генерации..." -ForegroundColor Cyan
python $scriptPath

Write-Host ("=" * 60)
Write-Host " Готово!" -ForegroundColor Green
Write-Host " Результаты: $studioPath\aurora\output\batch_50" -ForegroundColor Cyan
