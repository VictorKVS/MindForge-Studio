# ========================================
# Название: Запуск стресс-теста AURORA
# Описание: Тест максимальных нагрузок
# ========================================

$studioPath = "G:\1\MindForge_Studio"
$scriptPath = "$studioPath\aurora\scripts\stress_test.py"

Write-Host " AURORA STRESS TEST" -ForegroundColor Red
Write-Host ("=" * 60)

cd $studioPath

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
    Write-Host "   Команда: cd G:\1\AI\ComfyUI; .\run_nvidia_gpu.bat --listen 0.0.0.0" -ForegroundColor Yellow
    exit 1
}

$venvPath = "$studioPath\.venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    & $venvPath
    Write-Host " venv активирован" -ForegroundColor Green
}

Write-Host " Запуск стресс-теста (100 изображений, 3 разрешения)..." -ForegroundColor Cyan
python $scriptPath

Write-Host ("=" * 60)
Write-Host " Стресс-тест завершён!" -ForegroundColor Green
Write-Host " Результаты: $studioPath\aurora\output\stress_test" -ForegroundColor Cyan
