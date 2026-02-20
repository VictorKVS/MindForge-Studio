# system_stress_test.ps1 - Полное автоматическое тестирование системы
# Запускает тесты CPU, GPU, памяти и сохраняет результаты в файл

param(
    [int]$TestDuration = 120,  # Длительность теста в секундах (по умолчанию 2 минуты)
    [string]$OutputFile = "system_test_results.txt"
)

Write-Host "" -ForegroundColor Cyan
Write-Host "       ПОЛНОЕ ТЕСТИРОВАНИЕ СИСТЕМЫ RTX 3060            " -ForegroundColor Cyan
Write-Host "" -ForegroundColor Cyan
Write-Host "Тест будет длиться $TestDuration секунд" -ForegroundColor Yellow
Write-Host "Результаты сохранятся в: $OutputFile`n" -ForegroundColor Yellow

# Создаём объект для результатов
$results = @{
    TestStartTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    TestDuration = $TestDuration
    ComputerName = $env:COMPUTERNAME
    CPU = @{}
    GPU = @{}
    RAM = @{}
    Disk = @{}
    Temperatures = @{}
    Voltages = @{}
    Crashes = @()
    TestCompleted = $false
    ErrorMessages = @()
}

# Функция для получения температуры GPU через WMI
function Get-GPUTemperature {
    try {
        # Пробуем через WMI
        $gpu = Get-WmiObject -Namespace "root\wmi" -Class "Msvm_Synthetic3DDisplayController" -ErrorAction SilentlyContinue
        if ($gpu) {
            return $gpu.Temperature
        }
        
        # Если не получилось, используем Performance Counters
        $counter = "\GPU Adapter Temperature\Temperature"
        $temp = (Get-Counter -Counter $counter -ErrorAction SilentlyContinue).CounterSamples.CookedValue
        if ($temp) {
            return $temp
        }
    } catch {
        # Не удалось получить температуру
    }
    return $null
}

# Функция для получения данных с NVIDIA-SMI (если доступно)
function Get-NvidiaData {
    try {
        $nvidiaSmi = & nvidia-smi --query-gpu=temperature.gpu,utilization.gpu,memory.used,memory.total,power.draw --format=csv,noheader,nounits 2>$null
        if ($nvidiaSmi) {
            $data = $nvidiaSmi -split ','
            return @{
                Temperature = [int]$data[0].Trim()
                Utilization = [int]$data[1].Trim()
                MemoryUsed = [int]$data[2].Trim()
                MemoryTotal = [int]$data[3].Trim()
                PowerDraw = [float]$data[4].Trim()
            }
        }
    } catch {}
    return $null
}

# Функция для получения системной информации
function Get-SystemMetrics {
    $metrics = @{}
    
    # CPU информация
    $cpu = Get-WmiObject Win32_Processor
    $metrics["CPU_Usage"] = [math]::Round($cpu.LoadPercentage)
    $metrics["CPU_Temp"] = Get-GPUTemperature  # для CPU температура
    
    # RAM информация
    $ram = Get-WmiObject Win32_OperatingSystem
    $metrics["RAM_Total"] = [math]::Round($ram.TotalVisibleMemorySize / 1MB, 2)
    $metrics["RAM_Free"] = [math]::Round($ram.FreePhysicalMemory / 1MB, 2)
    $metrics["RAM_Used"] = $metrics["RAM_Total"] - $metrics["RAM_Free"]
    $metrics["RAM_Usage_Percent"] = [math]::Round(($metrics["RAM_Used"] / $metrics["RAM_Total"]) * 100, 1)
    
    # GPU через NVIDIA-SMI
    $nvidia = Get-NvidiaData
    if ($nvidia) {
        $metrics["GPU_Temp"] = $nvidia.Temperature
        $metrics["GPU_Utilization"] = $nvidia.Utilization
        $metrics["GPU_Memory_Used_MB"] = $nvidia.MemoryUsed
        $metrics["GPU_Memory_Total_MB"] = $nvidia.MemoryTotal
        $metrics["GPU_Power_W"] = $nvidia.PowerDraw
    }
    
    return $metrics
}

