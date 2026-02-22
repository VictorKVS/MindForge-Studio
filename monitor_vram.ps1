param([int]$Interval = 1)
$logFile = "logs\vram_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
"Время,Темп(C),GPU(%),VRAM(MB),Всего(MB)" | Out-File -Encoding utf8 $logFile
Write-Host " Мониторинг VRAM запущен" -ForegroundColor Cyan
Write-Host "   Лог: $logFile" -ForegroundColor Green
while ($true) {
    $t = Get-Date -Format "HH:mm:ss"
    $gpu = nvidia-smi --query-gpu=temperature.gpu,utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits 2>$null
    if ($gpu) {
        $p = ($gpu -split ', ').Trim()
        "$t,$($p[0]),$($p[1]),$($p[2]),$($p[3])" | Out-File -Encoding utf8 $logFile -Append
        Write-Host "[$t] GPU: $($p[1])% | VRAM: $($p[2])/$($p[3]) MB | Temp: $($p[0])C" -ForegroundColor White
    }
    Start-Sleep -Seconds $Interval
}
