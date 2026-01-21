# Скрипт для исправления проблем с PyTorch на Windows
# Запустите: .\fix_pytorch.ps1

Write-Host "=" -NoNewline
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "ИСПРАВЛЕНИЕ ПРОБЛЕМ С PYTORCH" -ForegroundColor Cyan
Write-Host "=" -NoNewline
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""

# Проверка версии CUDA (если установлена)
Write-Host "Проверка версии CUDA..." -ForegroundColor Yellow
$cudaVersion = $null
try {
    $nvidiaSmi = nvidia-smi 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ NVIDIA драйверы обнаружены" -ForegroundColor Green
        $cudaVersion = "12.1"  # По умолчанию используем 12.1
        Write-Host "  Рекомендуется использовать CUDA 12.1" -ForegroundColor Gray
    } else {
        Write-Host "⚠ NVIDIA драйверы не обнаружены" -ForegroundColor Yellow
        Write-Host "  Будет установлена CPU-only версия PyTorch" -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠ nvidia-smi не найден" -ForegroundColor Yellow
    Write-Host "  Будет установлена CPU-only версия PyTorch" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Шаг 1: Удаление старой версии PyTorch..." -ForegroundColor Yellow
pip uninstall -y torch torchvision torchaudio 2>&1 | Out-Null
Write-Host "✓ Старая версия удалена" -ForegroundColor Green

Write-Host ""
Write-Host "Шаг 2: Установка новой версии PyTorch..." -ForegroundColor Yellow

if ($cudaVersion) {
    Write-Host "  Установка версии с поддержкой CUDA $cudaVersion..." -ForegroundColor Gray
    $installCmd = "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"
} else {
    Write-Host "  Установка CPU-only версии..." -ForegroundColor Gray
    $installCmd = "pip install torch torchvision torchaudio"
}

Write-Host "  Выполняется: $installCmd" -ForegroundColor Gray
Invoke-Expression $installCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ PyTorch успешно установлен" -ForegroundColor Green
} else {
    Write-Host "✗ Ошибка при установке PyTorch" -ForegroundColor Red
    Write-Host ""
    Write-Host "Если проблема сохраняется:" -ForegroundColor Yellow
    Write-Host "1. Установите Visual C++ Redistributables:" -ForegroundColor White
    Write-Host "   https://aka.ms/vs/17/release/vc_redist.x64.exe" -ForegroundColor Cyan
    Write-Host "2. Перезагрузите компьютер" -ForegroundColor White
    exit 1
}

Write-Host ""
Write-Host "Шаг 3: Проверка установки..." -ForegroundColor Yellow
python -c "import torch; print(f'PyTorch версия: {torch.__version__}'); print(f'CUDA доступна: {torch.cuda.is_available()}')" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=" -NoNewline
    Write-Host ("=" * 59) -ForegroundColor Cyan
    Write-Host "УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО!" -ForegroundColor Green
    Write-Host "=" -NoNewline
    Write-Host ("=" * 59) -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Запустите проверку GPU:" -ForegroundColor Yellow
    Write-Host "  python check_gpu.py" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "⚠ PyTorch установлен, но есть проблемы с загрузкой" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "РЕШЕНИЕ:" -ForegroundColor Yellow
    Write-Host "1. Установите Visual C++ Redistributables:" -ForegroundColor White
    Write-Host "   https://aka.ms/vs/17/release/vc_redist.x64.exe" -ForegroundColor Cyan
    Write-Host "2. Перезагрузите компьютер" -ForegroundColor White
    Write-Host "3. Проверьте антивирус (может блокировать DLL)" -ForegroundColor White
}