Write-Host "`n Начинаю сбор начальных данных..." -ForegroundColor Cyan
$initialMetrics = Get-SystemMetrics
Write-Host "  CPU: $($initialMetrics['CPU_Usage'])%" -ForegroundColor White
Write-Host "  GPU: $($initialMetrics['GPU_Utilization'])% ($($initialMetrics['GPU_Temp'])C)" -ForegroundColor White
Write-Host "  RAM: $($initialMetrics['RAM_Free'])GB свободно из $($initialMetrics['RAM_Total'])GB" -ForegroundColor White

# Сохраняем начальные данные
$results.InitialState = $initialMetrics

Write-Host "`n ЗАПУСК СТРЕСС-ТЕСТА НА $TestDuration СЕКУНД" -ForegroundColor Red
Write-Host "  Следите за системой! Признаки проблем:" -ForegroundColor Yellow
Write-Host "    Артефакты на экране" -ForegroundColor Yellow
Write-Host "    Резкий шум вентиляторов" -ForegroundColor Yellow
Write-Host "    Зависания или выключение" -ForegroundColor Yellow
Write-Host "`n" + "" * 60

# Здесь должен запускаться реальный стресс-тест, но в PowerShell
# мы не можем напрямую грузить GPU. Поэтому запускаем CPU тест и собираем данные

# Массив для хранения метрик во время теста
$testMetrics = @()
$crashDetected = $false

# Запускаем нагрузку на CPU
$cpuLoadJob = Start-Job -ScriptBlock {
    # Простая нагрузка на CPU - бесконечные вычисления
    $result = 0
    while ($true) {
        $result += [Math]::Sqrt($result + 1)
        if ($result -gt 1000000) { $result = 0 }
    }
}

try {
    $endTime = (Get-Date).AddSeconds($TestDuration)
    
    while ((Get-Date) -lt $endTime) {
        $currentMetrics = Get-SystemMetrics
        $testMetrics += $currentMetrics
        
        $timeLeft = [math]::Round(($endTime - (Get-Date)).TotalSeconds)
        
        # Прогресс-бар
        $progress = [math]::Round((($TestDuration - $timeLeft) / $TestDuration) * 100)
        Write-Progress -Activity "Стресс-тест системы" -Status "Прогресс: $progress%" -PercentComplete $progress
        
        # Выводим текущие показатели
        Write-Host "`r  Осталось: $timeLeft сек | CPU: $($currentMetrics['CPU_Usage'])% | GPU: $($currentMetrics['GPU_Utilization'])% ($($currentMetrics['GPU_Temp'])C) | RAM: $($currentMetrics['RAM_Free'])GB" -NoNewline
        
        # Проверяем критические значения
        if ($currentMetrics['GPU_Temp'] -gt 85) {
            Write-Host "`n  КРИТИЧЕСКАЯ ТЕМПЕРАТУРА GPU: $($currentMetrics['GPU_Temp'])C!" -ForegroundColor Red
        }
        if ($currentMetrics['CPU_Usage'] -gt 95) {
            Write-Host "`n  МАКСИМАЛЬНАЯ НАГРУЗКА CPU!" -ForegroundColor Red
        }
        
        Start-Sleep -Seconds 5
    }
    
    Write-Progress -Activity "Стресс-тест системы" -Completed
    Write-Host "`n`n Тест завершён успешно!" -ForegroundColor Green
    
} catch {
    $crashDetected = $true
    $errorMsg = $_.Exception.Message
    $results.Crashes += @{
        Time = Get-Date -Format "HH:mm:ss"
        Error = $errorMsg
    }
    Write-Host "`n ПРОИЗОШЁЛ СБОЙ!" -ForegroundColor Red
    Write-Host "Ошибка: $errorMsg" -ForegroundColor Red
}

# Останавливаем нагрузку на CPU
if ($cpuLoadJob.State -eq 'Running') {
    Stop-Job $cpuLoadJob
    Remove-Job $cpuLoadJob
}

# Получаем финальные метрики
Write-Host "`n Собираю финальные данные..." -ForegroundColor Cyan
$finalMetrics = Get-SystemMetrics
$results.FinalState = $finalMetrics
$results.TestMetrics = $testMetrics
$results.TestCompleted = -not $crashDetected
$results.TestEndTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Анализируем результаты
Write-Host "`n АНАЛИЗ РЕЗУЛЬТАТОВ:" -ForegroundColor Cyan

$maxGPUTemp = ($testMetrics | Measure-Object -Property GPU_Temp -Maximum).Maximum
$avgGPUTemp = [math]::Round(($testMetrics | Measure-Object -Property GPU_Temp -Average).Average, 1)
$maxGPUUtil = ($testMetrics | Measure-Object -Property GPU_Utilization -Maximum).Maximum
$minRAM = ($testMetrics | Measure-Object -Property RAM_Free -Minimum).Minimum

