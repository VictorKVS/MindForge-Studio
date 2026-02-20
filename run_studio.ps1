# ========================================
# MindForge Studio  Master Launcher
# Версия: 1.0.0
# ========================================

Write-Host " MindForge Studio" -ForegroundColor Cyan
Write-Host ("=" * 60)

Write-Host "`n Выберите задачу:" -ForegroundColor Cyan
Write-Host "1. Генерация изображений (50 шт)"
Write-Host "2. Upscaling до 2048x2048"
Write-Host "3. Экспорт для стоков"
Write-Host "4. Web Content Generator (Premium)"
Write-Host "5. Открыть результаты"
Write-Host "6. Проверка структуры"
Write-Host "7. Выход"

$choice = Read-Host "`nВаш выбор (1-7)"

switch ($choice) {
    "1" { 
        Write-Host "`n Запуск генерации..." -ForegroundColor Cyan
        python aurora\scripts\batch_gen_50.py
    }
    "2" { 
        Write-Host "`n Запуск upscaling..." -ForegroundColor Cyan
        python aurora\scripts\upscale_batch.py
    }
    "3" { 
        Write-Host "`n Запуск экспорта..." -ForegroundColor Cyan
        python aurora\scripts\stock_export.py
    }
    "4" { 
        Write-Host "`n Запуск Web Generator..." -ForegroundColor Cyan
        python core\web_pipeline\content_generator.py
    }
    "5" { 
        Write-Host "`n Открытие результатов..." -ForegroundColor Cyan
        explorer aurora\output\batch_50
    }
    "6" { 
        Write-Host "`n Проверка структуры..." -ForegroundColor Cyan
        Get-ChildItem "knowledge" -Recurse -File | Select-Object FullName
        Get-ChildItem "exports" -Recurse -File | Select-Object FullName
    }
    "7" { 
        Write-Host "`n Выход..." -ForegroundColor Cyan
        exit
    }
    default { 
        Write-Host "`n Неверный выбор" -ForegroundColor Red
    }
}

Write-Host "`n" + ("=" * 60)
Write-Host " ЗАВЕРШЕНО" -ForegroundColor Green
Write-Host ("=" * 60)
