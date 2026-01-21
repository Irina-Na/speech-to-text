# Исправление ошибки DLL в PyTorch

## Проблема
```
OSError: [WinError 1114] Произошел сбой в программе инициализации библиотеки 
динамической компоновки (DLL). Error loading "c10.dll" or one of its dependencies.
```

## Быстрое решение

### Вариант 1: Автоматический скрипт (рекомендуется)
```powershell
.\fix_pytorch.ps1
```

### Вариант 2: Ручная установка

1. **Установите Visual C++ Redistributables**
   - Скачайте: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - Установите и перезагрузите компьютер

2. **Переустановите PyTorch**

   **Если у вас есть NVIDIA GPU:**
   ```powershell
   pip uninstall torch torchvision torchaudio
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

   **Если GPU нет или нужна CPU-only версия:**
   ```powershell
   pip uninstall torch torchvision torchaudio
   pip install torch torchvision torchaudio
   ```

3. **Проверьте установку**
   ```powershell
   python check_gpu.py
   ```

## Дополнительные шаги (если проблема сохраняется)

1. **Проверьте драйверы NVIDIA** (если есть GPU):
   ```powershell
   nvidia-smi
   ```
   Если команда не работает, обновите драйверы: https://www.nvidia.com/drivers

2. **Проверьте антивирус**
   - Временно отключите антивирус
   - Добавьте папку `venv` в исключения

3. **Перезагрузите компьютер**
   - После установки Visual C++ Redistributables обязательна перезагрузка

4. **Проверьте версию Python**
   - Рекомендуется Python 3.10-3.12
   - Проверьте: `python --version`

## Проверка после исправления

После исправления запустите:
```powershell
python check_gpu.py
```

Должно показать информацию о GPU или причины, почему CUDA недоступна.