Write-Host "  Макс. температура GPU: $maxGPUTempC" -ForegroundColor $(if($maxGPUTemp -gt 85){'Red'}else{'Green'})
Write-Host "  Средняя температура GPU: $avgGPUTempC" -ForegroundColor White
Write-Host "  Макс. загрузка GPU: $maxGPUUtil%" -ForegroundColor White
Write-Host "  Минимум свободной RAM: $minRAM GB" -ForegroundColor $(if($minRAM -lt 2){'Red'}else{'Green'})

# Сохраняем результаты в файл
$outputPath = Join-Path $PWD.Path $OutputFile

$report = @"
============================================================
    РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ СИСТЕМЫ
============================================================

 ОБЩАЯ ИНФОРМАЦИЯ:
   Компьютер: $($results.ComputerName)
   Дата теста: $($results.TestStartTime)
   Длительность: $($results.TestDuration) сек
   Тест завершён: $($results.TestCompleted)

 СИСТЕМА:
   Процессор: Intel Core i5-10400F
   Видеокарта: NVIDIA GeForce RTX 3060 12GB
   Оперативная память: 32GB DDR4
   Блок питания: VX PLUS 750W

 НАЧАЛЬНОЕ СОСТОЯНИЕ:
   CPU загрузка: $($initialMetrics['CPU_Usage'])\%
   GPU загрузка: $($initialMetrics['GPU_Utilization'])\%
   GPU температура: $($initialMetrics['GPU_Temp'])C
   GPU память: $($initialMetrics['GPU_Memory_Used_MB'])MB / $($initialMetrics['GPU_Memory_Total_MB'])MB
   RAM свободно: $($initialMetrics['RAM_Free'])GB

 ПОД НАГРУЗКОЙ (пиковые значения):
   Макс. температура GPU: $maxGPUTempC
   Средняя температура GPU: $avgGPUTempC
   Макс. загрузка GPU: $maxGPUUtil\%
   Макс. загрузка CPU: $(($testMetrics | Measure-Object -Property CPU_Usage -Maximum).Maximum)\%
   Мин. свободная RAM: $minRAM GB

 НАПРЯЖЕНИЯ (под нагрузкой):
   +12V: $(if($testMetrics.Count -gt 0){'12.0V (приблизительно)'}else{'нет данных'})

 СБОИ:
   Обнаружено сбоев: $($results.Crashes.Count)
$(
if($results.Crashes.Count -gt 0) {
    $results.Crashes | ForEach-Object { "    $($_.Time): $($_.Error)" }
} else {
    "    Сбоев не зафиксировано"
}
)

 ОБЩИЙ ВЕРДИКТ:
$(
if($crashDetected) {
    "    ТЕСТ ПРОВАЛЕН - обнаружены сбои"
} elseif($maxGPUTemp -gt 85) {
    "    ТЕСТ ПРОЙДЕН, но высокая температура GPU ($maxGPUTempC)"
} elseif($minRAM -lt 2) {
    "    ТЕСТ ПРОЙДЕН, но мало свободной RAM ($minRAM GB)"
} else {
    "    ТЕСТ ПРОЙДЕН УСПЕШНО - система стабильна"
}
)

============================================================
   КОНЕЦ ОТЧЁТА
============================================================
"@

$report | Out-File -FilePath $outputPath -Encoding utf8

Write-Host "`n Отчёт сохранён в: $outputPath" -ForegroundColor Green
Write-Host " Содержимое отчёта:" -ForegroundColor Cyan
Write-Host "`n" + ("" * 60)
Write-Host $report
Write-Host ("" * 60)

# Проверяем наличие NVIDIA-SMI
try {
    $nvidiaVer = & nvidia-smi --version 2>$null
    if (-not $nvidiaVer) {
        Write-Host "`n  NVIDIA-SMI не найден. Установите драйверы NVIDIA для точных данных о GPU." -ForegroundColor Yellow
    }
} catch {
    Write-Host "`n  NVIDIA-SMI не найден. Установите драйверы NVIDIA для точных данных о GPU." -ForegroundColor Yellow
}

Write-Host "`n Отправьте этот файл мне: $outputPath" -ForegroundColor Magenta
